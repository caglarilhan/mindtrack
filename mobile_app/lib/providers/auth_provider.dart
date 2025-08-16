import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthProvider extends ChangeNotifier {
  bool _isAuthenticated = false;
  bool _isDarkMode = false;
  String? _userToken;
  String? _userId;
  String? _username;
  
  // Getters
  bool get isAuthenticated => _isAuthenticated;
  bool get isDarkMode => _isDarkMode;
  String? get userToken => _userToken;
  String? get userId => _userId;
  String? get username => _username;
  
  AuthProvider() {
    _loadPreferences();
  }
  
  // Load saved preferences
  Future<void> _loadPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _isDarkMode = prefs.getBool('isDarkMode') ?? false;
      _userToken = prefs.getString('userToken');
      _userId = prefs.getString('userId');
      _username = prefs.getString('username');
      
      if (_userToken != null) {
        _isAuthenticated = true;
      }
      
      notifyListeners();
    } catch (e) {
      print('Preferences yüklenemedi: $e');
    }
  }
  
  // Save preferences
  Future<void> _savePreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('isDarkMode', _isDarkMode);
      await prefs.setString('userToken', _userToken ?? '');
      await prefs.setString('userId', _userId ?? '');
      await prefs.setString('username', _username ?? '');
    } catch (e) {
      print('Preferences kaydedilemedi: $e');
    }
  }
  
  // Login
  Future<bool> login(String username, String password) async {
    try {
      // TODO: Implement real API login
      // For now, simulate successful login
      await Future.delayed(const Duration(seconds: 1));
      
      _isAuthenticated = true;
      _userToken = 'demo_token_${DateTime.now().millisecondsSinceEpoch}';
      _userId = 'user_${DateTime.now().millisecondsSinceEpoch}';
      _username = username;
      
      await _savePreferences();
      notifyListeners();
      
      return true;
    } catch (e) {
      print('Login hatası: $e');
      return false;
    }
  }
  
  // Logout
  Future<void> logout() async {
    _isAuthenticated = false;
    _userToken = null;
    _userId = null;
    _username = null;
    
    await _savePreferences();
    notifyListeners();
  }
  
  // Toggle dark mode
  Future<void> toggleDarkMode() async {
    _isDarkMode = !_isDarkMode;
    await _savePreferences();
    notifyListeners();
  }
  
  // Update user info
  Future<void> updateUserInfo({
    String? username,
    String? userId,
  }) async {
    if (username != null) _username = username;
    if (userId != null) _userId = userId;
    
    await _savePreferences();
    notifyListeners();
  }
}
