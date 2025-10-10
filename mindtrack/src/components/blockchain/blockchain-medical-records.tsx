'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Shield, 
  Lock, 
  Key, 
  Database, 
  Network, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  User, 
  FileText, 
  Download, 
  Upload, 
  Eye, 
  Settings, 
  BarChart3, 
  TrendingUp, 
  Sparkles,
  Cpu,
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
  Unlock,
  Eye as EyeIcon,
  Settings as SettingsIcon
} from 'lucide-react';

interface BlockchainRecord {
  id: string;
  patientId: string;
  providerId: string;
  type: 'medical_record' | 'prescription' | 'lab_result' | 'assessment' | 'treatment_plan';
  title: string;
  content: string;
  hash: string;
  previousHash: string;
  timestamp: string;
  blockNumber: number;
  isVerified: boolean;
  verificationCount: number;
  accessLevel: 'public' | 'private' | 'restricted';
  metadata: any;
}

interface BlockchainTransaction {
  id: string;
  from: string;
  to: string;
  amount: number;
  type: 'access_grant' | 'data_share' | 'verification' | 'audit';
  status: 'pending' | 'confirmed' | 'failed';
  timestamp: string;
  blockHash: string;
  gasUsed: number;
}

interface BlockchainMedicalRecordsProps {
  patientId: string;
  providerId: string;
  providerType: 'psychiatrist' | 'psychologist';
}

