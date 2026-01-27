"""
환경 변수 및 설정 관리 모듈
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

# API 키
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 데이터 경로
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"

# ChromaDB 설정
CHROMA_PERSIST_DIR = str(EMBEDDINGS_DIR / "chroma_db")

# 임베딩 설정 (HuggingFace - 로컬 실행, API 제한 없음)
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"

# LLM 설정
LLM_MODEL = "gemini-3-flash-preview"
LLM_TEMPERATURE = 0.7

# 검색 설정
SEARCH_TOP_K = 5
BM25_WEIGHT = 0.3
VECTOR_WEIGHT = 0.7

# 청킹 설정
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
