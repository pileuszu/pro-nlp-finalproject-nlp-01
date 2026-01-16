# Mocking Strategy for Frontend Development

백엔드 개발이 완료되지 않은 상태에서도 프론트엔드 개발 및 테스트를 원활하게 진행하기 위한 **Mocking 전략**입니다.

## 1. MSW (Mock Service Worker) 도입 ✅ (강력 추천)
서비스 워커(Service Worker)를 사용하여 네트워크 요청을 가로채고(Intercept), 실제 백엔드 API인 것처럼 모의 응답(Mock Response)을 내려주는 도구입니다.

### 장점
- **실제 코드 수정 불필요**: `fetch`나 `axios` 코드를 전혀 건드리지 않고, 브라우저 레벨에서 네트워크만 가로챕니다. 백엔드가 붙으면 MSW만 끄면 됩니다.
- **모든 상태 시뮬레이션**: 성공(`200`), 실패(`400`, `500`), 로딩 지연(`delay`) 등을 자유자재로 테스트할 수 있습니다.
- **Storybook 연동**: UI 컴포넌트 테스트 시에도 동일한 Mock 데이터를 사용할 수 있습니다.

### 구현 예시
`src/mocks/handlers.ts`
```typescript
import { http, HttpResponse } from 'msw'

export const handlers = [
  // 로그인 API Mocking
  http.post('/api/auth/login', () => {
    return HttpResponse.json({
      access_token: 'mock-jwt-token',
      user: { id: 1, name: 'Test User' },
    })
  }),
  
  // 공고 리스트 Mocking
  http.get('/api/recruit', () => {
    return HttpResponse.json([
      { id: 1, title: 'Frontend Developer', company: 'Google' },
      { id: 2, title: 'Backend Developer', company: 'Amazon' },
    ])
  }),
]
```

---

## 2. Next.js API Routes (Route Handlers) 활용
Next.js의 백엔드 기능인 Route Handlers(`app/api/...`)를 임시 백엔드로 사용하는 방법입니다.

### 장점
- **백엔드 로직 이해**: 실제 백엔드와 유사하게 Request/Response를 다루므로 백엔드 로직을 이해하는 데 도움이 됩니다.
- **쉬운 환경 설정**: 별도의 라이브러리 설치 없이 Next.js 기능만으로 구현 가능합니다.

### 단점
- 나중에 실제 백엔드 API 경로(`http://localhost:8080/api...`)로 교체할 때 코드를 수정해야 할 수도 있습니다. (Proxy 설정으로 완화 가능)

---

## 3. 추천 워크플로우 (MSW 방식)

1.  **API 명세서(Swagger/Notion) 합의**: 백엔드 팀과 URL, Request, Response JSON 형태를 먼저 확정합니다.
2.  **MSW 핸들러 작성**: 합의된 명세를 바탕으로 `src/mocks/handlers.ts`에 가짜 응답을 작성합니다.
3.  **UI 개발**: 프론트엔드는 실제 API가 있는 것처럼 개발을 진행합니다.
4.  **통합**: 백엔드 개발이 완료되면 MSW를 끄(`enabled: false`)거나 제거하면, 코드 수정 없이 즉시 실제 서버와 통신됩니다.
