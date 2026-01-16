# Frontend Implementation Plan

본 문서는 **취업/자소서/포트폴리오 관리형 웹 서비스** 구축을 위한 프론트엔드 기술 스택 및 구현 전략을 정의합니다.

## 1. 기술 스택 (Tech Stack)

### 🏗️ Framework & Language
- **Framework**: Next.js 14 (App Router)
  - **이유**: SEO 최적화(공고 페이지), 복잡한 라우팅 구조 관리, SSR/RSC를 통한 성능 이점, 향후 AI 기능 연동 용이성.
- **Language**: TypeScript
  - **이유**: 데이터(자소서, 공고, 포트폴리오 등)의 명확한 타입 정의, 유지보수성 및 협업 효율 증대.

### 🗃️ State Management
- **Server State**: TanStack Query (React Query)
  - **용도**: 기업 공고 리스트, 자소서 조회, 포트폴리오 목록 등 비동기 데이터 관리.
- **Client State**: Zustand
  - **용도**: 로그인 세션, 모달 UI, 단계별 폼 진행 상태 등 전역 UI 상태 관리.

### 🎨 Styling
- **CSS Framework**: Tailwind CSS
- **UI Component Library**: shadcn/ui
  - **이유**: 빠른 UI 구현, 높은 커스터마이징 자유도, 다크모드 용이, 취업 포트폴리오 프로젝트 표준 스택.

### 📝 Form & Validation
- **Library**: React Hook Form + Zod
  - **용도**: 로그인, 회원가입, 자소서 작성, 포트폴리오 등록 등 복잡한 폼 처리 및 유효성 검증.

### 🔐 Authentication & Network
- **Auth**: JWT (JSON Web Token)
- **HTTP Client**: Axios
  - **전략**: Interceptor를 활용한 토큰 자동 주입 및 에러 처리 표준화.

---

## 2. 폴더 구조 (Directory Structure)




`src` 폴더를 기반으로 **확장성**과 **협업**에 유리한 **Route Groups** 구조를 채택합니다.
`(...)` 폴더는 URL에 영향을 주지 않으면서 **레이아웃(Layout) 범위**를 결정합니다.

```text
src/
 ├── app/
 │   │
 │   ├── (public)/               # [레이아웃] 헤더 + 푸터 (쇼케이스용)
 │   │   ├── layout.tsx          # Public 전용 레이아웃
 │   │   ├── page.tsx            # 메인: 채용 공고 리스트
 │   │   └── recruit/
 │   │       └── [id]/           # 상세: 공고 보기
 │   │
 │   ├── (auth)/                 # [레이아웃] 헤더 없음, 중앙 정렬 (집중형)
 │   │   ├── layout.tsx          # Auth 전용 레이아웃
 │   │   ├── login/              # 로그인
 │   │   └── signup/             # 회원가입
 │   │
 │   └── (workspace)/            # [레이아웃] 사이드바 + 탑바 (작업 공간)
 │       ├── layout.tsx          # Workspace 전용 레이아웃 (Sidebar 포함)
 │       └── my/
 │           ├── dashboard/      # 대시보드
 │           ├── profile/        # 개인정보
 │           ├── cover-letters/  # 자소서 관리
 │           │   ├── page.tsx    # 목록
 │           │   └── [id]/       # ⭐️ 에디터 (AI 첨삭 기능 탑재)
 │           └── portfolios/     # 포트폴리오 관리
 │               ├── page.tsx    # 목록/등록/연동 (Tab UI)
 │               └── [id]/       # 상세 수정
 │
 ├── components/                 # 컴포넌트
 │   ├── layout/                 # Header, Sidebar, Footer 등
 │   ├── ui/                     # 버튼, 인풋 (shadcn/ui)
 │   └── domains/                # 도메인별 (RecruitCard, ResumeForm...)
 ...
```

---

## 3. 핵심 구조 변경 사유 & 유저 플로우 매핑
1. **레이아웃의 물리적 분리 (Scalability)**:
   - `(public)`, `(auth)`, `(workspace)`가 각각 완벽히 다른 `layout.tsx`를 가집니다.
   - 전역 레이아웃에서 `if (path === '/login')` 같은 지저분한 분기 처리를 할 필요가 없어 협업 시 코드 충돌이 없습니다.

2. **작업 공간(Workspace) 명확화**:
   - `dashboard` 대신 `(workspace)`라는 이름을 사용하여, 단순 조회를 넘어 '자소서 작성', '포트폴리오 관리' 등의 **생산성 작업**이 이루어지는 공간임을 명확히 했습니다.

3. **유저 및 데이터 플로우**:
   - **Main Flow**: `(public)/page.tsx` (메인 공고) -> `recruit/[id]` (상세)
   - **Auth Flow**: `(auth)/login` (로그인) -> **Redirect Logic** (포트폴리오 없으면 `my/portfolios`로 강제 이동)

   - **Work Flow**: `my/portfolios` (등록) -> `my/cover-letters/[id]` (에디터 진입, Query Param으로 공고 정보 연동)

---

   - **Work Flow**: `my/portfolios` (등록) -> `my/cover-letters/[id]` (에디터 진입, Query Param으로 공고 정보 연동)

---

## 4. Key Features from Lean Canvas (Agent-Driven)

### 🤖 1. Agent 기반 취업 비서 (Core Value)
단순한 공고 나열이 아닌, **"탐색 → 분석 → 작성"**의 전 과정을 자동화하는 Agent UI를 구현합니다.
- **포트폴리오 파싱**: GitHub Repo, Notion 링크 입력 시 Agent가 이를 분석하여 핵심 역량을 추출하는 **Progress UI** (업스테이지 Document Parse 등 활용).
- **공고 적합성 분석 (Fit check)**: 공고 상세 페이지 진입 시, 내 포트폴리오와 비교하여 **매칭 점수(%)**와 **부족한 역량**을 시각화.
- **자소서 초안 생성 (Auto-Drafting)**: "이 기업 맞춤 자소서 써줘" 버튼 클릭 시, 내 경험과 기업 인재상을 매핑하여 초안을 스트리밍(`Streaming`)으로 작성.

### 🎯 2. 개인 맞춤형 공고 추천 (Curated UI)
- **메인 페이지**: 단순 리스트가 아닌 **"오늘의 추천 공고 3선"**, **"내 기술 스택과 일치하는 공고"** 위젯 배치.
- **리마인드**: 자격증 만료, 공고 마감 임박 알림을 위한 **Notification Center** (Toaster).

### 💰 3. 수익화 모델 대응 (Subscription)
- **Plan UI**: 프리미엄 기능(무제한 생성, 고급 기업 추천) 접근 시 **"업그레이드 유도 모달"** 및 기능 잠금(Lock) 처리를 고려한 컴포넌트 설계 (`<PremiumGuard>`).

---

## 5. Mocking Strategy (Backend-less Development)
백엔드 API가 준비되지 않은 상태에서도 UI를 완벽하게 구현하기 위해 **MSW (Mock Service Worker)**를 도입합니다.

- **도구**: `msw` (Browser Level Interception)
- **전략**:
  1. API 명세(JSON) 합의
  2. `src/mocks/handlers.ts` 구현
  3. UI 개발 (실제 Network 요청처럼 작성)
  4. 백엔드 배포 시 MSW Off -> 즉시 연동
- [상세 전략 문서 보기](./MOCKING_STRATEGY.md)
