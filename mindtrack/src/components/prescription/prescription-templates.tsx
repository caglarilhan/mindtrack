"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PrescriptionTemplate, getTemplates, addTemplate, deleteTemplate, updateTemplate } from "@/lib/prescription/templates";
import { RegionId } from "@/lib/prescription/types";
import { Badge } from "@/components/ui/badge";

interface Props {
  region: RegionId;
  onSelect: (tpl: PrescriptionTemplate) => void;
}

export function PrescriptionTemplates({ region, onSelect }: Props) {
  const [templates, setTemplates] = React.useState<PrescriptionTemplate[]>(() => getTemplates(region));
  const [name, setName] = React.useState("");
  const [notes, setNotes] = React.useState("");
  const [medications, setMedications] = React.useState<
    { name: string; dose?: string; freq: string }[]
  >([{ name: "", dose: "", freq: "qd" }]);
  const [editingId, setEditingId] = React.useState<string | null>(null);

  const handleSave = () => {
    if (!name || medications.some((m) => !m.name)) {
      alert("Şablon adı ve tüm ilaç adları gerekli");
      return;
    }
    const medsPayload = medications.map((m) => ({
      name: m.name,
      doseMg: m.dose ? Number(m.dose) : undefined,
      frequency: m.freq,
    }));

    if (editingId) {
      updateTemplate(editingId, { name, region, medications: medsPayload, notes });
    } else {
      const created = addTemplate({ name, region, medications: medsPayload, notes });
      onSelect(created);
    }

    setTemplates(getTemplates(region));
    setName("");
    setMedications([{ name: "", dose: "", freq: "qd" }]);
    setNotes("");
    setEditingId(null);
  };

  const handleDelete = (id: string) => {
    deleteTemplate(id);
    setTemplates(getTemplates(region));
  };

  const handleEdit = (tpl: PrescriptionTemplate) => {
    setEditingId(tpl.id);
    setName(tpl.name);
    setNotes(tpl.notes || "");
    setMedications(
      tpl.medications.map((m) => ({
        name: m.name,
        dose: m.doseMg ? String(m.doseMg) : "",
        freq: m.frequency || "qd",
      }))
    );
  };

  const updateMed = (idx: number, field: "name" | "dose" | "freq", value: string) => {
    setMedications((prev) => prev.map((m, i) => (i === idx ? { ...m, [field]: value } : m)));
  };

  const addMedRow = () => {
    setMedications((prev) => [...prev, { name: "", dose: "", freq: "qd" }]);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reçete Şablonları</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Input placeholder="Şablon adı" value={name} onChange={(e) => setName(e.target.value)} />
          {medications.map((m, idx) => (
            <div key={idx} className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Input
                placeholder="İlaç"
                value={m.name}
                onChange={(e) => updateMed(idx, "name", e.target.value)}
              />
              <Input
                placeholder="Doz (mg)"
                value={m.dose}
                onChange={(e) => updateMed(idx, "dose", e.target.value)}
              />
              <Select value={m.freq} onValueChange={(v) => updateMed(idx, "freq", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Sıklık" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="qd">Günde 1</SelectItem>
                  <SelectItem value="bid">Günde 2</SelectItem>
                  <SelectItem value="tid">Günde 3</SelectItem>
                  <SelectItem value="qhs">Gece</SelectItem>
                  <SelectItem value="prn">PRN</SelectItem>
                </SelectContent>
              </Select>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={addMedRow}>
            + İlaç satırı
          </Button>
        </div>
        <Textarea placeholder="Notlar" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
        <div className="flex justify-end">
          <Button onClick={handleSave}>{editingId ? "Şablonu Güncelle" : "Şablon Ekle"}</Button>
        </div>

        <div className="space-y-2">
          {templates.map((tpl) => (
            <div
              key={tpl.id}
              className="p-3 border rounded-lg flex items-start justify-between gap-3 bg-muted/30 hover:bg-muted cursor-pointer"
              onClick={() => onSelect(tpl)}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{tpl.name}</span>
                  <Badge variant="outline">{tpl.region}</Badge>
                </div>
                <div className="text-sm text-gray-700">
                  {tpl.medications.map((m, idx) => (
                    <span key={idx} className="mr-2">
                      {m.name}
                      {m.doseMg ? ` ${m.doseMg}mg` : ""} {m.frequency ? `(${m.frequency})` : ""}
                    </span>
                  ))}
                </div>
                {tpl.notes && <div className="text-xs text-gray-600">{tpl.notes}</div>}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEdit(tpl);
                  }}
                >
                  Düzenle
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(tpl.id);
                  }}
                >
                  Sil
                </Button>
              </div>
            </div>
          ))}
          {templates.length === 0 && (
            <div className="text-sm text-gray-500">Bu bölge için şablon yok.</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

