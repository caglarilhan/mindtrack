"use client";

import { useQuery } from "@tanstack/react-query";
import { createSupabaseBrowserClient } from "@/lib/supabaseClient";
import { queryKeys } from "@/lib/react-query";
import { createPaginationMeta, DEFAULT_PAGINATION, type PaginationParams, type PaginatedResult } from "@/lib/db/pagination";
import type { Note } from "@/types/domain";

interface UsePaginatedSOAPNotesOptions extends PaginationParams {
  clientId?: string;
  enabled?: boolean;
}

/**
 * Paginated SOAP notes hook
 * Uses pagination for better performance with large datasets
 */
export function usePaginatedSOAPNotes(options: UsePaginatedSOAPNotesOptions = DEFAULT_PAGINATION) {
  const { clientId, page, pageSize, enabled = true } = options;
  const supabase = createSupabaseBrowserClient();

  return useQuery({
    queryKey: queryKeys.soapNotes(clientId),
    queryFn: async (): Promise<PaginatedResult<Note>> => {
      // Get total count
      let countQuery = supabase
        .from("notes")
        .select("*", { count: "exact", head: true })
        .eq("type", "SOAP");

      if (clientId) {
        countQuery = countQuery.eq("client_id", clientId);
      }

      const { count, error: countError } = await countQuery;

      if (countError) {
        throw new Error(`Failed to count SOAP notes: ${countError.message}`);
      }

      // Get paginated data
      const offset = (page - 1) * pageSize;
      let dataQuery = supabase
        .from("notes")
        .select("*")
        .eq("type", "SOAP")
        .order("created_at", { ascending: false })
        .range(offset, offset + pageSize - 1);

      if (clientId) {
        dataQuery = dataQuery.eq("client_id", clientId);
      }

      const { data, error: dataError } = await dataQuery;

      if (dataError) {
        throw new Error(`Failed to fetch SOAP notes: ${dataError.message}`);
      }

      return createPaginationMeta(
        (data || []) as Note[],
        count || 0,
        page,
        pageSize
      );
    },
    enabled,
    staleTime: 2 * 60 * 1000, // 2 dakika
  });
}





