"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Upload, Github, Sparkles, ExternalLink, Plus, Check, FileText } from "lucide-react";
import { portfolioApi } from "@/lib/portfolioApi";

export default function NewPortfolioPage() {
    const router = useRouter();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isUploading, setIsUploading] = useState(false);

    // Form States
    const [githubUrl, setGithubUrl] = useState("");
    const [notionUrl, setNotionUrl] = useState("");

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setIsUploading(true);
            try {
                // Currently backend supports single file upload. 
                // Loop if multiple selected or just pick first. Backend endpoint is single file.
                await portfolioApi.uploadFile(e.target.files[0]);
                alert("파일이 업로드되었습니다. AI가 배경에서 분석을 시작했습니다.");
                router.push('/my/portfolios');
            } catch (err: any) {
                console.error(err);
                alert(`업로드 실패: ${err.message}`);
            } finally {
                setIsUploading(false);
            }
        }
    };

    const handleGithubImport = async (url: string) => {
        if (!url) {
            alert("GitHub URL을 입력해주세요.");
            return;
        }
        setIsUploading(true);
        try {
            await portfolioApi.importGithub(url);
            alert("GitHub 포트폴리오 가져오기 성공! AI 분석이 시작되었습니다.");
            router.push('/my/portfolios');
        } catch (err: any) {
            console.error(err);
            alert(`GitHub 연동 실패: ${err.message}`);
        } finally {
            setIsUploading(false);
        }
    };

    const handleNotionImport = async (url: string) => {
        if (!url) {
            alert("Notion URL을 입력해주세요.");
            return;
        }
        setIsUploading(true);
        try {
            await portfolioApi.importNotion(url);
            alert("Notion 페이지 가져오기 성공! AI 분석이 시작되었습니다.");
            router.push('/my/portfolios');
        } catch (err: any) {
            console.error(err);
            alert(`Notion 연동 실패: ${err.message}`);
        } finally {
            setIsUploading(false);
        }
    };

    if (isUploading) {
        return (
            <div className="flex flex-col h-[70vh] items-center justify-center space-y-10 animate-in fade-in duration-700">
                <div className="relative">
                    <div className="h-28 w-28 rounded-full border-[6px] border-slate-100 border-t-blue-500 animate-spin" />
                    <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-10 w-10 text-blue-500 fill-blue-500 animate-pulse" />
                </div>
                <div className="text-center space-y-4 max-w-lg">
                    <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
                        AI 데이터 분석 및 업로드 중...
                    </h2>
                    <p className="text-slate-500 leading-relaxed font-medium">
                        서버로 데이터를 전송하고 있습니다.<br />잠시만 기다려주세요.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="container max-w-4xl mx-auto py-12 px-4 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center space-x-2 mb-4">
                <Button variant="ghost" size="icon" onClick={() => router.back()} className="-ml-3 hover:bg-slate-100 text-slate-400">
                    <ArrowLeft className="h-5 w-5" />
                </Button>
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900">포트폴리오 신규 등록</h1>
                    <p className="text-sm text-slate-500">데이터를 연결하면 AI가 자동으로 경험을 분석하고 최적화해 드립니다.</p>
                </div>
            </div>

            <Tabs defaultValue="github" className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-10 bg-slate-100 p-1 rounded-2xl">
                    <TabsTrigger value="github" className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm transition-all font-bold">GitHub</TabsTrigger>
                    <TabsTrigger value="notion" className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm transition-all font-bold">Notion</TabsTrigger>
                    <TabsTrigger value="file" className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-blue-600 data-[state=active]:shadow-sm transition-all font-bold">PDF / Files</TabsTrigger>
                </TabsList>

                <div className="grid gap-6">
                    {/* [GitHub] */}
                    <TabsContent value="github" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <Card className="border-slate-200 shadow-sm border-2 overflow-hidden hover:border-blue-200 transition-colors bg-white">
                            <CardHeader className="p-8">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-slate-900 rounded-2xl">
                                        <Github className="h-8 w-8 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <CardTitle className="text-xl font-bold text-slate-900">GitHub 리포지토리 분석</CardTitle>
                                        <CardDescription className="text-slate-500">전체 프로필 또는 특정 레포를 분석하여 포트폴리오를 생성합니다.</CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="px-8 pb-8 space-y-6">
                                <div className="p-6 rounded-2xl border border-slate-100 bg-slate-50/50 space-y-4">
                                    <Label className="font-bold text-slate-700">리포지토리 또는 프로필 URL</Label>
                                    <p className="text-xs text-slate-500 leading-relaxed font-medium">
                                        예: https://github.com/username 또는 https://github.com/username/repo
                                    </p>
                                    <div className="flex gap-2">
                                        <Input
                                            placeholder="https://github.com/..."
                                            className="border-slate-200 bg-white focus-visible:ring-blue-500 h-11"
                                            value={githubUrl}
                                            onChange={(e) => setGithubUrl(e.target.value)}
                                        />
                                        <Button onClick={() => handleGithubImport(githubUrl)} className="bg-blue-600 hover:bg-blue-700 text-white font-bold h-11 px-6 rounded-xl transition-all">
                                            연동 및 분석
                                        </Button>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* [Notion] */}
                    <TabsContent value="notion" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <Card className="border-slate-200 shadow-sm border-2 overflow-hidden bg-white">
                            <CardContent className="p-16 text-center space-y-8">
                                <div className="mx-auto w-24 h-24 bg-slate-50 rounded-3xl flex items-center justify-center border border-slate-100 shadow-inner group">
                                    <div className="text-4xl font-black text-slate-800 group-hover:scale-110 transition-transform">N</div>
                                </div>
                                <div className="space-y-3">
                                    <h3 className="text-2xl font-bold text-slate-900 tracking-tight">Notion 페이지 연결</h3>
                                    <p className="text-slate-500 max-w-sm mx-auto leading-relaxed font-medium">
                                        공개된 Notion 페이지 URL을 입력하세요.<br />
                                        하위 페이지까지 AI가 자동으로 분석합니다.
                                    </p>
                                </div>
                                <div className="flex gap-2 max-w-md mx-auto w-full">
                                    <Input
                                        placeholder="https://notion.site/..."
                                        className="border-slate-200 bg-white focus-visible:ring-blue-500 h-12"
                                        value={notionUrl}
                                        onChange={(e) => setNotionUrl(e.target.value)}
                                    />
                                    <Button
                                        onClick={() => handleNotionImport(notionUrl)}
                                        className="bg-blue-600 hover:bg-blue-700 text-white h-12 px-6 rounded-xl font-bold shadow-xl shadow-blue-500/10 transition-all hover:-translate-y-1"
                                    >
                                        가져오기 <ExternalLink className="ml-2 h-5 w-5" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* [File] */}
                    <TabsContent value="file" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <Card className="border-slate-200 shadow-sm border-2 overflow-hidden bg-white">
                            <CardContent className="p-8">
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileUpload}
                                    // multiple // Backend currently supports single file per request
                                    accept=".pdf,.doc,.docx,.hwp,.txt,.md"
                                    className="hidden"
                                />
                                <div
                                    onClick={() => fileInputRef.current?.click()}
                                    className="border-2 border-dashed border-slate-100 rounded-[2rem] p-20 flex flex-col items-center justify-center text-slate-400 hover:bg-blue-50/30 hover:border-blue-200 transition-all cursor-pointer group"
                                >
                                    <div className="relative mb-6">
                                        <div className="p-6 rounded-3xl bg-slate-50 group-hover:bg-white group-hover:shadow-lg transition-all duration-500">
                                            <Upload className="h-16 w-16 text-slate-300 group-hover:text-blue-500 group-hover:scale-110 transition-all duration-500" />
                                        </div>
                                        <div className="absolute -bottom-2 -right-2 bg-blue-600 h-8 w-8 rounded-full flex items-center justify-center text-white shadow-lg animate-bounce">
                                            <Plus className="h-5 w-5" />
                                        </div>
                                    </div>
                                    <p className="font-bold text-slate-800 text-2xl tracking-tight">파일을 드래그하여 업로드</p>
                                    <p className="text-slate-500 mt-3 font-medium text-center">
                                        PDF, Word, 텍스트 파일을 분석하여<br />
                                        프로젝트 항목을 자동 추출합니다.
                                    </p>
                                    <div className="flex gap-2 mt-8">
                                        {["PDF", "DOCX", "TXT", "MD"].map(ext => (
                                            <Badge key={ext} variant="outline" className="border-slate-200 text-slate-400 font-bold bg-white px-3 py-1">
                                                {ext}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </div>
            </Tabs>
        </div>
    );
}
