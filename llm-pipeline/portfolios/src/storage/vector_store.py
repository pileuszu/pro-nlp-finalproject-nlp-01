from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

class PortfolioVectorStore:
    """Manages embedding storage in Chroma DB."""

    def __init__(self, persist_dir: str = "chroma_db_experiment"):
        self.persist_dir = Path(__file__).parent.parent.parent / persist_dir
        # Configuration (matching self_introduction where possible)
        self.embedding_model_name = "jhgan/ko-sroberta-multitask"
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def save(self, text: str, metadata: dict) -> None:
        """
        Converts text to embeddings and saves to Chroma DB.
        """
        doc = Document(
            page_content=text,
            metadata=metadata
        )
        
        print(f"Storing in Chroma DB at {self.persist_dir}...")
        
        Chroma.from_documents(
            documents=[doc],
            embedding=self.embeddings,
            collection_name="portfolio_experiment",
            persist_directory=str(self.persist_dir)
        )
