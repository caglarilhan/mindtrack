import { createSpeechRecognition } from "./live-transcription";

export type VoiceCommand = 
  | 'create_soap'
  | 'save'
  | 'stop'
  | 'clear'
  | 'export_pdf'
  | 'unknown';

export interface VoiceCommandResult {
  command: VoiceCommand;
  confidence: number;
  rawText: string;
}

/**
 * Ses komutlarını tanı
 */
export function recognizeVoiceCommand(text: string): VoiceCommandResult {
  const lowerText = text.toLowerCase().trim();
  
  // SOAP oluştur komutları
  if (
    lowerText.includes('soap oluştur') ||
    lowerText.includes('soap notu') ||
    lowerText.includes('soap yap') ||
    lowerText.includes('create soap') ||
    lowerText.includes('generate soap')
  ) {
    return {
      command: 'create_soap',
      confidence: 0.9,
      rawText: text,
    };
  }
  
  // Kaydet komutları
  if (
    lowerText.includes('kaydet') ||
    lowerText.includes('save') ||
    lowerText.includes('kayıt')
  ) {
    return {
      command: 'save',
      confidence: 0.8,
      rawText: text,
    };
  }
  
  // Durdur komutları
  if (
    lowerText.includes('durdur') ||
    lowerText.includes('stop') ||
    lowerText.includes('bitir') ||
    lowerText.includes('dur')
  ) {
    return {
      command: 'stop',
      confidence: 0.9,
      rawText: text,
    };
  }
  
  // Temizle komutları
  if (
    lowerText.includes('temizle') ||
    lowerText.includes('clear') ||
    lowerText.includes('sil')
  ) {
    return {
      command: 'clear',
      confidence: 0.8,
      rawText: text,
    };
  }
  
  // PDF export komutları
  if (
    lowerText.includes('pdf') ||
    lowerText.includes('indir') ||
    lowerText.includes('download') ||
    lowerText.includes('export')
  ) {
    return {
      command: 'export_pdf',
      confidence: 0.7,
      rawText: text,
    };
  }
  
  return {
    command: 'unknown',
    confidence: 0,
    rawText: text,
  };
}

/**
 * Ses komutları dinleyicisi oluştur
 */
export function createVoiceCommandListener(
  onCommand: (command: VoiceCommandResult) => void,
  onError: (error: string) => void
): SpeechRecognition | null {
  if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
    onError("Ses komutları desteklenmiyor");
    return null;
  }

  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous = true;
  recognition.interimResults = false; // Sadece final sonuçlar
  recognition.lang = "tr-TR";

  recognition.onresult = (event: SpeechRecognitionEvent) => {
    const lastResult = event.results[event.results.length - 1];
    if (lastResult.isFinal) {
      const text = lastResult[0].transcript;
      const command = recognizeVoiceCommand(text);
      
      if (command.command !== 'unknown') {
        onCommand(command);
      }
    }
  };

  recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
    onError(event.error);
  };

  return recognition;
}





