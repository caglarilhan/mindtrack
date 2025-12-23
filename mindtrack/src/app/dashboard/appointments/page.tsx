"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface AppointmentItem { id: string; patientId: string; startAt: string; link?: string; status?: string; type?: string; location?: string }

export default function AppointmentsListPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<AppointmentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Demo verisi; gerçek uygulamada Supabase'den çekilir
    setItems([
      { id: 'appt-1', patientId: 'test-p-1', startAt: new Date().toISOString(), link: '', status: 'scheduled', type: 'consult', location: 'Telehealth' },
      { id: 'appt-2', patientId: 'test-p-2', startAt: new Date(Date.now()+3600_000).toISOString(), link: '', status: 'scheduled', type: 'followup', location: 'Office' }
    ]);
    setLoading(false);
  }, []);

  const filtered = items.filter(a => a.id.toLowerCase().includes(query.toLowerCase()) || a.patientId.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="max-w-5xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Randevular</CardTitle>
          <CardDescription>Arama yapın ve ayarlara hızlıca gidin</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Randevu veya hasta ID ara" />
          </div>
          {loading ? (
            <div>Yükleniyor...</div>
          ) : (
            <div className="space-y-2">
              {filtered.map(a => (
                <div key={a.id} className="flex items-center justify-between border rounded p-3">
                  <div>
                    <div className="font-medium">Randevu: {a.id}</div>
                    <div className="text-sm text-gray-600">Hasta: {a.patientId}</div>
                    <div className="text-xs text-gray-500">Başlangıç: {new Date(a.startAt).toLocaleString()}</div>
                    <div className="text-xs text-gray-500">Durum: {a.status} · Tür: {a.type} · Lokasyon: {a.location}</div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => router.push(`/dashboard/appointments/${a.id}/settings`)}>Ayarlar</Button>
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


