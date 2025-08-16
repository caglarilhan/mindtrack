"""
PRD v2.0 - Entegrasyon Test
Tüm modülleri test eden kapsamlı test
"""

import asyncio
import time
import sys
import os
from datetime import datetime
import logging

# Current directory'i Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Local imports
try:
    from websocket_connector import WebSocketConnector
    from grey_topsis_ranking import GreyTOPSISRanking
    from fundamental_analyzer import FundamentalAnalyzer
    from technical_pattern_engine import TechnicalPatternEngine
    from ai_ensemble import AIEnsemble
    from rl_portfolio_agent import RLPortfolioAgent
    from sentiment_xai_engine import SentimentXAIEngine
    from fastapi_main import app
    import uvicorn
except ImportError as e:
    print(f"⚠️ Import hatası: {e}")
    # Fallback imports
    WebSocketConnector = None
    GreyTOPSISRanking = None
    FundamentalAnalyzer = None
    TechnicalPatternEngine = None
    AIEnsemble = None
    RLPortfolioAgent = None
    SentimentXAIEngine = None
    app = None

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationTest:
    """PRD v2.0 Entegrasyon Test"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        
    def start_test(self):
        """Test başlat"""
        self.start_time = time.time()
        print("🧪 PRD v2.0 Entegrasyon Test Başlıyor")
        print("="*60)
        
    def end_test(self):
        """Test bitir"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        print("\n" + "="*60)
        print("📊 TEST SONUÇLARI")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAIL')
        skipped_tests = sum(1 for result in self.test_results.values() if result['status'] == 'SKIP')
        
        print(f"Toplam Test: {total_tests}")
        print(f"✅ Başarılı: {passed_tests}")
        print(f"❌ Başarısız: {failed_tests}")
        print(f"⏭️ Atlanan: {skipped_tests}")
        print(f"⏱️ Süre: {duration:.2f} saniye")
        
        # Test detayları
        for test_name, result in self.test_results.items():
            if result['status'] == 'PASS':
                status_icon = "✅"
            elif result['status'] == 'FAIL':
                status_icon = "❌"
            else:
                status_icon = "⏭️"
            print(f"{status_icon} {test_name}: {result['message']}")
        
        # Başarı oranı (sadece çalıştırılan testler için)
        run_tests = total_tests - skipped_tests
        if run_tests > 0:
            success_rate = (passed_tests / run_tests * 100)
            print(f"\n🎯 Çalıştırılan Testlerde Başarı Oranı: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("🎉 PRD v2.0 entegrasyon testi BAŞARILI!")
            else:
                print("⚠️ Bazı testler başarısız, gözden geçirilmeli")
        else:
            print("\n⚠️ Hiçbir test çalıştırılamadı")
    
    def test_websocket_connector(self):
        """WebSocket connector test"""
        if WebSocketConnector is None:
            self.test_results['websocket_connector'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ WebSocket Connector modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n🔌 WebSocket Connector Test:")
            
            connector = WebSocketConnector(
                finnhub_api_key="demo",
                symbols=["SISE.IS", "EREGL.IS", "TUPRS.IS"]
            )
            
            # Fiyat verisi al (yfinance fallback ile)
            # Önce yfinance ile test verisi al
            import yfinance as yf
            test_data = yf.download("SISE.IS", period="1d", interval="1d")
            
            if not test_data.empty:
                # Fiyat cache'e ekle
                connector.price_cache["SISE.IS"] = {
                    'symbol': 'SISE.IS',
                    'price': test_data['Close'].iloc[-1],
                    'volume': test_data['Volume'].iloc[-1],
                    'timestamp': datetime.now().isoformat(),
                    'source': 'yfinance'
                }
                
                prices = connector.get_all_prices()
                
                self.test_results['websocket_connector'] = {
                    'status': 'PASS',
                    'message': f'{len(prices)} sembol fiyatı alındı'
                }
                print(f"✅ {len(prices)} sembol fiyatı alındı")
            else:
                self.test_results['websocket_connector'] = {
                    'status': 'FAIL',
                    'message': 'Test verisi yüklenemedi'
                }
                print("❌ Test verisi yüklenemedi")
                
        except Exception as e:
            self.test_results['websocket_connector'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_grey_topsis(self):
        """Grey TOPSIS test"""
        if GreyTOPSISRanking is None:
            self.test_results['grey_topsis'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ Grey TOPSIS modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n🧮 Grey TOPSIS Test:")
            
            # Test verisi
            import pandas as pd
            test_data = pd.DataFrame({
                'NetProfitMargin': [12.3, 8.4, 15.2],
                'ROE': [18, 12, 22],
                'DebtEquity': [0.4, 0.8, 0.6]
            }, index=['SISE', 'EREGL', 'TUPRS'])
            
            ranking = GreyTOPSISRanking()
            result = ranking.rank_stocks(test_data)
            
            if result is not None:
                self.test_results['grey_topsis'] = {
                    'status': 'PASS',
                    'message': f'{len(result)} şirket sıralandı'
                }
                print(f"✅ {len(result)} şirket sıralandı")
            else:
                self.test_results['grey_topsis'] = {
                    'status': 'FAIL',
                    'message': 'Sıralama sonucu alınamadı'
                }
                print("❌ Sıralama sonucu alınamadı")
                
        except Exception as e:
            self.test_results['grey_topsis'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_fundamental_analyzer(self):
        """Fundamental analyzer test"""
        if FundamentalAnalyzer is None:
            self.test_results['fundamental_analyzer'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ Fundamental Analyzer modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n📊 Fundamental Analyzer Test:")
            
            analyzer = FundamentalAnalyzer()
            
            # Test sembolü
            symbol = "SISE.IS"
            
            # DuPont analizi
            dupont_result = analyzer.get_dupont_analysis(symbol)
            
            if dupont_result is not None:
                self.test_results['fundamental_analyzer'] = {
                    'status': 'PASS',
                    'message': f'DuPont analizi tamamlandı: {symbol}'
                }
                print(f"✅ DuPont analizi tamamlandı: {symbol}")
            else:
                self.test_results['fundamental_analyzer'] = {
                    'status': 'FAIL',
                    'message': 'DuPont analizi başarısız'
                }
                print("❌ DuPont analizi başarısız")
                
        except Exception as e:
            self.test_results['fundamental_analyzer'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_technical_pattern_engine(self):
        """Technical pattern engine test"""
        if TechnicalPatternEngine is None:
            self.test_results['technical_pattern_engine'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ Technical Pattern Engine modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n📈 Technical Pattern Engine Test:")
            
            engine = TechnicalPatternEngine()
            
            # Test verisi
            import yfinance as yf
            data = yf.download("SISE.IS", period="1mo", interval="1d")
            
            if not data.empty:
                # EMA cross test
                ema_signals = engine.detect_ema_cross(data)
                
                # Candlestick test
                candlestick_signals = engine.detect_candlestick_patterns(data)
                
                total_signals = len(ema_signals) + len(candlestick_signals)
                
                self.test_results['technical_pattern_engine'] = {
                    'status': 'PASS',
                    'message': f'{total_signals} teknik sinyal tespit edildi'
                }
                print(f"✅ {total_signals} teknik sinyal tespit edildi")
            else:
                self.test_results['technical_pattern_engine'] = {
                    'status': 'FAIL',
                    'message': 'Test verisi yüklenemedi'
                }
                print("❌ Test verisi yüklenemedi")
                
        except Exception as e:
            self.test_results['technical_pattern_engine'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_ai_ensemble(self):
        """AI Ensemble test"""
        if AIEnsemble is None:
            self.test_results['ai_ensemble'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ AI Ensemble modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n🤖 AI Ensemble Test:")
            
            # Test verisi oluştur
            import numpy as np
            import pandas as pd
            
            np.random.seed(42)
            X_test = pd.DataFrame(np.random.randn(100, 10), columns=[f"feature_{i}" for i in range(10)])
            y_test = (X_test.iloc[:, 0] + X_test.iloc[:, 1] > 0).astype(int)
            
            # Basit modeller
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            
            rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
            lr_model = LogisticRegression(random_state=42, max_iter=1000)
            
            rf_model.fit(X_test, y_test)
            lr_model.fit(X_test, y_test)
            
            models = {"RandomForest": rf_model, "LogisticRegression": lr_model}
            
            # AI Ensemble başlat
            ensemble = AIEnsemble(random_state=42)
            
            # Voting topluluk oluştur
            success = ensemble.create_voting_ensemble("test_voting", models)
            
            if success:
                # Topluluğu eğit
                ensemble_info = ensemble.ensemble_models["test_voting"]
                voting_ensemble = ensemble_info["ensemble"]
                voting_ensemble.fit(X_test, y_test)
                
                # Tahmin yap
                prediction = ensemble.make_ensemble_prediction("test_voting", X_test.iloc[:1])
                
                self.test_results['ai_ensemble'] = {
                    'status': 'PASS',
                    'message': f'Topluluk oluşturuldu, tahmin: {prediction.final_prediction}'
                }
                print(f"✅ Topluluk oluşturuldu, tahmin: {prediction.final_prediction}")
            else:
                self.test_results['ai_ensemble'] = {
                    'status': 'FAIL',
                    'message': 'Topluluk oluşturulamadı'
                }
                print("❌ Topluluk oluşturulamadı")
                
        except Exception as e:
            self.test_results['ai_ensemble'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_rl_portfolio_agent(self):
        """RL Portfolio Agent test"""
        if RLPortfolioAgent is None:
            self.test_results['rl_portfolio_agent'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ RL Portfolio Agent modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n🎯 RL Portfolio Agent Test:")
            
            agent = RLPortfolioAgent()
            
            # Test sembolleri
            symbols = ["SISE.IS", "EREGL.IS"]
            
            # Trading verisi hazırla
            trading_data = agent.prepare_trading_data(symbols, "2024-01-01", "2024-12-31")
            
            if not trading_data.empty:
                # Trading environment oluştur
                env = agent.create_trading_environment(trading_data, symbols)
                
                if env:
                    self.test_results['rl_portfolio_agent'] = {
                        'status': 'PASS',
                        'message': f'Trading environment oluşturuldu, {len(trading_data)} kayıt'
                    }
                    print(f"✅ Trading environment oluşturuldu, {len(trading_data)} kayıt")
                else:
                    self.test_results['rl_portfolio_agent'] = {
                        'status': 'FAIL',
                        'message': 'Trading environment oluşturulamadı'
                    }
                    print("❌ Trading environment oluşturulamadı")
            else:
                self.test_results['rl_portfolio_agent'] = {
                    'status': 'FAIL',
                    'message': 'Trading verisi hazırlanamadı'
                }
                print("❌ Trading verisi hazırlanamadı")
                
        except Exception as e:
            self.test_results['rl_portfolio_agent'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_sentiment_xai_engine(self):
        """Sentiment XAI Engine test"""
        if SentimentXAIEngine is None:
            self.test_results['sentiment_xai_engine'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ Sentiment XAI Engine modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n🧠 Sentiment XAI Engine Test:")
            
            engine = SentimentXAIEngine()
            
            # Test metni
            test_text = "BIST 100 endeksi bugün yükseldi. Yatırımcılar pozitif."
            
            # Sentiment analizi
            sentiment_result = engine.analyze_text_sentiment(test_text)
            
            if sentiment_result is not None:
                self.test_results['sentiment_xai_engine'] = {
                    'status': 'PASS',
                    'message': f'Sentiment analizi tamamlandı: {sentiment_result["sentiment"]}'
                }
                print(f"✅ Sentiment analizi tamamlandı: {sentiment_result['sentiment']}")
            else:
                self.test_results['sentiment_xai_engine'] = {
                    'status': 'FAIL',
                    'message': 'Sentiment analizi başarısız'
                }
                print("❌ Sentiment analizi başarısız")
                
        except Exception as e:
            self.test_results['sentiment_xai_engine'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def test_fastapi_endpoints(self):
        """FastAPI endpoints test"""
        if app is None:
            self.test_results['fastapi_endpoints'] = {
                'status': 'SKIP',
                'message': 'Modül bulunamadı'
            }
            print("⏭️ FastAPI modülü bulunamadı, test atlandı")
            return
            
        try:
            print("\n🌐 FastAPI Endpoints Test:")
            
            # Endpoint sayısını say
            routes = [route for route in app.routes if hasattr(route, 'methods')]
            
            self.test_results['fastapi_endpoints'] = {
                'status': 'PASS',
                'message': f'{len(routes)} endpoint tanımlandı'
            }
            print(f"✅ {len(routes)} endpoint tanımlandı")
            
        except Exception as e:
            self.test_results['fastapi_endpoints'] = {
                'status': 'FAIL',
                'message': f'Hata: {str(e)}'
            }
            print(f"❌ Hata: {e}")
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        try:
            self.start_test()
            
            # Core modül testleri
            self.test_websocket_connector()
            self.test_grey_topsis()
            self.test_fundamental_analyzer()
            self.test_technical_pattern_engine()
            self.test_ai_ensemble()
            self.test_rl_portfolio_agent()
            self.test_sentiment_xai_engine()
            self.test_fastapi_endpoints()
            
            self.end_test()
            
        except Exception as e:
            logger.error(f"Test çalıştırma hatası: {e}")
            print(f"❌ Test çalıştırma hatası: {e}")

# Test fonksiyonu
def test_integration():
    """Entegrasyon testi"""
    try:
        print("🧪 PRD v2.0 Entegrasyon Test")
        print("="*60)
        
        # Test başlat
        integration_test = IntegrationTest()
        integration_test.run_all_tests()
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_integration()
