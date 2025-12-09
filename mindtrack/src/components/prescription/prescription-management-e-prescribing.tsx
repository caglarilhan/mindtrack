"use client";

import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { REGION_CONFIG } from "@/lib/prescription/region-config";
import { mockPrescriptions } from "@/lib/prescription/mock-data";
import { Prescription, RegionId } from "@/lib/prescription/types";
import { PrescriptionTabs } from "./prescription-tabs";
import { OverviewTab } from "./overview-tab";
import { PrescriptionsTab } from "./prescriptions-tab";
import { ErxTab } from "./erx-tab";
import { PrescriptionDetailModal } from "./prescription-detail-modal";
import { RegionDetailsModal } from "./region-details-modal";
import { CompliancePanel } from "./compliance-panel";
import { DrugInteractionChecker } from "./drug-interaction-checker";
import { mockLabResults } from "@/lib/prescription/lab-types";
import { LabTrackingTab } from "./lab-tracking-tab";
import { SideEffectsTab } from "./side-effects-tab";
import { mockSideEffects } from "@/lib/prescription/side-effects";
import { EPrescribingDetails } from "./e-prescribing-details";
import { getERxRecords, createPendingERx, markERxFailed, markERxSent } from "@/lib/prescription/mock-erx-store";
import { addAuditEntry } from "@/lib/prescription/audit-log";

type ActiveTab = "overview" | "prescriptions" | "erx" | "interactions" | "lab" | "sideEffects" | "compliance";

export default function PrescriptionManagementEprescribing() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [region, setRegion] = useState<RegionId>("TR");
  const [prescriptions, setPrescriptions] = useState<Prescription[]>(mockPrescriptions);
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [showRegionDetails, setShowRegionDetails] = useState(false);
  const [_, forceRerender] = useState(0); // for mock stores
  const erxRecords = getERxRecords();

  const handleAddPrescription = (p: Prescription) => {
    setPrescriptions((prev) => [p, ...prev]);
    addAuditEntry({
      userId: "test@mindtrack.com",
      eventType: "PRESCRIPTION_CREATED",
      prescriptionId: p.id,
      details: `${p.patientName} için yeni reçete`,
    });
    setActiveTab("prescriptions");
  };

  const handleVoidPrescription = (id: string) => {
    setPrescriptions((prev) => prev.map((p) => (p.id === id ? { ...p, status: "voided" } : p)));
    addAuditEntry({
      userId: "test@mindtrack.com",
      eventType: "PRESCRIPTION_VOIDED",
      prescriptionId: id,
      details: `Reçete iptal edildi`,
    });
  };

  const cfg = REGION_CONFIG[region];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">İlaç Reçetesi Yönetimi</h1>
          <p className="text-sm text-gray-600">{cfg.subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={region}
            onChange={(e) => setRegion(e.target.value as RegionId)}
            className="border rounded-md px-3 py-2 text-sm"
          >
            <option value="TR">🇹🇷 Türkiye</option>
            <option value="US">🇺🇸 United States</option>
            <option value="EU">🇪🇺 European Union</option>
          </select>
          <Button onClick={() => setShowRegionDetails(true)} variant="outline">
            Bölge Detayları
          </Button>
          <Button onClick={() => setActiveTab("erx")}>Yeni Reçete</Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <PrescriptionTabs activeTab={activeTab} onChange={setActiveTab} region={region} />
        </CardContent>
      </Card>

      {activeTab === "overview" && (
        <OverviewTab
          prescriptions={prescriptions}
          region={region}
          onMetricClick={(tab) => setActiveTab(tab)}
          onSelectPrescription={(p) => {
            setSelectedPrescription(p);
          }}
        />
      )}

      {activeTab === "prescriptions" && (
        <PrescriptionsTab
          prescriptions={prescriptions}
          onNewPrescriptionClick={() => setActiveTab("erx")}
          onViewPrescription={(id) => {
            const found = prescriptions.find((p) => p.id === id) || null;
            setSelectedPrescription(found);
          }}
          onVoidPrescription={handleVoidPrescription}
        />
      )}

      {activeTab === "erx" && (
        <ErxTab
          region={region}
          onCreatePrescription={(p) => {
            handleAddPrescription(p);
            const pending = createPendingERx(p.id);
            // mock send: 90% success
            setTimeout(() => {
              if (Math.random() < 0.9) {
                markERxSent(pending.id);
                addAuditEntry({
                  userId: "test@mindtrack.com",
                  eventType: "ERX_SENT",
                  prescriptionId: p.id,
                  details: "E-Reçete gönderildi (mock)",
                });
              } else {
                markERxFailed(pending.id, "PHARM_TIMEOUT", "Eczane yanıt vermedi");
                addAuditEntry({
                  userId: "test@mindtrack.com",
                  eventType: "ERX_FAILED",
                  prescriptionId: p.id,
                  details: "E-Reçete gönderimi başarısız (mock)",
                });
              }
              forceRerender((x) => x + 1);
            }, 800);
            setActiveTab("erx");
          }}
        />
      )}

      {activeTab === "compliance" && <CompliancePanel region={region} prescriptions={prescriptions} />}

      {activeTab === "interactions" && (
        <DrugInteractionChecker medications={prescriptions.flatMap((p) => p.medications)} />
      )}

      {activeTab === "lab" && <LabTrackingTab labResults={mockLabResults} />}

      {activeTab === "sideEffects" && <SideEffectsTab sideEffects={mockSideEffects} />}

      {activeTab === "e-prescribing" && <EPrescribingDetails region={region} />}

      <PrescriptionDetailModal
        prescription={selectedPrescription}
        open={!!selectedPrescription}
        onClose={() => setSelectedPrescription(null)}
      />

      <RegionDetailsModal region={region} open={showRegionDetails} onClose={() => setShowRegionDetails(false)} />
    </div>
  );
}
