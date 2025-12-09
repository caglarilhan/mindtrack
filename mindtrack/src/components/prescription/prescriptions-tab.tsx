"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { PrescriptionsTable } from "./prescriptions-table";
import { Prescription } from "@/lib/prescription/types";

interface Props {
  prescriptions: Prescription[];
  onNewPrescriptionClick: () => void;
  onViewPrescription: (id: string) => void;
  onVoidPrescription: (id: string) => void;
}

export function PrescriptionsTab({
  prescriptions,
  onNewPrescriptionClick,
  onViewPrescription,
  onVoidPrescription,
}: Props) {
  const [search, setSearch] = React.useState("");
  const [status, setStatus] = React.useState<string>("all");

  const filtered = React.useMemo(() => {
    return prescriptions.filter((p) => {
      const matchesSearch =
        p.patientName.toLowerCase().includes(search.toLowerCase()) ||
        p.medications.some((m) => m.name.toLowerCase().includes(search.toLowerCase()));
      const matchesStatus = status === "all" ? true : p.status === status;
      return matchesSearch && matchesStatus;
    });
  }, [prescriptions, search, status]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Reçeteler</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Input
              placeholder="Hasta veya ilaç ara..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Durum" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Durumlar</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="voided">Voided</SelectItem>
                <SelectItem value="expired">Expired</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex justify-end">
              <Button onClick={onNewPrescriptionClick}>Yeni Reçete</Button>
            </div>
          </div>
          <PrescriptionsTable prescriptions={filtered} onView={onViewPrescription} onVoid={onVoidPrescription} />
          {filtered.length === 0 && (
            <div className="p-3 border rounded-md text-sm text-gray-700 bg-muted/30">
              Kayıt bulunamadı. Yeni Reçete oluşturmak için sağ üstteki butonu kullanın.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


