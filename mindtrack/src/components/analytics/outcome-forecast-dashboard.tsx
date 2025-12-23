"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target,
  Calendar,
  CheckCircle,
  AlertCircle,
  BarChart3,
  LineChart
} from "lucide-react";
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface OutcomeForecastDashboardProps {
  patientId?: string;
  clinicId?: string;
  period?: '30d' | '90d' | '180d' | '1y';
}

export function OutcomeForecastDashboard({ 
  patientId, 
  clinicId, 
  period = '90d' 
}: OutcomeForecastDashboardProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(period);

  useEffect(() => {
    fetchOutcomes();
  }, [patientId, clinicId, selectedPeriod]);

  const fetchOutcomes = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (patientId) params.set('patientId', patientId);
      if (clinicId) params.set('clinicId', clinicId);
      params.set('period', selectedPeriod);

      const res = await fetch(`/api/analytics/outcomes?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch outcomes');
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4">Yükleniyor...</div>;
  }

  if (error || !data) {
    return <div className="p-4 text-red-600">Hata: {error || 'Veri bulunamadı'}</div>;
  }

  const { summary, trends, forecast } = data;

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="flex items-center gap-2">
        {(['30d', '90d', '180d', '1y'] as const).map((p) => (
          <Button
            key={p}
            variant={selectedPeriod === p ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedPeriod(p)}
          >
            {p === '30d' ? '30 Gün' : p === '90d' ? '90 Gün' : p === '180d' ? '180 Gün' : '1 Yıl'}
          </Button>
        ))}
        <Button variant="ghost" size="sm" onClick={fetchOutcomes}>
          Yenile
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Toplam Değerlendirme</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.totalAssessments}</div>
            <p className="text-xs text-muted-foreground">Son {selectedPeriod}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tamamlanma Oranı</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.completionRate.toFixed(1)}%</div>
            <Progress value={summary.completionRate} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {summary.completedAppointments} / {summary.totalAppointments} seans
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tahmin</CardTitle>
          </CardHeader>
          <CardContent>
            {forecast ? (
              <>
                <div className="flex items-center gap-2">
                  {forecast.next30Days === 'improving' ? (
                    <TrendingUp className="h-5 w-5 text-green-600" />
                  ) : forecast.next30Days === 'declining' ? (
                    <TrendingDown className="h-5 w-5 text-red-600" />
                  ) : (
                    <Activity className="h-5 w-5 text-yellow-600" />
                  )}
                  <span className="text-lg font-semibold capitalize">
                    {forecast.next30Days === 'improving' ? 'İyileşme' : forecast.next30Days === 'declining' ? 'Düşüş' : 'Stabil'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Güven: {forecast.confidence === 'high' ? 'Yüksek' : forecast.confidence === 'medium' ? 'Orta' : 'Düşük'}
                </p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Yetersiz veri</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tahmin Edilen Skor</CardTitle>
          </CardHeader>
          <CardContent>
            {forecast ? (
              <div className="text-2xl font-bold">{forecast.predictedScore}%</div>
            ) : (
              <p className="text-sm text-muted-foreground">-</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Score Trends Chart */}
      {trends.scoreTrends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Skor Trendi</CardTitle>
            <CardDescription>Zaman içinde değerlendirme skorları</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsLineChart data={trends.scoreTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="percentage" stroke="#2563eb" name="Skor %" />
              </RechartsLineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Severity Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Şiddet Dağılımı</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(trends.severityDistribution).map(([severity, count]) => (
              <div key={severity} className="text-center">
                <div className="text-2xl font-bold">{count as number}</div>
                <Badge variant={
                  severity === 'critical' ? 'destructive' :
                  severity === 'high' ? 'destructive' :
                  severity === 'medium' ? 'default' : 'secondary'
                }>
                  {severity === 'critical' ? 'Kritik' :
                   severity === 'high' ? 'Yüksek' :
                   severity === 'medium' ? 'Orta' : 'Düşük'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}










