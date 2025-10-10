'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Video, 
  Mic, 
  Camera, 
  Eye, 
  Brain, 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  Calendar, 
  User, 
  FileText, 
  Settings, 
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
  Play,
  Pause,
  Square,
  RotateCcw,
  SkipBack,
  SkipForward,
  Repeat,
  Shuffle,
  Volume1,
  Volume,
  Volume2,
  VolumeX,
  Maximize,
  Minimize,
  Smartphone,
  Watch,
  Monitor,
  Wifi,
  Bluetooth,
  Battery,
  Signal,
  Thermometer,
  Droplets,
  Wind,
  Snowflake,
  CloudRain,
  CloudSnow,
  CloudLightning,
  Sunrise,
  Sunset,
  Target,
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
  MessageSquare,
  Bell,
  Edit,
  Trash2,
  Copy,
  Share,
  Lock,
  Unlock,
  Eye as EyeIcon,
  Settings as SettingsIcon,
  Zap,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';

interface AIAnalysis {
  id: string;
  sessionId: string;
  type: 'facial_expression' | 'voice_tone' | 'emotion' | 'stress' | 'engagement';
  value: number;
  confidence: number;
  timestamp: string;
  metadata: any;
}

interface EmotionAnalysis {
  id: string;
  sessionId: string;
  emotion: 'happy' | 'sad' | 'angry' | 'fearful' | 'surprised' | 'disgusted' | 'neutral';
  intensity: number;
  confidence: number;
  timestamp: string;
}

interface StressLevel {
  id: string;
  sessionId: string;
  level: number; // 1-10
  indicators: string[];
  confidence: number;
  timestamp: string;
}

interface EngagementScore {
  id: string;
  sessionId: string;
  score: number; // 0-100
  factors: string[];
  confidence: number;
  timestamp: string;
}

