"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  Activity, 
  Bell, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle,
  Calendar,
  Clock,
  FileText,
  Plus,
  RefreshCw
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface LabTest {
  id: string;
  testName: string;
  testCode: string;
  category: 'metabolic' | 'liver' | 'kidney' | 'thyroid' | 'drug_level' | 'other';
  medicationRelated: boolean;
  medicationName?: string;
  frequency: number; // days between tests
  lastTestDate?: string;
  nextTestDate?: string;
  isOverdue: boolean;
  status: 'scheduled' | 'ordered' | 'completed' | 'overdue';
}

interface LabResult {
  id: string;
  testName: string;
  testCode: string;
  value: number | string;
  unit: string;
  referenceRange: string;
  status: 'normal' | 'abnormal' | 'critical';
  testDate: string;
  labName: string;
  notes?: string;
}

interface LabTrackingProps {
  patientId?: string;
  currentMedications?: string[];
}

// Mock data - Gerçek uygulamada API'den gelecek
const mockLabTests: LabTest[] = [
  {
    id: '1',
    testName: 'Complete Metabolic Panel',
    testCode: 'CMP',
    category: 'metabolic',
    medicationRelated: true,
    medicationName: 'Lithium',
    frequency: 90,
    lastTestDate: '2024-11-15',
    nextTestDate: '2025-02-13',
    isOverdue: false,
    status: 'scheduled'
  },
  {
    id: '2',
    testName: 'Liver Function Tests',
    testCode: 'LFT',
    category: 'liver',
    medicationRelated: true,
    medicationName: 'Valproic Acid',
    frequency: 180,
    lastTestDate: '2024-10-01',
    nextTestDate: '2025-03-30',
    isOverdue: false,
    status: 'scheduled'
  },
  {
    id: '3',
    testName: 'Thyroid Function Tests',
    testCode: 'TSH, T3, T4',
    category: 'thyroid',
    medicationRelated: false,
    frequency: 365,
    lastTestDate: '2024-06-01',
    nextTestDate: '2025-06-01',
    isOverdue: false,
    status: 'scheduled'
  },
  {
    id: '4',
    testName: 'Lithium Level',
    testCode: 'LITH',
    category: 'drug_level',
    medicationRelated: true,
    medicationName: 'Lithium',
    frequency: 90,
    lastTestDate: '2024-11-15',
    nextTestDate: '2025-02-13',
    isOverdue: false,
    status: 'scheduled'
  }
];

const mockLabResults: LabResult[] = [
  {
    id: '1',
    testName: 'Lithium Level',
    testCode: 'LITH',
    value: 0.8,
    unit: 'mEq/L',
    referenceRange: '0.6-1.2',
    status: 'normal',
    testDate: '2024-11-15',
    labName: 'LabCorp'
  },
  {
    id: '2',
    testName: 'Lithium Level',
    testCode: 'LITH',
    value: 0.9,
    unit: 'mEq/L',
    referenceRange: '0.6-1.2',
    status: 'normal',
    testDate: '2024-08-15',
    labName: 'LabCorp'
  },
  {
    id: '3',
    testName: 'Lithium Level',
    testCode: 'LITH',
    value: 0.7,
    unit: 'mEq/L',
    referenceRange: '0.6-1.2',
    status: 'normal',
    testDate: '2024-05-15',
    labName: 'LabCorp'
  },
  {
    id: '4',
    testName: 'ALT',
    testCode: 'ALT',
    value: 45,
    unit: 'U/L',
    referenceRange: '7-56',
    status: 'normal',
    testDate: '2024-11-15',
    labName: 'Quest Diagnostics'
  }
];

