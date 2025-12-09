"use client";

import * as React from "react";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  AlertTriangle, 
  Plus, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  FileText,
  Bell,
  Activity,
  X,
  Calendar,
  User
} from "lucide-react";
import { 
  type SideEffect, 
  type SideEffectSeverity,
  type SideEffectStatus,
  calculateSeverityScore,
  getSeverityColor,
  getSeverityIcon,
  commonSideEffects,
  sideEffectCategories,
  getRecommendedActions
} from "@/lib/side-effects";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface SideEffectTrackingProps {
  patientId?: string;
  currentMedications?: string[];
}

// Mock data
const mockSideEffects: SideEffect[] = [
  {
    id: '1',
    patientId: 'patient1',
    medicationId: 'med1',
    medicationName: 'Sertraline',
    sideEffectName: 'Nausea',
    category: 'gastrointestinal',
    severity: 'moderate',
    status: 'ongoing',
    onsetDate: '2024-12-01',
    reportedDate: '2024-12-02',
    description: 'Sabahları mide bulantısı, özellikle ilacı aç karnına aldığımda',
    impactOnDailyLife: 'moderate',
    actionTaken: ['Yemekle birlikte alınması önerildi'],
    outcome: 'Devam ediyor',
    reportedBy: 'patient',
    notes: 'Hasta yemekle birlikte almayı deniyor'
  },
  {
    id: '2',
    patientId: 'patient1',
    medicationId: 'med1',
    medicationName: 'Sertraline',
    sideEffectName: 'Insomnia',
    category: 'neurological',
    severity: 'mild',
    status: 'resolved',
    onsetDate: '2024-11-15',
    reportedDate: '2024-11-16',
    resolvedDate: '2024-11-25',
    description: 'Uykuya dalmada güçlük',
    impactOnDailyLife: 'mild',
    actionTaken: ['İlacı sabah alması önerildi'],
    outcome: 'Çözüldü',
    reportedBy: 'patient'
  },
  {
    id: '3',
    patientId: 'patient1',
    medicationId: 'med2',
    medicationName: 'Alprazolam',
    sideEffectName: 'Drowsiness',
    category: 'neurological',
    severity: 'moderate',
    status: 'ongoing',
    onsetDate: '2024-12-05',
    reportedDate: '2024-12-06',
    description: 'Gün içinde aşırı uykulu hissetme',
    impactOnDailyLife: 'severe',
    actionTaken: ['Dozaj azaltıldı'],
    outcome: 'İzleniyor',
    reportedBy: 'patient'
  }
];

