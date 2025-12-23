import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { saveRecordingMetadata, getRecordingMetadata, generateSignedDownloadUrl } from "@/lib/server/telehealthRecording";

export async function POST(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const body = await request.json();
    const { sessionId, recordingUrl, duration, fileSize, quality, storageLocation } = body;

    if (!sessionId || !recordingUrl) {
      return NextResponse.json({ error: "sessionId ve recordingUrl gerekli" }, { status: 400 });
    }

    await saveRecordingMetadata({
      sessionId,
      recordingUrl,
      duration: duration || 0,
      fileSize: fileSize || 0,
      quality: quality || "HD",
      storageLocation: storageLocation || "s3",
      encrypted: true,
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[telehealth-recording] POST error", error);
    return NextResponse.json({ error: "Recording kaydedilemedi" }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");

    if (!sessionId) {
      return NextResponse.json({ error: "sessionId gerekli" }, { status: 400 });
    }

    const metadata = await getRecordingMetadata(sessionId);
    if (!metadata) {
      return NextResponse.json({ error: "Recording bulunamadı" }, { status: 404 });
    }

    const signedUrl = await generateSignedDownloadUrl(metadata.recording_url);
    return NextResponse.json({ metadata, downloadUrl: signedUrl });
  } catch (error) {
    console.error("[telehealth-recording] GET error", error);
    return NextResponse.json({ error: "Recording alınamadı" }, { status: 500 });
  }
}
