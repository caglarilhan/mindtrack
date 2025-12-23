import { Suspense } from "react";
import { fetchIntegrationCatalog, fetchIntegrationConnections, fetchIntegrationEvents, fetchAutomationRules } from "@/lib/server/integrations";
import IntegrationsClient from "./integrations-client";

const DEFAULT_CLINIC = "demo-clinic";

async function IntegrationsContent() {
  const [catalog, connections, events, rules] = await Promise.all([
    fetchIntegrationCatalog(),
    fetchIntegrationConnections(DEFAULT_CLINIC),
    fetchIntegrationEvents(DEFAULT_CLINIC),
    fetchAutomationRules(DEFAULT_CLINIC),
  ]);

  return (
    <IntegrationsClient
      clinicId={DEFAULT_CLINIC}
      initialCatalog={catalog}
      initialConnections={connections}
      initialEvents={events}
      initialRules={rules}
    />
  );
}

export default function IntegrationsPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Integration Marketplace</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Üçüncü parti servisleri bağlayın, webhook eventlerini izleyin ve otomasyon kuralları oluşturun.
      </p>
      <Suspense fallback={<div className="text-sm text-muted-foreground">Yükleniyor...</div>}>
        <IntegrationsContent />
      </Suspense>
    </div>
  );
}
