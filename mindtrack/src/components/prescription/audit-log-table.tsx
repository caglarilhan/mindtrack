"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { AuditLogEntry } from "@/lib/prescription/audit-log";

interface Props {
  logs: AuditLogEntry[];
}

export function AuditLogTable({ logs }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit Log</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tarih</TableHead>
              <TableHead>Kullanıcı</TableHead>
              <TableHead>Olay</TableHead>
              <TableHead>Reçete</TableHead>
              <TableHead>Detay</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>{new Date(log.timestamp).toLocaleString("tr-TR")}</TableCell>
                <TableCell>{log.userId}</TableCell>
                <TableCell>
                  <Badge variant="outline">{log.eventType}</Badge>
                </TableCell>
                <TableCell>{log.prescriptionId || "-"}</TableCell>
                <TableCell className="max-w-[300px] whitespace-pre-wrap">{log.details}</TableCell>
              </TableRow>
            ))}
            {logs.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-gray-500 py-6">
                  Kayıt yok
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}


