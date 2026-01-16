"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, User, FileText, Briefcase, LogOut } from "lucide-react";

const sidebarItems = [
    { href: "/my/dashboard", icon: LayoutDashboard, label: "대시보드" },
    { href: "/my/cover-letters", icon: FileText, label: "자기소개서" },
    { href: "/my/portfolios", icon: Briefcase, label: "포트폴리오" },
    { href: "/my/profile", icon: User, label: "내 정보" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="flex h-screen w-64 flex-col border-r bg-background">
            <div className="flex h-14 items-center border-b px-6 font-bold text-xl">
                <Link href="/">Pro-NLP</Link>
            </div>
            <div className="flex-1 overflow-auto py-4">
                <nav className="grid items-start px-4 text-sm font-medium lg:px-4">
                    {sidebarItems.map((item) => {
                        const isActive = pathname.startsWith(item.href);
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary",
                                    isActive
                                        ? "bg-muted text-primary"
                                        : "text-muted-foreground"
                                )}
                            >
                                <item.icon className="h-4 w-4" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>
            </div>
            <div className="mt-auto border-t p-4">
                <Link
                    href="/"
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-all hover:text-primary"
                >
                    <LogOut className="h-4 w-4" />
                    로그아웃 (임시)
                </Link>
            </div>
        </div>
    );
}
