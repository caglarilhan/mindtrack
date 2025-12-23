"use client";

import { AnalyticsDashboardLazy } from "@/components/ai/analytics-dashboard-lazy";
import { useAnalytics } from "@/hooks/use-analytics";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSearchParams } from "next/navigation";

export default function AnalyticsPage() {
  const searchParams = useSearchParams();
  const clientId = searchParams.get("clientId") || undefined;
  const days = parseInt(searchParams.get("days") || "30", 10);
  
  const { data, isLoading, error } = useAnalytics(clientId, days);

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Analytics</CardTitle>
            <CardDescription>Yükleniyor...</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-24 bg-gray-100 rounded animate-pulse" />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Hata</CardTitle>
            <CardDescription>Analytics yüklenemedi</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="container mx-auto p-6">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>SOAP Analytics</CardTitle>
          <CardDescription>
            {clientId ? "Client Analytics" : "Genel Analytics"} - Son {days} gün
          </CardDescription>
        </CardHeader>
      </Card>
      
      <AnalyticsDashboardLazy
        analytics={data.analytics}
        trends={data.trends}
        usageStats={data.usageStats}
      />
    </div>
  );
}
