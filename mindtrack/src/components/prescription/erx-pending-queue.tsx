"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Prescription } from "@/lib/prescription/types";
import { EPrescriptionRecord } from "@/lib/prescription/erx-types";
import { Button } from "@/components/ui/button";

interface Props {
  items: EPrescriptionRecord[];
  prescriptions: Prescription[];
  onRetry?: (id: string) => void;
}

export function ErxPendingQueue({ items, prescriptions, onRetry }: Props) {
  const findPrescription = (id: string) => prescriptions.find((p) => p.id === id);

  const statusBadge = (status: EPrescriptionRecord["status"]) => {
    const map = {
      pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
      sent: "bg-green-100 text-green-800 border-green-200",
      failed: "bg-red-100 text-red-800 border-red-200",
    };
    return <Badge className={map[status]}>{status}</Badge>;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bekleyen E-Reçeteler</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Hasta</TableHead>
              <TableHead>İlaç</TableHead>
              <TableHead>Durum</TableHead>
              <TableHead>Oluşturma</TableHead>
              <TableHead>Mesaj</TableHead>
              <TableHead className="text-right">Aksiyon</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => {
              const p = findPrescription(item.prescriptionId);
              return (
                <TableRow key={item.id}>
                  <TableCell>{p?.patientName || "-"}</TableCell>
                  <TableCell>{p?.medications?.[0]?.name || "-"}</TableCell>
                <TableCell>{statusBadge(item.status)}</TableCell>
                  <TableCell>{new Date(item.createdAt).toLocaleString("tr-TR")}</TableCell>
                  <TableCell>{item.pharmacyResponseMessage || item.pharmacyResponseCode || "-"}</TableCell>
                  <TableCell className="text-right">
                    {item.status === "failed" && onRetry && (
                      <Button size="sm" variant="outline" onClick={() => onRetry(item.id)}>
                        Retry
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
            {items.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-gray-500 py-6">
                  Bekleyen e-reçete yok
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}


