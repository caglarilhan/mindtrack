/**
 * Secure Audio Streaming
 * HIPAA-compliant encrypted audio streaming via WebSocket
 */

import { encryptAudioData, AudioStreamEncryptor } from "./audio-encryption";
import { logDataAccess } from "@/lib/hipaa/audit-log";

export interface SecureStreamConfig {
  endpoint: string;
  userId: string;
  sessionId: string;
  clientId: string;
  onError?: (error: Error) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
}

export interface StreamedAudioChunk {
  encrypted: string;
  metadata: {
    size: number;
    type: string;
    timestamp: number;
    sequence: number;
  };
}

export class SecureAudioStream {
  private ws: WebSocket | null = null;
  private config: SecureStreamConfig;
  private encryptor: AudioStreamEncryptor;
  private isConnected = false;
  private sequenceNumber = 0;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(config: SecureStreamConfig) {
    this.config = config;
    this.encryptor = new AudioStreamEncryptor();
  }

  /**
   * Connect to secure WebSocket endpoint
   */
  async connect(): Promise<void> {
    if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        // Use wss:// for secure connection
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}${this.config.endpoint}`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.isConnected = true;
          this.reconnectAttempts = 0;
          
          // Send authentication
          this.send({
            type: "auth",
            userId: this.config.userId,
            sessionId: this.config.sessionId,
            clientId: this.config.clientId,
          });

          this.config.onConnected?.();
          resolve();
        };

        this.ws.onerror = (error) => {
          const err = new Error(`WebSocket error: ${error}`);
          this.config.onError?.(err);
          reject(err);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          this.config.onDisconnected?.();
          
          // Attempt reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
              this.connect().catch(console.error);
            }, this.reconnectDelay * this.reconnectAttempts);
          }
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };
      } catch (error) {
        const err = error instanceof Error ? error : new Error("Failed to create WebSocket");
        reject(err);
      }
    });
  }

  /**
   * Send encrypted audio chunk
   */
  async sendAudioChunk(audioBlob: Blob): Promise<void> {
    if (!this.isConnected || this.ws?.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket not connected");
    }

    try {
      // Encrypt audio chunk
      const encrypted = await this.encryptor.encryptChunk(audioBlob);
      
      const chunk: StreamedAudioChunk = {
        encrypted,
        metadata: {
          size: audioBlob.size,
          type: audioBlob.type,
          timestamp: Date.now(),
          sequence: this.sequenceNumber++,
        },
      };

      // Send encrypted chunk
      this.send({
        type: "audio_chunk",
        chunk,
      });
    } catch (error) {
      const err = error instanceof Error ? error : new Error("Failed to send audio chunk");
      this.config.onError?.(err);
      throw err;
    }
  }

  /**
   * Send message
   */
  private send(data: unknown): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket not connected");
    }

    this.ws.send(JSON.stringify(data));
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: { type: string; data?: unknown }): void {
    switch (message.type) {
      case "ack":
        // Acknowledgment received
        break;
      case "error":
        const error = new Error(message.data as string);
        this.config.onError?.(error);
        break;
      default:
        console.warn("Unknown message type:", message.type);
    }
  }

  /**
   * Disconnect
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.encryptor.clear();
  }

  /**
   * Check if connected
   */
  getConnected(): boolean {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN;
  }
}





