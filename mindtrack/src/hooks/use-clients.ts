"use client";

import { useQuery } from "@tanstack/react-query";
import { createSupabaseBrowserClient } from "@/lib/supabaseClient";
import { queryKeys } from "@/lib/react-query";
import type { Client } from "@/types/domain";

/**
 * Tüm client'ları fetch etmek için hook
 */
export function useClients() {
  const supabase = createSupabaseBrowserClient();

  return useQuery({
    queryKey: queryKeys.clients(),
    queryFn: async () => {
      // Optimized select - only fetch needed fields
      const { data, error } = await supabase
        .from("clients")
        .select("id, name, status, email, phone, created_at")
        .eq("status", "active") // Filter active clients only
        .order("name", { ascending: true });

      if (error) {
        throw new Error(`Failed to fetch clients: ${error.message}`);
      }

      return (data || []) as Client[];
    },
    staleTime: 5 * 60 * 1000, // 5 dakika - client listesi daha az değişir
  });
}

/**
 * Tek bir client'ı fetch etmek için hook
 */
export function useClient(clientId: string | null) {
  const supabase = createSupabaseBrowserClient();

  return useQuery({
    queryKey: queryKeys.client(clientId || ""),
    queryFn: async () => {
      if (!clientId) return null;

      const { data, error } = await supabase
        .from("clients")
        .select("*")
        .eq("id", clientId)
        .single();

      if (error) {
        throw new Error(`Failed to fetch client: ${error.message}`);
      }

      return data as Client;
    },
    enabled: !!clientId,
    staleTime: 5 * 60 * 1000,
  });
}

