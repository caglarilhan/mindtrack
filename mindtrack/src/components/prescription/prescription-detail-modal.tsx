"use client";

import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Prescription } from "@/lib/prescription/types";

interface Props {
  prescription: Prescription | null;
  open: boolean;
  onClose: () => void;
}

export function PrescriptionDetailModal({ prescription, open, onClose }: Props) {
  if (!prescription) return null;
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>{prescription.patientName}</DialogTitle>
          <DialogDescription>Reçete detayları</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{prescription.status}</Badge>
            <Badge variant="secondary">{prescription.risk}</Badge>
            <Badge variant="outline">{prescription.region}</Badge>
          </div>

          <div className="text-sm text-gray-700">
            <p className="font-semibold">İlaçlar</p>
            <ul className="list-disc list-inside space-y-1">
              {prescription.medications.map((m, idx) => (
                <li key={idx}>
                  <span className="font-medium">{m.name}</span>
                  {m.doseMg ? ` ${m.doseMg}mg` : ""} {m.frequency ? `(${m.frequency})` : ""}
                </li>
              ))}
            </ul>
          </div>

          <div className="grid grid-cols-1 gap-2 text-sm text-gray-700">
            <div>
              <span className="font-semibold">Hasta ID: </span>
              {prescription.patientId}
            </div>
            {prescription.pharmacyName && (
              <div>
                <span className="font-semibold">Eczane: </span>
                {prescription.pharmacyName}
              </div>
            )}
            {prescription.notes && (
              <div>
                <span className="font-semibold">Notlar: </span>
                {prescription.notes}
              </div>
            )}
          </div>

          <div className="text-xs text-gray-500">
            Oluşturma: {new Date(prescription.createdAt).toLocaleString("tr-TR")}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}


