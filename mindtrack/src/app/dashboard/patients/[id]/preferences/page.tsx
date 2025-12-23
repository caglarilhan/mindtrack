"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type ContactPreference = 'email' | 'sms' | 'none';

export default function PatientCommunicationPreferencesPage() {
  const params = useParams<{ id: string }>();
  const patientId = params?.id as string;
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [timeZone, setTimeZone] = useState('Europe/Berlin');
  const [contactPreference, setContactPreference] = useState<ContactPreference>('email');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [consentMarketing, setConsentMarketing] = useState(false);
  const [consentReminders, setConsentReminders] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    (async () => {
      try {
        const res = await fetch(`/api/patients/${patientId}/preferences`);
        const data = await res.json();
        if (res.ok && data?.preferences) {
          const p = data.preferences;
          setPreferredLanguage(p.preferredLanguage || 'en');
          setTimeZone(p.timeZone || 'Europe/Berlin');
          setContactPreference(p.contactPreference || 'email');
          setEmail(p.email || '');
          setPhone(p.phone || '');
          setConsentMarketing(!!p.consentMarketing);
          setConsentReminders(p.consentReminders !== false);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [patientId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`/api/patients/${patientId}/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences: { preferredLanguage, timeZone, contactPreference, email, phone, consentMarketing, consentReminders } })
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
          <CardTitle>Hasta İletişim Tercihleri</CardTitle>
          <CardDescription>Dil, saat dilimi, iletişim tercihi ve izinler</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="mb-2 block">Tercih Edilen Dil</Label>
              <Select value={preferredLanguage} onValueChange={setPreferredLanguage}>
                <SelectTrigger><SelectValue placeholder="Select language" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="tr">Türkçe</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">Saat Dilimi</Label>
              <Input value={timeZone} onChange={(e) => setTimeZone(e.target.value)} placeholder="Europe/Berlin" />
            </div>
            <div>
              <Label className="mb-2 block">İletişim Tercihi</Label>
              <Select value={contactPreference} onValueChange={(v) => setContactPreference(v as ContactPreference)}>
                <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="sms">SMS</SelectItem>
                  <SelectItem value="none">None</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">E‑posta</Label>
              <Input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="patient@example.com" />
            </div>
            <div>
              <Label className="mb-2 block">Telefon</Label>
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+49..., +44..., +1..." />
            </div>
            <div className="md:col-span-2 text-sm text-gray-600">
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={consentReminders} onChange={(e) => setConsentReminders(e.target.checked)} />
                <span>Hatırlatmalara onay</span>
              </label>
              <label className="flex items-center gap-2 mt-2">
                <input type="checkbox" checked={consentMarketing} onChange={(e) => setConsentMarketing(e.target.checked)} />
                <span>Pazarlama onayı</span>
              </label>
            </div>
          </div>
          <div className="mt-6">
            <Button onClick={handleSave} disabled={saving}>{saving ? 'Kaydediliyor...' : 'Tercihleri Kaydet'}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


