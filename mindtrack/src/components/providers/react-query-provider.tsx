"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import * as React from "react";

// Query client configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 dakika - data fresh kalır
      cacheTime: 10 * 60 * 1000, // 10 dakika - cache'de kalır
      refetchOnWindowFocus: false, // Window focus'ta refetch yapma
      refetchOnMount: true, // Component mount'ta refetch yap
      retry: 1, // 1 kez retry yap
      retryDelay: 1000, // 1 saniye bekle
    },
    mutations: {
      retry: 1,
      retryDelay: 1000,
    },
  },
});

// Query Client Provider wrapper
export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = React.useState(() => queryClient);

  return (
    <QueryClientProvider client={client}>
      {children}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}





