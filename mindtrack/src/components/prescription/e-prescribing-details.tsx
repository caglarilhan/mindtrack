"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Send, CheckCircle, XCircle, Clock, AlertTriangle, RefreshCw,
  FileText, Search, Download, Eye, Calendar, User, Activity
} from "lucide-react";
import { type PrescriptionRegion } from "@/lib/prescription-region";

interface EPrescriptionLog {
  id: string;
  prescriptionId: string;
  patientName: string;
  medicationName: string;
  pharmacyName: string;
  status: 'pending' | 'sent' | 'delivered' | 'rejected' | 'cancelled';
  sentAt?: string;
  deliveredAt?: string;
  rejectedAt?: string;
  rejectionReason?: string;
  transactionId?: string;
  errorCode?: string;
  errorMessage?: string;
}

interface EPrescriptionError {
  id: string;
  timestamp: string;
  prescriptionId: string;
  errorType: 'validation' | 'network' | 'pharmacy_reject' | 'dea_validation' | 'other';
  errorCode: string;
  errorMessage: string;
  resolved: boolean;
  resolvedAt?: string;
}

interface EPrescribingDetailsProps {
  region: PrescriptionRegion;
}

// Mock data
const mockPendingPrescriptions: EPrescriptionLog[] = [
  {
    id: 'ep1',
    prescriptionId: 'RX001',
    patientName: 'Sarah Johnson',
    medicationName: 'Sertraline 50mg',
    pharmacyName: 'CVS Pharmacy #1234',
    status: 'pending',
    sentAt: '2024-12-15T10:30:00Z'
  },
  {
    id: 'ep2',
    prescriptionId: 'RX002',
    patientName: 'Michael Chen',
    medicationName: 'Bupropion 150mg',
    pharmacyName: 'Walgreens #5678',
    status: 'pending',
    sentAt: '2024-12-15T09:15:00Z'
  },
];

const mockEPrescriptionLogs: EPrescriptionLog[] = [
  ...mockPendingPrescriptions,
  {
    id: 'ep3',
    prescriptionId: 'RX003',
    patientName: 'Emily Rodriguez',
    medicationName: 'Alprazolam 0.5mg',
    pharmacyName: 'Rite Aid #9012',
    status: 'delivered',
    sentAt: '2024-12-14T14:20:00Z',
    deliveredAt: '2024-12-14T14:25:00Z',
    transactionId: 'TXN-123456789'
  },
  {
    id: 'ep4',
    prescriptionId: 'RX004',
    patientName: 'John Smith',
    medicationName: 'Lithium 300mg',
    pharmacyName: 'CVS Pharmacy #1234',
    status: 'rejected',
    sentAt: '2024-12-13T11:00:00Z',
    rejectedAt: '2024-12-13T11:05:00Z',
    rejectionReason: 'Pharmacy not accepting new prescriptions',
    errorCode: 'PHARM_REJECT_001'
  },
];

const mockErrors: EPrescriptionError[] = [
  {
    id: 'err1',
    timestamp: '2024-12-15T10:30:00Z',
    prescriptionId: 'RX001',
    errorType: 'validation',
    errorCode: 'VAL_001',
    errorMessage: 'DEA number validation failed',
    resolved: false
  },
  {
    id: 'err2',
    timestamp: '2024-12-13T11:00:00Z',
    prescriptionId: 'RX004',
    errorType: 'pharmacy_reject',
    errorCode: 'PHARM_REJECT_001',
    errorMessage: 'Pharmacy not accepting new prescriptions',
    resolved: true,
    resolvedAt: '2024-12-13T12:00:00Z'
  },
  {
    id: 'err3',
    timestamp: '2024-12-12T09:00:00Z',
    prescriptionId: 'RX005',
    errorType: 'network',
    errorCode: 'NET_001',
    errorMessage: 'Network timeout during transmission',
    resolved: true,
    resolvedAt: '2024-12-12T09:30:00Z'
  },
];

