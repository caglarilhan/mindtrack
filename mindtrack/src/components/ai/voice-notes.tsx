'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { 
  Mic, 
  MicOff, 
  Play, 
  Pause, 
  Square, 
  Download, 
  Upload, 
  FileText, 
  Brain, 
  Zap, 
  Clock, 
  Calendar, 
  User, 
  MessageSquare, 
  Volume2, 
  VolumeX, 
  Settings, 
  Edit, 
  Trash2, 
  Share2, 
  Eye, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Warning, 
  Check, 
  X, 
  ArrowRight, 
  ArrowLeft, 
  Home, 
  MapPin, 
  Compass, 
  Navigation,
  Sparkles,
  Cpu,
  Database,
  Network,
  Shield,
  Star,
  Award,
  Trophy,
  Rocket,
  Gem,
  Crown,
  Diamond,
  Flame,
  Thunder,
  Sun,
  Moon,
  Cloud,
  Rainbow,
  Waves,
  Music,
  Headphones,
  Radio,
  Disc,
  Disc3,
  SkipBack,
  SkipForward,
  Repeat,
  Shuffle,
  Volume1,
  Volume
} from 'lucide-react';

interface VoiceNote {
  id: string;
  patientId: string;
  providerId: string;
  title: string;
  duration: number;
  audioUrl: string;
  transcription: string;
  summary: string;
  keywords: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
  confidence: number;
  createdAt: string;
  isProcessed: boolean;
  tags: string[];
}

interface VoiceNotesProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function VoiceNotes({ patientId, providerId, providerType }: VoiceNotesProps) {
  const [voiceNotes, setVoiceNotes] = useState<VoiceNote[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentNote, setCurrentNote] = useState<VoiceNote | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<'record' | 'notes' | 'transcriptions'>('record');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadVoiceNotes();
  }, [patientId]);

  const loadVoiceNotes = async () => {
    try {
      const response = await fetch(`/api/ai/voice-notes?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setVoiceNotes(data.notes || []);
      }
    } catch (error) {
      console.error('Error loading voice notes:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const audioChunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await uploadVoiceNote(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const uploadVoiceNote = async (audioBlob: Blob) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, `voice-note-${Date.now()}.wav`);
      formData.append('patientId', patientId);
      formData.append('providerId', providerId);

      const response = await fetch('/api/ai/voice-notes', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        await loadVoiceNotes();
      }
    } catch (error) {
      console.error('Error uploading voice note:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const playVoiceNote = (note: VoiceNote) => {
    if (audioRef.current) {
      audioRef.current.src = note.audioUrl;
      audioRef.current.play();
      setIsPlaying(true);
      setCurrentNote(note);
    }
  };

  const pauseVoiceNote = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'neutral': return 'bg-gray-100 text-gray-800';
      case 'negative': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderVoiceNote = (note: VoiceNote) => (
    <Card key={note.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Mic className="h-5 w-5 text-blue-600" />
            <div>
              <CardTitle className="text-lg">{note.title}</CardTitle>
              <CardDescription>
                {new Date(note.createdAt).toLocaleDateString()} • {formatTime(note.duration)}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getSentimentColor(note.sentiment)}>
              {note.sentiment}
            </Badge>
            <Badge variant="outline">
              {note.confidence}% confidence
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => playVoiceNote(note)}
            >
              <Play className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {note.summary && (
            <div>
              <Label className="text-sm font-medium">AI Summary</Label>
              <div className="text-sm text-muted-foreground">{note.summary}</div>
            </div>
          )}
          {note.keywords.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Keywords</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {note.keywords.map((keyword, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {keyword}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          {note.tags.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Tags</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {note.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-2">
            <Mic className="h-8 w-8 text-blue-600" />
            <span>Voice Notes</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            Record session notes with AI-powered transcription and analysis
          </p>
        </div>
      </div>

      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'record' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('record')}
          className="flex-1"
        >
          <Mic className="h-4 w-4 mr-2" />
          Record
        </Button>
        <Button
          variant={activeTab === 'notes' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('notes')}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-2" />
          Notes
        </Button>
        <Button
          variant={activeTab === 'transcriptions' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('transcriptions')}
          className="flex-1"
        >
          <Brain className="h-4 w-4 mr-2" />
          Transcriptions
        </Button>
      </div>

      {activeTab === 'record' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Mic className="h-5 w-5 text-blue-600" />
                <span>Voice Recording</span>
              </CardTitle>
              <CardDescription>
                Record session notes, patient interactions, or clinical observations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="text-center">
                  <div className="mb-4">
                    {isRecording ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
                        <span className="text-red-600 font-medium">Recording...</span>
                      </div>
                    ) : (
                      <div className="text-muted-foreground">Ready to record</div>
                    )}
                  </div>
                  
                  <div className="text-3xl font-mono mb-4">
                    {formatTime(recordingTime)}
                  </div>
                  
                  <div className="flex items-center justify-center space-x-4">
                    {!isRecording ? (
                      <Button
                        onClick={startRecording}
                        size="lg"
                        className="bg-red-600 hover:bg-red-700"
                      >
                        <Mic className="h-6 w-6 mr-2" />
                        Start Recording
                      </Button>
                    ) : (
                      <Button
                        onClick={stopRecording}
                        size="lg"
                        className="bg-red-600 hover:bg-red-700"
                      >
                        <Square className="h-6 w-6 mr-2" />
                        Stop Recording
                      </Button>
                    )}
                  </div>
                </div>

                {isProcessing && (
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <Brain className="h-4 w-4 text-purple-600 animate-pulse" />
                      <span className="text-sm text-muted-foreground">
                        Processing audio with AI...
                      </span>
                    </div>
                    <Progress value={66} className="w-full" />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recording Tips</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium text-green-600">Best Practices</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Speak clearly and at moderate pace</li>
                    <li>• Minimize background noise</li>
                    <li>• Use specific clinical terminology</li>
                    <li>• Record in a quiet environment</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-blue-600">AI Features</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Automatic transcription</li>
                    <li>• Sentiment analysis</li>
                    <li>• Keyword extraction</li>
                    <li>• Clinical summary generation</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'notes' && (
        <div className="space-y-4">
          {voiceNotes.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Mic className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Voice Notes</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Start recording to create your first voice note
                </p>
                <Button onClick={() => setActiveTab('record')}>
                  <Mic className="h-4 w-4 mr-2" />
                  Start Recording
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {voiceNotes.map(renderVoiceNote)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'transcriptions' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-purple-600" />
                <span>AI Transcriptions</span>
              </CardTitle>
              <CardDescription>
                View and edit AI-generated transcriptions of your voice notes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {voiceNotes.map(note => (
                  <div key={note.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{note.title}</h4>
                      <Badge variant="outline">
                        {formatTime(note.duration)}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground mb-2">
                      {note.transcription}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button size="sm" variant="outline">
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-3 w-3 mr-1" />
                        Export
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Audio Player */}
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />
    </div>
  );
}
