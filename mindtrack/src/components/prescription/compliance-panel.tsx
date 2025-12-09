"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { REGION_CONFIG } from "@/lib/prescription/region-config";
import { RegionId, Prescription } from "@/lib/prescription/types";
import { calculateComplianceSummary } from "@/lib/prescription/compliance-rules";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface Props {
  region: RegionId;
  prescriptions?: Prescription[];
}

export function CompliancePanel({ region, prescriptions = [] }: Props) {
  const cfg = REGION_CONFIG[region];
  const summary = calculateComplianceSummary(prescriptions, region);
  return (
    <Card>
      <CardHeader>
        <CardTitle>{cfg.complianceTitle}</CardTitle>
        <CardDescription>{summary.ruleLabel}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Uyumluluk Skoru</span>
            <span className="font-semibold">{summary.score}%</span>
          </div>
          <Progress value={summary.score} />
          <div className="text-sm text-gray-700">
            Kontrollü reçete: {summary.totalControlled} / {summary.limit} ({summary.usagePercent}%)
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span>Kontrollü kullanım</span>
              <span>{summary.usagePercent}%</span>
            </div>
            <Progress value={summary.usagePercent} />
            <div className="text-xs text-gray-600">
              Kalan limit: {summary.remaining} / {summary.limit}
            </div>
          </div>
          {summary.scheduleCounts && Object.keys(summary.scheduleCounts).length > 0 && (
            <div className="flex flex-wrap gap-2 text-sm text-gray-700">
              {Object.entries(summary.scheduleCounts).map(([sch, cnt]) => (
                <Badge key={sch} variant="outline">
                  Schedule {sch}: {cnt}
                </Badge>
              ))}
            </div>
          )}
          {summary.warnings.length > 0 && (
            <ul className="list-disc list-inside text-sm text-yellow-700">
              {summary.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          )}
          {summary.warnings.length === 0 && (
            <div className="text-sm text-green-700">Şu anda kritik uyarı yok.</div>
          )}
          {summary.ruleNotes && summary.ruleNotes.length > 0 && (
            <ul className="list-disc list-inside text-sm text-gray-700">
              {summary.ruleNotes.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
