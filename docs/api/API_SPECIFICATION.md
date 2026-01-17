# API 명세서 (API Specification)

이 문서는 AI 채용 플랫폼의 프론트엔드와 백엔드 간 협업을 위한 상세 API 규격을 정의합니다. Postman 등의 도구를 활용한 테스트 및 실제 구현의 기준이 됩니다.

## 공통 가이드

### 기본 환경
- **Base URL**: `https://api.pro-nlp.com/api` (또는 로컬 환경: `http://localhost:8080/api`)
- **Content-Type**: `application/json`
- **인증 방식**: Bearer Token 인증 (로그인이 필요한 모든 API는 Header에 `Authorization: Bearer {token}` 포함 필수)

### 공통 에러 응답 구조
에러 발생 시 다음과 같은 일관된 응답 구조를 반환합니다.

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자에게 보여줄 에러 메시지",
    "details": "개발용 디버깅 정보 (선택 사항)"
  }
}
```

### 주요 상태 코드
- `200 OK`: 요청 성공
- `201 Created`: 생성 요청 성공 (POST)
- `400 Bad Request`: 필수 파라미터 누락 또는 유효하지 않은 데이터
- `401 Unauthorized`: 인증 토큰 누락 또는 만료
- `403 Forbidden`: 접근 권한 없음
- `404 Not Found`: 요청한 리소스를 찾을 수 없음
- `500 Internal Server Error`: 서버 내부 오류

---

## 1. 인증 (Authentication)

### POST `/api/auth/login`
사용자 인증을 수행하고 세션 토큰을 반환합니다.

**요청 본문:**
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**응답 성공 (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "김코딩"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답 실패 (401 Unauthorized):**
```json
{
  "success": false,
  "error": { "code": "AUTH_001", "message": "이메일 또는 비밀번호가 일치하지 않습니다." }
}
```

### POST `/api/auth/signup`
신규 회원가입을 처리합니다.

**요청 본문:**
```json
{
  "email": "test@example.com",
  "password": "password123",
  "name": "김코딩"
}
```

**응답 성공 (201 Created):**
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다."
}
```

### GET `/api/auth/me`
현재 로그인된 사용자의 프로필 정보를 조회합니다.

**필수 헤더:** `Authorization: Bearer {token}`

**응답 성공 (200 OK):**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "김코딩"
}
```

---

## 2. 채용 공고 (Recruitments)

### GET `/api/recruits`
채용 공고 목록을 조회합니다. 필터링, 키워드 검색 및 페이지네이션을 지원합니다.

**쿼리 파라미터:**
| 필드 | 타입 | 필수 여부 | 설명 | 예시 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | Integer | - | 조회할 페이지 번호 (기본: 1) | `1` |
| `limit` | Integer | - | 페이지당 항목 수 (기본: 10) | `20` |
| `category` | String | - | 직무 카테고리 필터 | `frontend` |
| `techStack` | String | - | 기술 스택 필터 (콤마 구분) | `React,TS` |
| `keyword` | String | - | 검색어 (회사명, 공고명) | `구글` |
| `sort` | String | - | 정렬 (`latest`, `popular`) | `popular` |

**응답 성공 (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "프론트엔드 개발자",
      "company": "Google",
      "startDate": "2026-02-01",
      "deadline": "2026-03-01",
      "tags": ["React", "TypeScript"]
    }
  ],
  "meta": { "total": 128, "page": 1, "limit": 10, "totalPages": 13 }
}
```

### GET `/api/recruits/:id`
특정 채용 공고의 상세 정보를 조회합니다.

**응답 성공 (200 OK):**
```json
{
  "id": 1,
  "title": "프론트엔드 개발자",
  "company": "Google",
  "startDate": "2026-02-01",
  "deadline": "2026-03-01",
  "tags": ["React", "TypeScript"],
  "content": "상세 채용 공고 내용..."
}
```

### GET `/api/recruits/recommend`
사용자 커리어 데이터 기반 AI 추천 공고 목록을 조회합니다.

**쿼리 파라미터:** 
| 필드 | 타입 | 필수 여부 | 설명 | 예시 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | Integer | - | 페이지 번호 | `1` |
| `limit` | Integer | - | 페이지당 수 | `9` |

---

