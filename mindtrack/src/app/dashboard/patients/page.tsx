"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface PatientItem { id: string; name: string; email?: string }

export default function PatientsListPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [patients, setPatients] = useState<PatientItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Demo verisi; gerçek uygulamada Supabase'den çekilir
    setPatients([
      { id: 'test-p-1', name: 'Hasta 1', email: 'h1@example.com' },
      { id: 'test-p-2', name: 'Hasta 2', email: 'h2@example.com' }
    ]);
    setLoading(false);
  }, []);

  const filtered = patients.filter(p => p.name.toLowerCase().includes(query.toLowerCase()) || (p.email||'').toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="max-w-5xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Hastalar</CardTitle>
          <CardDescription>Arama yapın ve hızlıca tercihler/ anamneze gidin</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="İsim veya e‑posta ara" />
          </div>
          {loading ? (
            <div>Yükleniyor...</div>
          ) : (
            <div className="space-y-2">
              {filtered.map(p => (
                <div key={p.id} className="flex items-center justify-between border rounded p-3">
                  <div>
                    <div className="font-medium">{p.name}</div>
                    <div className="text-sm text-gray-600">{p.email}</div>
                    <div className="text-xs text-gray-500">ID: {p.id}</div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => router.push(`/dashboard/patients/${p.id}/preferences`)}>Tercihler</Button>
                    <Button variant="outline" onClick={() => router.push(`/dashboard/patients/${p.id}/anamnesis`)}>Anamnez</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


