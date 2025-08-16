"""
PRD v2.0 - Firestore Veri Şeması
Veri ve Model Akışı için Firestore collections tasarımı
"""

from firebase_admin import firestore
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class FirestoreSchema:
    """BIST AI Smart Trader v2.0 Firestore şeması"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        
    # Collection names
    COLLECTIONS = {
        'prices': 'market_prices',
        'fundamentals': 'company_fundamentals', 
        'signals': 'trading_signals',
        'portfolios': 'user_portfolios',
        'users': 'users',
        'news': 'market_news',
        'sentiment': 'sentiment_scores',
        'backtests': 'backtest_results',
        'models': 'ai_models'
    }
    
    def create_price_document(self, symbol: str, price_data: Dict) -> Dict:
        """Fiyat verisi için document yapısı"""
        return {
            'symbol': symbol,
            'price': price_data.get('price'),
            'volume': price_data.get('volume'),
            'timestamp': price_data.get('timestamp'),
            'source': price_data.get('source', 'unknown'),
            'open': price_data.get('open'),
            'high': price_data.get('high'),
            'low': price_data.get('low'),
            'close': price_data.get('close'),
            'market_cap': price_data.get('market_cap'),
            'pe_ratio': price_data.get('pe_ratio'),
            'dividend_yield': price_data.get('dividend_yield'),
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
    
    def create_fundamental_document(self, symbol: str, fundamental_data: Dict) -> Dict:
        """Fundamental veri için document yapısı (DuPont + Piotroski)"""
        return {
            'symbol': symbol,
            'company_name': fundamental_data.get('company_name'),
            'sector': fundamental_data.get('sector'),
            'industry': fundamental_data.get('industry'),
            
            # DuPont Analizi
            'dupont_analysis': {
                'roe': fundamental_data.get('roe'),
                'roa': fundamental_data.get('roa'),
                'net_profit_margin': fundamental_data.get('net_profit_margin'),
                'asset_turnover': fundamental_data.get('asset_turnover'),
                'financial_leverage': fundamental_data.get('financial_leverage'),
                'dupont_score': fundamental_data.get('dupont_score')
            },
            
            # Piotroski F-Score
            'piotroski_score': fundamental_data.get('piotroski_score'),
            'piotroski_details': fundamental_data.get('piotroski_details', {}),
            
            # Finansal Oranlar
            'financial_ratios': {
                'debt_to_equity': fundamental_data.get('debt_to_equity'),
                'current_ratio': fundamental_data.get('current_ratio'),
                'quick_ratio': fundamental_data.get('quick_ratio'),
                'gross_margin': fundamental_data.get('gross_margin'),
                'operating_margin': fundamental_data.get('operating_margin'),
                'ebitda_margin': fundamental_data.get('ebitda_margin')
            },
            
            'last_updated': firestore.SERVER_TIMESTAMP,
            'data_source': fundamental_data.get('data_source', 'unknown')
        }
    
    def create_signal_document(self, signal_data: Dict) -> Dict:
        """Trading sinyali için document yapısı"""
        return {
            'symbol': signal_data.get('symbol'),
            'signal_type': signal_data.get('signal_type'),  # BUY, SELL, HOLD
            'confidence': signal_data.get('confidence'),  # 0-100
            'timestamp': firestore.SERVER_TIMESTAMP,
            
            # Sinyal Detayları
            'signal_details': {
                'technical_score': signal_data.get('technical_score'),
                'fundamental_score': signal_data.get('fundamental_score'),
                'sentiment_score': signal_data.get('sentiment_score'),
                'market_regime': signal_data.get('market_regime'),
                'time_horizon': signal_data.get('time_horizon')  # 1d, 4h, 10d
            },
            
            # AI Model Çıktıları
            'ai_models': {
                'lightgbm_prob': signal_data.get('lightgbm_prob'),
                'lstm_prob': signal_data.get('lstm_prob'),
                'timegpt_prob': signal_data.get('timegpt_prob'),
                'ensemble_prob': signal_data.get('ensemble_prob')
            },
            
            # Formasyon Bilgileri
            'patterns': signal_data.get('patterns', []),
            'support_resistance': signal_data.get('support_resistance', {}),
            
            # Risk Yönetimi
            'risk_management': {
                'stop_loss': signal_data.get('stop_loss'),
                'take_profit': signal_data.get('take_profit'),
                'position_size': signal_data.get('position_size'),
                'risk_reward_ratio': signal_data.get('risk_reward_ratio')
            },
            
            'status': 'active',  # active, executed, expired
            'executed_at': None,
            'execution_price': None
        }
    
    def create_portfolio_document(self, user_id: str, portfolio_data: Dict) -> Dict:
        """Kullanıcı portföyü için document yapısı"""
        return {
            'user_id': user_id,
            'portfolio_name': portfolio_data.get('portfolio_name', 'Ana Portföy'),
            'total_value': portfolio_data.get('total_value', 0),
            'cash_balance': portfolio_data.get('cash_balance', 0),
            'invested_amount': portfolio_data.get('invested_amount', 0),
            'unrealized_pnl': portfolio_data.get('unrealized_pnl', 0),
            'realized_pnl': portfolio_data.get('realized_pnl', 0),
            
            # Portföy Performansı
            'performance': {
                'total_return': portfolio_data.get('total_return', 0),
                'sharpe_ratio': portfolio_data.get('sharpe_ratio', 0),
                'max_drawdown': portfolio_data.get('max_drawdown', 0),
                'volatility': portfolio_data.get('volatility', 0)
            },
            
            # RL Agent Bilgileri
            'rl_agent': {
                'model_version': portfolio_data.get('rl_model_version'),
                'last_optimization': portfolio_data.get('last_optimization'),
                'optimization_frequency': portfolio_data.get('optimization_frequency', 'daily')
            },
            
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'is_active': True
        }
    
    def create_portfolio_position_document(self, portfolio_id: str, position_data: Dict) -> Dict:
        """Portföy pozisyonu için document yapısı"""
        return {
            'portfolio_id': portfolio_id,
            'symbol': position_data.get('symbol'),
            'quantity': position_data.get('quantity'),
            'average_price': position_data.get('average_price'),
            'current_price': position_data.get('current_price'),
            'market_value': position_data.get('market_value'),
            'unrealized_pnl': position_data.get('unrealized_pnl'),
            'unrealized_pnl_percent': position_data.get('unrealized_pnl_percent'),
            
            # Pozisyon Detayları
            'position_type': position_data.get('position_type', 'long'),  # long, short
            'entry_date': position_data.get('entry_date'),
            'last_updated': firestore.SERVER_TIMESTAMP,
            
            # Risk Yönetimi
            'stop_loss': position_data.get('stop_loss'),
            'take_profit': position_data.get('take_profit'),
            'trailing_stop': position_data.get('trailing_stop'),
            
            # AI Önerileri
            'ai_recommendations': {
                'hold_probability': position_data.get('hold_probability'),
                'sell_probability': position_data.get('sell_probability'),
                'confidence': position_data.get('confidence'),
                'next_review': position_data.get('next_review')
            }
        }
    
    def create_user_document(self, user_data: Dict) -> Dict:
        """Kullanıcı bilgileri için document yapısı"""
        return {
            'email': user_data.get('email'),
            'display_name': user_data.get('display_name'),
            'risk_profile': user_data.get('risk_profile', 'moderate'),  # conservative, moderate, aggressive
            'investment_goals': user_data.get('investment_goals', []),
            'preferred_sectors': user_data.get('preferred_sectors', []),
            'notification_preferences': {
                'push_notifications': user_data.get('push_notifications', True),
                'email_notifications': user_data.get('email_notifications', True),
                'signal_alerts': user_data.get('signal_alerts', True),
                'portfolio_updates': user_data.get('portfolio_updates', True)
            },
            
            # Kullanıcı Ayarları
            'settings': {
                'default_currency': user_data.get('default_currency', 'TRY'),
                'timezone': user_data.get('timezone', 'Europe/Istanbul'),
                'language': user_data.get('language', 'tr'),
                'theme': user_data.get('theme', 'light')
            },
            
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': firestore.SERVER_TIMESTAMP,
            'is_active': True
        }
    
    def create_news_document(self, news_data: Dict) -> Dict:
        """Haber verisi için document yapısı"""
        return {
            'title': news_data.get('title'),
            'content': news_data.get('content'),
            'source': news_data.get('source'),
            'url': news_data.get('url'),
            'published_at': news_data.get('published_at'),
            'symbols': news_data.get('symbols', []),  # Etkilenen semboller
            'sector': news_data.get('sector'),
            'sentiment_score': news_data.get('sentiment_score'),
            'sentiment_label': news_data.get('sentiment_label'),  # positive, negative, neutral
            'impact_score': news_data.get('impact_score'),  # 1-10
            'created_at': firestore.SERVER_TIMESTAMP
        }
    
    def create_sentiment_document(self, sentiment_data: Dict) -> Dict:
        """Sentiment skoru için document yapısı"""
        return {
            'symbol': sentiment_data.get('symbol'),
            'timestamp': firestore.SERVER_TIMESTAMP,
            'overall_sentiment': sentiment_data.get('overall_sentiment'),
            
            # Sentiment Detayları
            'sentiment_breakdown': {
                'news_sentiment': sentiment_data.get('news_sentiment'),
                'social_sentiment': sentiment_data.get('social_sentiment'),
                'kap_sentiment': sentiment_data.get('kap_sentiment'),
                'analyst_sentiment': sentiment_data.get('analyst_sentiment')
            },
            
            'sentiment_score': sentiment_data.get('sentiment_score'),  # -1 to 1
            'confidence': sentiment_data.get('confidence'),
            'data_sources': sentiment_data.get('data_sources', []),
            'last_updated': firestore.SERVER_TIMESTAMP
        }
    
    def create_backtest_document(self, backtest_data: Dict) -> Dict:
        """Backtest sonuçları için document yapısı"""
        return {
            'strategy_name': backtest_data.get('strategy_name'),
            'symbols': backtest_data.get('symbols', []),
            'start_date': backtest_data.get('start_date'),
            'end_date': backtest_data.get('end_date'),
            
            # Performans Metrikleri
            'performance_metrics': {
                'total_return': backtest_data.get('total_return'),
                'annualized_return': backtest_data.get('annualized_return'),
                'sharpe_ratio': backtest_data.get('sharpe_ratio'),
                'max_drawdown': backtest_data.get('max_drawdown'),
                'win_rate': backtest_data.get('win_rate'),
                'profit_factor': backtest_data.get('profit_factor'),
                'calmar_ratio': backtest_data.get('calmar_ratio')
            },
            
            # Sinyal İstatistikleri
            'signal_stats': {
                'total_signals': backtest_data.get('total_signals'),
                'buy_signals': backtest_data.get('buy_signals'),
                'sell_signals': backtest_data.get('sell_signals'),
                'signal_accuracy': backtest_data.get('signal_accuracy'),
                'precision': backtest_data.get('precision'),
                'recall': backtest_data.get('recall')
            },
            
            'parameters': backtest_data.get('parameters', {}),
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'completed'  # running, completed, failed
        }
    
    def create_model_document(self, model_data: Dict) -> Dict:
        """AI model bilgileri için document yapısı"""
        return {
            'model_name': model_data.get('model_name'),
            'model_type': model_data.get('model_type'),  # lightgbm, lstm, timegpt, ensemble
            'version': model_data.get('version'),
            'status': model_data.get('status', 'active'),  # active, training, deprecated
            
            # Model Performansı
            'performance_metrics': {
                'accuracy': model_data.get('accuracy'),
                'precision': model_data.get('precision'),
                'recall': model_data.get('recall'),
                'f1_score': model_data.get('f1_score'),
                'auc': model_data.get('auc'),
                'rmse': model_data.get('rmse')
            },
            
            # Model Detayları
            'model_details': {
                'hyperparameters': model_data.get('hyperparameters', {}),
                'feature_importance': model_data.get('feature_importance', {}),
                'training_data_size': model_data.get('training_data_size'),
                'last_training': model_data.get('last_training')
            },
            
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
    
    # Collection oluşturma yardımcı fonksiyonları
    def create_collections(self):
        """Tüm collection'ları oluştur"""
        for collection_name in self.COLLECTIONS.values():
            try:
                # Collection referansı oluştur (otomatik oluşur)
                collection_ref = self.db.collection(collection_name)
                print(f"✅ Collection oluşturuldu: {collection_name}")
            except Exception as e:
                print(f"❌ Collection oluşturma hatası {collection_name}: {e}")
    
    def create_indexes(self):
        """Gerekli index'leri oluştur"""
        indexes = [
            # Prices collection
            ('market_prices', ['symbol', 'timestamp']),
            ('market_prices', ['timestamp', 'symbol']),
            
            # Signals collection  
            ('trading_signals', ['symbol', 'timestamp']),
            ('trading_signals', ['signal_type', 'timestamp']),
            ('trading_signals', ['confidence', 'timestamp']),
            
            # Portfolio collection
            ('user_portfolios', ['user_id', 'created_at']),
            ('user_portfolios', ['user_id', 'updated_at']),
            
            # News collection
            ('market_news', ['symbols', 'published_at']),
            ('market_news', ['sentiment_score', 'published_at']),
            
            # Sentiment collection
            ('sentiment_scores', ['symbol', 'timestamp']),
            ('sentiment_scores', ['sentiment_score', 'timestamp'])
        ]
        
        print("📊 Index'ler oluşturuluyor...")
        # Not: Firestore'da index'ler otomatik oluşur, bu sadece referans

# Test fonksiyonu
def test_schema():
    """Firestore schema test"""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Firebase bağlantısı (test için)
        if not firebase_admin._apps:
            cred = credentials.Certificate('bist-backend-key.json')
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        schema = FirestoreSchema(db)
        
        # Test document'ları oluştur
        test_price = schema.create_price_document("SISE.IS", {
            'price': 45.50,
            'volume': 1000000,
            'timestamp': '2024-01-15T10:30:00',
            'source': 'finnhub_ws'
        })
        
        test_signal = schema.create_signal_document({
            'symbol': 'SISE.IS',
            'signal_type': 'BUY',
            'confidence': 85,
            'technical_score': 0.8,
            'fundamental_score': 0.7,
            'sentiment_score': 0.6
        })
        
        print("✅ Schema test başarılı!")
        print(f"Price document: {json.dumps(test_price, indent=2, default=str)}")
        print(f"Signal document: {json.dumps(test_signal, indent=2, default=str)}")
        
    except Exception as e:
        print(f"❌ Schema test hatası: {e}")

if __name__ == "__main__":
    test_schema()
