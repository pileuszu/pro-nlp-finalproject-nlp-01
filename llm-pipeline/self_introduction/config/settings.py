"""
환경 변수 및 설정 관리 모듈
- HyperCLOVA OpenAI 호환 API 사용
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

# API 키 (CLOVA Studio)
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")

# CLOVA Studio OpenAI 호환 API 설정
CLOVA_BASE_URL = "https://clovastudio.stream.ntruss.com/v1/openai"

# 데이터 경로
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"

# ChromaDB 설정
CHROMA_PERSIST_DIR = str(EMBEDDINGS_DIR / "chroma_db")

# 임베딩 설정 (CLOVA bge-m3)
EMBEDDING_MODEL = "bge-m3"

# LLM 설정 (HyperCLOVA X)
LLM_MODEL = "HCX-005"
LLM_TEMPERATURE = 0.7

# 검색 설정
SEARCH_TOP_K = 5
BM25_WEIGHT = 0.3
VECTOR_WEIGHT = 0.7

# 청킹 설정
CHUNK_SIZE = 800
CHUNK_OVERLAP = 50
