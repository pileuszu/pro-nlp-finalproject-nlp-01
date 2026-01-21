# Multi-Modal Civil Complaint Classifier

멀티모달(이미지 + 텍스트) 기반 민원 분류 연구 프로젝트

## 프로젝트 구조

```
study-multi-modal-civil-complaint-classifier/
├── notebooks/              # Jupyter 노트북 (실험 및 탐색)
├── src/                    # 소스 코드
│   ├── models/            # 모델 정의
│   ├── data/              # 데이터 로더 및 전처리
│   ├── training/          # 학습 스크립트
│   ├── evaluation/        # 평가 스크립트
│   └── utils/             # 유틸리티 함수
├── data/                   # 데이터 저장소
│   ├── raw/               # 원본 데이터
│   ├── processed/         # 전처리된 데이터
│   └── external/          # 외부 데이터
├── models/                # 학습된 모델 저장
├── configs/               # 설정 파일 (YAML/JSON)
├── experiments/           # 실험 결과
├── scripts/               # 실행 스크립트
├── logs/                  # 로그 파일
└── requirements.txt        # 패키지 의존성
```

## 설치

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

## 사용 방법

### 노트북 실행
```bash
jupyter notebook notebooks/
```

### 학습 실행
```bash
python scripts/train.py --config configs/default.yaml
```

### 평가 실행
```bash
python scripts/evaluate.py --model_path models/best_model.pt
```

## 모델

- **KoCLIP**: 한국어 특화 CLIP 모델 (`Bingsu/clip-vit-base-patch32-ko`)
- **Task**: 44개 민원 유형 분류

## 데이터

민원 데이터는 이미지와 텍스트로 구성됩니다.

## 실험

실험 결과는 `experiments/` 디렉토리에 저장됩니다.

## 라이선스

MIT License

