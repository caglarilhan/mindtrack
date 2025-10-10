'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Glasses, 
  Eye, 
  Brain, 
  Heart, 
  Zap, 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Volume2, 
  VolumeX, 
  Maximize, 
  Minimize, 
  RotateCcw, 
  SkipBack, 
  SkipForward, 
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
  Repeat,
  Shuffle,
  Volume1,
  Volume,
  Smartphone,
  Watch,
  Monitor,
  Camera,
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
  CheckCircle,
  AlertCircle,
  Info,
  Warning,
  Check,
  X,
  ArrowRight,
  ArrowLeft,
  FileText,
  BarChart3,
  PieChart,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  Calendar,
  User,
  MessageSquare,
  Bell,
  Download,
  Upload,
  Share2,
  Edit,
  Trash2,
  Eye as EyeIcon,
  Settings as SettingsIcon
} from 'lucide-react';

interface VRTherapySession {
  id: string;
  patientId: string;
  therapistId: string;
  type: 'exposure' | 'mindfulness' | 'relaxation' | 'social' | 'phobia' | 'ptsd';
  title: string;
  description: string;
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  environment: string;
  objectives: string[];
  progress: number;
  completedAt?: string;
  createdAt: string;
}

interface VREnvironment {
  id: string;
  name: string;
  type: string;
  description: string;
  thumbnail: string;
  duration: number;
  difficulty: string;
  objectives: string[];
  isAvailable: boolean;
}

