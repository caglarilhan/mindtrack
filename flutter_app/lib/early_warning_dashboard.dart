import 'package:flutter/material.dart';
import 'early_warning_model.dart';

class EarlyWarningDashboard extends StatelessWidget {
  const EarlyWarningDashboard({Key? key}) : super(key: key);

  Color _signalColor(String signal) {
    switch (signal) {
      case 'YÜKSELİŞ ERKEN UYARI':
        return Colors.green;
      case 'DÜŞÜŞ ERKEN UYARI':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _signalIcon(String signal) {
    switch (signal) {
      case 'YÜKSELİŞ ERKEN UYARI':
        return Icons.trending_up;
      case 'DÜŞÜŞ ERKEN UYARI':
        return Icons.trending_down;
      default:
        return Icons.horizontal_rule;
    }
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<List<EarlyWarning>>(
      stream: earlyWarningStream(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const Center(child: Text('Veri bulunamadı.'));
        }
        final warnings = snapshot.data!;
        return ListView.builder(
          itemCount: warnings.length,
          itemBuilder: (context, index) {
            final ew = warnings[index];
            return Card(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              child: ListTile(
                leading: Icon(_signalIcon(ew.signal), color: _signalColor(ew.signal), size: 32),
                title: Text(
                  ew.symbol,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      ew.signal,
                      style: TextStyle(
                        color: _signalColor(ew.signal),
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Text('Güven: ', style: TextStyle(fontWeight: FontWeight.w500)),
                        Text((ew.confidence * 100).toStringAsFixed(1) + '%'),
                        const SizedBox(width: 16),
                        Text('Bullish: ${ew.bullishScore.toStringAsFixed(2)}'),
                        const SizedBox(width: 8),
                        Text('Bearish: ${ew.bearishScore.toStringAsFixed(2)}'),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        Text('Sosyal: ${ew.socialScore.toStringAsFixed(2)}'),
                        const SizedBox(width: 8),
                        Text('Trend: ${ew.trendScore.toStringAsFixed(2)}'),
                        const SizedBox(width: 8),
                        Text('Haber: ${ew.newsScore.toStringAsFixed(2)}'),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text('Son güncelleme: ${ew.timestamp.toLocal()}'),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
} 