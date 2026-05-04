import { useAuthStore } from "@/stores/useAuthStore";

export function isMockMode(): boolean {
    if (typeof window === 'undefined') return false;
    return window.location.hostname.includes('github.io') || process.env.NEXT_PUBLIC_MOCK === 'true';
}

export function getApiUrl(path: string): string {
    const isGitHubPages = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
    const basePath = isGitHubPages ? '/pro-nlp-finalproject-nlp-01' : '';

    if (isMockMode()) {
        const cleanPath = path.startsWith('/') ? path : `/${path}`;
        if (basePath && cleanPath.startsWith(basePath)) {
            return cleanPath;
        }
        return `${basePath}${cleanPath}`;
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

    // Helper to return JSON responses
    const jsonRes = (data: any, status = 200) => new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });

    // 1. Intercept Auth
    if ((path.includes('/auth/login') || path.includes('/auth/test-login')) && method === 'POST') {
        try {
            const body = JSON.parse(options.body as string);
            const email = body.email || '';
            const role = body.role || '';
            let targetEmail = email;
            if (role && path.includes('test-login')) {
                targetEmail = `exhibit_${role}@pro-nlp.ai`;
            }

            if (targetEmail.includes('exhibit')) {
                const usersRes = await fetch(`${basePath}/mock-data/users.json`);
                const users = await usersRes.json();
                const user = users.find((u: { email: string }) => u.email === targetEmail);
                if (user) {
                    return jsonRes({
                        access_token: "mock-token-" + user.id,
                        token_type: "bearer",
                        user: user
                    });
                }
            }
        } catch (e) {}
        return jsonRes({ detail: "테스트 계정 정보를 확인해주세요." }, 401);
    }

    // 2. Intercept Writes (POST/PUT/PATCH/DELETE) - Return dummy success for Demo
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        if (path.includes('/portfolios/upload') || path.includes('/portfolios/analyze')) {
            // Pick a mock portfolio ID for demo flow
            return jsonRes({ success: true, portfolio_id: 6, status: 'completed' });
        }
        if (path.includes('/integrations/github/auth-url') || path.includes('/integrations/notion/auth-url')) {
            return jsonRes({ url: "#" });
        }
        // General success for other writes
        return jsonRes({ success: true, message: "Mocking 환경에서 처리되었습니다." });
    }

    // 3. Handle Read operations (GET)
    try {
        let mockFile = '';
        if (path.includes('/recruits')) mockFile = 'recruitments.json';
        else if (path.includes('/portfolios')) mockFile = 'portfolios.json';
        else if (path.includes('/cover-letters')) mockFile = 'cover_letters.json';
        else if (path.includes('/cover-letter-items')) mockFile = 'cover_letter_items.json';
        else if (path.includes('/notifications')) mockFile = 'notifications.json';
        else if (path.includes('/integrations')) mockFile = 'user_integrations.json';
        else if (path.includes('/users/me')) {
            const token = useAuthStore.getState().token || '';
            const userId = token.replace('mock-token-', '');
            const usersRes = await fetch(`${basePath}/mock-data/users.json`);
            const users = await usersRes.json();
            const me = users.find((u: { id: string }) => String(u.id) === userId) || users[0];
            return jsonRes(me);
        }

        if (mockFile) {
            const res = await fetch(`${basePath}/mock-data/${mockFile}`);
            const rawData = await res.json();

            // Normalize data
            const normalize = (obj: any) => {
                if (!obj || typeof obj !== 'object') return obj;
                const arrayFields = ['tags', 'questions', 'tech_stack', 'strengths'];
                arrayFields.forEach(field => {
                    if (typeof obj[field] === 'string') {
                        try { obj[field] = JSON.parse(obj[field]); } catch (e) { obj[field] = []; }
                    }
                });
                return obj;
            };

            const data = Array.isArray(rawData) ? rawData.map(normalize) : normalize(rawData);

            // Detail mapping
            const idMatch = path.match(/\/(\d+)$/);
            if (idMatch) {
                const id = idMatch[1];
                const item = data.find((i: { id: string }) => String(i.id) === id);
                return item ? jsonRes(item) : jsonRes({ detail: "Not Found" }, 404);
            }

            // List mapping with metadata for recruits
            if (path.includes('/recruits')) {
                return jsonRes({
                    items: data.slice(0, 10),
                    meta: { total: data.length, page: 1, limit: 10, totalPages: 1 }
                });
            }

            return jsonRes(data);
        }
    } catch (e) {
        console.error("Mock fetch error:", e);
    }

    return jsonRes({ detail: "Mock data not found" }, 404);
}
