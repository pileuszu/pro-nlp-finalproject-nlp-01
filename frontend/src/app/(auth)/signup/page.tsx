"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import Link from "next/link";
import { useState } from "react";
import { User, Mail, Lock, ArrowRight, CheckCircle2 } from "lucide-react";

export default function SignupPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);

    const handleSignup = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        // Mock signup delay
        setTimeout(() => {
            alert("회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.");
            router.push("/login");
            setLoading(false);
        }, 1500);
    };

    return (
        <div className="flex items-center justify-center min-h-screen px-4 bg-slate-50/50 animate-in fade-in duration-700">
            <div className="w-full max-w-[600px] space-y-6">

                {/* Branding Section */}
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-black tracking-tight text-slate-900">
                        Pro-NLP <span className="text-blue-600">Membership</span>
                    </h1>
                    <p className="text-slate-500">
                        취업 성공을 위한 첫 걸음을 내딛으세요.
                    </p>
                </div>

                <Card className="shadow-2xl border-slate-200 bg-white overflow-hidden rounded-xl">
                    <CardHeader className="space-y-1 text-center bg-slate-50/50 border-b border-slate-100 py-8">
                        <CardTitle className="text-xl font-bold text-slate-800">계정 생성</CardTitle>
                        <CardDescription className="text-slate-400 text-sm">
                            아래 정보를 입력하여 무료로 시작하세요.
                        </CardDescription>
                    </CardHeader>

                    <form onSubmit={handleSignup}>
                        <CardContent className="space-y-4 p-10">
                            <div className="space-y-2">
                                <Label htmlFor="name" className="text-xs font-bold text-slate-500 uppercase tracking-wider ml-1">이름</Label>
                                <div className="relative border-none">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                                        <User className="h-4 w-4" />
                                    </div>
                                    <Input
                                        id="name"
                                        placeholder="홍길동"
                                        required
                                        className="pl-11 h-11 border-slate-200 focus-visible:ring-blue-500 bg-slate-50/30 text-sm transition-all focus:bg-white rounded-md"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email" className="text-xs font-bold text-slate-500 uppercase tracking-wider ml-1">이메일 주소</Label>
                                <div className="relative border-none">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                                        <Mail className="h-4 w-4" />
                                    </div>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="name@example.com"
                                        required
                                        className="pl-11 h-11 border-slate-200 focus-visible:ring-blue-500 bg-slate-50/30 text-sm transition-all focus:bg-white rounded-md"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="password" className="text-xs font-bold text-slate-500 uppercase tracking-wider ml-1">비밀번호</Label>
                                    <div className="relative border-none">
                                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                                            <Lock className="h-4 w-4" />
                                        </div>
                                        <Input
                                            id="password"
                                            type="password"
                                            required
                                            placeholder="••••••••"
                                            className="pl-11 h-11 border-slate-200 focus-visible:ring-blue-500 bg-slate-50/30 text-sm transition-all focus:bg-white rounded-md"
                                        />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="passwordConfirm" className="text-xs font-bold text-slate-500 uppercase tracking-wider ml-1">비밀번호 확인</Label>
                                    <div className="relative border-none">
                                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                                            <CheckCircle2 className="h-4 w-4" />
                                        </div>
                                        <Input
                                            id="passwordConfirm"
                                            type="password"
                                            required
                                            placeholder="••••••••"
                                            className="pl-11 h-11 border-slate-200 focus-visible:ring-blue-500 bg-slate-50/30 text-sm transition-all focus:bg-white rounded-md"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="pt-2">
                                <Button
                                    variant="brand"
                                    size="lg"
                                    className="w-full rounded-md"
                                    type="submit"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        "계정 생성 중..."
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            가입 완료하기 <ArrowRight className="h-4 w-4" />
                                        </span>
                                    )}
                                </Button>
                            </div>
                        </CardContent>

                        <CardFooter className="flex justify-center pb-8 pt-0">
                            <p className="text-sm text-slate-500">
                                이미 계정이 있으신가요?{" "}
                                <Link href="/login" className="text-blue-600 font-bold hover:underline transition-colors ml-1">
                                    로그인하기
                                </Link>
                            </p>
                        </CardFooter>
                    </form>
                </Card>
            </div>
        </div>
    );
}
