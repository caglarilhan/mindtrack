"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RegionId, Prescription } from "@/lib/prescription/types";
import { NewPrescriptionForm } from "./new-prescription-form";
import { ErxPendingQueue } from "./erx-pending-queue";
import { EPrescriptionRecord } from "@/lib/prescription/erx-types";
import { PrescriptionTemplates } from "./prescription-templates";
import { PrescriptionTemplate } from "@/lib/prescription/templates";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CheckCircle, XCircle } from "lucide-react";

interface Props {
  region: RegionId;
  onCreatePrescription: (p: Prescription) => void;
  onSendERx: (prescription: Prescription) => void;
  erxRecords: EPrescriptionRecord[];
  prescriptions: Prescription[];
  onRetryERx: (erxId: string) => void;
  message?: { type: "success" | "error"; text: string } | null;
}

export function ErxTab({ region, onCreatePrescription, onSendERx, erxRecords, prescriptions, onRetryERx, message }: Props) {
  const [selectedTemplate, setSelectedTemplate] = React.useState<PrescriptionTemplate | null>(null);

  return (
    <div className="space-y-4">
      <div id="erx-form-anchor" />
      <Card>
        <CardHeader>
          <CardTitle>E-Reçete (v1)</CardTitle>
          <CardDescription>
            Bu sekmede reçete kaydedebilir ve elektronik gönderimi (mock) başlatabilirsiniz.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {message && (
            <Alert variant={message.type === "success" ? "default" : "destructive"}>
              {message.type === "success" ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <AlertTitle>{message.type === "success" ? "Başarılı" : "Hata"}</AlertTitle>
              <AlertDescription>{message.text}</AlertDescription>
            </Alert>
          )}
          <NewPrescriptionForm region={region} onSubmit={onCreatePrescription} template={selectedTemplate} />
          <PrescriptionTemplates region={region} onSelect={(tpl) => setSelectedTemplate(tpl)} />
          <div className="p-3 bg-muted/50 rounded-lg text-sm text-gray-700">
            <strong>Not:</strong> Kaydettiğiniz reçeteler “Reçeteler” sekmesinde listelenir. “E-Reçete Gönder”
            mock olarak %90 başarı / %10 hata ile çalışır ve aşağıdaki kuyrukta görünür.
          </div>
          <div className="flex justify-end">
            <Button
              onClick={() => {
                const latest = prescriptions[0];
                if (!latest) {
                  alert("Önce bir reçete kaydedin.");
                  return;
                }
                onSendERx(latest);
              }}
            >
              E-Reçete Gönder (mock)
            </Button>
          </div>
        </CardContent>
      </Card>

      <ErxPendingQueue items={erxRecords} prescriptions={prescriptions} onRetry={onRetryERx} />
    </div>
  );
}


