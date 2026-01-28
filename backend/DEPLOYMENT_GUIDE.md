# Google Cloud Run Deployment Guide

본 문서는 `backend` 애플리케이션을 Google Cloud Run에 배포하는 방법을 안내합니다.

## 1. 사전 준비 (Prerequisites)

1.  **Google Cloud SDK (gcloud CLI)** 설치 및 로그인:
    ```bash
    gcloud auth login
    gcloud config set project [YOUR_PROJECT_ID]
    ```
2.  **API 활성화**:
    *   Cloud Run API
    *   Artifact Registry API
    *   Cloud Build API

## 2. 이미지 빌드 및 저장 (Build)

Google Artifact Registry에 Docker 이미지를 빌드하고 푸시합니다.

```bash
# 예: asia-northeast3(서울) 리전의 'repository' 레포지토리에 'backend'라는 이름으로 빌드
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/[PROJECT_ID]/[REPO_NAME]/pro-nlp-backend:latest .
```

> **참고**: `repository`가 없다면 먼저 생성해야 합니다:
> `gcloud artifacts repositories create [REPO_NAME] --repository-format=docker --location=asia-northeast3`

## 3. Cloud Run 배포 (Deploy)

빌드된 이미지를 Cloud Run 서비스로 배포합니다.

```bash
gcloud run deploy pro-nlp-backend \
  --image asia-northeast3-docker.pkg.dev/[PROJECT_ID]/[REPO_NAME]/pro-nlp-backend:latest \
  --region asia-northeast3 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://user:pass@host:port/db" \
  --set-env-vars "GOOGLE_API_KEY=your_gemini_api_key" \
  --set-env-vars "SECRET_KEY=your_secret_key" \
  --set-env-vars "ALGORITHM=HS256" \
  --set-env-vars "KAKAO_REST_API_KEY=your_kakao_api_key" \
  --set-env-vars "KAKAO_CLIENT_SECRET=your_kakao_secret" \
  --set-env-vars "KAKAO_REDIRECT_URI=https://your-frontend-domain.com/auth/kakao/callback" \
  --set-env-vars "NCP_CLOVASTUDIO_API_KEY=your_api_key" \
  --set-env-vars "NCP_CLOVASTUDIO_BASE_URL=https://clovastudio.stream.ntruss.com"
```

*   `--allow-unauthenticated`: 외부 접속 허용 (테스트용). 보안이 중요하다면 제거하고 별도 인증 구성.
*   `--set-env-vars`: 필요한 환경변수를 모두 설정합니다.
    *   `DATABASE_URL`: DB 접속 주소 (`postgresql://`). 내부적으로 비동기 변환을 처리합니다.
    *   `GOOGLE_API_KEY`: Gemini API 사용 (채팅/분석용)
    *   `SECRET_KEY`, `ALGORITHM`: JWT 인증용
    *   `NCP_CLOVASTUDIO_API_KEY`: NAVER Clova Studio API Key (임베딩용)
    *   `NCP_CLOVASTUDIO_BASE_URL`: Clova Studio 게이트웨이 주소


## 4. 데이터베이스 마이그레이션

현재 `Dockerfile`의 실행 명령(`CMD`)에 마이그레이션이 포함되어 있습니다.

```dockerfile
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

따라서 **배포가 성공적으로 완료되어 컨테이너가 시작될 때마다 자동으로 최신 DB 스키마가 적용**됩니다. 별도의 마이그레이션 작업이 필요 없습니다.

## 5. 문제 해결 (Troubleshooting)

*   **배포 실패 시 로그 확인**:
    Google Cloud Console > Cloud Run > 해당 서비스 > **LOGS** 탭에서 상세 오류를 확인하세요.
*   **DB 연결 오류**:
    Supabase는 "Transaction Pooler" (포트 6543)와 "Session Pooler" (포트 5432)가 있습니다.
    *   `DATABASE_URL` (Sync)에는 5432 또는 6543 모두 가능하지만, 알 수 없는 오류 시 5432(Direct connection)를 시도해보세요.
    *   벡터 저장소(`SUPABASE_URL`)는 `postgres` 드라이버와 호환되어야 하므로 `postgresql+asyncpg://` 형식을 정확히 지켜야 합니다.
