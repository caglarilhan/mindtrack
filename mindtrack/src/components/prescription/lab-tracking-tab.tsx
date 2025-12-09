"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LabResult } from "@/lib/prescription/lab-types";
import { mockPatients } from "@/lib/prescription/mock-patients";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface Props {
  labResults: LabResult[];
}

const riskColor: Record<LabResult["riskLevel"], string> = {
  normal: "bg-green-100 text-green-800",
  borderline: "bg-yellow-100 text-yellow-800",
  critical: "bg-red-100 text-red-800",
};

export function LabTrackingTab({ labResults }: Props) {
  const [riskFilter, setRiskFilter] = React.useState<LabResult["riskLevel"] | "all">("all");
  const [search, setSearch] = React.useState("");
  const [sortDesc, setSortDesc] = React.useState(true);

  const filtered = labResults
    .filter((r) => {
      const matchRisk = riskFilter === "all" ? true : r.riskLevel === riskFilter;
      const text = `${r.patientId} ${r.testType}`.toLowerCase();
      const matchSearch = text.includes(search.toLowerCase());
      return matchRisk && matchSearch;
    })
    .sort((a, b) => {
      const diff = new Date(a.resultDate).getTime() - new Date(b.resultDate).getTime();
      return sortDesc ? diff * -1 : diff;
    });

  const criticalList = React.useMemo(
    () => filtered.filter((r) => r.riskLevel === "critical"),
    [filtered]
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <CardTitle>Lab Sonuçları</CardTitle>
          <div className="flex flex-wrap gap-2">
            <Input
              placeholder="Hasta / test ara..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-9 w-48"
            />
            <Select value={riskFilter} onValueChange={(v) => setRiskFilter(v as any)}>
              <SelectTrigger className="h-9 w-36">
                <SelectValue placeholder="Risk" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tümü</SelectItem>
                <SelectItem value="normal">Normal</SelectItem>
                <SelectItem value="borderline">Borderline</SelectItem>
                <SelectItem value="critical">Kritik</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {criticalList.length > 0 && (
          <Alert variant="destructive" className="mb-3">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Kritik lab sonuçları</AlertTitle>
            <AlertDescription>
              {criticalList.length} kayıt:{" "}
              {criticalList
                .map((r) => `${mockPatients.find((p) => p.id === r.patientId)?.name || r.patientId} - ${r.testType}`)
                .join(", ")}
            </AlertDescription>
          </Alert>
        )}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Hasta</TableHead>
              <TableHead>Test</TableHead>
              <TableHead>Değer</TableHead>
              <TableHead className="cursor-pointer select-none" onClick={() => setSortDesc((p) => !p)}>
                Tarih {sortDesc ? "↓" : "↑"}
              </TableHead>
              <TableHead>Risk</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((r) => (
              <TableRow key={r.id}>
                <TableCell>{mockPatients.find((p) => p.id === r.patientId)?.name || r.patientId}</TableCell>
                <TableCell>{r.testType}</TableCell>
                <TableCell>
                  {r.value} {r.unit} ({r.referenceRange})
                </TableCell>
                <TableCell>{new Date(r.resultDate).toLocaleDateString("tr-TR")}</TableCell>
                <TableCell>
                  <Badge className={riskColor[r.riskLevel]}>{r.riskLevel}</Badge>
                </TableCell>
              </TableRow>
            ))}
            {filtered.length === 0 && (
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


