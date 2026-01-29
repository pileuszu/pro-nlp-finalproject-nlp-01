
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_naver import ChatClovaX
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import numpy as np

from app.models import models
from app.schemas import schemas
from app.core.config import settings # Assuming settings exist, or fallback to os.getenv

logger = logging.getLogger(__name__)

# --- Configuration ---
# Use environment variables directly if settings not fully configured
NCP_CLOVASTUDIO_API_KEY = os.getenv("NCP_CLOVASTUDIO_API_KEY")
NCP_APIGW_API_KEY = os.getenv("NCP_APIGW_API_KEY") 
NCP_CLOVASTUDIO_APP_ID = os.getenv("NCP_CLOVASTUDIO_APP_ID")

class PGHybridRetriever:
    """
    Hybrid Retriever combining BM25 (Keyword) and Vector Search (Semantic)
    using stored embeddings in PostgreSQL.
    """
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.documents = [] # (id, text, embedding, metadata)
        self.bm25 = None
        
        self._load_documents()

    def _load_documents(self):
        """Load user's portfolios and recruitment data for context"""
        # Fetch Portfolios
        portfolios = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == self.user_id
        ).all()
        
        for p in portfolios:
            # Combine relevant text fields
            content = f"{p.project_name}\n{p.description or ''}\n{p.role or ''}\n{p.content or ''}"
            
            # Using stored embedding if available, otherwise skip vector part for this doc
            embedding = p.embedding
            if isinstance(embedding, str):
                try:
                    embedding = json.loads(embedding)
                except:
                    embedding = None
            
            self.documents.append({
                "id": p.id,
                "text": content,
                "embedding": embedding,
                "metadata": {
                    "source": "portfolio",
                    "project_name": p.project_name,
                    "role": p.role,
                    "stack": p.tech_stack
                }
            })
            
        # Initialize BM25
        if self.documents:
            tokenized_corpus = [doc["text"].lower().split() for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, query_embedding: List[float] = None, top_k: int = 5) -> List[Document]:
        if not self.documents:
            return []

        # 1. BM25 Scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Normalize BM25 (Min-Max)
        if len(bm25_scores) > 0:
            min_s, max_s = min(bm25_scores), max(bm25_scores)
            if max_s > min_s:
                bm25_scores = [(s - min_s) / (max_s - min_s) for s in bm25_scores]
            else:
                bm25_scores = [1.0] * len(bm25_scores) # All same

        # 2. Vector Scores (Cosine Similarity)
        vector_scores = [0.0] * len(self.documents)
        if query_embedding:
            q_vec = np.array(query_embedding)
            norm_q = np.linalg.norm(q_vec)
            
            for i, doc in enumerate(self.documents):
                if doc["embedding"]:
                    d_vec = np.array(doc["embedding"])
                    norm_d = np.linalg.norm(d_vec)
                    if norm_q > 0 and norm_d > 0:
                        cos_sim = np.dot(q_vec, d_vec) / (norm_q * norm_d)
                        vector_scores[i] = (cos_sim + 1) / 2 # Normalize -1~1 to 0~1
        
        # 3. Hybrid Combination
        # Weight: BM25 0.3, Vector 0.7 (Adjustable)
        final_scores = []
        for i in range(len(self.documents)):
            score = 0.3 * bm25_scores[i] + 0.7 * vector_scores[i]
            final_scores.append((score, self.documents[i]))
            
        final_scores.sort(key=lambda x: x[0], reverse=True)
        
        # Convert to LangChain Documents
        results = []
        for score, doc_data in final_scores[:top_k]:
            results.append(Document(
                page_content=doc_data["text"],
                metadata=doc_data["metadata"]
            ))
            
        return results

