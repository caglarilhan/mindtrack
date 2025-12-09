"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Prescription } from "@/lib/prescription/types";
import { RiskBadge } from "./risk-badge";
import { StatusBadge } from "./status-badge";
import { calculateComplianceSummary } from "@/lib/prescription/compliance-rules";

type TabKey = "prescriptions" | "erx" | "compliance";

interface Props {
  prescriptions: Prescription[];
  region: string;
  onMetricClick: (tab: TabKey) => void;
  onSelectPrescription: (p: Prescription) => void;
}

export function OverviewTab({ prescriptions, region, onMetricClick, onSelectPrescription }: Props) {
  const total = prescriptions.length;
  const active = prescriptions.filter((p) => p.status === "active").length;
  const critical = prescriptions.filter((p) => p.risk === "critical").length;
  const erxTotal = Math.floor(total * 0.8);
  const complianceScore = calculateComplianceSummary(prescriptions, region as any).score;

  const recent = [...prescriptions]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card onClick={() => onMetricClick("prescriptions")} className="cursor-pointer hover:shadow">
          <CardHeader>
            <CardTitle>Toplam Reçete</CardTitle>
            <CardDescription>Son kayıtlar</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{total}</p>
          </CardContent>
        </Card>
        <Card onClick={() => onMetricClick("erx")} className="cursor-pointer hover:shadow">
          <CardHeader>
            <CardTitle>E-Reçete</CardTitle>
            <CardDescription>Uyumluluk oranı</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{erxTotal}</p>
            <p className="text-sm text-gray-600">94% compliance (mock)</p>
          </CardContent>
        </Card>
        <Card onClick={() => onMetricClick("prescriptions")} className="cursor-pointer hover:shadow">
          <CardHeader>
            <CardTitle>Aktif Reçeteler</CardTitle>
            <CardDescription>Kritik riskler</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{active}</p>
            <p className="text-sm text-red-600">{critical} critical</p>
          </CardContent>
        </Card>
        <Card onClick={() => onMetricClick("compliance")} className="cursor-pointer hover:shadow">
          <CardHeader>
            <CardTitle>Uyumluluk Skoru</CardTitle>
            <CardDescription>Mock skor</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{complianceScore}%</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Son Reçeteler</CardTitle>
          <CardDescription>En son eklenen 5 kayıt</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {recent.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between p-3 bg-muted/30 rounded-lg cursor-pointer hover:bg-muted"
              onClick={() => onSelectPrescription(p)}
            >
              <div>
                <p className="font-medium">{p.patientName}</p>
                <p className="text-sm text-gray-600">
                  {p.medications[0]?.name}
                  {p.medications.length > 1 ? ` +${p.medications.length - 1}` : ""}
                </p>
              </div>
                <div className="flex gap-2">
                  <StatusBadge status={p.status} />
                  <RiskBadge risk={p.risk} />
                </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}


