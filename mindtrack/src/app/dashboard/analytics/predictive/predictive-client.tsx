"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

const RELAPSE_DATA = [
  { week: "Week 1", risk: 0.42 },
  { week: "Week 2", risk: 0.48 },
  { week: "Week 3", risk: 0.51 },
  { week: "Week 4", risk: 0.47 },
  { week: "Week 5", risk: 0.55 },
];

const NO_SHOW_DATA = [
  { week: "Week 1", probability: 0.12 },
  { week: "Week 2", probability: 0.14 },
  { week: "Week 3", probability: 0.2 },
  { week: "Week 4", probability: 0.16 },
];

const FEATURE_IMPORTANCE = [
  { feature: "Last PHQ-9", value: 0.32 },
  { feature: "Sessions missed", value: 0.24 },
  { feature: "Medication adherence", value: 0.18 },
  { feature: "Care gap count", value: 0.12 },
  { feature: "Telehealth risk events", value: 0.08 },
];

export default function PredictiveClient() {
  const [metric, setMetric] = useState("relapse");
  return (
    <Tabs defaultValue="relapse" className="space-y-4" onValueChange={setMetric}>
      <TabsList>
        <TabsTrigger value="relapse">Relapse Risk</TabsTrigger>
        <TabsTrigger value="no-show">No-Show Forecast</TabsTrigger>
        <TabsTrigger value="denial">Billing Denial</TabsTrigger>
      </TabsList>
      <TabsContent value="relapse" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Relapse Risk Projection</CardTitle>
            <CardDescription>Demo verisi · model offline</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 mb-4">
              <Badge variant="destructive">Risk: 55%</Badge>
              <span className="text-sm text-muted-foreground">Top features: PHQ-9, missed sessions</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={RELAPSE_DATA}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
                  <Tooltip formatter={(value: number) => `${Math.round(value * 100)}%`} />
                  <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top Features (SHAP Placeholder)</CardTitle>
            <CardDescription>Gerçek SHAP grafiği Sprint 6'da bağlanacak</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {FEATURE_IMPORTANCE.map((item) => (
              <div key={item.feature} className="flex items-center justify-between text-sm">
                <span>{item.feature}</span>
                <div className="h-2 w-40 bg-muted rounded">
                  <div className="h-2 rounded bg-emerald-500" style={{ width: `${item.value * 100}%` }} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="no-show" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>No-Show Forecast</CardTitle>
            <CardDescription>Demo LightGBM output</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={NO_SHOW_DATA}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis domain={[0, 0.4]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
                  <Tooltip formatter={(value: number) => `${Math.round(value * 100)}%`} />
                  <Area type="monotone" dataKey="probability" stroke="#3b82f6" fill="#bfdbfe" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="denial" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Denial Forecast</CardTitle>
            <CardDescription>Örnek denial oranı: 22%</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Gerçek model pipeline'ı Sprint 6'da planlanacak. Şimdilik placeholder grafikleri gösteriyoruz.
            </p>
            <Button variant="outline" size="sm">Download Plan</Button>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
