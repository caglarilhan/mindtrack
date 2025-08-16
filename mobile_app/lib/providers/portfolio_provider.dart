import 'package:flutter/material.dart';

class PortfolioProvider extends ChangeNotifier {
  Map<String, dynamic> _portfolio = {};
  List<Map<String, dynamic>> _transactions = [];
  List<Map<String, dynamic>> _positions = [];
  double _totalValue = 0.0;
  double _totalPnL = 0.0;
  bool _isLoading = false;
  
  // Getters
  Map<String, dynamic> get portfolio => _portfolio;
  List<Map<String, dynamic>> get transactions => _transactions;
  List<Map<String, dynamic>> get positions => _positions;
  double get totalValue => _totalValue;
  double get totalPnL => _totalPnL;
  bool get isLoading => _isLoading;
  
  PortfolioProvider() {
    _loadPortfolio();
  }
  
  // Load portfolio data
  Future<void> _loadPortfolio() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      // TODO: Implement real API call
      await Future.delayed(const Duration(seconds: 1));
      
      // Mock data for testing
      _portfolio = {
        'cash': 10000.0,
        'invested': 5000.0,
        'total_value': 15000.0,
        'daily_change': 2.5,
        'monthly_change': 8.2,
        'yearly_change': 15.7,
      };
      
      _positions = [
        {
          'symbol': 'SISE.IS',
          'quantity': 100,
          'avg_price': 45.20,
          'current_price': 46.80,
          'market_value': 4680.0,
          'unrealized_pnl': 160.0,
          'pnl_percentage': 3.54,
          'weight': 31.2,
        },
        {
          'symbol': 'EREGL.IS',
          'quantity': 50,
          'avg_price': 32.15,
          'current_price': 31.80,
          'market_value': 1590.0,
          'unrealized_pnl': -17.5,
          'pnl_percentage': -1.09,
          'weight': 10.6,
        }
      ];
      
      _transactions = [
        {
          'id': '1',
          'symbol': 'SISE.IS',
          'type': 'BUY',
          'quantity': 100,
          'price': 45.20,
          'total': 4520.0,
          'timestamp': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
          'status': 'COMPLETED'
        },
        {
          'id': '2',
          'symbol': 'EREGL.IS',
          'type': 'BUY',
          'quantity': 50,
          'price': 32.15,
          'total': 1607.5,
          'timestamp': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
          'status': 'COMPLETED'
        }
      ];
      
      _calculateTotals();
      
    } catch (e) {
      print('Portfolio yüklenemedi: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Calculate totals
  void _calculateTotals() {
    _totalValue = _portfolio['total_value'] ?? 0.0;
    _totalPnL = _positions.fold(0.0, (sum, position) => sum + (position['unrealized_pnl'] ?? 0.0));
  }
  
  // Add position
  void addPosition(Map<String, dynamic> position) {
    _positions.add(position);
    _calculateTotals();
    notifyListeners();
  }
  
  // Update position
  void updatePosition(String symbol, Map<String, dynamic> updates) {
    final index = _positions.indexWhere((position) => position['symbol'] == symbol);
    if (index != -1) {
      _positions[index].addAll(updates);
      _calculateTotals();
      notifyListeners();
    }
  }
  
  // Remove position
  void removePosition(String symbol) {
    _positions.removeWhere((position) => position['symbol'] == symbol);
    _calculateTotals();
    notifyListeners();
  }
  
  // Add transaction
  void addTransaction(Map<String, dynamic> transaction) {
    _transactions.insert(0, transaction);
    notifyListeners();
  }
  
  // Get position by symbol
  Map<String, dynamic>? getPositionBySymbol(String symbol) {
    try {
      return _positions.firstWhere((position) => position['symbol'] == symbol);
    } catch (e) {
      return null;
    }
  }
  
  // Get transactions by symbol
  List<Map<String, dynamic>> getTransactionsBySymbol(String symbol) {
    return _transactions.where((transaction) => transaction['symbol'] == symbol).toList();
  }
  
  // Get transactions by type
  List<Map<String, dynamic>> getTransactionsByType(String type) {
    return _transactions.where((transaction) => transaction['type'] == type.toUpperCase()).toList();
  }
  
  // Update portfolio value
  void updatePortfolioValue(double newValue) {
    _portfolio['total_value'] = newValue;
    _totalValue = newValue;
    notifyListeners();
  }
  
  // Refresh portfolio
  Future<void> refreshPortfolio() async {
    await _loadPortfolio();
  }
  
  // Get portfolio performance
  Map<String, double> getPortfolioPerformance() {
    return {
      'daily_change': _portfolio['daily_change'] ?? 0.0,
      'monthly_change': _portfolio['monthly_change'] ?? 0.0,
      'yearly_change': _portfolio['yearly_change'] ?? 0.0,
    };
  }
  
  // Get top performers
  List<Map<String, dynamic>> getTopPerformers(int count) {
    final sorted = List<Map<String, dynamic>>.from(_positions);
    sorted.sort((a, b) => (b['pnl_percentage'] ?? 0.0).compareTo(a['pnl_percentage'] ?? 0.0));
    return sorted.take(count).toList();
  }
  
  // Get worst performers
  List<Map<String, dynamic>> getWorstPerformers(int count) {
    final sorted = List<Map<String, dynamic>>.from(_positions);
    sorted.sort((a, b) => (a['pnl_percentage'] ?? 0.0).compareTo(b['pnl_percentage'] ?? 0.0));
    return sorted.take(count).toList();
  }
}
