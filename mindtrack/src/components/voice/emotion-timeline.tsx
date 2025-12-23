"use client";

/**
 * Emotion Timeline Component
 * Real-time emotion visualization during session
 */

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { EmotionScores } from "@/lib/ai/emotion-detection";
import type { RiskDetectionResult } from "@/lib/risk/voice-risk-detection";

export interface EmotionTimelinePoint {
  timestamp: number;
  emotions: EmotionScores;
  riskLevel?: "low" | "medium" | "high" | "critical";
}

export interface EmotionTimelineProps {
  points: EmotionTimelinePoint[];
  onRiskAlert?: (risk: RiskDetectionResult) => void;
}

export function EmotionTimeline({ points, onRiskAlert }: EmotionTimelineProps) {
  const [chartData, setChartData] = useState<Array<{
    time: string;
    sadness: number;
    anxiety: number;
    anger: number;
    happiness: number;
    fear: number;
    hope: number;
    mood: number;
  }>>([]);

  useEffect(() => {
    // Convert points to chart data
    const data = points.map((point) => ({
      time: new Date(point.timestamp).toLocaleTimeString("tr-TR", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
      sadness: point.emotions.sadness * 100,
      anxiety: point.emotions.anxiety * 100,
      anger: point.emotions.anger * 100,
      happiness: point.emotions.happiness * 100,
      fear: point.emotions.fear * 100,
      hope: point.emotions.hope * 100,
      mood: (point.emotions.overallMood + 1) * 50, // Convert -1 to 1 range to 0-100
    }));

    setChartData(data);
  }, [points]);

  if (points.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center text-muted-foreground">
          <p>Henüz duygu verisi yok</p>
          <p className="text-sm mt-2">Ses kaydı başladığında duygular burada görünecek</p>
        </div>
      </Card>
    );
  }

  const latestPoint = points[points.length - 1];
  const riskColor = latestPoint.riskLevel === "critical" ? "bg-red-500" :
                    latestPoint.riskLevel === "high" ? "bg-orange-500" :
                    latestPoint.riskLevel === "medium" ? "bg-yellow-500" :
                    "bg-green-500";

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Duygu Zaman Çizelgesi</h3>
          {latestPoint.riskLevel && (
            <div className={`px-3 py-1 rounded-full text-white text-sm ${riskColor}`}>
              Risk: {latestPoint.riskLevel.toUpperCase()}
            </div>
          )}
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="sadness" stroke="#ef4444" strokeWidth={2} name="Üzgün" />
            <Line type="monotone" dataKey="anxiety" stroke="#f59e0b" strokeWidth={2} name="Kaygılı" />
            <Line type="monotone" dataKey="anger" stroke="#dc2626" strokeWidth={2} name="Öfkeli" />
            <Line type="monotone" dataKey="happiness" stroke="#10b981" strokeWidth={2} name="Mutlu" />
            <Line type="monotone" dataKey="fear" stroke="#8b5cf6" strokeWidth={2} name="Korkulu" />
            <Line type="monotone" dataKey="hope" stroke="#3b82f6" strokeWidth={2} name="Umutlu" />
            <Line type="monotone" dataKey="mood" stroke="#6366f1" strokeWidth={3} name="Genel Ruh Hali" />
          </LineChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground">Son Üzgünlük</div>
            <div className="text-lg font-semibold">{(latestPoint.emotions.sadness * 100).toFixed(0)}%</div>
          </div>
          <div>
            <div className="text-muted-foreground">Son Kaygı</div>
            <div className="text-lg font-semibold">{(latestPoint.emotions.anxiety * 100).toFixed(0)}%</div>
          </div>
          <div>
            <div className="text-muted-foreground">Son Mutluluk</div>
            <div className="text-lg font-semibold">{(latestPoint.emotions.happiness * 100).toFixed(0)}%</div>
          </div>
          <div>
            <div className="text-muted-foreground">Genel Ruh Hali</div>
            <div className={`text-lg font-semibold ${
              latestPoint.emotions.overallMood > 0.3 ? "text-green-600" :
              latestPoint.emotions.overallMood < -0.3 ? "text-red-600" :
              "text-yellow-600"
            }`}>
              {latestPoint.emotions.overallMood > 0.3 ? "Pozitif" :
               latestPoint.emotions.overallMood < -0.3 ? "Negatif" :
               "Nötr"}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}





