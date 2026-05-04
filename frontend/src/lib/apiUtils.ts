import { useAuthStore } from "@/stores/useAuthStore";

export function isMockMode(): boolean {
    if (typeof window === 'undefined') return false;
    // Enable mock mode if hostname contains github.io or if explicitly set in env
    return window.location.hostname.includes('github.io') || process.env.NEXT_PUBLIC_MOCK === 'true';
}

export function getApiUrl(path: string): string {
    if (isMockMode()) {
        // In mock mode, we point to the public/mock-data directory
        // We'll handle the actual fetching in fetchWithAuth
        return path;
    }

    let baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    if (baseUrl && !baseUrl.startsWith('http')) {
        baseUrl = `https://${baseUrl}`;
    }
    const prefix = process.env.NEXT_PUBLIC_API_URL_PREFIX || '/api';

    const cleanPath = path.startsWith('http')
        ? path
        : path.startsWith('/') ? path : `/${path}`;

    if (cleanPath.startsWith(prefix)) {
        return `${baseUrl}${cleanPath}`;
    }

    return `${baseUrl}${prefix}${cleanPath}`;
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
    if (isMockMode()) {
        return mockFetch(url, options);
    }

    const token = useAuthStore.getState().token;
    const headers: HeadersInit = {
        ...options.headers,
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    };

    if (options.method && !["GET", "HEAD"].includes(options.method.toUpperCase())) {
        const isFormData = options.body instanceof FormData;
        if (!isFormData && !(headers as Record<string, string>)["Content-Type"]) {
            (headers as Record<string, string>)["Content-Type"] = "application/json";
        }
    }

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
        useAuthStore.getState().logout();
        if (typeof window !== 'undefined') {
            window.location.href = '/login';
        }
    }

    return res;
}

async function mockFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const method = options.method?.toUpperCase() || 'GET';
    const path = url.split('?')[0];
    const isGitHubPages = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
    const basePath = isGitHubPages ? '/pro-nlp-finalproject-nlp-01' : '';

    // 1. Intercept Auth
    if (path.includes('/auth/login') && method === 'POST') {
        try {
            const body = JSON.parse(options.body as string);
            const email = body.email || '';
            
            // Allow login for exhibit users
            if (email.includes('exhibit')) {
                const usersRes = await fetch(`${basePath}/mock-data/users.json`);
                const users = await usersRes.json();
                const user = users.find((u: { email: string }) => u.email === email);
                
                if (user) {
                    return new Response(JSON.stringify({
                        access_token: "mock-token-" + user.id,
                        token_type: "bearer",
                        user: user
                    }), { status: 200, headers: { 'Content-Type': 'application/json' } });
                }
            }
        } catch (e) {
            console.error("Login mock error:", e);
        }
        return new Response(JSON.stringify({ detail: "테스트 계정 정보를 확인해주세요." }), { status: 401 });
    }

    const isAuth = path.includes('/auth/register') || path.includes('/auth/kakao');
    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(method);

    if (isAuth || (isWrite && !path.includes('/auth/login'))) {
        return new Response(JSON.stringify({ detail: "현재 Mocking 에서 지원하지않는 기능입니다." }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' }
        });
    }

    // 2. Handle Read operations (GET)
    try {
        let mockFile = '';
        // Map common endpoints to mock files
        if (path.includes('/recruits')) {
            mockFile = 'recruitments.json';
        } else if (path.includes('/portfolios')) {
            mockFile = 'portfolios.json';
        } else if (path.includes('/cover-letters')) {
            mockFile = 'cover_letters.json';
        } else if (path.includes('/notifications')) {
            mockFile = 'notifications.json';
        } else if (path.includes('/users/me')) {
            const token = useAuthStore.getState().token || '';
            const userId = token.replace('mock-token-', '');
            
            const usersRes = await fetch(`${basePath}/mock-data/users.json`);
            const users = await usersRes.json();
            const me = users.find((u: { id: string }) => u.id === userId) || users[0];
            return new Response(JSON.stringify(me), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        if (mockFile) {
            const res = await fetch(`${basePath}/mock-data/${mockFile}`);
            const rawData = await res.json();

            // Normalize data (ensure arrays are actual arrays)
            const normalize = (obj: any) => {
                if (!obj || typeof obj !== 'object') return obj;
                const arrayFields = ['tags', 'questions', 'tech_stack', 'strengths'];
                arrayFields.forEach(field => {
                    if (typeof obj[field] === 'string') {
                        try {
                            obj[field] = JSON.parse(obj[field]);
                        } catch (e) {
                            obj[field] = [];
                        }
                    }
                });
                return obj;
            };

            const data = Array.isArray(rawData) ? rawData.map(normalize) : normalize(rawData);

            // Handle list vs detail
            const idMatch = path.match(/\/(\d+)$/);
            if (idMatch) {
                const id = idMatch[1];
                const item = data.find((i: { id: string }) => String(i.id) === id);
                if (item) {
                    return new Response(JSON.stringify(item), { status: 200, headers: { 'Content-Type': 'application/json' } });
                }
                return new Response(JSON.stringify({ detail: "Not Found" }), { status: 404 });
            }

            // Handle filtering/pagination (simple mock)
            if (path.includes('/recruits')) {
                return new Response(JSON.stringify({
                    items: data.slice(0, 10),
                    meta: { total: data.length, page: 1, limit: 10, totalPages: 1 }
                }), { status: 200, headers: { 'Content-Type': 'application/json' } });
            }

            return new Response(JSON.stringify(data), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }
    } catch (e) {
        console.error("Mock fetch error:", e);
    }

    return new Response(JSON.stringify({ detail: "Mock data not found" }), { status: 404 });
}
