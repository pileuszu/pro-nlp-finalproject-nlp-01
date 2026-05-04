import { useAuthStore } from "@/stores/useAuthStore";

export function isMockMode(): boolean {
    if (typeof window === 'undefined') return false;
    return window.location.hostname.includes('github.io') || process.env.NEXT_PUBLIC_MOCK === 'true';
}

// Helper to normalize paths and include basePath for GitHub Pages
function normalizeMockPath(path: string): string {
    const isGitHubPages = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
    const basePath = isGitHubPages ? '/pro-nlp-finalproject-nlp-01' : '';
    
    let cleanPath = path;
    if (path.startsWith('http')) {
        try {
            cleanPath = new URL(path).pathname;
        } catch (e) {}
    }
    
    if (!cleanPath.startsWith('/')) cleanPath = '/' + cleanPath;
    
    // Remove duplicate basePath if present
    if (basePath && cleanPath.startsWith(basePath)) {
        return cleanPath;
    }
    return `${basePath}${cleanPath}`;
}

export function getApiUrl(path: string): string {
    if (isMockMode()) {
        return normalizeMockPath(path);
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

// Global Fetch Interceptor for Mock Mode
if (typeof window !== 'undefined' && isMockMode()) {
    const originalFetch = window.fetch;
    window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : (input as URL).toString();
        // If it's a request for mock data itself, use original fetch to avoid infinite loop
        if (url.includes('/mock-data/')) {
            return originalFetch(input, init);
        }
        return mockFetch(url, init);
    };
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
    // If global fetch is already patched, this will automatically call mockFetch via window.fetch
    return fetch(url, options);
}

async function mockFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const method = options.method?.toUpperCase() || 'GET';
    const isGitHubPages = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
    const basePath = isGitHubPages ? '/pro-nlp-finalproject-nlp-01' : '';
    
    // Extract path from URL
    let path = url;
    if (url.startsWith('http')) {
        try {
            path = new URL(url).pathname;
        } catch (e) {}
    }
    const cleanPath = path.split('?')[0];

    const jsonRes = (data: any, status = 200) => new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });

    // 1. Intercept Auth
    if ((cleanPath.includes('/auth/login') || cleanPath.includes('/auth/test-login')) && method === 'POST') {
        try {
            const body = JSON.parse(options.body as string);
            const email = body.email || '';
            const role = body.role || '';
            let targetEmail = email;
            if (role && cleanPath.includes('test-login')) {
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

    // 2. Intercept Writes (POST/PUT/PATCH/DELETE)
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        if (cleanPath.includes('/portfolios/upload') || cleanPath.includes('/portfolios/analyze')) {
            return jsonRes({ success: true, portfolio_id: 6, status: 'completed' });
        }
        if (cleanPath.includes('/integrations/github/auth-url') || cleanPath.includes('/integrations/notion/auth-url')) {
            return jsonRes({ url: "#" });
        }
        return jsonRes({ success: true, message: "Mocking 환경에서 처리되었습니다." });
    }

    // 3. Handle Read operations (GET)
    try {
        let mockFile = '';
        if (cleanPath.includes('/recruits')) mockFile = 'recruitments.json';
        else if (cleanPath.includes('/portfolios')) mockFile = 'portfolios.json';
        else if (cleanPath.includes('/cover-letters')) mockFile = 'cover_letters.json';
        else if (cleanPath.includes('/cover-letter-items')) mockFile = 'cover_letter_items.json';
        else if (cleanPath.includes('/notifications')) mockFile = 'notifications.json';
        else if (cleanPath.includes('/integrations')) mockFile = 'user_integrations.json';
        else if (cleanPath.includes('/users/me')) {
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

            const idMatch = cleanPath.match(/\/(\d+)$/);
            if (idMatch) {
                const id = idMatch[1];
                const item = data.find((i: { id: string }) => String(i.id) === id);
                return item ? jsonRes(item) : jsonRes({ detail: "Not Found" }, 404);
            }

            if (cleanPath.includes('/recruits')) {
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

    // Default to original fetch for anything else (like internal Next.js assets)
    // but in mock mode, if we reach here for an API call, it's a 404
    return jsonRes({ detail: "Mock data not found" }, 404);
}