export default function SideEffectTracking({ patientId, currentMedications = [] }: SideEffectTrackingProps) {
  const t = useTranslations("prescription");
  const [sideEffects, setSideEffects] = React.useState<SideEffect[]>(mockSideEffects);
  const [showReportForm, setShowReportForm] = React.useState(false);
  const [selectedMedication, setSelectedMedication] = React.useState<string>("");
  const [selectedSideEffect, setSelectedSideEffect] = React.useState<string>("");
  const [severity, setSeverity] = React.useState<SideEffectSeverity>('mild');
  const [category, setCategory] = React.useState<SideEffect['category']>('other');
  const [description, setDescription] = React.useState("");
  const [impactOnDailyLife, setImpactOnDailyLife] = React.useState<SideEffect['impactOnDailyLife']>('none');
  const [customSideEffect, setCustomSideEffect] = React.useState("");

  // İstatistikler
  const stats = React.useMemo(() => {
    const total = sideEffects.length;
    const bySeverity = sideEffects.reduce((acc, se) => {
      acc[se.severity] = (acc[se.severity] || 0) + 1;
      return acc;
    }, {} as Record<SideEffectSeverity, number>);
    
    const byStatus = sideEffects.reduce((acc, se) => {
      acc[se.status] = (acc[se.status] || 0) + 1;
      return acc;
    }, {} as Record<SideEffectStatus, number>);

    const resolved = sideEffects.filter(se => se.status === 'resolved').length;
    const resolutionRate = total > 0 ? (resolved / total) * 100 : 0;

    const critical = sideEffects.filter(se => se.severity === 'critical' || se.severity === 'severe').length;

    return {
      total,
      bySeverity,
      byStatus,
      resolutionRate,
      critical
    };
  }, [sideEffects]);

  // Grafik verileri
  const severityChartData = React.useMemo(() => {
    return Object.entries(stats.bySeverity).map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      value,
      color: getSeverityColor(key as SideEffectSeverity).split(' ')[0].replace('bg-', '')
    }));
  }, [stats.bySeverity]);

  const handleSubmitReport = () => {
    if (!selectedMedication || !selectedSideEffect || !description) {
      alert('Lütfen tüm gerekli alanları doldurun');
      return;
    }

    const newSideEffect: SideEffect = {
      id: Date.now().toString(),
      patientId: patientId || 'patient1',
      medicationId: 'med1',
      medicationName: selectedMedication,
      sideEffectName: selectedSideEffect || customSideEffect,
      category,
      severity,
      status: 'reported',
      onsetDate: new Date().toISOString().split('T')[0],
      reportedDate: new Date().toISOString().split('T')[0],
      description,
      impactOnDailyLife,
      actionTaken: [],
      outcome: 'Yeni bildirildi',
      reportedBy: 'patient'
    };

    setSideEffects([...sideEffects, newSideEffect]);
    setShowReportForm(false);
    // Formu sıfırla
    setSelectedMedication("");
    setSelectedSideEffect("");
    setDescription("");
    setSeverity('mild');
    setCategory('other');
    setImpactOnDailyLife('none');
    setCustomSideEffect("");
  };

  const getAvailableSideEffects = () => {
    if (!selectedMedication) return [];
    return commonSideEffects[selectedMedication] || [];
  };

  const getSeverityBadge = (severity: SideEffectSeverity) => {
    return (
      <Badge className={`${getSeverityColor(severity)} border`}>
        {getSeverityIcon(severity)} {severity.charAt(0).toUpperCase() + severity.slice(1)}
      </Badge>
    );
  };

  const getStatusBadge = (status: SideEffectStatus) => {
    const badges = {
      'reported': <Badge className="bg-blue-100 text-blue-800">Bildirildi</Badge>,
      'investigating': <Badge className="bg-yellow-100 text-yellow-800">İnceleniyor</Badge>,
      'resolved': <Badge className="bg-green-100 text-green-800">Çözüldü</Badge>,
      'ongoing': <Badge className="bg-orange-100 text-orange-800">Devam Ediyor</Badge>
    };
    return badges[status];
  };

  const criticalSideEffects = sideEffects.filter(se => 
    se.severity === 'critical' || se.severity === 'severe'
  );

  return (
    <div className="space-y-6">
      {/* Özet Kartlar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam Bildirim</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Kritik/Şiddetli</p>
                <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Çözülme Oranı</p>
                <p className="text-2xl font-bold text-green-600">{stats.resolutionRate.toFixed(0)}%</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Devam Eden</p>
                <p className="text-2xl font-bold text-orange-600">
                  {sideEffects.filter(se => se.status === 'ongoing').length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Kritik Yan Etkiler Uyarısı */}
      {criticalSideEffects.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Kritik/Şiddetli Yan Etkiler</AlertTitle>
          <AlertDescription>
            {criticalSideEffects.length} kritik veya şiddetli yan etki bildirildi. Lütfen hemen inceleyin.
            <ul className="list-disc list-inside mt-2">
              {criticalSideEffects.map(se => (
                <li key={se.id}>
                  <strong>{se.medicationName}</strong> - {se.sideEffectName} ({se.severity})
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Yan Etki Bildirimi Formu */}
      {showReportForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Yeni Yan Etki Bildirimi</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setShowReportForm(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <CardDescription>
              Hasta tarafından bildirilen yan etkiyi kaydedin
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>İlaç *</Label>
                <Select value={selectedMedication} onValueChange={setSelectedMedication}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="İlaç seçin" />
                  </SelectTrigger>
                  <SelectContent>
                    {currentMedications.map(med => (
                      <SelectItem key={med} value={med}>{med}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Yan Etki *</Label>
                {selectedMedication && getAvailableSideEffects().length > 0 ? (
                  <Select value={selectedSideEffect} onValueChange={setSelectedSideEffect}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Yan etki seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      {getAvailableSideEffects().map(se => (
                        <SelectItem key={se} value={se}>{se}</SelectItem>
                      ))}
                      <SelectItem value="custom">Diğer (özel)</SelectItem>
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    value={customSideEffect}
                    onChange={(e) => setCustomSideEffect(e.target.value)}
                    placeholder="Yan etki adı"
                    className="mt-1"
                  />
                )}
              </div>
            </div>

            {selectedSideEffect === 'custom' && (
              <div>
                <Label>Özel Yan Etki Adı *</Label>
                <Input
                  value={customSideEffect}
                  onChange={(e) => setCustomSideEffect(e.target.value)}
                  placeholder="Yan etki adını girin"
                  className="mt-1"
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Şiddet *</Label>
                <Select value={severity} onValueChange={(v) => setSeverity(v as SideEffectSeverity)}>
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mild">Hafif</SelectItem>
                    <SelectItem value="moderate">Orta</SelectItem>
                    <SelectItem value="severe">Şiddetli</SelectItem>
                    <SelectItem value="critical">Kritik</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Kategori *</Label>
                <Select value={category} onValueChange={(v) => setCategory(v as SideEffect['category'])}>
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {sideEffectCategories.map(cat => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.icon} {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Günlük Yaşama Etkisi *</Label>
              <Select value={impactOnDailyLife} onValueChange={(v) => setImpactOnDailyLife(v as SideEffect['impactOnDailyLife'])}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Etkisi Yok</SelectItem>
                  <SelectItem value="mild">Hafif Etki</SelectItem>
                  <SelectItem value="moderate">Orta Etki</SelectItem>
                  <SelectItem value="severe">Şiddetli Etki</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Açıklama *</Label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Yan etkinin detaylı açıklaması..."
                className="mt-1"
                rows={4}
              />
            </div>

            {/* Önerilen Aksiyonlar */}
            {severity && (
              <Alert className={getSeverityColor(severity)}>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Önerilen Aksiyonlar</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc list-inside mt-2">
                    {getRecommendedActions(severity, category).map((action, idx) => (
                      <li key={idx}>{action}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowReportForm(false)}>
                İptal
              </Button>
              <Button onClick={handleSubmitReport}>
                Bildir
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Yan Etki Listesi ve Grafikler */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Yan Etki Listesi */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Yan Etki Bildirimleri</h3>
            <Button onClick={() => setShowReportForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Yeni Bildirim
            </Button>
          </div>

          <div className="space-y-3">
            {sideEffects.map(se => (
              <Card key={se.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold">{se.medicationName}</span>
                        <span className="text-gray-500">-</span>
                        <span className="font-medium">{se.sideEffectName}</span>
                        {getSeverityBadge(se.severity)}
                        {getStatusBadge(se.status)}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{se.description}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>Başlangıç: {new Date(se.onsetDate).toLocaleDateString('tr-TR')}</span>
                        <span>Bildirim: {new Date(se.reportedDate).toLocaleDateString('tr-TR')}</span>
                        {se.resolvedDate && (
                          <span>Çözüm: {new Date(se.resolvedDate).toLocaleDateString('tr-TR')}</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {se.actionTaken.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-sm font-medium mb-1">Alınan Aksiyonlar:</p>
                      <ul className="list-disc list-inside text-sm text-gray-600">
                        {se.actionTaken.map((action, idx) => (
                          <li key={idx}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {se.notes && (
                    <div className="mt-2 text-sm text-gray-600">
                      <strong>Notlar:</strong> {se.notes}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}

            {sideEffects.length === 0 && (
              <Card>
                <CardContent className="p-8 text-center text-gray-500">
                  <AlertTriangle className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                  <p>Henüz yan etki bildirimi yok</p>
                  <Button className="mt-4" onClick={() => setShowReportForm(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    İlk Bildirimi Ekle
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* İstatistikler ve Grafikler */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Şiddet Dağılımı</CardTitle>
            </CardHeader>
            <CardContent>
              {severityChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={severityChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {severityChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={
                          entry.name === 'Critical' ? '#ef4444' :
                          entry.name === 'Severe' ? '#f97316' :
                          entry.name === 'Moderate' ? '#eab308' :
                          '#3b82f6'
                        } />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-gray-500 text-center py-8">Veri yok</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Durum Dağılımı</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(stats.byStatus).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{status}</span>
                    <Badge>{count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

