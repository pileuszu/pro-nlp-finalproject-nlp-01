import logging
import traceback
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy as sa
from langchain_core.documents import Document

from common import models

logger = logging.getLogger(__name__)

async def precompute_recommendations_for_portfolio(db: AsyncSession, portfolio_id: int):
    """
    Run the full AI recommendation pipeline for a specific portfolio and save results to the DB.
    """
    from jobs.core.recruit.matcher import RecruitMatcher
    from jobs.core.recruit.indexer import RecruitIndexer
    from jobs.infra.models import Portfolio, Recommendation, Recruitment, User, PortfolioJobQuery
    
    logger.info(f"Starting recommendation pre-computation for Portfolio {portfolio_id}")

    stmt = select(Portfolio).where(Portfolio.id == portfolio_id)
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    if not portfolio: 
        logger.error(f"Portfolio {portfolio_id} not found")
        return []

    portfolio_data = {
        "project_name": portfolio.project_name,
        "description": portfolio.description,
        "tech_stack": portfolio.tech_stack,
        "role": portfolio.role,
        "period": portfolio.period
    }
    
    # Add User context if available
    user_stmt = select(User).where(User.id == portfolio.user_id)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()
    if user:
        portfolio_data["user_summary"] = user.profile_summary
        portfolio_data["desired_job_title"] = user.desired_job_title

    matcher = RecruitMatcher()
    indexer = RecruitIndexer()

    # 1. Fetch Job Queries and Search
    query_stmt = select(PortfolioJobQuery).where(PortfolioJobQuery.portfolio_id == portfolio.id)
    query_result = await db.execute(query_stmt)
    db_queries = query_result.scalars().all()

    all_candidates = []
    seen_ids = set()
    
    for db_q in db_queries:
        if not db_q.query_text: continue
        if db_q.embedding is not None:
             # Use pre-calculated embedding directly
             initial_results = await indexer.search_by_vector(db, db_q.embedding, k=3)
        else:
             # Fallback: Generate embedding and search
             initial_results = await indexer.search(db, db_q.query_text, k=3)
        
        # Optimization: Skip local reranking to reduce API calls. 
        # We rely on Vector Score for initial candidate selection (Top 10)
        # and then use Global Reranker for final ordering.
        refined_results = initial_results 
        
        for doc in refined_results:
            uid = doc.metadata.get('id')
            if uid and uid not in seen_ids:
                all_candidates.append(doc)
                seen_ids.add(uid)

    if not all_candidates:
        # Fallback if no specific queries: use user context or project name
        fallback_query = (user.desired_job_title if user else None) or portfolio.project_name or "개발자"
        logger.info(f"No candidates from queries, using fallback search: {fallback_query}")
        initial_results = await indexer.search(db, fallback_query, k=10)
        all_candidates = initial_results

    if not all_candidates:
        logger.info("No candidates found even after fallback.")
        return []

    # 2. AI Re-rank and Reason
    logger.info(f"Ranking {len(all_candidates)} candidates...")
    recommendations = await matcher.rank_and_reason(portfolio_data, all_candidates)
    
    # 3. Save to Recommendation Table
    # Clear old ones first
    delete_stmt = sa.delete(Recommendation).where(Recommendation.portfolio_id == portfolio_id)
    await db.execute(delete_stmt)
    
    saved_results = []
    for i, rec in enumerate(recommendations):
        # We need the recruitment_id. Matcher returns metadata.
        # Assuming unique_id or some field maps to recruitment.id
        # Let's try to find it by company and title if id is not obvious
        recruit_id = rec.get("id")
        if not recruit_id:
             r_stmt = select(Recruitment).where(
                 Recruitment.company == rec.get("company"),
                 Recruitment.title == rec.get("title")
             )
             r_res = await db.execute(r_stmt)
             r_obj = r_res.scalar_one_or_none()
             if r_obj: recruit_id = r_obj.id

        if recruit_id:
            new_rec = Recommendation(
                portfolio_id=portfolio_id,
                recruitment_id=recruit_id,
                rank_order=i,
                score=rec.get("score"),
                reason=rec.get("reason", "")
            )
            db.add(new_rec)
            saved_results.append(rec)
    
    await db.commit()
    logger.info(f"Saved {len(saved_results)} recommendations for Portfolio {portfolio_id}")
    return saved_results

