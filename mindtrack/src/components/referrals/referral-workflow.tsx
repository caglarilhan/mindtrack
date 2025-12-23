"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  UserPlus, 
  Search, 
  Filter,
  CheckCircle,
  Clock,
  XCircle,
  AlertCircle,
  Send,
  Calendar,
  MapPin,
  Phone,
  Mail
} from "lucide-react";

interface ReferralContact {
  id: string;
  name: string;
  specialty: string;
  organization: string;
  region: string;
  contactInfo: {
    phone?: string;
    email?: string;
    address?: string;
  };
}

interface Referral {
  id: string;
  contactId: string;
  contact?: ReferralContact;
  reason: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'sent' | 'acknowledged' | 'completed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
  patientHash?: string;
}

interface ReferralWorkflowProps {
  clinicId?: string;
  patientId?: string;
}

export function ReferralWorkflow({ clinicId, patientId }: ReferralWorkflowProps) {
  const [contacts, setContacts] = useState<ReferralContact[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedContact, setSelectedContact] = useState<string>('');
  const [reason, setReason] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');

  useEffect(() => {
    fetchReferrals();
  }, [clinicId, filterStatus]);

  const fetchReferrals = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (clinicId) params.set('clinicId', clinicId);
      if (filterStatus !== 'all') params.set('status', filterStatus);
      if (searchTerm) params.set('search', searchTerm);

      const res = await fetch(`/api/referrals?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch referrals');
      const json = await res.json();
      setContacts(json.contacts || []);
      setReferrals(json.referrals || []);
    } catch (e: any) {
      console.error('Error fetching referrals:', e);
    } finally {
      setLoading(false);
    }
  };

  const createReferral = async () => {
    if (!selectedContact || !reason) {
      alert('Lütfen referans ve sebep seçin');
      return;
    }

    try {
      const res = await fetch('/api/referrals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clinicId,
          contactId: selectedContact,
          reason,
          priority,
          patientHash: patientId || null
        })
      });

      if (!res.ok) throw new Error('Failed to create referral');
      await fetchReferrals();
      setShowCreateForm(false);
      setSelectedContact('');
      setReason('');
      setPriority('medium');
    } catch (e: any) {
      alert('Referral oluşturulamadı: ' + e.message);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      pending: { variant: 'secondary' as const, icon: Clock, label: 'Beklemede' },
      sent: { variant: 'default' as const, icon: Send, label: 'Gönderildi' },
      acknowledged: { variant: 'default' as const, icon: CheckCircle, label: 'Onaylandı' },
      completed: { variant: 'default' as const, icon: CheckCircle, label: 'Tamamlandı' },
      cancelled: { variant: 'destructive' as const, icon: XCircle, label: 'İptal' }
    };
    const config = variants[status] || variants.pending;
    const Icon = config.icon;
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-gray-100 text-gray-800'
    };
    return (
      <Badge className={colors[priority] || colors.medium}>
        {priority === 'urgent' ? 'Acil' : priority === 'high' ? 'Yüksek' : priority === 'medium' ? 'Orta' : 'Düşük'}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Referral Yönetimi</h2>
          <p className="text-muted-foreground">Sağlık hizmeti sağlayıcılarına yönlendirme</p>
        </div>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <UserPlus className="h-4 w-4 mr-2" />
          Yeni Referral
        </Button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Yeni Referral Oluştur</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Referans Sağlayıcı</Label>
              <select
                value={selectedContact}
                onChange={(e) => setSelectedContact(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
              >
                <option value="">Seçiniz...</option>
                {contacts.map((contact) => (
                  <option key={contact.id} value={contact.id}>
                    {contact.name} - {contact.specialty} ({contact.organization})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Sebep</Label>
              <Textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Referral sebebini açıklayın..."
                className="mt-1"
              />
            </div>
            <div>
              <Label>Öncelik</Label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as any)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
              >
                <option value="low">Düşük</option>
                <option value="medium">Orta</option>
                <option value="high">Yüksek</option>
                <option value="urgent">Acil</option>
              </select>
            </div>
            <div className="flex gap-2">
              <Button onClick={createReferral}>Oluştur</Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>İptal</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Ara..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              <option value="all">Tüm Durumlar</option>
              <option value="pending">Beklemede</option>
              <option value="sent">Gönderildi</option>
              <option value="acknowledged">Onaylandı</option>
              <option value="completed">Tamamlandı</option>
              <option value="cancelled">İptal</option>
            </select>
            <Button onClick={fetchReferrals} variant="outline">
              Yenile
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Referrals List */}
      {loading ? (
        <div className="p-4">Yükleniyor...</div>
      ) : referrals.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            Referral bulunamadı
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {referrals.map((referral) => {
            const contact = contacts.find(c => c.id === referral.contactId);
            return (
              <Card key={referral.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{contact?.name || 'Bilinmeyen'}</CardTitle>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(referral.status)}
                      {getPriorityBadge(referral.priority)}
                    </div>
                  </div>
                  <CardDescription>
                    {contact?.specialty} - {contact?.organization}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-medium mb-1">Sebep:</p>
                    <p className="text-sm text-muted-foreground">{referral.reason}</p>
                  </div>
                  {contact?.contactInfo && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      {contact.contactInfo.phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          <span>{contact.contactInfo.phone}</span>
                        </div>
                      )}
                      {contact.contactInfo.email && (
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          <span>{contact.contactInfo.email}</span>
                        </div>
                      )}
                      {contact.contactInfo.address && (
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4" />
                          <span>{contact.contactInfo.address}</span>
                        </div>
                      )}
                    </div>
                  )}
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      Oluşturulma: {new Date(referral.createdAt).toLocaleDateString('tr-TR')}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      Güncelleme: {new Date(referral.updatedAt).toLocaleDateString('tr-TR')}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}










