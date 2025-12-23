import ReferralClient from "./referral-client";

export default function ReferralsPage() {
  return (
    <div className="container mx-auto p-6 space-y-2">
      <h1 className="text-3xl font-bold">Referral Network</h1>
      <p className="text-sm text-muted-foreground">
        Uzmanlık, bölge ve sigorta uygunluğuna göre sevk edebileceğiniz provider directory placeholder'ı.
      </p>
      <ReferralClient />
    </div>
  );
}
