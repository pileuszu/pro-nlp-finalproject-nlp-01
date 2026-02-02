"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { X, MapPin, Coins, GraduationCap, Sparkles, Zap, Wand2, MessageSquare, LayoutList, Target, Brain, Loader2, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { Recruit as RecruitDetail } from "@/types";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type AiMode = 'draft' | 'strategy' | 'refine';

interface RecruitInfoPanelProps {
    isOpen: boolean;
    onClose: () => void;
    recruit: RecruitDetail | null;
    panelTab: string;
    setPanelTab: (tab: string) => void;
    // AI Studio Props
    aiMode: AiMode;
    setAiMode: (mode: AiMode) => void;
    // Removed Tone/Focus/Subheading props
    temperature: number;
    setTemperature: (val: number) => void;
    isGenerating: boolean;
    onRunGeneration: () => void;
}

export function RecruitInfoPanel({
    isOpen,
    onClose,
    recruit,
    panelTab,
    setPanelTab,
    aiMode,
    setAiMode,
    temperature,
    setTemperature,
    isGenerating,
    onRunGeneration
}: RecruitInfoPanelProps) {
    return (
        <div className={cn("transition-all duration-700 overflow-hidden shrink-0 hidden xl:block h-full", isOpen ? "w-[580px] opacity-100" : "w-0 opacity-0 pointer-events-none")}>
            <div className="w-[580px] px-8 pt-8 pb-8 flex flex-col h-full">
                <div className="bg-white border-2 border-slate-100 rounded-[2.5rem] shadow-2xl flex-1 flex flex-col overflow-hidden">
                    <Tabs value={panelTab} onValueChange={setPanelTab} className="h-full flex flex-col">
                        <div className="p-8 pb-4 bg-white">
                            <div className="flex justify-between items-center mb-6">
                                <div className="flex items-center gap-3">
                                    <div className="p-3 bg-blue-600 rounded-2xl shadow-lg shadow-blue-500/20 text-white"><Sparkles className="h-5 w-5" /></div>
                                    <div className="space-y-0.5">
                                        <h2 className="font-black text-xl tracking-tight text-slate-900">AI 라이팅 스튜디오</h2>
                                        <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">AI Writing Studio</p>
                                    </div>
                                </div>
                                <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full hover:bg-slate-100 trasition-all"><X className="h-5 w-5 text-slate-400" /></Button>
                            </div>
                            <TabsList className="grid grid-cols-2 w-full h-11 bg-slate-100 p-1 rounded-xl border border-slate-200/50 shadow-inner mb-2 font-pretendard">
                                <TabsTrigger
                                    value="recruit"
                                    className="flex items-center gap-2 rounded-lg font-bold text-[13px] data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm transition-all duration-200"
                                >
                                    <FileText className="h-3.5 w-3.5" /> 공고 원문
                                </TabsTrigger>
                                <TabsTrigger
                                    value="ai_writing"
                                    className="flex items-center gap-2 rounded-lg font-bold text-[13px] data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm transition-all duration-200"
                                >
                                    <Sparkles className="h-3.5 w-3.5 text-blue-500 fill-blue-500/10" /> AI 라이팅
                                </TabsTrigger>
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

                                        {recruit.tags && Array.isArray(recruit.tags) && recruit.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-2 pt-4">
                                                {recruit.tags.map((tag, i) => (
                                                    <Badge key={i} variant="secondary" className="bg-slate-100 text-slate-500 hover:bg-slate-200 border-none px-3 py-1 font-bold text-[11px] rounded-lg">#{tag}</Badge>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ) : <div className="text-center py-24 text-slate-400 font-medium">연결된 공고가 없습니다.</div>}
                            </TabsContent>
                            <TabsContent value="ai_writing" className="m-0 space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
                                <div className="bg-blue-600 p-6 rounded-3xl shadow-xl shadow-blue-500/20 mb-2 group relative overflow-hidden">
                                    <Sparkles className="absolute -top-4 -right-4 h-24 w-24 text-white/10 rotate-12" />
                                    <p className="text-white text-md font-black mb-1 flex items-center gap-2 relative z-10">
                                        AI 라이팅 스튜디오
                                    </p>
                                    <p className="text-blue-100 text-[12px] leading-relaxed font-semibold relative z-10">
                                        지원자님의 모든 포트폴리오를 참조하여 최적의 답변을 생성합니다.
                                    </p>
                                </div>

                                <div className="space-y-6 pb-20">
                                    {/* Mode Selection */}
                                    <div className="space-y-3">
                                        <Label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 ml-1">
                                            <Zap className="h-3.5 w-3.5 text-blue-500 fill-blue-500" /> 답변 구성 모드
                                        </Label>
                                        <div className="grid grid-cols-3 gap-2">
                                            {[
                                                { id: 'draft', label: '기본 스타일', icon: <Wand2 className="h-4 w-4" /> },
                                                { id: 'strategy', label: '가이드라인 생성', icon: <LayoutList className="h-4 w-4" /> },
                                                { id: 'refine', label: '소제목 스타일', icon: <MessageSquare className="h-4 w-4" /> }
                                            ].map(mode => (
                                                <div key={mode.id} onClick={() => setAiMode(mode.id as AiMode)} className={cn("p-4 rounded-2xl border-2 transition-all cursor-pointer text-center space-y-2", aiMode === mode.id ? "border-blue-600 bg-blue-50/50 shadow-md" : "border-slate-50 bg-slate-50/50 hover:border-slate-100 hover:bg-white")}>
                                                    <div className={cn("mx-auto h-8 w-8 rounded-xl flex items-center justify-center transition-all", aiMode === mode.id ? "bg-blue-600 text-white" : "bg-white text-slate-300")}>{mode.icon}</div>
                                                    <div className={cn("font-black text-[11px] tracking-tight", aiMode === mode.id ? "text-blue-900" : "text-slate-600")}>{mode.label}</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Temperature Control */}
                                    <div className="space-y-4">
                                        <Label className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 ml-1">
                                            <Brain className="h-3.5 w-3.5 text-blue-500" /> 창의성 (Temperature): {temperature.toFixed(1)}
                                        </Label>
                                        <div className="px-1">
                                            <input
                                                type="range"
                                                min="0.0"
                                                max="1.0"
                                                step="0.1"
                                                value={temperature}
                                                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                                                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                                            />
                                            <div className="flex justify-between text-[10px] text-slate-400 font-bold mt-2">
                                                <span>정확함 (0.0)</span>
                                                <span>균형 (0.5)</span>
                                                <span>창의적 (1.0)</span>
                                            </div>
                                        </div>
                                        <p className="text-[11px] text-slate-400 font-medium leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                                            정확한 사실 기반 작성이 필요하면 <b>0.0</b>,
                                            더 다채로운 표현을 원하면 <b>0.5 이상</b>으로 설정하세요.
                                        </p>
                                    </div>

                                    {/* Action Button */}
                                    <Button variant="default" size="lg" onClick={onRunGeneration} disabled={isGenerating} className="w-full h-16 rounded-2xl text-[15px] font-black shadow-xl shadow-blue-500/20 bg-blue-600 hover:bg-blue-700">
                                        {isGenerating ? (
                                            <span className="flex items-center gap-2"><Loader2 className="h-5 w-5 animate-spin" /> 생성 중...</span>
                                        ) : (
                                            <span className="flex items-center gap-2"><Sparkles className="h-5 w-5" /> AI로 전체 문항 일괄 작성</span>
                                        )}
                                    </Button>
                                </div>
                            </TabsContent>
                        </div>
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
