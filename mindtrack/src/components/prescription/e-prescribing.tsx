"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  Send, 
  CheckCircle, 
  Clock, 
  XCircle, 
  AlertTriangle,
  Search,
  Shield,
  FileText,
  RefreshCw,
  MapPin,
  Phone,
  Mail
} from "lucide-react";
import { 
  type EPrescription,
  type EPrescriptionStatus,
  type Pharmacy,
  sendEPrescription,
  checkEPrescriptionStatus,
  searchPharmacies,
  createDigitalSignature,
  getEPrescriptionStatusColor,
  getEPrescriptionProvider
} from "@/lib/e-prescribing";
import { type PrescriptionRegion, regionConfigs } from "@/lib/prescription-region";

interface EPrescribingProps {
  region: PrescriptionRegion;
  prescriptionId?: string;
  patientId?: string;
  medications: Array<{
    medicationId: string;
    medicationName: string;
    dosage: string;
    quantity: number;
    refills: number;
    instructions: string;
  }>;
  onSent?: (ePrescription: EPrescription) => void;
}

export default function EPrescribing({
  region,
  prescriptionId,
  patientId,
  medications,
  onSent
}: EPrescribingProps) {
  const t = useTranslations("prescription");
  const regionConfig = regionConfigs[region];
  const [selectedPharmacy, setSelectedPharmacy] = React.useState<Pharmacy | null>(null);
  const [pharmacySearch, setPharmacySearch] = React.useState("");
  const [pharmacyResults, setPharmacyResults] = React.useState<Pharmacy[]>([]);
  const [isSearching, setIsSearching] = React.useState(false);
  const [isSending, setIsSending] = React.useState(false);
  const [ePrescription, setEPrescription] = React.useState<EPrescription | null>(null);
  const [digitalSignature, setDigitalSignature] = React.useState<any>(null);

  // Eczane ara
  const handleSearchPharmacy = async () => {
    if (!pharmacySearch.trim()) return;

    setIsSearching(true);
    try {
      const results = await searchPharmacies(pharmacySearch, region);
      setPharmacyResults(results);
    } catch (error) {
      console.error('Eczane arama hatası:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Dijital imza oluştur
  const handleCreateSignature = async () => {
    try {
      const signature = await createDigitalSignature(
        'provider-001',
        'Dr. John Doe',
        region
      );
      setDigitalSignature(signature);
    } catch (error) {
      console.error('Dijital imza hatası:', error);
      alert('Dijital imza oluşturulamadı');
    }
  };

  // E-reçete gönder
  const handleSendEPrescription = async () => {
    if (!selectedPharmacy) {
      alert('Lütfen bir eczane seçin');
      return;
    }

    if (regionConfig.requiresDigitalSignature && !digitalSignature) {
      alert('Dijital imza gerekli');
      return;
    }

    setIsSending(true);
    try {
      const eRx = await sendEPrescription({
        prescriptionId: prescriptionId || `rx-${Date.now()}`,
        patientId: patientId || 'patient-001',
        providerId: 'provider-001',
        region,
        medications: medications.map(med => ({
          ...med,
          substitutionAllowed: region === 'us' // ABD'de yaygın
        })),
        pharmacy: selectedPharmacy,
        digitalSignature: digitalSignature || undefined
      });

      setEPrescription(eRx);
      if (onSent) {
        onSent(eRx);
      }
    } catch (error: any) {
      console.error('E-reçete gönderme hatası:', error);
      alert(error.message || 'E-reçete gönderilemedi');
    } finally {
      setIsSending(false);
    }
  };

  // Durum kontrolü
  const handleCheckStatus = async () => {
    if (!ePrescription) return;

    try {
      const status = await checkEPrescriptionStatus(ePrescription.id, region);
      setEPrescription({ ...ePrescription, status });
    } catch (error) {
      console.error('Durum kontrolü hatası:', error);
    }
  };

  const getStatusBadge = (status: EPrescriptionStatus) => {
    const labels: Record<EPrescriptionStatus, string> = {
      'draft': 'Taslak',
      'pending': 'Beklemede',
      'sent': 'Gönderildi',
      'delivered': 'Teslim Edildi',
      'filled': 'Hazırlandı',
      'cancelled': 'İptal Edildi',
      'rejected': 'Reddedildi'
    };

    return (
      <Badge className={getEPrescriptionStatusColor(status)}>
        {labels[status]}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* E-Reçete Bilgileri */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            E-Reçete Gönderimi
          </CardTitle>
          <CardDescription>
            {regionConfig.flag} {regionConfig.name} - {regionConfig.erxProvider}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Bölgeye Özel Bilgiler */}
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertTitle>Bölgeye Özel Gereksinimler</AlertTitle>
            <AlertDescription>
              {region === 'us' && (
                <ul className="list-disc list-inside mt-2">
                  <li>DEA ve NPI numarası gerekli</li>
                  <li>Surescripts entegrasyonu</li>
                  <li>Dijital sertifika ile imza</li>
                </ul>
              )}
              {region === 'eu' && (
                <ul className="list-disc list-inside mt-2">
                  <li>GDPR uyumluluğu</li>
                  <li>Ülke bazlı e-reçete sistemi</li>
                  <li>Biyometrik veya PIN ile imza</li>
                </ul>
              )}
              {region === 'tr' && (
                <ul className="list-disc list-inside mt-2">
                  <li>e-Nabız entegrasyonu</li>
                  <li>TİTCK lisans numarası</li>
                  <li>Dijital imza gerekli</li>
                </ul>
              )}
            </AlertDescription>
          </Alert>

          {/* Dijital İmza */}
          {regionConfig.requiresDigitalSignature && (
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <Label>Dijital İmza</Label>
                {digitalSignature ? (
                  <Badge className="bg-green-100 text-green-800">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    İmzalandı
                  </Badge>
                ) : (
                  <Button size="sm" onClick={handleCreateSignature}>
                    <Shield className="h-4 w-4 mr-1" />
                    İmza Oluştur
                  </Button>
                )}
              </div>
              {digitalSignature && (
                <div className="mt-2 text-sm text-gray-600">
                  <p>İmzalayan: {digitalSignature.signerName}</p>
                  <p>Yöntem: {digitalSignature.signatureMethod}</p>
                  <p>Tarih: {new Date(digitalSignature.signedAt).toLocaleString('tr-TR')}</p>
                </div>
              )}
            </div>
          )}

          {/* Eczane Arama */}
          <div className="space-y-2">
            <Label>Eczane Seç</Label>
            <div className="flex gap-2">
              <Input
                value={pharmacySearch}
                onChange={(e) => setPharmacySearch(e.target.value)}
                placeholder="Eczane adı veya adres ara..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearchPharmacy();
                  }
                }}
              />
              <Button onClick={handleSearchPharmacy} disabled={isSearching}>
                {isSearching ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Eczane Sonuçları */}
            {pharmacyResults.length > 0 && (
              <div className="space-y-2 mt-2">
                {pharmacyResults.map(pharmacy => (
                  <button
                    key={pharmacy.id}
                    onClick={() => setSelectedPharmacy(pharmacy)}
                    className={`w-full text-left p-3 border rounded-lg transition-colors ${
                      selectedPharmacy?.id === pharmacy.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-medium">{pharmacy.name}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {pharmacy.address}
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            <Phone className="h-3 w-3" />
                            {pharmacy.phone}
                          </div>
                          {pharmacy.npi && (
                            <div className="text-xs text-gray-500 mt-1">
                              NPI: {pharmacy.npi}
                            </div>
                          )}
                        </div>
                      </div>
                      {selectedPharmacy?.id === pharmacy.id && (
                        <CheckCircle className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Seçili Eczane */}
            {selectedPharmacy && (
              <Alert className="bg-blue-50 border-blue-200">
                <CheckCircle className="h-4 w-4 text-blue-600" />
                <AlertTitle>Seçili Eczane</AlertTitle>
                <AlertDescription>
                  <strong>{selectedPharmacy.name}</strong> - {selectedPharmacy.address}
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Gönder Butonu */}
          <Button
            onClick={handleSendEPrescription}
            disabled={!selectedPharmacy || isSending || (regionConfig.requiresDigitalSignature && !digitalSignature)}
            className="w-full"
            size="lg"
          >
            {isSending ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Gönderiliyor...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                E-Reçete Gönder
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* E-Reçete Durumu */}
      {ePrescription && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>E-Reçete Durumu</CardTitle>
              <Button variant="outline" size="sm" onClick={handleCheckStatus}>
                <RefreshCw className="h-4 w-4 mr-1" />
                Durumu Güncelle
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="font-medium">Durum:</span>
              {getStatusBadge(ePrescription.status)}
            </div>

            {ePrescription.trackingNumber && (
              <div>
                <span className="font-medium">Takip Numarası:</span>
                <p className="text-sm text-gray-600 font-mono mt-1">
                  {ePrescription.trackingNumber}
                </p>
              </div>
            )}

            {ePrescription.sentAt && (
              <div>
                <span className="font-medium">Gönderilme Tarihi:</span>
                <p className="text-sm text-gray-600 mt-1">
                  {new Date(ePrescription.sentAt).toLocaleString('tr-TR')}
                </p>
              </div>
            )}

            {ePrescription.deliveredAt && (
              <div>
                <span className="font-medium">Teslim Tarihi:</span>
                <p className="text-sm text-gray-600 mt-1">
                  {new Date(ePrescription.deliveredAt).toLocaleString('tr-TR')}
                </p>
              </div>
            )}

            {ePrescription.filledAt && (
              <Alert className="bg-green-50 border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertTitle>Reçete Hazırlandı</AlertTitle>
                <AlertDescription>
                  {new Date(ePrescription.filledAt).toLocaleString('tr-TR')}
                </AlertDescription>
              </Alert>
            )}

            {ePrescription.rejectionReason && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertTitle>Reddedildi</AlertTitle>
                <AlertDescription>
                  {ePrescription.rejectionReason}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

