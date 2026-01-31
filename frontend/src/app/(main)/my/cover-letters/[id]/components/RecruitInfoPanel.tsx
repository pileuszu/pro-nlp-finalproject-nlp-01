"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { X, Search, MapPin, Coins, GraduationCap, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { Recruit as RecruitDetail } from "@/types";

interface RecruitInfoPanelProps {
    isOpen: boolean;
    onClose: () => void;
    recruit: RecruitDetail | null;
    panelTab: string;
    setPanelTab: (tab: string) => void;
}

export function RecruitInfoPanel({
    isOpen,
    onClose,
    recruit,
    panelTab,
    setPanelTab
}: RecruitInfoPanelProps) {
    return (
        <div className={cn("sticky top-0 transition-all duration-700 overflow-hidden shrink-0 hidden xl:block", isOpen ? "w-[580px] opacity-100 h-auto self-start" : "w-0 opacity-0 pointer-events-none")}>
            <div className="w-[580px] px-8 pt-20 pb-24 flex flex-col">
                <div className="bg-white border-2 border-slate-100 rounded-[2.5rem] shadow-2xl flex-1 flex flex-col overflow-hidden">
                    <Tabs value={panelTab} onValueChange={setPanelTab} className="h-full flex flex-col">
                        <div className="p-8 pb-4 bg-white">
                            <div className="flex justify-between items-center mb-6">
                                <div className="flex items-center gap-3">
                                    <div className="p-3 bg-blue-600 rounded-2xl shadow-lg shadow-blue-500/20 text-white"><Search className="h-5 w-5" /></div>
                                    <div className="space-y-0.5">
                                        <h2 className="font-black text-xl tracking-tight text-slate-900">공고 분석 패널</h2>
                                        <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">AI Context Studio</p>
                                    </div>
                                </div>
                                <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full hover:bg-slate-100 trasition-all"><X className="h-5 w-5 text-slate-400" /></Button>
                            </div>
                            <TabsList className="grid grid-cols-2 w-full h-12 bg-slate-100 p-1.5 rounded-[1.25rem] mb-2 font-pretendard">
                                <TabsTrigger value="recruit" className="rounded-[0.9rem] font-black text-xs">공고 원문</TabsTrigger>
                                <TabsTrigger value="reference" className="rounded-[0.9rem] font-black text-xs">포트폴리오</TabsTrigger>
                            </TabsList>
                        </div>
                        <div className="flex-1 overflow-y-auto overflow-x-hidden p-8 pt-4 scrollbar-hide font-pretendard">
                            <TabsContent value="recruit" className="m-0 space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                                {recruit ? (
                                    <div className="space-y-8 pb-8">
                                        <div className="space-y-4">
                                            <h3 className="text-2xl font-black tracking-tight text-slate-900 leading-tight">{recruit.title}</h3>
                                            <div className="flex flex-wrap gap-2">
                                                <Badge variant="default" className="px-3 py-1 font-bold rounded-lg bg-blue-600 hover:bg-blue-700 text-white border-none">{recruit.company}</Badge>
                                                {recruit.experience && <Badge variant="outline" className="border-slate-200 text-slate-600 rounded-lg px-3 py-1 font-bold">{recruit.experience}</Badge>}
                                                {recruit.location && <Badge variant="outline" className="border-slate-200 text-slate-600 rounded-lg px-3 py-1 font-bold"><MapPin className="h-3 w-3 mr-1" />{recruit.location}</Badge>}
                                                {recruit.salary && <Badge variant="outline" className="border-slate-200 text-slate-600 rounded-lg px-3 py-1 font-bold"><Coins className="h-3 w-3 mr-1" />{recruit.salary}</Badge>}
                                                {recruit.education && <Badge variant="outline" className="border-slate-200 text-slate-600 rounded-lg px-3 py-1 font-bold"><GraduationCap className="h-3 w-3 mr-1" />{recruit.education}</Badge>}
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">공고 등록</div>
                                                <div className="text-sm font-bold text-slate-700">{recruit.start_date || 'N/A'}</div>
                                            </div>
                                            <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">마감 기한</div>
                                                <div className="text-sm font-bold text-red-600">{recruit.deadline || 'N/A'}</div>
                                            </div>
                                        </div>

                                        <div className="space-y-8">
                                            {recruit.key_responsibilities && (
                                                <div className="space-y-3">
                                                    <div className="flex items-center gap-2 text-sm font-black text-slate-900"><div className="h-1.5 w-1.5 bg-blue-600 rounded-full" /> 주요 업무</div>
                                                    <p className="text-[14px] text-slate-600 leading-relaxed bg-slate-50/50 p-4 rounded-2xl border border-slate-100 whitespace-pre-wrap font-medium">{recruit.key_responsibilities}</p>
                                                </div>
                                            )}
                                            {recruit.required_qualifications && (
                                                <div className="space-y-3">
                                                    <div className="flex items-center gap-2 text-sm font-black text-slate-900"><div className="h-1.5 w-1.5 bg-green-600 rounded-full" /> 자격 요건</div>
                                                    <p className="text-[14px] text-slate-600 leading-relaxed bg-slate-50/50 p-4 rounded-2xl border border-slate-100 whitespace-pre-wrap font-medium">{recruit.required_qualifications}</p>
                                                </div>
                                            )}
                                            {recruit.preferred_qualifications && (
                                                <div className="space-y-3">
                                                    <div className="flex items-center gap-2 text-sm font-black text-slate-900"><div className="h-1.5 w-1.5 bg-amber-600 rounded-full" /> 우대 사항</div>
                                                    <p className="text-[14px] text-slate-600 leading-relaxed bg-slate-50/50 p-4 rounded-2xl border border-slate-100 whitespace-pre-wrap font-medium">{recruit.preferred_qualifications}</p>
                                                </div>
                                            )}
                                        </div>

                                        {recruit.tags && recruit.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-2 pt-4">
                                                {recruit.tags.map((tag, i) => (
                                                    <Badge key={i} variant="secondary" className="bg-slate-100 text-slate-500 hover:bg-slate-200 border-none px-3 py-1 font-bold text-[11px] rounded-lg">#{tag}</Badge>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ) : <div className="text-center py-24 text-slate-400 font-medium">연결된 공고가 없습니다.</div>}
                            </TabsContent>
                            <TabsContent value="reference" className="m-0 space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
                                <div className="bg-blue-600 p-6 rounded-3xl shadow-xl shadow-blue-500/20 mb-4 group relative overflow-hidden">
                                    <Sparkles className="absolute -top-4 -right-4 h-24 w-24 text-white/10 rotate-12" />
                                    <p className="text-white text-md font-black mb-1 flex items-center gap-2 relative z-10">
                                        AI 자동 컨텍스트 매칭
                                    </p>
                                    <p className="text-blue-100 text-[13px] leading-relaxed font-semibold relative z-10">
                                        필요한 정보를 찾기 위해 지원자님의 모든 포트폴리오 데이터를 실시간으로 참조하고 있습니다.
                                        <span className="block mt-2 opacity-80 font-normal">AI 라이팅 스튜디오에서 원하시는 강조 포인트를 설정해 보세요.</span>
                                    </p>
                                </div>
                            </TabsContent>
                        </div>
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
