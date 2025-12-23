"use client";

import * as React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { User, Eye, Calendar, AlertTriangle } from "lucide-react";

interface PatientHoverCardProps {
  patient: {
    id: string;
    displayName: string;
    patientId: string;
    age: number | null;
    gender: string | null;
    riskLevel: 'low' | 'medium' | 'high';
    primaryDiagnosis: string | null;
    lastAppointment: {
      date: string;
      type: string;
      therapist: string | null;
    } | null;
    portalStatus: 'active' | 'invited' | 'never_opened';
  };
  onOpen: () => void;
}

export function PatientHoverCard({ patient, onOpen }: PatientHoverCardProps) {
  const getRiskBadge = (risk: string) => {
    const variants: Record<string, { label: string; className: string }> = {
      high: { label: 'Yüksek', className: 'bg-red-100 text-red-800 border-red-300' },
      medium: { label: 'Orta', className: 'bg-orange-100 text-orange-800 border-orange-300' },
      low: { label: 'Düşük', className: 'bg-green-100 text-green-800 border-green-300' }
    };
    const config = variants[risk] || variants.low;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <Card className="w-80 shadow-xl border-2">
      <CardContent className="p-4">
        <div className="flex items-start gap-3 mb-3">
          <div className="h-16 w-16 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
            <User className="h-8 w-8 text-gray-500" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-lg truncate">{patient.displayName}</div>
            <div className="text-xs text-gray-500">{patient.patientId}</div>
            <div className="text-sm text-gray-600 mt-1">
              {patient.age && `${patient.age} yaş`}
              {patient.gender && ` • ${patient.gender === 'male' ? 'Erkek' : patient.gender === 'female' ? 'Kadın' : 'Diğer'}`}
            </div>
          </div>
        </div>

        <div className="space-y-2 mb-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Risk Seviyesi</span>
            {getRiskBadge(patient.riskLevel)}
          </div>
          
          {patient.primaryDiagnosis && (
            <div>
              <span className="text-xs text-gray-500">Tanı:</span>
              <div className="text-sm font-medium mt-0.5">{patient.primaryDiagnosis}</div>
            </div>
          )}

          {patient.lastAppointment && (
            <div>
              <span className="text-xs text-gray-500">Son Görüşme:</span>
              <div className="text-sm mt-0.5">
                {formatDate(patient.lastAppointment.date)}
                {patient.lastAppointment.therapist && (
                  <span className="text-gray-500"> • {patient.lastAppointment.therapist}</span>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Portal:</span>
            <Badge className={
              patient.portalStatus === 'active' ? 'bg-green-100 text-green-800' :
              patient.portalStatus === 'invited' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }>
              {patient.portalStatus === 'active' ? 'Aktif' :
               patient.portalStatus === 'invited' ? 'Davet Bekliyor' :
               'Hiç Açmadı'}
            </Badge>
          </div>
        </div>

        <Button
          onClick={onOpen}
          className="w-full"
          size="sm"
        >
          <Eye className="h-4 w-4 mr-2" />
          Hasta Kartını Aç
        </Button>
      </CardContent>
    </Card>
  );
}










