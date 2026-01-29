import os
import shutil
from typing import List, Dict, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configuration constants
# Adjust these paths as needed, assuming we run from project root or relative to this file
CURRENT_DIR = Path(__file__).resolve().parent
RECRUIT_ROOT = CURRENT_DIR.parent
PERSIST_DIR = RECRUIT_ROOT / "data" / "chroma_db"
EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"

class RecruitIndexer:
    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or str(PERSIST_DIR)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
    def preprocess_recruitment(self, data: Dict) -> Document:
        """
        Preprocesses raw recruitment JSON into a LangChain Document.
        
        Policy:
        1. Embedding Content: Concatenate 'key_responsibilities', 'required_qualifications', 
           'preferred_qualifications'.
        2. Metadata: Store ALL fields from the input JSON.
        3. Unique ID: Use 'link' field.
        """
        # 1. Construct Embedding Content
        # We handle missing fields gracefully by defaulting to empty strings
        content_parts = [
            f"주요 업무: {data.get('key_responsibilities', '')}",
            f"자격 요건: {data.get('required_qualifications', '')}",
            f"우대 사항: {data.get('preferred_qualifications', '')}"
        ]
        page_content = " ".join(content_parts)
        
        # 2. Metadata (All fields)
        # ChromaDB requires metadata values to be str, int, float, or bool.
        # We must convert lists to strings.
        metadata = {}
        for key, value in data.items():
            if isinstance(value, list):
                metadata[key] = ", ".join([str(v) for v in value])
            else:
                metadata[key] = value
        
        # 3. Create Document
        # Ideally we pass 'id' to the vectorstore add_documents method, 
        # but storing it in metadata/object is also good practice.
        return Document(page_content=page_content, metadata=metadata)

    def create_vectorstore(self, data_list: List[Dict], collection_name: str = "recruit_collection"):
        """
        Creates or updates a Chroma vectorstore from a list of recruitment dictionaries.
        """
        documents = []
        ids = []
        
        for item in data_list:
            doc = self.preprocess_recruitment(item)
            
            # Generate Unique ID: company + title
            company = item.get('company', 'UnknownCompany')
            title = item.get('title', 'UnknownTitle')
            unique_id = f"{company}_{title}"
            
            # 검색 시 바로 꺼내 쓸 수 있도록 메타데이터에도 ID 저장
            doc.metadata['unique_id'] = unique_id
            
            documents.append(doc)
            ids.append(unique_id)
            
        # Ensure persist directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize Chroma
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_dir
        )
        
        # Add documents with custom IDs
        vectorstore.add_documents(documents=documents, ids=ids)
        
        return vectorstore

    def search_recruitments(self, query: str, k: int = 5, collection_name: str = "recruit_collection"):
        """
        Simple search wrapper for verification.
        """
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_dir
        )
        
        return vectorstore.similarity_search(query, k=k)

    def search_recruitments_with_scores(self, query: str, k: int = 5, collection_name: str = "recruit_collection"):
        """
        Search with similarity scores (lower distance is better for Chroma/L2).
        Returns List[Tuple[Document, float]]
        """
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_dir
        )
        
        return vectorstore.similarity_search_with_score(query, k=k)

    def get_all_documents(self, collection_name: str = "recruit_collection"):
        """
        Retrieves all documents stored in the vectorstore.
        Returns a dictionary containing 'ids', 'metadatas', and 'documents' (page_content).
        """
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_dir
        )
        return vectorstore.get()

if __name__ == "__main__":
    print("RecruitIndexer module loaded.")
