'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Trophy, 
  Award, 
  Star, 
  Crown, 
  Gem, 
  Target, 
  Zap, 
  Flame, 
  Rocket, 
  Diamond, 
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
  Activity,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  BarChart3,
  PieChart,
  LineChart,
  Heart,
  Smile,
  ThumbsUp,
  Gift,
  Medal,
  Flag,
  Gamepad2,
  Dice1,
  Dice2,
  Dice3,
  Dice4,
  Dice5,
  Dice6,
  Puzzle,
  Lightbulb,
  BookOpen,
  GraduationCap,
  Users,
  UserPlus,
  UserCheck,
  UserX,
  Plus,
  Minus,
  RefreshCw
} from 'lucide-react';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  category: 'therapy' | 'medication' | 'exercise' | 'mindfulness' | 'social' | 'learning';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  isUnlocked: boolean;
  unlockedAt?: string;
  progress: number;
  maxProgress: number;
}

interface Quest {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'monthly' | 'special';
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  rewards: {
    points: number;
    badges: string[];
    items: string[];
  };
  objectives: string[];
  progress: number;
  maxProgress: number;
  isCompleted: boolean;
  expiresAt: string;
}

interface Leaderboard {
  id: string;
  patientId: string;
  patientName: string;
  totalPoints: number;
  level: number;
  rank: number;
  achievements: number;
  questsCompleted: number;
  streak: number;
}

interface GamificationTherapyProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function GamificationTherapy({ patientId, providerId, providerType }: GamificationTherapyProps) {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [quests, setQuests] = useState<Quest[]>([]);
  const [leaderboard, setLeaderboard] = useState<Leaderboard[]>([]);
  const [patientStats, setPatientStats] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'quests' | 'leaderboard' | 'rewards'>('overview');

  useEffect(() => {
    loadAchievements();
    loadQuests();
    loadLeaderboard();
    loadPatientStats();
  }, [patientId]);

  const loadAchievements = async () => {
    try {
      const response = await fetch(`/api/gamification/achievements?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setAchievements(data.achievements || []);
      }
    } catch (error) {
      console.error('Error loading achievements:', error);
    }
  };

  const loadQuests = async () => {
    try {
      const response = await fetch(`/api/gamification/quests?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setQuests(data.quests || []);
      }
    } catch (error) {
      console.error('Error loading quests:', error);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const response = await fetch(`/api/gamification/leaderboard?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    }
  };

  const loadPatientStats = async () => {
    try {
      const response = await fetch(`/api/gamification/stats?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setPatientStats(data.stats);
      }
    } catch (error) {
      console.error('Error loading patient stats:', error);
    }
  };

  const claimReward = async (achievementId: string) => {
    try {
      const response = await fetch(`/api/gamification/achievements/${achievementId}/claim`, {
        method: 'POST',
      });

      if (response.ok) {
        await loadAchievements();
        await loadPatientStats();
      }
    } catch (error) {
      console.error('Error claiming reward:', error);
    }
  };

  const completeQuest = async (questId: string) => {
    try {
      const response = await fetch(`/api/gamification/quests/${questId}/complete`, {
        method: 'POST',
      });

      if (response.ok) {
        await loadQuests();
        await loadPatientStats();
      }
    } catch (error) {
      console.error('Error completing quest:', error);
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'bg-gray-100 text-gray-800';
      case 'rare': return 'bg-blue-100 text-blue-800';
      case 'epic': return 'bg-purple-100 text-purple-800';
      case 'legendary': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-orange-100 text-orange-800';
      case 'expert': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'daily': return 'bg-blue-100 text-blue-800';
      case 'weekly': return 'bg-green-100 text-green-800';
      case 'monthly': return 'bg-purple-100 text-purple-800';
      case 'special': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'therapy': return <Brain className="h-4 w-4" />;
      case 'medication': return <Pill className="h-4 w-4" />;
      case 'exercise': return <Activity className="h-4 w-4" />;
      case 'mindfulness': return <Heart className="h-4 w-4" />;
      case 'social': return <Users className="h-4 w-4" />;
      case 'learning': return <BookOpen className="h-4 w-4" />;
      default: return <Star className="h-4 w-4" />;
    }
  };

