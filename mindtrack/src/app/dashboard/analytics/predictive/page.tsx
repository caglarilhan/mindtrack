import PredictiveClient from "./predictive-client";

export default function PredictiveAnalyticsPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Predictive Analytics</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Relapse, no-show ve denial risklerini öngören placeholder dashboard. Henüz demo verisi gösteriyor.
      </p>
      <PredictiveClient />
    </div>
  );
}
