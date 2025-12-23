"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabaseClient";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Users, Calendar, FileText, Settings, LogOut, Heart, Pill, Video, Send, Clock, Link2, User, BarChart3, Zap } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface SpecialtyConfig {
  name: string;
  icon: any;
  color: string;
  bgColor: string;
  stats: {
    title: string;
    value: string;
    description: string;
  }[];
  quickActions: {
    title: string;
    description: string;
    icon: any;
    color: string;
  }[];
}

const specialtyConfigs: Record<string, SpecialtyConfig> = {
  psychiatrist: {
    name: "Psikiyatrist",
    icon: Brain,
    color: "text-purple-600",
    bgColor: "bg-purple-50",
    stats: [
      { title: "Aktif Hasta", value: "127", description: "Tedavi altında" },
      { title: "İlaç Reçetesi", value: "342", description: "Bu ay" },
      { title: "Kontrol Randevusu", value: "89", description: "Bu hafta" },
      { title: "Acil Durum", value: "3", description: "Bekleyen" }
    ],
    quickActions: [
      { title: "Hasta Dosyaları", description: "Psikiyatrik hasta kayıtları ve geçmiş", icon: FileText, color: "text-purple-600" },
      { title: "İlaç Reçetesi", description: "Psikotropik ilaç reçetesi ve takip", icon: Pill, color: "text-green-600" },
      { title: "Tanı Kriterleri", description: "DSM-5 tanı kriterleri ve kodlama", icon: Brain, color: "text-blue-600" },
      { title: "Randevu Planlama", description: "Hasta randevu sistemi ve takvim", icon: Calendar, color: "text-orange-600" },
      { title: "Lab Sonuçları", description: "Kan tahlili ve ilaç seviyesi takibi", icon: FileText, color: "text-indigo-600" },
      { title: "Konsültasyon", description: "Diğer uzmanlarla konsültasyon", icon: Users, color: "text-cyan-600" },
      { title: "Yan Etki Takibi", description: "İlaç yan etkileri ve tolerans", icon: FileText, color: "text-red-600" },
      { title: "Acil Protokoller", description: "Kriz müdahale protokolleri", icon: Settings, color: "text-yellow-600" }
    ]
  },
  psychologist: {
    name: "Psikolog",
    icon: Heart,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    stats: [
      { title: "Aktif Danışan", value: "45", description: "Terapi alan" },
      { title: "Seans Sayısı", value: "156", description: "Bu ay" },
      { title: "Test Uygulanan", value: "23", description: "Bu hafta" },
      { title: "Tamamlanan Tedavi", value: "12", description: "Bu ay" }
    ],
    quickActions: [
      { title: "Danışan Dosyaları", description: "Psikoterapi danışan kayıtları", icon: FileText, color: "text-blue-600" },
      { title: "Seans Planlama", description: "Terapi seansları ve randevular", icon: Calendar, color: "text-green-600" },
      { title: "Psikolojik Testler", description: "MMPI, Beck, WAIS test uygulamaları", icon: Brain, color: "text-purple-600" },
      { title: "Tedavi Planları", description: "Bireysel ve grup terapi planları", icon: Heart, color: "text-orange-600" },
      { title: "Seans Notları", description: "Terapi seans kayıtları ve gözlemler", icon: FileText, color: "text-indigo-600" },
      { title: "Aile Terapisi", description: "Aile ve çift terapisi seansları", icon: Users, color: "text-cyan-600" },
      { title: "Kriz Müdahalesi", description: "Acil psikolojik müdahale protokolleri", icon: Settings, color: "text-red-600" },
      { title: "Değerlendirme Raporları", description: "Psikolojik değerlendirme raporları", icon: FileText, color: "text-yellow-600" }
    ]
  },
  client: {
    name: "Danışan",
    icon: Users,
    color: "text-green-600",
    bgColor: "bg-green-50",
    stats: [
      { title: "Aktif Tedavi", value: "1", description: "Devam eden" },
      { title: "Gelecek Randevu", value: "2", description: "Bu hafta" },
      { title: "Tamamlanan Seans", value: "8", description: "Bu ay" },
      { title: "Ödeme Durumu", value: "Güncel", description: "Son ödeme" }
    ],
    quickActions: [
      { title: "Randevularım", description: "Randevu görüntüleme, iptal ve yeniden planlama", icon: Calendar, color: "text-green-600" },
      { title: "Tedavi Geçmişim", description: "Kişisel tedavi kayıtları ve ilerleme", icon: FileText, color: "text-blue-600" },
      { title: "Ödeme ve Faturalar", description: "Ödeme geçmişi ve fatura bilgileri", icon: FileText, color: "text-purple-600" },
      { title: "İlaç Takibim", description: "İlaç kullanım takibi ve hatırlatıcılar", icon: Pill, color: "text-orange-600" },
      { title: "Doktorumla İletişim", description: "Güvenli mesajlaşma sistemi", icon: Users, color: "text-indigo-600" },
      { title: "Kişisel Günlük", description: "Günlük ruh hali ve aktivite takibi", icon: Heart, color: "text-cyan-600" },
      { title: "Eğitim Materyalleri", description: "Psikoeğitim ve kendi kendine yardım kaynakları", icon: FileText, color: "text-yellow-600" },
      { title: "Acil Durum", description: "Kriz durumunda iletişim bilgileri", icon: Settings, color: "text-red-600" }
    ]
  },
  "social-worker": {
    name: "Sosyal Hizmet Uzmanı",
    icon: Users,
    color: "text-orange-600",
    bgColor: "bg-orange-50",
    stats: [
      { title: "Aktif Vaka", value: "67", description: "Takip edilen" },
      { title: "Ev Ziyareti", value: "23", description: "Bu hafta" },
      { title: "Kurum Görüşmesi", value: "15", description: "Bu ay" },
      { title: "Acil Müdahale", value: "4", description: "Bekleyen" }
    ],
    quickActions: [
      { title: "Vaka Dosyaları", description: "Sosyal hizmet vaka kayıtları", icon: FileText, color: "text-orange-600" },
      { title: "Ev Ziyaretleri", description: "Ev ziyareti planlama ve raporlama", icon: Calendar, color: "text-green-600" },
      { title: "Kurum İletişimi", description: "Belediye, okul, hastane koordinasyonu", icon: Users, color: "text-blue-600" },
      { title: "Sosyal Destek", description: "Maddi ve manevi destek programları", icon: Heart, color: "text-purple-600" },
      { title: "Aile Danışmanlığı", description: "Aile içi sorunlar ve çözüm önerileri", icon: Users, color: "text-indigo-600" },
      { title: "Kriz Müdahalesi", description: "Acil sosyal durum müdahaleleri", icon: Settings, color: "text-red-600" },
      { title: "Kaynak Yönetimi", description: "Sosyal yardım ve kaynak koordinasyonu", icon: FileText, color: "text-cyan-600" },
      { title: "Raporlama", description: "Sosyal hizmet raporları ve istatistikler", icon: FileText, color: "text-yellow-600" }
    ]
  },
  admin: {
    name: "Yönetici",
    icon: Settings,
    color: "text-indigo-600",
    bgColor: "bg-indigo-50",
    stats: [
      { title: "Toplam Hasta", value: "1,247", description: "Kayıtlı hasta" },
      { title: "Aktif Personel", value: "28", description: "Çalışan uzman" },
      { title: "Aylık Randevu", value: "3,456", description: "Bu ay" },
      { title: "Aylık Gelir", value: "₺487,200", description: "Bu ay" }
    ],
    quickActions: [
      { title: "Personel Yönetimi", description: "Doktor, psikolog ve personel yönetimi", icon: Users, color: "text-indigo-600" },
      { title: "Finansal Dashboard", description: "Gelir-gider, mali raporlar ve analiz", icon: FileText, color: "text-green-600" },
      { title: "Randevu Yönetimi", description: "Sistem geneli randevu ve takvim yönetimi", icon: Calendar, color: "text-blue-600" },
      { title: "Hasta Veritabanı", description: "Tüm hasta kayıtları ve istatistikler", icon: Users, color: "text-orange-600" },
      { title: "Sistem Ayarları", description: "Klinik, güvenlik ve sistem konfigürasyonu", icon: Settings, color: "text-purple-600" },
      { title: "Performans Analizi", description: "Klinik performans ve KPI raporları", icon: FileText, color: "text-cyan-600" },
      { title: "Kalite Kontrol", description: "Hasta memnuniyeti ve kalite ölçümleri", icon: Heart, color: "text-yellow-600" },
      { title: "Yedekleme ve Güvenlik", description: "Veri yedekleme ve güvenlik protokolleri", icon: Settings, color: "text-red-600" }
    ]
  }
};

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [specialty, setSpecialty] = useState<string>("psychiatrist");
  // Telehealth UI state
  const [provider, setProvider] = useState<"custom" | "google_meet" | "zoom">("custom");
  const [customUrl, setCustomUrl] = useState("");
  const [generatedLink, setGeneratedLink] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("Your session is scheduled soon.");
  const [reminderLink, setReminderLink] = useState("");
  const [reminderStatus, setReminderStatus] = useState("");
  const [cronWindow, setCronWindow] = useState<number>(60);
  const [patientIdNav, setPatientIdNav] = useState<string>("");
  const [appointmentIdNav, setAppointmentIdNav] = useState<string>("");
  const router = useRouter();

  useEffect(() => {
    const getUser = async () => {
      // Test için: Eğer kullanıcı yoksa test kullanıcısı oluştur
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        // Test modu: Fake user oluştur
        setUser({ 
          id: 'test-user', 
          email: 'test@mindtrack.com',
          created_at: new Date().toISOString()
        });
        setLoading(false);
        return;
      }
      
      setUser(user);
      setLoading(false);
    };

    getUser();
  }, [router]);

  const currentSpecialty = specialtyConfigs[specialty] || specialtyConfigs.psychiatrist;
  const SpecialtyIcon = currentSpecialty.icon;

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/landing");
  };

  const handleGenerateLink = async () => {
    try {
      setGeneratedLink("");
      const res = await fetch("/api/telehealth/link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, customUrl: customUrl || undefined })
      });
      const data = await res.json();
      if (!res.ok || !data?.url) throw new Error(data?.error || "Failed");
      setGeneratedLink(data.url);
      setReminderLink(data.url);
    } catch (e: any) {
      setGeneratedLink("");
      alert(e?.message || "Failed to generate link");
    }
  };

  const handleSendReminder = async () => {
    try {
      setReminderStatus("Sending...");
      const res = await fetch("/api/telehealth/reminders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email || undefined, phone: phone || undefined, subject: "Telehealth Session Reminder", message, link: reminderLink || undefined })
      });
      const data = await res.json();
      if (!res.ok || !data?.success) throw new Error(data?.error || "Failed");
      setReminderStatus("Sent ✅");
    } catch (e: any) {
      setReminderStatus("Failed ❌");
      alert(e?.message || "Failed to send reminder");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <Brain className="h-12 w-12 text-blue-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <SpecialtyIcon className={`h-8 w-8 ${currentSpecialty.color}`} />
              <span className="text-2xl font-bold text-gray-900">MindTrack</span>
              <span className={`text-sm px-2 py-1 rounded-full ${currentSpecialty.bgColor} ${currentSpecialty.color}`}>
                {currentSpecialty.name}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                    onClick={() => router.push('/pick-role')}
                variant="outline" 
                size="sm"
              >
                Rol Değiştir
              </Button>
              <span className="text-sm text-gray-600">
                Hoş geldin, {user?.email}
              </span>
              <Button onClick={() => router.push('/dashboard/settings/communications')} variant="secondary" size="sm">
                İletişim Ayarları
              </Button>
              <Button onClick={handleLogout} variant="outline" size="sm">
                <LogOut className="h-4 w-4 mr-2" />
                Çıkış
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{currentSpecialty.name} Dashboard</h1>
          <p className="text-gray-600 mt-2">{currentSpecialty.name} rolüne özel yönetim paneline hoş geldiniz</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {currentSpecialty.stats.map((stat, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <SpecialtyIcon className={`h-4 w-4 ${currentSpecialty.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {currentSpecialty.quickActions.map((action, index) => {
            const ActionIcon = action.icon;
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <ActionIcon className={`h-5 w-5 mr-2 ${action.color}`} />
                    {action.title}
                  </CardTitle>
                  <CardDescription>
                    {action.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button className="w-full">{action.title}</Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Telehealth MVP Actions */}
        <div className="mt-10 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card id="telehealth-generate">
            <CardHeader>
          <CardTitle className="flex items-center"><Video className="h-5 w-5 mr-2 text-blue-600" />Tele‑seans Linki Oluştur</CardTitle>
          <CardDescription>Zoom / Google Meet / Custom seçenekleriyle hızlı bağlantı üretin</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                <div>
                  <Label className="mb-2 block">Sağlayıcı</Label>
                  <Select onValueChange={(v) => setProvider(v as any)} defaultValue={provider}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sağlayıcı seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="custom">Özel</SelectItem>
                      <SelectItem value="google_meet">Google Meet</SelectItem>
                      <SelectItem value="zoom">Zoom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="md:col-span-2">
                  <Label className="mb-2 block">Özel URL (opsiyonel)</Label>
                  <Input value={customUrl} onChange={(e) => setCustomUrl(e.target.value)} placeholder="https://..." />
                </div>
              </div>
              <div className="flex items-center gap-3 mt-4">
                <Button onClick={handleGenerateLink}>
                  <Video className="h-4 w-4 mr-2" />Bağlantı Oluştur
                </Button>
                {generatedLink && (
                  <a className="text-blue-600 underline break-all" href={generatedLink} target="_blank" rel="noreferrer">{generatedLink}</a>
                )}
              </div>
            </CardContent>
          </Card>

          <Card id="telehealth-reminder">
            <CardHeader>
              <CardTitle className="flex items-center"><Send className="h-5 w-5 mr-2 text-green-600" />Hatırlatma Gönder</CardTitle>
              <CardDescription>E‑posta ve/veya SMS ile hatırlatma gönder</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="mb-2 block">E‑posta</Label>
                  <Input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="hasta@example.com" />
                </div>
                <div>
                  <Label className="mb-2 block">Telefon (uluslararası)</Label>
                  <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+49..., +44..., +1..." />
                </div>
                <div className="md:col-span-2">
                  <Label className="mb-2 block">Mesaj</Label>
                  <Input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Seansınız yakında başlayacaktır." />
                </div>
                <div className="md:col-span-2">
                  <Label className="mb-2 block">Tele‑seans Bağlantısı</Label>
                  <Input value={reminderLink} onChange={(e) => setReminderLink(e.target.value)} placeholder="https://..." />
                </div>
              </div>
              <div className="flex items-center gap-3 mt-4">
                <Button variant="outline" onClick={handleSendReminder}><Send className="h-4 w-4 mr-2" />Hatırlatma Gönder</Button>
                {reminderStatus && <span className="text-sm text-gray-600">{reminderStatus}</span>}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><Clock className="h-5 w-5 mr-2 text-purple-600" />Hatırlatma Cron’unu Çalıştır</CardTitle>
              <CardDescription>Otomatik hatırlatma zamanlayıcısını şimdi çalıştırın</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                <div>
                  <Label className="mb-2 block">Pencere (dakika)</Label>
                  <Input type="number" value={cronWindow} onChange={(e) => setCronWindow(parseInt(e.target.value || '0', 10))} />
                </div>
                <div className="md:col-span-2">
                  <Button variant="outline" onClick={async () => {
                    try {
                      const res = await fetch('/api/cron/reminders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ windowMinutes: cronWindow }) });
                      const data = await res.json();
                      if (!res.ok || !data?.success) throw new Error(data?.error || 'Failed');
                      alert('Cron çalıştırıldı ✅');
                    } catch (e: any) {
                      alert(e?.message || 'Cron çalıştırılamadı');
                    }
                  }}>Run Now</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><Zap className="h-5 w-5 mr-2 text-yellow-600" />Advanced Features</CardTitle>
              <CardDescription>AI klinik karar desteği, ilaç etkileşim kontrolü ve laboratuvar entegrasyonu</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button 
                  onClick={() => router.push('/dashboard/advanced')}
                  className="w-full"
                  variant="outline"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Advanced Features'ı Aç
                </Button>
                <div className="text-sm text-gray-600">
                  AI destekli klinik karar desteği, ilaç etkileşim kontrolü, laboratuvar entegrasyonu ve mobil PWA özellikleri.
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><BarChart3 className="h-5 w-5 mr-2 text-blue-600" />Analytics Dashboard</CardTitle>
              <CardDescription>Hasta istatistikleri, randevu analizi ve compliance raporları</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button 
                  onClick={() => router.push('/dashboard/analytics')}
                  className="w-full"
                  variant="outline"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analytics Dashboard'u Aç
                </Button>
                <div className="text-sm text-gray-600">
                  Hasta demografisi, randevu trendleri, ilaç takibi ve HIPAA/GDPR compliance raporları.
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><User className="h-5 w-5 mr-2 text-green-600" />Hasta Portalı</CardTitle>
              <CardDescription>Hasta portalına erişim ve yönetim</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button 
                  onClick={() => router.push('/dashboard/portal')}
                  className="w-full"
                  variant="outline"
                >
                  <User className="h-4 w-4 mr-2" />
                  Hasta Portalını Aç
                </Button>
                <div className="text-sm text-gray-600">
                  Hastaların randevularını onaylaması, eğitim materyallerini görüntülemesi ve güvenli mesajlaşma için portal erişimi.
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><Link2 className="h-5 w-5 mr-2 text-purple-600" />Hızlı Erişim</CardTitle>
              <CardDescription>Hasta ve randevu ayar sayfalarına hızlı erişim</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                <div>
                  <Label className="mb-2 block">Patient ID</Label>
                  <Input value={patientIdNav} onChange={(e) => setPatientIdNav(e.target.value)} placeholder="patient-id" />
                </div>
                <div>
                  <Button variant="outline" onClick={() => patientIdNav && router.push(`/dashboard/patients/${patientIdNav}/preferences`)}>Hasta Tercihleri</Button>
                </div>
                <div>
                  <Label className="mb-2 block">Appointment ID</Label>
                  <Input value={appointmentIdNav} onChange={(e) => setAppointmentIdNav(e.target.value)} placeholder="appointment-id" />
                </div>
                <div>
                  <Button variant="outline" onClick={() => appointmentIdNav && router.push(`/dashboard/appointments/${appointmentIdNav}/settings`)}>Randevu Ayarları</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Adult Psychiatry Toolkit */}
        <div className="mt-10">
          <Card>
            <CardHeader>
              <CardTitle>Adult Psychiatry Toolkit</CardTitle>
              <CardDescription>Tele-seans, hatırlatmalar, hasta tercihleri ve anamnez için hızlı erişim</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Button onClick={() => {
                  const el = document.querySelector('#telehealth-generate');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }}>Generate Telehealth Link</Button>
                <Button variant="outline" onClick={() => {
                  const el = document.querySelector('#telehealth-reminder');
                  if (el) el.scrollIntoView({ behavior: 'smooth' });
                }}>Send Reminder</Button>
                <Button variant="secondary" onClick={() => patientIdNav && router.push(`/dashboard/patients/${patientIdNav}/preferences`)}>Patient Preferences</Button>
                <Button variant="secondary" onClick={() => patientIdNav && router.push(`/dashboard/patients/${patientIdNav}/anamnesis`)}>Patient Anamnesis</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
