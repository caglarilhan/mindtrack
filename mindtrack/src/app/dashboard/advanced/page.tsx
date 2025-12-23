'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Pill, 
  FlaskConical, 
  Smartphone,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Zap,
  Shield
} from 'lucide-react';

interface ClinicalRecommendation {
  diagnosis: {
    primary: string;
    secondary?: string[];
    confidence: number;
  };
  treatment: {
    medications: Array<{
      name: string;
      dosage: string;
      duration: string;
      rationale: string;
    }>;
    lifestyle: string[];
    followUp: string;
  };
  warnings: string[];
  references: string[];
}

interface DrugInteraction {
  severity: 'minor' | 'moderate' | 'major' | 'contraindicated';
  description: string;
  mechanism: string;
  clinicalSignificance: string;
  management: string;
}

interface LabResult {
  id: string;
  testName: string;
  value: string | number;
  unit: string;
  status: 'normal' | 'abnormal' | 'critical';
  labDate: string;
}

export default function AdvancedFeaturesPage() {
  const [clinicalData, setClinicalData] = useState({
    patientAge: 35,
    patientGender: 'female',
    symptoms: ['kaygı', 'uyku bozukluğu', 'enerji kaybı'],
    currentMedications: ['Sertraline'],
    medicalHistory: ['depresyon'],
    vitalSigns: {
      bloodPressure: '120/80',
      heartRate: 72,
      temperature: 36.5
    }
  });

  const [clinicalResult, setClinicalResult] = useState<ClinicalRecommendation | null>(null);
  const [drugInteractions, setDrugInteractions] = useState<DrugInteraction[]>([]);
  const [labResults, setLabResults] = useState<LabResult[]>([]);
  const [loading, setLoading] = useState({
    clinical: false,
    interactions: false,
    lab: false
  });

  const handleClinicalDecision = async () => {
    setLoading(prev => ({ ...prev, clinical: true }));
    try {
      const response = await fetch('/api/ai/clinical-decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(clinicalData)
      });
      
      const data = await response.json();
      if (data.success) {
        setClinicalResult(data.recommendation);
      }
    } catch (error) {
      console.error('Clinical decision error:', error);
    } finally {
      setLoading(prev => ({ ...prev, clinical: false }));
    }
  };

  const handleDrugInteractionCheck = async () => {
    setLoading(prev => ({ ...prev, interactions: true }));
    try {
      const response = await fetch('/api/medications/interactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          medications: clinicalData.currentMedications,
          patientAge: clinicalData.patientAge,
          comorbidities: clinicalData.medicalHistory
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setDrugInteractions(data.result.interactions);
      }
    } catch (error) {
      console.error('Drug interaction error:', error);
    } finally {
      setLoading(prev => ({ ...prev, interactions: false }));
    }
  };

  const handleLabSync = async () => {
    setLoading(prev => ({ ...prev, lab: true }));
    try {
      const response = await fetch('/api/lab/results', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: 'test-patient-001',
          labProvider: 'Acibadem Lab'
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setLabResults(data.results);
      }
    } catch (error) {
      console.error('Lab sync error:', error);
    } finally {
      setLoading(prev => ({ ...prev, lab: false }));
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'major': return 'text-red-600 bg-red-50';
      case 'moderate': return 'text-yellow-600 bg-yellow-50';
      case 'minor': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'text-red-600';
      case 'abnormal': return 'text-yellow-600';
      case 'normal': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Advanced Features</h1>
        <Badge variant="outline" className="text-sm">
          AI Destekli Klinik Araçlar
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Clinical Decision Support */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-600" />
              AI Klinik Karar Desteği
            </CardTitle>
            <CardDescription>
              Hasta semptomlarına göre AI destekli tanı ve tedavi önerileri
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Hasta Yaşı</Label>
                <Input 
                  type="number" 
                  value={clinicalData.patientAge}
                  onChange={(e) => setClinicalData(prev => ({ ...prev, patientAge: parseInt(e.target.value) }))}
                />
              </div>
              <div>
                <Label>Cinsiyet</Label>
                <Select value={clinicalData.patientGender} onValueChange={(value) => setClinicalData(prev => ({ ...prev, patientGender: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Erkek</SelectItem>
                    <SelectItem value="female">Kadın</SelectItem>
                    <SelectItem value="other">Diğer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label>Semptomlar</Label>
              <Textarea 
                value={clinicalData.symptoms.join(', ')}
                onChange={(e) => setClinicalData(prev => ({ ...prev, symptoms: e.target.value.split(', ') }))}
                placeholder="kaygı, uyku bozukluğu, enerji kaybı"
              />
            </div>

            <div>
              <Label>Mevcut İlaçlar</Label>
              <Textarea 
                value={clinicalData.currentMedications.join(', ')}
                onChange={(e) => setClinicalData(prev => ({ ...prev, currentMedications: e.target.value.split(', ') }))}
                placeholder="Sertraline, Lorazepam"
              />
            </div>

            <Button 
              onClick={handleClinicalDecision} 
              disabled={loading.clinical}
              className="w-full"
            >
              {loading.clinical ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Analiz Ediliyor...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  AI Analizi Başlat
                </>
              )}
            </Button>

            {clinicalResult && (
              <div className="mt-4 p-4 border rounded-lg bg-purple-50">
                <h4 className="font-medium mb-2">AI Önerisi:</h4>
                <div className="space-y-2">
                  <div>
                    <strong>Tanı:</strong> {clinicalResult.diagnosis.primary}
                    <Badge variant="outline" className="ml-2">
                      %{Math.round(clinicalResult.diagnosis.confidence * 100)} güven
                    </Badge>
                  </div>
                  {clinicalResult.treatment.medications.length > 0 && (
                    <div>
                      <strong>Önerilen İlaçlar:</strong>
                      <ul className="list-disc list-inside ml-4">
                        {clinicalResult.treatment.medications.map((med, index) => (
                          <li key={index}>{med.name} - {med.dosage}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {clinicalResult.warnings.length > 0 && (
                    <div>
                      <strong>Uyarılar:</strong>
                      <ul className="list-disc list-inside ml-4">
                        {clinicalResult.warnings.map((warning, index) => (
                          <li key={index} className="text-red-600">{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Drug Interaction Checker */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Pill className="h-5 w-5 text-green-600" />
              İlaç Etkileşim Kontrolü
            </CardTitle>
            <CardDescription>
              İlaç kombinasyonlarının güvenlik analizi
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Kontrol Edilecek İlaçlar</Label>
              <Textarea 
                value={clinicalData.currentMedications.join(', ')}
                onChange={(e) => setClinicalData(prev => ({ ...prev, currentMedications: e.target.value.split(', ') }))}
                placeholder="Sertraline, Fluoxetine, Lorazepam"
              />
            </div>

            <Button 
              onClick={handleDrugInteractionCheck} 
              disabled={loading.interactions}
              className="w-full"
            >
              {loading.interactions ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Kontrol Ediliyor...
                </>
              ) : (
                <>
                  <Pill className="h-4 w-4 mr-2" />
                  Etkileşim Kontrolü
                </>
              )}
            </Button>

            {drugInteractions.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-medium">Tespit Edilen Etkileşimler:</h4>
                {drugInteractions.map((interaction, index) => (
                  <div key={index} className={`p-3 border rounded-lg ${getSeverityColor(interaction.severity)}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={interaction.severity === 'major' || interaction.severity === 'contraindicated' ? 'destructive' : 'default'}>
                        {interaction.severity === 'major' ? 'Major' : 
                         interaction.severity === 'moderate' ? 'Orta' :
                         interaction.severity === 'minor' ? 'Minor' : 'Kontrendike'}
                      </Badge>
                      <span className="font-medium">{interaction.description}</span>
                    </div>
                    <p className="text-sm mb-1"><strong>Mekanizma:</strong> {interaction.mechanism}</p>
                    <p className="text-sm mb-1"><strong>Klinik Önem:</strong> {interaction.clinicalSignificance}</p>
                    <p className="text-sm"><strong>Yönetim:</strong> {interaction.management}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Lab Integration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FlaskConical className="h-5 w-5 text-blue-600" />
              Laboratuvar Entegrasyonu
            </CardTitle>
            <CardDescription>
              Laboratuvar sonuçlarının otomatik senkronizasyonu
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Hasta ID</Label>
                <Input value="test-patient-001" readOnly />
              </div>
              <div>
                <Label>Lab Sağlayıcı</Label>
                <Select defaultValue="Acibadem Lab">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Acibadem Lab">Acibadem Lab</SelectItem>
                    <SelectItem value="Memorial Lab">Memorial Lab</SelectItem>
                    <SelectItem value="Anadolu Lab">Anadolu Lab</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button 
              onClick={handleLabSync} 
              disabled={loading.lab}
              className="w-full"
            >
              {loading.lab ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Senkronize Ediliyor...
                </>
              ) : (
                <>
                  <FlaskConical className="h-4 w-4 mr-2" />
                  Lab Sonuçlarını Senkronize Et
                </>
              )}
            </Button>

            {labResults.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-medium">Senkronize Edilen Sonuçlar:</h4>
                {labResults.map((result) => (
                  <div key={result.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{result.testName}</span>
                      <Badge variant={result.status === 'critical' ? 'destructive' : result.status === 'abnormal' ? 'default' : 'secondary'}>
                        {result.status === 'critical' ? 'Kritik' : 
                         result.status === 'abnormal' ? 'Anormal' : 'Normal'}
                      </Badge>
                    </div>
                    <div className="text-sm space-y-1">
                      <p><strong>Değer:</strong> {result.value} {result.unit}</p>
                      <p><strong>Tarih:</strong> {new Date(result.labDate).toLocaleDateString('tr-TR')}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Mobile PWA Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Smartphone className="h-5 w-5 text-indigo-600" />
              Mobil PWA Durumu
            </CardTitle>
            <CardDescription>
              Progressive Web App özellikleri ve durumu
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Service Worker</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Aktif
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Offline Support</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Destekleniyor
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Push Notifications</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Hazır
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>App Install</span>
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Mevcut
                </Badge>
              </div>
            </div>

            <div className="text-sm text-gray-600">
              <p><strong>PWA Özellikleri:</strong></p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Offline çalışma desteği</li>
                <li>Push bildirimleri</li>
                <li>Ana ekrana ekleme</li>
                <li>Hızlı yükleme</li>
                <li>Responsive tasarım</li>
              </ul>
            </div>

            <Button variant="outline" className="w-full">
              <Smartphone className="h-4 w-4 mr-2" />
              PWA Ayarlarını Yönet
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* System Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-green-600" />
            Sistem Durumu
          </CardTitle>
          <CardDescription>Advanced features sistem durumu ve performans</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <Brain className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <div className="font-medium">AI Engine</div>
              <Badge variant="default" className="bg-green-100 text-green-800 mt-1">
                <CheckCircle className="h-3 w-3 mr-1" />
                Aktif
              </Badge>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Pill className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <div className="font-medium">Drug Database</div>
              <Badge variant="default" className="bg-green-100 text-green-800 mt-1">
                <CheckCircle className="h-3 w-3 mr-1" />
                Güncel
              </Badge>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <FlaskConical className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <div className="font-medium">Lab Integration</div>
              <Badge variant="default" className="bg-green-100 text-green-800 mt-1">
                <CheckCircle className="h-3 w-3 mr-1" />
                Bağlı
              </Badge>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Shield className="h-8 w-8 mx-auto mb-2 text-indigo-600" />
              <div className="font-medium">Security</div>
              <Badge variant="default" className="bg-green-100 text-green-800 mt-1">
                <CheckCircle className="h-3 w-3 mr-1" />
                Güvenli
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