export default function LabTracking({ patientId, currentMedications = [] }: LabTrackingProps) {
  const t = useTranslations("prescription");
  const [labTests, setLabTests] = React.useState<LabTest[]>(mockLabTests);
  const [labResults, setLabResults] = React.useState<LabResult[]>(mockLabResults);
  const [selectedTest, setSelectedTest] = React.useState<string | null>(null);

  // İlaç bazlı otomatik lab test önerileri
  const getMedicationBasedTests = React.useMemo(() => {
    const medicationTestMap: Record<string, LabTest[]> = {
      'Lithium': [
        {
          id: 'lith-1',
          testName: 'Lithium Level',
          testCode: 'LITH',
          category: 'drug_level',
          medicationRelated: true,
          medicationName: 'Lithium',
          frequency: 90,
          status: 'scheduled',
          isOverdue: false
        },
        {
          id: 'lith-2',
          testName: 'Complete Metabolic Panel',
          testCode: 'CMP',
          category: 'metabolic',
          medicationRelated: true,
          medicationName: 'Lithium',
          frequency: 90,
          status: 'scheduled',
          isOverdue: false
        },
        {
          id: 'lith-3',
          testName: 'Thyroid Function Tests',
          testCode: 'TSH',
          category: 'thyroid',
          medicationRelated: true,
          medicationName: 'Lithium',
          frequency: 180,
          status: 'scheduled',
          isOverdue: false
        }
      ],
      'Valproic Acid': [
        {
          id: 'val-1',
          testName: 'Valproic Acid Level',
          testCode: 'VAL',
          category: 'drug_level',
          medicationRelated: true,
          medicationName: 'Valproic Acid',
          frequency: 90,
          status: 'scheduled',
          isOverdue: false
        },
        {
          id: 'val-2',
          testName: 'Liver Function Tests',
          testCode: 'LFT',
          category: 'liver',
          medicationRelated: true,
          medicationName: 'Valproic Acid',
          frequency: 180,
          status: 'scheduled',
          isOverdue: false
        },
        {
          id: 'val-3',
          testName: 'Complete Blood Count',
          testCode: 'CBC',
          category: 'metabolic',
          medicationRelated: true,
          medicationName: 'Valproic Acid',
          frequency: 180,
          status: 'scheduled',
          isOverdue: false
        }
      ]
    };

    const recommendedTests: LabTest[] = [];
    currentMedications.forEach(med => {
      const tests = medicationTestMap[med] || [];
      recommendedTests.push(...tests);
    });

    return recommendedTests;
  }, [currentMedications]);

  // Trend verileri hazırla
  const getTrendData = (testCode: string) => {
    const results = labResults
      .filter(r => r.testCode === testCode)
      .sort((a, b) => new Date(a.testDate).getTime() - new Date(b.testDate).getTime());

    return results.map(r => ({
      date: new Date(r.testDate).toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' }),
      value: typeof r.value === 'number' ? r.value : parseFloat(r.value as string),
      status: r.status
    }));
  };

  const getStatusBadge = (status: LabTest['status']) => {
    const badges = {
      'scheduled': <Badge className="bg-blue-100 text-blue-800">Planlandı</Badge>,
      'ordered': <Badge className="bg-yellow-100 text-yellow-800">Sipariş Edildi</Badge>,
      'completed': <Badge className="bg-green-100 text-green-800">Tamamlandı</Badge>,
      'overdue': <Badge className="bg-red-100 text-red-800">Gecikmiş</Badge>
    };
    return badges[status];
  };

  const getResultStatusBadge = (status: LabResult['status']) => {
    const badges = {
      'normal': <Badge className="bg-green-100 text-green-800">Normal</Badge>,
      'abnormal': <Badge className="bg-yellow-100 text-yellow-800">Anormal</Badge>,
      'critical': <Badge className="bg-red-100 text-red-800">Kritik</Badge>
    };
    return badges[status];
  };

  const overdueTests = labTests.filter(t => t.isOverdue);
  const upcomingTests = labTests.filter(t => 
    !t.isOverdue && 
    t.nextTestDate && 
    new Date(t.nextTestDate) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 gün içinde
  );

  return (
    <div className="space-y-6">
      {/* Özet Kartlar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam Test</p>
                <p className="text-2xl font-bold">{labTests.length}</p>
              </div>
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Gecikmiş</p>
                <p className="text-2xl font-bold text-red-600">{overdueTests.length}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Yaklaşan</p>
                <p className="text-2xl font-bold text-orange-600">{upcomingTests.length}</p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Sonuçlar</p>
                <p className="text-2xl font-bold text-green-600">{labResults.length}</p>
              </div>
              <FileText className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gecikmiş Testler Uyarısı */}
      {overdueTests.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Gecikmiş Lab Testleri</AlertTitle>
          <AlertDescription>
            {overdueTests.length} test gecikmiş. Lütfen hemen sipariş edin.
            <ul className="list-disc list-inside mt-2">
              {overdueTests.map(test => (
                <li key={test.id}>{test.testName} - {test.medicationName && `(${test.medicationName})`}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* İlaç Bazlı Öneriler */}
      {getMedicationBasedTests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              İlaç Bazlı Lab Test Önerileri
            </CardTitle>
            <CardDescription>
              Mevcut ilaçlarınız için önerilen düzenli lab testleri
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {getMedicationBasedTests.map(test => (
                <div key={test.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{test.testName}</span>
                      {test.medicationName && (
                        <Badge variant="outline">{test.medicationName}</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Her {test.frequency} günde bir
                    </p>
                  </div>
                  <Button size="sm" variant="outline">
                    <Plus className="h-4 w-4 mr-1" />
                    Ekle
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lab Testleri Listesi */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Lab Testleri</CardTitle>
              <CardDescription>
                Planlanmış ve tamamlanmış lab testleri
              </CardDescription>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Yeni Test Ekle
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {labTests.map(test => (
              <div 
                key={test.id} 
                className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedTest(selectedTest === test.id ? null : test.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{test.testName}</span>
                      {getStatusBadge(test.status)}
                      {test.medicationName && (
                        <Badge variant="outline" className="text-xs">
                          {test.medicationName}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      {test.lastTestDate && (
                        <span>Son: {new Date(test.lastTestDate).toLocaleDateString('tr-TR')}</span>
                      )}
                      {test.nextTestDate && (
                        <span>Sonraki: {new Date(test.nextTestDate).toLocaleDateString('tr-TR')}</span>
                      )}
                      <span>Frekans: Her {test.frequency} gün</span>
                    </div>
                  </div>
                </div>

                {/* Trend Grafiği */}
                {selectedTest === test.id && (
                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-medium mb-3">Trend Grafiği</h4>
                    {getTrendData(test.testCode).length > 0 ? (
                      <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={getTrendData(test.testCode)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="value" 
                            stroke="#3b82f6" 
                            strokeWidth={2}
                            name={test.testName}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="text-sm text-gray-500 text-center py-4">
                        Bu test için henüz sonuç bulunmuyor
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Lab Sonuçları */}
      <Card>
        <CardHeader>
          <CardTitle>Lab Sonuçları</CardTitle>
          <CardDescription>
            Son laboratuvar test sonuçları
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {labResults.map(result => (
              <div key={result.id} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{result.testName}</span>
                    {getResultStatusBadge(result.status)}
                  </div>
                  <span className="text-sm text-gray-600">
                    {new Date(result.testDate).toLocaleDateString('tr-TR')}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Değer:</span>
                    <p className="font-medium">{result.value} {result.unit}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Referans:</span>
                    <p className="font-medium">{result.referenceRange}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Lab:</span>
                    <p className="font-medium">{result.labName}</p>
                  </div>
                </div>
                {result.notes && (
                  <p className="text-sm text-gray-600 mt-2">{result.notes}</p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

