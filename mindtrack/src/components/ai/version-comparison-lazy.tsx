"use client";

import dynamic from "next/dynamic";
import { SOAPSkeleton } from "@/components/ui/skeleton";

// Lazy load VersionComparison
export const VersionComparisonLazy = dynamic(
  () => import("./version-comparison").then((mod) => ({ default: mod.VersionComparison })),
  {
    loading: () => <SOAPSkeleton />,
    ssr: false,
  }
);





