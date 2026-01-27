# 포트폴리오 처리 파이프라인 (실험용)

이 모듈은 다양한 소스(파일, GitHub, Notion)에서 사용자 포트폴리오를 처리하고, LLM을 사용하여 내용을 정제한 후, Chroma DB에 벡터 임베딩으로 저장하는 실험적인 파이프라인을 구현합니다.

## 주요 기능

-   **다중 소스 추출**:
    -   **파일**: (작업 중) 로컬 파일 처리 로직 구현 대기 중.
    -   **GitHub**: GitHub README (단일 Repo) 또는 사용자 전체 Public Repo README 추출 지원.
    -   **Notion**: Notion 페이지 및 데이터베이스 재귀적 크롤링 지원.
-   **LLM 정제**: (작업 중) Google Gemini를 사용한 정제 로직 구현 대기 중.
-   **벡터 저장소**: HuggingFace 모델을 사용하여 로컬 Chroma DB 인스턴스에 임베딩 저장.

## 설정 (Setup)

1.  **환경 변수**:
    `llm-pipeline/portfolios/` 폴더 내에 `.env` 파일을 생성합니다 (또는 `llm-pipeline/`의 파일을 사용):
    ```ini
    GOOGLE_API_KEY=your_google_api_key
    ```

2.  **설치**:
    전용 가상 환경(virtual environment)을 사용하는 것을 권장합니다.
    ```bash
    # 가상 환경 생성 (없는 경우)
    python -m venv llm-pipeline/portfolios/venv

    # 의존성 패키지 설치
    llm-pipeline/portfolios/venv/Scripts/pip install -r llm-pipeline/portfolios/requirements.txt
    ```

    > **참고**: 이미지 추출을 위한 `surya-ocr`은 PyTorch를 필요로 하며, 첫 실행 시 모델을 다운로드할 수 있습니다.

## 사용법 (Usage)

프로젝트 루트에서 `main.py` 스크립트를 실행합니다.

### 1. 로컬 파일 처리
```bash
llm-pipeline/portfolios/venv/Scripts/python llm-pipeline/portfolios/main.py --source_type file --source_path llm-pipeline/portfolios/data/sample_portfolio.txt
```

### 2. GitHub URL 처리
```bash
llm-pipeline/portfolios/venv/Scripts/python llm-pipeline/portfolios/main.py --source_type github --source_path https://github.com/user/repo/blob/main/README.md
```

### 3. Notion 처리 (계획됨)
```bash
llm-pipeline/portfolios/venv/Scripts/python llm-pipeline/portfolios/main.py --source_type notion --source_path <page_id>
```

## 디렉토리 구조

```
llm-pipeline/portfolios/
├── src/
│   ├── extractors/       # 소스별 추출기 (File, GitHub, Notion)
│   ├── processors/       # 텍스트 처리기 (LLM Refinement)
│   └── storage/          # 벡터 데이터베이스 연동 (Chroma)
├── data/                 # 샘플 데이터
├── venv/                 # 가상 환경
├── main.py               # 진입점(Entry point) 스크립트
├── requirements.txt      # 의존성 패키지 목록
└── README.md             # 본 파일
```
