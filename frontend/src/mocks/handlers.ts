import { http, HttpResponse } from 'msw'

export const handlers = [
    // 로그인
    http.post('/api/auth/login', async ({ request }) => {
        // const { email, password } = await request.json() as any;
        // 간단한 모의 로직
        return HttpResponse.json({
            user: { id: 1, email: 'test@example.com', name: '김코딩' },
            token: 'mock-jwt-token'
        })
    }),

    // 채용 공고 리스트
    http.get('/api/recruits', () => {
        return HttpResponse.json([
            { id: 1, title: 'Frontend Developer', company: 'Google', deadline: '2026-03-01', tags: ['React', 'Next.js'] },
            { id: 2, title: 'Backend Engineer', company: 'Amazon', deadline: '2026-02-15', tags: ['Java', 'Spring'] },
            { id: 3, title: 'AI Researcher', company: 'OpenAI', deadline: '2026-04-10', tags: ['Python', 'PyTorch'] },
            { id: 4, title: 'Product Manager', company: 'Toss', deadline: '2026-02-28', tags: ['Agile', 'Communication'] },
            { id: 5, title: 'DevOps Engineer', company: 'Netflix', deadline: '2026-03-20', tags: ['AWS', 'Kubernetes'] },
        ])
    }),

    // 포트폴리오 리스트
    http.get('/api/portfolios', () => {
        return HttpResponse.json([
            { id: 1, title: '개인 블로그 프로젝트', type: 'link', url: 'https://blog.example.com', createdAt: '2025-12-01' },
            { id: 2, title: '캡스톤 디자인 PDF', type: 'file', createdAt: '2026-01-10' },
        ])
    }),

    // 자소서 리스트
    http.get('/api/cover-letters', () => {
        return HttpResponse.json([
            { id: 1, title: '구글 2026 상반기 지원', content: '저는...', updatedAt: '2026-01-15' },
            { id: 2, title: '네이버 체험형 인턴', content: '열심히...', updatedAt: '2026-01-02' },
        ])
    }),
]
