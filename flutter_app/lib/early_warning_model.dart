import 'package:cloud_firestore/cloud_firestore.dart';

class EarlyWarning {
  final String symbol;
  final String signal;
  final double confidence;
  final double bullishScore;
  final double bearishScore;
  final double bullishEws;
  final double bearishEws;
  final double socialScore;
  final double trendScore;
  final double newsScore;
  final DateTime timestamp;

  EarlyWarning({
    required this.symbol,
    required this.signal,
    required this.confidence,
    required this.bullishScore,
    required this.bearishScore,
    required this.bullishEws,
    required this.bearishEws,
    required this.socialScore,
    required this.trendScore,
    required this.newsScore,
    required this.timestamp,
  });

  factory EarlyWarning.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return EarlyWarning(
      symbol: data['symbol'] ?? '',
      signal: data['signal'] ?? '',
      confidence: (data['confidence'] ?? 0).toDouble(),
      bullishScore: (data['bullish_score'] ?? 0).toDouble(),
      bearishScore: (data['bearish_score'] ?? 0).toDouble(),
      bullishEws: (data['bullish_ews'] ?? 0).toDouble(),
      bearishEws: (data['bearish_ews'] ?? 0).toDouble(),
      socialScore: (data['social_score'] ?? 0).toDouble(),
      trendScore: (data['trend_score'] ?? 0).toDouble(),
      newsScore: (data['news_score'] ?? 0).toDouble(),
      timestamp: (data['timestamp'] is Timestamp)
          ? (data['timestamp'] as Timestamp).toDate()
          : DateTime.now(),
    );
  }
}

Stream<List<EarlyWarning>> earlyWarningStream() {
  return FirebaseFirestore.instance
      .collection('early_warnings')
      .orderBy('confidence', descending: true)
      .snapshots()
      .map((snapshot) => snapshot.docs
          .map((doc) => EarlyWarning.fromFirestore(doc))
          .toList());
} 