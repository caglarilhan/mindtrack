'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Calendar, MessageSquare, BookOpen, FileText, Clock, CheckCircle, XCircle } from 'lucide-react';

interface Appointment {
  id: string;
  startAt: string;
  type: string;
  status: string;
  location: string;
  doctorName: string;
}

interface EducationMaterial {
  id: string;
  title: string;
  type: 'article' | 'video' | 'pdf';
  description: string;
  readTime?: number;
}

export default function PatientPortalPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([
    {
      id: 'apt-1',
      startAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      type: 'consult',
      status: 'scheduled',
      location: 'Telehealth',
      doctorName: 'Dr. Ahmet Yılmaz'
    },
    {
      id: 'apt-2',
      startAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      type: 'follow-up',
      status: 'scheduled',
      location: 'Klinik',
      doctorName: 'Dr. Ayşe Demir'
    }
  ]);

  const [educationMaterials] = useState<EducationMaterial[]>([
    {
      id: 'edu-1',
      title: 'Anksiyete Bozuklukları Hakkında',
      type: 'article',
      description: 'Anksiyete belirtileri ve başa çıkma yöntemleri',
      readTime: 5
    },
    {
      id: 'edu-2',
      title: 'Nefes Egzersizleri Videosu',
      type: 'video',
      description: 'Günlük stres yönetimi için nefes teknikleri',
      readTime: 10
    },
    {
      id: 'edu-3',
      title: 'İlaç Kullanım Rehberi',
      type: 'pdf',
      description: 'Psikiyatrik ilaçların doğru kullanımı',
      readTime: 15
    }
  ]);

  const [messages] = useState([
    { id: 'msg-1', from: 'Dr. Ahmet Yılmaz', content: 'Randevunuzu onaylayabilir misiniz?', time: '2 saat önce', unread: true },
    { id: 'msg-2', from: 'Klinik', content: 'Yeni eğitim materyali eklendi', time: '1 gün önce', unread: false }
  ]);

  const handleAppointmentAction = async (appointmentId: string, action: 'confirm' | 'cancel') => {
    try {
      const response = await fetch(`/api/appointments/${appointmentId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setAppointments(prev => 
          prev.map(apt => 
            apt.id === appointmentId 
              ? { ...apt, status: action === 'confirm' ? 'confirmed' : 'cancelled' }
              : apt
          )
        );
      }
    } catch (error) {
      console.error('Randevu işlemi başarısız:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      scheduled: 'secondary',
      confirmed: 'default',
      cancelled: 'destructive',
      completed: 'outline'
    } as const;
    
    const labels = {
      scheduled: 'Planlandı',
      confirmed: 'Onaylandı',
      cancelled: 'İptal Edildi',
      completed: 'Tamamlandı'
    };

    return <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
      {labels[status as keyof typeof labels] || status}
    </Badge>;
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'consult': return <Calendar className="h-4 w-4" />;
      case 'follow-up': return <Clock className="h-4 w-4" />;
      default: return <Calendar className="h-4 w-4" />;
    }
  };

  const getEducationIcon = (type: string) => {
    switch (type) {
      case 'article': return <FileText className="h-4 w-4" />;
      case 'video': return <BookOpen className="h-4 w-4" />;
      case 'pdf': return <FileText className="h-4 w-4" />;
      default: return <BookOpen className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Hasta Portalı</h1>
        <Badge variant="outline" className="text-sm">
          Hoş geldiniz, Hasta
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Randevular */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Randevularım
            </CardTitle>
            <CardDescription>
              Yaklaşan randevularınızı görüntüleyin ve yönetin
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {appointments.map((appointment) => (
              <div key={appointment.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(appointment.type)}
                    <span className="font-medium">
                      {new Date(appointment.startAt).toLocaleDateString('tr-TR')} - {new Date(appointment.startAt).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  {getStatusBadge(appointment.status)}
                </div>
                
                <div className="text-sm text-gray-600">
                  <p><strong>Doktor:</strong> {appointment.doctorName}</p>
                  <p><strong>Lokasyon:</strong> {appointment.location}</p>
                  <p><strong>Tür:</strong> {appointment.type === 'consult' ? 'Konsültasyon' : 'Takip'}</p>
                </div>

                {appointment.status === 'scheduled' && (
                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      onClick={() => handleAppointmentAction(appointment.id, 'confirm')}
                      className="flex items-center gap-1"
                    >
                      <CheckCircle className="h-4 w-4" />
                      Onayla
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleAppointmentAction(appointment.id, 'cancel')}
                      className="flex items-center gap-1"
                    >
                      <XCircle className="h-4 w-4" />
                      İptal Et
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Eğitim Materyalleri */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Eğitim Materyalleri
            </CardTitle>
            <CardDescription>
              Sağlığınız için hazırlanmış kaynaklar
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {educationMaterials.map((material) => (
              <div key={material.id} className="border rounded-lg p-4 space-y-2">
                <div className="flex items-center gap-2">
                  {getEducationIcon(material.type)}
                  <h3 className="font-medium">{material.title}</h3>
                </div>
                <p className="text-sm text-gray-600">{material.description}</p>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-xs">
                    {material.type === 'article' ? 'Makale' : material.type === 'video' ? 'Video' : 'PDF'}
                  </Badge>
                  {material.readTime && (
                    <span className="text-xs text-gray-500">
                      ~{material.readTime} dk
                    </span>
                  )}
                </div>
                <Button size="sm" variant="outline" className="w-full">
                  Görüntüle
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Mesajlar */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Mesajlar
            </CardTitle>
            <CardDescription>
              Doktorunuz ve klinik ile güvenli iletişim
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`border rounded-lg p-4 ${message.unread ? 'bg-blue-50 border-blue-200' : ''}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{message.from}</span>
                    {message.unread && <Badge variant="default" className="text-xs">Yeni</Badge>}
                  </div>
                  <span className="text-sm text-gray-500">{message.time}</span>
                </div>
                <p className="text-sm text-gray-700">{message.content}</p>
                <Button size="sm" variant="outline" className="mt-2">
                  Yanıtla
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


