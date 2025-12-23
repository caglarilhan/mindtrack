"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { 
  Shield, 
  Search, 
  Filter,
  Calendar,
  User,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  FileText
} from "lucide-react";

interface AuditLog {
  id: string;
  action: string;
  user_id: string;
  patient_id?: string;
  appointment_id?: string;
  ip?: string;
  user_agent?: string;
  context?: Record<string, any>;
  created_at: string;
  user_profiles?: {
    full_name?: string;
    role?: string;
  };
}

interface SupervisionHubProps {
  clinicId?: string;
}

export function SupervisionHub({ clinicId }: SupervisionHubProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAction, setFilterAction] = useState<string>('all');
  const [filterUserId, setFilterUserId] = useState<string>('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    fetchLogs();
  }, [filterAction, filterUserId, startDate, endDate]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterAction !== 'all') params.set('action', filterAction);
      if (filterUserId) params.set('userId', filterUserId);
      if (startDate) params.set('startDate', startDate);
      if (endDate) params.set('endDate', endDate);
      params.set('limit', '100');

      const res = await fetch(`/api/audit/logs?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch audit logs');
      const json = await res.json();
      setLogs(json.logs || []);
    } catch (e: any) {
      console.error('Error fetching audit logs:', e);
    } finally {
      setLoading(false);
    }
  };

  const getActionBadge = (action: string) => {
    if (action.includes('write') || action.includes('create')) {
      return <Badge variant="destructive">Yazma</Badge>;
    }
    if (action.includes('read')) {
      return <Badge variant="default">Okuma</Badge>;
    }
    if (action.includes('decrypt')) {
      return <Badge variant="destructive" className="bg-purple-600">Şifre Çözme</Badge>;
    }
    return <Badge variant="secondary">{action}</Badge>;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('tr-TR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredLogs = logs.filter(log => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        log.action.toLowerCase().includes(searchLower) ||
        log.user_profiles?.full_name?.toLowerCase().includes(searchLower) ||
        log.patient_id?.toLowerCase().includes(searchLower) ||
        log.ip?.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  // Action types for filter
  const actionTypes = Array.from(new Set(logs.map(l => l.action.split('.')[0])));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Shield className="h-6 w-6" />
          Supervision Hub
        </h2>
        <p className="text-muted-foreground">Audit logları ve compliance takibi</p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtreler</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Ara</label>
              <Input
                placeholder="Aksiyon, kullanıcı, hasta..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Aksiyon Tipi</label>
              <select
                value={filterAction}
                onChange={(e) => setFilterAction(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">Tümü</option>
                {actionTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Başlangıç Tarihi</label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Bitiş Tarihi</label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={fetchLogs}>Yenile</Button>
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setFilterAction('all');
              setFilterUserId('');
              setStartDate('');
              setEndDate('');
            }}>
              Temizle
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Toplam Log</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{logs.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Yazma İşlemleri</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {logs.filter(l => l.action.includes('write') || l.action.includes('create')).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Okuma İşlemleri</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {logs.filter(l => l.action.includes('read')).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Şifre Çözme</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {logs.filter(l => l.action.includes('decrypt')).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Logs List */}
      {loading ? (
        <div className="p-4">Yükleniyor...</div>
      ) : filteredLogs.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            Log bulunamadı
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {filteredLogs.map((log) => (
            <Card key={log.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      {getActionBadge(log.action)}
                      <span className="text-sm font-medium">{log.action}</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        <span>{log.user_profiles?.full_name || log.user_id || 'Bilinmeyen'}</span>
                        {log.user_profiles?.role && (
                          <Badge variant="outline" className="text-xs">{log.user_profiles.role}</Badge>
                        )}
                      </div>
                      {log.patient_id && (
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          <span>Hasta: {log.patient_id.slice(0, 8)}...</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(log.created_at)}</span>
                      </div>
                    </div>
                    {log.ip && (
                      <div className="text-xs text-muted-foreground">
                        IP: {log.ip} {log.user_agent && `• ${log.user_agent.slice(0, 50)}...`}
                      </div>
                    )}
                    {log.context && Object.keys(log.context).length > 0 && (
                      <details className="text-xs">
                        <summary className="cursor-pointer text-muted-foreground">Detaylar</summary>
                        <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                          {JSON.stringify(log.context, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}