export default function EPrescribingDetails({ region }: EPrescribingDetailsProps) {
  const [pendingPrescriptions] = React.useState<EPrescriptionLog[]>(mockPendingPrescriptions);
  const [ePrescriptionLogs] = React.useState<EPrescriptionLog[]>(mockEPrescriptionLogs);
  const [errors] = React.useState<EPrescriptionError[]>(mockErrors);
  const [searchTerm, setSearchTerm] = React.useState("");
  const [filterStatus, setFilterStatus] = React.useState<string>('all');

  const filteredLogs = React.useMemo(() => {
    return ePrescriptionLogs.filter(log => {
      const matchesSearch = 
        log.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.medicationName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.pharmacyName.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = filterStatus === 'all' || log.status === filterStatus;
      return matchesSearch && matchesStatus;
    });
  }, [ePrescriptionLogs, searchTerm, filterStatus]);

  const getStatusBadge = (status: EPrescriptionLog['status']) => {
    const badges = {
      'pending': <Badge className="bg-yellow-100 text-yellow-800">Bekliyor</Badge>,
      'sent': <Badge className="bg-blue-100 text-blue-800">Gönderildi</Badge>,
      'delivered': <Badge className="bg-green-100 text-green-800">Teslim Edildi</Badge>,
      'rejected': <Badge className="bg-red-100 text-red-800">Reddedildi</Badge>,
      'cancelled': <Badge className="bg-gray-100 text-gray-800">İptal Edildi</Badge>
    };
    return badges[status];
  };

  const getErrorTypeBadge = (errorType: EPrescriptionError['errorType']) => {
    const badges = {
      'validation': <Badge className="bg-red-100 text-red-800">Doğrulama</Badge>,
      'network': <Badge className="bg-orange-100 text-orange-800">Ağ</Badge>,
      'pharmacy_reject': <Badge className="bg-yellow-100 text-yellow-800">Eczane Reddi</Badge>,
      'dea_validation': <Badge className="bg-purple-100 text-purple-800">DEA Doğrulama</Badge>,
      'other': <Badge className="bg-gray-100 text-gray-800">Diğer</Badge>
    };
    return badges[errorType];
  };

  const stats = React.useMemo(() => {
    return {
      total: ePrescriptionLogs.length,
      pending: ePrescriptionLogs.filter(l => l.status === 'pending').length,
      delivered: ePrescriptionLogs.filter(l => l.status === 'delivered').length,
      rejected: ePrescriptionLogs.filter(l => l.status === 'rejected').length,
      errorRate: ePrescriptionLogs.length > 0 
        ? (errors.filter(e => !e.resolved).length / ePrescriptionLogs.length * 100).toFixed(1)
        : '0'
    };
  }, [ePrescriptionLogs, errors]);

  return (
    <div className="space-y-6">
      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam E-Reçete</p>
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
                <p className="text-sm text-gray-600">Bekleyen</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Teslim Edilen</p>
                <p className="text-2xl font-bold text-green-600">{stats.delivered}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Hata Oranı</p>
                <p className="text-2xl font-bold text-red-600">{stats.errorRate}%</p>
              </div>
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Queue */}
      {pendingPrescriptions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Bekleyen E-Reçeteler ({pendingPrescriptions.length})
            </CardTitle>
            <CardDescription>
              Eczaneye gönderilmeyi bekleyen reçeteler
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pendingPrescriptions.map((prescription) => (
                <div key={prescription.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold">{prescription.patientName}</span>
                        <span className="text-gray-500">-</span>
                        <span>{prescription.medicationName}</span>
                        {getStatusBadge(prescription.status)}
                      </div>
                      <div className="text-sm text-gray-600">
                        <div>Eczane: {prescription.pharmacyName}</div>
                        {prescription.sentAt && (
                          <div>Gönderim: {new Date(prescription.sentAt).toLocaleString('tr-TR')}</div>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4 mr-1" />
                        Yeniden Dene
                      </Button>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        Detaylar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Breakdown */}
      {errors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Hata Detayları ({errors.filter(e => !e.resolved).length} Çözülmemiş)
            </CardTitle>
            <CardDescription>
              E-reçete gönderim hataları ve çözüm durumları
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {errors.map((error) => (
                <div key={error.id} className={`p-4 border rounded-lg ${
                  !error.resolved ? 'bg-red-50 border-red-200' : 'bg-gray-50'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getErrorTypeBadge(error.errorType)}
                        <Badge variant="outline">{error.errorCode}</Badge>
                        {error.resolved && (
                          <Badge className="bg-green-100 text-green-800">Çözüldü</Badge>
                        )}
                      </div>
                      <p className="text-sm font-medium mb-1">{error.errorMessage}</p>
                      <div className="text-xs text-gray-600">
                        <div>Reçete ID: {error.prescriptionId}</div>
                        <div>Zaman: {new Date(error.timestamp).toLocaleString('tr-TR')}</div>
                        {error.resolvedAt && (
                          <div>Çözüm: {new Date(error.resolvedAt).toLocaleString('tr-TR')}</div>
                        )}
                      </div>
                    </div>
                    {!error.resolved && (
                      <Button variant="outline" size="sm">
                        Çözüldü İşaretle
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* E-Prescription Logs */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>E-Reçete Gönderim Geçmişi</CardTitle>
              <CardDescription>
                Tüm e-reçete gönderim kayıtları
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-48"
              />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border rounded-md text-sm"
              >
                <option value="all">Tüm Durumlar</option>
                <option value="pending">Bekliyor</option>
                <option value="sent">Gönderildi</option>
                <option value="delivered">Teslim Edildi</option>
                <option value="rejected">Reddedildi</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tarih</TableHead>
                  <TableHead>Hasta</TableHead>
                  <TableHead>İlaç</TableHead>
                  <TableHead>Eczane</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Transaction ID</TableHead>
                  <TableHead>Hata</TableHead>
                  <TableHead>Aksiyonlar</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      <div className="text-sm">
                        {log.sentAt ? new Date(log.sentAt).toLocaleDateString('tr-TR') : '-'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {log.sentAt ? new Date(log.sentAt).toLocaleTimeString('tr-TR') : '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-gray-400" />
                        <span className="text-sm">{log.patientName}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{log.medicationName}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-gray-600">{log.pharmacyName}</span>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(log.status)}
                    </TableCell>
                    <TableCell>
                      {log.transactionId ? (
                        <span className="text-xs font-mono text-gray-600">{log.transactionId}</span>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {log.errorCode ? (
                        <div>
                          <Badge variant="outline" className="text-xs text-red-600">
                            {log.errorCode}
                          </Badge>
                          {log.rejectionReason && (
                            <div className="text-xs text-gray-600 mt-1">{log.rejectionReason}</div>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {log.status === 'pending' && (
                          <Button variant="ghost" size="sm">
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

