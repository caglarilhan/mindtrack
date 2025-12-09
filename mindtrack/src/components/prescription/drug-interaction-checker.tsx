"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { DrugInteractionResult, checkInteractions } from "@/lib/prescription/safety-engine";
import { Badge } from "@/components/ui/badge";

interface Props {
  medications: { name: string; doseMg?: number }[];
}

export function DrugInteractionChecker({ medications }: Props) {
  const [results, setResults] = React.useState<DrugInteractionResult[]>([]);

  const riskColor: Record<DrugInteractionResult["risk"], string> = {
    major: "bg-red-100 text-red-800 border-red-200",
    moderate: "bg-orange-100 text-orange-800 border-orange-200",
    minor: "bg-yellow-100 text-yellow-800 border-yellow-200",
    none: "bg-green-100 text-green-800 border-green-200",
  };

  const handleCheck = () => {
    const names = medications.map((m) => m.name);
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
        </div>
        <Button variant="outline" onClick={handleCheck}>
          Etkileşimleri Kontrol Et
        </Button>
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

