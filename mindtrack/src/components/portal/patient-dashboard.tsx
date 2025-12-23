"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { 
  Calendar, 
  Clock, 
  Video, 
  MapPin,
  CheckCircle,
  AlertCircle,
  FileText,
  MessageSquare,
  Target,
  BookOpen,
  Shield,
  Activity,
  TrendingUp,
  TrendingDown,
  Phone,
  Mail,
  User,
  Settings,
  LogOut,
  Bell,
  Heart,
  Brain,
  Zap
} from "lucide-react";

interface PatientDashboardProps {
  patientId?: string;
}

export function PatientDashboard({ patientId }: PatientDashboardProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [moodScore, setMoodScore] = useState<number | null>(null);
  const [moodNote, setMoodNote] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, [patientId]);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/portal/dashboard');
      if (!res.ok) throw new Error('Failed to fetch dashboard');
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const submitMoodCheck = async () => {
    if (moodScore === null) return;
    try {
      // TODO: Implement mood check API
      await fetch('/api/portal/mood-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ score: moodScore, note: moodNote })
      });
      setMoodScore(null);
      setMoodNote('');
      alert('Ruh hali kaydedildi');
    } catch (e) {
      alert('Kayıt başarısız');
    }
  };

  const calculateTimeUntil = (dateString: string) => {
    const now = new Date();
    const target = new Date(dateString);
    const diff = target.getTime() - now.getTime();
    if (diff < 0) return null;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours} saat ${minutes} dakika`;
  };

  if (loading) {
    return <div className="p-8 text-center">Yükleniyor...</div>;
  }

  if (error || !data) {
    return <div className="p-8 text-center text-red-600">Hata: {error || 'Veri bulunamadı'}</div>;
  }

  const { patient, nextAppointment, appointments, assignments, forms, messages } = data;
  const isLiteMode = patient.mode === 'lite';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">
                Merhaba, {patient.displayName}
              </h1>
              {!isLiteMode && patient.email && (
                <p className="text-sm text-muted-foreground mt-1">
                  {patient.email}
                </p>
              )}
              {data.nextAppointment?.providerName && (
                <p className="text-sm text-muted-foreground mt-1">
                  Terapistin: {data.nextAppointment.providerName} ({data.nextAppointment.providerRole})
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="destructive" size="sm">
                <AlertCircle className="h-4 w-4 mr-2" />
                Kriz Desteği
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Ayarlar
              </Button>
              <Button variant="outline" size="sm">
                <LogOut className="h-4 w-4 mr-2" />
                Çıkış
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Today Overview - Next Appointment */}
        {nextAppointment && (
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-600" />
                Bir Sonraki Seans
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">
                      {new Date(nextAppointment.date).toLocaleDateString('tr-TR', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  {nextAppointment.type === 'telehealth' ? (
                    <div className="flex items-center gap-2">
                      <Video className="h-4 w-4 text-green-600" />
                      <span>Online Seans</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span>{nextAppointment.location || 'Yüz yüze'}</span>
                    </div>
                  )}
                  {calculateTimeUntil(nextAppointment.date) && (
                    <Badge variant="outline" className="w-fit">
                      Seansa {calculateTimeUntil(nextAppointment.date)} kaldı
                    </Badge>
                  )}
                </div>
                <div className="flex gap-2">
                  {nextAppointment.telehealthLink && (
                    <Button size="sm" variant="default">
                      <Video className="h-4 w-4 mr-2" />
                      Seansa Katıl
                    </Button>
                  )}
                  <Button size="sm" variant="outline">
                    Detayları Gör
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Mood Check-in */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-pink-600" />
              Bugün Nasıl Hissediyorsun?
            </CardTitle>
            <CardDescription>Günlük ruh hali kontrolü</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              {[1, 2, 3, 4, 5].map((score) => (
                <button
                  key={score}
                  onClick={() => setMoodScore(score)}
                  className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl transition-all ${
                    moodScore === score
                      ? 'bg-pink-500 text-white scale-110'
                      : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {score === 1 ? '😢' : score === 2 ? '😕' : score === 3 ? '😐' : score === 4 ? '🙂' : '😊'}
                </button>
              ))}
            </div>
            <Input
              placeholder="İstersen birkaç kelimeyle anlat..."
              value={moodNote}
              onChange={(e) => setMoodNote(e.target.value)}
            />
            <Button onClick={submitMoodCheck} disabled={moodScore === null}>
              Kaydet
            </Button>
          </CardContent>
        </Card>

        {/* Goals & Treatment Progress */}
        {assignments && assignments.goals && assignments.goals.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                Hedeflerim & Terapötik Süreç
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {assignments.goals.slice(0, 3).map((goal: any, idx: number) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{goal.title || goal}</span>
                      <Badge variant="outline">Erken Aşama</Badge>
                    </div>
                    <Progress value={30} className="h-2" />
                  </div>
                ))}
              </div>
              <Button variant="outline" className="mt-4 w-full">
                Detayları Gör
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Assignments */}
        {assignments && assignments.interventions && assignments.interventions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-green-600" />
                Aktif Ödevlerim
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {assignments.interventions.slice(0, 3).map((intervention: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{intervention.title || intervention}</div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {intervention.description || 'Ödev açıklaması'}
                      </div>
                    </div>
                    <Badge variant="outline">Devam Ediyor</Badge>
                  </div>
                ))}
              </div>
              <Button variant="outline" className="mt-4 w-full">
                Tüm Ödevleri Gör
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Forms & Tests */}
        {forms && (forms.pending.length > 0 || forms.recent.length > 0) && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-purple-600" />
                Formlar & Testler
              </CardTitle>
            </CardHeader>
            <CardContent>
              {forms.pending.length > 0 && (
                <div className="space-y-2 mb-4">
                  <h4 className="font-medium text-sm">Bekleyen Formlar</h4>
                  {forms.pending.map((form: any) => (
                    <div key={form.id} className="flex items-center justify-between p-2 border rounded">
                      <span className="text-sm">{form.type}</span>
                      <Button size="sm" variant="default">
                        Doldur
                      </Button>
                    </div>
                  ))}
                </div>
              )}
              {forms.recent.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-sm">Son Sonuçlar</h4>
                  {forms.recent.map((form: any) => (
                    <div key={form.id} className="flex items-center justify-between p-2 border rounded">
                      <div>
                        <span className="text-sm">{form.type}</span>
                        {form.severity && (
                          <Badge variant={
                            form.severity === 'high' ? 'destructive' :
                            form.severity === 'medium' ? 'default' : 'secondary'
                          } className="ml-2">
                            {form.severity === 'high' ? 'Yüksek' : form.severity === 'medium' ? 'Orta' : 'Düşük'}
                          </Badge>
                        )}
                      </div>
                      <Button size="sm" variant="outline">
                        Detay
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Messages & Notifications */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                Mesajlar
                {messages.unreadCount > 0 && (
                  <Badge variant="destructive">{messages.unreadCount}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                {messages.unreadCount > 0 
                  ? `${messages.unreadCount} yeni mesajın var`
                  : 'Yeni mesaj yok'}
              </p>
              <Button variant="outline" className="w-full">
                Mesajları Aç
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-yellow-600" />
                Bildirimler
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Yaklaşan seans hatırlatmaları ve güncellemeler
              </p>
              <Button variant="outline" className="w-full">
                Tüm Bildirimleri Gör
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Appointments History */}
        <Card>
          <CardHeader>
            <CardTitle>Randevu Geçmişi & Gelecek</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Son 3 Seans</h4>
                <div className="space-y-2">
                  {appointments.recent.map((apt: any) => (
                    <div key={apt.id} className="flex items-center justify-between p-2 border rounded text-sm">
                      <div>
                        <div>{new Date(apt.start_at).toLocaleDateString('tr-TR')}</div>
                        <div className="text-muted-foreground">{apt.type}</div>
                      </div>
                      <Badge variant={apt.status === 'completed' ? 'default' : 'secondary'}>
                        {apt.status === 'completed' ? 'Tamamlandı' : apt.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-3">Gelecek 3 Seans</h4>
                <div className="space-y-2">
                  {appointments.upcoming.map((apt: any) => (
                    <div key={apt.id} className="flex items-center justify-between p-2 border rounded text-sm">
                      <div>
                        <div>{new Date(apt.start_at).toLocaleDateString('tr-TR')}</div>
                        <div className="text-muted-foreground">{apt.type}</div>
                      </div>
                      <Badge variant="outline">{apt.status}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security & Privacy (especially for Lite mode) */}
        <Card className={isLiteMode ? 'border-green-200 bg-green-50' : ''}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-green-600" />
              Güvenlik & Gizlilik
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLiteMode ? (
              <div className="space-y-2">
                <p className="text-sm">
                  <strong>Anonim moddasın.</strong> İsim, telefon ve e-posta bilgilerin saklanmıyor.
                </p>
                <p className="text-sm text-muted-foreground">
                  Verilerin sadece terapistin tarafından görülebilir ve şifrelenmiş şekilde saklanıyor.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm">Verilerin HIPAA/GDPR uyumlu şekilde saklanıyor.</p>
              </div>
            )}
            <div className="flex gap-2 mt-4">
              <Button variant="outline" size="sm">
                Veri Tercihlerimi Yönet
              </Button>
              <Button variant="outline" size="sm">
                Verilerimi İndir (GDPR)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}










