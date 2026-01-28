import os
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import create_async_engine

class SupabaseVectorStore:
    """
    Manages embedding storage in Supabase using PGVector.
    """

    def __init__(self, table_name: str = "portfolio_embeddings"):
        self.connection_string = os.getenv("SUPABASE_URL")
        if not self.connection_string:
            raise ValueError("SUPABASE_URL environment variable is not set")

        # Use the same model as the original pipeline for consistency
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.table_name = table_name
        self.vector_store = PGVector(
            embeddings=self.embedding_model,
            collection_name=table_name,
            connection=self.connection_string,
            use_jsonb=True,
        )

    async def add_documents(self, documents: List[Document]):
        """
        Adds documents to the Supabase vector store.
        """
        await self.vector_store.aadd_documents(documents)

    async def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Performs similarity search.
        """
        return await self.vector_store.asimilarity_search(query, k=k)
