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
  erxTotal?: number;
  onMetricClick: (tab: TabKey) => void;
  onSelectPrescription: (p: Prescription) => void;
}

export function OverviewTab({ prescriptions, region, erxTotal = 0, onMetricClick, onSelectPrescription }: Props) {
  const total = prescriptions.length;
  const active = prescriptions.filter((p) => p.status === "active").length;
  const critical = prescriptions.filter((p) => p.risk === "critical").length;
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
            <CardDescription>Son 30 gün (mock)</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{total}</p>
          </CardContent>
        </Card>
        <Card onClick={() => onMetricClick("prescriptions")} className="cursor-pointer hover:shadow">
          <CardHeader>
            <CardTitle>Aktif Reçeteler</CardTitle>
            <CardDescription>Kritik risk: {critical}</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{active}</p>
          </CardContent>
        </Card>
        <Card onClick={() => onMetricClick("erx")} className="cursor-pointer hover:shadow">
          <CardHeader>
            <CardTitle>E-Reçete</CardTitle>
            <CardDescription>Gönderilen/planlanan</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{erxTotal}</p>
            <p className="text-sm text-gray-600">Şu an mock sayaç</p>
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Son Reçeteler</CardTitle>
            <CardDescription>En son eklenen 5 kayıt</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-5 text-xs font-semibold text-gray-600">
              <span>Hasta</span>
              <span>İlaç(lar)</span>
              <span>Durum</span>
              <span>Risk</span>
              <span>Tarih</span>
            </div>
            {recent.map((p) => (
              <div
                key={p.id}
                className="grid grid-cols-5 items-center p-2 rounded-md hover:bg-muted cursor-pointer text-sm"
                onClick={() => onSelectPrescription(p)}
              >
                <div>{p.patientName}</div>
                <div>
                  {p.medications[0]?.name}
                  {p.medications.length > 1 ? ` +${p.medications.length - 1}` : ""}
                </div>
                <div>
                  <StatusBadge status={p.status} />
                </div>
                <div>
                  <RiskBadge risk={p.risk} />
                </div>
                <div>{new Date(p.createdAt).toLocaleDateString("tr-TR")}</div>
              </div>
            ))}
            {recent.length === 0 && <p className="text-sm text-gray-500">Kayıt yok</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Uyumluluk</CardTitle>
            <CardDescription>Bölgeye özel kısa bilgi</CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-gray-700 space-y-2">
            <p>Region: {region}</p>
            <p>Bu sprintte temel skor gösterimi. Detaylı audit/kontrollü maddeler Compliance sekmesinde.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


