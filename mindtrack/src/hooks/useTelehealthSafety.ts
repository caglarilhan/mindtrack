"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  fetchRiskFeed,
  fetchTranscripts,
  ingestTranscripts,
  saveRecording,
  type TranscriptIngestSegment,
} from "@/lib/telehealth";

interface SafetyState {
  transcripts: any[];
  riskEvents: any[];
  riskCriticalCount: number;
  loading: boolean;
  error: string | null;
}

interface UseTelehealthSafetyOptions {
  sessionId: string;
  pollMs?: number;
}

export function useTelehealthSafety(options: UseTelehealthSafetyOptions) {
  const { sessionId, pollMs = 5000 } = options;
  const [state, setState] = useState<SafetyState>({
    transcripts: [],
    riskEvents: [],
    riskCriticalCount: 0,
    loading: false,
    error: null,
  });
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const fetchAll = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const [tRes, rRes] = await Promise.all([fetchTranscripts(sessionId, true), fetchRiskFeed(sessionId)]);
      setState((s) => ({
        ...s,
        loading: false,
        transcripts: tRes?.transcripts || [],
        riskEvents: tRes?.riskEvents || rRes?.events || [],
        riskCriticalCount: rRes?.criticalCount ?? 0,
      }));
    } catch (err: any) {
      setState((s) => ({ ...s, loading: false, error: err?.message || "Veri alınamadı" }));
    }
  }, [sessionId]);

  useEffect(() => {
    fetchAll();
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(fetchAll, pollMs);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchAll, pollMs]);

  const ingest = useCallback(
    async (segments: TranscriptIngestSegment[], region?: "us" | "eu") => {
      await ingestTranscripts({ sessionId, region, segments });
      await fetchAll();
    },
    [sessionId, fetchAll],
  );

  const saveRec = useCallback(
    async (params: { recordingUrl: string; duration?: number; fileSize?: number; quality?: "SD" | "HD" | "FHD"; storageLocation?: string }) => {
      await saveRecording({ sessionId, ...params });
      // recording save, no need to refetch transcripts/risk
    },
    [sessionId],
  );

  const riskBadges = useMemo(() => {
    const counts = state.riskEvents.reduce<Record<string, number>>((acc, ev: any) => {
      const cat = ev.category || "other";
      acc[cat] = (acc[cat] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([category, count]) => ({ category, count }));
  }, [state.riskEvents]);

  return {
    ...state,
    refresh: fetchAll,
    ingestTranscripts: ingest,
    saveRecording: saveRec,
    riskBadges,
  };
}










