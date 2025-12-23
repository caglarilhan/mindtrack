"use client";

import dynamic from "next/dynamic";
import { SOAPSkeleton } from "@/components/ui/skeleton";

// Lazy load AnalyticsDashboard with loading skeleton
export const AnalyticsDashboardLazy = dynamic(
  () => import("./analytics-dashboard").then((mod) => ({ default: mod.AnalyticsDashboard })),
  {
    loading: () => (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
        <SOAPSkeleton />
      </div>
    ),
    ssr: false, // Charts don't need SSR
  }
);