  const renderAchievement = (achievement: Achievement) => (
    <Card key={achievement.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getCategoryIcon(achievement.category)}
            <div>
              <CardTitle className="text-lg">{achievement.title}</CardTitle>
              <CardDescription>{achievement.description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getRarityColor(achievement.rarity)}>
              {achievement.rarity}
            </Badge>
            <div className="text-sm font-medium">
              {achievement.points} pts
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Progress</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={(achievement.progress / achievement.maxProgress) * 100} className="flex-1" />
              <span className="text-sm font-medium">
                {achievement.progress}/{achievement.maxProgress}
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              className="flex-1"
              onClick={() => claimReward(achievement.id)}
              disabled={!achievement.isUnlocked || achievement.progress < achievement.maxProgress}
            >
              <Trophy className="h-4 w-4 mr-2" />
              {achievement.isUnlocked ? 'Claimed' : 'Claim Reward'}
            </Button>
            <Button variant="outline" size="sm">
              <Eye className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderQuest = (quest: Quest) => (
    <Card key={quest.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Target className="h-4 w-4" />
            <div>
              <CardTitle className="text-lg">{quest.title}</CardTitle>
              <CardDescription>{quest.description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getTypeColor(quest.type)}>
              {quest.type}
            </Badge>
            <Badge className={getDifficultyColor(quest.difficulty)}>
              {quest.difficulty}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <Label className="text-sm font-medium">Progress</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Progress value={(quest.progress / quest.maxProgress) * 100} className="flex-1" />
              <span className="text-sm font-medium">
                {quest.progress}/{quest.maxProgress}
              </span>
            </div>
          </div>
          <div>
            <Label className="text-sm font-medium">Objectives</Label>
            <div className="space-y-1 mt-1">
              {quest.objectives.map((objective, index) => (
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
              onClick={() => completeQuest(quest.id)}
              disabled={quest.isCompleted || quest.progress < quest.maxProgress}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              {quest.isCompleted ? 'Completed' : 'Complete Quest'}
            </Button>
            <Button variant="outline" size="sm">
              <Gift className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderLeaderboardEntry = (entry: Leaderboard, index: number) => (
    <Card key={entry.id} className="mb-4">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
              {index === 0 && <Crown className="h-4 w-4 text-yellow-500" />}
              {index === 1 && <Medal className="h-4 w-4 text-gray-400" />}
              {index === 2 && <Award className="h-4 w-4 text-orange-500" />}
              {index > 2 && <span className="text-sm font-bold">#{index + 1}</span>}
            </div>
            <div>
              <div className="font-medium">{entry.patientName}</div>
              <div className="text-sm text-muted-foreground">Level {entry.level}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="font-bold text-lg">{entry.totalPoints.toLocaleString()}</div>
            <div className="text-sm text-muted-foreground">{entry.achievements} achievements</div>
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
            <Gamepad2 className="h-8 w-8 text-green-600" />
            <span>Gamification Therapy</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            Make therapy engaging with achievements, quests, and rewards
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
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
          variant={activeTab === 'achievements' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('achievements')}
          className="flex-1"
        >
          <Trophy className="h-4 w-4 mr-2" />
          Achievements
        </Button>
        <Button
          variant={activeTab === 'quests' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('quests')}
          className="flex-1"
        >
          <Target className="h-4 w-4 mr-2" />
          Quests
        </Button>
        <Button
          variant={activeTab === 'leaderboard' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('leaderboard')}
          className="flex-1"
        >
          <Crown className="h-4 w-4 mr-2" />
          Leaderboard
        </Button>
        <Button
          variant={activeTab === 'rewards' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('rewards')}
          className="flex-1"
        >
          <Gift className="h-4 w-4 mr-2" />
          Rewards
        </Button>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Star className="h-8 w-8 text-yellow-600" />
                  <div>
                    <p className="text-2xl font-bold">{patientStats?.totalPoints || 0}</p>
                    <p className="text-sm text-muted-foreground">Total Points</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Trophy className="h-8 w-8 text-purple-600" />
                  <div>
                    <p className="text-2xl font-bold">{patientStats?.achievements || 0}</p>
                    <p className="text-sm text-muted-foreground">Achievements</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Target className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="text-2xl font-bold">{patientStats?.questsCompleted || 0}</p>
                    <p className="text-sm text-muted-foreground">Quests Completed</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Flame className="h-8 w-8 text-orange-600" />
                  <div>
                    <p className="text-2xl font-bold">{patientStats?.streak || 0}</p>
                    <p className="text-sm text-muted-foreground">Day Streak</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Progress Overview</CardTitle>
              <CardDescription>
                Your journey through gamified therapy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted rounded">
                <div className="text-center">
                  <LineChart className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Progress chart will be displayed here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'achievements' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Achievements</h2>
          
          {achievements.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Trophy className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Achievements</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Complete therapy activities to unlock achievements
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {achievements.map(renderAchievement)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'quests' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Quests</h2>
          
          {quests.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Target className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Quests</h3>
                <p className="text-muted-foreground text-center mb-4">
                  New quests will appear here to guide your therapy journey
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {quests.map(renderQuest)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'leaderboard' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Leaderboard</h2>
          
          {leaderboard.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Crown className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Leaderboard</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Compete with other patients on the leaderboard
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {leaderboard.map(renderLeaderboardEntry)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'rewards' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Rewards</h2>
          
          <Card>
            <CardHeader>
              <CardTitle>Available Rewards</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded">
                  <Gift className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <div className="font-medium">Therapy Session</div>
                  <div className="text-sm text-muted-foreground">500 points</div>
                </div>
                <div className="text-center p-4 border rounded">
                  <BookOpen className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <div className="font-medium">Learning Material</div>
                  <div className="text-sm text-muted-foreground">300 points</div>
                </div>
                <div className="text-center p-4 border rounded">
                  <Heart className="h-8 w-8 text-red-600 mx-auto mb-2" />
                  <div className="font-medium">Wellness Kit</div>
                  <div className="text-sm text-muted-foreground">750 points</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
