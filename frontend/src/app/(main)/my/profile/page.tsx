"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/useAuthStore";
import { getApiUrl, fetchWithAuth } from "@/lib/apiUtils";
import { User } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Target, Sparkles, User as UserIcon, Mail, Calendar, Briefcase } from "lucide-react";
import { motion } from "framer-motion";

export default function ProfilePage() {
    const { isAuthenticated } = useAuthStore();
    const [profile, setProfile] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isAuthenticated) return;

        fetchWithAuth(getApiUrl("/auth/me"))
            .then(res => res.json())
            .then(data => {
                setProfile(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [isAuthenticated]);

    if (loading) return <div className="flex h-[calc(100vh-64px)] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>;
    if (!profile) return <div className="text-center py-20 font-bold text-slate-500">로그인이 필요합니다.</div>;

    return (
        <div className="container max-w-screen-md mx-auto py-12 px-4 md:px-8 space-y-10 animate-in fade-in duration-700">
            {/* User Intro Section */}
            <div className="text-center space-y-6">
                <div className="inline-flex p-4 rounded-[2.5rem] bg-gradient-to-br from-blue-500 to-indigo-600 shadow-xl shadow-blue-500/20 mb-2">
                    <UserIcon className="h-12 w-12 text-white" />
                </div>
                <div className="space-y-2">
                    <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">{profile.name}님의 프로필</h1>
                    <div className="flex items-center justify-center gap-2 text-slate-500 font-medium">
                        <Mail className="h-4 w-4" />
                        <span>{profile.email}</span>
                    </div>
                </div>

                {profile.desired_job_title ? (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="flex justify-center pt-2"
                    >
                        <Badge variant="default" className="h-10 px-6 rounded-2xl bg-blue-600 hover:bg-blue-600 text-white font-bold text-sm shadow-lg shadow-blue-500/20 gap-2">
                            <Target className="h-4 w-4" />
                            {profile.desired_job_title}
                        </Badge>
                    </motion.div>
                ) : (
                    <div className="pt-2">
                        <Badge variant="outline" className="h-10 px-6 rounded-2xl border-slate-200 text-slate-400 font-bold text-sm border-dashed">
                            목표 직무 분석 중...
                        </Badge>
                    </div>
                )}
            </div>

            {/* Profile Content Cards */}
            <div className="grid gap-8">
                {/* AI Career Summary */}
                <Card className="border-2 border-slate-100 rounded-[2.5rem] shadow-xl shadow-slate-200/40 overflow-hidden bg-white group">
                    <CardHeader className="bg-slate-50/50 border-b border-slate-100 p-8">
                        <CardTitle className="flex items-center gap-3 text-xl font-black text-slate-800">
                            <div className="p-2.5 bg-white rounded-2xl shadow-sm border border-slate-100 text-blue-600">
                                <Sparkles className="h-5 w-5 fill-blue-50" />
                            </div>
                            AI 통합 커리어 요약
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-10">
                        {profile.profile_summary ? (
                            <p className="text-lg text-slate-700 leading-loose whitespace-pre-line font-medium antialiased">
                                {profile.profile_summary}
                            </p>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-10 space-y-4">
                                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center animate-pulse">
                                    <Sparkles className="h-8 w-8 text-slate-200" />
                                </div>
                                <p className="text-slate-400 font-bold italic">
                                    포트폴리오를 등록하면 AI가 커리어를 분석해 드립니다.
                                </p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Additional Info / Settings Placeholder */}
                <div className="grid sm:grid-cols-2 gap-4">
                    <div className="p-6 bg-white border border-slate-100 rounded-3xl flex items-center gap-4 shadow-sm">
                        <div className="p-3 bg-slate-50 rounded-2xl text-slate-400">
                            <Calendar className="h-5 w-5" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-300 uppercase tracking-widest">가입일</div>
                            <div className="font-bold text-slate-700">2026. 02. 01</div>
                        </div>
                    </div>
                    <div className="p-6 bg-white border border-slate-100 rounded-3xl flex items-center gap-4 shadow-sm">
                        <div className="p-3 bg-slate-50 rounded-2xl text-slate-400">
                            <Briefcase className="h-5 w-5" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-300 uppercase tracking-widest">포트폴리오</div>
                            <div className="font-bold text-slate-700">관리 중</div>
                        </div>
                    </div>
                </div>
            </div>

            <p className="text-center text-xs text-slate-400 leading-relaxed font-medium pb-10">
                이 정보는 등록하신 포트폴리오를 AI가 종합적으로 분석한 결과입니다.<br />
                포트폴리오가 추가되거나 변경되면 실시간으로 업데이트됩니다.
            </p>
        </div>
    );
}
