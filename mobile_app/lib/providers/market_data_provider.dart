import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

class MarketDataProvider extends ChangeNotifier {
  Map<String, dynamic> _prices = {};
  Map<String, dynamic> _marketData = {};
  bool _isConnected = false;
  WebSocketChannel? _channel;
  List<String> _watchlist = [];
  
  // Getters
  Map<String, dynamic> get prices => _prices;
  Map<String, dynamic> get marketData => _marketData;
  bool get isConnected => _isConnected;
  List<String> get watchlist => _watchlist;
  
  MarketDataProvider() {
    _initializeWebSocket();
    _loadWatchlist();
  }
  
  // Initialize WebSocket connection
  void _initializeWebSocket() {
    try {
      // TODO: Replace with real WebSocket URL
      const wsUrl = 'ws://localhost:8000/ws';
      
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        (message) {
          _handleWebSocketMessage(message);
        },
        onError: (error) {
          print('WebSocket error: $error');
          _isConnected = false;
          notifyListeners();
        },
        onDone: () {
          print('WebSocket connection closed');
          _isConnected = false;
          notifyListeners();
        },
      );
      
      _isConnected = true;
      notifyListeners();
      
    } catch (e) {
      print('WebSocket başlatılamadı: $e');
      _isConnected = false;
      notifyListeners();
    }
  }
  
  // Handle WebSocket messages
  void _handleWebSocketMessage(dynamic message) {
    try {
      if (message is String) {
        final data = json.decode(message);
        _processMarketData(data);
      } else if (message is Map) {
        _processMarketData(Map<String, dynamic>.from(message));
      }
    } catch (e) {
      print('WebSocket mesaj işleme hatası: $e');
    }
  }
  
  // Process market data
  void _processMarketData(Map<String, dynamic> data) {
    try {
      if (data['type'] == 'price_update') {
        final symbol = data['symbol'];
        final price = data['price'];
        final volume = data['volume'];
        final timestamp = data['timestamp'];
        
        _prices[symbol] = {
          'price': price,
          'volume': volume,
          'timestamp': timestamp,
          'change': _calculatePriceChange(symbol, price),
        };
        
        notifyListeners();
      }
    } catch (e) {
      print('Market data işleme hatası: $e');
    }
  }
  
  // Calculate price change
  double _calculatePriceChange(String symbol, double newPrice) {
    if (_prices.containsKey(symbol)) {
      final oldPrice = _prices[symbol]['price'] ?? newPrice;
      return ((newPrice - oldPrice) / oldPrice) * 100;
    }
    return 0.0;
  }
  
  // Get price for symbol
  Map<String, dynamic>? getPrice(String symbol) {
    return _prices[symbol];
  }
  
  // Get all prices
  Map<String, dynamic> getAllPrices() {
    return Map.from(_prices);
  }
  
  // Add to watchlist
  void addToWatchlist(String symbol) {
    if (!_watchlist.contains(symbol)) {
      _watchlist.add(symbol);
      _saveWatchlist();
      notifyListeners();
    }
  }
  
  // Remove from watchlist
  void removeFromWatchlist(String symbol) {
    _watchlist.remove(symbol);
    _saveWatchlist();
    notifyListeners();
  }
  
  // Load watchlist from preferences
  Future<void> _loadWatchlist() async {
    // TODO: Implement SharedPreferences
    _watchlist = ['SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'AAPL', 'MSFT'];
    notifyListeners();
  }
  
  // Save watchlist to preferences
  Future<void> _saveWatchlist() async {
    // TODO: Implement SharedPreferences
  }
  
  // Update market data manually (for testing)
  void updatePrice(String symbol, double price, {double? volume}) {
    _prices[symbol] = {
      'price': price,
      'volume': volume ?? (_prices[symbol]?['volume'] ?? 0),
      'timestamp': DateTime.now().toIso8601String(),
      'change': _calculatePriceChange(symbol, price),
    };
    
    notifyListeners();
  }
  
  // Disconnect WebSocket
  void disconnect() {
    _channel?.sink.close();
    _isConnected = false;
    notifyListeners();
  }
  
  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
