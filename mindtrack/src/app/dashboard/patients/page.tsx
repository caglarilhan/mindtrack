"use client";

import * as React from "react";
import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  UserPlus, 
  Download, 
  Upload, 
  Filter,
  X,
  Search,
  MoreVertical,
  FileText,
  Calendar,
  MessageSquare,
  Video,
  Plus,
  ChevronLeft,
  ChevronRight,
  User,
  Phone,
  Mail,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye
} from "lucide-react";
import { PatientCreateForm } from "@/components/patients/patient-create-form";
import { useDebounce } from "@/hooks/useDebounce";
import { parseSmartSearch } from "@/lib/utils/smartSearch";
import { ColumnSettings, ColumnConfig, ColumnKey } from "@/components/patients/column-settings";
import { PatientHoverCard } from "@/components/patients/patient-hover-card";
import { ArrowUpDown, ArrowUp, ArrowDown, Brain, Sparkles } from "lucide-react";

interface Patient {
  id: string;
  displayName: string;
  patientId: string;
  age: number | null;
  gender: string | null;
  phone: string | null;
  email: string | null;
  mode: 'full' | 'lite';
  status: string;
  riskLevel: 'low' | 'medium' | 'high';
  primaryDiagnosis: string | null;
  secondaryDiagnoses: string[];
  lastAppointment: {
    date: string;
    type: string;
    duration: number | null;
    therapist: string | null;
  } | null;
  nextAppointment: {
    date: string;
    type: string;
    telehealthLink: string | null;
    therapist: string | null;
  } | null;
  portalStatus: 'active' | 'invited' | 'never_opened';
  portalLastLogin: string | null;
}

