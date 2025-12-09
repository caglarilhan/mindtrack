"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  Info, Shield, FileText, AlertTriangle, CheckCircle, 
  ExternalLink, Download, Upload, Database, Globe, X
} from "lucide-react";
import { type PrescriptionRegion, regionConfigs } from "@/lib/prescription-region";

interface RegionDetailsPanelProps {
  region: PrescriptionRegion;
  onClose: () => void;
}

export default function RegionDetailsPanel({ region, onClose }: RegionDetailsPanelProps) {
  const config = regionConfigs[region];

  const controlledSubstances = React.useMemo(() => {
    if (region === 'us') {
      return [
        { schedule: 'I', description: 'Yüksek bağımlılık riski - Federal olarak yasak', examples: ['Heroin', 'LSD', 'Marijuana (federal)'] },
        { schedule: 'II', description: 'Yüksek bağımlılık riski - Kağıt reçete gerekli, refill yok', examples: ['Oxycodone', 'Morphine', 'Fentanyl'] },
        { schedule: 'III', description: 'Orta bağımlılık riski - 5 refill, 6 ay içinde', examples: ['Testosterone', 'Ketamine'] },
        { schedule: 'IV', description: 'Düşük bağımlılık riski - 5 refill, 6 ay içinde', examples: ['Xanax', 'Valium', 'Ambien'] },
        { schedule: 'V', description: 'En düşük bağımlılık riski - 5 refill, 6 ay içinde', examples: ['Codeine cough syrup'] },
      ];
    } else if (region === 'eu') {
      return [
        { category: 'A', description: 'Yalnızca eczanelerden, reçete ile', examples: ['Opioids', 'Benzodiazepines'] },
        { category: 'B', description: 'Eczanelerden, reçete ile', examples: ['Antibiotics', 'Antidepressants'] },
        { category: 'C', description: 'Eczanelerden, reçetesiz', examples: ['Paracetamol', 'Ibuprofen'] },
      ];
    } else {
      return [
        { category: 'Kırmızı Reçete', description: 'Narkotik ve psikotrop maddeler', examples: ['Morphine', 'Fentanyl'] },
        { category: 'Turuncu Reçete', description: 'Psikotrop maddeler', examples: ['Benzodiazepines', 'Barbiturates'] },
        { category: 'Yeşil Reçete', description: 'Normal reçeteli ilaçlar', examples: ['Antibiotics', 'Antidepressants'] },
      ];
    }
  }, [region]);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                {config.flag} {config.name} - Bölge Detayları
              </CardTitle>
              <CardDescription>
                {config.complianceAuthority} Reçete Kuralları ve Düzenlemeleri
              </CardDescription>
            </div>
            <Button variant="ghost" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Genel Bilgiler */}
          <div>
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              <Info className="h-4 w-4" />
              Genel Bilgiler
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Uyumluluk Otoritesi</p>
                <p className="font-medium">{config.complianceAuthority}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Kağıt Reçete Desteği</p>
                <Badge variant={config.supportsPaperPrescription ? "default" : "secondary"}>
                  {config.supportsPaperPrescription ? "Evet" : "Hayır"}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">DEA/NPI Gereksinimi</p>
                <Badge variant={config.deaRequired ? "default" : "secondary"}>
                  {config.deaRequired ? "Gerekli" : "Gerekli Değil"}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Maksimum Refill</p>
                <p className="font-medium">{config.maxRefills} adet</p>
              </div>
            </div>
          </div>

          {/* Kontrollü Maddeler */}
          <div>
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Kontrollü Maddeler {region === 'us' ? '(DEA Schedule)' : region === 'eu' ? '(EMA Category)' : '(TİTCK Kategorileri)'}
            </h3>
            <div className="space-y-3">
              {controlledSubstances.map((substance, idx) => (
                <Card key={idx} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">
                          {region === 'us' ? `Schedule ${substance.schedule}` : substance.category}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{substance.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {substance.examples.map((example, eIdx) => (
                          <Badge key={eIdx} variant="secondary" className="text-xs">
                            {example}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* E-Reçete Entegrasyonu */}
          <div>
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              <Database className="h-4 w-4" />
              Elektronik Reçete Entegrasyonu
            </h3>
            {region === 'us' && (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>Surescripts EPCS</AlertTitle>
                <AlertDescription>
                  ABD'de elektronik reçete gönderimi için Surescripts EPCS (Electronic Prescribing of Controlled Substances) sistemi kullanılır.
                  DEA numarası ve dijital sertifika gereklidir.
                </AlertDescription>
              </Alert>
            )}
            {region === 'eu' && (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>EMA Standartları</AlertTitle>
                <AlertDescription>
                  Avrupa Birliği'nde ülkeye göre farklı e-reçete sistemleri kullanılır (örn: eRezept - Almanya, ePrescription - İspanya).
                  GDPR uyumluluğu zorunludur.
                </AlertDescription>
              </Alert>
            )}
            {region === 'tr' && (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>e-Nabız Entegrasyonu</AlertTitle>
                <AlertDescription>
                  Türkiye'de elektronik reçete gönderimi için e-Nabız sistemi kullanılır.
                  TİTCK lisans numarası ve dijital imza gereklidir.
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Reçete Formatı */}
          <div>
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Reçete Formatı Gereksinimleri
            </h3>
            <div className="space-y-2">
              {region === 'us' && (
                <>
                  <p className="text-sm">• DEA numarası zorunlu (Schedule II-V için)</p>
                  <p className="text-sm">• NPI (National Provider Identifier) numarası zorunlu</p>
                  <p className="text-sm">• Schedule II için kağıt reçete veya EPCS gerekli</p>
                  <p className="text-sm">• Schedule II için refill yapılamaz</p>
                </>
              )}
              {region === 'eu' && (
                <>
                  <p className="text-sm">• Lisans numarası zorunlu</p>
                  <p className="text-sm">• GDPR uyumlu hasta verisi işleme</p>
                  <p className="text-sm">• Ülkeye özel reçete formatı</p>
                  <p className="text-sm">• Biyometrik veya PIN ile dijital imza</p>
                </>
              )}
              {region === 'tr' && (
                <>
                  <p className="text-sm">• TİTCK lisans numarası zorunlu</p>
                  <p className="text-sm">• e-Nabız entegrasyonu</p>
                  <p className="text-sm">• Dijital imza gereklidir</p>
                  <p className="text-sm">• Kırmızı/Turuncu reçeteler için özel kurallar</p>
                </>
              )}
            </div>
          </div>

          {/* Aksiyonlar */}
          <div className="flex gap-2 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Kapat
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Kuralları İndir (PDF)
            </Button>
            <Button variant="outline">
              <ExternalLink className="h-4 w-4 mr-2" />
              Resmi Dökümanlar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

