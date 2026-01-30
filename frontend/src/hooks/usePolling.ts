import { useState, useEffect, useRef } from 'react';
import { getApiUrl, fetchWithAuth } from '@/lib/apiUtils';

export function usePolling<T>(
    endpoint: string,
    intervalMs: number = 3000,
    stopCondition?: (data: T) => boolean
) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<any>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const fetchData = async () => {
        try {
            const res = await fetchWithAuth(getApiUrl(endpoint));
            if (!res.ok) throw new Error("Failed to fetch");
            const result = await res.json();
            setData(result);
            return result;
        } catch (err) {
            setError(err);
            return null;
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Initial fetch
        fetchData().then((result) => {
             if (result && stopCondition && stopCondition(result)) {
                // Already done, don't poll
                return;
            }
             // Start polling
             intervalRef.current = setInterval(async () => {
                const newData = await fetchData();
                if (newData && stopCondition && stopCondition(newData)) {
                    if (intervalRef.current) clearInterval(intervalRef.current);
                }
            }, intervalMs);
        });

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [endpoint, intervalMs]);

    return { data, loading, error };
}