interface VRTherapyProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function VRTherapy({ patientId, providerId, providerType }: VRTherapyProps) {
  const [sessions, setSessions] = useState<VRTherapySession[]>([]);
  const [environments, setEnvironments] = useState<VREnvironment[]>([]);
  const [selectedSession, setSelectedSession] = useState<VRTherapySession | null>(null);
  const [isVRConnected, setIsVRConnected] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionProgress, setSessionProgress] = useState(0);
  const [activeTab, setActiveTab] = useState<'environments' | 'sessions' | 'progress' | 'settings'>('environments');

  useEffect(() => {
    loadVRSessions();
    loadVREnvironments();
    checkVRConnection();
  }, [patientId]);

  const loadVRSessions = async () => {
    try {
      const response = await fetch(`/api/vr/sessions?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Error loading VR sessions:', error);
    }
  };

  const loadVREnvironments = async () => {
    try {
      const response = await fetch('/api/vr/environments');
      if (response.ok) {
        const data = await response.json();
        setEnvironments(data.environments || []);
      }
    } catch (error) {
      console.error('Error loading VR environments:', error);
    }
  };

  const checkVRConnection = async () => {
    try {
      const response = await fetch('/api/vr/connection');
      if (response.ok) {
        const data = await response.json();
        setIsVRConnected(data.connected);
      }
    } catch (error) {
      console.error('Error checking VR connection:', error);
    }
  };

  const startVRSession = async (environmentId: string) => {
    try {
      const response = await fetch('/api/vr/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId,
          therapistId: providerId,
          environmentId
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedSession(data.session);
        setIsSessionActive(true);
        setSessionProgress(0);
        await loadVRSessions();
      }
    } catch (error) {
      console.error('Error starting VR session:', error);
    }
  };

  const stopVRSession = async () => {
    if (selectedSession) {
      try {
        const response = await fetch(`/api/vr/sessions/${selectedSession.id}/stop`, {
          method: 'PUT',
        });

        if (response.ok) {
          setIsSessionActive(false);
          setSessionProgress(0);
          await loadVRSessions();
        }
      } catch (error) {
        console.error('Error stopping VR session:', error);
      }
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'exposure': return <Eye className="h-4 w-4" />;
      case 'mindfulness': return <Brain className="h-4 w-4" />;
      case 'relaxation': return <Heart className="h-4 w-4" />;
      case 'social': return <User className="h-4 w-4" />;
      case 'phobia': return <AlertCircle className="h-4 w-4" />;
      case 'ptsd': return <Shield className="h-4 w-4" />;
      default: return <Glasses className="h-4 w-4" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderEnvironment = (environment: VREnvironment) => (
    <Card key={environment.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getTypeIcon(environment.type)}
            <div>
              <CardTitle className="text-lg">{environment.name}</CardTitle>
              <CardDescription>{environment.description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getDifficultyColor(environment.difficulty)}>
              {environment.difficulty}
            </Badge>
            <Badge variant="outline">
              {environment.duration} min
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="h-32 bg-muted rounded flex items-center justify-center">
            <div className="text-center">
              <Glasses className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">VR Environment Preview</p>
            </div>
          </div>
          <div>
            <Label className="text-sm font-medium">Objectives</Label>
            <div className="space-y-1 mt-1">
              {environment.objectives.map((objective, index) => (
                <div key={index} className="flex items-start space-x-2 text-sm">
                  <CheckCircle className="h-3 w-3 text-green-500 mt-1 flex-shrink-0" />
                  <span className="text-muted-foreground">{objective}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              className="flex-1"
              onClick={() => startVRSession(environment.id)}
              disabled={!isVRConnected || !environment.isAvailable}
            >
              <Play className="h-4 w-4 mr-2" />
              Start Session
            </Button>
            <Button variant="outline" size="sm">
              <Eye className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderSession = (session: VRTherapySession) => (
    <Card key={session.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getTypeIcon(session.type)}
            <div>
              <CardTitle className="text-lg">{session.title}</CardTitle>
              <CardDescription>
                {new Date(session.createdAt).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getDifficultyColor(session.difficulty)}>
              {session.difficulty}
            </Badge>
            {session.completedAt && (
              <Badge variant="default">
                <CheckCircle className="h-3 w-3 mr-1" />
                Completed
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Progress</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={session.progress} className="flex-1" />
              <span className="text-sm font-medium">{session.progress}%</span>
            </div>
          </div>
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <div className="text-sm text-muted-foreground">{session.description}</div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              className="flex-1"
              onClick={() => setSelectedSession(session)}
              disabled={!isVRConnected}
            >
              <Play className="h-4 w-4 mr-2" />
              Continue Session
            </Button>
            <Button variant="outline" size="sm">
              <Eye className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-2">
            <Glasses className="h-8 w-8 text-purple-600" />
            <span>Virtual Reality Therapy</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            Immersive VR therapy sessions for exposure therapy, mindfulness, and relaxation
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={isVRConnected ? 'default' : 'secondary'}>
            {isVRConnected ? 'VR Connected' : 'VR Disconnected'}
          </Badge>
          <Button variant="outline" onClick={checkVRConnection}>
            <Glasses className="h-4 w-4 mr-2" />
            Check Connection
          </Button>
        </div>
      </div>

      {isSessionActive && (
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Glasses className="h-5 w-5 text-purple-600" />
                  <span className="font-medium">VR Session Active</span>
                </div>
                <Button onClick={stopVRSession} variant="destructive">
                  <Square className="h-4 w-4 mr-2" />
                  Stop Session
                </Button>
              </div>
              <div>
                <Label className="text-sm font-medium">Session Progress</Label>
                <div className="flex items-center space-x-2 mt-1">
                  <Progress value={sessionProgress} className="flex-1" />
                  <span className="text-sm font-medium">{sessionProgress}%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'environments' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('environments')}
          className="flex-1"
        >
          <Glasses className="h-4 w-4 mr-2" />
          Environments
        </Button>
        <Button
          variant={activeTab === 'sessions' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('sessions')}
          className="flex-1"
        >
          <Play className="h-4 w-4 mr-2" />
          Sessions
        </Button>
        <Button
          variant={activeTab === 'progress' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('progress')}
          className="flex-1"
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          Progress
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

      {activeTab === 'environments' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">VR Therapy Environments</h2>
          
          {environments.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Glasses className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No VR Environments</h3>
                <p className="text-muted-foreground text-center mb-4">
                  VR therapy environments will be available here
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {environments.map(renderEnvironment)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'sessions' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">VR Therapy Sessions</h2>
          
          {sessions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Play className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No VR Sessions</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Start a VR therapy session to begin treatment
                </p>
                <Button onClick={() => setActiveTab('environments')}>
                  <Glasses className="h-4 w-4 mr-2" />
                  Browse Environments
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {sessions.map(renderSession)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'progress' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">VR Therapy Progress</h2>
          
          <Card>
            <CardHeader>
              <CardTitle>Session Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{sessions.length}</div>
                  <div className="text-sm text-muted-foreground">Total Sessions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {sessions.filter(s => s.completedAt).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Completed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.round(sessions.reduce((acc, s) => acc + s.progress, 0) / sessions.length) || 0}%
                  </div>
                  <div className="text-sm text-muted-foreground">Avg Progress</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">VR Settings</h2>
          
          <Card>
            <CardHeader>
              <CardTitle>VR Device Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">VR Headset</Label>
                  <select className="w-full p-2 border rounded mt-1">
                    <option value="oculus">Oculus Quest</option>
                    <option value="htc">HTC Vive</option>
                    <option value="valve">Valve Index</option>
                    <option value="pico">Pico 4</option>
                  </select>
                </div>
                <div>
                  <Label className="text-sm font-medium">Audio Output</Label>
                  <select className="w-full p-2 border rounded mt-1">
                    <option value="headphones">Headphones</option>
                    <option value="speakers">Speakers</option>
                    <option value="both">Both</option>
                  </select>
                </div>
                <div>
                  <Label className="text-sm font-medium">Session Duration (minutes)</Label>
                  <input
                    type="number"
                    min="5"
                    max="60"
                    defaultValue="30"
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
