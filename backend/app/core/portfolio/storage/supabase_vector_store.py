import os
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

class SupabaseVectorStore:
    """
    Manages embedding storage in Supabase using PGVector.
    Uses Hugging Face Inference API (Free) for lightweight serverless deployment.
    """

    def __init__(self, table_name: str = "portfolio_embeddings"):
        self.connection_string = os.getenv("SUPABASE_URL")
        if not self.connection_string:
            raise ValueError("SUPABASE_URL environment variable is not set")
        
        self.table_name = table_name
        self._embedding_model = None
        self._vector_store = None
        
        # Hugging Face Token (required for Inference API)
        self.hf_token = os.getenv("HF_TOKEN")
        if not self.hf_token:
             # Fallback: Inference API can sometimes work without token for low volume,
             # but we highly recommend it.
             print("Warning: HF_TOKEN not set. Inference API may be rate limited.")

    @property
    def embedding_model(self):
        if not self._embedding_model:
            # API-based embedding: Zero local memory/CPU overhead
            self._embedding_model = HuggingFaceInferenceAPIEmbeddings(
                api_key=self.hf_token,
                model_name="jhgan/ko-sroberta-multitask"
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
        return await self.vector_store.asimilarity_search(query, k=k)
