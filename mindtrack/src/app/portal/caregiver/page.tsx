import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { fetchCaregiverPortalData } from "@/lib/server/portal";
import { verifyCaregiverToken, recordCaregiverAccessLog } from "@/lib/server/caregiverTokens";

interface CaregiverPortalProps {
  searchParams: {
    token?: string;
    patientId?: string;
    region?: string;
  };
}

export default async function CaregiverPortalPage({ searchParams }: CaregiverPortalProps) {
  const token = searchParams.token;
  const patientId = searchParams.patientId;
  const region = (searchParams.region as "us" | "eu") || "us";

  if (!token || !patientId) {
    return <UnauthorizedView reason="Token veya patientId eksik" />;
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
    return <UnauthorizedView reason="Token doğrulanamadı" />;
  }

  await recordCaregiverAccessLog({
    tokenId: verification.tokenId ?? null,
    tokenLabel: verification.label ?? null,
    patientId,
    region,
    status: "allowed",
    reason: "portal-caregiver",
  });

  const data = await fetchCaregiverPortalData(patientId, region);

  return (
    <main className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-blue-50 py-10">
      <div className="mx-auto max-w-4xl space-y-6 px-4">
        <header className="space-y-2 text-center">
          <p className="text-xs uppercase tracking-wide text-orange-600">Caregiver Snapshot</p>
          <h1 className="text-3xl font-semibold">{data.patientName} için bakım özeti</h1>
          <p className="text-sm text-muted-foreground">Bölge: {region === "us" ? "ABD" : "Avrupa"}</p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <Card className="border border-orange-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-orange-700">Risk Seviyesi</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant={data.caregiverSummary.riskLevel === "high" ? "destructive" : "secondary"}>
                {data.caregiverSummary.riskLevel.toUpperCase()}
              </Badge>
            </CardContent>
          </Card>
          <Card className="border border-sky-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-sky-700">Top Gaps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-xs">
              {data.caregiverSummary.careGaps.length === 0 && <p className="text-muted-foreground">Gap yok</p>}
              {data.caregiverSummary.careGaps.map((gap) => (
                <p key={gap.id}>{gap.title}</p>
              ))}
            </CardContent>
          </Card>
          <Card className="border border-emerald-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-emerald-700">Öncelik</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-slate-700">
              {data.caregiverSummary.keyAction || "Klinikten gelecek talimatları bekleyin."}
            </CardContent>
          </Card>
        </section>

        <Card>
          <CardHeader>
            <CardTitle>Care Gap Detayları</CardTitle>
            <CardDescription>Klinik ekip tarafından paylaşılan öncelikler</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.careGaps.slice(0, 4).map((gap) => (
              <div key={gap.id} className="rounded border border-slate-200 p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{gap.title}</span>
                  <Badge variant={gap.severity === "high" ? "destructive" : "outline"}>{gap.severity}</Badge>
                </div>
                <p className="text-muted-foreground text-xs">{gap.description}</p>
                <p className="text-xs text-emerald-700">Önerilen aksiyon: {gap.recommendedAction}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Destek Planı</CardTitle>
            <CardDescription>Caregiver olarak yapabilecekleriniz</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>1. Seans öncesi günlük ruh hali kontrolü yapın.</p>
            <p>2. İlaç kutusunu her akşam aynı saatte kontrol edin.</p>
            <p>3. Kriz durumunda klinik + {region === "us" ? "988" : "112"} numarasına başvurun.</p>
            <Button variant="outline" size="sm" asChild>
              <a href={`/portal/client?token=${token}&patientId=${patientId}&region=${region}`}>Hasta görünümüne geç</a>
            </Button>
          </CardContent>
        </Card>
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
          <p className="text-sm text-muted-foreground">Klinik ekibinden yeni bir link isteyin.</p>
        </CardContent>
      </Card>
    </main>
  );
}
