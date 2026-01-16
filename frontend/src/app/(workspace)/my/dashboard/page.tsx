"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/useAuthStore";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { User, FileText, Briefcase } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
    const user = useAuthStore((state) => state.user);
    const [stats, setStats] = useState({
        coverLetters: 0,
        portfolios: 0,
        applications: 0
    });

    useEffect(() => {
        // Mock API calls for dashboard stats
        // Promise.all([ fetch('/api/cover-letters'), ... ])
        // Here we just hardcode/simulate or fetch mock
        const fetchData = async () => {
            const clRes = await fetch('/api/cover-letters');
            const pfRes = await fetch('/api/portfolios');
            const clData = await clRes.json();
            const pfData = await pfRes.json();
            setStats({
                coverLetters: clData.length,
                portfolios: pfData.length,
                applications: 5 // Mocked fixed value
            });
        }
        fetchData();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">대시보드</h2>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">총 자소서</CardTitle>
                        <FileText className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.coverLetters}</div>
                        <p className="text-xs text-muted-foreground">작성 중: 1개</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">내 포트폴리오</CardTitle>
                        <Briefcase className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.portfolios}</div>
                        <p className="text-xs text-muted-foreground">지난 달 대비 +1</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">지원 완료</CardTitle>
                        <User className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.applications}</div>
                        <p className="text-xs text-muted-foreground">이번 시즌</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>최근 작성 중인 자소서</CardTitle>
                        <CardDescription>
                            마감 기한이 임박한 자소서가 있습니다.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-medium leading-none">구글 2026 상반기 지원</p>
                                    <p className="text-sm text-muted-foreground">2026.03.01 마감</p>
                                </div>
                                <div className="ml-auto font-medium">
                                    <Link href="/my/cover-letters/1">
                                        <Button size="sm" variant="outline">이어서 작성</Button>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>빠른 접근</CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-2">
                        <Link href="/recruit">
                            <Button className="w-full" variant="secondary">채용 공고 둘러보기</Button>
                        </Link>
                        <Link href="/my/portfolios">
                            <Button className="w-full" variant="secondary">포트폴리오 관리</Button>
                        </Link>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
