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
          <p className="text-sm text-gray-600">Etkileşim bulunamadı veya henüz kontrol etmediniz.</p>
        )}
        {results.map((r, idx) => (
          <Alert key={idx} variant={r.risk === "major" ? "destructive" : "default"}>
            <AlertTitle>
              {r.drugA} + {r.drugB} → {r.risk.toUpperCase()}
            </AlertTitle>
            <AlertDescription>{r.message}</AlertDescription>
          </Alert>
        ))}
      </CardContent>
    </Card>
  );
}

