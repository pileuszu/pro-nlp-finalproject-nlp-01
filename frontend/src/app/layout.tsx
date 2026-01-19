import { Analytics } from "@vercel/analytics/next"
import { SpeedInsights } from "@vercel/speed-insights/next"
import type { Metadata } from "next";
import { Noto_Sans_KR as FontSans } from "next/font/google";
import { cn } from "@/lib/utils";
import "./globals.css";
import { MSWComponent } from "@/components/MSWComponent";

const fontSans = FontSans({
    subsets: ["latin"],
    weight: ["300", "400", "500", "700", "900"],
    variable: "--font-sans",
});

export const metadata: Metadata = {
    title: "Pro-NLP Job Manager",
    description: "AI-powered job application manager",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="ko" suppressHydrationWarning>
            <body className={cn(
                "min-h-screen bg-background font-sans antialiased flex flex-col",
                fontSans.variable
            )}>
                <MSWComponent>
                    {children}
                </MSWComponent>
                <Analytics />
                <SpeedInsights />
            </body>
        </html>
    );
}
