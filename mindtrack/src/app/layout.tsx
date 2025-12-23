import type { Metadata } from "next";
import "./globals.css";
import { NextIntlClientProvider } from "next-intl";
import trMessages from "../../messages/tr.json";
import { ReactQueryProvider } from "@/components/providers/react-query-provider";

export const metadata: Metadata = {
  title: "MindTrack",
  description: "Therapist Practice Management",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>
        <ReactQueryProvider>
          <NextIntlClientProvider locale="tr" messages={trMessages as unknown as Record<string, any>}>
            {children}
          </NextIntlClientProvider>
        </ReactQueryProvider>
      </body>
    </html>
  );
}
