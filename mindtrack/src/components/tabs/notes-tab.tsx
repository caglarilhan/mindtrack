"use client";

import * as React from "react";
import { createSupabaseBrowserClient } from "@/lib/supabaseClient";
import type { Note, Client } from "@/types/domain";
import { encryptNote, decryptNote, hasPassphraseConfigured, setPassphrase, encryptNoteWithPassphrase, decryptNoteWithPassphrase } from "@/lib/crypto";
import type { AINoteRequest, AINoteResponse } from "@/lib/ai-assistant";
import { logRisk, getRiskStats } from "@/lib/ai/risk-logging";
import { sendRiskNotifications } from "@/lib/ai/risk-notifications";
import { saveSOAPVersion, getSOAPVersions, getLatestSOAPVersion } from "@/lib/ai/soap-versioning";
import { editSOAPSection, getSOAPSuggestions, completeSOAPSection } from "@/lib/ai/soap-editor";
import { DEFAULT_TEMPLATES, applyTemplate, getTemplateById } from "@/lib/ai/soap-templates";
import { analyzeTrends } from "@/lib/ai/trend-analysis";
import { VersionComparisonLazy } from "@/components/ai/version-comparison-lazy";
import { compareVersions, getSOAPVersion } from "@/lib/ai/soap-versioning";
import { createSpeechRecognition, isSpeechRecognitionSupported, analyzeAudioLevel } from "@/lib/ai/live-transcription";
import { transcribeAudio } from "@/lib/ai-assistant";
import { createVoiceCommandListener, recognizeVoiceCommand } from "@/lib/ai/voice-commands";
import { SOAPDisplay } from "@/components/ai/soap-display";
import { useToast, ToastContainer } from "@/components/ui/toast";
import { SOAPSkeleton } from "@/components/ui/skeleton";
import { exportSOAPToWord, generateShareLink, generateQRCode } from "@/lib/ai/export-utils";
import { FeedbackWidget } from "@/components/ai/feedback-widget";
import { ErrorBoundary } from "@/components/ai/error-boundary";
import { useSOAPNotes } from "@/hooks/use-soap-notes";
import { useClients } from "@/hooks/use-clients";

const NOTE_TYPES = ["SOAP", "BIRP", "DAP"] as const;

