import { createServerClient } from "@supabase/ssr";

export function createClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    throw new Error("Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY");
  }

  // next/headers sadece server ortamında mevcuttur; burada güvenle içe aktarabiliriz.
  const cookiesApi = require("next/headers");
  const cookieStore = cookiesApi.cookies();

  return createServerClient(url, anonKey, {
    cookies: {
      get(name: string) {
        return cookieStore.get(name)?.value;
      },
      getAll() {
        return cookieStore.getAll().map((c: any) => ({ name: c.name, value: c.value }));
      },
      set(name: string, value: string, options?: any) {
        try {
          cookieStore.set({ name, value, ...(options || {}) });
        } catch {
          // no-op fallback
        }
      },
      setAll(cookiesToSet: { name: string; value: string; options?: any }[]) {
        for (const { name, value, options } of cookiesToSet) {
          try {
            cookieStore.set({ name, value, ...(options || {}) });
          } catch {
            // no-op fallback
          }
        }
      },
      remove(name: string, options?: any) {
        try {
          cookieStore.set({ name, value: '', ...(options || {}), maxAge: 0 });
        } catch {
          // no-op
        }
      },
    },
  });
}



