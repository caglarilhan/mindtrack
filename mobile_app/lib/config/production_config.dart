// PRD v2.0 - BIST AI Smart Trader Production Configuration
class ProductionConfig {
  // API Configuration
  static const String baseUrl = 'https://your-production-api.com';
  static const String apiVersion = '/api/v1';
  static const String wsUrl = 'wss://your-production-api.com/ws';
  
  // Firebase Configuration
  static const String firebaseProjectId = 'your-firebase-project-id';
  static const String firebaseApiKey = 'your-firebase-api-key';
  static const String firebaseAuthDomain = 'your-firebase-auth-domain';
  static const String firebaseStorageBucket = 'your-firebase-storage-bucket';
  static const String firebaseMessagingSenderId = 'your-messaging-sender-id';
  static const String firebaseAppId = 'your-firebase-app-id';
  
  // Feature Flags
  static const bool enableRealTimeData = true;
  static const bool enablePushNotifications = true;
  static const bool enableAnalytics = true;
  static const bool enableCrashReporting = true;
  
  // Performance Settings
  static const Duration priceRefreshInterval = Duration(seconds: 5);
  static const Duration signalRefreshInterval = Duration(seconds: 30);
  static const Duration portfolioRefreshInterval = Duration(minutes: 1);
  
  // Cache Settings
  static const Duration priceCacheDuration = Duration(minutes: 5);
  static const Duration signalCacheDuration = Duration(minutes: 10);
  static const Duration portfolioCacheDuration = Duration(minutes: 15);
  
  // Security Settings
  static const bool enableSSL = true;
  static const bool enableCertificatePinning = false;
  static const Duration tokenRefreshInterval = Duration(minutes: 25);
  
  // Monitoring Settings
  static const bool enablePerformanceMonitoring = true;
  static const bool enableErrorReporting = true;
  static const bool enableUsageAnalytics = true;
  
  // Default Symbols (Production)
  static const List<String> defaultSymbols = [
    'SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'AKBNK.IS', 'GARAN.IS',
    'THYAO.IS', 'KRDMD.IS', 'ASELS.IS', 'BIMAS.IS', 'SAHOL.IS',
    'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META'
  ];
  
  // App Information
  static const String appName = 'BIST AI Smart Trader';
  static const String appVersion = '2.0.0';
  static const String appDescription = 'PRD v2.0 - AI-powered trading assistant';
  static const String appWebsite = 'https://your-app-website.com';
  static const String supportEmail = 'support@your-app.com';
  
  // Legal Information
  static const String privacyPolicyUrl = 'https://your-app.com/privacy';
  static const String termsOfServiceUrl = 'https://your-app.com/terms';
  static const String disclaimer = 'This app is for educational purposes only. Not financial advice.';
  
  // Social Media
  static const String twitterUrl = 'https://twitter.com/your-app';
  static const String linkedinUrl = 'https://linkedin.com/company/your-app';
  static const String githubUrl = 'https://github.com/your-app';
  
  // Support & Documentation
  static const String helpCenterUrl = 'https://help.your-app.com';
  static const String apiDocsUrl = 'https://docs.your-app.com';
  static const String communityUrl = 'https://community.your-app.com';
}
