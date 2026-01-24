# Render Deployment Guide (FastAPI + Docker)

본 문서는 `backend` 브랜치의 코드를 Render.com에 배포하는 방법을 단계별로 안내합니다.

## 1. Render 사전 준비
1. [Render.com](https://render.com/) 가입 및 로그인.
2. 대시보드에서 **New +** > **Web Service** 선택.
3. GitHub 계정을 연결하고 `pro-nlp-finalproject-nlp-01` 저장소를 선택합니다.

## 2. 서비스 설정 (Settings)
배포 시 아래와 같이 설정해 주세요:

| 항목 | 설정값 |
| :--- | :--- |
| **Name** | `pro-nlp-backend` (자유롭게 지정) |
| **Region** | `Singapore` (South East Asia) |
| **Branch** | `backend` (또는 `develop`) |
| **Language** | `Docker` |
| **Docker Development Context** | `backend` (중요: 루트가 아닌 backend 폴더 기준) |
| **DockerfilePath** | `./Dockerfile` |

## 3. 환경 변수 설정 (Environment Variables)
**Advanced** 섹션에서 아래 변수들을 반드시 추가해야 합니다:

- `DATABASE_URL`: 알려주신 Supabase Pooler 주소 (비밀번호 포함)
- `SECRET_KEY`: 자동 생성된 키 또는 본인의 비밀 키
- `ALGORITHM`: `HS256`
- `PYTHONPATH`: `/app`

## 4. 자동 배포 (Continuous Deployment)
1. Render의 서비스 페이지에서 **Settings** > **Deploy Hook** 항목을 찾습니다.
2. 생성된 URL을 복사하여 GitHub 저장소의 **Settings > Secrets and variables > Actions**에 `RENDER_DEPLOY_HOOK_URL`이라는 이름으로 등록해 두면, 코드 푸시 시 자동으로 배포가 시작됩니다.

## 5. 서버 잠듬 방지 (Keep Awake)
무료 티어는 15분 미사용 시 서버가 잠듭니다.
1. [cron-job.org](https://cron-job.org/) 가입.
2. 본인의 앱 주소(`https://xxx.onrender.com/api/health`)를 10분 간격으로 ping 하도록 설정하세요.
