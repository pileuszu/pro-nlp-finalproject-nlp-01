"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Sparkles, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

export type ProcessingStatus = 'PENDING' | 'PROCESSING' | 'REVIEW_REQUIRED' | 'COMPLETED' | 'FAILED';

interface StatusBadgeProps {
    status: ProcessingStatus | string; // Accept string for flexibility with API responses
    className?: string;
    showIcon?: boolean;
}

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
    const normalizedStatus = status?.toUpperCase();

    if (normalizedStatus === 'PENDING' || normalizedStatus === 'PROCESSING') {
        return (
            <Badge
                variant="outline"
                className={cn(
                    "bg-yellow-50 border-yellow-100 text-yellow-600 text-[10px] gap-1 font-black animate-pulse py-0.5",
                    className
                )}
            >
                {showIcon && <Loader2 className="h-2.5 w-2.5 animate-spin" />}
                {normalizedStatus === 'PENDING' ? 'PENDING...' : 'ANALYZING...'}
            </Badge>
        );
    }

    if (normalizedStatus === 'REVIEW_REQUIRED') {
        return (
            <Badge
                variant="outline"
                className={cn(
                    "bg-amber-500 border-amber-600 text-white text-[10px] gap-1 font-black py-0.5 shadow-sm shadow-amber-200 animate-bounce",
                    className
                )}
            >
                {showIcon && <Sparkles className="h-2.5 w-2.5 fill-white" />}
                검토 필요
            </Badge>
        );
    }

    if (normalizedStatus === 'COMPLETED') {
        return (
            <Badge
                variant="outline"
                className={cn(
                    "bg-emerald-50 border-emerald-100 text-emerald-600 text-[10px] gap-1 font-black py-0.5",
                    className
                )}
            >
                {showIcon && <CheckCircle2 className="h-2.5 w-2.5" />}
                최종 확정
            </Badge>
        );
    }

    if (normalizedStatus === 'FAILED') {
        return (
            <Badge
                variant="outline"
                className={cn(
                    "bg-red-50 border-red-100 text-red-600 text-[10px] gap-1 font-black py-0.5",
                    className
                )}
            >
                {showIcon && <AlertCircle className="h-2.5 w-2.5" />}
                분석 실패
            </Badge>
        );
    }

    // Default Fallback
    return (
        <Badge variant="outline" className={cn("text-[10px] font-bold py-0.5", className)}>
            {status}
        </Badge>
    );
}
