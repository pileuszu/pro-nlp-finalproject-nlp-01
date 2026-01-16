"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CoverLetter } from "@/types";

export default function CoverLettersPage() {
    const [coverLetters, setCoverLetters] = useState<CoverLetter[]>([]);

    useEffect(() => {
        fetch('/api/cover-letters')
            .then(res => res.json())
            .then(data => setCoverLetters(data));
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">자기소개서 보관함</h2>
            </div>

            <div className="space-y-4">
                {coverLetters.map((cl) => (
                    <Card key={cl.id} className="cursor-pointer hover:shadow-md transition-shadow">
                        <CardHeader>
                            <CardTitle>{cl.title}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground line-clamp-2">{cl.content}</p>
                            <p className="text-xs text-muted-foreground mt-4">수정일: {cl.updatedAt}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
}
