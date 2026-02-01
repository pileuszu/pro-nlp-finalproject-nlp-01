import { getApiUrl, fetchWithAuth } from "./apiUtils";

export interface IntegrationRepo {
    name: string;
    url: string;
    private: boolean;
    description: string | null;
}

export interface UserIntegration {
    id: number;
    provider: string;
    created_at: string;
}

export const integrationApi = {
    fetchIntegrations: async (): Promise<UserIntegration[]> => {
        const res = await fetchWithAuth(getApiUrl("/integrations"));
        if (!res.ok) return [];
        return res.json();
    },

    getGithubLoginUrl: (): string => {
        return getApiUrl("/integrations/github/login");
    },

    fetchGithubRepos: async (): Promise<IntegrationRepo[]> => {
        const res = await fetchWithAuth(getApiUrl("/integrations/github/repos"));
        if (!res.ok) throw new Error("Failed to fetch Github repos");
        return res.json();
    },

    removeIntegration: async (id: number): Promise<boolean> => {
        const res = await fetchWithAuth(getApiUrl(`/integrations/${id}`), {
            method: "DELETE"
        });
        return res.ok;
    }
};
