"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  User, Pill, Calculator, CheckCircle, AlertTriangle, X,
  ChevronRight, ChevronLeft, Search, Plus, Trash2, Pharmacy
} from "lucide-react";
import MedicationAutocomplete from "./medication-autocomplete";
import { type PrescriptionRegion } from "@/lib/prescription-region";
import { checkMultipleDrugInteractions } from "@/lib/drug-interactions";

interface Patient {
  id: string;
  fullName: string;
  dob: string;
  allergies: string[];
  activeMedications: string[];
}

interface MedicationItem {
  id: string;
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
  duration: number;
  quantity: number;
  refills: number;
  sig: string;
}

interface NewPrescriptionWizardProps {
  region: PrescriptionRegion;
  onComplete: (data: {
    patientId: string;
    medications: MedicationItem[];
    pharmacy?: string;
    diagnosis: string;
  }) => void;
  onCancel: () => void;
}

const STEPS = ['patient', 'medications', 'review'] as const;
type Step = typeof STEPS[number];

export default function NewPrescriptionWizard({
  region,
  onComplete,
  onCancel
}: NewPrescriptionWizardProps) {
  const t = useTranslations("prescription");
  const [currentStep, setCurrentStep] = React.useState<Step>('patient');
  const [stepIndex, setStepIndex] = React.useState(0);
  
  // Form state
  const [patientSearch, setPatientSearch] = React.useState("");
  const [selectedPatient, setSelectedPatient] = React.useState<Patient | null>(null);
  const [medications, setMedications] = React.useState<MedicationItem[]>([]);
  const [selectedMedicationIndex, setSelectedMedicationIndex] = React.useState<number | null>(null);
  const [pharmacy, setPharmacy] = React.useState("");
  const [diagnosis, setDiagnosis] = React.useState("");
  
  // Validation & warnings
  const [drugInteractions, setDrugInteractions] = React.useState<any[]>([]);
  const [allergyWarnings, setAllergyWarnings] = React.useState<string[]>([]);
  const [warnings, setWarnings] = React.useState<string[]>([]);

  // Mock patients
  const mockPatients: Patient[] = [
    { id: '1', fullName: 'Sarah Johnson', dob: '1985-05-15', allergies: ['Penicillin'], activeMedications: [] },
    { id: '2', fullName: 'Michael Chen', dob: '1978-09-22', allergies: [], activeMedications: ['Sertraline'] },
    { id: '3', fullName: 'Emily Rodriguez', dob: '1992-03-10', allergies: ['Latex'], activeMedications: [] },
  ];

  const filteredPatients = React.useMemo(() => {
    if (!patientSearch) return mockPatients;
    return mockPatients.filter(p => 
      p.fullName.toLowerCase().includes(patientSearch.toLowerCase())
    );
  }, [patientSearch]);

  const addMedication = () => {
    setMedications([...medications, {
      id: `med-${Date.now()}`,
      medication: null,
      dosage: '',
      strength: '',
      frequency: 'once_daily',
      route: 'oral',
      duration: 30,
      quantity: 30,
      refills: 0,
      sig: ''
    }]);
    setSelectedMedicationIndex(medications.length);
  };

  const removeMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
    if (selectedMedicationIndex === index) {
      setSelectedMedicationIndex(null);
    }
  };

  const updateMedication = (index: number, updates: Partial<MedicationItem>) => {
    const updated = [...medications];
    updated[index] = { ...updated[index], ...updates };
    setMedications(updated);
    
    // Auto-generate SIG
    if (updates.dosage || updates.frequency || updates.route) {
      const med = updated[index];
      if (med.dosage && med.frequency && med.route) {
        const freqText = {
          'once_daily': 'once daily',
          'twice_daily': 'twice daily',
          'three_times_daily': 'three times daily',
          'four_times_daily': 'four times daily',
          'as_needed': 'as needed'
        }[med.frequency] || med.frequency;
        
        updated[index].sig = `Take ${med.dosage} ${med.route} ${freqText}`;
      }
    }
    
    // Check interactions
    checkDrugInteractions();
  };

  const checkDrugInteractions = React.useCallback(async () => {
    const medicationNames = medications
      .filter(m => m.medication?.name)
      .map(m => m.medication!.name);
    
    if (medicationNames.length >= 2) {
      const interactions = checkMultipleDrugInteractions(medicationNames, region);
      setDrugInteractions(interactions);
    } else {
      setDrugInteractions([]);
    }
  }, [medications, region]);

  const checkAllergies = React.useCallback(() => {
    if (!selectedPatient) return;
    
    const medicationNames = medications
      .filter(m => m.medication?.name)
      .map(m => m.medication!.name);
    
    const warnings: string[] = [];
    medicationNames.forEach(medName => {
      selectedPatient.allergies.forEach(allergy => {
        if (medName.toLowerCase().includes(allergy.toLowerCase())) {
          warnings.push(`${medName} may contain ${allergy}`);
        }
      });
    });
    
    setAllergyWarnings(warnings);
  }, [medications, selectedPatient]);

  React.useEffect(() => {
    checkDrugInteractions();
    checkAllergies();
  }, [medications, checkDrugInteractions, checkAllergies]);

  const canProceedToMedications = selectedPatient !== null;
  const canProceedToReview = medications.length > 0 && medications.every(m => 
    m.medication && m.dosage && m.strength && m.frequency && m.duration > 0
  );

  const handleNext = () => {
    if (stepIndex < STEPS.length - 1) {
      setStepIndex(stepIndex + 1);
      setCurrentStep(STEPS[stepIndex + 1]);
    }
  };

  const handleBack = () => {
    if (stepIndex > 0) {
      setStepIndex(stepIndex - 1);
      setCurrentStep(STEPS[stepIndex - 1]);
    }
  };

  const handleComplete = () => {
    if (!selectedPatient) return;
    
    onComplete({
      patientId: selectedPatient.id,
      medications,
      pharmacy,
      diagnosis
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Yeni Reçete Oluştur</CardTitle>
              <CardDescription>
                Adım {stepIndex + 1} / {STEPS.length}: {
                  currentStep === 'patient' && 'Hasta Seçimi'
                }{
                  currentStep === 'medications' && 'İlaçlar'
                }{
                  currentStep === 'review' && 'Gözden Geçir'
                }
              </CardDescription>
            </div>
            <Button variant="ghost" onClick={onCancel}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4 flex gap-2">
            {STEPS.map((step, idx) => (
              <div
                key={step}
                className={`flex-1 h-2 rounded ${
                  idx <= stepIndex ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Step 1: Patient Selection */}
          {currentStep === 'patient' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="patient-search">Hasta Ara</Label>
                <div className="relative mt-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="patient-search"
                    value={patientSearch}
                    onChange={(e) => setPatientSearch(e.target.value)}
                    placeholder="Hasta adı veya ID ile ara..."
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filteredPatients.map((patient) => (
                  <div
                    key={patient.id}
                    onClick={() => setSelectedPatient(patient)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedPatient?.id === patient.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <User className="h-5 w-5 text-gray-400" />
                        <div>
                          <div className="font-semibold">{patient.fullName}</div>
                          <div className="text-sm text-gray-600">
                            Doğum: {new Date(patient.dob).toLocaleDateString('tr-TR')}
                          </div>
                          {patient.allergies.length > 0 && (
                            <div className="mt-1">
                              <Badge variant="outline" className="text-xs text-red-600">
                                Alerji: {patient.allergies.join(', ')}
                              </Badge>
                            </div>
                          )}
                        </div>
                      </div>
                      {selectedPatient?.id === patient.id && (
                        <CheckCircle className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              {selectedPatient && (
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertTitle>Hasta Seçildi</AlertTitle>
                  <AlertDescription>
                    {selectedPatient.fullName} için reçete oluşturuluyor.
                    {selectedPatient.allergies.length > 0 && (
                      <span className="block mt-1 text-red-600">
                        ⚠️ Alerjiler: {selectedPatient.allergies.join(', ')}
                      </span>
                    )}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}

          {/* Step 2: Medications */}
          {currentStep === 'medications' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>İlaçlar</Label>
                <Button onClick={addMedication} size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  İlaç Ekle
                </Button>
              </div>
              
              <div className="space-y-4">
                {medications.map((medication, index) => (
                  <Card key={medication.id} className="p-4">
                    <div className="flex items-start justify-between mb-4">
                      <h4 className="font-semibold">İlaç {index + 1}</h4>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeMedication(index)}
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="md:col-span-2">
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
                          }}
                          region={region}
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label>Güç *</Label>
                        <Input
                          value={medication.strength}
                          onChange={(e) => updateMedication(index, { strength: e.target.value })}
                          placeholder="50mg"
                          className="mt-1"
                        />
                      </div>
                      
                      <div>
                        <Label>Sıklık *</Label>
                        <select
                          value={medication.frequency}
                          onChange={(e) => updateMedication(index, { frequency: e.target.value })}
                          className="w-full mt-1 p-2 border rounded-md"
                        >
                          <option value="once_daily">Günde 1 kez</option>
                          <option value="twice_daily">Günde 2 kez</option>
                          <option value="three_times_daily">Günde 3 kez</option>
                          <option value="four_times_daily">Günde 4 kez</option>
                          <option value="as_needed">İhtiyaç halinde</option>
                        </select>
                      </div>
                      
                      <div>
                        <Label>Süre (gün) *</Label>
                        <Input
                          type="number"
                          value={medication.duration}
                          onChange={(e) => {
                            const duration = parseInt(e.target.value) || 0;
                            const quantity = Math.ceil((duration * (medication.frequency === 'once_daily' ? 1 : medication.frequency === 'twice_daily' ? 2 : 3)) / 30) * 30;
                            updateMedication(index, { duration, quantity });
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
                      </div>
                      
                      <div>
                        <Label>Refill</Label>
                        <Input
                          type="number"
                          value={medication.refills}
                          onChange={(e) => updateMedication(index, { refills: parseInt(e.target.value) || 0 })}
                          className="mt-1"
                          max={region === 'us' ? 5 : 3}
                        />
                      </div>
                      
                      <div className="md:col-span-2">
                        <Label>Sig (Kullanım Talimatı)</Label>
                        <Input
                          value={medication.sig}
                          onChange={(e) => updateMedication(index, { sig: e.target.value })}
                          placeholder="Take 1 tablet by mouth once daily"
                          className="mt-1"
                        />
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
              
              {medications.length === 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    En az bir ilaç eklemelisiniz.
                  </AlertDescription>
                </Alert>
              )}
              
              {/* Drug Interactions */}
              {drugInteractions.length > 0 && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>İlaç Etkileşimleri Bulundu</AlertTitle>
                  <AlertDescription>
                    <ul className="list-disc list-inside mt-2">
                      {drugInteractions.map((interaction, idx) => (
                        <li key={idx}>
                          {interaction.drug1} + {interaction.drug2}: {interaction.severity}
                        </li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
              
              {/* Allergy Warnings */}
              {allergyWarnings.length > 0 && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Alerji Uyarıları</AlertTitle>
                  <AlertDescription>
                    <ul className="list-disc list-inside mt-2">
                      {allergyWarnings.map((warning, idx) => (
                        <li key={idx}>{warning}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}

          {/* Step 3: Review */}
          {currentStep === 'review' && (
            <div className="space-y-4">
              <div>
                <Label>Tanı</Label>
                <Input
                  value={diagnosis}
                  onChange={(e) => setDiagnosis(e.target.value)}
                  placeholder="Örn: Major Depressive Disorder (F32.9)"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label className="flex items-center gap-2">
                  <Pharmacy className="h-4 w-4" />
                  Eczane (Opsiyonel)
                </Label>
                <Input
                  value={pharmacy}
                  onChange={(e) => setPharmacy(e.target.value)}
                  placeholder="Eczane adı veya adres"
                  className="mt-1"
                />
              </div>
              
              <Card className="p-4 bg-gray-50">
                <h4 className="font-semibold mb-3">Reçete Özeti</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Hasta:</strong> {selectedPatient?.fullName}</div>
                  <div><strong>İlaçlar:</strong> {medications.length} adet</div>
                  <div><strong>Toplam Miktar:</strong> {medications.reduce((sum, m) => sum + m.quantity, 0)} adet</div>
                </div>
              </Card>
            </div>
          )}
          
          {/* Navigation Buttons */}
          <div className="flex justify-between pt-4 border-t">
            <Button
              variant="outline"
              onClick={stepIndex === 0 ? onCancel : handleBack}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              {stepIndex === 0 ? 'İptal' : 'Geri'}
            </Button>
            
            {stepIndex < STEPS.length - 1 ? (
              <Button
                onClick={handleNext}
                disabled={
                  (currentStep === 'patient' && !canProceedToMedications) ||
                  (currentStep === 'medications' && !canProceedToReview)
                }
              >
                İleri
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button
                onClick={handleComplete}
                disabled={!diagnosis || drugInteractions.some(i => i.severity === 'contraindicated')}
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Reçeteyi Oluştur
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

