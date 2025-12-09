"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { RegionId, Prescription } from "@/lib/prescription/types";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { checkInteractions, checkDose, checkAllergy } from "@/lib/prescription/safety-engine";
import { mockPatients } from "@/lib/prescription/mock-patients";
import { PrescriptionTemplate } from "@/lib/prescription/templates";
import { Badge } from "@/components/ui/badge";

interface Props {
  region: RegionId;
  onSubmit: (draft: Prescription) => void;
  template?: PrescriptionTemplate | null;
}

export function NewPrescriptionForm({ region, onSubmit, template }: Props) {
  const [patientName, setPatientName] = React.useState("");
  const [patientId, setPatientId] = React.useState("");
  const [medications, setMedications] = React.useState<{ name: string; dose: string; freq: string }[]>([
    { name: "", dose: "", freq: "qd" },
  ]);
  React.useEffect(() => {
    if (template) {
      setMedications(
        template.medications.length > 0
          ? template.medications.map((m) => ({
              name: m.name,
              dose: m.doseMg ? String(m.doseMg) : "",
              freq: m.frequency || "qd",
            }))
          : [{ name: "", dose: "", freq: "qd" }]
      );
      setNotes(template.notes || "");
    }
  }, [template]);
  const [quantity, setQuantity] = React.useState(30);
  const [notes, setNotes] = React.useState("");

  const [doseAlert, setDoseAlert] = React.useState<string | null>(null);
  const [interactionAlert, setInteractionAlert] = React.useState<string | null>(null);
  const [allergyAlert, setAllergyAlert] = React.useState<string | null>(null);

  const selectedPatient = React.useMemo(
    () => mockPatients.find((p) => p.id === patientId),
    [patientId]
  );

  React.useEffect(() => {
    const firstMed = medications[0];
    if (firstMed?.name) {
      const d = checkDose(firstMed.name, firstMed.dose ? Number(firstMed.dose) : undefined);
      setDoseAlert(d.level !== "ok" ? d.message : null);
    } else {
      setDoseAlert(null);
    }

    if (firstMed?.name && selectedPatient) {
      const a = checkAllergy(firstMed.name, selectedPatient.allergies);
      setAllergyAlert(a.hasAllergy ? a.message : null);
    } else {
      setAllergyAlert(null);
    }

    const namedMeds = medications.filter((m) => m.name);
    if (namedMeds.length >= 2) {
      const res = checkInteractions(namedMeds.map((m) => m.name));
      setInteractionAlert(res.length > 0 ? res[0].message : null);
    } else {
      setInteractionAlert(null);
    }
  }, [medications, selectedPatient]);

  const handleSubmit = () => {
    if (!patientName || !medications[0]?.name || quantity <= 0) {
      alert("Hasta adı, en az bir ilaç ve miktar zorunlu.");
      return;
    }

    const firstMed = medications[0];
    const doseResult = checkDose(firstMed.name, firstMed.dose ? Number(firstMed.dose) : undefined);
    if (doseResult.level === "danger") {
      if (!confirm(`Doz uyarısı: ${doseResult.message}\nYine de devam edilsin mi?`)) return;
    }

    if (selectedPatient) {
      const allergyResult = checkAllergy(firstMed.name, selectedPatient.allergies);
      if (allergyResult.hasAllergy) {
        if (!confirm(`Alerji uyarısı: ${allergyResult.message}\nYine de devam edilsin mi?`)) return;
      }
    }

    const draft: Prescription = {
      id: `RX-${Date.now()}`,
      patientName,
      patientId: patientId || `P-${Date.now()}`,
      region,
      medications: medications
        .filter((m) => m.name)
        .map((m) => ({
          name: m.name,
          doseMg: m.dose ? Number(m.dose) : undefined,
          frequency: m.freq,
        })),
      status: "active",
      risk: "medium",
      createdAt: new Date().toISOString(),
      notes,
    };
    onSubmit(draft);
    setPatientName("");
    setPatientId("");
    setMedications([{ name: "", dose: "", freq: "qd" }]);
    setQuantity(30);
    setNotes("");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Yeni Reçete</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Hasta *</Label>
            <select
              value={patientId}
              onChange={(e) => {
                const pid = e.target.value;
                setPatientId(pid);
                const p = mockPatients.find((x) => x.id === pid);
                setPatientName(p?.name || "");
              }}
              className="w-full border rounded-md h-10 px-2"
            >
              <option value="">Hasta seçin</option>
              {mockPatients.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.id})
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Hasta ID (manuel)</Label>
            <Input value={patientId} onChange={(e) => setPatientId(e.target.value)} placeholder="Opsiyonel" />
          </div>
        </div>
        <div className="space-y-3">
          {medications.map((m, idx) => (
            <div key={idx} className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>İlaç *</Label>
                <Input
                  value={m.name}
                  onChange={(e) =>
                    setMedications((prev) => prev.map((row, i) => (i === idx ? { ...row, name: e.target.value } : row)))
                  }
                  placeholder="Sertraline"
                />
              </div>
              <div>
                <Label>Doz (mg)</Label>
                <Input
                  value={m.dose}
                  onChange={(e) =>
                    setMedications((prev) => prev.map((row, i) => (i === idx ? { ...row, dose: e.target.value } : row)))
                  }
                  placeholder="50"
                />
              </div>
              <div>
                <Label>Sıklık</Label>
                <select
                  value={m.freq}
                  onChange={(e) =>
                    setMedications((prev) => prev.map((row, i) => (i === idx ? { ...row, freq: e.target.value } : row)))
                  }
                  className="w-full border rounded-md h-10 px-2"
                >
                  <option value="qd">Günde 1</option>
                  <option value="bid">Günde 2</option>
                  <option value="tid">Günde 3</option>
                  <option value="qhs">Gece</option>
                  <option value="prn">İhtiyaç halinde</option>
                </select>
              </div>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={() => setMedications((prev) => [...prev, { name: "", dose: "", freq: "qd" }])}>
            + İlaç Ekle
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Miktar *</Label>
            <Input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              min={1}
              placeholder="30"
            />
          </div>
          <div>
            <Label>Notlar</Label>
            <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Kısa not" />
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {doseAlert && (
            <Badge className="bg-yellow-100 text-yellow-800 border border-yellow-200">Doz: {doseAlert}</Badge>
          )}
          {allergyAlert && (
            <Badge className="bg-red-100 text-red-800 border border-red-200">Alerji: {allergyAlert}</Badge>
          )}
          {interactionAlert && (
            <Badge className="bg-orange-100 text-orange-800 border border-orange-200">Etkileşim: {interactionAlert}</Badge>
          )}
          {!doseAlert && !allergyAlert && !interactionAlert && (
            <Badge variant="outline">Güvenlik uyarısı bulunmuyor</Badge>
          )}
        </div>

        {doseAlert && (
          <Alert variant="warning">
            <AlertTitle>Doz Uyarısı</AlertTitle>
            <AlertDescription>{doseAlert}</AlertDescription>
          </Alert>
        )}
        {allergyAlert && (
          <Alert variant="destructive">
            <AlertTitle>Alerji Uyarısı</AlertTitle>
            <AlertDescription>{allergyAlert}</AlertDescription>
          </Alert>
        )}
        {interactionAlert && (
          <Alert variant="destructive">
            <AlertTitle>Etkileşim Uyarısı</AlertTitle>
            <AlertDescription>{interactionAlert}</AlertDescription>
          </Alert>
        )}

        <div className="flex justify-end">
          <Button onClick={handleSubmit}>Kaydet</Button>
        </div>
      </CardContent>
    </Card>
  );
}


