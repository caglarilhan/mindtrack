"use client";

import * as React from "react";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  Shield, 
  Mail, 
  Phone, 
  Calendar,
  MapPin,
  AlertCircle,
  CheckCircle,
  Info
} from "lucide-react";

interface PatientCreateFormProps {
  clinicId?: string;
  therapistId?: string;
  onSuccess?: (patientId: string) => void;
  onCancel?: () => void;
}

export function PatientCreateForm({ clinicId, therapistId, onSuccess, onCancel }: PatientCreateFormProps) {
  const [mode, setMode] = useState<'full' | 'lite'>('full');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Full mode fields
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [address, setAddress] = useState('');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [insuranceInfo, setInsuranceInfo] = useState('');
  
  // Lite mode fields
  const [pseudoName, setPseudoName] = useState('');
  const [ageRange, setAgeRange] = useState('');
  const [gender, setGender] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload: any = {
        mode,
        clinicId,
        therapistId
      };

      if (mode === 'full') {
        payload.firstName = firstName;
        payload.lastName = lastName;
        payload.email = email;
        payload.phone = phone || undefined;
        payload.dateOfBirth = dateOfBirth || undefined;
        payload.address = address || undefined;
        payload.emergencyContact = emergencyContact || undefined;
        if (insuranceInfo) {
          try {
            payload.insuranceInfo = JSON.parse(insuranceInfo);
          } catch {
            payload.insuranceInfo = { notes: insuranceInfo };
          }
        }
      } else {
        payload.pseudoName = pseudoName || undefined;
        payload.ageRange = ageRange || undefined;
        payload.gender = gender || undefined;
        payload.encryptedLocalNotes = true;
      }

      const res = await fetch('/api/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Danışan oluşturulamadı');
      }

      const data = await res.json();
      if (onSuccess) {
        onSuccess(data.patient.id);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Yeni Danışan Ekle</CardTitle>
        <CardDescription>
          Danışan kayıt tipini seçin: Full Client Profile (HIPAA uyumlu) veya Lite/Anonymous Profile (GDPR-friendly)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Mode Selection */}
          <div className="space-y-4">
            <Label className="text-base font-semibold">Kayıt Tipi</Label>
            <div className="space-y-3">
              <div 
                className={`flex items-start space-x-3 space-y-0 rounded-md border p-4 cursor-pointer transition-all ${
                  mode === 'full' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setMode('full')}
              >
                <input
                  type="radio"
                  id="full"
                  name="mode"
                  value="full"
                  checked={mode === 'full'}
                  onChange={() => setMode('full')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <Label htmlFor="full" className="font-medium cursor-pointer">
                    Full Client Profile (Önerilen / HIPAA Uyumlu)
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    Tam kimlik bilgileri, iletişim bilgileri ve tıbbi geçmiş. ABD klinikleri için önerilir.
                  </p>
                </div>
                <Badge variant="default">Önerilen</Badge>
              </div>
              <div 
                className={`flex items-start space-x-3 space-y-0 rounded-md border p-4 cursor-pointer transition-all ${
                  mode === 'lite' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setMode('lite')}
              >
                <input
                  type="radio"
                  id="lite"
                  name="mode"
                  value="lite"
                  checked={mode === 'lite'}
                  onChange={() => setMode('lite')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <Label htmlFor="lite" className="font-medium cursor-pointer">
                    Lite / Anonymous Client Profile (GDPR-Friendly)
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    Takma isim, yaş aralığı ve şifreli yerel notlar. Avrupa ve gizlilik odaklı kullanım için.
                  </p>
                </div>
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
                  Gizlilik Odaklı
                </Badge>
              </div>
            </div>
          </div>

          {/* Full Mode Fields */}
          {mode === 'full' && (
            <div className="space-y-4 border-t pt-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Info className="h-4 w-4" />
                <span>Full mode için aşağıdaki alanlar zorunludur</span>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">Ad *</Label>
                  <Input
                    id="firstName"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                    placeholder="John"
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Soyad *</Label>
                  <Input
                    id="lastName"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="email">E-posta *</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="john@example.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Telefon</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+1 555-1234"
                  />
                </div>
                <div>
                  <Label htmlFor="dateOfBirth">Doğum Tarihi</Label>
                  <Input
                    id="dateOfBirth"
                    type="date"
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="address">Adres</Label>
                <Input
                  id="address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="123 Main St, City, State ZIP"
                />
              </div>

              <div>
                <Label htmlFor="emergencyContact">Acil İletişim Kişisi</Label>
                <Input
                  id="emergencyContact"
                  value={emergencyContact}
                  onChange={(e) => setEmergencyContact(e.target.value)}
                  placeholder="Jane Doe - +1 555-5678"
                />
              </div>

              <div>
                <Label htmlFor="insuranceInfo">Sigorta Bilgileri (JSON veya metin)</Label>
                <Textarea
                  id="insuranceInfo"
                  value={insuranceInfo}
                  onChange={(e) => setInsuranceInfo(e.target.value)}
                  placeholder='{"provider": "Blue Cross", "policyNumber": "123456"}'
                  rows={3}
                />
              </div>
            </div>
          )}

          {/* Lite Mode Fields */}
          {mode === 'lite' && (
            <div className="space-y-4 border-t pt-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                <Shield className="h-4 w-4 text-green-600" />
                <span>Lite mode: Kişisel tanımlayıcı bilgiler saklanmaz</span>
              </div>

              <div>
                <Label htmlFor="pseudoName">Takma İsim (Opsiyonel)</Label>
                <Input
                  id="pseudoName"
                  value={pseudoName}
                  onChange={(e) => setPseudoName(e.target.value)}
                  placeholder="Client #14 (otomatik üretilebilir)"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Boş bırakılırsa otomatik olarak "Client #[numara]" formatında oluşturulur
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="ageRange">Yaş Aralığı (Opsiyonel)</Label>
                  <select
                    id="ageRange"
                    value={ageRange}
                    onChange={(e) => setAgeRange(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="">Seçiniz...</option>
                    <option value="18-25">18-25</option>
                    <option value="26-35">26-35</option>
                    <option value="36-45">36-45</option>
                    <option value="46-55">46-55</option>
                    <option value="56-65">56-65</option>
                    <option value="65+">65+</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="gender">Cinsiyet (Opsiyonel)</Label>
                  <select
                    id="gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="">Seçiniz...</option>
                    <option value="male">Erkek</option>
                    <option value="female">Kadın</option>
                    <option value="other">Diğer</option>
                    <option value="prefer_not_to_say">Belirtmek istemiyorum</option>
                  </select>
                </div>
              </div>

              <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-green-900">Gizlilik Garantisi</p>
                    <p className="text-green-700 mt-1">
                      Lite modda isim, e-posta, telefon gibi kişisel tanımlayıcı bilgiler saklanmaz. 
                      Notlar sadece terapistin cihazında şifreli olarak tutulur.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-600">
              {error}
            </div>
          )}

          <div className="flex gap-2 justify-end">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                İptal
              </Button>
            )}
            <Button type="submit" disabled={loading}>
              {loading ? 'Oluşturuluyor...' : 'Danışan Oluştur'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

