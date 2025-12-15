"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TrendingUp, ShieldAlert, Target, CheckCircle2 } from "lucide-react";

type RiskLevel = "low" | "medium" | "high";

interface OutcomePredictorProps {
  clientName?: string;
  diagnosis?: string;
  riskLevel?: RiskLevel;
  progressPercent: number; // 0-100 overall treatment progress
  sessionsCompleted?: number;
  totalSessions?: number;
}

export default function AIOutcomePredictor({
  clientName,
  diagnosis,
  riskLevel = "medium",
  progressPercent,
  sessionsCompleted = 0,
  totalSessions = 12,
}: OutcomePredictorProps) {
  // Simple heuristic for success probability
  const base = 60;
  const progressBoost = Math.min(progressPercent * 0.4, 30);
  const riskPenalty = riskLevel === "high" ? 15 : riskLevel === "medium" ? 7 : 0;
  const successProbability = Math.max(
    5,
    Math.min(95, Math.round(base + progressBoost - riskPenalty))
  );

  const sessionsRemaining = Math.max(totalSessions - sessionsCompleted, 0);
  const estimatedWeeks =
    sessionsRemaining <= 0 ? 0 : Math.max(2, Math.round(sessionsRemaining / 1));

  const recommendations: string[] = [];
  if (successProbability < 60) {
    recommendations.push("Seans sıklığını artırın veya modality değişimini düşünün.");
  }
  if (riskLevel !== "low") {
    recommendations.push("Risk yönetimi için guardrails ve kriz protokolünü gözden geçirin.");
  }
  if (progressPercent < 40) {
    recommendations.push("Hedefleri daha küçük adımlara bölüp kısa vadeli başarılar ekleyin.");
  }
  if (successProbability >= 70) {
    recommendations.push("Mevcut plan iyi ilerliyor, aynı yaklaşımı koruyun.");
  }

  const riskBadgeVariant = riskLevel === "high" ? "destructive" : riskLevel === "medium" ? "secondary" : "outline";

  return (
    <Card className="border-purple-200 bg-purple-50/40">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-purple-600" />
          Outcome Predictor
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2 flex-wrap">
          {clientName && <Badge variant="outline">{clientName}</Badge>}
          {diagnosis && <Badge variant="outline">{diagnosis}</Badge>}
          <Badge variant={riskBadgeVariant}>Risk: {riskLevel}</Badge>
          <Badge variant="secondary">
            {sessionsCompleted}/{totalSessions} seans
          </Badge>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold">Başarı Olasılığı</span>
            <span
              className={`text-lg font-bold ${
                successProbability >= 70
                  ? "text-green-600"
                  : successProbability >= 50
                  ? "text-orange-600"
                  : "text-red-600"
              }`}
            >
              %{successProbability}
            </span>
          </div>
          <Progress
            value={successProbability}
            className={`h-3 ${
              successProbability >= 70
                ? "[&>div]:bg-green-600"
                : successProbability >= 50
                ? "[&>div]:bg-orange-500"
                : "[&>div]:bg-red-500"
            }`}
          />
          <p className="text-xs text-gray-600 mt-2">
            Tahmini tamamlanma: {estimatedWeeks} hafta · Seans kalan: {sessionsRemaining}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Alert className="bg-white">
            <Target className="h-4 w-4" />
            <AlertDescription className="text-sm">
              İlerleme: %{Math.round(progressPercent)} · Hedeflere doğru gidişatı sürdürün.
            </AlertDescription>
          </Alert>
          {riskLevel !== "low" && (
            <Alert variant="destructive">
              <ShieldAlert className="h-4 w-4" />
              <AlertDescription className="text-sm">
                Risk seviyesi {riskLevel}. Seans öncesi risk kontrol listesi uygulayın.
              </AlertDescription>
            </Alert>
          )}
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            Öneriler
          </p>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

