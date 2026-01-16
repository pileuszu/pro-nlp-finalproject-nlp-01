"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/useAuthStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

const loginSchema = z.object({
    email: z.string().email({ message: "유효한 이메일을 입력해주세요." }),
    password: z.string().min(1, { message: "비밀번호를 입력해주세요." }),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const router = useRouter();
    const login = useAuthStore((state) => state.login);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginForm>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginForm) => {
        try {
            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            if (!res.ok) throw new Error("로그인 실패");

            const responseData = await res.json();
            login(responseData.user); // Zustand Store 업데이트

            // 포트폴리오 체크 로직 (Flow: 포트폴리오 없으면 강제 이동)
            // 여기서는 Mocking 상황이므로 임의로 체크
            // 실제로는 /api/portfoliosCount 같은걸 찔러봐야 함

            router.push("/my/dashboard"); // 일단 대시보드로 이동
        } catch (error) {
            alert("로그인에 실패했습니다.");
        }
    };

    return (
        <Card className="w-full">
            <CardHeader className="space-y-1">
                <CardTitle className="text-2xl text-center">로그인</CardTitle>
                <CardDescription className="text-center">
                    이메일과 비밀번호를 입력하여 로그인하세요.
                </CardDescription>
            </CardHeader>
            <form onSubmit={handleSubmit(onSubmit)}>
                <CardContent className="grid gap-4">
                    <div className="grid gap-2">
                        <Label htmlFor="email">이메일</Label>
                        <Input id="email" type="email" placeholder="m@example.com" {...register("email")} />
                        {errors.email && <p className="text-red-500 text-xs">{errors.email.message}</p>}
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="password">비밀번호</Label>
                        <Input id="password" type="password" {...register("password")} />
                        {errors.password && <p className="text-red-500 text-xs">{errors.password.message}</p>}
                    </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-4">
                    <Button className="w-full" type="submit" disabled={isSubmitting}>
                        {isSubmitting ? "로그인 중..." : "로그인"}
                    </Button>
                    <div className="text-sm text-muted-foreground text-center">
                        계정이 없으신가요? <Link href="/signup" className="text-primary hover:underline">회원가입</Link>
                    </div>
                </CardFooter>
            </form>
        </Card>
    );
}
