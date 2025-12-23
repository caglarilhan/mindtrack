"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type EmailProvider = 'sendgrid' | 'postmark' | 'ses' | 'brevo' | 'mailjet' | 'mailgun_eu';
type SmsProvider = 'twilio' | 'messagebird' | 'vonage' | 'sinch';
type DataRegion = 'us' | 'eu';

export default function CommunicationsSettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [emailProvider, setEmailProvider] = useState<EmailProvider>('sendgrid');
  const [smsProvider, setSmsProvider] = useState<SmsProvider>('twilio');
  const [dataRegion, setDataRegion] = useState<DataRegion>('us');
  const [defaultReminderOffsetMinutes, setDefaultReminderOffsetMinutes] = useState<number>(60);
  const [emailSubject, setEmailSubject] = useState('Telehealth Session Reminder');
  const [emailBody, setEmailBody] = useState('Your session is scheduled soon. Join using the link: {{link}}');
  const [smsBody, setSmsBody] = useState('Your session is scheduled soon. Join: {{link}}');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/api/settings/communications');
        const data = await res.json();
        if (res.ok && data?.settings) {
          const s = data.settings;
          setEmailProvider(s.emailProvider);
          setSmsProvider(s.smsProvider);
          setDataRegion(s.dataRegion);
          setDefaultReminderOffsetMinutes(s.defaultReminderOffsetMinutes);
          setEmailSubject(s.templates.emailSubject);
          setEmailBody(s.templates.emailBody);
          setSmsBody(s.templates.smsBody);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/settings/communications', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          settings: {
            emailProvider,
            smsProvider,
            dataRegion,
            defaultReminderOffsetMinutes,
            templates: { emailSubject, emailBody, smsBody }
          }
        })
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

  if (loading) {
    return <div className="p-6">Yükleniyor...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>İletişim Ayarları</CardTitle>
          <CardDescription>Sağlayıcı/bölge seçimi, şablonlar ve varsayılan hatırlatma</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="mb-2 block">E‑posta Sağlayıcısı</Label>
              <Select value={emailProvider} onValueChange={(v) => setEmailProvider(v as EmailProvider)}>
                <SelectTrigger><SelectValue placeholder="Select provider" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="sendgrid">SendGrid</SelectItem>
                  <SelectItem value="postmark">Postmark</SelectItem>
                  <SelectItem value="ses">AWS SES</SelectItem>
                  <SelectItem value="brevo">Brevo (EU)</SelectItem>
                  <SelectItem value="mailjet">Mailjet (EU)</SelectItem>
                  <SelectItem value="mailgun_eu">Mailgun (EU)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">SMS Sağlayıcısı</Label>
              <Select value={smsProvider} onValueChange={(v) => setSmsProvider(v as SmsProvider)}>
                <SelectTrigger><SelectValue placeholder="Select provider" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="twilio">Twilio</SelectItem>
                  <SelectItem value="messagebird">MessageBird (EU)</SelectItem>
                  <SelectItem value="vonage">Vonage</SelectItem>
                  <SelectItem value="sinch">Sinch</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">Veri Bölgesi</Label>
              <Select value={dataRegion} onValueChange={(v) => setDataRegion(v as DataRegion)}>
                <SelectTrigger><SelectValue placeholder="Select region" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="us">US</SelectItem>
                  <SelectItem value="eu">EU</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">Varsayılan Hatırlatma (dakika önce)</Label>
              <Input type="number" value={defaultReminderOffsetMinutes} onChange={(e) => setDefaultReminderOffsetMinutes(parseInt(e.target.value || '0', 10))} />
            </div>
            <div className="md:col-span-2">
              <Label className="mb-2 block">E‑posta Konusu</Label>
              <Input value={emailSubject} onChange={(e) => setEmailSubject(e.target.value)} />
            </div>
            <div className="md:col-span-2">
              <Label className="mb-2 block">E‑posta İçeriği</Label>
              <Input value={emailBody} onChange={(e) => setEmailBody(e.target.value)} />
            </div>
            <div className="md:col-span-2">
              <Label className="mb-2 block">SMS İçeriği</Label>
              <Input value={smsBody} onChange={(e) => setSmsBody(e.target.value)} />
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


