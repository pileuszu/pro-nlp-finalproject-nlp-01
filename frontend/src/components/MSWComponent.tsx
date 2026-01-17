"use client";

import { useEffect, useState } from "react";

export const MSWComponent = ({ children }: { children: React.ReactNode }) => {
    const [mswReady, setMswReady] = useState(false);

    useEffect(() => {
        const initMsw = async () => {
            // 개발 환경이 아니면 바로 통과
            if (process.env.NODE_ENV !== 'development') {
                setMswReady(true);
                return;
            }

            if (typeof window !== 'undefined') {
                try {
                    const { worker } = await import('@/mocks/browser');
                    await worker.start({
                        onUnhandledRequest: 'bypass',
                    });
                    console.log("[MSW] Mock Service Worker started");
                    setMswReady(true);
                } catch (error) {
                    console.error("[MSW] Failed to start:", error);
                    setMswReady(true); // 에러나도 일단 진행
                }
            }
        };
        initMsw();
    }, []);

    if (!mswReady) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-background">
                <div className="text-center space-y-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                    <p className="text-sm text-muted-foreground">개발 환경 설정 중...</p>
                </div>
            </div>
        );
    }

    return <>{children}</>;
};
