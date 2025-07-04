import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const BistAIApp());
}

class BistAIApp extends StatelessWidget {
  const BistAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BIST AI Kazanç Asistanı',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.green,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.green,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const SignalDashboard(),
    );
  }
}

class SignalDashboard extends StatefulWidget {
  const SignalDashboard({super.key});

  @override
  State<SignalDashboard> createState() => _SignalDashboardState();
}

class _SignalDashboardState extends State<SignalDashboard> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🎯 BIST AI Sinyaller'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {}); // Refresh signals
            },
          ),
        ],
      ),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance
            .collection('latest_signals')
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Hata: ${snapshot.error}'),
                ],
              ),
            );
          }

          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Sinyaller yükleniyor...'),
                ],
              ),
            );
          }

          final signals = snapshot.data?.docs ?? [];

          if (signals.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.signal_cellular_off, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('Henüz sinyal yok'),
                  Text('Backend çalışıyor mu kontrol edin...'),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: signals.length,
            itemBuilder: (context, index) {
              final signal = signals[index].data() as Map<String, dynamic>;
              return SignalCard(signal: signal);
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Test için manuel sinyal ekle
          _addTestSignal();
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  void _addTestSignal() {
    FirebaseFirestore.instance.collection('latest_signals').add({
      'symbol': 'THYAO.IS',
      'signal': 'BUY',
      'confidence': 0.87,
      'timestamp': Timestamp.now(),
      'model': 'TestSignal',
      'price': 25.40,
      'reason': 'Test sinyali - Manuel eklendi',
      'sl_percent': 5.0,
      'tp_percent': 12.0,
    });
  }
}

class SignalCard extends StatelessWidget {
  final Map<String, dynamic> signal;

  const SignalCard({super.key, required this.signal});

  @override
  Widget build(BuildContext context) {
    final signalType = signal['signal'] ?? 'HOLD';
    final confidence = (signal['confidence'] ?? 0.0) * 100;
    final symbol = signal['symbol'] ?? '';
    final price = signal['price'] ?? 0.0;
    final reason = signal['reason'] ?? '';

    Color signalColor;
    IconData signalIcon;
    
    switch (signalType) {
      case 'BUY':
        signalColor = Colors.green;
        signalIcon = Icons.trending_up;
        break;
      case 'SELL':
        signalColor = Colors.red;
        signalIcon = Icons.trending_down;
        break;
      default:
        signalColor = Colors.orange;
        signalIcon = Icons.pause;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(signalIcon, color: signalColor, size: 32),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        symbol,
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '₺${price.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: signalColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    signalType,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Güven: %${confidence.toStringAsFixed(1)}',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      if (signal['sl_percent'] != null)
                        Text(
                          'SL: %${signal['sl_percent']}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      if (signal['tp_percent'] != null)
                        Text(
                          'TP: %${signal['tp_percent']}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              reason,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
