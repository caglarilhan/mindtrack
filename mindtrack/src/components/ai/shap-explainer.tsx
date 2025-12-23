"use client";

import * as React from "react";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Info,
  BarChart3,
  AlertCircle
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";

interface ShapExplainerProps {
  patientId?: string;
  decisionType?: string;
  features?: Record<string, number>;
}

export function ShapExplainer({ 
  patientId, 
  decisionType = 'risk_assessment',
  features 
}: ShapExplainerProps) {
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [inputPatientId, setInputPatientId] = useState(patientId || '');

  const generateExplanation = async () => {
    if (!inputPatientId) {
      setError('Hasta ID gerekli');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/ai/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: inputPatientId,
          decisionType,
          features
        })
      });

      if (!res.ok) throw new Error('Açıklama oluşturulamadı');
      const json = await res.json();
      setExplanation(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (patientId) {
      generateExplanation();
    }
  }, [patientId]);

  const chartData = explanation?.featureImportance?.map((item: any) => ({
    feature: item.feature,
    importance: item.importance,
    contribution: item.contribution
  })) || [];

  const COLORS = {
    positive: '#ef4444', // red
    negative: '#10b981' // green
  };

  return (
    <div className="space-y-4">
      {/* Input */}
      {!patientId && (
        <Card>
          <CardHeader>
            <CardTitle>Açıklanabilir AI (XAI)</CardTitle>
            <CardDescription>Model kararlarının açıklamasını görüntüle</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="patientId">Hasta ID</Label>
              <Input
                id="patientId"
                value={inputPatientId}
                onChange={(e) => setInputPatientId(e.target.value)}
                placeholder="Hasta ID girin"
                className="mt-1"
              />
            </div>
            <Button onClick={generateExplanation} disabled={loading}>
              {loading ? 'Yükleniyor...' : 'Açıklama Oluştur'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Explanation */}
      {explanation && (
        <>
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Model Açıklaması
              </CardTitle>
              <CardDescription>{explanation.explanation}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Model:</span>
                  <Badge>{explanation.model}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Karar Tipi:</span>
                  <Badge variant="outline">{explanation.decisionType}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Zaman:</span>
                  <span className="text-muted-foreground">
                    {new Date(explanation.timestamp).toLocaleString('tr-TR')}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Top Contributors */}
          {explanation.topContributors && explanation.topContributors.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>En Etkili Faktörler</CardTitle>
                <CardDescription>Bu kararı en çok etkileyen özellikler</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {explanation.topContributors.map((contributor: any, idx: number) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{contributor.feature}</span>
                        <div className="flex items-center gap-2">
                          {contributor.contribution === 'positive' ? (
                            <TrendingUp className="h-4 w-4 text-red-600" />
                          ) : (
                            <TrendingDown className="h-4 w-4 text-green-600" />
                          )}
                          <Badge variant={contributor.contribution === 'positive' ? 'destructive' : 'default'}>
                            {(contributor.importance * 100).toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                      <Progress 
                        value={contributor.importance * 100} 
                        className="h-2"
                      />
                      <p className="text-xs text-muted-foreground">
                        {contributor.contribution === 'positive' 
                          ? 'Risk seviyesini artırıyor' 
                          : 'Risk seviyesini düşürüyor'}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Feature Importance Chart */}
          {chartData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Özellik Önemi</CardTitle>
                <CardDescription>SHAP değerleri ile feature importance</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={chartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="feature" type="category" width={150} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="importance" name="Önem">
                      {chartData.map((entry: any, index: number) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.contribution === 'positive' ? COLORS.positive : COLORS.negative} 
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="flex items-center gap-4 mt-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-red-500" />
                    <span>Risk Artırıcı</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-green-500" />
                    <span>Risk Azaltıcı</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}










