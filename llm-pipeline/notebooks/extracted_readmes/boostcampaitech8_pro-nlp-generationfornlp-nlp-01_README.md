# NLP Generation Project

## 1. 대회 소개 (Competition Info)
본 대회는 소형 언어 모델(Small LLM)을 활용하여 수능(CSAT) 국어 및 사회 과목의 문제를 효과적으로 해결하는 모델을 개발하는 것을 목표로 합니다. 대형 모델(GPT-4, Claude 등)에 버금가는 성능을 목표로 한국어와 수능 시험의 특성을 반영한 최적화된 모델을 구축합니다.

## 2. 리더보드 (Leaderboard)

| Rank | Team | Score | Model | Methods | Date |
|:---:|:---:|:---:|:---:|:---:|:---:|
| - | **NLP-01** | - | - | - | - |

## 3. 팀 소개 (Team Introduction)

### Members
<table width="100%">
    <tr>
        <td align="center" width="16%">
            <a href="https://github.com/Jinyoung001">
                <img src="https://github.com/Jinyoung001.png" width="100px;" alt=""/>
                <br />
                <b>강진영</b>
            </a>
        </td>
        <td align="center" width="16%">
            <a href="https://github.com/pileuszu">
                <img src="https://github.com/pileuszu.png" width="100px;" alt=""/>
                <br />
                <b>김지환</b>
            </a>
        </td>
        <td align="center" width="16%">
            <a href="https://github.com/CoramDeo03">
                <img src="https://github.com/CoramDeo03.png" width="100px;" alt=""/>
                <br />
                <b>박준하</b>
            </a>
        </td>
        <td align="center" width="16%">
            <a href="https://github.com/gongryong">
                <img src="https://github.com/gongryong.png" width="100px;" alt=""/>
                <br />
                <b>배민석</b>
            </a>
        </td>
        <td align="center" width="16%">
            <a href="https://github.com/juyeonbae">
                <img src="https://github.com/juyeonbae.png" width="100px;" alt=""/>
                <br />
                <b>배주연</b>
            </a>
        </td>
        <td align="center" width="16%">
            <a href="https://github.com/jjw0071">
                <img src="https://github.com/jjw0071.png" width="100px;" alt=""/>
                <br />
                <b>정제원</b>
            </a>
        </td>
    </tr>
</table>

### Roles
| Member | Role |
|:---:|:---|
| **강진영** | 모델 탐색, 하이퍼 파라미터 튜닝, 앙상블, 모델 양자화, 데이터셋 튜닝, 프롬프트 엔지니어링 |
| **김지환** | 파이프라인 초안 구현, 분산 샤드 다운 구현, 모델 비교, 리팩토링 |
| **박준하** | EDA, 추가 데이터셋 구축, 모델 양자화 |
| **배민석** | EDA, 프롬프트 엔지니어링, DPO |
| **배주연** | EDA, 데이터 증강, RAG 구현 |
| **정제원** | EDA, 추가 데이터셋 구축, RAG 구현 |

## 4. 프로젝트 개요 (Project Overview)
*   **개발 환경**: Linux (Ubuntu), Python 3.10
*   **협업 툴**: GitHub, Slack, Notion, WandB
*   **주요 접근법**:
    *   RAG (Retrieval-Augmented Generation)
    *   Prompt Engineering
    *   Fine-tuning (PEFT, LoRA)

## 5. 프로젝트 구조 (Directory Structure)

```bash
├── .github/              # Github Action 및 Template
├── notebooks/            # EDA 및 실험용 Jupyter Notebook
│   ├── analysis/
│   ├── data_engineering/
│   ├── evaluation/
│   └── modeling/
├── scripts/              # 서버 설정 및 자동화 스크립트
│   ├── setup_part1.sh    # 유저 및 SSH 설정
│   └── setup_part2.sh    # 환경 설정 및 데이터 다운로드
├── src/                  # 메인 소스 코드
├── .env                  # (Git Ignored) 환경 변수 및 시크릿
├── .gitignore
├── requirements.txt
└── README.md
```

## 6. 진행 상황 & 타임라인 (Timeline)
### 📅 Project Timeline (3 Weeks)
**2025.12.15 (Mon) 10:00 ~ 2026.01.06 (Tue) 19:00**

- [ ] **Week 1 (12/15 ~ 12/21)**
    - EDA 및 베이스라인 코드 분석
    - 팀 병합 (12/17 16:00 까지)
    - 리더보드 오픈 (12/17 10:00) 및 초기 제출
- [ ] **Week 2 (12/22 ~ 12/28)**
    - 데이터 전처리 및 증강 (Data Augmentation)
    - 모델 실험 (Fine-tuning, RAG, Prompt Engineering)
    - 중간 성능 점검
- [ ] **Week 3 (12/29 ~ 01/06)**
    - 모델 고도화 및 하이퍼파라미터 튜닝
    - 앙상블 (Ensemble) 적용
    - **최종 제출 및 리더보드 마감 (01/06 19:00)**

## 7. 실행 방법 (How to Run)

### 7.1 환경 변수 설정 (.env)
프로젝트 루트(`Pro-NLP-GenerationForNLP-NLP-01/`)에 `.env` 파일을 생성합니다. (보안상 Git에 포함되지 않음)

```properties
# .env example
NLP_USERS="jinyoung001 pileuszu ..."
NLP_EMAIL_jinyoung001="example@gmail.com"
DATA_URL="https://..."
CODE_URL="https://..."
```

### 7.2 서버 초기화 (Part 1)
Root 권한으로 스크립트를 실행하여 유저를 생성하고 SSH 키를 발급합니다.
```bash
cd scripts
sudo ./setup_part1.sh
```
> **중요**: 스크립트 실행 마지막에 출력되는 **SSH Public Key**를 복사하여 Github 계정에 등록해야 `setup_part2.sh`가 정상 작동합니다.

### 7.3 환경 구축 및 데이터 로드 (Part 2)
레포지토리 Clone, 가상환경(.venv) 생성, 데이터 다운로드를 자동으로 수행합니다.
```bash
# 사용법: sudo ./setup_part2.sh [실행할_유저명]
sudo ./setup_part2.sh pileuszu
```

### 7.4 가상환경 활성화
```bash
source .venv/bin/activate
```
