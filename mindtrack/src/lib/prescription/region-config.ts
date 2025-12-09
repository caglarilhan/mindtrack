import { RegionId } from "./types";

export const REGION_CONFIG: Record<
  RegionId,
  {
    id: RegionId;
    label: string;
    authority: string;
    subtitle: string;
    complianceTitle: string;
  }
> = {
  TR: {
    id: "TR",
    label: "Türkiye",
    authority: "TİTCK",
    subtitle: "TİTCK uyumlu elektronik reçete sistemi",
    complianceTitle: "TİTCK Uyumluluğu",
  },
  US: {
    id: "US",
    label: "United States",
    authority: "DEA",
    subtitle: "DEA compliant electronic prescribing",
    complianceTitle: "DEA Compliance",
  },
  EU: {
    id: "EU",
    label: "European Union",
    authority: "EMA",
    subtitle: "EMA compliant electronic prescribing",
    complianceTitle: "EMA Compliance",
  },
};


