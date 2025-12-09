"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { DrugInteractionResult, checkInteractions } from "@/lib/prescription/safety-engine";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { X } from "lucide-react";

interface Props {
  medications: { name: string; doseMg?: number }[];
}

export function DrugInteractionChecker({ medications }: Props) {
  const [results, setResults] = React.useState<DrugInteractionResult[]>([]);
  const [inputA, setInputA] = React.useState("");
  const [inputB, setInputB] = React.useState("");
  const [manualMeds, setManualMeds] = React.useState<string[]>([]);

  const riskColor: Record<DrugInteractionResult["risk"], string> = {
    major: "bg-red-100 text-red-800 border-red-200",
    moderate: "bg-orange-100 text-orange-800 border-orange-200",
    minor: "bg-yellow-100 text-yellow-800 border-yellow-200",
    none: "bg-green-100 text-green-800 border-green-200",
  };

  const handleCheck = () => {
    const names = [...medications.map((m) => m.name), ...manualMeds];
    if (inputA) names.push(inputA);
    if (inputB) names.push(inputB);
    const res = checkInteractions(names);
    setResults(res);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>İlaç Etkileşimleri</CardTitle>
        <CardDescription>Seçili ilaçlar arasında olası etkileşimleri kontrol edin.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {medications.map((m, idx) => (
            <Badge key={idx} variant="secondary">
              {m.name}
            </Badge>
          ))}
          {medications.length === 0 && (
            <>
              <Badge variant="secondary">Sertraline</Badge>
              <Badge variant="secondary">Bupropion</Badge>
              <Badge variant="secondary">Alprazolam</Badge>
              <Badge variant="secondary">Tramadol</Badge>
            </>
          )}
          {manualMeds.map((m, idx) => (
            <Badge key={idx} variant="outline" className="flex items-center gap-1">
              {m}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => setManualMeds((prev) => prev.filter((_, i) => i !== idx))}
              />
            </Badge>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label>İlaç ekle (A)</Label>
            <Input value={inputA} onChange={(e) => setInputA(e.target.value)} placeholder="Örn: Sertraline" />
          </div>
          <div className="space-y-1">
            <Label>İlaç ekle (B)</Label>
            <Input value={inputB} onChange={(e) => setInputB(e.target.value)} placeholder="Örn: Tramadol" />
          </div>
        </div>
        <Button variant="outline" onClick={handleCheck}>
          Etkileşimleri Kontrol Et
        </Button>
        <div className="flex flex-wrap gap-2 text-xs text-gray-600">
          {inputA && (
            <Badge
              variant="outline"
              className="cursor-pointer"
              onClick={() => {
                setManualMeds((prev) => [...prev, inputA]);
                setInputA("");
              }}
            >
              A'yı ekle
            </Badge>
          )}
          {inputB && (
            <Badge
              variant="outline"
              className="cursor-pointer"
              onClick={() => {
                setManualMeds((prev) => [...prev, inputB]);
                setInputB("");
              }}
            >
              B'yi ekle
            </Badge>
          )}
        </div>
        {results.length === 0 && (
          <p className="text-sm text-gray-600">
            {medications.length === 0
              ? "Henüz ilaç eklenmedi. Etkileşim kontrolü için en az iki ilaç seçin."
              : "Etkileşim bulunamadı veya henüz kontrol etmediniz."}
          </p>
        )}
        {results.map((r, idx) => (
          <Alert
            key={idx}
            variant={r.risk === "major" ? "destructive" : r.risk === "moderate" ? "warning" : "default"}
            className="flex flex-col gap-1"
          >
            <div className="flex items-center gap-2">
              <AlertTitle className="flex-1">
                {r.drugA} + {r.drugB}
              </AlertTitle>
              <Badge className={riskColor[r.risk]}>{r.risk.toUpperCase()}</Badge>
            </div>
            <AlertDescription>{r.message}</AlertDescription>
          </Alert>
        ))}
      </CardContent>
    </Card>
  );
}

