"use client";

import dynamic from "next/dynamic";

// Lazy load Recharts components (heavy library)
export const BarChartLazy = dynamic(
  () => import("recharts").then((mod) => mod.BarChart),
  { ssr: false }
);

export const LineChartLazy = dynamic(
  () => import("recharts").then((mod) => mod.LineChart),
  { ssr: false }
);

export const PieChartLazy = dynamic(
  () => import("recharts").then((mod) => mod.PieChart),
  { ssr: false }
);

export const ResponsiveContainerLazy = dynamic(
  () => import("recharts").then((mod) => mod.ResponsiveContainer),
  { ssr: false }
);

// Re-export other components that are lighter
export {
  Bar,
  Line,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";





