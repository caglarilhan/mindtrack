"use client";

import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/react-query";
import type { SOAPAnalytics, TrendData, UsageStats } from "@/lib/ai/analytics";

interface AnalyticsResponse {
  analytics: SOAPAnalytics;
  trends: TrendData[];
  usageStats: UsageStats;
}

/**
 * Analytics verilerini fetch etmek için hook
 */
export function useAnalytics(clientId?: string, days: number = 30) {
  return useQuery({
    queryKey: queryKeys.analytics(clientId, days),
    queryFn: async (): Promise<AnalyticsResponse> => {
      const params = new URLSearchParams();
      if (clientId) params.set("clientId", clientId);
      params.set("days", days.toString());

      const response = await fetch(`/api/ai/analytics?${params.toString()}`);

      if (!response.ok) {
        throw new Error("Failed to fetch analytics");
      }

      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 dakika - analytics daha az değişir
  });
}