class AICoverLetterService:
    def __init__(self):
        # Initialize HyperCLOVA X
        # HCX-007 is the model ID
        self.llm = ChatClovaX(
            model="HCX-007",
            temperature=0.5,
            max_tokens=2048,
            # thinking={"effort": "low"} # Optional if supported
        )

    async def generate_cover_letter(
        self, 
        db: Session, 
        user_id: int, 
        generate_req: schemas.CoverLetterGenerateRequest
    ) -> models.CoverLetter:
        
        # 1. Fetch Recruitment Logic
        recruitment = db.query(models.Recruitment).filter(
            models.Recruitment.id == generate_req.recruitId
        ).first()
        if not recruitment:
            raise ValueError("Recruitment not found")

        # 2. Hybrid Retrieval
        retriever = PGHybridRetriever(db, user_id)
        
        # Use recruitment embedding if available for query, else rely on BM25 only (or simple embedding if needed)
        query_embedding = None
        if recruitment.embedding:
             # Handle vector format (string or list)
            if isinstance(recruitment.embedding, str):
                 try:
                    query_embedding = json.loads(recruitment.embedding)
                 except: pass
            else:
                 query_embedding = recruitment.embedding

        # Search Query: Summary + Qualifications
        query_text = f"{recruitment.company} {recruitment.title} {recruitment.required_qualifications or ''}"
        relevant_docs = retriever.search(query_text, query_embedding, top_k=5)
        
        context_text = "\n\n".join([d.page_content for d in relevant_docs])

        # 3. Gap Analysis (Optional but recommended for context)
        # We can implement a simplified gap analysis here or as a separate step
        gap_result = self._analyze_gap(context_text, query_text)

        # 4. Generate Main Content (Cover Letter)
        # Assuming the request generates ONE comprehensive cover letter or handling multiple items?
        # The schema supports multiple items. The request might have 'question' field.
        # If 'question' is provided, we generate one item.
        
        # Create Cover Letter Record
        cover_letter = models.CoverLetter(
            user_id=user_id,
            recruitment_id=recruitment.id,
            title=f"{recruitment.company} - {recruitment.title} 자소서",
            content="", # Will fill based on items or summary
            status="PENDING",
            gap_analysis=gap_result
        )
        db.add(cover_letter)
        db.commit() # Commit to get ID
        db.refresh(cover_letter)
        
        try:
            # Generate Answer
            answer_data = self._generate_answer(
                company_name=recruitment.company,
                job_title=recruitment.title,
                question=generate_req.question,
                context=context_text,
                gap_analysis=gap_result,
                tone=generate_req.tone
            )
            
            # Save Item
            item = models.CoverLetterItem(
                cover_letter_id=cover_letter.id,
                question=generate_req.question,
                content=answer_data.get("content"),
                key_points=answer_data.get("key_points"),
                suggested_improvements=answer_data.get("suggested_improvements"),
                category="general" # Can be classified
            )
            db.add(item)
            
            # Update Main Status
            cover_letter.status = "COMPLETED"
            cover_letter.content = answer_data.get("content") # For backward compatibility or summary
            db.commit()
            
            return cover_letter
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            cover_letter.status = "FAILED"
            db.commit()
            raise e

    def _analyze_gap(self, user_context: str, job_req: str) -> Dict:
        prompt = PromptTemplate.from_template(
            """당신은 채용 분석 전문가입니다. 
            지원자의 경험과 채용 공고를 비교하여 분석 결과를 JSON으로 출력하세요.
            
            [채용 공고 요약]
            {job_req}
            
            [지원자 경험]
            {user_context}
            
            반드시 아래 JSON 형식으로만 출력하세요:
            {{
                "matching_points": ["매칭점1", "매칭점2"],
                "missing_elements": ["부족한점1", "부족한점2"],
                "overall_fit": "상/중/하 판단"
            }}
            """
        )
        chain = prompt | self.llm | JsonOutputParser()
        try:
            return chain.invoke({"job_req": job_req, "user_context": user_context})
        except:
            return {}

    def _generate_answer(self, company_name, job_title, question, context, gap_analysis, tone) -> Dict:
        prompt = PromptTemplate.from_template(
            """당신은 {tone} 톤앤매너를 구사하는 전문 자기소개서 컨설턴트입니다.
            지원자의 경험을 바탕으로 해당 문항에 대한 최적의 답변을 작성하세요.
            
            **기업**: {company_name}
            **직무**: {job_title}
            **문항**: {question}
            
            **참고 경험**:
            {context}
            
            **분석 참고**:
            {gap_analysis}
            
            답변은 다음 JSON 구조로 작성하세요:
            {{
                "content": "작성된 자기소개서 본문 (700자 내외)",
                "key_points": ["강조된 역량1", "강조된 역량2"],
                "suggested_improvements": ["개선 제안1", "개선 제안2"]
            }}
            """
        )
        chain = prompt | self.llm | JsonOutputParser()
        return chain.invoke({
            "company_name": company_name,
            "job_title": job_title,
            "question": question,
            "context": context,
            "gap_analysis": json.dumps(gap_analysis, ensure_ascii=False),
            "tone": tone
        })

cover_letter_service = AICoverLetterService()
