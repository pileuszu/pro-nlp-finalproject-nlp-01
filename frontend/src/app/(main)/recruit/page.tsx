"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Recruit } from "@/types";
import Link from "next/link";
import { useAuthStore } from "@/stores/useAuthStore";
import { Sparkles, Flame, LayoutGrid, List, ArrowRight, Building, Calendar, MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

export default function RecruitPage() {
    const { isAuthenticated } = useAuthStore();
    const [recruits, setRecruits] = useState<Recruit[]>([]);
    const [recommendRecruits, setRecommendRecruits] = useState<Recruit[]>([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [itemsPerPage] = useState(9);
    const [currentPage, setCurrentPage] = useState(1);

    useEffect(() => {
        // Fetch all recruits
        fetch("/api/recruits")
            .then((res) => res.json())
            .then((data) => {
                setRecruits(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to fetch recruits", err);
                setLoading(false);
            });

        // Fetch recommended recruits if authenticated
        if (isAuthenticated) {
            fetch("/api/recruits/recommend")
                .then((res) => res.json())
                .then((data) => setRecommendRecruits(data))
                .catch((err) => console.error("Failed to fetch recommendations", err));
        }
    }, [isAuthenticated]);

    // 공통 카드 렌더링 함수
    const renderRecruitList = (items: Recruit[]) => {
        const totalPages = Math.ceil(items.length / itemsPerPage);
        const startIndex = (currentPage - 1) * itemsPerPage;
        const visibleItems = items.slice(startIndex, startIndex + itemsPerPage);

        return (
            <div className="space-y-12">
                <AnimatePresence mode="wait">
                    {viewMode === 'grid' ? (
                        <motion.div
                            key={`grid-${currentPage}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.3 }}
                            className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
                        >
                            {visibleItems.map((recruit, index) => (
                                <motion.div
                                    key={recruit.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <Link href={`/recruit/${recruit.id}`} className="block h-full group">
                                        <Card className="flex flex-col h-full hover:shadow-xl transition-all duration-500 ease-in-out hover:-translate-y-1.5 cursor-pointer border-slate-200 bg-white rounded-2xl overflow-hidden ring-4 ring-transparent hover:ring-blue-500/5 shadow-sm">
                                            <CardHeader className="pb-4">
                                                <div className="flex justify-between items-start mb-2">
                                                    <Badge variant="outline" className="bg-slate-50 text-slate-400 border-slate-100 text-[10px] font-black uppercase tracking-widest px-2 py-0.5">
                                                        JOB OPENING
                                                    </Badge>
                                                </div>
                                                <CardTitle className="line-clamp-1 text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors duration-300 mb-1">{recruit.title}</CardTitle>
                                                <CardDescription className="text-sm font-bold text-slate-500 flex items-center gap-1.5 antialiased">
                                                    <Building className="h-3.5 w-3.5 opacity-50" /> {recruit.company}
                                                </CardDescription>
                                            </CardHeader>
                                            <CardContent className="flex-1 pb-6">
                                                <div className="flex flex-wrap gap-2">
                                                    {recruit.tags.map((tag) => (
                                                        <Badge key={tag} variant="secondary" className="font-bold bg-slate-100/80 text-slate-600 border-none px-2.5 py-0.5 text-[11px]">
                                                            {tag}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </CardContent>
                                            <CardFooter className="border-t border-slate-50 pt-5 pb-5 px-6 text-[11px] font-black text-slate-400 flex justify-between items-center bg-slate-50/30 group-hover:bg-blue-50/30 transition-colors duration-300 rounded-b-xl uppercase tracking-wider">
                                                <div className="flex items-center gap-2">
                                                    <Calendar className="h-3.5 w-3.5 opacity-40 text-blue-500" />
                                                    <span>마감일: {recruit.deadline}</span>
                                                </div>
                                                <div className="flex items-center gap-1 text-blue-600 font-black group-hover:translate-x-1.5 transition-all duration-500 ease-in-out">
                                                    APPLY <ArrowRight className="h-3.5 w-3.5" />
                                                </div>
                                            </CardFooter>
                                        </Card>
                                    </Link>
                                </motion.div>
                            ))}
                        </motion.div>
                    ) : (
                        <motion.div
                            key={`list-${currentPage}`}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            transition={{ duration: 0.3 }}
                            className="space-y-4 p-0"
                        >
                            {visibleItems.map((recruit, index) => (
                                <motion.div
                                    key={recruit.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <Link href={`/recruit/${recruit.id}`} className="block group">
                                        <div className="flex flex-col md:flex-row md:items-center justify-between p-5 rounded-xl border border-slate-100 bg-white transition-all duration-500 ease-in-out group-hover:border-blue-200 group-hover:bg-slate-50/50 group-hover:translate-x-1.5 hover:shadow-md">
                                            <div className="flex flex-col md:flex-row md:items-center gap-6 flex-1 min-w-0 pr-4">
                                                <div className="h-14 w-14 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-white group-hover:border-blue-100 group-hover:text-blue-600 transition-[background-color,border-color,color] duration-300 shrink-0">
                                                    <Building className="h-6 w-6" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-3 mb-1.5">
                                                        <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-700 transition-colors duration-300 truncate">
                                                            {recruit.title}
                                                        </h3>
                                                        <span className="text-xs font-black text-slate-300 uppercase tracking-widest hidden sm:block">|</span>
                                                        <span className="text-sm font-bold text-slate-500">{recruit.company}</span>
                                                    </div>
                                                    <div className="flex flex-wrap gap-2">
                                                        {recruit.tags.map((tag) => (
                                                            <span key={tag} className="text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100 group-hover:bg-white group-hover:border-blue-100 group-hover:text-blue-500 transition-colors duration-300">
                                                                #{tag}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center justify-between md:justify-end gap-8 mt-4 md:mt-0 shrink-0 border-t md:border-t-0 pt-4 md:pt-0">
                                                <div className="text-[11px] font-black text-slate-300 uppercase tracking-widest flex items-center gap-2">
                                                    <Calendar className="h-3.5 w-3.5 opacity-40" />
                                                    마감: {recruit.deadline}
                                                </div>
                                                <Button size="sm" variant="outline" className="rounded-lg h-9 font-black text-[11px] border-slate-200 hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-all duration-500 ease-in-out uppercase tracking-widest flex items-center justify-center gap-2">
                                                    View Detail
                                                </Button>
                                            </div>
                                        </div>
                                    </Link>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Smart Pagination UI */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-2 pt-8">
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={currentPage === 1}
                            onClick={() => { setCurrentPage(prev => Math.max(1, prev - 1)); window.scrollTo({ top: 400, behavior: 'smooth' }); }}
                            className="rounded-xl h-10 px-4 border-slate-200 font-bold hover:bg-blue-50 hover:text-blue-600 transition-all shrink-0"
                        >
                            이전
                        </Button>
                        <div className="flex items-center gap-1 mx-2">
                            {(() => {
                                const pages = [];
                                const delta = 1; // Number of pages to show around current page

                                for (let i = 1; i <= totalPages; i++) {
                                    if (
                                        i === 1 ||
                                        i === totalPages ||
                                        (i >= currentPage - delta && i <= currentPage + delta)
                                    ) {
                                        pages.push(i);
                                    } else if (
                                        i === currentPage - delta - 1 ||
                                        i === currentPage + delta + 1
                                    ) {
                                        pages.push('...');
                                    }
                                }

                                return pages.map((page, index) => {
                                    if (page === '...') {
                                        return (
                                            <div key={`ellipsis-${index}`} className="flex items-center justify-center w-10 h-10 text-slate-300">
                                                <MoreHorizontal className="h-4 w-4" />
                                            </div>
                                        );
                                    }

                                    const pageNum = page as number;
                                    return (
                                        <Button
                                            key={pageNum}
                                            variant={currentPage === pageNum ? "default" : "ghost"}
                                            size="sm"
                                            onClick={() => { setCurrentPage(pageNum); window.scrollTo({ top: 400, behavior: 'smooth' }); }}
                                            className={cn(
                                                "h-10 w-10 p-0 rounded-xl font-bold transition-all",
                                                currentPage === pageNum ? "bg-blue-600 text-white shadow-md shadow-blue-500/20" : "text-slate-500 hover:bg-slate-100"
                                            )}
                                        >
                                            {pageNum}
                                        </Button>
                                    );
                                });
                            })()}
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={currentPage === totalPages}
                            onClick={() => { setCurrentPage(prev => Math.min(totalPages, prev + 1)); window.scrollTo({ top: 400, behavior: 'smooth' }); }}
                            className="rounded-xl h-10 px-4 border-slate-200 font-bold hover:bg-blue-50 hover:text-blue-600 transition-all shrink-0"
                        >
                            다음
                        </Button>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="container max-w-screen-xl mx-auto py-12 px-4 md:px-8 animate-in fade-in duration-500">
            {/* 히어로 섹션 */}
            <div className="mb-12 text-center space-y-4">
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
                    당신의 커리어를 <span className="text-blue-600 drop-shadow-sm">Boost</span>하세요
                </h1>
                <p className="text-lg text-slate-500 max-w-3xl mx-auto leading-relaxed font-medium">
                    Pro-NLP는 단순한 공고 리스트가 아닙니다.<br />
                    당신의 포트폴리오를 분석하여 가장 적합한 기업을 추천하고,<br />
                    자소서 초안까지 작성해드립니다.
                </p>
            </div>

            {/* 탭 네비게이션 섹션 */}
            <div className="mb-8 w-full max-w-5xl mx-auto">
                <Tabs defaultValue="all" className="w-full" onValueChange={() => setCurrentPage(1)}>
                    <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4 border-b border-slate-100 pb-6">
                        <TabsList className="grid w-full max-w-[400px] grid-cols-3 bg-slate-100 p-1 rounded-xl">
                            <TabsTrigger value="all" className="rounded-lg font-bold">전체 공고</TabsTrigger>
                            <TabsTrigger value="recommend" className="flex items-center gap-1.5 rounded-lg font-bold">
                                <Sparkles className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500" /> 추천
                            </TabsTrigger>
                            <TabsTrigger value="popular" className="flex items-center gap-1.5 rounded-lg font-bold">
                                <Flame className="h-3.5 w-3.5 text-orange-500 fill-orange-500" /> 인기
                            </TabsTrigger>
                        </TabsList>

                        <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-inner">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setViewMode('grid')}
                                className={cn("h-8 w-10 px-0 rounded-lg transition-all", viewMode === 'grid' ? "bg-white text-blue-600 shadow-sm" : "text-slate-400 hover:text-slate-600")}
                            >
                                <LayoutGrid className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setViewMode('list')}
                                className={cn("h-8 w-10 px-0 rounded-lg transition-all", viewMode === 'list' ? "bg-white text-blue-600 shadow-sm" : "text-slate-400 hover:text-slate-600")}
                            >
                                <List className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>

                    {loading ? (
                        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                            {[1, 2, 3, 4, 5, 6].map((i) => (
                                <div key={i} className="h-[250px] w-full animate-pulse rounded-2xl bg-slate-100 border border-slate-200" />
                            ))}
                        </div>
                    ) : (
                        <>
                            <TabsContent value="all" className="mt-0 outline-none">
                                {renderRecruitList(recruits)}
                            </TabsContent>
                            <TabsContent value="recommend" className="mt-0 outline-none">
                                {isAuthenticated ? (
                                    recommendRecruits.length > 0 ? (
                                        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                            <div className="flex items-center gap-3 p-4 bg-blue-50/50 border border-blue-100 rounded-2xl text-[13px] text-blue-700 shadow-sm shadow-blue-500/5 antialiased font-semibold">
                                                <div className="p-2 bg-blue-100 rounded-xl">
                                                    <Sparkles className="h-4 w-4 text-blue-600 fill-blue-600" />
                                                </div>
                                                <span>회원님의 포트폴리오를 기반으로 AI가 분석한 추천 공고입니다.</span>
                                            </div>
                                            {renderRecruitList(recommendRecruits)}
                                        </div>
                                    ) : (
                                        <div className="text-center py-20 text-slate-400 animate-in fade-in slide-in-from-bottom-4 duration-500 bg-slate-50/50 rounded-3xl border border-dashed border-slate-200 font-bold italic">
                                            추천 공고를 분석 중입니다...
                                        </div>
                                    )
                                ) : (
                                    <div className="text-center py-20 text-slate-500 p-12 border border-dashed border-slate-200 rounded-3xl animate-in fade-in slide-in-from-bottom-4 duration-500 bg-white shadow-sm">
                                        <Sparkles className="h-12 w-12 text-blue-100 mx-auto mb-6" />
                                        <p className="mb-2 font-medium">로그인 후 내 포트폴리오를 등록하면</p>
                                        <p className="font-black text-2xl text-slate-900 mb-8">AI가 딱 맞는 공고를 추천해드려요!</p>
                                        <Link href="/login">
                                            <Button className="h-12 px-10 rounded-xl font-bold text-lg shadow-lg shadow-blue-500/10 transition-all">
                                                로그인하러 가기
                                            </Button>
                                        </Link>
                                    </div>
                                )}
                            </TabsContent>
                            <TabsContent value="popular" className="mt-0 outline-none">
                                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="flex items-center gap-3 p-4 bg-orange-50/50 border border-orange-100 rounded-2xl text-[13px] text-orange-700 shadow-sm shadow-orange-500/5 antialiased font-semibold">
                                        <div className="p-2 bg-orange-100 rounded-xl">
                                            <Flame className="h-4 w-4 text-orange-600 fill-orange-600" />
                                        </div>
                                        <span>지금 가장 많은 지원자들이 관심을 보이고 있는 인기 채용공고입니다.</span>
                                    </div>
                                    {renderRecruitList(recruits)}
                                </div>
                            </TabsContent>
                        </>
                    )}
                </Tabs>
            </div>
        </div>
    );
}
