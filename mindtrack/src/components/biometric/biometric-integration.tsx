'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { 
  Heart, 
  Moon, 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Clock, 
  Calendar, 
  User, 
  FileText, 
  BarChart3, 
  PieChart, 
  Eye, 
  Settings, 
  Play, 
  Pause, 
  RotateCcw, 
  Download, 
  Upload, 
  Share2, 
  Bell, 
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
  Sunset
} from 'lucide-react';

interface BiometricData {
  id: string;
  patientId: string;
  type: 'heart_rate' | 'sleep' | 'activity' | 'stress' | 'mood' | 'blood_pressure' | 'temperature' | 'weight';
  value: number;
  unit: string;
  timestamp: string;
  source: 'apple_health' | 'google_fit' | 'fitbit' | 'samsung_health' | 'manual' | 'device';
  deviceId?: string;
  metadata?: any;
}

interface SleepData {
  id: string;
  patientId: string;
  date: string;
  totalSleep: number; // minutes
  deepSleep: number; // minutes
  lightSleep: number; // minutes
  remSleep: number; // minutes
  sleepEfficiency: number; // percentage
  awakenings: number;
  bedTime: string;
  wakeTime: string;
  quality: 'poor' | 'fair' | 'good' | 'excellent';
}

interface ActivityData {
  id: string;
  patientId: string;
  date: string;
  steps: number;
  distance: number; // km
  calories: number;
  activeMinutes: number;
  heartRateAvg: number;
  heartRateMax: number;
  heartRateMin: number;
  stressLevel: number; // 1-10
  mood: number; // 1-10
}

interface BiometricInsight {
  id: string;
  patientId: string;
  type: 'trend' | 'anomaly' | 'correlation' | 'recommendation';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  data: any;
  recommendations: string[];
  createdAt: string;
}

