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
  Brain, 
  Zap, 
  Search, 
  Lightbulb, 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  User, 
  FileText, 
  BarChart3, 
  PieChart, 
  Activity, 
  Heart, 
  Pill, 
  Stethoscope, 
  MessageSquare, 
  Eye, 
  Settings, 
  Play, 
  Pause, 
  RotateCcw, 
  Download, 
  Upload, 
  Share2, 
  Bell, 
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
  Rainbow
} from 'lucide-react';

interface ClinicalInsight {
  id: string;
  type: 'diagnosis' | 'treatment' | 'risk' | 'recommendation' | 'pattern';
  title: string;
  description: string;
  confidence: number;
  evidence: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  tags: string[];
  createdAt: string;
  isReviewed: boolean;
  providerNotes?: string;
}

interface PatientAnalysis {
  id: string;
  patientId: string;
  analysisType: 'comprehensive' | 'symptom' | 'medication' | 'therapy' | 'risk';
  findings: ClinicalFinding[];
  recommendations: ClinicalRecommendation[];
  riskFactors: RiskFactor[];
  treatmentSuggestions: TreatmentSuggestion[];
  confidence: number;
  createdAt: string;
  updatedAt: string;
}

interface ClinicalFinding {
  id: string;
  category: string;
  description: string;
  severity: 'mild' | 'moderate' | 'severe';
  evidence: string[];
  confidence: number;
}

interface ClinicalRecommendation {
  id: string;
  type: 'medication' | 'therapy' | 'assessment' | 'referral' | 'monitoring';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  rationale: string;
  expectedOutcome: string;
  timeline: string;
}

interface RiskFactor {
  id: string;
  factor: string;
  level: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  mitigation: string;
  monitoring: string;
}

interface TreatmentSuggestion {
  id: string;
  treatment: string;
  modality: string;
  duration: string;
  expectedImprovement: number;
  sideEffects: string[];
  alternatives: string[];
  cost: string;
}

