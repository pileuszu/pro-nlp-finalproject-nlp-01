"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Portfolio } from "@/types";
import { Plus, FileText, Link as LinkIcon, Github, Sparkles, LayoutGrid, List } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { getApiUrl } from "@/lib/apiUtils";

export default function PortfoliosPage() {
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

    useEffect(() => {
        fetch(getApiUrl("/portfolios"))
            .then(res => res.json())
            .then(data => {
                if (data.items) {
                    setPortfolios(data.items);
                } else {
                    setPortfolios(data); // 폴백 (배열로 올 경우 대비)
                }
            })
            .catch(err => console.error(err));
    }, []);

    const getIcon = (type: string) => {
        switch (type) {
            case 'github': return <Github className="h-5 w-5" />;
            case 'link': return <LinkIcon className="h-5 w-5" />;
            default: return <FileText className="h-5 w-5" />;
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500 container max-w-screen-xl mx-auto py-8 px-4 md:px-8">
            <div className="flex items-center justify-between border-b border-slate-100 pb-8 gap-4 flex-wrap">
                <div className="flex-1">
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 leading-tight">내 포트폴리오</h1>
                    <p className="text-slate-500 mt-2 font-medium">등록된 포트폴리오를 관리하고 채용 공고에 활용하세요.</p>
                </div>
                <div className="flex items-center gap-4">
                    {/* View Toggle */}
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

                    <Link href="/my/portfolios/new">
                        <Button variant="brand" className="h-11 pl-5 pr-6 rounded-xl font-bold shadow-lg shadow-blue-500/10 flex items-center justify-center gap-2">
                            <Plus className="h-5 w-5" />
                            <span>새 포트폴리오 등록</span>
                        </Button>
                    </Link>
                </div>
            </div>

            <AnimatePresence mode="wait">
                {viewMode === 'grid' ? (
                    <motion.div
                        key="grid"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 1.02 }}
                        transition={{ duration: 0.3 }}
                        className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
                    >
                        {portfolios.map((portfolio, index) => (
                            <motion.div
                                key={portfolio.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                            >
                                <Card className="flex flex-col hover:shadow-xl transition-all duration-500 ease-in-out border-slate-200 hover:-translate-y-1.5 bg-white group overflow-hidden rounded-2xl shadow-sm ring-4 ring-transparent hover:ring-blue-500/5">
                                    <CardHeader className="pb-4 relative">
                                        <CardTitle className="flex items-center gap-3 text-lg font-bold text-slate-800 group-hover:text-blue-700 transition-colors duration-300">
                                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 group-hover:bg-blue-50 group-hover:border-blue-100 transition-colors duration-300">
                                                {getIcon(portfolio.type)}
                                            </div>
                                            <span className="line-clamp-1">{portfolio.title}</span>
                                        </CardTitle>
                                        <div className="text-[11px] text-slate-400 font-bold flex items-center justify-between uppercase tracking-wider">
                                            {portfolio.createdAt}
                                            {portfolio.content && (
                                                <Badge variant="outline" className="bg-blue-50/50 border-blue-100 text-blue-600 text-[10px] gap-1 font-black animate-pulse py-0.5">
                                                    <Sparkles className="h-2.5 w-2.5 fill-blue-500" /> AI READY
                                                </Badge>
                                            )}
                                        </div>
                                    </CardHeader>
                                    <CardContent className="flex-1 pb-6">
                                        <p className="text-sm text-slate-500 line-clamp-3 leading-relaxed font-medium">
                                            {portfolio.description || "포트폴리오에 대한 설명이 없습니다."}
                                        </p>
                                    </CardContent>
                                    <CardFooter className="pt-4 border-t border-slate-50 p-6 bg-slate-50/30">
                                        <Link href={`/my/portfolios/${portfolio.id}`} className="w-full">
                                            <Button variant="outline" className="w-full border-slate-200 h-10 rounded-xl hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 text-slate-600 font-black transition-[background-color,border-color,color] duration-300" size="sm">
                                                상세 보기
                                            </Button>
                                        </Link>
                                    </CardFooter>
                                </Card>
                            </motion.div>
                        ))}
                    </motion.div>
                ) : (
                    <motion.div
                        key="list"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ duration: 0.3 }}
                        className="space-y-4 p-0"
                    >
                        {portfolios.map((portfolio, index) => (
                            <motion.div
                                key={portfolio.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                            >
                                <Link href={`/my/portfolios/${portfolio.id}`} className="block group">
                                    <div className="flex items-center justify-between p-5 rounded-xl border border-slate-100 bg-white transition-all duration-500 ease-in-out group-hover:border-blue-200 group-hover:bg-slate-50/50 group-hover:translate-x-1.5 hover:shadow-md">
                                        <div className="flex items-center gap-6 flex-1 min-w-0 pr-4">
                                            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-slate-400 group-hover:bg-white group-hover:border-blue-100 group-hover:text-blue-600 transition-[background-color,border-color,color] duration-300 shrink-0">
                                                {getIcon(portfolio.type)}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-3 mb-1.5">
                                                    <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-700 transition-colors duration-300 truncate">
                                                        {portfolio.title}
                                                    </h3>
                                                    {portfolio.content && (
                                                        <Badge variant="outline" className="bg-blue-50 border-blue-100 text-blue-600 text-[9px] font-black uppercase py-0 px-2 shrink-0">
                                                            AI Ready
                                                        </Badge>
                                                    )}
                                                </div>
                                                <p className="text-sm text-slate-400 font-medium truncate italic antialiased leading-relaxed">
                                                    {portfolio.description || "설명이 없습니다."}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-8 shrink-0">
                                            <div className="text-[11px] font-black text-slate-300 uppercase tracking-widest hidden sm:block">
                                                Created: {portfolio.createdAt}
                                            </div>
                                            <div className="h-8 w-8 rounded-full flex items-center justify-center text-slate-300 group-hover:text-blue-600 group-hover:bg-blue-50 transition-all duration-300">
                                                <LinkIcon className="h-4 w-4" />
                                            </div>
                                        </div>
                                    </div>
                                </Link>
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
