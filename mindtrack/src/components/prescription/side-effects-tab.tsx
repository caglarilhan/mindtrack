"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SideEffectEntry, mockSideEffects } from "@/lib/prescription/side-effects";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { mockPatients } from "@/lib/prescription/mock-patients";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle } from "lucide-react";

interface Props {
  sideEffects: SideEffectEntry[];
}

const sevColor: Record<SideEffectEntry["severity"], string> = {
  mild: "bg-green-100 text-green-800",
  moderate: "bg-yellow-100 text-yellow-800",
  severe: "bg-red-100 text-red-800",
};

export function SideEffectsTab({ sideEffects }: Props) {
  const [list, setList] = React.useState<SideEffectEntry[]>(sideEffects);
  const [drugName, setDrugName] = React.useState("");
  const [effect, setEffect] = React.useState("");
  const [severity, setSeverity] = React.useState<SideEffectEntry["severity"]>("mild");
  const [patientId, setPatientId] = React.useState("");
  const [filterSeverity, setFilterSeverity] = React.useState<SideEffectEntry["severity"] | "all">("all");
  const [search, setSearch] = React.useState("");

  const criticalList = React.useMemo(
    () => list.filter((s) => s.severity === "severe"),
    [list]
  );

  const handleAdd = () => {
    if (!drugName || !effect || !patientId) {
      alert("Hasta, ilaç ve yan etki adı gerekli");
      return;
    }
    const row: SideEffectEntry = {
      id: `SE-${Date.now()}`,
      patientId,
      drugName,
      sideEffectName: effect,
      severity,
      firstObserved: new Date().toISOString(),
      lastUpdated: new Date().toISOString(),
    };
    setList((prev) => [row, ...prev]);
    setDrugName("");
    setEffect("");
    setPatientId("");
    setSeverity("mild");
  };

  const filtered = list.filter((s) => {
    const matchSeverity = filterSeverity === "all" ? true : s.severity === filterSeverity;
    const text = `${s.drugName} ${s.sideEffectName}`.toLowerCase();
    const matchSearch = text.includes(search.toLowerCase());
    return matchSeverity && matchSearch;
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Yeni Yan Etki Ekle</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <Select value={patientId} onValueChange={setPatientId}>
            <SelectTrigger>
              <SelectValue placeholder="Hasta seçin" />
            </SelectTrigger>
            <SelectContent>
              {mockPatients.map((p) => (
                <SelectItem key={p.id} value={p.id}>
                  {p.name} ({p.id})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input placeholder="İlaç" value={drugName} onChange={(e) => setDrugName(e.target.value)} />
          <Input placeholder="Yan etki" value={effect} onChange={(e) => setEffect(e.target.value)} />
          <Select value={severity} onValueChange={(v) => setSeverity(v as any)}>
            <SelectTrigger>
              <SelectValue placeholder="Şiddet" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mild">Hafif</SelectItem>
              <SelectItem value="moderate">Orta</SelectItem>
              <SelectItem value="severe">Şiddetli</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleAdd}>Ekle</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-3">
            <CardTitle>Yan Etki Listesi</CardTitle>
            <div className="flex flex-wrap gap-2">
              <Input
                placeholder="İlaç / yan etki ara..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-9 w-48"
              />
              <Select value={filterSeverity} onValueChange={(v) => setFilterSeverity(v as any)}>
                <SelectTrigger className="h-9 w-32">
                  <SelectValue placeholder="Şiddet" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tümü</SelectItem>
                  <SelectItem value="mild">Hafif</SelectItem>
                  <SelectItem value="moderate">Orta</SelectItem>
                  <SelectItem value="severe">Şiddetli</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {criticalList.length > 0 && (
            <Alert variant="destructive" className="mb-3">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Kritik / Şiddetli yan etkiler</AlertTitle>
              <AlertDescription>
                {criticalList.length} kayıt:{" "}
                {criticalList
                  .map((s) => `${mockPatients.find((p) => p.id === s.patientId)?.name || s.patientId} - ${s.drugName}`)
                  .join(", ")}
              </AlertDescription>
            </Alert>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Hasta</TableHead>
                <TableHead>İlaç</TableHead>
                <TableHead>Yan Etki</TableHead>
                <TableHead>Şiddet</TableHead>
                <TableHead>İlk</TableHead>
                <TableHead>Son</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((s) => (
                <TableRow key={s.id}>
                <TableCell>
                  {mockPatients.find((p) => p.id === s.patientId)?.name || s.patientId}
                </TableCell>
                  <TableCell>{s.drugName}</TableCell>
                  <TableCell>{s.sideEffectName}</TableCell>
                  <TableCell>
                    <Badge className={sevColor[s.severity]}>{s.severity}</Badge>
                  </TableCell>
                  <TableCell>{new Date(s.firstObserved).toLocaleDateString("tr-TR")}</TableCell>
                  <TableCell>{new Date(s.lastUpdated).toLocaleDateString("tr-TR")}</TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500 py-6">
                    Kayıt yok
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}


