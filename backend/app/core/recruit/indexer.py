import logging
from typing import List, Dict, Optional
from datetime import date
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Recruitment
from app.core.portfolio.storage.supabase_vector_store import SupabaseVectorStore

logger = logging.getLogger(__name__)

class RecruitIndexer:
    """
    Handles indexing of recruitment data into the Supabase Vector Store.
    Adapted from llm-pipeline/recruit/src/recruit_indexer.py
    """
    def __init__(self, collection_name: str = "recruitment_embeddings"):
        self.vector_store = SupabaseVectorStore(table_name=collection_name)

    def preprocess_recruitment(self, data: Dict) -> Document:
        """
        Preprocesses raw recruitment JSON into a LangChain Document.
        
        Policy:
        1. Embedding Content: Concatenate 'key_responsibilities', 'required_qualifications', 
           'preferred_qualifications'.
        2. Metadata: Store ALL fields from the input JSON.
        3. Unique ID: Use 'company' + 'title'.
        """
        content_parts = [
            f"회사: {data.get('company', '')}",
            f"제목: {data.get('title', '')}",
            f"카테고리: {data.get('category', '')}",
            f"경험 수준: {data.get('experience', '')}",
            f"학력: {data.get('education', '')}",
            f"고용 형태: {data.get('employment_type', '')}",
            f"급여: {data.get('salary', '')}",
            f"주요 업무: {data.get('key_responsibilities', '')}",
            f"자격 요건: {data.get('required_qualifications', '')}",
            f"우대 사항: {data.get('preferred_qualifications', '')}",
        ]
        page_content = " ".join([p for p in content_parts if p.split(": ")[1]])
        
        # 2. Metadata (All fields)
        # ChromaDB/Supabase requires metadata values to be str, int, float, or bool.
        metadata = {}
        for key, value in data.items():
            if value is None:
                continue
            if isinstance(value, list):
                metadata[key] = ", ".join([str(v) for v in value])
            elif isinstance(value, (str, int, float, bool)):
                metadata[key] = value
            else:
                metadata[key] = str(value)
        
        # Add a source for generic tracking
        metadata["source"] = "crawler"
        
        return Document(page_content=page_content, metadata=metadata)

    async def add_recruitments(self, db: AsyncSession, data_list: List[Dict]):
        """
        Processes and adds multiple recruitment items to BOTH SQL DB and vector store.
        """
        import datetime
        documents = []
        for item in data_list:
            # 1. SQL DB Insertion/Update
            # Check if exists by title and company
            stmt = select(Recruitment).where(
                Recruitment.title == item.get('title'),
                Recruitment.company == item.get('company')
            )
            result = await db.execute(stmt)
            db_recruit = result.scalar_one_or_none()
            
            # Format deadline and start_date
            deadline_val = item.get('deadline')
            if deadline_val and isinstance(deadline_val, str):
                 # Try common formats if needed, or just store as is if it matches date format
                 # Minimal handling for common "YYYY-MM-DD"
                 try:
                     deadline_date = datetime.date.fromisoformat(deadline_val)
                 except:
                     deadline_date = None
            else:
                 deadline_date = None
            
            start_date_val = item.get('start_date')
            if start_date_val and isinstance(start_date_val, str):
                 try:
                     start_date_obj = datetime.date.fromisoformat(start_date_val)
                 except:
                     start_date_obj = None
            else:
                 start_date_obj = None

            if not db_recruit:
                db_recruit = Recruitment(
                    title=item.get('title'),
                    company=item.get('company'),
                    link=item.get('link'),
                    start_date=start_date_obj,
                    deadline=deadline_date,
                    location=item.get('location'),
                    experience=item.get('experience'),
                    education=item.get('education'),
                    employment_type=item.get('employment_type'),
                    salary=item.get('salary'),
                    category=item.get('category'),
                    key_responsibilities=item.get('key_responsibilities'),
                    required_qualifications=item.get('required_qualifications'),
                    preferred_qualifications=item.get('preferred_qualifications'),
                    tags=item.get('tags', [])
                )
                db.add(db_recruit)
            else:
                # Update existing
                db_recruit.link = item.get('link', db_recruit.link)
                db_recruit.deadline = deadline_date or db_recruit.deadline
                # ... update other fields as needed
            
            await db.flush() # Get the ID for metadata
            
            # 2. Vector Store Preprocessing
            doc = self.preprocess_recruitment(item)
            doc.metadata['id'] = db_recruit.id
            doc.metadata['unique_id'] = f"{db_recruit.company}_{db_recruit.title}"
            documents.append(doc)
            
        await db.commit()

        if documents:
            logger.info(f"Adding {len(documents)} recruitment documents to vector store.")
            await self.vector_store.add_documents(documents)
            return len(documents)
        return 0

    async def search(self, query: str, k: int = 5):
        """
        Search for relevant recruitments.
        """
        return await self.vector_store.similarity_search(query, k=k)