interface AIClinicalAssistantProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function AIClinicalAssistant({ patientId, providerId, providerType }: AIClinicalAssistantProps) {
  const [insights, setInsights] = useState<ClinicalInsight[]>([]);
  const [analyses, setAnalyses] = useState<PatientAnalysis[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<PatientAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [activeTab, setActiveTab] = useState<'insights' | 'analysis' | 'recommendations' | 'patterns'>('insights');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    loadInsights();
    loadAnalyses();
  }, [patientId]);

  const loadInsights = async () => {
    try {
      const response = await fetch(`/api/ai/clinical-insights?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setInsights(data.insights || []);
      }
    } catch (error) {
      console.error('Error loading clinical insights:', error);
    }
  };

  const loadAnalyses = async () => {
    try {
      const response = await fetch(`/api/ai/patient-analyses?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalyses(data.analyses || []);
      }
    } catch (error) {
      console.error('Error loading patient analyses:', error);
    }
  };

  const runComprehensiveAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);

    try {
      // Simulate analysis progress
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return prev + 10;
        });
      }, 500);

      const response = await fetch('/api/ai/comprehensive-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId,
          providerId,
          providerType,
          analysisType: 'comprehensive'
        }),
      });

      clearInterval(progressInterval);
      setAnalysisProgress(100);

      if (response.ok) {
        const data = await response.json();
        setAnalyses(prev => [data.analysis, ...prev]);
        await loadInsights();
      }
    } catch (error) {
      console.error('Error running comprehensive analysis:', error);
    } finally {
      setIsAnalyzing(false);
      setAnalysisProgress(0);
    }
  };

  const generateTreatmentPlan = async (analysisId: string) => {
    try {
      const response = await fetch(`/api/ai/generate-treatment-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysisId, providerType }),
      });

      if (response.ok) {
        const data = await response.json();
        // Handle treatment plan generation
        console.log('Treatment plan generated:', data);
      }
    } catch (error) {
      console.error('Error generating treatment plan:', error);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'diagnosis': return <Stethoscope className="h-4 w-4" />;
      case 'treatment': return <Pill className="h-4 w-4" />;
      case 'risk': return <AlertTriangle className="h-4 w-4" />;
      case 'recommendation': return <Lightbulb className="h-4 w-4" />;
      case 'pattern': return <BarChart3 className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    if (confidence >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const renderInsight = (insight: ClinicalInsight) => (
    <Card key={insight.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getInsightIcon(insight.type)}
            <div>
              <CardTitle className="text-lg">{insight.title}</CardTitle>
              <CardDescription>
                {insight.category} • {new Date(insight.createdAt).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getSeverityColor(insight.severity)}>
              {insight.severity}
            </Badge>
            <div className={`text-sm font-medium ${getConfidenceColor(insight.confidence)}`}>
              {insight.confidence}% confidence
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                // Mark as reviewed
                setInsights(prev => prev.map(i => 
                  i.id === insight.id ? { ...i, isReviewed: true } : i
                ));
              }}
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <div className="text-sm text-muted-foreground">{insight.description}</div>
          </div>
          {insight.evidence.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Evidence</Label>
              <div className="space-y-1 mt-1">
                {insight.evidence.map((evidence, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm">
                    <CheckCircle className="h-3 w-3 text-green-500 mt-1 flex-shrink-0" />
                    <span className="text-muted-foreground">{evidence}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {insight.tags.length > 0 && (
            <div>
              <Label className="text-sm font-medium">Tags</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {insight.tags.map((tag, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
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

  const renderAnalysis = (analysis: PatientAnalysis) => (
    <Card key={analysis.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-purple-600" />
            <div>
              <CardTitle className="text-lg">
                {analysis.analysisType.charAt(0).toUpperCase() + analysis.analysisType.slice(1)} Analysis
              </CardTitle>
              <CardDescription>
                {new Date(analysis.createdAt).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`text-sm font-medium ${getConfidenceColor(analysis.confidence)}`}>
              {analysis.confidence}% confidence
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedAnalysis(analysis)}
            >
              <Eye className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{analysis.findings.length}</div>
              <div className="text-xs text-muted-foreground">Findings</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{analysis.recommendations.length}</div>
              <div className="text-xs text-muted-foreground">Recommendations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{analysis.riskFactors.length}</div>
              <div className="text-xs text-muted-foreground">Risk Factors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{analysis.treatmentSuggestions.length}</div>
              <div className="text-xs text-muted-foreground">Treatments</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              onClick={() => generateTreatmentPlan(analysis.id)}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Treatment Plan
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedAnalysis(analysis)}
            >
              <Eye className="h-4 w-4 mr-2" />
              View Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const filteredInsights = insights.filter(insight => {
    const matchesSearch = insight.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         insight.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || insight.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-2">
            <Brain className="h-8 w-8 text-purple-600" />
            <span>AI Clinical Assistant</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            Advanced AI-powered clinical insights and treatment recommendations
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={runComprehensiveAnalysis}
            disabled={isAnalyzing}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          >
            {isAnalyzing ? (
              <>
                <RotateCcw className="h-4 w-4 mr-2 animate-spin" />
                Analyzing... {analysisProgress}%
              </>
            ) : (
              <>
                <Cpu className="h-4 w-4 mr-2" />
                Run Analysis
              </>
            )}
          </Button>
        </div>
      </div>

      {isAnalyzing && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-purple-600 animate-pulse" />
                <span className="font-medium">AI is analyzing patient data...</span>
              </div>
              <Progress value={analysisProgress} className="w-full" />
              <div className="text-sm text-muted-foreground">
                Processing medical history, symptoms, medications, and treatment outcomes
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'insights' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('insights')}
          className="flex-1"
        >
          <Lightbulb className="h-4 w-4 mr-2" />
          Insights
        </Button>
        <Button
          variant={activeTab === 'analysis' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('analysis')}
          className="flex-1"
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          Analysis
        </Button>
        <Button
          variant={activeTab === 'recommendations' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('recommendations')}
          className="flex-1"
        >
          <Target className="h-4 w-4 mr-2" />
          Recommendations
        </Button>
        <Button
          variant={activeTab === 'patterns' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('patterns')}
          className="flex-1"
        >
          <TrendingUp className="h-4 w-4 mr-2" />
          Patterns
        </Button>
      </div>

      {activeTab === 'insights' && (
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <Input
                placeholder="Search insights..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="max-w-sm"
              />
            </div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="p-2 border rounded"
            >
              <option value="all">All Categories</option>
              <option value="diagnosis">Diagnosis</option>
              <option value="treatment">Treatment</option>
              <option value="risk">Risk Assessment</option>
              <option value="recommendation">Recommendations</option>
              <option value="pattern">Patterns</option>
            </select>
          </div>

          {filteredInsights.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Clinical Insights</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Run a comprehensive analysis to generate AI-powered clinical insights
                </p>
                <Button onClick={runComprehensiveAnalysis}>
                  <Cpu className="h-4 w-4 mr-2" />
                  Generate Insights
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredInsights.map(renderInsight)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'analysis' && (
        <div className="space-y-4">
          {analyses.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BarChart3 className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Patient Analyses</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Run a comprehensive analysis to get detailed patient insights
                </p>
                <Button onClick={runComprehensiveAnalysis}>
                  <Cpu className="h-4 w-4 mr-2" />
                  Run Analysis
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {analyses.map(renderAnalysis)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-green-600" />
                <span>AI Treatment Recommendations</span>
              </CardTitle>
              <CardDescription>
                Personalized treatment suggestions based on patient data and clinical evidence
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Pill className="h-4 w-4 text-blue-600" />
                      <span className="font-medium">Medication Optimization</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      AI suggests adjusting current medication regimen based on response patterns and side effects.
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <MessageSquare className="h-4 w-4 text-green-600" />
                      <span className="font-medium">Therapy Modality</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Recommended therapy approach based on patient characteristics and treatment history.
                    </p>
                  </div>
                </div>
                <Button className="w-full">
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Personalized Recommendations
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'patterns' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <span>Clinical Patterns & Trends</span>
              </CardTitle>
              <CardDescription>
                AI-identified patterns in patient symptoms, treatment responses, and outcomes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600">85%</div>
                    <div className="text-sm text-muted-foreground">Treatment Adherence</div>
                  </div>
                  <div className="p-4 border rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600">+23%</div>
                    <div className="text-sm text-muted-foreground">Symptom Improvement</div>
                  </div>
                  <div className="p-4 border rounded-lg text-center">
                    <div className="text-2xl font-bold text-orange-600">12</div>
                    <div className="text-sm text-muted-foreground">Risk Factors Identified</div>
                  </div>
                </div>
                <Button className="w-full">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analyze Treatment Patterns
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analysis Details Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-purple-600" />
                <span>Detailed Analysis Results</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">Clinical Findings</h3>
                    <div className="space-y-2">
                      {selectedAnalysis.findings.map((finding, index) => (
                        <div key={index} className="p-3 border rounded">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{finding.category}</span>
                            <Badge className={getSeverityColor(finding.severity)}>
                              {finding.severity}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{finding.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-3">Risk Factors</h3>
                    <div className="space-y-2">
                      {selectedAnalysis.riskFactors.map((risk, index) => (
                        <div key={index} className="p-3 border rounded">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{risk.factor}</span>
                            <Badge className={getSeverityColor(risk.level)}>
                              {risk.level}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{risk.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setSelectedAnalysis(null)}
                  >
                    Close
                  </Button>
                  <Button
                    onClick={() => generateTreatmentPlan(selectedAnalysis.id)}
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate Treatment Plan
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
