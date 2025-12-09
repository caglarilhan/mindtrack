"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import React from "react";

type TabKey = "overview" | "prescriptions" | "erx" | "interactions" | "lab" | "sideEffects" | "compliance";

interface Props {
  activeTab: TabKey;
  onChange: (tab: TabKey) => void;
  region: string;
}

export function PrescriptionTabs({ activeTab, onChange }: Props) {
  const disabledKeys = ["lab", "sideEffects", "compliance"] as const;

  return (
    <Tabs value={activeTab} onValueChange={(v) => onChange(v as TabKey)}>
      <TabsList className="grid w-full grid-cols-7 bg-white shadow-sm">
        {[
          { key: "overview", label: "Genel Bakış" },
          { key: "prescriptions", label: "Reçeteler" },
          { key: "erx", label: "E-Reçete" },
          { key: "interactions", label: "Etkileşimler" },
          { key: "lab", label: "Lab" },
          { key: "sideEffects", label: "Yan Etkiler" },
          { key: "compliance", label: "Uyumluluk" },
        ].map((tab) => {
          const isDisabled = (disabledKeys as readonly string[]).includes(tab.key);
          return (
            <TabsTrigger
              key={tab.key}
              value={tab.key}
              disabled={isDisabled}
              title={isDisabled ? "Yakında" : undefined}
              className={`flex items-center justify-center data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 data-[state=active]:font-semibold ${
                isDisabled ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {tab.label}
            </TabsTrigger>
          );
        })}
      </TabsList>
    </Tabs>
  );
}


