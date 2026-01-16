"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Recruit } from "@/types";
import Link from "next/link";

export default function HomePage() {
  const [recruits, setRecruits] = useState<Recruit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // MSW가 Intercept 하므로 실제 fetch 처럼 작성
    fetch("/api/recruits")
      .then((res) => res.json())
      .then((data) => {
        setRecruits(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch recruits", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="container py-8 px-4 md:px-8">
      <div className="mb-8 flex flex-col items-start gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">채용 공고</h1>
          <p className="text-muted-foreground mt-1">
            원하는 기업의 공고를 찾고 간편하게 자소서를 작성해보세요.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">최신순</Button>
          <Button variant="outline">인기순</Button>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-[200px] w-full animate-pulse rounded-xl bg-muted" />
          ))}
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {recruits.map((recruit) => (
            <Card key={recruit.id} className="flex flex-col hover:shadow-lg transition-shadow cursor-pointer group">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="line-clamp-1">{recruit.title}</CardTitle>
                </div>
                <CardDescription>{recruit.company}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <div className="flex flex-wrap gap-2 mt-2">
                  {recruit.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="border-t pt-4 text-sm text-muted-foreground flex justify-between items-center bg-muted/20 group-hover:bg-muted/40 transition-colors rounded-b-xl">
                <span>마감일: {recruit.deadline}</span>
                <Link href={`/recruit/${recruit.id}`}>
                  <Button size="sm" variant="ghost" className="h-8">지원하기 &rarr;</Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
