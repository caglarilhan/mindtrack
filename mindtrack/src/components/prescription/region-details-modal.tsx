"use client";

import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { REGION_CONFIG } from "@/lib/prescription/region-config";
import { RegionId } from "@/lib/prescription/types";

interface Props {
  region: RegionId;
  open: boolean;
  onClose: () => void;
}

export function RegionDetailsModal({ region, open, onClose }: Props) {
  const cfg = REGION_CONFIG[region];

  const regionInfo: Record<RegionId, string[]> = {
    TR: [
      "Otorite: TİTCK",
      "Kırmızı/yeşil reçete süreçleri ileride eklenecek.",
      "E-Nabız entegrasyonu Sprint 2+ planında.",
    ],
    US: [
      "Otorite: DEA",
      "Schedule II/III/IV kontrollü maddeler takip edilecek.",
      "EPCS (Electronic Prescribing of Controlled Substances) gereksinimleri Sprint 3’te ele alınacak.",
    ],
    EU: [
      "Otorite: EMA",
      "ATC sınıfları ve ülke bazlı e-reçete kuralları ileride eklenecek.",
      "GDPR uyumluluğu için veri minimizasyonu ve audit planlı.",
    ],
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{cfg.label} - Bölge Detayları</DialogTitle>
          <DialogDescription>{cfg.authority} hakkında kısa bilgi</DialogDescription>
        </DialogHeader>
        <div className="space-y-2 text-sm text-gray-700">
          <p>{cfg.subtitle}</p>
          <ul className="list-disc list-inside">
            {regionInfo[region].map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
          <p>Bu sprintte bilgilendirme amaçlıdır; detaylı regülasyon kuralları Sprint 3'te eklenecek.</p>
        </div>
      </DialogContent>
    </Dialog>
  );
}


