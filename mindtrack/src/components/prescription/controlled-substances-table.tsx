"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Prescription } from "@/lib/prescription/types";
import { Badge } from "@/components/ui/badge";

interface Props {
  prescriptions: Prescription[];
}

export function ControlledSubstancesTable({ prescriptions }: Props) {
  const controlled = prescriptions.filter((p) => p.risk === "high" || p.risk === "critical" || p.controlledSchedule);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Kontrollü Maddeler</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Hasta</TableHead>
              <TableHead>İlaç</TableHead>
              <TableHead>Risk</TableHead>
              <TableHead>Schedule</TableHead>
              <TableHead>Tarih</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {controlled.map((p) => (
              <TableRow key={p.id}>
                <TableCell>{p.patientName}</TableCell>
                <TableCell>{p.medications[0]?.name || "-"}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={p.risk === "critical" ? "bg-red-100 text-red-800" : "bg-orange-100 text-orange-800"}>
                    {p.risk}
                  </Badge>
                </TableCell>
                <TableCell>{p.controlledSchedule || "-"}</TableCell>
                <TableCell>{new Date(p.createdAt).toLocaleDateString("tr-TR")}</TableCell>
              </TableRow>
            ))}
            {controlled.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-gray-500 py-6">
                  Kontrollü madde kaydı yok
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}


