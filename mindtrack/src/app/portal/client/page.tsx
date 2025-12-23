import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { fetchClientPortalData } from "@/lib/server/portal";
import { verifyCaregiverToken, recordCaregiverAccessLog } from "@/lib/server/caregiverTokens";
import { computeCareGaps } from "@/lib/server/careGaps";

interface PortalPageProps {
  searchParams: {
    token?: string;
    patientId?: string;
    region?: string;
  };
}

export default async function ClientPortalPage({ searchParams }: PortalPageProps) {
  const token = searchParams.token;
  const patientId = searchParams.patientId;
  const region = (searchParams.region as "us" | "eu") || "us";

  if (!token || !patientId) {
    return <UnauthorizedView reason="Token ve patientId gerekli" />;
  }

  const verification = await verifyCaregiverToken(token, region);
  if (!verification.ok) {
    await recordCaregiverAccessLog({
      tokenId: verification.tokenId ?? null,
      tokenLabel: verification.label ?? null,
      patientId,
      region,
      status: "denied",
      reason: verification.reason ?? "invalid-token",
    });
    return <UnauthorizedView reason="Geçersiz veya süresi dolmuş token" />;
  }

  await recordCaregiverAccessLog({
    tokenId: verification.tokenId ?? null,
    tokenLabel: verification.label ?? null,
    patientId,
    region,
    status: "allowed",
    reason: "portal-client",
  });

  const data = await fetchClientPortalData(patientId, region);

  return (
    <main className="min-h-screen bg-slate-50 py-10">
      <div className="mx-auto max-w-5xl space-y-6 px-4">
        <header className="space-y-2 text-center">
          <p className="text-sm uppercase tracking-wide text-muted-foreground">MindTrack Client Portal</p>
          <h1 className="text-3xl font-semibold">Merhaba {data.patientName}</h1>
          <p className="text-sm text-muted-foreground">Bölge: {region === "us" ? "ABD" : "Avrupa"}</p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          {data.nextActions.slice(0, 3).map((action, idx) => (
            <Card key={idx} className="border-emerald-100 bg-white/70">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-emerald-700">Önerilen Adım</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-700">{action}</p>
              </CardContent>
            </Card>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Yaklaşan Randevular</CardTitle>
              <CardDescription>Telehealth & klinik ziyaretler</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.appointments.map((appt) => (
                <div key={appt.id} className="rounded-lg border p-3">
                  <div className="flex items-center justify-between text-sm">
                    <span>{new Date(appt.date).toLocaleString()}</span>
                    <Badge variant={appt.status === "scheduled" ? "default" : "secondary"}>
                      {appt.status.toUpperCase()}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-700">Uzman: {appt.provider}</p>
                  <p className="text-xs text-muted-foreground">{appt.location ?? "Telehealth"}</p>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Faturalar & Claim Durumu</CardTitle>
              <CardDescription>Ödeme özetiniz</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold">Faturalar</h3>
                <div className="space-y-2">
                  {data.invoices.map((invoice) => (
                    <div key={invoice.id} className="rounded border p-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span>#{invoice.id}</span>
                        <Badge variant={invoice.status === "paid" ? "default" : "secondary"}>{invoice.status}</Badge>
                      </div>
                      <p>${invoice.amount.toFixed(2)} · Due {new Date(invoice.dueDate).toLocaleDateString()}</p>
                    </div>
                  ))}
                </div>
              </div>
              <Separator />
              <div>
                <h3 className="text-sm font-semibold">Claims</h3>
                <div className="space-y-2">
                  {data.claims.map((claim) => (
                    <div key={claim.id} className="rounded border p-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span>{claim.claimNumber}</span>
                        <Badge variant="outline">{claim.status}</Badge>
                      </div>
                      {claim.amount && <p>${claim.amount.toFixed(2)}</p>}
                      {claim.updatedAt && (
                        <p className="text-xs text-muted-foreground">Güncellendi: {new Date(claim.updatedAt).toLocaleDateString()}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Care Gap & Güvenlik</CardTitle>
              <CardDescription>Klinik ekipten uyarılar</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.careGaps.length === 0 ? (
                <p className="text-sm text-muted-foreground">Aktif care gap bulunmuyor.</p>
              ) : (
                data.careGaps.slice(0, 4).map((gap) => (
                  <div key={gap.id} className="rounded border p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{gap.title}</span>
                      <Badge variant={gap.severity === "high" || gap.severity === "critical" ? "destructive" : "outline"}>
                        {gap.severity.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground text-xs">{gap.description}</p>
                    <p className="text-xs text-emerald-700 mt-1">Öneri: {gap.recommendedAction}</p>
                  </div>
                ))
              )}
              {data.safetySummary && (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm">
                  <p className="font-medium">Risk Seviyesi: {data.safetySummary.highestSeverity.toUpperCase()}</p>
                  <p className="text-xs text-muted-foreground">Son güncelleme: {data.safetySummary.lastUpdated || "-"}</p>
                </div>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Destek</CardTitle>
              <CardDescription>Klinik ekibine hızlı erişim</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>MindTrack destek hattı: <span className="font-semibold">+1 (555) 010-9988</span></p>
              <p>E-posta: <a href="mailto:support@mindtrack.health" className="underline">support@mindtrack.health</a></p>
              <p>Öneri: Seans öncesi 10 dk önce bağlanmayı unutmayın.</p>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}

function UnauthorizedView({ reason }: { reason: string }) {
  return (
    <main className="min-h-screen bg-slate-100 flex items-center justify-center">
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Erişim Engellendi</CardTitle>
          <CardDescription>{reason}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Linkin süresi dolmuş olabilir. Klinik ekibinden yeni bir erişim isteyin.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