interface TelemedicineAIProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function TelemedicineAI({ patientId, providerId, providerType }: TelemedicineAIProps) {
  const [analyses, setAnalyses] = useState<AIAnalysis[]>([]);
  const [emotions, setEmotions] = useState<EmotionAnalysis[]>([]);
  const [stressLevels, setStressLevels] = useState<StressLevel[]>([]);
  const [engagementScores, setEngagementScores] = useState<EngagementScore[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'emotions' | 'stress' | 'engagement' | 'settings'>('overview');

  useEffect(() => {
    loadAIAnalyses();
    loadEmotionAnalyses();
    loadStressAnalyses();
    loadEngagementAnalyses();
  }, [patientId]);

  const loadAIAnalyses = async () => {
    try {
      const response = await fetch(`/api/telemedicine/ai/analyses?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalyses(data.analyses || []);
      }
    } catch (error) {
      console.error('Error loading AI analyses:', error);
    }
  };

  const loadEmotionAnalyses = async () => {
    try {
      const response = await fetch(`/api/telemedicine/ai/emotions?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setEmotions(data.emotions || []);
      }
    } catch (error) {
      console.error('Error loading emotion analyses:', error);
    }
  };

  const loadStressAnalyses = async () => {
    try {
      const response = await fetch(`/api/telemedicine/ai/stress?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setStressLevels(data.stressLevels || []);
      }
    } catch (error) {
      console.error('Error loading stress analyses:', error);
    }
  };

  const loadEngagementAnalyses = async () => {
    try {
      const response = await fetch(`/api/telemedicine/ai/engagement?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setEngagementScores(data.engagementScores || []);
      }
    } catch (error) {
      console.error('Error loading engagement analyses:', error);
    }
  };

  const startAIAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/telemedicine/ai/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId,
          providerId,
          videoEnabled: isVideoEnabled,
          audioEnabled: isAudioEnabled
        }),
      });

      if (response.ok) {
        await loadAIAnalyses();
        await loadEmotionAnalyses();
        await loadStressAnalyses();
        await loadEngagementAnalyses();
      }
    } catch (error) {
      console.error('Error starting AI analysis:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const stopAIAnalysis = async () => {
    try {
      const response = await fetch('/api/telemedicine/ai/stop', {
        method: 'POST',
      });

      if (response.ok) {
        setIsAnalyzing(false);
      }
    } catch (error) {
      console.error('Error stopping AI analysis:', error);
    }
  };

  const getEmotionColor = (emotion: string) => {
    switch (emotion) {
      case 'happy': return 'bg-yellow-100 text-yellow-800';
      case 'sad': return 'bg-blue-100 text-blue-800';
      case 'angry': return 'bg-red-100 text-red-800';
      case 'fearful': return 'bg-purple-100 text-purple-800';
      case 'surprised': return 'bg-orange-100 text-orange-800';
      case 'disgusted': return 'bg-green-100 text-green-800';
      case 'neutral': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStressColor = (level: number) => {
    if (level <= 3) return 'bg-green-100 text-green-800';
    if (level <= 6) return 'bg-yellow-100 text-yellow-800';
    if (level <= 8) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const getEngagementColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    if (score >= 40) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const renderEmotion = (emotion: EmotionAnalysis) => (
    <Card key={emotion.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Eye className="h-4 w-4" />
            <div>
              <CardTitle className="text-lg">{emotion.emotion}</CardTitle>
              <CardDescription>
                {new Date(emotion.timestamp).toLocaleTimeString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getEmotionColor(emotion.emotion)}>
              {emotion.emotion}
            </Badge>
            <div className="text-sm font-medium">
              {emotion.confidence}% confidence
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Intensity</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={emotion.intensity} className="flex-1" />
              <span className="text-sm font-medium">{emotion.intensity}/10</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderStress = (stress: StressLevel) => (
    <Card key={stress.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4" />
            <div>
              <CardTitle className="text-lg">Stress Level</CardTitle>
              <CardDescription>
                {new Date(stress.timestamp).toLocaleTimeString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getStressColor(stress.level)}>
              Level {stress.level}
            </Badge>
            <div className="text-sm font-medium">
              {stress.confidence}% confidence
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Stress Level</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={stress.level * 10} className="flex-1" />
              <span className="text-sm font-medium">{stress.level}/10</span>
            </div>
          </div>
          {stress.indicators.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Indicators</Label>
              <div className="space-y-1 mt-1">
                {stress.indicators.map((indicator, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm">
                    <AlertCircle className="h-3 w-3 text-orange-500 mt-1 flex-shrink-0" />
                    <span className="text-muted-foreground">{indicator}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const renderEngagement = (engagement: EngagementScore) => (
    <Card key={engagement.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-4 w-4" />
            <div>
              <CardTitle className="text-lg">Engagement Score</CardTitle>
              <CardDescription>
                {new Date(engagement.timestamp).toLocaleTimeString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getEngagementColor(engagement.score)}>
              {engagement.score}%
            </Badge>
            <div className="text-sm font-medium">
              {engagement.confidence}% confidence
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Engagement Score</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={engagement.score} className="flex-1" />
              <span className="text-sm font-medium">{engagement.score}%</span>
            </div>
          </div>
          {engagement.factors.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Factors</Label>
              <div className="space-y-1 mt-1">
                {engagement.factors.map((factor, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm">
                    <CheckCircle className="h-3 w-3 text-green-500 mt-1 flex-shrink-0" />
                    <span className="text-muted-foreground">{factor}</span>
                  </div>
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
            <Brain className="h-8 w-8 text-purple-600" />
            <span>Telemedicine AI</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            AI-powered analysis of facial expressions, voice tone, and engagement
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={isAnalyzing ? stopAIAnalysis : startAIAnalysis}
            variant={isAnalyzing ? 'destructive' : 'default'}
          >
            {isAnalyzing ? (
              <Square className="h-4 w-4 mr-2" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {isAnalyzing ? 'Stop Analysis' : 'Start Analysis'}
          </Button>
        </div>
      </div>

      {isAnalyzing && (
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  <span className="font-medium">AI Analysis Active</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={isVideoEnabled ? 'default' : 'secondary'}>
                    <Camera className="h-3 w-3 mr-1" />
                    Video
                  </Badge>
                  <Badge variant={isAudioEnabled ? 'default' : 'secondary'}>
                    <Mic className="h-3 w-3 mr-1" />
                    Audio
                  </Badge>
                </div>
              </div>
              <div className="h-32 bg-muted rounded flex items-center justify-center">
                <div className="text-center">
                  <Video className="h-8 w-8 text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Live Video Feed</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'overview' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('overview')}
          className="flex-1"
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          Overview
        </Button>
        <Button
          variant={activeTab === 'emotions' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('emotions')}
          className="flex-1"
        >
          <Eye className="h-4 w-4 mr-2" />
          Emotions
        </Button>
        <Button
          variant={activeTab === 'stress' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('stress')}
          className="flex-1"
        >
          <Activity className="h-4 w-4 mr-2" />
          Stress
        </Button>
        <Button
          variant={activeTab === 'engagement' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('engagement')}
          className="flex-1"
        >
          <Brain className="h-4 w-4 mr-2" />
          Engagement
        </Button>
        <Button
          variant={activeTab === 'settings' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('settings')}
          className="flex-1"
        >
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Eye className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-2xl font-bold">Neutral</p>
                    <p className="text-sm text-muted-foreground">Dominant Emotion</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Activity className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="text-2xl font-bold">3.2</p>
                    <p className="text-sm text-muted-foreground">Avg Stress Level</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Brain className="h-8 w-8 text-purple-600" />
                  <div>
                    <p className="text-2xl font-bold">78%</p>
                    <p className="text-sm text-muted-foreground">Engagement Score</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-8 w-8 text-orange-600" />
                  <div>
                    <p className="text-2xl font-bold">92%</p>
                    <p className="text-sm text-muted-foreground">AI Accuracy</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Real-time Analysis</CardTitle>
              <CardDescription>
                Live AI analysis of patient's emotional state and engagement
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted rounded">
                <div className="text-center">
                  <LineChart className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Real-time analysis chart will be displayed here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'emotions' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Emotion Analysis</h2>
          
          {emotions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Eye className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Emotion Data</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Start AI analysis to detect emotions in real-time
                </p>
                <Button onClick={startAIAnalysis}>
                  <Play className="h-4 w-4 mr-2" />
                  Start Analysis
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {emotions.map(renderEmotion)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'stress' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Stress Level Analysis</h2>
          
          {stressLevels.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Activity className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Stress Data</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Start AI analysis to monitor stress levels
                </p>
                <Button onClick={startAIAnalysis}>
                  <Play className="h-4 w-4 mr-2" />
                  Start Analysis
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {stressLevels.map(renderStress)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'engagement' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Engagement Analysis</h2>
          
          {engagementScores.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Engagement Data</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Start AI analysis to measure patient engagement
                </p>
                <Button onClick={startAIAnalysis}>
                  <Play className="h-4 w-4 mr-2" />
                  Start Analysis
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {engagementScores.map(renderEngagement)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">AI Settings</h2>
          
          <Card>
            <CardHeader>
              <CardTitle>Analysis Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-medium">Video Analysis</Label>
                  <Button
                    variant={isVideoEnabled ? 'default' : 'outline'}
                    onClick={() => setIsVideoEnabled(!isVideoEnabled)}
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    {isVideoEnabled ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-medium">Audio Analysis</Label>
                  <Button
                    variant={isAudioEnabled ? 'default' : 'outline'}
                    onClick={() => setIsAudioEnabled(!isAudioEnabled)}
                  >
                    <Mic className="h-4 w-4 mr-2" />
                    {isAudioEnabled ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
                <div>
                  <Label className="text-sm font-medium">Analysis Sensitivity</Label>
                  <select className="w-full p-2 border rounded mt-1">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div>
                  <Label className="text-sm font-medium">Update Frequency (seconds)</Label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    defaultValue="5"
                    className="w-full p-2 border rounded mt-1"
                  />
                </div>
                <Button className="w-full">
                  <Settings className="h-4 w-4 mr-2" />
                  Save Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
