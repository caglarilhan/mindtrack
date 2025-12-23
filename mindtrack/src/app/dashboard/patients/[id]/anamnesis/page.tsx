"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

export default function PatientAnamnesisPage() {
  const params = useParams<{ id: string }>();
  const patientId = params?.id as string;
  const [loading, setLoading] = useState(true);
  const [maskedPreview, setMaskedPreview] = useState<string>("");
  const [text, setText] = useState<string>("");
  const [passphrase, setPassphrase] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [mode, setMode] = useState<'record' | 'patient' | 'clinic'>('record');

  useEffect(() => {
    if (!patientId) return;
    (async () => {
      try {
        const res = await fetch(`/api/patients/${patientId}/anamnesis`);
        const data = await res.json();
        if (res.ok && data?.exists) setMaskedPreview(data.maskedPreview || "");
        if (res.ok && data?.mode) setMode(data.mode);
      } finally {
        setLoading(false);
      }
    })();
  }, [patientId]);

  const handleEncryptSave = async () => {
    setStatus("Saving...");
    try {
      const res = await fetch(`/api/patients/${patientId}/anamnesis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, passphrase, mode })
      });
      const data = await res.json();
      if (!res.ok || !data?.success) throw new Error(data?.error || 'Failed');
      setStatus("Saved ✅");
    } catch (e: any) {
      setStatus("Failed ❌");
      alert(e?.message || 'Failed to save');
    }
  };

  const handleDecrypt = async (asAdmin = false) => {
    setStatus("Decrypting...");
    try {
      const res = await fetch(`/api/patients/${patientId}/anamnesis`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asAdmin, passphrase: asAdmin ? undefined : passphrase, mode })
      });
      const data = await res.json();
      if (!res.ok || !data?.success) throw new Error(data?.error || 'Failed');
      setText(data.text || "");
      setStatus("Decrypted ✅");
    } catch (e: any) {
      setStatus("Failed ❌");
      alert(e?.message || 'Failed to decrypt');
    }
  };

  if (loading) return <div className="p-6">Yükleniyor...</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Hasta Anamnezi (Şifreli)</CardTitle>
          <CardDescription>Şifrele, güvenle kaydet; kullanıcı parolası veya admin anahtarı ile çöz</CardDescription>
        </CardHeader>
        <CardContent>
          {maskedPreview && (
            <div className="mb-4 text-xs text-gray-500">Stored (masked): {maskedPreview}</div>
          )}
          <div className="grid grid-cols-1 gap-4">
            <div>
              <Label className="mb-2 block">Şifreleme Modu</Label>
              <Select value={mode} onValueChange={(v) => setMode(v as any)}>
                <SelectTrigger><SelectValue placeholder="Mod seçin" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="record">Yalnızca bu kayıt</SelectItem>
                  <SelectItem value="patient">Hastanın tüm kayıtları</SelectItem>
                  <SelectItem value="clinic">Klinik genel varsayılan</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="mb-2 block">Parola</Label>
              <Input type="password" value={passphrase} onChange={(e) => setPassphrase(e.target.value)} placeholder="Parola girin" />
            </div>
            <div>
              <Label className="mb-2 block">Anamnez Metni</Label>
              <textarea className="w-full border rounded p-3 min-h-[180px]" value={text} onChange={(e) => setText(e.target.value)} placeholder="Anamnez girin..." />
            </div>
            <div className="flex items-center gap-3">
              <Button onClick={handleEncryptSave}>Şifrele ve Kaydet</Button>
              <Button variant="outline" onClick={() => handleDecrypt(false)}>Çöz (Kullanıcı)</Button>
              <Button variant="outline" onClick={() => handleDecrypt(true)}>Çöz (Admin)</Button>
              {status && <span className="text-sm text-gray-600">{status}</span>}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


