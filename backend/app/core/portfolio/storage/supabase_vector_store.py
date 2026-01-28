import os
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

class SupabaseVectorStore:
    """
    Manages embedding storage in Supabase using PGVector.
    Uses Google Gemini Embeddings (API) for lightweight serverless deployment.
    """

    def __init__(self, table_name: str = "portfolio_embeddings"):
        self.connection_string = os.getenv("SUPABASE_URL")
        if not self.connection_string:
            raise ValueError("SUPABASE_URL environment variable is not set")
        
        self.table_name = table_name
        self._embedding_model = None
        self._vector_store = None
        
        # Check API Key
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
             raise ValueError("GOOGLE_API_KEY is required for Gemini Embeddings")

    @property
    def embedding_model(self):
        if not self._embedding_model:
            # Zero-memory overhead, API-based embedding
            self._embedding_model = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=self.api_key,
                task_type="retrieval_document" # Optimized for storage
            )
        return self._embedding_model

    @property
    def vector_store(self):
        if not self._vector_store:
            self._vector_store = PGVector(
                embeddings=self.embedding_model,
                collection_name=self.table_name,
                connection=self.connection_string,
                use_jsonb=True,
            )
        return self._vector_store

    async def add_documents(self, documents: List[Document]):
        """
        Adds documents to the Supabase vector store.
        """
        await self.vector_store.aadd_documents(documents)

    async def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Performs similarity search.
        """
        # For query, we might want task_type="retrieval_query" but langchain handle this automatically 
        # based on methods typically, or we configure the model instance.
        # GoogleGenerativeAIEmbeddings doesn't dynamic switch task_type easily without re-init 
        # in some versions, but 'retrieval_document' is generally fine or 'semantic_similarity'.
        # However, for best results, queries should ideally use retrieval_query.
        # But keeping it simple with the same instance for now as typical LangChain usage.
        return await self.vector_store.asimilarity_search(query, k=k)
