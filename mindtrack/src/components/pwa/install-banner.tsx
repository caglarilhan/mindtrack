"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { X, DownloadCloud, Bell } from "lucide-react";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export default function InstallBanner() {
  const [event, setEvent] = React.useState<BeforeInstallPromptEvent | null>(null);
  const [visible, setVisible] = React.useState(false);
  const [notificationStatus, setNotificationStatus] = React.useState<"idle" | "granted" | "denied">("idle");

  React.useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setEvent(e as BeforeInstallPromptEvent);
      setVisible(true);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  if (!visible || !event) {
    return null;
  }

  const handleInstall = async () => {
    try {
      await event.prompt();
      const choice = await event.userChoice;
      if (choice.outcome === "accepted") {
        setVisible(false);
      }
    } catch (error) {
      console.error("install prompt error", error);
    }
  };

  const requestNotifications = async () => {
    if (!("Notification" in window)) {
      setNotificationStatus("denied");
      return;
    }
    const permission = await Notification.requestPermission();
    setNotificationStatus(permission === "granted" ? "granted" : "denied");
  };

  return (
    <div className="fixed bottom-4 right-4 max-w-sm rounded-xl border bg-white shadow-lg p-4 z-50">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold">MindTrack'i yükle</p>
          <p className="text-xs text-muted-foreground">Offline form doldurma & push bildirimleri için PWA olarak kur.</p>
        </div>
        <button className="text-muted-foreground hover:text-foreground" onClick={() => setVisible(false)}>
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button size="sm" onClick={handleInstall}>
          <DownloadCloud className="h-4 w-4 mr-1" />
          Yükle
        </Button>
        <Button size="sm" variant="outline" onClick={requestNotifications} disabled={notificationStatus === "granted"}>
          <Bell className="h-4 w-4 mr-1" />
          {notificationStatus === "granted" ? "Bildirim açık" : "Bildirim iste"}
        </Button>
      </div>
    </div>
  );
}
