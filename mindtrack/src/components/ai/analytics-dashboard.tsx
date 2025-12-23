"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  BarChartLazy as BarChart, 
  LineChartLazy as LineChart, 
  PieChartLazy as PieChart,
  ResponsiveContainerLazy as ResponsiveContainer,
  Bar, 
  Line, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from "@/components/ai/charts-lazy";
import { TrendingUp, TrendingDown, Activity, AlertTriangle, Clock, FileText } from "@/lib/icons";
import type { SOAPAnalytics, TrendData, UsageStats } from "@/lib/ai/analytics";

interface AnalyticsDashboardProps {
  analytics: SOAPAnalytics;
  trends: TrendData[];
  usageStats: UsageStats;
}

const COLORS = {
  low: '#10b981',      // green
  medium: '#f59e0b',   // yellow
  high: '#ef4444',     // red
  critical: '#991b1b', // dark red
  standard: '#3b82f6', // blue
  premium: '#8b5cf6',  // purple
  consultation: '#ec4899', // pink
};

export function AnalyticsDashboard({ analytics, trends, usageStats }: AnalyticsDashboardProps) {
  // Risk distribution data for pie chart
  const riskData = [
    { name: 'Düşük', value: analytics.riskDistribution.low, color: COLORS.low },
    { name: 'Orta', value: analytics.riskDistribution.medium, color: COLORS.medium },
    { name: 'Yüksek', value: analytics.riskDistribution.high, color: COLORS.high },
    { name: 'Kritik', value: analytics.riskDistribution.critical, color: COLORS.critical },
  ].filter((item) => item.value > 0);

  // Mode usage data
  const modeData = [
    { name: 'Standart', value: analytics.modeUsage.standard, color: COLORS.standard },
    { name: 'Premium', value: analytics.modeUsage.premium, color: COLORS.premium },
    { name: 'Konsültasyon', value: analytics.modeUsage.consultation, color: COLORS.consultation },
  ].filter((item) => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Toplam SOAP Notu</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.totalNotes}</div>
            <p className="text-xs text-muted-foreground">
              {usageStats.avgNotesPerSession.toFixed(1)} not/seans
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ortalama Risk Skoru</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{usageStats.averageRiskScore.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Risk tespit oranı: %{usageStats.riskDetectionRate.toFixed(1)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ortalama Oluşturma Süresi</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(analytics.generationTime.average / 1000).toFixed(1)}s</div>
            <p className="text-xs text-muted-foreground">
              P95: {(analytics.generationTime.p95 / 1000).toFixed(1)}s
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Çok Kullanılan Mod</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{usageStats.mostUsedMode}</div>
            <p className="text-xs text-muted-foreground">
              {usageStats.mostUsedMode === 'standard' ? 'Standart' : 
               usageStats.mostUsedMode === 'premium' ? 'Premium' : 'Konsültasyon'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle>SOAP Notu Trendi (Son 30 Gün)</CardTitle>
            <CardDescription>Günlük not sayısı ve risk skoru</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString('tr-TR')}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="count" 
                  stroke="#3b82f6" 
                  name="Not Sayısı"
                  strokeWidth={2}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="riskScore" 
                  stroke="#ef4444" 
                  name="Risk Skoru"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Risk Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Dağılımı</CardTitle>
            <CardDescription>SOAP notlarındaki risk seviyeleri</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Mode Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Mod Kullanımı</CardTitle>
            <CardDescription>AI modlarının kullanım dağılımı</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={modeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8">
                  {modeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Monthly Notes */}
        <Card>
          <CardHeader>
            <CardTitle>Aylık Not Sayısı</CardTitle>
            <CardDescription>Son 6 ayın not sayısı</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.notesByMonth.slice(-6)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Average Length */}
      <Card>
        <CardHeader>
          <CardTitle>Ortalama Bölüm Uzunluğu</CardTitle>
          <CardDescription>SOAP notlarının bölüm bazında ortalama uzunlukları</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded">
              <div className="text-sm text-gray-600 mb-1">Subjective</div>
              <div className="text-2xl font-bold text-blue-600">{analytics.averageLength.subjective}</div>
              <div className="text-xs text-gray-500">karakter</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded">
              <div className="text-sm text-gray-600 mb-1">Objective</div>
              <div className="text-2xl font-bold text-green-600">{analytics.averageLength.objective}</div>
              <div className="text-xs text-gray-500">karakter</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded">
              <div className="text-sm text-gray-600 mb-1">Assessment</div>
              <div className="text-2xl font-bold text-yellow-600">{analytics.averageLength.assessment}</div>
              <div className="text-xs text-gray-500">karakter</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded">
              <div className="text-sm text-gray-600 mb-1">Plan</div>
              <div className="text-2xl font-bold text-purple-600">{analytics.averageLength.plan}</div>
              <div className="text-xs text-gray-500">karakter</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

