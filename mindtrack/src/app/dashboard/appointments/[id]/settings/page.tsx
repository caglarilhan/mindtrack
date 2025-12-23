"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type Provider = 'custom' | 'google_meet' | 'zoom';

export default function AppointmentSettingsPage() {
  const params = useParams<{ id: string }>();
  const appointmentId = params?.id as string;
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [telehealthProvider, setTelehealthProvider] = useState<Provider>('custom');
  const [telehealthLink, setTelehealthLink] = useState('');
  const [autoReminderMinutes, setAutoReminderMinutes] = useState<number>(60);

  useEffect(() => {
    if (!appointmentId) return;
    (async () => {
      try {
        const res = await fetch(`/api/appointments/${appointmentId}/settings`);
        const data = await res.json();
        if (res.ok && data?.settings) {
          const s = data.settings;
          setTelehealthProvider(s.telehealthProvider || 'custom');
          setTelehealthLink(s.telehealthLink || '');
          setAutoReminderMinutes(s.autoReminderMinutes ?? 60);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [appointmentId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`/api/appointments/${appointmentId}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: { telehealthProvider, telehealthLink, autoReminderMinutes } })
      });
      const data = await res.json();
      if (!res.ok || !data?.success) throw new Error(data?.error || 'Failed');
      alert('Saved ✅');
    } catch (e: any) {
      alert(e?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6">Yükleniyor...</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Randevu Ayarları</CardTitle>
          <CardDescription>Tele‑sağlık sağlayıcı/bağlantı ve otomatik hatırlatma</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="mb-2 block">Tele‑sağlık Sağlayıcı</Label>
              <Select value={telehealthProvider} onValueChange={(v) => setTelehealthProvider(v as Provider)}>
                <SelectTrigger><SelectValue placeholder="Select provider" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="custom">Custom</SelectItem>
                  <SelectItem value="google_meet">Google Meet</SelectItem>
                  <SelectItem value="zoom">Zoom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">Tele‑sağlık Bağlantısı</Label>
              <Input value={telehealthLink} onChange={(e) => setTelehealthLink(e.target.value)} placeholder="https://..." />
            </div>
            <div>
              <Label className="mb-2 block">Otomatik Hatırlatma (dakika önce)</Label>
              <Input type="number" value={autoReminderMinutes} onChange={(e) => setAutoReminderMinutes(parseInt(e.target.value || '0', 10))} />
            </div>
          </div>
          <div className="mt-6">
            <Button onClick={handleSave} disabled={saving}>{saving ? 'Kaydediliyor...' : 'Ayarları Kaydet'}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


