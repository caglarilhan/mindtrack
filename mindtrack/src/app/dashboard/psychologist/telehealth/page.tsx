"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import TelehealthVoiceToText from "@/components/psychologist/telehealth-voice-to-text";
import {
  Video,
  Link2,
  Copy,
  CheckCircle,
  Clock,
  User,
  Calendar,
  Mail,
  MessageSquare,
  BarChart3,
  TrendingUp,
  Eye,
  Trash2,
} from "lucide-react";
import Link from "next/link";

// Mock telehealth data
const mockTelehealthLinks = [
  {
    id: "TL001",
    sessionId: "S001",
    clientId: "C001",
    clientName: "Ayşe Yılmaz",
    link: "https://meet.mindtrack.com/session-abc123",
    createdDate: "2024-01-15T10:00:00",
    sessionDate: "2024-01-15T14:00:00",
    status: "completed",
    duration: 50,
    participants: 2,
    reminderSent: true,
    joined: true,
  },
  {
    id: "TL002",
    sessionId: "S002",
    clientId: "C002",
    clientName: "Mehmet Demir",
    link: "https://meet.mindtrack.com/session-xyz789",
    createdDate: "2024-01-15T11:00:00",
    sessionDate: "2024-01-15T15:30:00",
    status: "scheduled",
    duration: 50,
    participants: null,
    reminderSent: true,
    joined: false,
  },
  {
    id: "TL003",
    sessionId: "S003",
    clientId: "C003",
    clientName: "Zeynep Kaya",
    link: "https://meet.mindtrack.com/session-def456",
    createdDate: "2024-01-14T09:00:00",
    sessionDate: "2024-01-16T10:00:00",
    status: "scheduled",
    duration: 90,
    participants: null,
    reminderSent: false,
    joined: false,
  },
];

