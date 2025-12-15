"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  User,
  Calendar,
  FileText,
  AlertTriangle,
  Brain,
  Target,
  TrendingUp,
  Clock,
  Phone,
  Mail,
  MapPin,
  Plus,
  Edit,
  Download,
  Upload,
  History,
  Activity,
  Shield,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import AIProgressTracker from "@/components/psychologist/ai-progress-tracker";
import AIPatternRecognition from "@/components/psychologist/ai-pattern-recognition";
import AISentimentTimeline from "@/components/psychologist/ai-sentiment-timeline";
import AIOutcomePredictor from "@/components/psychologist/ai-outcome-predictor";
import FileManager from "@/components/psychologist/file-manager";

// Mock EMR data
const mockClientEMR = {
  id: "C001",
  name: "Ayşe Yılmaz",
  age: 32,
  gender: "Kadın",
  phone: "+90 532 123 45 67",
  email: "ayse.yilmaz@example.com",
  address: "İstanbul, Kadıköy",
  emergencyContact: {
    name: "Mehmet Yılmaz",
    relation: "Eş",
    phone: "+90 532 987 65 43",
  },
  demographics: {
    birthDate: "1992-05-15",
    occupation: "Öğretmen",
    education: "Üniversite",
    maritalStatus: "Evli",
    children: 1,
  },
  diagnosis: "Yaygın Anksiyete Bozukluğu",
  riskLevel: "low",
  status: "active",
  sessionsCompleted: 8,
  totalSessions: 12,
  startDate: "2023-11-01",
  therapist: "Dr. Zeynep Kaya",
  insurance: "SGK",
  notes: "Hasta kaygı yönetimi teknikleri üzerinde çalışıyor. İlerleme kaydediyor.",
};

const mockSessionHistory = [
  {
    id: "S001",
    date: "2024-01-15",
    duration: 50,
    type: "Bireysel",
    modality: "CBT",
    therapist: "Dr. Zeynep Kaya",
    summary: "Kaygı yönetimi teknikleri üzerinde çalışıldı. Nefes egzersizleri öğretildi.",
    moodBefore: 4,
    moodAfter: 6,
    homework: "Günlük nefes egzersizleri yapılacak",
  },
  {
    id: "S002",
    date: "2024-01-08",
    duration: 50,
    type: "Bireysel",
    modality: "CBT",
    therapist: "Dr. Zeynep Kaya",
    summary: "Bilişsel çarpıtmalar üzerinde çalışıldı. Düşünce kayıt formu verildi.",
    moodBefore: 3,
    moodAfter: 5,
    homework: "Düşünce kayıt formu doldurulacak",
  },
];

const mockAssessments = [
  {
    id: "A001",
    testName: "Beck Depresyon Envanteri (BDI-II)",
    date: "2024-01-10",
    score: 18,
    severity: "Orta",
    interpretation: "Orta düzeyde depresif belirtiler gözlenmektedir.",
  },
  {
    id: "A002",
    testName: "GAD-7 (Yaygın Anksiyete)",
    date: "2024-01-05",
    score: 12,
    severity: "Orta",
    interpretation: "Orta düzeyde anksiyete belirtileri mevcuttur.",
  },
];

const mockRiskAssessments = [
  {
    date: "2024-01-15",
    riskLevel: "low",
    factors: ["İntihar düşüncesi yok", "Sosyal destek mevcut"],
    assessedBy: "Dr. Zeynep Kaya",
  },
  {
    date: "2024-01-01",
    riskLevel: "medium",
    factors: ["Uyku bozukluğu", "İş stresi"],
    assessedBy: "Dr. Zeynep Kaya",
  },
];

const mockAttachments = [
  {
    id: "ATT001",
    name: "İlk Değerlendirme Raporu.pdf",
    type: "pdf",
    uploadDate: "2023-11-01",
    uploadedBy: "Dr. Zeynep Kaya",
  },
  {
    id: "ATT002",
    name: "Hasta Onam Formu.pdf",
    type: "pdf",
    uploadDate: "2023-11-01",
    uploadedBy: "Dr. Zeynep Kaya",
  },
];

