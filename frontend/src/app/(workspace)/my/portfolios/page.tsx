"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Portfolio } from "@/types";

export default function PortfoliosPage() {
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);

    useEffect(() => {
        fetch('/api/portfolios')
            .then(res => res.json())
            .then(data => setPortfolios(data));
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">포트폴리오 관리</h2>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {portfolios.map((pf) => (
                    <Card key={pf.id} className="cursor-pointer hover:border-primary transition-colors">
                        <CardHeader>
                            <CardTitle className="flex justify-between items-center">
                                {pf.title}
                                <span className="text-xs font-normal px-2 py-1 bg-muted rounded-full">{pf.type}</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">생성일: {pf.createdAt}</p>
                        </CardContent>
                    </Card>
                ))}

                {/* 추가 버튼 카드 */}
                <Card className="flex items-center justify-center h-[150px] border-dashed cursor-pointer hover:bg-muted/50 transition-colors">
                    <span className="text-muted-foreground">+ 새 포트폴리오 등록</span>
                </Card>
            </div>
        </div>
    )
}
