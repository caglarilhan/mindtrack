"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { createSupabaseBrowserClient } from "@/lib/supabaseClient";
import { queryKeys } from "@/lib/react-query";
import type { Note } from "@/types/domain";

interface UseSOAPNotesOptions {
  clientId?: string;
  enabled?: boolean;
}

/**
 * SOAP notlarını fetch etmek için hook
 */
export function useSOAPNotes(options: UseSOAPNotesOptions = {}) {
  const { clientId, enabled = true } = options;
  const supabase = createSupabaseBrowserClient();

  return useQuery({
    queryKey: queryKeys.soapNotes(clientId),
    queryFn: async () => {
      // Optimized select - only fetch needed fields
      let query = supabase
        .from("notes")
        .select("id, client_id, type, content_encrypted, created_at, updated_at, owner_id, metadata")
        .eq("type", "SOAP")
        .order("created_at", { ascending: false })
        .limit(100); // Limit to prevent huge queries

      if (clientId) {
        query = query.eq("client_id", clientId);
      }

      const { data, error } = await query;

      if (error) {
        throw new Error(`Failed to fetch SOAP notes: ${error.message}`);
      }

      return (data || []) as Note[];
    },
    enabled,
    staleTime: 2 * 60 * 1000, // 2 dakika - SOAP notları daha sık güncellenebilir
  });
}

/**
 * Tek bir SOAP notunu fetch etmek için hook
 */
export function useSOAPNote(noteId: string | null) {
  const supabase = createSupabaseBrowserClient();

  return useQuery({
    queryKey: queryKeys.soapNote(noteId || ""),
    queryFn: async () => {
      if (!noteId) return null;

      const { data, error } = await supabase
        .from("notes")
        .select("*")
        .eq("id", noteId)
        .eq("type", "SOAP")
        .single();

      if (error) {
        throw new Error(`Failed to fetch SOAP note: ${error.message}`);
      }

      return data as Note;
    },
    enabled: !!noteId,
  });
}

/**
 * SOAP notu oluşturma mutation'ı
 */
export function useCreateSOAPNote() {
  const queryClient = useQueryClient();
  const supabase = createSupabaseBrowserClient();

  return useMutation({
    mutationFn: async (note: {
      client_id: string;
      content_encrypted: string;
      metadata?: Record<string, unknown>;
    }) => {
      const { data, error } = await supabase
        .from("notes")
        .insert({
          ...note,
          type: "SOAP",
        })
        .select()
        .single();

      if (error) {
        throw new Error(`Failed to create SOAP note: ${error.message}`);
      }

      return data as Note;
    },
    onSuccess: (data) => {
      // Cache'i invalidate et
      queryClient.invalidateQueries({ queryKey: queryKeys.soapNotes(data.client_id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.soapNotes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.analytics() });
    },
  });
}

/**
 * SOAP notu güncelleme mutation'ı
 */
export function useUpdateSOAPNote() {
  const queryClient = useQueryClient();
  const supabase = createSupabaseBrowserClient();

  return useMutation({
    mutationFn: async ({
      noteId,
      updates,
    }: {
      noteId: string;
      updates: Partial<Note>;
    }) => {
      const { data, error } = await supabase
        .from("notes")
        .update(updates)
        .eq("id", noteId)
        .select()
        .single();

      if (error) {
        throw new Error(`Failed to update SOAP note: ${error.message}`);
      }

      return data as Note;
    },
    onSuccess: (data) => {
      // İlgili cache'leri güncelle
      queryClient.setQueryData(queryKeys.soapNote(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.soapNotes(data.client_id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.soapNotes() });
    },
  });
}

/**
 * SOAP notu silme mutation'ı
 */
export function useDeleteSOAPNote() {
  const queryClient = useQueryClient();
  const supabase = createSupabaseBrowserClient();

  return useMutation({
    mutationFn: async ({ noteId, clientId }: { noteId: string; clientId?: string }) => {
      const { error } = await supabase.from("notes").delete().eq("id", noteId);

      if (error) {
        throw new Error(`Failed to delete SOAP note: ${error.message}`);
      }

      return { noteId, clientId };
    },
    onSuccess: ({ clientId }) => {
      // Cache'i invalidate et
      queryClient.invalidateQueries({ queryKey: queryKeys.soapNotes(clientId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.soapNotes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.analytics() });
    },
  });
}

