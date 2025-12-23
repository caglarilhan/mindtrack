import CommunityClient from "./community-client";

export default function CommunityPage() {
  return (
    <div className="container mx-auto p-6 space-y-2">
      <h1 className="text-3xl font-bold">Clinician Community</h1>
      <p className="text-sm text-muted-foreground">
        Vaka tartışmaları ve guideline paylaşımları için güvenli community placeholder'ı.
      </p>
      <CommunityClient />
    </div>
  );
}
