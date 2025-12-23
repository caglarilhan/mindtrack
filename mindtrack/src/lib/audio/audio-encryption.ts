/**
 * Audio Encryption (Client-Side)
 * Encrypts audio data before transmission/storage (HIPAA compliant)
 */

import { encryptPHI } from "@/lib/hipaa/encryption";

/**
 * Encrypt audio data (Blob or ArrayBuffer)
 */
export async function encryptAudioData(
  audioData: Blob | ArrayBuffer
): Promise<{ encrypted: string; iv: string; metadata: { size: number; type: string } }> {
  // Convert to base64
  const base64 = await blobToBase64(audioData instanceof Blob ? audioData : new Blob([audioData]));
  
  // Encrypt using HIPAA encryption
  const encrypted = encryptPHI(base64);
  
  // Extract metadata
  const metadata = {
    size: audioData instanceof Blob ? audioData.size : audioData.byteLength,
    type: audioData instanceof Blob ? audioData.type : "audio/webm",
  };

  return {
    encrypted,
    iv: "", // IV is included in encrypted string
    metadata,
  };
}

/**
 * Decrypt audio data
 */
export async function decryptAudioData(
  encrypted: string,
  metadata: { size: number; type: string }
): Promise<Blob> {
  const { decryptPHI } = await import("@/lib/hipaa/encryption");
  
  // Decrypt
  const decryptedBase64 = decryptPHI(encrypted);
  
  // Convert base64 to Blob
  const blob = await base64ToBlob(decryptedBase64, metadata.type);
  
  return blob;
}

/**
 * Convert Blob to base64
 */
function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      // Remove data URL prefix if present
      const base64Data = base64.includes(",") ? base64.split(",")[1] : base64;
      resolve(base64Data);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Convert base64 to Blob
 */
function base64ToBlob(base64: string, mimeType: string): Promise<Blob> {
  return new Promise((resolve, reject) => {
    try {
      // Add data URL prefix if not present
      const dataUrl = base64.startsWith("data:") ? base64 : `data:${mimeType};base64,${base64}`;
      
      fetch(dataUrl)
        .then((res) => res.blob())
        .then((blob) => resolve(blob))
        .catch(reject);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Encrypt audio stream chunks
 */
export class AudioStreamEncryptor {
  private chunkSize: number;
  private encryptedChunks: string[] = [];

  constructor(chunkSize: number = 1024 * 10) { // 10KB chunks
    this.chunkSize = chunkSize;
  }

  /**
   * Encrypt audio chunk
   */
  async encryptChunk(chunk: Blob): Promise<string> {
    const encrypted = await encryptAudioData(chunk);
    this.encryptedChunks.push(encrypted.encrypted);
    return encrypted.encrypted;
  }

  /**
   * Get all encrypted chunks
   */
  getEncryptedChunks(): string[] {
    return [...this.encryptedChunks];
  }

  /**
   * Clear chunks
   */
  clear(): void {
    this.encryptedChunks = [];
  }
}





