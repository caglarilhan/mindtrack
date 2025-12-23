import { createBrowserClient, createServerClient } from "@supabase/ssr";

export const createSupabaseBrowserClient = () => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    throw new Error("Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY");
  }

  return createBrowserClient(url, anonKey);
};

// Alias for easier import
export const createClient = createSupabaseBrowserClient;

export const createSupabaseServerClient = async () => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    throw new Error("Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY");
  }

  // Import next/headers only at runtime inside the server function to avoid
  // bundling server-only modules in client components that import this file.
  const { cookies } = await import("next/headers");
  const cookieStore = await cookies();

  return createServerClient(url, anonKey, {
    cookies: {
      get(name: string) {
        return cookieStore.get(name)?.value;
      },
      getAll() {
        return cookieStore.getAll().map((c) => ({ name: c.name, value: c.value }));
      },
      set(name: string, value: string, options?: any) {
        try {
          // @ts-ignore - runtime supports object form
          cookieStore.set({ name, value, ...(options || {}) });
        } catch {
          // @ts-ignore
          cookieStore.set(name as any, value as any);
        }
      },
      setAll(cookiesToSet: { name: string; value: string; options?: any }[]) {
        for (const { name, value, options } of cookiesToSet) {
          // @ts-ignore
          cookieStore.set({ name, value, ...(options || {}) });
        }
      },
      remove(name: string, options?: any) {
        try {
          // @ts-ignore - runtime supports object form
          cookieStore.set({ name, value: '', ...(options || {}), maxAge: 0 });
        } catch {
          // no-op fallback
        }
      },
    },
  });
};