export default function TelehealthPage() {
  const [newLink, setNewLink] = useState({
    clientId: "",
    sessionDate: "",
    sessionTime: "",
    duration: "50",
    reminder: true,
  });
  const [generatedLink, setGeneratedLink] = useState<string | null>(null);

  const handleGenerateLink = () => {
    // Mock link generation
    const mockLink = `https://meet.mindtrack.com/session-${Math.random().toString(36).substr(2, 9)}`;
    setGeneratedLink(mockLink);
    alert("Tele-seans linki oluşturuldu!");
  };

  const handleCopyLink = (link: string) => {
    navigator.clipboard.writeText(link);
    alert("Link kopyalandı!");
  };

  const handleSendReminder = (linkId: string) => {
    alert("Hatırlatma gönderildi!");
  };

  const stats = {
    totalLinks: mockTelehealthLinks.length,
    completed: mockTelehealthLinks.filter((l) => l.status === "completed").length,
    scheduled: mockTelehealthLinks.filter((l) => l.status === "scheduled").length,
    avgDuration: Math.round(
      mockTelehealthLinks
        .filter((l) => l.duration)
        .reduce((acc, l) => acc + l.duration, 0) /
        mockTelehealthLinks.filter((l) => l.duration).length
    ),
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Video className="h-8 w-8 text-blue-600" />
            Tele-Seans Yönetimi
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Online seans linkleri, hatırlatmalar ve istatistikler
          </p>
        </div>
        <Button onClick={handleGenerateLink}>
          <Link2 className="h-4 w-4 mr-2" />
          Yeni Link Oluştur
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Toplam Link</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.totalLinks}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Tamamlanan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{stats.completed}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Planlanan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{stats.scheduled}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Ortalama Süre</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">{stats.avgDuration} dk</div>
          </CardContent>
        </Card>
      </div>

      {/* Voice to Text */}
      <TelehealthVoiceToText sessionId="S001" />

      {/* Generate New Link */}
      {generatedLink && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              Link Oluşturuldu
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Input value={generatedLink} readOnly className="flex-1" />
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopyLink(generatedLink)}
              >
                <Copy className="h-4 w-4 mr-1" />
                Kopyala
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Link Form */}
      <Card>
        <CardHeader>
          <CardTitle>Yeni Tele-Seans Linki Oluştur</CardTitle>
          <CardDescription>Danışan için online seans linki oluşturun</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Danışan</Label>
              <Input
                placeholder="Danışan seçin veya ID girin"
                value={newLink.clientId}
                onChange={(e) => setNewLink({ ...newLink, clientId: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label>Seans Tarihi</Label>
              <Input
                type="date"
                value={newLink.sessionDate}
                onChange={(e) => setNewLink({ ...newLink, sessionDate: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label>Seans Saati</Label>
              <Input
                type="time"
                value={newLink.sessionTime}
                onChange={(e) => setNewLink({ ...newLink, sessionTime: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label>Süre (dakika)</Label>
              <Input
                type="number"
                value={newLink.duration}
                onChange={(e) => setNewLink({ ...newLink, duration: e.target.value })}
                className="mt-2"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="reminder"
              checked={newLink.reminder}
              onChange={(e) => setNewLink({ ...newLink, reminder: e.target.checked })}
            />
            <Label htmlFor="reminder">Otomatik hatırlatma gönder (SMS + E-mail)</Label>
          </div>
          <Button onClick={handleGenerateLink} className="w-full">
            <Link2 className="h-4 w-4 mr-2" />
            Link Oluştur ve Gönder
          </Button>
        </CardContent>
      </Card>

      {/* Links History */}
      <Card>
        <CardHeader>
          <CardTitle>Link Geçmişi</CardTitle>
          <CardDescription>Tüm oluşturulan tele-seans linkleri</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockTelehealthLinks.map((link) => (
              <Card key={link.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div>
                          <h3 className="font-semibold">{link.clientName}</h3>
                          <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {new Date(link.sessionDate).toLocaleString("tr-TR")}
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              {link.duration} dakika
                            </div>
                            {link.participants !== null && (
                              <div className="flex items-center gap-1">
                                <User className="h-4 w-4" />
                                {link.participants} katılımcı
                              </div>
                            )}
                          </div>
                        </div>
                        <Badge
                          variant={
                            link.status === "completed"
                              ? "default"
                              : link.status === "scheduled"
                              ? "secondary"
                              : "outline"
                          }
                        >
                          {link.status === "completed"
                            ? "Tamamlandı"
                            : link.status === "scheduled"
                            ? "Planlandı"
                            : "İptal"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Input value={link.link} readOnly className="flex-1 text-sm" />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCopyLink(link.link)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        {link.reminderSent && (
                          <div className="flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            <span>Hatırlatma gönderildi</span>
                          </div>
                        )}
                        {link.joined && (
                          <div className="flex items-center gap-1">
                            <CheckCircle className="h-3 w-3 text-green-600" />
                            <span>Katılım sağlandı</span>
                          </div>
                        )}
                        <span>
                          Oluşturulma: {new Date(link.createdDate).toLocaleString("tr-TR")}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      {link.status === "scheduled" && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSendReminder(link.id)}
                          >
                            <MessageSquare className="h-4 w-4 mr-1" />
                            Hatırlatma Gönder
                          </Button>
                          <Button variant="outline" size="sm">
                            <Video className="h-4 w-4 mr-1" />
                            Seansa Katıl
                          </Button>
                        </>
                      )}
                      {link.status === "completed" && (
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          İstatistikleri Gör
                        </Button>
                      )}
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Tele-Seans İstatistikleri
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-semibold mb-2">Katılım Oranı</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div className="bg-green-600 h-3 rounded-full" style={{ width: "85%" }} />
                  </div>
                  <span className="text-sm font-semibold">85%</span>
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold mb-2">Hatırlatma Gönderim Oranı</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div className="bg-blue-600 h-3 rounded-full" style={{ width: "90%" }} />
                  </div>
                  <span className="text-sm font-semibold">90%</span>
                </div>
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold mb-2">Cihaz Dağılımı</p>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Masaüstü</span>
                  <span className="font-semibold">60%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Mobil</span>
                  <span className="font-semibold">35%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Tablet</span>
                  <span className="font-semibold">5%</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