## 3. 포트폴리오 (Portfolios)

**필수 헤더 (모든 API 공통):** `Authorization: Bearer {token}`

### GET `/api/portfolios`
로그인한 사용자의 포트폴리오 목록을 조회합니다.

**쿼리 파라미터:**
| 필드 | 타입 | 필수 여부 | 설명 | 예시 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | Integer | - | 페이지 번호 | `1` |
| `limit` | Integer | - | 페이지당 수 | `10` |

**응답 성공 (200 OK):**
```json
{
  "items": [{ "id": 1, "title": "개인 프로젝트", "type": "github", "createdAt": "2026-01-15" }],
  "meta": { "total": 5, "page": 1, "limit": 10, "totalPages": 1 }
}
```

### POST `/api/portfolios`
새 포트폴리오를 등록합니다.

**요청 본문:**
```json
{
  "title": "내 기술 블로그",
  "type": "link",
  "url": "https://...",
  "description": "설명...",
  "content": "추출된 텍스트..."
}
```

**응답 성공 (201 Created):**
```json
{ "id": 123, "title": "내 기술 블로그", "createdAt": "2026-01-18" }
```

### PATCH `/api/portfolios/:id`
기존 포트폴리오 정보를 수정합니다.

**요청 본문:** `POST /api/portfolios`와 동일 (변경이 필요한 필드만 포함 가능)

**응답 성공 (200 OK):** 수정된 포트폴리오 객체

### DELETE `/api/portfolios/:id`
포트폴리오를 삭제합니다. **응답 성공 (200 OK)**

### POST `/api/portfolios/analyze`
GitHub, URL, 파일 등에서 프로젝트 데이터를 추출하는 AI 분석을 수행합니다.

**요청 본문:**
```json
{
  "source": "https://github.com/user/repo",
  "type": "github",
  "customPrompt": "특정 부분 위주로 분석해줘 (선택)"
}
```

**응답 성공 (200 OK):** 분석된 프로젝트 항목들의 배열

---

## 4. 자기소개서 (Cover Letters)

**필수 헤더:** `Authorization: Bearer {token}`

### GET `/api/cover-letters`
자소서 목록을 조회합니다.

**쿼리 파라미터:**
| 필드 | 타입 | 필수 여부 | 설명 | 예시 |
| :--- | :--- | :--- | :--- | :--- |
| `recruitId` | Integer | - | 특정 공고 관련 자소서만 필터링 | `1` |
| `page` | Integer | - | 페이지 번호 | `1` |
| `limit` | Integer | - | 페이지당 수 | `10` |

**응답 성공 (200 OK):**
```json
{
  "items": [
    { "id": 1, "title": "[지원] Google", "recruitId": 1, "updatedAt": "2026-01-15" }
  ],
  "meta": { "total": 12, "page": 1, "limit": 10, "totalPages": 2 }
}
```

### GET `/api/cover-letters/:id`
특정 자소서를 상세 조회합니다.

**응답 성공 (200 OK):**
```json
{
  "id": 1,
  "title": "제목",
  "recruitId": 1,
  "questions": [
    { "id": 1642, "question": "지원동기", "answer": "저는..." }
  ]
}
```

### POST `/api/cover-letters`
새 자소서를 작성합니다.

**요청 본문:**
```json
{
  "title": "구글 지원 자소서",
  "recruitId": 1,
  "questions": [
    { "question": "지원동기", "answer": "..." }
  ]
}
```

**응답 성공 (201 Created):** 생성된 자소서 객체

### PATCH `/api/cover-letters/:id`
자소서를 수정합니다.

**요청 본문:** `POST /api/cover-letters`와 동일 (부분 수정 가능)

**응답 성공 (200 OK):** 수정된 자소서 객체

### DELETE `/api/cover-letters/:id`
자소서를 삭제합니다. **응답 성공 (200 OK)**

### POST `/api/cover-letters/generate`
AI를 통해 자소서 초안 또는 가이드를 생성합니다.

**요청 본문:**
```json
{
  "mode": "draft",
  "tone": "professional",
  "focus": "기술 스택",
  "portfolioIds": [1, 2],
  "question": "지원동기"
}
```

**응답 성공 (200 OK):**
```json
{
  "result": "AI가 생성한 텍스트 결과물..."
}
```