export default function NotesTab() {
  const supabase = React.useMemo(() => createSupabaseBrowserClient(), []);
  
  // React Query hooks
  const { data: clients = [], isLoading: clientsLoading } = useClients();
  const { data: notes = [], isLoading: notesLoading, refetch: refetchNotes } = useSOAPNotes({ clientId: undefined });
  
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [passphrase, setPassphraseInput] = React.useState<string>("");
  const [hasPassphrase, setHasPassphrase] = React.useState<boolean>(false);
  const [noteType, setNoteType] = React.useState<typeof NOTE_TYPES[number]>("SOAP");
  const [clientId, setClientId] = React.useState("");
  const [content, setContent] = React.useState("");
  
  // AI Note Assistant states
  const [showAIAssistant, setShowAIAssistant] = React.useState(false);
  const [aiLoading, setAiLoading] = React.useState(false);
  const [aiNoteData, setAiNoteData] = React.useState<AINoteRequest>({
    clientName: "",
    sessionType: "follow-up",
    sessionFocus: "",
    clientPresentation: "",
    interventions: "",
    progress: "",
    nextSteps: "",
    noteType: "SOAP"
  });
  const [aiResponse, setAiResponse] = React.useState<AINoteResponse | null>(null);
  const [transcript, setTranscript] = React.useState<string>("");
  const [analysisMode, setAnalysisMode] = React.useState<'standard' | 'premium' | 'consultation'>('standard');
  const [riskDetected, setRiskDetected] = React.useState<{ level: 'high' | 'medium' | 'low'; keywords: string[] } | null>(null);
  const [soapData, setSoapData] = React.useState<{ subjective: string; objective: string; assessment: string; plan: string } | null>(null);
  const [previousSessions, setPreviousSessions] = React.useState<string[]>([]);
  const [loadingHistory, setLoadingHistory] = React.useState(false);
  const [soapVersions, setSoapVersions] = React.useState<any[]>([]);
  const [currentVersion, setCurrentVersion] = React.useState<number | null>(null);
  const [selectedTemplate, setSelectedTemplate] = React.useState<string>('');
  const [editingSection, setEditingSection] = React.useState<'subjective' | 'objective' | 'assessment' | 'plan' | null>(null);
  const [editSuggestions, setEditSuggestions] = React.useState<any[]>([]);
  const [trendAnalysis, setTrendAnalysis] = React.useState<any>(null);
  const [comparingVersions, setComparingVersions] = React.useState<{ v1: number; v2: number } | null>(null);
  const [version1Data, setVersion1Data] = React.useState<any>(null);
  const [version2Data, setVersion2Data] = React.useState<any>(null);
  
  // Real-time transcription states
  const [isRecording, setIsRecording] = React.useState(false);
  const [isTranscribing, setIsTranscribing] = React.useState(false);
  const [recordingTime, setRecordingTime] = React.useState(0);
  const [audioLevel, setAudioLevel] = React.useState(0);
  const [recognition, setRecognition] = React.useState<SpeechRecognition | null>(null);
  const [currentSpeaker, setCurrentSpeaker] = React.useState<'patient' | 'therapist'>('patient');
  const [voiceCommandsEnabled, setVoiceCommandsEnabled] = React.useState(false);
  const [commandListener, setCommandListener] = React.useState<SpeechRecognition | null>(null);
  const [showSOAPDisplay, setShowSOAPDisplay] = React.useState(false);
  const [editingSection, setEditingSection] = React.useState<'subjective' | 'objective' | 'assessment' | 'plan' | null>(null);
  const [shareLink, setShareLink] = React.useState<string | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = React.useState<string | null>(null);
  const [showShareModal, setShowShareModal] = React.useState(false);
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const audioContextRef = React.useRef<AudioContext | null>(null);
  const timerRef = React.useRef<NodeJS.Timeout | null>(null);
  const audioLevelRef = React.useRef<NodeJS.Timeout | null>(null);
  const { toast, toasts } = useToast();

  const applyTemplate = (type: typeof NOTE_TYPES[number]) => {
    setNoteType(type);
    const templates: Record<typeof NOTE_TYPES[number], string> = {
      SOAP: `S: 
O: 
A: 
P: `,
      BIRP: `B: 
I: 
R: 
P: `,
      DAP: `D: 
A: 
P: `,
    } as const;
    setContent(templates[type]);
  };

  // React Query kullanıyoruz, fetchAll artık gerekli değil
  // Ancak diğer yerlerde kullanılıyorsa refetchNotes kullanabiliriz
  const fetchAll = React.useCallback(async () => {
    await refetchNotes();
  }, [refetchNotes]);

  // Geçmiş seansları yükle (clientId değiştiğinde)
  React.useEffect(() => {
    if (clientId) {
      loadPreviousSessions();
      loadSOAPVersions();
    } else {
      setPreviousSessions([]);
      setSoapVersions([]);
      setCurrentVersion(null);
    }
  }, [clientId, supabase]);

  const loadSOAPVersions = async () => {
    if (!clientId) return;
    
    try {
      const versions = await getSOAPVersions(clientId, 10);
      setSoapVersions(versions);
      
      // Son versiyonu bul
      const latest = await getLatestSOAPVersion(clientId);
      if (latest) {
        setCurrentVersion(latest.version);
      }
      
      // Trend analizi yap (5+ versiyon varsa)
      if (versions.length >= 5) {
        const trends = await analyzeTrends(clientId, 6);
        setTrendAnalysis(trends);
      }
    } catch (error) {
      console.error('SOAP versiyonları yüklenemedi:', error);
    }
  };

  // Real-time transcription başlat
  const startLiveTranscription = async () => {
    if (!isSpeechRecognitionSupported()) {
      setError('Tarayıcınız canlı transkripti desteklemiyor');
      return;
    }

    try {
      // Mikrofon izni al
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Audio context oluştur (ses seviyesi için)
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;
      
      // Ses seviyesi analizi başlat
      const updateAudioLevel = () => {
        if (audioContextRef.current && stream) {
          const { level } = analyzeAudioLevel(audioContextRef.current, stream);
          setAudioLevel(level);
        }
        if (isRecording) {
          audioLevelRef.current = setTimeout(updateAudioLevel, 100);
        }
      };
      updateAudioLevel();

      // Speech Recognition başlat
      const rec = createSpeechRecognition(
        (chunk) => {
          // Transkripti güncelle
          if (chunk.isFinal) {
            setTranscript(prev => prev + (prev ? ' ' : '') + chunk.text);
            
            // Risk kontrolü
            if (chunk.riskDetected) {
              const risk = analyzeRisk(chunk.text);
              if (risk) {
                setRiskDetected(risk);
              }
            }
          }
        },
        () => {
          // Kayıt bitti
          setIsRecording(false);
          setIsTranscribing(false);
        },
        (error) => {
          setError(`Transkript hatası: ${error}`);
          setIsRecording(false);
        },
        currentSpeaker
      );

      if (rec) {
        rec.start();
        setRecognition(rec);
        setIsRecording(true);
        setIsTranscribing(true);
        setRecordingTime(0);

        // Timer başlat
        timerRef.current = setInterval(() => {
          setRecordingTime(prev => prev + 1);
        }, 1000);
      }
    } catch (error: any) {
      console.error('Canlı transkript hatası:', error);
      setError(error.message || 'Mikrofon erişimi reddedildi');
    }
  };

  // Real-time transcription durdur
  const stopLiveTranscription = () => {
    if (recognition) {
      recognition.stop();
      setRecognition(null);
    }
    
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    if (audioLevelRef.current) {
      clearTimeout(audioLevelRef.current);
      audioLevelRef.current = null;
    }
    
    setIsRecording(false);
    setIsTranscribing(false);
    setAudioLevel(0);
  };

  // Ses kaydı başlat (MediaRecorder ile)
  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const audioChunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // Transkripte çevir
        setIsTranscribing(true);
        try {
          const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
          const transcribedText = await transcribeAudio(audioFile);
          setTranscript(prev => prev + (prev ? '\n\n' : '') + transcribedText);
        } catch (error) {
          console.error('Ses transkripti hatası:', error);
          setError('Ses transkripti oluşturulamadı');
        } finally {
          setIsTranscribing(false);
        }
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (error: any) {
      console.error('Ses kaydı hatası:', error);
      setError(error.message || 'Mikrofon erişimi reddedildi');
    }
  };

  // Ses kaydı durdur
  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // Ses komutları dinleyicisi
  React.useEffect(() => {
    if (voiceCommandsEnabled && !commandListener) {
      const listener = createVoiceCommandListener(
        (command) => {
          console.log('🎤 Ses komutu:', command);
          
          switch (command.command) {
            case 'create_soap':
              if (transcript.trim()) {
                handleAIGenerate();
              }
              break;
            case 'save':
              // Otomatik kaydetme zaten aktif
              break;
            case 'stop':
              stopLiveTranscription();
              stopAudioRecording();
              break;
            case 'clear':
              setTranscript('');
              setRiskDetected(null);
              break;
            case 'export_pdf':
              if (soapData) {
                exportToPDF();
              }
              break;
          }
        },
        (error) => {
          console.error('Ses komutu hatası:', error);
        }
      );
      
      if (listener) {
        listener.start();
        setCommandListener(listener);
      }
    } else if (!voiceCommandsEnabled && commandListener) {
      commandListener.stop();
      setCommandListener(null);
    }
    
    return () => {
      if (commandListener) {
        commandListener.stop();
      }
    };
  }, [voiceCommandsEnabled]);

  // Cleanup
  React.useEffect(() => {
    return () => {
      stopLiveTranscription();
      stopAudioRecording();
      if (commandListener) {
        commandListener.stop();
      }
    };
  }, []);

  // Versiyonları karşılaştır
  const handleCompareVersions = async (v1: number, v2: number) => {
    if (!clientId) return;
    
    try {
      const [version1, version2] = await Promise.all([
        getSOAPVersion(clientId, v1),
        getSOAPVersion(clientId, v2),
      ]);
      
      if (version1 && version2) {
        setVersion1Data(version1);
        setVersion2Data(version2);
        setComparingVersions({ v1, v2 });
      }
    } catch (error) {
      console.error('Versiyon karşılaştırma hatası:', error);
    }
  };

  // Template uygula
  const applySOAPTemplate = (templateId: string) => {
    const template = getTemplateById(templateId);
    if (!template) return;
    
    const templateSOAP = applyTemplate(template);
    const formattedSOAP = `S (Subjective):\n${templateSOAP.subjective}\n\nO (Objective):\n${templateSOAP.objective}\n\nA (Assessment):\n${templateSOAP.assessment}\n\nP (Plan):\n${templateSOAP.plan}`;
    
    setContent(formattedSOAP);
    setNoteType('SOAP');
    setSelectedTemplate(templateId);
  };

  // SOAP bölümünü düzenle
  const handleEditSection = async (section: 'subjective' | 'objective' | 'assessment' | 'plan', instruction: string) => {
    if (!soapData) return;
    
    setAiLoading(true);
    try {
      const edited = await editSOAPSection(section, soapData[section], instruction);
      
      // SOAP verisini güncelle
      const updatedSOAP = { ...soapData, [section]: edited };
      setSoapData(updatedSOAP);
      
      // İçeriği güncelle
      const formattedSOAP = `S (Subjective):\n${updatedSOAP.subjective}\n\nO (Objective):\n${updatedSOAP.objective}\n\nA (Assessment):\n${updatedSOAP.assessment}\n\nP (Plan):\n${updatedSOAP.plan}`;
      setContent(formattedSOAP);
    } catch (error) {
      console.error('Bölüm düzenleme hatası:', error);
      setError('Bölüm düzenlenemedi');
    } finally {
      setAiLoading(false);
    }
  };

  // AI önerileri al
  const loadEditSuggestions = async () => {
    if (!soapData) return;
    
    setAiLoading(true);
    try {
      const suggestions = await getSOAPSuggestions(soapData);
      setEditSuggestions(suggestions);
    } catch (error) {
      console.error('Öneriler yüklenemedi:', error);
    } finally {
      setAiLoading(false);
    }
  };

  // Versiyona geri dön
  const restoreVersion = async (version: number) => {
    if (!clientId) return;
    
    try {
      const versionData = await getSOAPVersions(clientId, 1);
      const targetVersion = versionData.find(v => v.version === version);
      
      if (!targetVersion) {
        setError('Versiyon bulunamadı');
        return;
      }
      
      // Versiyonu içeriğe yükle
      const formattedSOAP = `S (Subjective):\n${targetVersion.soap_data.subjective}\n\nO (Objective):\n${targetVersion.soap_data.objective}\n\nA (Assessment):\n${targetVersion.soap_data.assessment}\n\nP (Plan):\n${targetVersion.soap_data.plan}`;
      
      setContent(formattedSOAP);
      setSoapData(targetVersion.soap_data);
      setCurrentVersion(version);
      
      // Yeni versiyon olarak kaydet
      await saveSOAPVersion(
        clientId,
        targetVersion.soap_data,
        undefined,
        `Versiyon ${version}'den geri yüklendi`
      );
      
      await loadSOAPVersions();
    } catch (error) {
      console.error('Versiyon geri yükleme hatası:', error);
      setError('Versiyon geri yüklenemedi');
    }
  };

  const loadPreviousSessions = async () => {
    if (!clientId) return;
    
    setLoadingHistory(true);
    try {
      const { data: previousNotes, error } = await supabase
        .from("notes")
        .select("content_encrypted, created_at")
        .eq("client_id", clientId)
        .eq("type", "SOAP")
        .order("created_at", { ascending: false })
        .limit(5);

      if (error) throw error;

      const decryptedNotes: string[] = [];
      for (const note of previousNotes || []) {
        try {
          const decrypted = hasPassphrase && passphrase
            ? await decryptNoteWithPassphrase(note.content_encrypted, passphrase)
            : await decryptNote(note.content_encrypted);
          decryptedNotes.push(decrypted);
        } catch (e) {
          // Şifre çözülemezse atla
          console.warn('Not deşifre edilemedi:', e);
        }
      }

      setPreviousSessions(decryptedNotes);
    } catch (error) {
      console.error('Geçmiş seanslar yüklenemedi:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Geçmiş seanslardan context ekle
  const addContextFromHistory = () => {
    if (previousSessions.length === 0) {
      setError('Geçmiş seans bulunamadı');
      return;
    }

    const context = previousSessions
      .slice(0, 3) // Son 3 seans
      .map((note, idx) => `Geçmiş Seans ${idx + 1}:\n${note.substring(0, 200)}...`)
      .join('\n\n');

    setTranscript(prev => prev + (prev ? '\n\n--- Geçmiş Seanslar ---\n\n' : '') + context);
  };

  React.useEffect(() => {
    setHasPassphrase(hasPassphraseConfigured());
  }, []);

  const onAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || !clientId) return;
    
    try {
      let encryptedContent: string;
      if (hasPassphrase) {
        if (!passphrase) {
          setError("Lütfen passphrase giriniz");
          return;
        }
        encryptedContent = await encryptNoteWithPassphrase(content, passphrase);
      } else {
        encryptedContent = await encryptNote(content);
      }
      const { error: err } = await supabase.from("notes").insert({ 
        client_id: clientId, 
        type: noteType, 
        content_encrypted: encryptedContent 
      });
      if (err) throw err;
      setContent("");
      setClientId("");
      setNoteType("SOAP");
      fetchAll();
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "Insert failed";
      setError(errorMessage);
    }
  };

  const onDelete = async (id: string) => {
    try {
      const { error: err } = await supabase.from("notes").delete().eq("id", id);
      if (err) throw err;
      fetchAll();
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "Delete failed";
      setError(errorMessage);
    }
  };

  // Risk analizi fonksiyonu
  const analyzeRisk = (text: string): { level: 'high' | 'medium' | 'low'; keywords: string[] } | null => {
    const riskKeywords = {
      high: ['intihar', 'ölmek', 'kendimi öldürmek', 'yaşamak istemiyorum', 'zarar vermek', 'şiddet', 'saldırmak'],
      medium: ['umutsuz', 'çaresiz', 'hiçbir şey işe yaramıyor', 'aşırı alkol', 'uyuşturucu', 'overdose'],
      low: ['kaygı', 'panik', 'depresyon', 'üzgün', 'mutsuz', 'enerjisiz'],
    };

    const foundKeywords: string[] = [];
    let maxLevel: 'high' | 'medium' | 'low' | null = null;

    const lowerText = text.toLowerCase();

    // High risk kontrolü
    for (const keyword of riskKeywords.high) {
      if (lowerText.includes(keyword)) {
        foundKeywords.push(keyword);
        maxLevel = 'high';
      }
    }

    // Medium risk kontrolü (high yoksa)
    if (maxLevel !== 'high') {
      for (const keyword of riskKeywords.medium) {
        if (lowerText.includes(keyword)) {
          foundKeywords.push(keyword);
          if (maxLevel !== 'high') maxLevel = 'medium';
        }
      }
    }

    // Low risk kontrolü (high ve medium yoksa)
    if (maxLevel !== 'high' && maxLevel !== 'medium') {
      for (const keyword of riskKeywords.low) {
        if (lowerText.includes(keyword)) {
          foundKeywords.push(keyword);
          if (!maxLevel) maxLevel = 'low';
        }
      }
    }

    return maxLevel ? { level: maxLevel, keywords: foundKeywords } : null;
  };

  // Word export fonksiyonu
  const exportToWord = async () => {
    if (!soapData) return;
    
    try {
      const client = clients.find(c => c.id === clientId);
      await exportSOAPToWord(soapData, client?.name, new Date());
      toast({
        title: "Word İndirildi",
        description: "SOAP notu Word formatında indirildi",
        variant: "success",
      });
    } catch (error) {
      console.error('Word export hatası:', error);
      toast({
        title: "Hata",
        description: "Word dosyası oluşturulamadı",
        variant: "error",
      });
    }
  };

  // Paylaşım linki oluştur
  const createShareLink = async () => {
    if (!soapData || !clientId) return;
    
    try {
      // Basit ID oluştur (gerçekte veritabanından gelmeli)
      const soapId = `soap-${Date.now()}-${clientId}`;
      const link = generateShareLink(soapId);
      setShareLink(link);
      
      // QR kod oluştur
      const qr = await generateQRCode(link);
      setQrCodeUrl(qr);
      
      setShowShareModal(true);
    } catch (error) {
      console.error('Paylaşım linki hatası:', error);
      toast({
        title: "Hata",
        description: "Paylaşım linki oluşturulamadı",
        variant: "error",
      });
    }
  };

  // Link'i kopyala
  const copyShareLink = () => {
    if (shareLink) {
      navigator.clipboard.writeText(shareLink);
      toast({
        title: "Kopyalandı",
        description: "Paylaşım linki kopyalandı",
        variant: "success",
      });
    }
  };

  // PDF export fonksiyonu (geliştirilmiş)
  const exportToPDF = async () => {
    if (!soapData) return;

    try {
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'A4'
      });
      
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - (margin * 2);
      
      // Header
      doc.setFillColor(59, 130, 246); // Blue
      doc.rect(0, 0, pageWidth, 30, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(20);
      doc.setFont(undefined, 'bold');
      doc.text('SOAP Notu', margin, 20);
      
      // Client bilgisi
      const client = clients.find(c => c.id === clientId);
      if (client) {
        doc.setFontSize(12);
        doc.text(`Hasta: ${client.name}`, margin, 28);
      }
      
      // Tarih ve saat
      doc.setFontSize(10);
      doc.text(
        `Tarih: ${new Date().toLocaleDateString('tr-TR')} ${new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}`,
        pageWidth - margin - 60,
        28
      );
      
      // Content başlangıcı
      doc.setTextColor(0, 0, 0);
      let y = 40;
      
      // Subjective
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.setFillColor(239, 246, 255); // Light blue
      doc.rect(margin, y - 5, contentWidth, 8, 'F');
      doc.text('S - Subjective (Öznel)', margin + 2, y);
      
      doc.setFontSize(11);
      doc.setFont(undefined, 'normal');
      const subjectiveLines = doc.splitTextToSize(soapData.subjective || '(Boş)', contentWidth - 4);
      doc.text(subjectiveLines, margin + 2, y + 8);
      y += subjectiveLines.length * 5 + 15;
      
      // Sayfa kontrolü
      if (y > pageHeight - 30) {
        doc.addPage();
        y = 20;
      }
      
      // Objective
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.setFillColor(240, 253, 244); // Light green
      doc.rect(margin, y - 5, contentWidth, 8, 'F');
      doc.text('O - Objective (Nesnel)', margin + 2, y);
      
      doc.setFontSize(11);
      doc.setFont(undefined, 'normal');
      const objectiveLines = doc.splitTextToSize(soapData.objective || '(Boş)', contentWidth - 4);
      doc.text(objectiveLines, margin + 2, y + 8);
      y += objectiveLines.length * 5 + 15;
      
      // Sayfa kontrolü
      if (y > pageHeight - 30) {
        doc.addPage();
        y = 20;
      }
      
      // Assessment
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.setFillColor(255, 251, 235); // Light yellow
      doc.rect(margin, y - 5, contentWidth, 8, 'F');
      doc.text('A - Assessment (Değerlendirme)', margin + 2, y);
      
      doc.setFontSize(11);
      doc.setFont(undefined, 'normal');
      const assessmentLines = doc.splitTextToSize(soapData.assessment || '(Boş)', contentWidth - 4);
      doc.text(assessmentLines, margin + 2, y + 8);
      y += assessmentLines.length * 5 + 15;
      
      // Sayfa kontrolü
      if (y > pageHeight - 30) {
        doc.addPage();
        y = 20;
      }
      
      // Plan
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.setFillColor(253, 244, 255); // Light purple
      doc.rect(margin, y - 5, contentWidth, 8, 'F');
      doc.text('P - Plan (Plan)', margin + 2, y);
      
      doc.setFontSize(11);
      doc.setFont(undefined, 'normal');
      const planLines = doc.splitTextToSize(soapData.plan || '(Boş)', contentWidth - 4);
      doc.text(planLines, margin + 2, y + 8);
      
      // Footer (her sayfada)
      const totalPages = doc.internal.pages.length - 1;
      for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(128, 128, 128);
        doc.text(
          `Sayfa ${i} / ${totalPages}`,
          pageWidth / 2,
          pageHeight - 10,
          { align: 'center' }
        );
        
        // Risk bilgisi (ilk sayfada)
        if (i === 1 && riskDetected) {
          doc.setFontSize(9);
          doc.setTextColor(
            riskDetected.level === 'high' ? 220 : 
            riskDetected.level === 'medium' ? 200 : 
            100,
            riskDetected.level === 'high' ? 38 : 
            riskDetected.level === 'medium' ? 100 : 
            100,
            riskDetected.level === 'high' ? 38 : 
            riskDetected.level === 'medium' ? 50 : 
            100
          );
          doc.text(
            `⚠️ Risk Seviyesi: ${riskDetected.level === 'high' ? 'YÜKSEK' : riskDetected.level === 'medium' ? 'ORTA' : 'DÜŞÜK'}`,
            margin,
            pageHeight - 10
          );
        }
      }
      
      // Dosya adı
      const fileName = `SOAP-${client?.name || 'Hasta'}-${new Date().toISOString().split('T')[0]}.pdf`;
      doc.save(fileName);
      
      console.log('✅ PDF başarıyla oluşturuldu:', fileName);
      toast({
        title: "PDF İndirildi",
        description: fileName,
        variant: "success",
      });
    } catch (error) {
      console.error('PDF export hatası:', error);
      setError('PDF oluşturulamadı');
    }
  };

  const handleAIGenerate = async () => {
    // Eğer transkript varsa, direkt SOAP oluştur (Gemini ile)
    if (transcript.trim()) {
      setAiLoading(true);
      setError(null);
      setRiskDetected(null);
      
      // Risk analizi yap
      const risk = analyzeRisk(transcript);
      if (risk) {
        setRiskDetected(risk);
        
        // Risk'i veritabanına kaydet
        if (clientId) {
          try {
            const riskLog = await logRisk({
              client_id: clientId,
              risk_level: risk.level,
              keywords: risk.keywords,
              transcript_snippet: transcript,
            });
            
            // Bildirim gönder
            if (riskLog && risk.level === 'high') {
              await sendRiskNotifications(riskLog);
            }
          } catch (error) {
            console.warn('Risk loglama hatası:', error);
            // Devam et, kritik değil
          }
        }
      }
      
      try {
        const response = await fetch('/api/telehealth/generate-soap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            transcript: transcript,
            mode: analysisMode,
            clientId: clientId || undefined,
            sessionId: undefined,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || 'SOAP notu oluşturulamadı');
        }

        const data = await response.json();
        
        // SOAP verisini kaydet
        setSoapData(data.soap);
        
        // SOAP notunu formatla
        const formattedSOAP = `S (Subjective):\n${data.soap.subjective}\n\nO (Objective):\n${data.soap.objective}\n\nA (Assessment):\n${data.soap.assessment}\n\nP (Plan):\n${data.soap.plan}`;
        
        setContent(formattedSOAP);
        setNoteType('SOAP');
        
        // Versiyonlama ve otomatik kaydetme (eğer clientId varsa)
        if (clientId) {
          try {
            // Versiyonu kaydet
            const version = await saveSOAPVersion(
              clientId,
              data.soap,
              undefined, // sessionId
              `Otomatik oluşturuldu - Mod: ${analysisMode}`
            );
            
            if (version) {
              setCurrentVersion(version.version);
              // Versiyonları yeniden yükle
              const versions = await getSOAPVersions(clientId, 10);
              setSoapVersions(versions);
            }
            
            // Normal not olarak da kaydet
            let encryptedContent: string;
            if (hasPassphrase && passphrase) {
              encryptedContent = await encryptNoteWithPassphrase(formattedSOAP, passphrase);
            } else {
              encryptedContent = await encryptNote(formattedSOAP);
            }
            
            await supabase.from("notes").insert({ 
              client_id: clientId, 
              type: 'SOAP', 
              content_encrypted: encryptedContent 
            });
            
            fetchAll();
            console.log('✅ SOAP notu otomatik olarak kaydedildi ve versiyonlandı!');
          } catch (saveError) {
            console.warn('⚠️ SOAP notu kaydedilemedi:', saveError);
            // Hata olsa bile devam et
          }
        }
        
        // Başarı mesajı
        console.log('✅ SOAP notu başarıyla oluşturuldu!', data.mode);
        toast({
          title: "✅ SOAP Notu Oluşturuldu",
          description: `${data.mode === 'standard' ? 'Standart' : data.mode === 'premium' ? 'Premium' : 'Konsültasyon'} mod ile oluşturuldu`,
          variant: "success",
        });
        setShowSOAPDisplay(true);
        
      } catch (e: unknown) {
        const errorMessage = e instanceof Error ? e.message : "SOAP notu oluşturulamadı";
        setError(errorMessage);
        console.error('SOAP oluşturma hatası:', e);
      } finally {
        setAiLoading(false);
      }
      return;
    }

    // Eski yöntem: Form verileriyle not oluştur
    if (!aiNoteData.clientName || !aiNoteData.sessionFocus) {
      setError("Please fill in client name and session focus, or enter a transcript");
      return;
    }

    setAiLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/ai-notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'generate',
          data: aiNoteData
        })
      });

      if (!response.ok) {
        throw new Error('AI note generation failed');
      }

      const result: AINoteResponse = await response.json();
      setAiResponse(result);
      setContent(result.note);
      setNoteType(aiNoteData.noteType);
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "AI generation failed";
      setError(errorMessage);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAIEnhance = async () => {
    if (!content.trim()) {
      setError("Please enter note content to enhance");
      return;
    }

    setAiLoading(true);
    setError(null);
    
    try {
      const client = clients.find(c => c.id === clientId);
      const clientContext = client ? `Client: ${client.name}` : "Client context not available";
      
      const response = await fetch('/api/ai-notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'enhance',
          data: { note: content, clientContext }
        })
      });

      if (!response.ok) {
        throw new Error('AI enhancement failed');
      }

      const result = await response.json();
      setContent(result.enhancedNote);
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : "AI enhancement failed";
      setError(errorMessage);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Passphrase setup */}
      <div className="border rounded p-3 bg-yellow-50">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Not Şifreleme</span>
          <span className={`text-xs px-2 py-0.5 rounded ${hasPassphrase ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {hasPassphrase ? "Passphrase aktif" : "Passphrase ayarlı değil"}
          </span>
        </div>
        {!hasPassphrase && (
          <div className="mt-2 flex gap-2 items-end">
            <div className="flex-1">
              <label className="text-xs block mb-1">Passphrase</label>
              <input
                type="password"
                value={passphrase}
                onChange={(e) => setPassphraseInput(e.target.value)}
                className="border rounded px-3 py-2 w-full"
                placeholder="Notları şifrelemek için ikinci şifre"
              />
            </div>
            <button
              className="border rounded px-3 py-2"
              onClick={async () => {
                try {
                  if (!passphrase) {
                    setError("Passphrase boş olamaz");
                    return;
                  }
                  await setPassphrase(passphrase);
                  setHasPassphrase(true);
                } catch (e: unknown) {
                  const msg = e instanceof Error ? e.message : "Passphrase ayarlanamadı";
                  setError(msg);
                }
              }}
            >
              Kaydet
            </button>
          </div>
        )}
        {hasPassphrase && (
          <div className="mt-2">
            <label className="text-xs block mb-1">Passphrase</label>
            <input
              type="password"
              value={passphrase}
              onChange={(e) => setPassphraseInput(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              placeholder="Deşifre için passphrase giriniz"
            />
          </div>
        )}
      </div>
      {/* AI Note Assistant Toggle */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Clinical Notes</h3>
        <button
          onClick={() => setShowAIAssistant(!showAIAssistant)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {showAIAssistant ? "Hide" : "Show"} AI Assistant
        </button>
      </div>

      {/* AI Note Assistant Panel */}
      {showAIAssistant && (
        <div className="border rounded-lg p-4 bg-blue-50">
          <h4 className="font-semibold mb-3 text-blue-800">🤖 AI Note Assistant</h4>
          
          {/* Template Seçimi */}
          <div className="mb-4 p-3 bg-indigo-50 rounded border border-indigo-200">
            <label className="text-xs block mb-2 font-semibold text-indigo-800">📋 SOAP Template Seç</label>
            <select
              value={selectedTemplate}
              onChange={(e) => {
                setSelectedTemplate(e.target.value);
                if (e.target.value) {
                  applySOAPTemplate(e.target.value);
                }
              }}
              className="w-full border rounded px-3 py-2 text-sm"
            >
              <option value="">Template seçiniz...</option>
              {DEFAULT_TEMPLATES.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name} - {template.description}
                </option>
              ))}
            </select>
          </div>

          {/* Geçmiş Seanslar Context */}
          {clientId && previousSessions.length > 0 && (
            <div className="mb-4 p-3 bg-purple-50 rounded border border-purple-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold text-purple-800">
                  📚 Geçmiş Seanslar ({previousSessions.length} adet)
                </span>
                <button
                  type="button"
                  onClick={addContextFromHistory}
                  className="text-xs px-2 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
                  disabled={loadingHistory}
                >
                  {loadingHistory ? 'Yükleniyor...' : 'Context Ekle'}
                </button>
              </div>
              <p className="text-xs text-purple-700">
                Geçmiş seanslardan context ekleyerek daha iyi SOAP notu oluşturabilirsiniz.
              </p>
            </div>
          )}

          {/* Transcript Input (Gemini SOAP için) */}
          <div className="mb-4 p-3 bg-white rounded border">
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs block font-semibold">📝 Seans Transkripti (SOAP Notu için)</label>
              <div className="flex gap-2">
                {/* Konuşmacı Seçimi */}
                <select
                  value={currentSpeaker}
                  onChange={(e) => setCurrentSpeaker(e.target.value as 'patient' | 'therapist')}
                  className="text-xs px-2 py-1 border rounded bg-white"
                  disabled={isRecording}
                >
                  <option value="patient">👤 Danışan</option>
                  <option value="therapist">👨‍⚕️ Terapist</option>
                </select>
                
                {/* Canlı Transkript Butonu */}
                {isSpeechRecognitionSupported() && (
                  <button
                    type="button"
                    onClick={isRecording ? stopLiveTranscription : startLiveTranscription}
                    className={`text-xs px-3 py-1 rounded text-white ${
                      isRecording 
                        ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                        : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  >
                    {isRecording ? (
                      <span className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                        Durdur ({Math.floor(recordingTime / 60)}:{(recordingTime % 60).toString().padStart(2, '0')})
                      </span>
                    ) : (
                      '🎤 Canlı Transkript'
                    )}
                  </button>
                )}
                
                {/* Ses Kaydı Butonu */}
                <button
                  type="button"
                  onClick={isRecording ? stopAudioRecording : startAudioRecording}
                  className={`text-xs px-3 py-1 rounded ${
                    isRecording 
                      ? 'bg-red-600 text-white hover:bg-red-700' 
                      : 'bg-gray-600 text-white hover:bg-gray-700'
                  }`}
                  disabled={isTranscribing}
                >
                  {isTranscribing ? '⏳ İşleniyor...' : isRecording ? '⏹️ Durdur' : '🎙️ Ses Kaydet'}
                </button>
              </div>
            </div>
            
            {/* Ses Seviyesi Göstergesi */}
            {isRecording && audioLevel > 0 && (
              <div className="mb-2">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 transition-all duration-100"
                      style={{ width: `${audioLevel}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-600">{Math.round(audioLevel)}%</span>
                </div>
              </div>
            )}
            
            <textarea
              value={transcript}
              onChange={(e) => {
                setTranscript(e.target.value);
                // Real-time risk analizi
                if (e.target.value.trim()) {
                  const risk = analyzeRisk(e.target.value);
                  setRiskDetected(risk);
                } else {
                  setRiskDetected(null);
                }
              }}
              placeholder={
                isRecording 
                  ? "🎤 Konuşun... Transkript buraya yazılacak..."
                  : "Seans transkriptini buraya yapıştır veya yukarıdaki butonlarla kaydet... (Örn: Terapist: Merhaba... Danışan: İyi değilim...)"
              }
              className="border rounded px-3 py-2 w-full"
              rows={6}
              disabled={isRecording && isTranscribing}
            />
            
            {/* Risk Uyarısı */}
            {riskDetected && (
              <div className={`mt-2 p-2 rounded text-xs ${
                riskDetected.level === 'high' ? 'bg-red-100 text-red-800 border border-red-300' :
                riskDetected.level === 'medium' ? 'bg-yellow-100 text-yellow-800 border border-yellow-300' :
                'bg-blue-100 text-blue-800 border border-blue-300'
              }`}>
                <span className="font-semibold">
                  ⚠️ {riskDetected.level === 'high' ? 'YÜKSEK RİSK' : riskDetected.level === 'medium' ? 'ORTA RİSK' : 'DÜŞÜK RİSK'} TESPİT EDİLDİ:
                </span>
                <div className="mt-1">
                  Tespit edilen kelimeler: {riskDetected.keywords.join(', ')}
                </div>
              </div>
            )}
            
            <div className="mt-2 flex gap-2 items-center flex-wrap">
              <span className="text-xs text-muted-foreground">Analiz Modu:</span>
              <button
                type="button"
                onClick={() => setAnalysisMode('standard')}
                className={`text-xs px-2 py-1 rounded ${analysisMode === 'standard' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              >
                Standart
              </button>
              <button
                type="button"
                onClick={() => setAnalysisMode('premium')}
                className={`text-xs px-2 py-1 rounded ${analysisMode === 'premium' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              >
                🔬 Premium
              </button>
              <button
                type="button"
                onClick={() => setAnalysisMode('consultation')}
                className={`text-xs px-2 py-1 rounded ${analysisMode === 'consultation' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              >
                👥 Konsültasyon
              </button>
              
              {/* Ses Komutları */}
              {isSpeechRecognitionSupported() && (
                <button
                  type="button"
                  onClick={() => setVoiceCommandsEnabled(!voiceCommandsEnabled)}
                  className={`text-xs px-2 py-1 rounded ${
                    voiceCommandsEnabled 
                      ? 'bg-green-600 text-white' 
                      : 'bg-gray-200'
                  }`}
                >
                  {voiceCommandsEnabled ? '🎤 Komutlar Aktif' : '🎤 Ses Komutları'}
                </button>
              )}
            </div>
            
            {/* Ses Komutları Bilgisi */}
            {voiceCommandsEnabled && (
              <div className="mt-2 p-2 bg-green-50 rounded text-xs text-green-800">
                <strong>🎤 Ses Komutları Aktif:</strong> "SOAP oluştur", "Durdur", "Temizle", "PDF indir"
              </div>
            )}
          </div>
          
          {/* Trend Analizi */}
          {trendAnalysis && (
            <div className="mb-4 p-3 bg-yellow-50 rounded border border-yellow-200">
              <h5 className="text-xs font-semibold mb-2 text-yellow-800">📈 Trend Analizi</h5>
              <div className="space-y-1 text-xs">
                <div>
                  <strong>Genel Trend:</strong> {
                    trendAnalysis.overallTrend === 'improving' ? '📈 İyileşiyor' :
                    trendAnalysis.overallTrend === 'declining' ? '📉 Kötüleşiyor' :
                    '➡️ Stabil'
                  }
                </div>
                <div>
                  <strong>Risk Trend:</strong> {
                    trendAnalysis.riskTrend === 'decreasing' ? '✅ Azalıyor' :
                    trendAnalysis.riskTrend === 'increasing' ? '⚠️ Artıyor' :
                    '➡️ Stabil'
                  }
                </div>
                <div>
                  <strong>İlerleme Skoru:</strong> {trendAnalysis.progressScore}/100
                </div>
                {trendAnalysis.keyFindings.length > 0 && (
                  <div className="mt-2">
                    <strong>Bulgular:</strong>
                    <ul className="list-disc list-inside ml-2">
                      {trendAnalysis.keyFindings.map((f: string, idx: number) => (
                        <li key={idx}>{f}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* SOAP Sonuçları ve Export */}
          {soapData && (
            <div className="mb-4 space-y-4">
              <div className="p-3 bg-green-50 rounded border border-green-200">
                <div className="flex justify-between items-center mb-2">
                  <h5 className="font-semibold text-green-800">
                    ✅ SOAP Notu Oluşturuldu
                    {currentVersion && ` (v${currentVersion})`}
                  </h5>
                  <div className="flex gap-2 flex-wrap">
                    <button
                      onClick={() => setShowSOAPDisplay(!showSOAPDisplay)}
                      className="text-xs px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                    >
                      {showSOAPDisplay ? '📄 Liste Görünümü' : '🎨 Kart Görünümü'}
                    </button>
                    {soapVersions.length > 1 && (
                      <>
                        <select
                          value={currentVersion || ''}
                          onChange={(e) => restoreVersion(parseInt(e.target.value))}
                          className="text-xs px-2 py-1 border rounded bg-white"
                        >
                          <option value="">Versiyon Seç</option>
                          {soapVersions.map((v) => (
                            <option key={v.id} value={v.version}>
                              v{v.version} - {new Date(v.created_at).toLocaleDateString('tr-TR')}
                            </option>
                          ))}
                        </select>
                        {soapVersions.length >= 2 && (
                          <button
                            onClick={() => handleCompareVersions(
                              soapVersions[1].version,
                              soapVersions[0].version
                            )}
                            className="text-xs px-2 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
                          >
                            🔍 Karşılaştır
                          </button>
                        )}
                      </>
                    )}
                    <button
                      onClick={loadEditSuggestions}
                      disabled={aiLoading}
                      className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      {aiLoading ? '...' : '💡 AI Önerileri'}
                    </button>
                    <button
                      onClick={exportToPDF}
                      className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      📄 PDF
                    </button>
                    <button
                      onClick={exportToWord}
                      className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      📝 Word
                    </button>
                    <button
                      onClick={createShareLink}
                      className="text-xs px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
                    >
                      🔗 Paylaş
                    </button>
                  </div>
                </div>
                <div className="text-xs text-green-700">
                  Mod: {analysisMode === 'standard' ? 'Standart' : analysisMode === 'premium' ? 'Premium' : 'Konsültasyon'}
                  {riskDetected && ` | Risk: ${riskDetected.level === 'high' ? 'Yüksek' : riskDetected.level === 'medium' ? 'Orta' : 'Düşük'}`}
                  {soapVersions.length > 0 && ` | ${soapVersions.length} versiyon`}
                </div>
                
                {/* AI Önerileri */}
                {editSuggestions.length > 0 && (
                  <div className="mt-3 p-2 bg-white rounded border">
                    <h6 className="text-xs font-semibold mb-2">💡 AI Önerileri:</h6>
                    <div className="space-y-2">
                      {editSuggestions.slice(0, 3).map((suggestion, idx) => (
                        <div key={idx} className="text-xs p-2 bg-blue-50 rounded">
                          <strong>{suggestion.section}:</strong> {suggestion.reason}
                          <button
                            onClick={() => handleEditSection(suggestion.section, suggestion.reason)}
                            className="ml-2 text-blue-600 hover:underline"
                          >
                            Uygula
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* SOAP Display (Kart Görünümü) */}
              {showSOAPDisplay && (
                <ErrorBoundary>
                  <div className="space-y-4">
                    <div className="p-4 bg-white rounded-lg border shadow-sm">
                      <SOAPDisplay
                        soap={soapData}
                        onEdit={(section) => {
                          setEditingSection(section);
                          toast({
                            title: "Düzenleme Modu",
                            description: `${section} bölümü düzenleniyor...`,
                            variant: "default",
                          });
                        }}
                        onCopy={(section, content) => {
                          navigator.clipboard.writeText(content);
                          toast({
                            title: "Kopyalandı",
                            description: `${section} bölümü kopyalandı`,
                            variant: "success",
                          });
                        }}
                        collapsible={true}
                      />
                    </div>
                    
                    {/* Feedback Widget */}
                    <FeedbackWidget 
                      soapId={currentNoteId || undefined}
                      sessionId={sessionId || undefined}
                    />
                  </div>
                </ErrorBoundary>
              )}
            </div>
          )}
          
          {/* Paylaşım Modal */}
          {showShareModal && shareLink && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-md w-full">
                <h3 className="text-lg font-semibold mb-4">🔗 Paylaşım Linki</h3>
                
                <div className="space-y-4">
                  {/* QR Kod */}
                  {qrCodeUrl && (
                    <div className="flex justify-center">
                      <img src={qrCodeUrl} alt="QR Code" className="w-48 h-48 border rounded" />
                    </div>
                  )}
                  
                  {/* Link */}
                  <div>
                    <label className="text-xs block mb-1">Paylaşım Linki:</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={shareLink}
                        readOnly
                        className="flex-1 border rounded px-3 py-2 text-sm"
                      />
                      <button
                        onClick={copyShareLink}
                        className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Kopyala
                      </button>
                    </div>
                  </div>
                  
                  {/* Email Gönder (gelecek) */}
                  <div className="text-xs text-gray-500">
                    💡 Email gönderme özelliği yakında eklenecek
                  </div>
                </div>
                
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={() => {
                      setShowShareModal(false);
                      setShareLink(null);
                      setQrCodeUrl(null);
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Kapat
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Toast Container */}
          <ToastContainer 
            toasts={toasts} 
            onRemove={(id) => {
              // Toast'ları kaldır (useToast hook'u otomatik yönetiyor)
            }}
          />

          {/* Versiyon Karşılaştırma Modal */}
          {comparingVersions && version1Data && version2Data && (
            <VersionComparison
              version1={version1Data}
              version2={version2Data}
              onClose={() => {
                setComparingVersions(null);
                setVersion1Data(null);
                setVersion2Data(null);
              }}
            />
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs block mb-1">Client Name</label>
              <input
                value={aiNoteData.clientName}
                onChange={(e) => setAiNoteData({...aiNoteData, clientName: e.target.value})}
                placeholder="Client name"
                className="border rounded px-3 py-2 w-full"
              />
            </div>
            <div>
              <label className="text-xs block mb-1">Session Type</label>
              <select
                value={aiNoteData.sessionType}
                onChange={(e) => setAiNoteData({...aiNoteData, sessionType: e.target.value as "initial" | "follow-up" | "crisis" | "termination"})}
                className="border rounded px-3 py-2 w-full"
              >
                <option value="initial">Initial</option>
                <option value="follow-up">Follow-up</option>
                <option value="crisis">Crisis</option>
                <option value="termination">Termination</option>
              </select>
            </div>
            <div>
              <label className="text-xs block mb-1">Session Focus</label>
              <input
                value={aiNoteData.sessionFocus}
                onChange={(e) => setAiNoteData({...aiNoteData, sessionFocus: e.target.value})}
                placeholder="Main focus of session"
                className="border rounded px-3 py-2 w-full"
              />
            </div>
            <div>
              <label className="text-xs block mb-1">Note Type</label>
              <select
                value={aiNoteData.noteType}
                onChange={(e) => setAiNoteData({...aiNoteData, noteType: e.target.value as "SOAP" | "BIRP" | "DAP"})}
                className="border rounded px-3 py-2 w-full"
              >
                <option value="SOAP">SOAP</option>
                <option value="BIRP">BIRP</option>
                <option value="DAP">DAP</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="text-xs block mb-1">Client Presentation</label>
              <textarea
                value={aiNoteData.clientPresentation}
                onChange={(e) => setAiNoteData({...aiNoteData, clientPresentation: e.target.value})}
                placeholder="How client presented"
                className="border rounded px-3 py-2 w-full h-20"
              />
            </div>
            <div>
              <label className="text-xs block mb-1">Interventions</label>
              <textarea
                value={aiNoteData.interventions}
                onChange={(e) => setAiNoteData({...aiNoteData, interventions: e.target.value})}
                placeholder="Interventions used"
                className="border rounded px-3 py-2 w-full h-20"
              />
            </div>
            <div>
              <label className="text-xs block mb-1">Progress & Next Steps</label>
              <textarea
                value={aiNoteData.progress}
                onChange={(e) => setAiNoteData({...aiNoteData, progress: e.target.value})}
                placeholder="Progress made and next steps"
                className="border rounded px-3 py-2 w-full h-20"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleAIGenerate}
              disabled={aiLoading || (!transcript.trim() && (!aiNoteData.clientName || !aiNoteData.sessionFocus))}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition-all duration-200 flex items-center gap-2"
            >
              {aiLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>{transcript.trim() ? "SOAP Notu Oluşturuluyor..." : "Generating..."}</span>
                </>
              ) : (
                <>
                  <span>🤖</span>
                  <span>{transcript.trim() ? "Gemini ile SOAP Notu Oluştur" : "Generate AI Note"}</span>
                </>
              )}
            </button>
            
            {/* Loading Skeleton */}
            {aiLoading && !soapData && (
              <div className="mt-4">
                <SOAPSkeleton />
              </div>
            )}
            <button
              onClick={handleAIEnhance}
              disabled={aiLoading || !content.trim()}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
            >
              {aiLoading ? "Enhancing..." : "✨ Enhance Note"}
            </button>
          </div>

          {/* AI Response Display */}
          {aiResponse && (
            <div className="mt-4 p-3 bg-white rounded border">
              <h5 className="font-semibold mb-2">AI Suggestions:</h5>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <strong>Clinical Suggestions:</strong>
                  <ul className="list-disc list-inside mt-1">
                    {aiResponse.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div>
                  <strong>Risk Factors:</strong>
                  <ul className="list-disc list-inside mt-1">
                    {aiResponse.riskFactors.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
                <div>
                  <strong>Follow-up Questions:</strong>
                  <ul className="list-disc list-inside mt-1">
                    {aiResponse.followUpQuestions.map((q, i) => <li key={i}>{q}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Regular Note Form */}
      <form onSubmit={onAdd} className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-end">
        <div>
          <label className="text-xs block mb-1">Client</label>
          <select value={clientId} onChange={(e) => setClientId(e.target.value)} className="border rounded px-3 py-2 w-full">
            <option value="">Select client…</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs block mb-1">Type</label>
          <select value={noteType} onChange={(e) => setNoteType(e.target.value as typeof NOTE_TYPES[number])} className="border rounded px-3 py-2 w-full">
            {NOTE_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs block">Content</label>
            <div className="flex gap-1">
              {NOTE_TYPES.map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => applyTemplate(t)}
                  className="text-[10px] border px-2 py-0.5 rounded bg-gray-50 hover:bg-gray-100"
                  title={`${t} template`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Note content..."
            className="border rounded px-3 py-2 w-full"
            rows={3}
          />
        </div>
        <button type="submit" className="border rounded px-3 py-2">Add</button>
      </form>

      {error && <div className="text-sm text-red-600">{error}</div>}

      {loading ? (
        <div>Loading…</div>
      ) : (
        <div className="border rounded">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted text-left">
                <th className="p-2">Client</th>
                <th className="p-2">Type</th>
                <th className="p-2">Content</th>
                <th className="p-2">Created</th>
                <th className="p-2" />
              </tr>
            </thead>
            <tbody>
              {notes.map((n) => {
                const c = clients.find((x) => x.id === n.client_id);
                return (
                  <tr key={n.id} className="border-t">
                    <td className="p-2">{c?.name ?? n.client_id}</td>
                    <td className="p-2">{n.type}</td>
                    <td className="p-2">
                      <button
                        onClick={async () => {
                          try {
                            const decrypted = hasPassphrase && passphrase
                              ? await decryptNoteWithPassphrase(n.content_encrypted, passphrase)
                              : await decryptNote(n.content_encrypted);
                            alert(decrypted);
                          } catch (e: unknown) {
                            const errorMessage = e instanceof Error ? e.message : "Decrypt failed";
                            alert(errorMessage);
                          }
                        }}
                        className="text-xs border px-2 py-1 rounded"
                      >
                        View (Decrypted)
                      </button>
                    </td>
                    <td className="p-2">{new Date(n.created_at).toLocaleString()}</td>
                    <td className="p-2 text-right">
                      <button
                        className="text-xs border px-2 py-1 rounded"
                        onClick={() => onDelete(n.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
              {notes.length === 0 && (
                <tr>
                  <td className="p-4 text-muted-foreground" colSpan={5}>No notes</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}


