"""
PRD v2.0 - Configuration Management
Environment variables ve config yönetimi
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class APIConfig:
    """API configuration"""
    finnhub_api_key: str
    fmp_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        return cls(
            finnhub_api_key=os.getenv('FINNHUB_API_KEY', 'demo'),
            fmp_api_key=os.getenv('FMP_API_KEY'),
            news_api_key=os.getenv('NEWS_API_KEY')
        )

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    
    @classmethod
    def from_env(cls):
        return cls(
            project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
            private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            private_key=os.getenv('FIREBASE_PRIVATE_KEY', ''),
            client_email=os.getenv('FIREBASE_CLIENT_EMAIL', ''),
            client_id=os.getenv('FIREBASE_CLIENT_ID', ''),
            auth_uri=os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            token_uri=os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            auth_provider_x509_cert_url=os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
            client_x509_cert_url=os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
        )

@dataclass
class WebSocketConfig:
    """WebSocket configuration"""
    max_connections: int = 100
    heartbeat_interval: int = 30
    reconnect_delay: int = 5
    
    @classmethod
    def from_env(cls):
        return cls(
            max_connections=int(os.getenv('WEBSOCKET_MAX_CONNECTIONS', '100')),
            heartbeat_interval=int(os.getenv('WEBSOCKET_HEARTBEAT_INTERVAL', '30')),
            reconnect_delay=int(os.getenv('WEBSOCKET_RECONNECT_DELAY', '5'))
        )

@dataclass
class AIModelConfig:
    """AI Model configuration"""
    lightgbm_model_path: str = "models/lightgbm_model.pkl"
    lstm_model_path: str = "models/lstm_model.h5"
    timegpt_model_path: str = "models/timegpt_model.json"
    ensemble_weights_path: str = "models/ensemble_weights.json"
    
    @classmethod
    def from_env(cls):
        return cls(
            lightgbm_model_path=os.getenv('LIGHTGBM_MODEL_PATH', 'models/lightgbm_model.pkl'),
            lstm_model_path=os.getenv('LSTM_MODEL_PATH', 'models/lstm_model.h5'),
            timegpt_model_path=os.getenv('TIMEGPT_MODEL_PATH', 'models/timegpt_model.json'),
            ensemble_weights_path=os.getenv('ENSEMBLE_WEIGHTS_PATH', 'models/ensemble_weights.json')
        )

@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    finbert_model_path: str = "models/finbert-tr"
    update_interval: int = 3600  # 1 saat
    confidence_threshold: float = 0.6
    
    @classmethod
    def from_env(cls):
        return cls(
            finbert_model_path=os.getenv('FINBERT_MODEL_PATH', 'models/finbert-tr'),
            update_interval=int(os.getenv('SENTIMENT_UPDATE_INTERVAL', '3600')),
            confidence_threshold=float(os.getenv('SENTIMENT_CONFIDENCE_THRESHOLD', '0.6'))
        )

@dataclass
class MarketDataConfig:
    """Market data configuration"""
    update_interval: int = 60  # 1 dakika
    price_history_days: int = 365
    fundamental_update_interval: int = 86400  # 24 saat
    
    @classmethod
    def from_env(cls):
        return cls(
            update_interval=int(os.getenv('MARKET_DATA_UPDATE_INTERVAL', '60')),
            price_history_days=int(os.getenv('PRICE_HISTORY_DAYS', '365')),
            fundamental_update_interval=int(os.getenv('FUNDAMENTAL_UPDATE_INTERVAL', '86400'))
        )

@dataclass
class RiskManagementConfig:
    """Risk management configuration"""
    max_position_size: float = 0.1  # Portföyün %10'u
    stop_loss_default: float = 0.05  # %5
    take_profit_default: float = 0.15  # %15
    max_drawdown_threshold: float = 0.25  # %25
    
    @classmethod
    def from_env(cls):
        return cls(
            max_position_size=float(os.getenv('MAX_POSITION_SIZE', '0.1')),
            stop_loss_default=float(os.getenv('STOP_LOSS_DEFAULT', '0.05')),
            take_profit_default=float(os.getenv('TAKE_PROFIT_DEFAULT', '0.15')),
            max_drawdown_threshold=float(os.getenv('MAX_DRAWDOWN_THRESHOLD', '0.25'))
        )

@dataclass
class PerformanceConfig:
    """Performance thresholds configuration"""
    min_signal_confidence: float = 0.7
    min_fundamental_score: float = 0.6
    min_technical_score: float = 0.6
    min_sentiment_score: float = 0.5
    
    @classmethod
    def from_env(cls):
        return cls(
            min_signal_confidence=float(os.getenv('MIN_SIGNAL_CONFIDENCE', '0.7')),
            min_fundamental_score=float(os.getenv('MIN_FUNDAMENTAL_SCORE', '0.6')),
            min_technical_score=float(os.getenv('MIN_TECHNICAL_SCORE', '0.6')),
            min_sentiment_score=float(os.getenv('MIN_SENTIMENT_SCORE', '0.5'))
        )

@dataclass
class NotificationConfig:
    """Notification configuration"""
    push_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    
    @classmethod
    def from_env(cls):
        return cls(
            push_enabled=os.getenv('PUSH_NOTIFICATION_ENABLED', 'true').lower() == 'true',
            email_enabled=os.getenv('EMAIL_NOTIFICATION_ENABLED', 'true').lower() == 'true',
            sms_enabled=os.getenv('SMS_NOTIFICATION_ENABLED', 'false').lower() == 'true'
        )

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_path: str = "logs/bist_ai.log"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls):
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file_path=os.getenv('LOG_FILE_PATH', 'logs/bist_ai.log'),
            max_size=int(os.getenv('LOG_MAX_SIZE', '10485760')),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )

@dataclass
class DevelopmentConfig:
    """Development configuration"""
    debug_mode: bool = False
    test_mode: bool = False
    mock_data_enabled: bool = False
    
    @classmethod
    def from_env(cls):
        return cls(
            debug_mode=os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            test_mode=os.getenv('TEST_MODE', 'false').lower() == 'true',
            mock_data_enabled=os.getenv('MOCK_DATA_ENABLED', 'false').lower() == 'true'
        )

class Config:
    """Ana configuration sınıfı"""
    
    def __init__(self):
        self.api = APIConfig.from_env()
        self.firebase = FirebaseConfig.from_env()
        self.websocket = WebSocketConfig.from_env()
        self.ai_model = AIModelConfig.from_env()
        self.sentiment = SentimentConfig.from_env()
        self.market_data = MarketDataConfig.from_env()
        self.risk_management = RiskManagementConfig.from_env()
        self.performance = PerformanceConfig.from_env()
        self.notification = NotificationConfig.from_env()
        self.logging = LoggingConfig.from_env()
        self.development = DevelopmentConfig.from_env()
    
    def validate(self) -> bool:
        """Configuration validation"""
        required_fields = [
            self.api.finnhub_api_key,
            self.firebase.project_id,
            self.firebase.private_key,
            self.firebase.client_email
        ]
        
        return all(field for field in required_fields)
    
    def get_firebase_credentials(self) -> dict:
        """Firebase credentials dictionary"""
        return {
            "type": "service_account",
            "project_id": self.firebase.project_id,
            "private_key_id": self.firebase.private_key_id,
            "private_key": self.firebase.private_key,
            "client_email": self.firebase.client_email,
            "client_id": self.firebase.client_id,
            "auth_uri": self.firebase.auth_uri,
            "token_uri": self.firebase.token_uri,
            "auth_provider_x509_cert_url": self.firebase.auth_provider_x509_cert_url,
            "client_x509_cert_url": self.firebase.client_x509_cert_url
        }

# Global config instance
config = Config()

def get_config() -> Config:
    """Global config instance'ını döndür"""
    return config

# Test fonksiyonu
def test_config():
    """Configuration test"""
    try:
        cfg = Config()
        
        print("✅ Configuration yüklendi!")
        print(f"Finnhub API Key: {cfg.api.finnhub_api_key[:10]}...")
        print(f"Firebase Project: {cfg.firebase.project_id}")
        print(f"WebSocket Max Connections: {cfg.websocket.max_connections}")
        print(f"AI Model Path: {cfg.ai_model.lightgbm_model_path}")
        print(f"Risk Management - Max Position: {cfg.risk_management.max_position_size}")
        print(f"Performance - Min Signal Confidence: {cfg.performance.min_signal_confidence}")
        
        if cfg.validate():
            print("✅ Configuration validation başarılı!")
        else:
            print("❌ Configuration validation başarısız!")
            
    except Exception as e:
        print(f"❌ Configuration test hatası: {e}")

if __name__ == "__main__":
    test_config()