interface BiometricIntegrationProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function BiometricIntegration({ patientId, providerId, providerType }: BiometricIntegrationProps) {
  const [biometricData, setBiometricData] = useState<BiometricData[]>([]);
  const [sleepData, setSleepData] = useState<SleepData[]>([]);
  const [activityData, setActivityData] = useState<ActivityData[]>([]);
  const [insights, setInsights] = useState<BiometricInsight[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectedDevices, setConnectedDevices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'heart' | 'sleep' | 'activity' | 'insights' | 'devices'>('overview');
  const [selectedDateRange, setSelectedDateRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  useEffect(() => {
    loadBiometricData();
    loadSleepData();
    loadActivityData();
    loadInsights();
    checkDeviceConnections();
  }, [patientId, selectedDateRange]);

  const loadBiometricData = async () => {
    try {
      const response = await fetch(`/api/biometric/data?patientId=${patientId}&range=${selectedDateRange}`);
      if (response.ok) {
        const data = await response.json();
        setBiometricData(data.data || []);
      }
    } catch (error) {
      console.error('Error loading biometric data:', error);
    }
  };

  const loadSleepData = async () => {
    try {
      const response = await fetch(`/api/biometric/sleep?patientId=${patientId}&range=${selectedDateRange}`);
      if (response.ok) {
        const data = await response.json();
        setSleepData(data.data || []);
      }
    } catch (error) {
      console.error('Error loading sleep data:', error);
    }
  };

  const loadActivityData = async () => {
    try {
      const response = await fetch(`/api/biometric/activity?patientId=${patientId}&range=${selectedDateRange}`);
      if (response.ok) {
        const data = await response.json();
        setActivityData(data.data || []);
      }
    } catch (error) {
      console.error('Error loading activity data:', error);
    }
  };

  const loadInsights = async () => {
    try {
      const response = await fetch(`/api/biometric/insights?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setInsights(data.insights || []);
      }
    } catch (error) {
      console.error('Error loading biometric insights:', error);
    }
  };

  const checkDeviceConnections = async () => {
    try {
      const response = await fetch(`/api/biometric/devices?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setConnectedDevices(data.devices || []);
        setIsConnected(data.devices.length > 0);
      }
    } catch (error) {
      console.error('Error checking device connections:', error);
    }
  };

  const connectDevice = async (deviceType: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/biometric/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId,
          deviceType,
          providerId
        }),
      });

      if (response.ok) {
        await checkDeviceConnections();
        await loadBiometricData();
      }
    } catch (error) {
      console.error('Error connecting device:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const syncData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/biometric/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId }),
      });

      if (response.ok) {
        await loadBiometricData();
        await loadSleepData();
        await loadActivityData();
        await loadInsights();
      }
    } catch (error) {
      console.error('Error syncing data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'fair': return 'bg-yellow-100 text-yellow-800';
      case 'poor': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const renderSleepCard = (sleep: SleepData) => (
    <Card key={sleep.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Moon className="h-5 w-5 text-blue-600" />
            <div>
              <CardTitle className="text-lg">{new Date(sleep.date).toLocaleDateString()}</CardTitle>
              <CardDescription>
                {sleep.bedTime} - {sleep.wakeTime}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getQualityColor(sleep.quality)}>
              {sleep.quality}
            </Badge>
            <div className="text-sm font-medium">
              {sleep.sleepEfficiency}% efficiency
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{formatDuration(sleep.totalSleep)}</div>
              <div className="text-xs text-muted-foreground">Total Sleep</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{formatDuration(sleep.deepSleep)}</div>
              <div className="text-xs text-muted-foreground">Deep Sleep</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{formatDuration(sleep.remSleep)}</div>
              <div className="text-xs text-muted-foreground">REM Sleep</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{sleep.awakenings}</div>
              <div className="text-xs text-muted-foreground">Awakenings</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderActivityCard = (activity: ActivityData) => (
    <Card key={activity.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-green-600" />
            <div>
              <CardTitle className="text-lg">{new Date(activity.date).toLocaleDateString()}</CardTitle>
              <CardDescription>
                Daily Activity Summary
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline">
              {activity.steps.toLocaleString()} steps
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{activity.steps.toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">Steps</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{activity.distance.toFixed(1)} km</div>
              <div className="text-xs text-muted-foreground">Distance</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{activity.calories}</div>
              <div className="text-xs text-muted-foreground">Calories</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{activity.heartRateAvg}</div>
              <div className="text-xs text-muted-foreground">Avg HR</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Stress Level</Label>
              <div className="flex items-center space-x-2 mt-1">
                <Progress value={activity.stressLevel * 10} className="flex-1" />
                <span className="text-sm font-medium">{activity.stressLevel}/10</span>
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium">Mood</Label>
              <div className="flex items-center space-x-2 mt-1">
                <Progress value={activity.mood * 10} className="flex-1" />
                <span className="text-sm font-medium">{activity.mood}/10</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderInsight = (insight: BiometricInsight) => (
    <Card key={insight.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-purple-600" />
            <div>
              <CardTitle className="text-lg">{insight.title}</CardTitle>
              <CardDescription>
                {new Date(insight.createdAt).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getSeverityColor(insight.severity)}>
              {insight.severity}
            </Badge>
            <div className="text-sm font-medium">
              {insight.confidence}% confidence
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <div className="text-sm text-muted-foreground">{insight.description}</div>
          </div>
          {insight.recommendations.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Recommendations</Label>
              <div className="space-y-1 mt-1">
                {insight.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm">
                    <CheckCircle className="h-3 w-3 text-green-500 mt-1 flex-shrink-0" />
                    <span className="text-muted-foreground">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const availableDevices = [
    { type: 'apple_health', name: 'Apple Health', icon: <Smartphone className="h-5 w-5" /> },
    { type: 'google_fit', name: 'Google Fit', icon: <Activity className="h-5 w-5" /> },
    { type: 'fitbit', name: 'Fitbit', icon: <Watch className="h-5 w-5" /> },
    { type: 'samsung_health', name: 'Samsung Health', icon: <Monitor className="h-5 w-5" /> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-2">
            <Heart className="h-8 w-8 text-red-600" />
            <span>Biometric Integration</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            Comprehensive health monitoring with wearable devices and health apps
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={syncData}
            disabled={isLoading}
            variant="outline"
          >
            {isLoading ? (
              <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Sync Data
          </Button>
        </div>
      </div>

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
          variant={activeTab === 'heart' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('heart')}
          className="flex-1"
        >
          <Heart className="h-4 w-4 mr-2" />
          Heart Rate
        </Button>
        <Button
          variant={activeTab === 'sleep' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('sleep')}
          className="flex-1"
        >
          <Moon className="h-4 w-4 mr-2" />
          Sleep
        </Button>
        <Button
          variant={activeTab === 'activity' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('activity')}
          className="flex-1"
        >
          <Activity className="h-4 w-4 mr-2" />
          Activity
        </Button>
        <Button
          variant={activeTab === 'insights' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('insights')}
          className="flex-1"
        >
          <Brain className="h-4 w-4 mr-2" />
          Insights
        </Button>
        <Button
          variant={activeTab === 'devices' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('devices')}
          className="flex-1"
        >
          <Bluetooth className="h-4 w-4 mr-2" />
          Devices
        </Button>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Heart className="h-8 w-8 text-red-600" />
                  <div>
                    <p className="text-2xl font-bold">72</p>
                    <p className="text-sm text-muted-foreground">Avg Heart Rate</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Moon className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-2xl font-bold">7.5h</p>
                    <p className="text-sm text-muted-foreground">Avg Sleep</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Activity className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="text-2xl font-bold">8,234</p>
                    <p className="text-sm text-muted-foreground">Daily Steps</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-8 w-8 text-purple-600" />
                  <div>
                    <p className="text-2xl font-bold">85%</p>
                    <p className="text-sm text-muted-foreground">Health Score</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Health Trends</CardTitle>
              <CardDescription>
                Overview of key health metrics over the selected time period
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted rounded">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Health trends chart will be displayed here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'sleep' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Sleep Data</h2>
            <select
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value as any)}
              className="p-2 border rounded"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>

          {sleepData.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Moon className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Sleep Data</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Connect a sleep tracking device to monitor sleep patterns
                </p>
                <Button onClick={() => setActiveTab('devices')}>
                  <Bluetooth className="h-4 w-4 mr-2" />
                  Connect Device
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {sleepData.map(renderSleepCard)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Activity Data</h2>
            <select
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value as any)}
              className="p-2 border rounded"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>

          {activityData.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Activity className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Activity Data</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Connect an activity tracking device to monitor daily activity
                </p>
                <Button onClick={() => setActiveTab('devices')}>
                  <Bluetooth className="h-4 w-4 mr-2" />
                  Connect Device
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {activityData.map(renderActivityCard)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'insights' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">AI Health Insights</h2>
          
          {insights.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Health Insights</h3>
                <p className="text-muted-foreground text-center mb-4">
                  AI insights will appear here as more data is collected
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {insights.map(renderInsight)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'devices' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Connected Devices</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableDevices.map((device) => (
              <Card key={device.type} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-2">
                    {device.icon}
                    <CardTitle className="text-lg">{device.name}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Status</span>
                      <Badge variant={connectedDevices.includes(device.type) ? 'default' : 'secondary'}>
                        {connectedDevices.includes(device.type) ? 'Connected' : 'Not Connected'}
                      </Badge>
                    </div>
                    <Button
                      className="w-full"
                      onClick={() => connectDevice(device.type)}
                      disabled={isLoading || connectedDevices.includes(device.type)}
                    >
                      {connectedDevices.includes(device.type) ? (
                        <>
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Connected
                        </>
                      ) : (
                        <>
                          <Bluetooth className="h-4 w-4 mr-2" />
                          Connect
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
