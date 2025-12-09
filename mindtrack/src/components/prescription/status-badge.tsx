"use client";

import { Badge } from "@/components/ui/badge";
import React from "react";
import { PrescriptionStatus } from "@/lib/prescription/types";

export function StatusBadge({ status }: { status: PrescriptionStatus }) {
  const map: Record<PrescriptionStatus, string> = {
    active: "bg-green-100 text-green-800",
    draft: "bg-gray-100 text-gray-800",
    voided: "bg-red-100 text-red-800",
    expired: "bg-yellow-100 text-yellow-800",
  };
  return <Badge className={map[status]}>{status}</Badge>;
}


