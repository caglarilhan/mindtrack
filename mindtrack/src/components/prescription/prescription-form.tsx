"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  Pill, Plus, X, Calculator, AlertTriangle, CheckCircle, 
  Info, Shield, Calendar, Hash
} from "lucide-react";
import MedicationAutocomplete from "./medication-autocomplete";
import { 
  type PrescriptionRegion, 
  regionConfigs, 
  getMaxRefills, 
  getControlledSubstanceInfo,
  deaSchedules,
  emaCategories
} from "@/lib/prescription-region";
import { 
  checkMultipleDrugInteractions,
  getSeverityColor,
  type DrugInteraction
} from "@/lib/drug-interactions";

interface MedicationFormData {
  medication: {
    id: string;
    name: string;
    genericName: string;
    brandName?: string;
    category: string;
    schedule?: string;
  } | null;
  dosage: string;
  strength: string;
  frequency: string;
  route: string;
  duration: number; // days
  quantity: number;
  refills: number;
  instructions: string;
}

interface PrescriptionFormProps {
  region: PrescriptionRegion;
  patientId?: string;
  initialTemplate?: any; // PrescriptionTemplate
  onSubmit: (data: any) => void;
  onCancel: () => void;
}

export default function PrescriptionForm({ 
  region, 
  patientId,
  initialTemplate,
  onSubmit, 
  onCancel 
}: PrescriptionFormProps) {
  const t = useTranslations("prescription");
  const regionConfig = regionConfigs[region];
  
  const [diagnosis, setDiagnosis] = React.useState(initialTemplate?.diagnosis?.[0] || "");
  const [medications, setMedications] = React.useState<MedicationFormData[]>(
    initialTemplate?.medications?.map((med: any) => ({
      medication: { name: med.medicationName } as any,
      dosage: med.dosage,
      strength: med.strength,
      frequency: med.frequency,
      route: 'oral',
      duration: med.duration,
      quantity: med.quantity,
      refills: med.refills,
      instructions: med.instructions
    })) || []
  );
  const [selectedMedicationIndex, setSelectedMedicationIndex] = React.useState<number | null>(null);
  const [warnings, setWarnings] = React.useState<string[]>([]);
  const [drugInteractions, setDrugInteractions] = React.useState<DrugInteraction[]>([]);

  // Bölgeye özel alanlar
  const [deaNumber, setDeaNumber] = React.useState("");
  const [npiNumber, setNpiNumber] = React.useState("");
  const [licenseNumber, setLicenseNumber] = React.useState("");

  const addMedication = () => {
    setMedications([...medications, {
      medication: null,
      dosage: "",
      strength: "",
      frequency: "once_daily",
      route: "oral",
      duration: 30,
      quantity: 30,
      refills: 0,
      instructions: ""
    }]);
    setSelectedMedicationIndex(medications.length);
  };

  const removeMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
    if (selectedMedicationIndex === index) {
      setSelectedMedicationIndex(null);
    }
  };

  const updateMedication = (index: number, updates: Partial<MedicationFormData>) => {
    const updated = [...medications];
    updated[index] = { ...updated[index], ...updates };
    setMedications(updated);

    // Uyarıları kontrol et
    checkWarnings(updated[index]);

    // İlaç etkileşimlerini kontrol et
    checkAllDrugInteractions(updated);
  };

  // Tüm ilaçlar arasındaki etkileşimleri kontrol et
  const checkAllDrugInteractions = React.useCallback((meds: MedicationFormData[]) => {
    const medicationNames = meds
      .filter(m => m.medication?.name)
      .map(m => m.medication!.name);
    
    if (medicationNames.length >= 2) {
      const interactions = checkMultipleDrugInteractions(
        medicationNames,
        region === 'tr' ? 'eu' : region
      );
      setDrugInteractions(interactions);
    } else {
      setDrugInteractions([]);
    }
  }, [region]);

  const checkWarnings = (medication: MedicationFormData) => {
    const warningsList: string[] = [];
    
    if (medication.medication) {
      const substanceInfo = getControlledSubstanceInfo(region, medication.medication.name);
      
      if (region === 'us' && substanceInfo && 'schedule' in substanceInfo) {
        const schedule = substanceInfo as any;
        if (schedule.schedule === 'I') {
          warningsList.push('Schedule I ilaçlar federal olarak yasaktır');
        }
        if (schedule.schedule === 'II' && medication.refills > 0) {
          warningsList.push('Schedule II ilaçlar için refill yapılamaz');
        }
        if (schedule.schedule === 'II' && !regionConfig.supportsPaperPrescription) {
          warningsList.push('Schedule II ilaçlar için kağıt reçete gerekir');
        }
      }

      // Refill kontrolü
      const maxRefills = getMaxRefills(region, medication.medication.name);
      if (medication.refills > maxRefills) {
        warningsList.push(`Maksimum refill sayısı ${maxRefills}`);
      }
    }

    setWarnings(warningsList);
  };

  const calculateDosage = (medication: MedicationFormData) => {
    // Basit dozaj hesaplama örneği
    // Gerçek uygulamada hasta ağırlığı, yaş, böbrek fonksiyonu vs. dikkate alınır
    if (!medication.strength || !medication.frequency || !medication.duration) {
      return null;
    }

    const strength = parseFloat(medication.strength.replace('mg', ''));
    const frequencyMap: Record<string, number> = {
      'once_daily': 1,
      'twice_daily': 2,
      'three_times_daily': 3,
      'four_times_daily': 4
    };
    const frequency = frequencyMap[medication.frequency] || 1;
    const totalDoses = frequency * medication.duration;
    const totalQuantity = Math.ceil(totalDoses);

    return {
      recommendedQuantity: totalQuantity,
      totalDoses,
      dailyDosage: strength * frequency
    };
  };

  const handleSubmit = () => {
    // Validasyon
    if (!diagnosis.trim()) {
      alert('Tanı gerekli');
      return;
    }

    if (medications.length === 0) {
      alert('En az bir ilaç eklemelisiniz');
      return;
    }

    if (region === 'us' && (!deaNumber || !npiNumber)) {
      alert('DEA numarası ve NPI numarası gerekli');
      return;
    }

    if ((region === 'eu' || region === 'tr') && !licenseNumber) {
      alert('Lisans numarası gerekli');
      return;
    }

    // Kontrendike etkileşim kontrolü
    if (drugInteractions.some(i => i.severity === 'contraindicated')) {
      alert('Kontrendike ilaç etkileşimi var! Reçete oluşturulamaz.');
      return;
    }

    const formData = {
      region,
      diagnosis,
      medications: medications.map(med => ({
        ...med,
        calculatedDosage: calculateDosage(med)
      })),
      prescriberInfo: {
        deaNumber: region === 'us' ? deaNumber : undefined,
        npiNumber: region === 'us' ? npiNumber : undefined,
        licenseNumber: (region === 'eu' || region === 'tr') ? licenseNumber : undefined
      },
      patientId,
      drugInteractions: drugInteractions.length > 0 ? drugInteractions : undefined
    };

    onSubmit(formData);
  };

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Pill className="h-5 w-5" />
          {t("newPrescription")}
        </CardTitle>
        <CardDescription>
          {regionConfig.flag} {regionConfig.name} - {regionConfig.complianceAuthority}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Bölgeye Özel Prescriber Bilgileri */}
        {region === 'us' && (
          <div className="grid grid-cols-2 gap-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div>
              <Label htmlFor="deaNumber" className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                DEA Numarası *
              </Label>
              <Input
                id="deaNumber"
                value={deaNumber}
                onChange={(e) => setDeaNumber(e.target.value)}
                placeholder="DEA-XXXXXXXXX"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="npiNumber" className="flex items-center gap-2">
                <Hash className="h-4 w-4" />
                NPI Numarası *
              </Label>
              <Input
                id="npiNumber"
                value={npiNumber}
                onChange={(e) => setNpiNumber(e.target.value)}
                placeholder="10 haneli NPI"
                className="mt-1"
              />
            </div>
          </div>
        )}

        {(region === 'eu' || region === 'tr') && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <Label htmlFor="licenseNumber" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Lisans Numarası *
            </Label>
            <Input
              id="licenseNumber"
              value={licenseNumber}
              onChange={(e) => setLicenseNumber(e.target.value)}
              placeholder={regionConfig.licenseNumberFormat}
              className="mt-1"
            />
          </div>
        )}

        {/* Tanı */}
        <div>
          <Label htmlFor="diagnosis">{t("diagnosis")} *</Label>
          <Input
            id="diagnosis"
            value={diagnosis}
            onChange={(e) => setDiagnosis(e.target.value)}
            placeholder={t("diagnosisPlaceholder")}
            className="mt-1"
          />
        </div>

        {/* İlaçlar */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>{t("medications")}</Label>
            <Button onClick={addMedication} size="sm" variant="outline">
              <Plus className="h-4 w-4 mr-1" />
              {t("addMedication")}
            </Button>
          </div>

          {medications.map((medication, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-start justify-between mb-4">
                <h4 className="font-semibold">İlaç {index + 1}</h4>
                <Button
                  onClick={() => removeMedication(index)}
                  size="sm"
                  variant="ghost"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-4">
                {/* İlaç Arama */}
                <div>
                  <Label>İlaç *</Label>
                  <MedicationAutocomplete
                    value={medication.medication?.name || ""}
                    onChange={(med) => {
                      updateMedication(index, { 
                        medication: med ? {
                          id: med.id,
                          name: med.name,
                          genericName: med.genericName,
                          brandName: med.brandName,
                          category: med.category,
                          schedule: med.schedule
                        } : null
                      });
                      if (med) {
                        const maxRefills = getMaxRefills(region, med.name);
                        updateMedication(index, { refills: Math.min(medication.refills, maxRefills) });
                      }
                    }}
                    region={region}
                    className="mt-1"
                  />
                </div>

                {medication.medication && (
                  <>
                    {/* Güç/Doza */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Güç *</Label>
                        <Select
                          value={medication.strength}
                          onValueChange={(value) => updateMedication(index, { strength: value })}
                        >
                          <SelectTrigger className="mt-1">
                            <SelectValue placeholder="Güç seçin" />
                          </SelectTrigger>
                          <SelectContent>
                            {medication.medication && ['25mg', '50mg', '100mg', '150mg', '200mg'].map((strength) => (
                              <SelectItem key={strength} value={strength}>
                                {strength}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Sıklık *</Label>
                        <Select
                          value={medication.frequency}
                          onValueChange={(value) => updateMedication(index, { frequency: value })}
                        >
                          <SelectTrigger className="mt-1">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="once_daily">Günde 1 kez</SelectItem>
                            <SelectItem value="twice_daily">Günde 2 kez</SelectItem>
                            <SelectItem value="three_times_daily">Günde 3 kez</SelectItem>
                            <SelectItem value="four_times_daily">Günde 4 kez</SelectItem>
                            <SelectItem value="as_needed">İhtiyaç halinde</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Süre ve Miktar */}
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <Label>Süre (gün) *</Label>
                        <Input
                          type="number"
                          value={medication.duration}
                          onChange={(e) => {
                            const duration = parseInt(e.target.value) || 0;
                            updateMedication(index, { duration });
                            const calc = calculateDosage({ ...medication, duration });
                            if (calc) {
                              updateMedication(index, { quantity: calc.recommendedQuantity });
                            }
                          }}
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label>Miktar *</Label>
                        <Input
                          type="number"
                          value={medication.quantity}
                          onChange={(e) => updateMedication(index, { quantity: parseInt(e.target.value) || 0 })}
                          className="mt-1"
                        />
                        {calculateDosage(medication) && (
                          <p className="text-xs text-gray-500 mt-1">
                            Önerilen: {calculateDosage(medication)?.recommendedQuantity}
                          </p>
                        )}
                      </div>

                      <div>
                        <Label>Refill</Label>
                        <Input
                          type="number"
                          value={medication.refills}
                          onChange={(e) => {
                            const refills = parseInt(e.target.value) || 0;
                            const maxRefills = getMaxRefills(region, medication.medication?.name || '');
                            updateMedication(index, { refills: Math.min(refills, maxRefills) });
                          }}
                          className="mt-1"
                          max={getMaxRefills(region, medication.medication?.name || '')}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Maks: {getMaxRefills(region, medication.medication?.name || '')}
                        </p>
                      </div>
                    </div>

                    {/* Dozaj Hesaplayıcı */}
                    {calculateDosage(medication) && (
                      <Alert>
                        <Calculator className="h-4 w-4" />
                        <AlertDescription>
                          <div className="text-sm">
                            <strong>Hesaplanan Dozaj:</strong>
                            <ul className="list-disc list-inside mt-1">
                              <li>Günlük dozaj: {calculateDosage(medication)?.dailyDosage}mg</li>
                              <li>Toplam doz: {calculateDosage(medication)?.totalDoses}</li>
                              <li>Önerilen miktar: {calculateDosage(medication)?.recommendedQuantity}</li>
                            </ul>
                          </div>
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Uyarılar */}
                    {warnings.length > 0 && (
                      <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <ul className="list-disc list-inside">
                            {warnings.map((warning, idx) => (
                              <li key={idx}>{warning}</li>
                            ))}
                          </ul>
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Talimatlar */}
                    <div>
                      <Label>Talimatlar</Label>
                      <Textarea
                        value={medication.instructions}
                        onChange={(e) => updateMedication(index, { instructions: e.target.value })}
                        placeholder={t("instructionsPlaceholder")}
                        className="mt-1"
                        rows={2}
                      />
                    </div>
                  </>
                )}
              </div>
            </Card>
          ))}

          {medications.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              İlaç eklemek için "İlaç Ekle" butonuna tıklayın
            </div>
          )}
        </div>

        {/* İlaç Etkileşim Uyarıları */}
        {drugInteractions.length > 0 && (
          <div className="space-y-3 pt-4 border-t">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              İlaç Etkileşim Uyarıları ({drugInteractions.length})
            </h3>
            {drugInteractions.map((interaction) => {
              const severityColors = getSeverityColor(interaction.severity);
              const isCritical = interaction.severity === 'contraindicated' || interaction.severity === 'severe';
              
              return (
                <Alert 
                  key={interaction.id} 
                  variant={isCritical ? "destructive" : "default"}
                  className={isCritical ? '' : severityColors}
                >
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle className="font-semibold">
                    {interaction.drug1} + {interaction.drug2} - {interaction.severity.toUpperCase()}
                  </AlertTitle>
                  <AlertDescription className="mt-2">
                    <p className="font-medium mb-1">{interaction.description}</p>
                    <p className="text-sm mb-2">{interaction.recommendation}</p>
                    {interaction.alternativeDrugs && interaction.alternativeDrugs.length > 0 && (
                      <div className="mt-2">
                        <span className="text-sm font-medium">Alternatifler: </span>
                        <span className="text-sm">{interaction.alternativeDrugs.join(', ')}</span>
                      </div>
                    )}
                  </AlertDescription>
                </Alert>
              );
            })}
          </div>
        )}

        {/* Butonlar */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onCancel}>
            {t("cancel")}
          </Button>
          <Button 
            onClick={handleSubmit}
            disabled={drugInteractions.some(i => i.severity === 'contraindicated')}
          >
            {drugInteractions.some(i => i.severity === 'contraindicated') 
              ? 'Kontrendike Etkileşim Var!' 
              : t("create")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}


