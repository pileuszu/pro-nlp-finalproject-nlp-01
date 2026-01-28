import { useAuthStore } from "@/stores/useAuthStore";

export function getApiUrl(path: string): string {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const prefix = process.env.NEXT_PUBLIC_API_URL_PREFIX || '/api';

    // Ensure path starts with / if it's just the endpoint
    const cleanPath = path.startsWith('http')
        ? path
        : path.startsWith('/') ? path : `/${path}`;

    // If path is already relative /api/..., just prepend baseUrl
    if (cleanPath.startsWith(prefix)) {
        return `${baseUrl}${cleanPath}`;
    }

    return `${baseUrl}${prefix}${cleanPath}`;
    return `${baseUrl}${prefix}${cleanPath}`;
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = useAuthStore.getState().token;

    const headers: HeadersInit = {
        ...options.headers,
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    };

    // Default to JSON content type if not set, method is not GET/HEAD, and body is not FormData
    if (options.method && !["GET", "HEAD"].includes(options.method.toUpperCase())) {
        const isFormData = options.body instanceof FormData;
        if (!isFormData && !(headers as Record<string, string>)["Content-Type"]) {
            (headers as Record<string, string>)["Content-Type"] = "application/json";
        }
    }

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
        // Token expired or invalid
        useAuthStore.getState().logout();
        // Optionally redirect to login
        if (typeof window !== 'undefined') {
            window.location.href = '/login';
        }
    }

    return res;
}
