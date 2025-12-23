import { fetchSocialWorkerTasks, fetchSocialWorkerHandoffs } from "@/lib/server/social-worker";
import SocialWorkerClient from "./social-worker-client";

const DEFAULT_CLINIC = process.env.NEXT_PUBLIC_DEFAULT_CLINIC_ID || "demo-clinic";

export default async function SocialWorkerPage() {
  const [tasks, handoffs] = await Promise.all([
    fetchSocialWorkerTasks({ clinicId: DEFAULT_CLINIC }),
    fetchSocialWorkerHandoffs({ clinicId: DEFAULT_CLINIC }),
  ]);

  return (
    <div className="container mx-auto p-6 space-y-2">
      <h1 className="text-3xl font-bold">Social Worker Portal</h1>
      <p className="text-sm text-muted-foreground">
        Barınma, iş, okul ve aile odaklı görevler ile care team hand-off özetlerini gösteren pano.
      </p>
      <SocialWorkerClient clinicId={DEFAULT_CLINIC} initialTasks={tasks} initialHandoffs={handoffs} />
    </div>
  );
}
