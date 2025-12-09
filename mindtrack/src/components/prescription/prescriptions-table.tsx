"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Prescription } from "@/lib/prescription/types";
import { StatusBadge } from "./status-badge";
import { RiskBadge } from "./risk-badge";

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
                <TableHead>Aksiyonlar</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sorted.map((p) => (
                <TableRow key={p.id}>
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
                  <TableCell className="space-x-2">
                    <Button variant="outline" size="sm" onClick={() => onView(p.id)}>
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
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

