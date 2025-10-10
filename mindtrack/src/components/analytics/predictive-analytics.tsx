'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  LineChart, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Calendar, 
  User, 
  FileText, 
  Eye, 
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
  Brain,
  Zap,
  Target as TargetIcon,
  AlertCircle,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from 'lucide-react';

interface PredictionModel {
  id: string;
  name: string;
  type: 'crisis_prevention' | 'treatment_success' | 'medication_adherence' | 'symptom_progression' | 'relapse_risk';
  accuracy: number;
  lastTrained: string;
  status: 'active' | 'training' | 'inactive';
  features: string[];
  performance: {
    precision: number;
    recall: number;
    f1Score: number;
    auc: number;
  };
}

interface Prediction {
  id: string;
  patientId: string;
  modelId: string;
  type: string;
  prediction: number;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  factors: string[];
  recommendations: string[];
  createdAt: string;
  expiresAt: string;
}

interface RiskAlert {
  id: string;
  patientId: string;
  type: 'crisis' | 'medication' | 'appointment' | 'symptom';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  predictedDate: string;
  confidence: number;
  actions: string[];
  isAcknowledged: boolean;
  createdAt: string;
}

interface PredictiveAnalyticsProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function PredictiveAnalytics({ patientId, providerId, providerType }: PredictiveAnalyticsProps) {
  const [models, setModels] = useState<PredictionModel[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [isTraining, setIsTraining] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'predictions' | 'alerts' | 'models'>('overview');

  useEffect(() => {
    loadPredictionModels();
    loadPredictions();
    loadRiskAlerts();
  }, [patientId]);

  const loadPredictionModels = async () => {
    try {
      const response = await fetch('/api/analytics/predictive/models');
      if (response.ok) {
        const data = await response.json();
        setModels(data.models || []);
      }
    } catch (error) {
      console.error('Error loading prediction models:', error);
    }
  };

  const loadPredictions = async () => {
    try {
      const response = await fetch(`/api/analytics/predictive/predictions?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setPredictions(data.predictions || []);
      }
    } catch (error) {
      console.error('Error loading predictions:', error);
    }
  };

  const loadRiskAlerts = async () => {
    try {
      const response = await fetch(`/api/analytics/predictive/alerts?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Error loading risk alerts:', error);
    }
  };

  const trainModel = async (modelId: string) => {
    setIsTraining(true);
    try {
      const response = await fetch(`/api/analytics/predictive/models/${modelId}/train`, {
        method: 'POST',
      });

      if (response.ok) {
        await loadPredictionModels();
      }
    } catch (error) {
      console.error('Error training model:', error);
    } finally {
      setIsTraining(false);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/analytics/predictive/alerts/${alertId}/acknowledge`, {
        method: 'PUT',
      });

      if (response.ok) {
        await loadRiskAlerts();
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'crisis_prevention': return <AlertTriangle className="h-4 w-4" />;
      case 'treatment_success': return <CheckCircle className="h-4 w-4" />;
      case 'medication_adherence': return <Pill className="h-4 w-4" />;
      case 'symptom_progression': return <TrendingUp className="h-4 w-4" />;
      case 'relapse_risk': return <AlertCircle className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'training': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderModel = (model: PredictionModel) => (
    <Card key={model.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getTypeIcon(model.type)}
            <div>
              <CardTitle className="text-lg">{model.name}</CardTitle>
              <CardDescription>
                Last trained: {new Date(model.lastTrained).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getStatusColor(model.status)}>
              {model.status}
            </Badge>
            <div className="text-sm font-medium">
              {model.accuracy}% accuracy
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">{model.performance.precision}</div>
              <div className="text-xs text-muted-foreground">Precision</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">{model.performance.recall}</div>
              <div className="text-xs text-muted-foreground">Recall</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">{model.performance.f1Score}</div>
              <div className="text-xs text-muted-foreground">F1 Score</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-orange-600">{model.performance.auc}</div>
              <div className="text-xs text-muted-foreground">AUC</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              className="flex-1"
              onClick={() => trainModel(model.id)}
              disabled={isTraining || model.status === 'training'}
            >
              {isTraining ? (
                <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Cpu className="h-4 w-4 mr-2" />
              )}
              {model.status === 'training' ? 'Training...' : 'Train Model'}
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderPrediction = (prediction: Prediction) => (
    <Card key={prediction.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getTypeIcon(prediction.type)}
            <div>
              <CardTitle className="text-lg">{prediction.type.replace('_', ' ')}</CardTitle>
              <CardDescription>
                {new Date(prediction.createdAt).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getRiskLevelColor(prediction.riskLevel)}>
              {prediction.riskLevel} risk
            </Badge>
            <div className="text-sm font-medium">
              {prediction.confidence}% confidence
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Prediction Score</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={prediction.prediction * 100} className="flex-1" />
              <span className="text-sm font-medium">{(prediction.prediction * 100).toFixed(1)}%</span>
            </div>
          </div>
          {prediction.recommendations.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Recommendations</Label>
              <div className="space-y-1 mt-1">
                {prediction.recommendations.map((rec, index) => (
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

  const renderAlert = (alert: RiskAlert) => (
    <Card key={alert.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <div>
              <CardTitle className="text-lg">{alert.title}</CardTitle>
              <CardDescription>
                Predicted: {new Date(alert.predictedDate).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getSeverityColor(alert.severity)}>
              {alert.severity}
            </Badge>
            <div className="text-sm font-medium">
              {alert.confidence}% confidence
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <div className="text-sm text-muted-foreground">{alert.description}</div>
          </div>
          {alert.actions.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Recommended Actions</Label>
              <div className="space-y-1 mt-1">
                {alert.actions.map((action, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm">
                    <ArrowRight className="h-3 w-3 text-blue-500 mt-1 flex-shrink-0" />
                    <span className="text-muted-foreground">{action}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="flex items-center space-x-2">
            <Button
              className="flex-1"
              onClick={() => acknowledgeAlert(alert.id)}
              disabled={alert.isAcknowledged}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              {alert.isAcknowledged ? 'Acknowledged' : 'Acknowledge'}
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
            <Brain className="h-8 w-8 text-purple-600" />
            <span>Predictive Analytics</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            AI-powered predictions for crisis prevention and treatment success
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Cpu className="h-4 w-4 mr-2" />
            Train All Models
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
          variant={activeTab === 'predictions' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('predictions')}
          className="flex-1"
        >
          <TrendingUp className="h-4 w-4 mr-2" />
          Predictions
        </Button>
        <Button
          variant={activeTab === 'alerts' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('alerts')}
          className="flex-1"
        >
          <AlertTriangle className="h-4 w-4 mr-2" />
          Alerts
        </Button>
        <Button
          variant={activeTab === 'models' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('models')}
          className="flex-1"
        >
          <Cpu className="h-4 w-4 mr-2" />
          Models
        </Button>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="text-2xl font-bold">85%</p>
                    <p className="text-sm text-muted-foreground">Treatment Success Rate</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                  <div>
                    <p className="text-2xl font-bold">3</p>
                    <p className="text-sm text-muted-foreground">Active Risk Alerts</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Cpu className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-2xl font-bold">5</p>
                    <p className="text-sm text-muted-foreground">Active Models</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Target className="h-8 w-8 text-purple-600" />
                  <div>
                    <p className="text-2xl font-bold">92%</p>
                    <p className="text-sm text-muted-foreground">Prediction Accuracy</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Risk Trends</CardTitle>
              <CardDescription>
                Overview of predicted risks and trends over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted rounded">
                <div className="text-center">
                  <LineChart className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Risk trends chart will be displayed here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'predictions' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">AI Predictions</h2>
          
          {predictions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Predictions</h3>
                <p className="text-muted-foreground text-center mb-4">
                  AI predictions will appear here as models are trained
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {predictions.map(renderPrediction)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Risk Alerts</h2>
          
          {alerts.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <AlertTriangle className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Risk Alerts</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Risk alerts will appear here when potential issues are detected
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {alerts.map(renderAlert)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'models' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Prediction Models</h2>
          
          {models.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Cpu className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Models</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Prediction models will be available here
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {models.map(renderModel)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
