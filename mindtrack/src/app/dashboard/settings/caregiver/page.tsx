import { Suspense } from "react";
import CaregiverTokensClient from "./caregiver-tokens-client";

export default function CaregiverSettingsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50">
      <div className="max-w-6xl mx-auto px-6 py-10 space-y-6">
        <div>
          <p className="text-sm uppercase tracking-wide text-emerald-600 font-semibold">Security · Caregiver API</p>
          <h1 className="text-3xl font-bold text-gray-900">Caregiver Token Yönetimi</h1>
          <p className="text-gray-600 mt-2">
            Sosyal hizmet paylaşımları için kullanılan erişim anahtarlarını oluştur, döndür ve denetle.
          </p>
        </div>
        <Suspense fallback={<div className="text-sm text-muted-foreground">Yükleniyor...</div>}>
          <CaregiverTokensClient />
        </Suspense>
      </div>
    </div>
  );
}
