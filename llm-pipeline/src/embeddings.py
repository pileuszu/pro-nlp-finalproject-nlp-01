"""
벡터 스토어 관리 모듈
- HuggingFace Embeddings (오픈소스, 로컬 실행)
- ChromaDB 컬렉션 생성 및 관리
- 문서 임베딩 및 영속 저장
"""
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config.settings import (
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    EMBEDDINGS_DIR
)
from src.data_loader import get_all_user_documents, get_company_documents


def get_embeddings() -> HuggingFaceEmbeddings:
    """HuggingFace 임베딩 모델 초기화 (한국어 특화)"""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )


def get_or_create_vectorstore(
    collection_name: str,
    documents: Optional[List[Document]] = None
) -> Chroma:
    """
    벡터스토어 가져오기 또는 생성
    - 이미 존재하면 로드
    - 없으면 documents로 새로 생성
    """
    persist_directory = str(Path(CHROMA_PERSIST_DIR) / collection_name)
    embeddings = get_embeddings()
    
    # 디렉토리가 존재하고 데이터가 있으면 로드
    if Path(persist_directory).exists() and any(Path(persist_directory).iterdir()):
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
    
    # 새로 생성
    if documents is None:
        raise ValueError(f"Collection {collection_name} does not exist and no documents provided")
    
    # 디렉토리 생성
    Path(persist_directory).mkdir(parents=True, exist_ok=True)
    
    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )


def create_user_vectorstore(user_id: str) -> Chroma:
    """특정 사용자의 벡터스토어 생성"""
    documents = get_all_user_documents(user_id)
    collection_name = f"user_{user_id}"
    return get_or_create_vectorstore(collection_name, documents)


def create_company_vectorstore() -> Chroma:
    """기업 벡터스토어 생성"""
    documents = get_company_documents()
    return get_or_create_vectorstore("company", documents)


def load_user_vectorstore(user_id: str) -> Chroma:
    """사용자 벡터스토어 로드"""
    collection_name = f"user_{user_id}"
    persist_directory = str(Path(CHROMA_PERSIST_DIR) / collection_name)
    
    if not Path(persist_directory).exists():
        # 없으면 새로 생성
        return create_user_vectorstore(user_id)
    
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=persist_directory
    )


def load_company_vectorstore() -> Chroma:
    """기업 벡터스토어 로드"""
    persist_directory = str(Path(CHROMA_PERSIST_DIR) / "company")
    
    if not Path(persist_directory).exists():
        return create_company_vectorstore()
    
    return Chroma(
        collection_name="company",
        embedding_function=get_embeddings(),
        persist_directory=persist_directory
    )


def create_all_vectorstores():
    """모든 벡터스토어 생성 (초기화용)"""
    from rich import print as rprint
    
    rprint("[bold yellow]Creating vectorstores...[/bold yellow]")
    
    # 사용자 벡터스토어 생성
    for user_id in ["user1", "user2"]:
        rprint(f"  Creating {user_id} vectorstore...")
        create_user_vectorstore(user_id)
        rprint(f"  [green]✓ {user_id} vectorstore created[/green]")
    
    # 기업 벡터스토어 생성
    rprint("  Creating company vectorstore...")
    create_company_vectorstore()
    rprint("  [green]✓ company vectorstore created[/green]")
    
    rprint("[bold green]All vectorstores created successfully![/bold green]")


if __name__ == "__main__":
    create_all_vectorstores()
