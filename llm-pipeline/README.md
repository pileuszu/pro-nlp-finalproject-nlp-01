# LLM Pipeline Service

이 서비스는 **LangGraph, LangChain, LangFuse**를 활용하여 고도화된 LLM 파이프라인을 처리하는 독립적인 서버입니다.

## 🛠 Tech Stack
- **Framework**: FastAPI
- **Orchestration**: LangGraph, LangChain
- **Observability**: LangFuse
- **Package Manager**: pip (requirements.txt)

## 📂 Directory Structure
- `main.py`: FastAPI 애플리케이션 진입점 및 API 엔드포인트 정의.
- `notebooks/`: LLM 실험 및 프롬프트 엔지니어링을 위한 Jupyter Notebook 공간.
- `pipelines/`: (예정) 각 독립적인 LLM 워크플로우 로직.

## 🚀 Getting Started

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
uvicorn main:app --reload
```

## 🧪 Experiments
`notebooks/` 디렉토리에서 새로운 파이프라인을 실험하고 검증한 뒤, `pipelines/` 폴더로 모듈화하여 이동시키는 워크플로우를 권장합니다.