export default function ClientDetailPage() {
  const params = useParams();
  const clientId = params?.id as string;
  const [activeTab, setActiveTab] = useState("overview");

  const client = mockClientEMR; // In real app, fetch by ID

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case "high":
        return "destructive";
      case "medium":
        return "secondary";
      default:
        return "default";
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/psychologist/clients">
            <Button variant="outline" size="sm">
              ← Geri
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{client.name}</h1>
            <p className="text-gray-600 text-sm mt-1">Danışan Detayları ve EMR</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Edit className="h-4 w-4 mr-2" />
            Düzenle
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            PDF İndir
          </Button>
        </div>
      </div>

      {/* Quick Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Risk Seviyesi</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant={getRiskBadgeVariant(client.riskLevel)} className="text-lg px-3 py-1">
              {client.riskLevel === "high" ? "Yüksek" : client.riskLevel === "medium" ? "Orta" : "Düşük"}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Tamamlanan Seans</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{client.sessionsCompleted}/{client.totalSessions}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">İlerleme</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {Math.round((client.sessionsCompleted / client.totalSessions) * 100)}%
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Durum</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant={client.status === "active" ? "default" : "secondary"}>
              {client.status === "active" ? "Aktif" : "Pasif"}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="demographics">Demografi</TabsTrigger>
          <TabsTrigger value="sessions">Seans Geçmişi</TabsTrigger>
          <TabsTrigger value="assessments">Testler</TabsTrigger>
          <TabsTrigger value="risk">Risk Değerlendirme</TabsTrigger>
          <TabsTrigger value="attachments">Dosyalar</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Contact Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  İletişim Bilgileri
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-gray-400" />
                  <span>{client.phone}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-gray-400" />
                  <span>{client.email}</span>
                </div>
                <div className="flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-gray-400" />
                  <span>{client.address}</span>
                </div>
                <div className="pt-3 border-t">
                  <p className="text-sm font-semibold mb-2">Acil Durum İletişim</p>
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-red-400" />
                    <span>{client.emergencyContact.name} ({client.emergencyContact.relation})</span>
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <Phone className="h-4 w-4 text-red-400" />
                    <span>{client.emergencyContact.phone}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Diagnosis & Treatment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Tanı ve Tedavi
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-semibold mb-1">Tanı</p>
                  <Badge variant="outline" className="text-base px-3 py-1">{client.diagnosis}</Badge>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Terapist</p>
                  <p>{client.therapist}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Başlangıç Tarihi</p>
                  <p>{new Date(client.startDate).toLocaleDateString("tr-TR")}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Sigorta</p>
                  <p>{client.insurance}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Notlar</p>
                  <p className="text-sm text-gray-600">{client.notes}</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Progress Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                İlerleme Takibi
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Seans İlerlemesi</span>
                  <span>{Math.round((client.sessionsCompleted / client.totalSessions) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-green-600 h-4 rounded-full transition-all"
                    style={{ width: `${(client.sessionsCompleted / client.totalSessions) * 100}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Progress Tracker */}
          <AIProgressTracker clientId={clientId} timeframe="all" />

          {/* AI Pattern Recognition */}
          <AIPatternRecognition clientId={clientId} minFrequency={2} />

          {/* AI Sentiment Timeline */}
          <AISentimentTimeline clientId={clientId} />

          {/* AI Outcome Predictor */}
          <AIOutcomePredictor
            clientName={client.name}
            diagnosis={client.diagnosis}
            riskLevel={client.riskLevel as "low" | "medium" | "high"}
            progressPercent={(client.sessionsCompleted / client.totalSessions) * 100}
            sessionsCompleted={client.sessionsCompleted}
            totalSessions={client.totalSessions}
          />
        </TabsContent>

        {/* Demographics Tab */}
        <TabsContent value="demographics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Demografik Bilgiler</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-semibold mb-1">Doğum Tarihi</p>
                  <p>{new Date(client.demographics.birthDate).toLocaleDateString("tr-TR")}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Yaş</p>
                  <p>{client.age}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Cinsiyet</p>
                  <p>{client.gender}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Medeni Durum</p>
                  <p>{client.demographics.maritalStatus}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Meslek</p>
                  <p>{client.demographics.occupation}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Eğitim</p>
                  <p>{client.demographics.education}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold mb-1">Çocuk Sayısı</p>
                  <p>{client.demographics.children}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Session History Tab */}
        <TabsContent value="sessions" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Seans Geçmişi</h2>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Yeni Seans Ekle
            </Button>
          </div>
          <div className="space-y-4">
            {mockSessionHistory.map((session) => (
              <Card key={session.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">
                        {new Date(session.date).toLocaleDateString("tr-TR", {
                          weekday: "long",
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                        })}
                      </CardTitle>
                      <CardDescription>
                        {session.duration} dakika • {session.type} • {session.modality}
                      </CardDescription>
                    </div>
                    <Badge variant="outline">{session.therapist}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold mb-1">Özet</p>
                    <p className="text-sm text-gray-700">{session.summary}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-semibold mb-1">Seans Öncesi Ruh Hali</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(session.moodBefore / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold">{session.moodBefore}/10</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-semibold mb-1">Seans Sonrası Ruh Hali</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${(session.moodAfter / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold">{session.moodAfter}/10</span>
                      </div>
                    </div>
                  </div>
                  {session.homework && (
                    <div>
                      <p className="text-sm font-semibold mb-1">Ev Ödevi</p>
                      <p className="text-sm text-gray-700">{session.homework}</p>
                    </div>
                  )}
                  <div className="flex gap-2 pt-2">
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-1" />
                      Detaylı Notlar
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4 mr-1" />
                      Düzenle
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Assessments Tab */}
        <TabsContent value="assessments" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Psikolojik Testler</h2>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Yeni Test Ekle
            </Button>
          </div>
          <div className="space-y-4">
            {mockAssessments.map((assessment) => (
              <Card key={assessment.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{assessment.testName}</CardTitle>
                      <CardDescription>
                        {new Date(assessment.date).toLocaleDateString("tr-TR")}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">Skor: {assessment.score}</Badge>
                      <Badge
                        variant={
                          assessment.severity === "Hafif"
                            ? "default"
                            : assessment.severity === "Orta"
                            ? "secondary"
                            : "destructive"
                        }
                      >
                        {assessment.severity}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div>
                    <p className="text-sm font-semibold mb-1">Yorumlama</p>
                    <p className="text-sm text-gray-700">{assessment.interpretation}</p>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-1" />
                      Raporu Görüntüle
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-1" />
                      PDF İndir
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Risk Assessment Tab */}
        <TabsContent value="risk" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Risk Değerlendirme Geçmişi</h2>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Yeni Değerlendirme
            </Button>
          </div>
          <div className="space-y-4">
            {mockRiskAssessments.map((risk, idx) => (
              <Card key={idx}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        {new Date(risk.date).toLocaleDateString("tr-TR")}
                      </CardTitle>
                      <CardDescription>Değerlendiren: {risk.assessedBy}</CardDescription>
                    </div>
                    <Badge variant={getRiskBadgeVariant(risk.riskLevel)}>
                      {risk.riskLevel === "high" ? "Yüksek Risk" : risk.riskLevel === "medium" ? "Orta Risk" : "Düşük Risk"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div>
                    <p className="text-sm font-semibold mb-2">Risk Faktörleri</p>
                    <ul className="space-y-1">
                      {risk.factors.map((factor, fIdx) => (
                        <li key={fIdx} className="text-sm text-gray-700 flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-orange-500" />
                          {factor}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Attachments Tab */}
        <TabsContent value="attachments" className="space-y-4">
          <FileManager
            clientId={clientId}
            clientName={client.name}
            onFileUpload={async (files) => {
              console.log("Files uploaded:", files);
              // In real app, upload to server
            }}
            onFileDelete={async (fileId) => {
              console.log("File deleted:", fileId);
              // In real app, delete from server
            }}
            onFileShare={async (fileId) => {
              console.log("File shared:", fileId);
              // In real app, share file
            }}
            onFileDownload={async (fileId) => {
              console.log("File downloaded:", fileId);
              // In real app, download from server
            }}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