export default function PatientsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatients, setSelectedPatients] = useState<Set<string>>(new Set());
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [hoveredPatientId, setHoveredPatientId] = useState<string | null>(null);
  const [hoverPosition, setHoverPosition] = useState<{ x: number; y: number } | null>(null);
  const [aiInsights, setAiInsights] = useState<any[]>([]);
  
  // Filters
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || 'all');
  const [riskFilter, setRiskFilter] = useState(searchParams.get('riskLevel') || 'all');
  const [portalFilter, setPortalFilter] = useState(searchParams.get('portalStatus') || 'all');
  const [diagnosisFilter, setDiagnosisFilter] = useState(searchParams.get('diagnosis') || '');
  const [genderFilter, setGenderFilter] = useState(searchParams.get('gender') || 'all');
  const [ageRangeFilter, setAgeRangeFilter] = useState(searchParams.get('ageRange') || 'all');
  const [therapistFilter, setTherapistFilter] = useState(searchParams.get('therapistId') || 'all');
  const [lastVisitFrom, setLastVisitFrom] = useState(searchParams.get('lastVisitFrom') || '');
  const [lastVisitTo, setLastVisitTo] = useState(searchParams.get('lastVisitTo') || '');
  const [therapists, setTherapists] = useState<Array<{ id: string; name: string }>>([]);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSaveFilterModal, setShowSaveFilterModal] = useState(false);
  const [savedFilterName, setSavedFilterName] = useState('');
  
  // Sorting
  const [sortColumn, setSortColumn] = useState<string | null>(searchParams.get('sort') || null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(searchParams.get('dir') === 'desc' ? 'desc' : 'asc');
  
  // Columns
  const [columns, setColumns] = useState<ColumnConfig[]>([
    { key: 'patient', label: 'Hasta', visible: true, sortable: true, order: 0 },
    { key: 'diagnosis', label: 'Tanı', visible: true, sortable: false, order: 1 },
    { key: 'status', label: 'Durum', visible: true, sortable: true, order: 2 },
    { key: 'risk', label: 'Risk', visible: true, sortable: true, order: 3 },
    { key: 'lastAppointment', label: 'Son Görüşme', visible: true, sortable: true, order: 4 },
    { key: 'nextAppointment', label: 'Sonraki Randevu', visible: true, sortable: true, order: 5 },
    { key: 'portal', label: 'Portal', visible: true, sortable: false, order: 6 },
    { key: 'age', label: 'Yaş/Cinsiyet', visible: false, sortable: true, order: 7 },
    { key: 'therapist', label: 'Terapist', visible: false, sortable: true, order: 8 },
    { key: 'insurance', label: 'Sigorta', visible: false, sortable: false, order: 9 },
  ]);
  
  // Pagination
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1'));
  const [pageSize, setPageSize] = useState(parseInt(searchParams.get('pageSize') || '25'));
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const debouncedSearch = useDebounce(search, 300);

  // Smart search handler
  useEffect(() => {
    if (debouncedSearch) {
      const smartResult = parseSmartSearch(debouncedSearch);
      if (smartResult.filters?.riskLevel) {
        setRiskFilter(smartResult.filters.riskLevel);
      }
      if (smartResult.filters?.diagnosis) {
        setDiagnosisFilter(smartResult.filters.diagnosis);
      }
    }
  }, [debouncedSearch]);

  // Fetch AI insights
  useEffect(() => {
    const fetchInsights = async () => {
      try {
        // Mock AI insights - gerçek implementasyonda AI servisi çağrılacak
        const insights = [
          { type: 'care_gap', message: '3 hasta son 45 gündür görüşmemiş', count: 3, severity: 'medium' },
          { type: 'high_risk', message: '1 hastada yüksek risk notu var', count: 1, severity: 'high' },
        ];
        setAiInsights(insights);
      } catch (error) {
        console.error('Error fetching AI insights:', error);
      }
    };
    if (patients.length > 0) {
      fetchInsights();
    }
  }, [patients.length]);

  const fetchPatients = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (debouncedSearch) {
        const smartResult = parseSmartSearch(debouncedSearch);
        params.set('search', smartResult.value);
      }
      if (statusFilter !== 'all') params.set('status', statusFilter);
      if (riskFilter !== 'all') params.set('riskLevel', riskFilter);
      if (portalFilter !== 'all') params.set('portalStatus', portalFilter);
      if (diagnosisFilter) params.set('diagnosis', diagnosisFilter);
      if (genderFilter !== 'all') params.set('gender', genderFilter);
      if (ageRangeFilter !== 'all') params.set('ageRange', ageRangeFilter);
      if (therapistFilter !== 'all') params.set('therapistId', therapistFilter);
      if (lastVisitFrom) params.set('lastVisitFrom', lastVisitFrom);
      if (lastVisitTo) params.set('lastVisitTo', lastVisitTo);
      if (sortColumn) {
        params.set('sort', sortColumn);
        params.set('dir', sortDirection);
      }
      params.set('page', page.toString());
      params.set('pageSize', pageSize.toString());

      const res = await fetch(`/api/patients/list?${params.toString()}`);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        let errorMessage = errorData.error || `Hasta listesi alınamadı: ${res.status} ${res.statusText}`;
        
        // 401 Unauthorized durumunda - test modunda devam et
        if (res.status === 401) {
          console.warn('[PatientsPage] 401 Unauthorized, but continuing in test mode');
          // Test modunda boş liste göster
          setPatients([]);
          setTotal(0);
          setTotalPages(0);
          setError(null);
          return;
        }
        
        // 403 Forbidden durumunda daha açıklayıcı mesaj
        if (res.status === 403) {
          errorMessage = errorData.error || 'Bu sayfaya erişim yetkiniz bulunmuyor. Lütfen yöneticinizle iletişime geçin.';
        }
        
        setError(errorMessage);
        // Hata mesajını throw etme, sadece state'e kaydet
        return;
      }
      const data = await res.json();
      
      setPatients(data.patients || []);
      setTotal(data.pagination?.total || 0);
      setTotalPages(data.pagination?.totalPages || 0);
      setError(null);

      // Update URL
      router.replace(`/dashboard/patients?${params.toString()}`, { scroll: false });
    } catch (error: any) {
      console.error('Error fetching patients:', error);
      // Error mesajı zaten setError ile ayarlandı, sadece loglama yapıyoruz
      if (!error?.message) {
        setError('Hasta listesi yüklenirken bir hata oluştu.');
      }
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, statusFilter, riskFilter, portalFilter, diagnosisFilter, genderFilter, ageRangeFilter, therapistFilter, lastVisitFrom, lastVisitTo, sortColumn, sortDirection, page, pageSize, router]);

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
    setPage(1);
  };

  const getRowClassName = (patient: Patient) => {
    const classes: string[] = [];
    
    // High risk highlight
    if (patient.riskLevel === 'high') {
      classes.push('bg-red-50');
    }
    
    // Care gap (no appointment in last 30 days)
    if (patient.lastAppointment) {
      const lastVisit = new Date(patient.lastAppointment.date);
      const daysSince = Math.floor((Date.now() - lastVisit.getTime()) / (1000 * 60 * 60 * 24));
      if (daysSince > 30) {
        classes.push('bg-yellow-50');
      }
    } else {
      classes.push('bg-yellow-50');
    }
    
    // Today's appointment
    if (patient.nextAppointment) {
      const nextDate = new Date(patient.nextAppointment.date);
      const today = new Date();
      if (nextDate.toDateString() === today.toDateString()) {
        classes.push('bg-blue-50');
      }
    }
    
    // Portal never opened
    if (patient.portalStatus === 'never_opened') {
      classes.push('opacity-75');
    }
    
    return classes.join(' ');
  };

  const handleBulkAction = async (action: string) => {
    if (selectedPatients.size === 0) return;
    
    const patientIds = Array.from(selectedPatients);
    
    switch (action) {
      case 'invite_portal':
        // TODO: Send portal invitations
        alert(`${patientIds.length} hastaya portal daveti gönderilecek`);
        break;
      case 'deactivate':
        // TODO: Deactivate patients
        alert(`${patientIds.length} hasta pasifleştirilecek`);
        break;
      case 'export':
        // TODO: Export patients
        alert(`${patientIds.length} hasta export edilecek`);
        break;
      case 'assign_therapist':
        // TODO: Assign therapist
        alert(`${patientIds.length} hastaya terapist atanacak`);
        break;
    }
    
    setSelectedPatients(new Set());
  };

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  // Fetch therapists for filter
  useEffect(() => {
    const fetchTherapists = async () => {
      try {
        // TODO: Replace with actual API call
        const mockTherapists = [
          { id: 't1', name: 'Dr. Ayşe Yılmaz' },
          { id: 't2', name: 'Dr. Mehmet Demir' },
          { id: 't3', name: 'Uzm. Psk. Zeynep Kaya' },
        ];
        setTherapists(mockTherapists);
      } catch (error) {
        console.error('Error fetching therapists:', error);
      }
    };
    fetchTherapists();
  }, []);

  const clearFilters = () => {
    setSearch('');
    setStatusFilter('all');
    setRiskFilter('all');
    setPortalFilter('all');
    setDiagnosisFilter('');
    setGenderFilter('all');
    setAgeRangeFilter('all');
    setTherapistFilter('all');
    setLastVisitFrom('');
    setLastVisitTo('');
    setPage(1);
  };

  const togglePatientSelection = (patientId: string) => {
    const newSelected = new Set(selectedPatients);
    if (newSelected.has(patientId)) {
      newSelected.delete(patientId);
    } else {
      newSelected.add(patientId);
    }
    setSelectedPatients(newSelected);
  };

  const toggleAllSelection = () => {
    if (selectedPatients.size === patients.length) {
      setSelectedPatients(new Set());
    } else {
      setSelectedPatients(new Set(patients.map(p => p.id)));
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatRelativeDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHours === 0) {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return `${diffMins} dakika önce`;
      }
      return `${diffHours} saat önce`;
    } else if (diffDays === 1) {
      return 'Dün';
    } else if (diffDays < 7) {
      return `${diffDays} gün önce`;
    } else {
      return formatDate(dateString);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; label: string; className: string }> = {
      active: { variant: 'default', label: 'Aktif', className: 'bg-green-100 text-green-800 border-green-300' },
      inactive: { variant: 'secondary', label: 'Pasif', className: 'bg-gray-100 text-gray-800 border-gray-300' },
      pending: { variant: 'default', label: 'Beklemede', className: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
      evaluation: { variant: 'default', label: 'Değerlendirme', className: 'bg-blue-100 text-blue-800 border-blue-300' }
    };
    const config = variants[status] || variants.active;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getRiskBadge = (risk: string) => {
    const variants: Record<string, { label: string; className: string }> = {
      high: { label: 'Yüksek', className: 'bg-red-100 text-red-800 border-red-300' },
      medium: { label: 'Orta', className: 'bg-orange-100 text-orange-800 border-orange-300' },
      low: { label: 'Düşük', className: 'bg-green-100 text-green-800 border-green-300' }
    };
    const config = variants[risk] || variants.low;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getPortalBadge = (status: string, lastLogin: string | null) => {
    if (status === 'active' && lastLogin) {
      return (
        <div className="flex flex-col gap-1">
          <Badge className="bg-green-100 text-green-800 border-green-300">Aktif</Badge>
          <span className="text-xs text-gray-500">Son giriş: {formatRelativeDate(lastLogin)}</span>
        </div>
      );
    } else if (status === 'invited') {
      return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300">Davet Bekliyor</Badge>;
    } else {
      return <Badge className="bg-gray-100 text-gray-800 border-gray-300">Hiç Açmadı</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">
                Hastalar ({total})
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Tüm hastalarınızı yönetin, filtreleyin ve hızlı aksiyon alın.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                title="CSV veya Excel dosyasından hasta içe aktar"
              >
                <Upload className="h-4 w-4 mr-2" />
                İçeri Aktar (CSV/Excel)
              </Button>
              <div className="relative">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  title="Hasta listesini CSV, PDF veya Excel formatında dışa aktar"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Dışa Aktar
                </Button>
                {showExportMenu && (
                  <>
                    <div className="absolute right-0 top-full mt-1 bg-white border rounded-lg shadow-lg p-2 z-50 min-w-[200px]">
                      <button 
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded text-sm"
                        onClick={() => {
                          // TODO: Export CSV
                          alert('CSV export başlatılıyor...');
                          setShowExportMenu(false);
                        }}
                      >
                        CSV olarak indir
                      </button>
                      <button 
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded text-sm"
                        onClick={() => {
                          // TODO: Export PDF
                          alert('PDF export başlatılıyor...');
                          setShowExportMenu(false);
                        }}
                      >
                        PDF olarak indir
                      </button>
                      <button 
                        className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded text-sm"
                        onClick={() => {
                          // TODO: Export Excel
                          alert('Excel export başlatılıyor...');
                          setShowExportMenu(false);
                        }}
                      >
                        Excel olarak indir
                      </button>
                    </div>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setShowExportMenu(false)}
                    />
                  </>
                )}
              </div>
              <div className="relative flex items-center gap-2">
                <select 
                  className="px-3 py-2 border rounded-md text-sm"
                  onChange={(e) => {
                    if (e.target.value && e.target.value !== 'default') {
                      // TODO: Load saved filter
                      console.log('Loading filter:', e.target.value);
                    }
                  }}
                >
                  <option value="default">Kaydedilmiş Filtreler</option>
                  <option value="high-risk">Yüksek Risk</option>
                  <option value="portal-inactive">Portal Pasif</option>
                  <option value="no-visit-30">Son 30 günde görüşülmeyenler</option>
                </select>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowSaveFilterModal(true)}
                  title="Mevcut filtreleri yeni segment olarak kaydet"
                >
                  <Filter className="h-4 w-4 mr-1" />
                  Kaydet
                </Button>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                title="Bu sayfadaki filtreye göre hasta listesi raporu ve analitikler üretir"
              >
                <FileText className="h-4 w-4 mr-2" />
                Hasta Liste Raporları
              </Button>
              <Button onClick={() => setShowCreateForm(true)}>
                <UserPlus className="h-4 w-4 mr-2" />
                Yeni Hasta Ekle
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* AI Insights Panel */}
      {aiInsights.length > 0 && (
        <div className="max-w-7xl mx-auto px-6 py-2">
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="pt-4 pb-4">
              <div className="flex items-start gap-3">
                <Brain className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <div className="font-semibold text-sm text-blue-900 mb-2">
                    AI Öngörüleri
                  </div>
                  <div className="space-y-1">
                    {aiInsights.map((insight, idx) => (
                      <div key={idx} className="text-sm text-blue-800">
                        • {insight.message}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filter Panel */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <Card>
          <CardContent className="pt-6">
            {/* First Row: Search and Primary Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
              <div className="lg:col-span-2">
                <label htmlFor="general-search" className="text-xs text-gray-500 mb-1 block">Genel Arama</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="general-search"
                    type="text"
                    placeholder="İsim, ID, email veya telefon ile ara"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="pl-10"
                    title="Akıllı arama: ID (P-XXXX), telefon (+90...), email (@...), tanı kodu (F32.1), risk seviyesi (yüksek risk)"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="status-filter" className="text-xs text-gray-500 mb-1 block">Durum</label>
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="all">Tüm Durumlar</option>
                  <option value="active">Aktif</option>
                  <option value="inactive">Pasif</option>
                  <option value="pending">Beklemede</option>
                  <option value="evaluation">Değerlendirme</option>
                </select>
              </div>
              <div>
                <label htmlFor="risk-filter" className="text-xs text-gray-500 mb-1 block">Risk</label>
                <select
                  id="risk-filter"
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="all">Tüm Risk Seviyeleri</option>
                  <option value="low">Düşük</option>
                  <option value="medium">Orta</option>
                  <option value="high">Yüksek</option>
                </select>
              </div>
              <div>
                <label htmlFor="portal-filter" className="text-xs text-gray-500 mb-1 block">Portal</label>
                <select
                  id="portal-filter"
                  value={portalFilter}
                  onChange={(e) => setPortalFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="all">Tüm Portal Durumları</option>
                  <option value="active">Aktif</option>
                  <option value="invited">Davet Bekliyor</option>
                  <option value="never_opened">Hiç Açmadı</option>
                </select>
              </div>
            </div>

            {/* Second Row: Secondary Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="lg:col-span-2">
                <label htmlFor="diagnosis-filter" className="text-xs text-gray-500 mb-1 block">Tanı (DSM-5) Ara</label>
                <Input
                  id="diagnosis-filter"
                  placeholder="Örnek: F33.1, Major Depresyon, GAD"
                  value={diagnosisFilter}
                  onChange={(e) => setDiagnosisFilter(e.target.value)}
                  title="DSM-5 tanı kodu (örn: F32.1) veya tanı adı ile ara"
                />
              </div>
              <div>
                <label htmlFor="therapist-filter" className="text-xs text-gray-500 mb-1 block">Terapist</label>
                <select
                  id="therapist-filter"
                  value={therapistFilter}
                  onChange={(e) => setTherapistFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  title="Atanan terapist/psikiyatriste göre filtrele"
                >
                  <option value="all">Tüm Terapistler</option>
                  {therapists.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="gender-filter" className="text-xs text-gray-500 mb-1 block">Cinsiyet</label>
                <select
                  id="gender-filter"
                  value={genderFilter}
                  onChange={(e) => setGenderFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="all">Tüm Cinsiyetler</option>
                  <option value="male">Erkek</option>
                  <option value="female">Kadın</option>
                  <option value="other">Diğer</option>
                </select>
              </div>
              <div>
                <label htmlFor="age-filter" className="text-xs text-gray-500 mb-1 block">Yaş Aralığı</label>
                <select
                  id="age-filter"
                  value={ageRangeFilter}
                  onChange={(e) => setAgeRangeFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="all">Tüm Yaşlar</option>
                  <option value="0-18">0-18</option>
                  <option value="19-25">19-25</option>
                  <option value="26-35">26-35</option>
                  <option value="36-45">36-45</option>
                  <option value="46-55">46-55</option>
                  <option value="56-65">56-65</option>
                  <option value="65+">65+</option>
                </select>
              </div>
              <div className="lg:col-span-2">
                <label htmlFor="last-visit-from" className="text-xs text-gray-500 mb-1 block">Son Görüşme Tarihi</label>
                <div className="flex items-center gap-2">
                  <div className="flex-1">
                    <label htmlFor="last-visit-from" className="sr-only">Son Görüşme Başlangıç</label>
                    <Input
                      id="last-visit-from"
                      type="date"
                      value={lastVisitFrom}
                      onChange={(e) => setLastVisitFrom(e.target.value)}
                      className="text-sm"
                      placeholder="Başlangıç"
                      aria-label="Son görüşme başlangıç tarihi"
                    />
                  </div>
                  <span className="text-gray-400 text-sm">-</span>
                  <div className="flex-1">
                    <label htmlFor="last-visit-to" className="sr-only">Son Görüşme Bitiş</label>
                    <Input
                      id="last-visit-to"
                      type="date"
                      value={lastVisitTo}
                      onChange={(e) => setLastVisitTo(e.target.value)}
                      className="text-sm"
                      placeholder="Bitiş"
                      aria-label="Son görüşme bitiş tarihi"
                    />
                  </div>
                </div>
              </div>
              <div className="lg:col-span-3 flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={clearFilters}>
                  <X className="h-4 w-4 mr-2" />
                  Filtreleri Temizle
                </Button>
                <span className="text-sm text-gray-500">
                  {total} hasta bulundu
                  {(statusFilter !== 'all' || riskFilter !== 'all' || portalFilter !== 'all' || diagnosisFilter || genderFilter !== 'all' || ageRangeFilter !== 'all' || therapistFilter !== 'all' || lastVisitFrom || lastVisitTo) && (
                    <span className="ml-2 text-xs">
                      (Durum: {statusFilter === 'all' ? 'Tüm' : statusFilter}, 
                      Risk: {riskFilter === 'all' ? 'Tüm' : riskFilter}, 
                      Portal: {portalFilter === 'all' ? 'Tüm' : portalFilter})
                    </span>
                  )}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bulk Actions Bar */}
      {selectedPatients.size > 0 && (
        <div className="max-w-7xl mx-auto px-6 py-2">
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="pt-3 pb-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  {selectedPatients.size} hasta seçildi
                </span>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={() => handleBulkAction('invite_portal')}>
                    Portal Daveti Gönder
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleBulkAction('assign_therapist')}>
                    Terapist Ata
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleBulkAction('deactivate')}>
                    Pasifleştir
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleBulkAction('export')}>
                    Export
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => setSelectedPatients(new Set())}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="max-w-7xl mx-auto px-6 py-4">
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-4 pb-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                <div className="flex-1">
                  <div className="font-semibold text-sm text-red-900 mb-1">
                    Hata
                  </div>
                  <div className="text-sm text-red-800">
                    {error}
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="mt-3"
                    onClick={() => {
                      setError(null);
                      fetchPatients();
                    }}
                  >
                    Tekrar Dene
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Table */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        {loading ? (
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-16 bg-gray-200 animate-pulse rounded" />
                ))}
              </div>
            </CardContent>
          </Card>
        ) : patients.length === 0 ? (
          <>
            {/* Show table structure even when empty */}
            <Card>
              <CardContent className="p-0">
              <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center gap-2">
                  <ColumnSettings columns={columns} onColumnsChange={setColumns} />
                </div>
              </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-4 py-3 text-left sticky left-0 bg-gray-50 z-20">
                          <input type="checkbox" disabled className="rounded" />
                        </th>
                        {columns.find(c => c.key === 'patient')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 sticky left-10 bg-gray-50 z-20">Hasta</th>
                        )}
                        {columns.find(c => c.key === 'diagnosis')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Tanı</th>
                        )}
                        {columns.find(c => c.key === 'status')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Durum</th>
                        )}
                        {columns.find(c => c.key === 'risk')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Risk</th>
                        )}
                        {columns.find(c => c.key === 'lastAppointment')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Son Görüşme</th>
                        )}
                        {columns.find(c => c.key === 'nextAppointment')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Sonraki Randevu</th>
                        )}
                        {columns.find(c => c.key === 'portal')?.visible && (
                          <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Portal</th>
                        )}
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Aksiyonlar</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td colSpan={9} className="px-4 py-16 text-center">
                          <div className="flex flex-col items-center gap-4">
                            <User className="h-16 w-16 text-gray-300" />
                            <div>
                              <h3 className="text-lg font-semibold mb-2">
                                {search || statusFilter !== 'all' || riskFilter !== 'all' || therapistFilter !== 'all'
                                  ? 'Seçili filtrelere uygun hasta bulunamadı.'
                                  : 'Henüz hasta eklenmedi.'}
                              </h3>
                              <p className="text-gray-500 mb-4">
                                {search || statusFilter !== 'all' || riskFilter !== 'all' || therapistFilter !== 'all'
                                  ? 'Filtreleri temizleyip tekrar deneyin.'
                                  : 'İlk hastanızı hemen ekleyin veya CSV dosyasından içe aktarın.'}
                              </p>
                              <div className="flex items-center gap-3 justify-center">
                                {search || statusFilter !== 'all' || riskFilter !== 'all' || therapistFilter !== 'all' ? (
                                  <Button variant="outline" onClick={clearFilters}>
                                    Filtreleri Temizle
                                  </Button>
                                ) : (
                                  <>
                                    <Button onClick={() => setShowCreateForm(true)} size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
                                      <UserPlus className="h-4 w-4 mr-2" />
                                      Yeni Hasta Ekle
                                    </Button>
                                    <Button 
                                      variant="outline" 
                                      onClick={() => {
                                        // TODO: Download sample CSV
                                        alert('Örnek CSV dosyası indirilecek');
                                      }}
                                      size="lg"
                                      title="Kolon yapısını görmek için örnek CSV indirebilirsiniz"
                                    >
                                      <Download className="h-4 w-4 mr-2" />
                                      Örnek CSV İndir
                                    </Button>
                                  </>
                                )}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="p-0">
              <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center gap-2">
                  <ColumnSettings columns={columns} onColumnsChange={setColumns} />
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b sticky top-0 z-10">
                    <tr>
                      <th className="px-4 py-3 text-left sticky left-0 bg-gray-50 z-20">
                        <input
                          type="checkbox"
                          checked={selectedPatients.size === patients.length && patients.length > 0}
                          onChange={toggleAllSelection}
                          className="rounded"
                        />
                      </th>
                      {columns.find(c => c.key === 'patient')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 sticky left-10 bg-gray-50 z-20">
                          <button
                            onClick={() => handleSort('displayName')}
                            className="flex items-center gap-1 hover:text-gray-900"
                          >
                            Hasta
                            {sortColumn === 'displayName' ? (
                              sortDirection === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                            ) : (
                              <ArrowUpDown className="h-3 w-3 opacity-30" />
                            )}
                          </button>
                        </th>
                      )}
                      {columns.find(c => c.key === 'diagnosis')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Tanı</th>
                      )}
                      {columns.find(c => c.key === 'status')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                          <button
                            onClick={() => handleSort('status')}
                            className="flex items-center gap-1 hover:text-gray-900"
                          >
                            Durum
                            {sortColumn === 'status' ? (
                              sortDirection === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                            ) : (
                              <ArrowUpDown className="h-3 w-3 opacity-30" />
                            )}
                          </button>
                        </th>
                      )}
                      {columns.find(c => c.key === 'risk')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                          <button
                            onClick={() => handleSort('riskLevel')}
                            className="flex items-center gap-1 hover:text-gray-900"
                          >
                            Risk
                            {sortColumn === 'riskLevel' ? (
                              sortDirection === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                            ) : (
                              <ArrowUpDown className="h-3 w-3 opacity-30" />
                            )}
                          </button>
                        </th>
                      )}
                      {columns.find(c => c.key === 'lastAppointment')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                          <button
                            onClick={() => handleSort('lastAppointment')}
                            className="flex items-center gap-1 hover:text-gray-900"
                          >
                            Son Görüşme
                            {sortColumn === 'lastAppointment' ? (
                              sortDirection === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                            ) : (
                              <ArrowUpDown className="h-3 w-3 opacity-30" />
                            )}
                          </button>
                        </th>
                      )}
                      {columns.find(c => c.key === 'nextAppointment')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                          <button
                            onClick={() => handleSort('nextAppointment')}
                            className="flex items-center gap-1 hover:text-gray-900"
                          >
                            Sonraki Randevu
                            {sortColumn === 'nextAppointment' ? (
                              sortDirection === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                            ) : (
                              <ArrowUpDown className="h-3 w-3 opacity-30" />
                            )}
                          </button>
                        </th>
                      )}
                      {columns.find(c => c.key === 'portal')?.visible && (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Portal</th>
                      )}
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Aksiyonlar</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {patients.map((patient) => (
                      <tr
                        key={patient.id}
                        className={`hover:bg-gray-50 transition-colors cursor-pointer relative ${getRowClassName(patient)}`}
                        onClick={() => router.push(`/dashboard/patients/${patient.id}`)}
                        onMouseEnter={(e) => {
                          setHoveredPatientId(patient.id);
                          const rect = e.currentTarget.getBoundingClientRect();
                          setHoverPosition({ x: rect.right + 10, y: rect.top });
                        }}
                        onMouseLeave={() => {
                          setHoveredPatientId(null);
                          setHoverPosition(null);
                        }}
                      >
                        <td className="px-4 py-4 sticky left-0 bg-inherit z-10" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="checkbox"
                            checked={selectedPatients.has(patient.id)}
                            onChange={() => togglePatientSelection(patient.id)}
                            className="rounded"
                          />
                        </td>
                        {columns.find(c => c.key === 'patient')?.visible && (
                          <td className="px-4 py-4 sticky left-10 bg-inherit z-10">
                            <div className="flex items-center gap-3">
                              <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                <User className="h-5 w-5 text-gray-500" />
                              </div>
                              <div>
                                <div className="font-semibold">{patient.displayName}</div>
                                <div className="text-xs text-gray-500">
                                  {patient.patientId}
                                  {patient.age && ` • ${patient.age}${patient.gender ? patient.gender[0].toUpperCase() : ''}`}
                                  {patient.phone && ` • ${patient.phone}`}
                                  {patient.email && ` • ${patient.email}`}
                                </div>
                              </div>
                            </div>
                          </td>
                        )}
                        {columns.find(c => c.key === 'diagnosis')?.visible && (
                          <td className="px-4 py-4">
                            {patient.primaryDiagnosis ? (
                              <div>
                                <div className="text-sm font-medium">{patient.primaryDiagnosis}</div>
                                {patient.secondaryDiagnoses.length > 0 && (
                                  <div className="text-xs text-gray-500">
                                    Ek tanılar: {patient.secondaryDiagnoses.join(', ')}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <span className="text-gray-400">—</span>
                            )}
                          </td>
                        )}
                        {columns.find(c => c.key === 'status')?.visible && (
                          <td className="px-4 py-4">
                            {getStatusBadge(patient.status)}
                          </td>
                        )}
                        {columns.find(c => c.key === 'risk')?.visible && (
                          <td className="px-4 py-4">
                            <div className="flex items-center gap-2">
                              {getRiskBadge(patient.riskLevel)}
                              {patient.riskLevel === 'high' && (
                                <AlertTriangle className="h-4 w-4 text-red-600" title="Yüksek risk uyarısı" />
                              )}
                            </div>
                          </td>
                        )}
                        {columns.find(c => c.key === 'lastAppointment')?.visible && (
                          <td className="px-4 py-4">
                            {patient.lastAppointment ? (
                              <div>
                                <div className="text-sm">{formatDate(patient.lastAppointment.date)}</div>
                                <div className="text-xs text-gray-500">
                                  {patient.lastAppointment.type} / {patient.lastAppointment.duration || 45} dk
                                  {patient.lastAppointment.therapist && ` • ${patient.lastAppointment.therapist}`}
                                </div>
                              </div>
                            ) : (
                              <span className="text-gray-400">—</span>
                            )}
                          </td>
                        )}
                        {columns.find(c => c.key === 'nextAppointment')?.visible && (
                          <td className="px-4 py-4">
                            {patient.nextAppointment ? (
                              <div>
                                <div className="text-sm">{formatDate(patient.nextAppointment.date)}</div>
                                <div className="text-xs text-gray-500">
                                  {patient.nextAppointment.type === 'telehealth' ? 'Online' : 'Klinik ziyaret'}
                                  {patient.nextAppointment.therapist && ` • ${patient.nextAppointment.therapist}`}
                                </div>
                              </div>
                            ) : (
                              <span className="text-gray-400">—</span>
                            )}
                          </td>
                        )}
                        {columns.find(c => c.key === 'portal')?.visible && (
                          <td className="px-4 py-4">
                            {getPortalBadge(patient.portalStatus, patient.portalLastLogin)}
                          </td>
                        )}
                        <td className="px-4 py-4" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center gap-1">
                            <Button variant="ghost" size="sm" onClick={() => router.push(`/dashboard/patients/${patient.id}`)}>
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <FileText className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Calendar className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Video className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <MessageSquare className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pagination */}
        {patients.length > 0 && (
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Sayfa başına:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="px-2 py-1 border rounded text-sm"
              >
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                Toplam {total} hasta • Sayfa {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Hover Preview */}
      {hoveredPatientId && hoverPosition && (
        <div
          className="fixed z-50"
          style={{
            left: `${hoverPosition.x}px`,
            top: `${hoverPosition.y}px`,
            pointerEvents: 'none'
          }}
        >
          {(() => {
            const patient = patients.find(p => p.id === hoveredPatientId);
            return patient ? (
              <PatientHoverCard
                patient={patient}
                onOpen={() => {
                  router.push(`/dashboard/patients/${patient.id}`);
                  setHoveredPatientId(null);
                }}
              />
            ) : null;
          })()}
        </div>
      )}


      {/* Save Filter Modal */}
      {showSaveFilterModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Filtreleri Kaydet</h2>
              <Button variant="ghost" size="sm" onClick={() => {
                setShowSaveFilterModal(false);
                setSavedFilterName('');
              }}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              <div>
                <label htmlFor="filter-name" className="block text-sm font-medium text-gray-700 mb-2">
                  Segment Adı
                </label>
                <Input
                  id="filter-name"
                  placeholder="Örn: Yüksek Risk Hastalar"
                  value={savedFilterName}
                  onChange={(e) => setSavedFilterName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && savedFilterName.trim()) {
                      // TODO: Save filter
                      alert(`"${savedFilterName}" filtresi kaydedilecek`);
                      setShowSaveFilterModal(false);
                      setSavedFilterName('');
                    }
                  }}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Mevcut filtre ayarlarınız bu isimle kaydedilecek
                </p>
              </div>
              <div className="flex items-center gap-2 justify-end">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setShowSaveFilterModal(false);
                    setSavedFilterName('');
                  }}
                >
                  İptal
                </Button>
                <Button 
                  onClick={() => {
                    if (savedFilterName.trim()) {
                      // TODO: Save filter
                      alert(`"${savedFilterName}" filtresi kaydedilecek`);
                      setShowSaveFilterModal(false);
                      setSavedFilterName('');
                    }
                  }}
                  disabled={!savedFilterName.trim()}
                >
                  Kaydet
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Patient Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Yeni Hasta Ekle</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateForm(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <PatientCreateForm
                onSuccess={(patientId) => {
                  setShowCreateForm(false);
                  fetchPatients();
                  router.push(`/dashboard/patients/${patientId}`);
                }}
                onCancel={() => setShowCreateForm(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
