"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";

const MOCK_THREADS = [
  {
    id: "1",
    title: "Complex trauma – grounding techniques?",
    tag: "Trauma",
    region: "us" as const,
    replies: 4,
  },
  {
    id: "2",
    title: "EU – telehealth consent templates",
    tag: "Legal",
    region: "eu" as const,
    replies: 2,
  },
];

export default function CommunityClient() {
  const [draft, setDraft] = useState("");

  return (
    <div className="grid gap-6 md:grid-cols-[2fr,1fr] mt-4">
      <div className="space-y-4">
        {MOCK_THREADS.map((t) => (
          <Card key={t.id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-base">
                <span>{t.title}</span>
                <div className="flex gap-2 items-center">
                  <Badge variant="outline">{t.tag}</Badge>
                  <Badge variant="secondary">{t.region.toUpperCase()}</Badge>
                </div>
              </CardTitle>
              <CardDescription>{t.replies} replies · anonymized case snippets only</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
      <div className="space-y-3">
        <Card>
          <CardHeader>
            <CardTitle>New discussion (placeholder)</CardTitle>
            <CardDescription>
              Kimlik bilgisi paylaşmadan, sadece genel klinik soru ve guideline isteği yazın.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <Textarea
              rows={5}
              placeholder="Örnek: 'Adult ADHD + anxiety için session structure önerileri?'"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
            />
            <Button className="w-full" disabled>
              Post (mock)
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Guardrails</CardTitle>
            <CardDescription>Gizlilik ve regülasyon kuralları</CardDescription>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground space-y-1">
            <p>- İsim, telefon, adres, kurum bilgisi gibi tanımlayıcı veri paylaşmayın.</p>
            <p>- Sadece minimum gerekli klinik bağlamı yazın.</p>
            <p>- Ülke politikalarına göre community özelliği kapatılabilir.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