async def bulk_precompute_recommendations(db: AsyncSession):
    """
    Triggers pre-computation for all active portfolios in the database.
    Useful for background batch processing.
    """
    from jobs.infra.models import Portfolio
    stmt = select(Portfolio.id)
    result = await db.execute(stmt)
    portfolio_ids = result.scalars().all()
    
    logger.info(f"Starting bulk pre-computation for {len(portfolio_ids)} portfolios...")
    for pid in portfolio_ids:
        try:
            await precompute_recommendations_for_portfolio(db, pid)
            logger.info(f"Pre-computed recommendations for portfolio {pid}")
        except Exception as e:
            logger.error(f"Failed to pre-compute for portfolio {pid}: {e}")
    
    return len(portfolio_ids)

async def global_rerank_recommendations(db: AsyncSession, user_id: int):
    """
    Rerank ALL recommendations across all portfolios for a user using their global profile.
    This provides a unified Top-N list of jobs relevant to the user's overall profile.
    """
    from jobs.core.recruit.matcher import RecruitMatcher
    from jobs.infra.models import User, Portfolio, Recommendation, Recruitment
    
    logger.info(f"Starting global reranking for User {user_id}")
    
    # 1. Fetch User Profile
    user_stmt = select(User).where(User.id == user_id)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()
    if not user: return

    # Global Query: Use profile summary + desired job title
    global_query = ""
    if user.profile_summary:
        global_query = f"{user.desired_job_title or '개발자'} {user.profile_summary}"[:500]
    
    # Fallback to latest portfolio if user profile is empty
    if not global_query or len(global_query) < 10:
        port_stmt = select(Portfolio).where(Portfolio.user_id == user_id).order_by(Portfolio.created_at.desc()).limit(1)
        port_res = await db.execute(port_stmt)
        latest_port = port_res.scalar_one_or_none()
        
        if latest_port:
            techs = ""
            if latest_port.tech_stack:
                # Handle JSON list or string
                if isinstance(latest_port.tech_stack, list):
                    techs = ", ".join(latest_port.tech_stack)
                else:
                    techs = str(latest_port.tech_stack)
                    
            global_query = f"{latest_port.role or '개발자'} {techs} {latest_port.description or ''}"[:500]
    
    if not global_query:
        global_query = "개발자"

    # 2. Fetch ALL existing recommendations for this user
    # Join Portfolio to filter by user_id
    rec_stmt = select(Recommendation, Recruitment).join(Portfolio).join(Recruitment).where(
        Portfolio.user_id == user_id
    )
    rec_result = await db.execute(rec_stmt)
    rows = rec_result.all()
    
    if not rows: return

    # 3. Convert to "Document-like" objects for Reranker
    candidates = []
    seen_recruit_ids = set()
    
    for rec_obj, recruitment in rows:
        if recruitment.id in seen_recruit_ids:
            continue
        seen_recruit_ids.add(recruitment.id)
        
        content = (
            f"회사: {recruitment.company}\n"
            f"직무: {recruitment.title}\n"
            f"주요 업무: {recruitment.key_responsibilities}\n"
            f"자격 요건: {recruitment.required_qualifications}\n"
        )
        
        doc = Document(page_content=content, metadata={"id": str(rec_obj.id)})
        candidates.append(doc)
    
    if not candidates: return

    # 4. Rerank using NCP
    matcher = RecruitMatcher()
    refined_results = await matcher.rerank_with_ncp(global_query, candidates, top_n=20)
    
    # 5. Update Rank Order
    for i, doc in enumerate(refined_results):
        try:
            rec_id = int(doc.metadata.get("id"))
            update_stmt = sa.update(Recommendation).where(Recommendation.id == rec_id).values(rank_order=i)
            await db.execute(update_stmt)
        except:
            continue
            
    await db.commit()
    logger.info(f"Global reranking completed for User {user_id}")

