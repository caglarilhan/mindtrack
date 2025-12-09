"use client";

import { Badge } from "@/components/ui/badge";
import React from "react";
import { PrescriptionRisk } from "@/lib/prescription/types";

export function RiskBadge({ risk }: { risk: PrescriptionRisk }) {
  const map: Record<PrescriptionRisk, string> = {
    low: "bg-emerald-100 text-emerald-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-orange-100 text-orange-800",
    critical: "bg-red-100 text-red-800",
  };
  return <Badge className={map[risk]}>{risk}</Badge>;
}