export default function BlockchainMedicalRecords({ patientId, providerId, providerType }: BlockchainMedicalRecordsProps) {
  const [records, setRecords] = useState<BlockchainRecord[]>([]);
  const [transactions, setTransactions] = useState<BlockchainTransaction[]>([]);
  const [isBlockchainConnected, setIsBlockchainConnected] = useState(false);
  const [activeTab, setActiveTab] = useState<'records' | 'transactions' | 'verification' | 'settings'>('records');
  const [selectedRecord, setSelectedRecord] = useState<BlockchainRecord | null>(null);

  useEffect(() => {
    loadBlockchainRecords();
    loadBlockchainTransactions();
    checkBlockchainConnection();
  }, [patientId]);

  const loadBlockchainRecords = async () => {
    try {
      const response = await fetch(`/api/blockchain/records?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setRecords(data.records || []);
      }
    } catch (error) {
      console.error('Error loading blockchain records:', error);
    }
  };

  const loadBlockchainTransactions = async () => {
    try {
      const response = await fetch(`/api/blockchain/transactions?patientId=${patientId}`);
      if (response.ok) {
        const data = await response.json();
        setTransactions(data.transactions || []);
      }
    } catch (error) {
      console.error('Error loading blockchain transactions:', error);
    }
  };

  const checkBlockchainConnection = async () => {
    try {
      const response = await fetch('/api/blockchain/connection');
      if (response.ok) {
        const data = await response.json();
        setIsBlockchainConnected(data.connected);
      }
    } catch (error) {
      console.error('Error checking blockchain connection:', error);
    }
  };

  const createBlockchainRecord = async (recordData: any) => {
    try {
      const response = await fetch('/api/blockchain/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId,
          providerId,
          ...recordData
        }),
      });

      if (response.ok) {
        await loadBlockchainRecords();
        await loadBlockchainTransactions();
      }
    } catch (error) {
      console.error('Error creating blockchain record:', error);
    }
  };

  const verifyRecord = async (recordId: string) => {
    try {
      const response = await fetch(`/api/blockchain/records/${recordId}/verify`, {
        method: 'POST',
      });

      if (response.ok) {
        await loadBlockchainRecords();
        await loadBlockchainTransactions();
      }
    } catch (error) {
      console.error('Error verifying record:', error);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'medical_record': return <FileText className="h-4 w-4" />;
      case 'prescription': return <Pill className="h-4 w-4" />;
      case 'lab_result': return <TestTube className="h-4 w-4" />;
      case 'assessment': return <ClipboardList className="h-4 w-4" />;
      case 'treatment_plan': return <Target className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const getAccessLevelColor = (level: string) => {
    switch (level) {
      case 'public': return 'bg-green-100 text-green-800';
      case 'private': return 'bg-yellow-100 text-yellow-800';
      case 'restricted': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderRecord = (record: BlockchainRecord) => (
    <Card key={record.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getTypeIcon(record.type)}
            <div>
              <CardTitle className="text-lg">{record.title}</CardTitle>
              <CardDescription>
                Block #{record.blockNumber} • {new Date(record.timestamp).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getAccessLevelColor(record.accessLevel)}>
              {record.accessLevel}
            </Badge>
            {record.isVerified && (
              <Badge variant="default">
                <CheckCircle className="h-3 w-3 mr-1" />
                Verified
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Hash</Label>
              <div className="text-xs font-mono bg-muted p-2 rounded mt-1">
                {record.hash.substring(0, 20)}...
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium">Verifications</Label>
              <div className="text-sm font-medium mt-1">{record.verificationCount}</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              className="flex-1"
              onClick={() => setSelectedRecord(record)}
            >
              <Eye className="h-4 w-4 mr-2" />
              View Details
            </Button>
            <Button
              variant="outline"
              onClick={() => verifyRecord(record.id)}
              disabled={record.isVerified}
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderTransaction = (transaction: BlockchainTransaction) => (
    <Card key={transaction.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Network className="h-4 w-4" />
            <div>
              <CardTitle className="text-lg">{transaction.type}</CardTitle>
              <CardDescription>
                {new Date(transaction.timestamp).toLocaleDateString()}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getStatusColor(transaction.status)}>
              {transaction.status}
            </Badge>
            <div className="text-sm font-medium">
              {transaction.gasUsed} gas
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">From</Label>
              <div className="text-xs font-mono bg-muted p-2 rounded mt-1">
                {transaction.from.substring(0, 20)}...
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium">To</Label>
              <div className="text-xs font-mono bg-muted p-2 rounded mt-1">
                {transaction.to.substring(0, 20)}...
              </div>
            </div>
          </div>
          <div>
            <Label className="text-sm font-medium">Block Hash</Label>
            <div className="text-xs font-mono bg-muted p-2 rounded mt-1">
              {transaction.blockHash.substring(0, 20)}...
            </div>
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
            <Shield className="h-8 w-8 text-blue-600" />
            <span>Blockchain Medical Records</span>
            <Sparkles className="h-6 w-6 text-yellow-500" />
          </h1>
          <p className="text-muted-foreground">
            Secure, immutable medical records using blockchain technology
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={isBlockchainConnected ? 'default' : 'secondary'}>
            {isBlockchainConnected ? 'Blockchain Connected' : 'Blockchain Disconnected'}
          </Badge>
          <Button variant="outline" onClick={checkBlockchainConnection}>
            <Network className="h-4 w-4 mr-2" />
            Check Connection
          </Button>
        </div>
      </div>

      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'records' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('records')}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-2" />
          Records
        </Button>
        <Button
          variant={activeTab === 'transactions' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('transactions')}
          className="flex-1"
        >
          <Network className="h-4 w-4 mr-2" />
          Transactions
        </Button>
        <Button
          variant={activeTab === 'verification' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('verification')}
          className="flex-1"
        >
          <CheckCircle className="h-4 w-4 mr-2" />
          Verification
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

      {activeTab === 'records' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Blockchain Medical Records</h2>
            <Button onClick={() => createBlockchainRecord({ type: 'medical_record', title: 'New Record' })}>
              <Plus className="h-4 w-4 mr-2" />
              Create Record
            </Button>
          </div>

          {records.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Shield className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Blockchain Records</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Create your first blockchain medical record
                </p>
                <Button onClick={() => createBlockchainRecord({ type: 'medical_record', title: 'New Record' })}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Record
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {records.map(renderRecord)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'transactions' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Blockchain Transactions</h2>
          
          {transactions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Network className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Transactions</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Blockchain transactions will appear here
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {transactions.map(renderTransaction)}
            </div>
          )}
        </div>
      )}

      {activeTab === 'verification' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Record Verification</h2>
          
          <Card>
            <CardHeader>
              <CardTitle>Verification Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {records.filter(r => r.isVerified).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Verified Records</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">
                    {records.filter(r => !r.isVerified).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Pending Verification</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {Math.round(records.reduce((acc, r) => acc + r.verificationCount, 0) / records.length) || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Avg Verifications</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Blockchain Settings</h2>
          
          <Card>
            <CardHeader>
              <CardTitle>Network Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">Blockchain Network</Label>
                  <select className="w-full p-2 border rounded mt-1">
                    <option value="ethereum">Ethereum Mainnet</option>
                    <option value="polygon">Polygon</option>
                    <option value="arbitrum">Arbitrum</option>
                    <option value="testnet">Testnet</option>
                  </select>
                </div>
                <div>
                  <Label className="text-sm font-medium">Gas Price (Gwei)</Label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    defaultValue="20"
                    className="w-full p-2 border rounded mt-1"
                  />
                </div>
                <div>
                  <Label className="text-sm font-medium">Auto-Verification</Label>
                  <select className="w-full p-2 border rounded mt-1">
                    <option value="enabled">Enabled</option>
                    <option value="disabled">Disabled</option>
                  </select>
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
