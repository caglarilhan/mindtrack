"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Globe, Check, AlertCircle, Info } from "lucide-react";
import { regionConfigs, type PrescriptionRegion } from "@/lib/prescription-region";

interface RegionSelectorProps {
  currentRegion: PrescriptionRegion;
  onRegionChange: (region: PrescriptionRegion) => void;
  showInfo?: boolean;
}

export default function RegionSelector({ 
  currentRegion, 
  onRegionChange,
  showInfo = true 
}: RegionSelectorProps) {
  const t = useTranslations("prescription");
  const [showDetails, setShowDetails] = React.useState(false);

  const currentConfig = regionConfigs[currentRegion];

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-blue-600" />
            <CardTitle>Reçete Bölgesi</CardTitle>
          </div>
          <Badge variant="outline" className="text-lg">
            {currentConfig.flag} {currentConfig.name}
          </Badge>
        </div>
        <CardDescription>
          Mevcut bölge: {currentConfig.complianceAuthority}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Bölge Seçimi */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {Object.values(regionConfigs).map((config) => (
              <button
                key={config.region}
                onClick={() => onRegionChange(config.region)}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  currentRegion === config.region
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl">{config.flag}</span>
                  {currentRegion === config.region && (
                    <Check className="h-5 w-5 text-blue-600" />
                  )}
                </div>
                <div className="font-semibold text-sm">{config.name}</div>
                <div className="text-xs text-gray-600 mt-1">
                  {config.complianceAuthority}
                </div>
              </button>
            ))}
          </div>

          {/* Bölge Bilgileri */}
          {showInfo && (
            <div className="mt-4 pt-4 border-t">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
              >
                <Info className="h-4 w-4" />
                Bölge Detayları
                <span className={`ml-auto transition-transform ${showDetails ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </button>

              {showDetails && (
                <div className="mt-4 space-y-3 p-4 bg-gray-50 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Reçete Formatı:</span>
                      <p className="text-gray-600">{currentConfig.prescriptionFormat}</p>
                    </div>
                    <div>
                      <span className="font-medium">E-Reçete Desteği:</span>
                      <p className="text-gray-600">
                        {currentConfig.supportsERx ? '✅ Evet' : '❌ Hayır'}
                        {currentConfig.erxProvider && ` (${currentConfig.erxProvider})`}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Maksimum Refill:</span>
                      <p className="text-gray-600">{currentConfig.maxRefills}</p>
                    </div>
                    <div>
                      <span className="font-medium">Geçerlilik Süresi:</span>
                      <p className="text-gray-600">{currentConfig.defaultValidityDays} gün</p>
                    </div>
                    <div>
                      <span className="font-medium">Veri Koruma:</span>
                      <p className="text-gray-600">
                        {currentConfig.dataProtection === 'hipaa' && 'HIPAA'}
                        {currentConfig.dataProtection === 'gdpr' && 'GDPR'}
                        {currentConfig.dataProtection === 'both' && 'HIPAA + GDPR'}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Dijital İmza:</span>
                      <p className="text-gray-600">
                        {currentConfig.requiresDigitalSignature ? '✅ Gerekli' : '❌ Gerekli Değil'}
                      </p>
                    </div>
                  </div>

                  {/* Uyarılar */}
                  {currentRegion === 'us' && (
                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                        <div className="text-sm text-yellow-800">
                          <strong>ABD Sistemi:</strong> DEA numarası ve NPI gereklidir. 
                          Schedule II ilaçlar için kağıt reçete zorunludur.
                        </div>
                      </div>
                    </div>
                  )}

                  {(currentRegion === 'eu' || currentRegion === 'tr') && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                        <div className="text-sm text-blue-800">
                          <strong>Avrupa/Türkiye Sistemi:</strong> GDPR uyumluluğu gereklidir. 
                          Kontrollü ilaçlar için özel reçete formatı kullanılmalıdır.
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}


