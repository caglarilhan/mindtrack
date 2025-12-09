"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Prescription } from "@/lib/prescription/types";
import { StatusBadge } from "./status-badge";
import { RiskBadge } from "./risk-badge";
import { Badge } from "@/components/ui/badge";

interface Props {
  prescriptions: Prescription[];
  onView: (id: string) => void;
  onVoid: (id: string) => void;
}

export function PrescriptionsTable({ prescriptions, onView, onVoid }: Props) {
  const [sortDesc, setSortDesc] = React.useState(true);

  const sorted = React.useMemo(() => {
    return [...prescriptions].sort((a, b) => {
      const diff = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      return sortDesc ? diff * -1 : diff;
    });
  }, [prescriptions, sortDesc]);

  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Hasta</TableHead>
                <TableHead>İlaçlar</TableHead>
                <TableHead className="cursor-pointer" onClick={() => setSortDesc((p) => !p)}>
                  Tarih {sortDesc ? "↓" : "↑"}
                </TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Region / Eczane</TableHead>
                <TableHead>Aksiyonlar</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
            {sorted.map((p) => (
              <TableRow
                key={p.id}
                className="cursor-pointer hover:bg-muted/40"
                onClick={() => onView(p.id)}
              >
                  <TableCell>{p.patientName}</TableCell>
                  <TableCell>
                    {p.medications[0]?.name}
                    {p.medications.length > 1 ? ` +${p.medications.length - 1}` : ""}
                  </TableCell>
                  <TableCell>{new Date(p.createdAt).toLocaleDateString("tr-TR")}</TableCell>
                  <TableCell>
                    <StatusBadge status={p.status} />
                  </TableCell>
                  <TableCell>
                    <RiskBadge risk={p.risk} />
                  </TableCell>
                <TableCell>
                  <div className="flex flex-col gap-1">
                    <Badge variant="outline">{p.region}</Badge>
                    {p.pharmacyName && (
                      <span className="text-xs text-gray-600">{p.pharmacyName}</span>
                    )}
                  </div>
                </TableCell>
                  <TableCell className="space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onView(p.id);
                      }}
                    >
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        e.stopPropagation();
                        if (confirm("Bu reçeteyi iptal etmek istiyor musunuz?")) onVoid(p.id);
                      }}
                    >
                      Void
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {sorted.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500 py-6">
                    Henüz reçete yok
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

