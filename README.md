# 모두취업 (구 Pro-NLP Final Project)

이 프로젝트는 **Monorepo** 구조로, 백엔드와 프론트엔드 코드를 하나의 리포지토리에서 통합 관리합니다.

## 📂 Project Structure

```text
pro-nlp-finalproject-nlp-01/
├── common/             # Shared Code (Models, DB, Schemas) - Single Source of Truth
├── backend/            # Backend API Service (FastAPI)
├── jobs/               # Background Worker Service (Heavy AI Tasks)
├── frontend/           # Frontend Client (Next.js)
├── llm-pipeline/       # Legacy/Experimental LLM Scripts
├── docs/               # Documentation
│   ├── conventions/    # Collaboration Guides
│   ├── api/            # API Specs
│   └── db/             # DB Schema
└── README.md           # Project Main Document
```

## 🧠 Technical Resources

- **LLM Pipeline Guide**: [고도화된 LLM 파이프라인 구축 가이드](./docs/LLM_PIPELINE_GUIDE.md)

## 🚀 Getting Started

각 디렉토리의 `README.md`를 참고하여 서비스를 실행해주세요.

- [Backend Guide](./backend/README.md)
- [Frontend Guide](./frontend/README.md)

## 🤝 Collaboration Guide

프로젝트 협업을 위한 가이드는 `docs/conventions` 디렉토리에 정의되어 있습니다.

- **Git Branch Strategy**: [전략 보기](./docs/conventions/GIT_BRANCH_STRATEGY.md)
- **Commit Convention**: [컨벤션 보기](./docs/conventions/COMMIT_CONVENTION.md)
- **PR Convention**: [가이드 보기](./docs/conventions/PR_CONVENTION.md)
