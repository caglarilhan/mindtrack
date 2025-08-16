import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple, Optional
import yfinance as yf

from financial_ranking import FinancialRankingEngine
from pattern_detector import PatternDetector
from ai_ensemble import AIEnsemblePipeline
from early_warning_engine import EarlyWarningEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalEngine:
    """
    Ana Sinyal Motoru - Tüm modülleri birleştirir
    Finansal sıralama + Teknik formasyon + AI Ensemble
    """
    
    def __init__(self, api_key: str = None):
        self.financial_ranking = FinancialRankingEngine(api_key)
        self.pattern_detector = PatternDetector()
        self.ai_ensemble = AIEnsemblePipeline()
        self.early_warning = EarlyWarningEngine()
        
        # Sinyal geçmişi
        self.signal_history = []
        self.performance_metrics = {}
        
    def analyze_stock_comprehensive(self, symbol: str, period: str = "1y") -> Dict:
        """
        Kapsamlı hisse analizi - tüm modülleri kullanır
        """
        logger.info(f"🎯 {symbol} için kapsamlı analiz başlatılıyor...")
        
        try:
            # 1. Finansal Sıralama
            financial_rank = self.financial_ranking.rank_stocks([symbol])
            
            # 2. Teknik Formasyon Analizi
            pattern_analysis = self.pattern_detector.analyze_stock(symbol, period)
            
            # 3. AI Ensemble Tahmin
            ai_prediction = self._get_ai_prediction(symbol, period)
            
            # 4. Erken Uyarı Sinyalleri
            early_warning = self.early_warning.analyze_stock(symbol)
            
            # 5. Sinyal Skoru Hesapla
            signal_score = self._calculate_signal_score(
                financial_rank, pattern_analysis, ai_prediction, early_warning
            )
            
            # 6. Risk/Ödül Analizi
            risk_reward = self._analyze_risk_reward(pattern_analysis, ai_prediction)
            
            # 7. Final Sinyal Üret
            final_signal = self._generate_final_signal(signal_score, risk_reward)
            
            # Sonucu kaydet
            analysis_result = {
                "symbol": symbol,
                "analysis_date": datetime.now().isoformat(),
                "data_period": period,
                "financial_ranking": financial_rank,
                "pattern_analysis": pattern_analysis,
                "ai_prediction": ai_prediction,
                "early_warning": early_warning,
                "signal_score": signal_score,
                "risk_reward": risk_reward,
                "final_signal": final_signal,
                "confidence_level": self._calculate_confidence_level(
                    financial_rank, pattern_analysis, ai_prediction
                )
            }
            
            # Sinyal geçmişine ekle
            self.signal_history.append(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"{symbol} kapsamlı analiz hatası: {e}")
            return {"error": str(e)}
    
    def _get_ai_prediction(self, symbol: str, period: str) -> Dict:
        """
        AI Ensemble tahminini alır
        """
        try:
            # Veri çek
            data = yf.download(symbol, period=period, interval="1d")
            if data.empty:
                return {"error": "Veri bulunamadı"}
            
            # Target oluştur
            data['target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
            
            # Feature engineering
            data = self.ai_ensemble.prepare_features(data)
            
            if data.empty:
                return {"error": "Feature engineering başarısız"}
            
            # Modelleri eğit
            lgbm_result = self.ai_ensemble.train_lightgbm(data, data['target'])
            lstm_result = self.ai_ensemble.train_lstm(data, data['target'])
            
            # Ensemble tahmin
            if lgbm_result and 'error' not in lstm_result:
                prediction = self.ai_ensemble.predict_ensemble(data)
                return prediction
            else:
                return {"error": "Model eğitimi başarısız"}
                
        except Exception as e:
            logger.error(f"AI tahmin hatası: {e}")
            return {"error": str(e)}
    
    def _calculate_signal_score(self, financial_rank: Dict, pattern_analysis: Dict, 
                               ai_prediction: Dict, early_warning: Dict) -> Dict:
        """
        Çok kriterli sinyal skoru hesaplar
        """
        try:
            score = 0
            max_score = 100
            breakdown = {}
            
            # 1. Finansal Sıralama Skoru (0-30 puan)
            if "error" not in financial_rank:
                try:
                    if "ranked_stocks" in financial_rank and financial_rank["ranked_stocks"]:
                        stock_data = list(financial_rank["ranked_stocks"].values())[0]
                        if "TOPSIS_Score" in stock_data:
                            financial_score = min(30, stock_data["TOPSIS_Score"] * 30)
                            score += financial_score
                            breakdown["financial"] = financial_score
                        else:
                            breakdown["financial"] = 0
                    else:
                        breakdown["financial"] = 0
                except:
                    breakdown["financial"] = 0
            else:
                breakdown["financial"] = 0
            
            # 2. Teknik Formasyon Skoru (0-25 puan)
            if "error" not in pattern_analysis:
                try:
                    # EMA sinyalleri
                    ema_score = min(10, pattern_analysis.get("ema_signals", {}).get("total_signals", 0) * 2)
                    
                    # Candlestick formasyonları
                    candlestick_score = min(10, pattern_analysis.get("candlestick_patterns", {}).get("total_patterns", 0) * 2)
                    
                    # Support/Resistance
                    sr_score = min(5, pattern_analysis.get("support_resistance", {}).get("total_levels", 0))
                    
                    pattern_score = ema_score + candlestick_score + sr_score
                    score += pattern_score
                    breakdown["technical"] = pattern_score
                except:
                    breakdown["technical"] = 0
            else:
                breakdown["technical"] = 0
            
            # 3. AI Ensemble Skoru (0-25 puan)
            if "error" not in ai_prediction:
                try:
                    confidence = ai_prediction.get("ensemble", {}).get("confidence", 0)
                    ai_score = confidence * 25
                    score += ai_score
                    breakdown["ai"] = ai_score
                except:
                    breakdown["ai"] = 0
            else:
                breakdown["ai"] = 0
            
            # 4. Erken Uyarı Skoru (0-20 puan)
            if "error" not in early_warning:
                try:
                    # Risk ve fırsat sinyalleri
                    risk_signals = early_warning.get("risk_signals", [])
                    opportunity_signals = early_warning.get("opportunity_signals", [])
                    
                    warning_score = min(20, (len(risk_signals) + len(opportunity_signals)) * 2)
                    score += warning_score
                    breakdown["warning"] = warning_score
                except:
                    breakdown["warning"] = 0
            else:
                breakdown["warning"] = 0
            
            # Normalize skor (0-100)
            normalized_score = min(100, score)
            
            return {
                "total_score": normalized_score,
                "breakdown": breakdown,
                "grade": self._get_grade(normalized_score),
                "recommendation": self._get_recommendation(normalized_score)
            }
            
        except Exception as e:
            logger.error(f"Sinyal skor hesaplama hatası: {e}")
            return {"error": str(e)}
    
    def _get_grade(self, score: float) -> str:
        """Skor için harf notu"""
        if score >= 80:
            return "A+"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "B+"
        elif score >= 50:
            return "B"
        elif score >= 40:
            return "C+"
        elif score >= 30:
            return "C"
        else:
            return "D"
    
    def _get_recommendation(self, score: float) -> str:
        """Skor için öneri"""
        if score >= 80:
            return "STRONG BUY"
        elif score >= 70:
            return "BUY"
        elif score >= 60:
            return "BUY"
        elif score >= 50:
            return "HOLD"
        elif score >= 40:
            return "HOLD"
        elif score >= 30:
            return "SELL"
        else:
            return "STRONG SELL"
    
    def _analyze_risk_reward(self, pattern_analysis: Dict, ai_prediction: Dict) -> Dict:
        """
        Risk/Ödül analizi yapar
        """
        try:
            risk_reward = {}
            
            # Pattern analizinden risk/ödül
            if "error" not in pattern_analysis:
                risk_reward["technical"] = pattern_analysis.get("risk_reward_ratio", 1.0)
            else:
                risk_reward["technical"] = 1.0
            
            # AI tahmininden güven skoru
            if "error" not in ai_prediction:
                confidence = ai_prediction.get("ensemble", {}).get("confidence", 0.5)
                risk_reward["ai_confidence"] = confidence
            else:
                risk_reward["ai_confidence"] = 0.5
            
            # Genel risk/ödül skoru
            overall_rr = (risk_reward["technical"] + risk_reward["ai_confidence"]) / 2
            risk_reward["overall"] = overall_rr
            
            # Risk seviyesi
            if overall_rr >= 2.0:
                risk_level = "LOW"
            elif overall_rr >= 1.5:
                risk_level = "MEDIUM-LOW"
            elif overall_rr >= 1.0:
                risk_level = "MEDIUM"
            elif overall_rr >= 0.5:
                risk_level = "MEDIUM-HIGH"
            else:
                risk_level = "HIGH"
            
            risk_reward["risk_level"] = risk_level
            
            return risk_reward
            
        except Exception as e:
            logger.error(f"Risk/Ödül analiz hatası: {e}")
            return {"error": str(e)}
    
    def _generate_final_signal(self, signal_score: Dict, risk_reward: Dict) -> Dict:
        """
        Final sinyal üretir
        """
        try:
            score = signal_score.get("total_score", 0)
            recommendation = signal_score.get("recommendation", "HOLD")
            risk_level = risk_reward.get("risk_level", "MEDIUM")
            
            # Sinyal gücü
            if score >= 80:
                signal_strength = "VERY STRONG"
                action = "IMMEDIATE BUY"
            elif score >= 70:
                signal_strength = "STRONG"
                action = "BUY"
            elif score >= 60:
                signal_strength = "MODERATE"
                action = "BUY ON DIP"
            elif score >= 50:
                signal_strength = "WEAK"
                action = "WAIT"
            elif score >= 40:
                signal_strength = "WEAK"
                action = "WAIT"
            elif score >= 30:
                signal_strength = "MODERATE"
                action = "SELL"
            else:
                signal_strength = "STRONG"
                action = "IMMEDIATE SELL"
            
            # Stop Loss ve Take Profit önerileri
            sl_tp = self._calculate_sl_tp_recommendations(score, risk_level)
            
            return {
                "action": action,
                "strength": signal_strength,
                "recommendation": recommendation,
                "risk_level": risk_level,
                "stop_loss": sl_tp["stop_loss"],
                "take_profit": sl_tp["take_profit"],
                "position_size": sl_tp["position_size"],
                "time_horizon": sl_tp["time_horizon"]
            }
            
        except Exception as e:
            logger.error(f"Final sinyal üretme hatası: {e}")
            return {"error": str(e)}
    
    def _calculate_sl_tp_recommendations(self, score: float, risk_level: str) -> Dict:
        """
        Stop Loss ve Take Profit önerileri hesaplar
        """
        try:
            # Risk seviyesine göre SL/TP
            if risk_level == "LOW":
                sl_percentage = 0.05  # %5
                tp_percentage = 0.15  # %15
                position_size = "FULL"
            elif risk_level == "MEDIUM-LOW":
                sl_percentage = 0.07  # %7
                tp_percentage = 0.12  # %12
                position_size = "FULL"
            elif risk_level == "MEDIUM":
                sl_percentage = 0.10  # %10
                tp_percentage = 0.10  # %10
                position_size = "HALF"
            elif risk_level == "MEDIUM-HIGH":
                sl_percentage = 0.12  # %12
                tp_percentage = 0.08  # %8
                position_size = "QUARTER"
            else:  # HIGH
                sl_percentage = 0.15  # %15
                tp_percentage = 0.05  # %5
                position_size = "MINIMAL"
            
            # Skor bazlı ayarlamalar
            if score >= 80:
                sl_percentage *= 0.8  # Daha sıkı SL
                tp_percentage *= 1.2  # Daha yüksek TP
            elif score <= 30:
                sl_percentage *= 1.5  # Daha gevşek SL
                tp_percentage *= 0.8  # Daha düşük TP
            
            # Zaman ufku
            if score >= 70:
                time_horizon = "SHORT-TERM (1-5 days)"
            elif score >= 50:
                time_horizon = "MEDIUM-TERM (1-2 weeks)"
            else:
                time_horizon = "LONG-TERM (1+ months)"
            
            return {
                "stop_loss": f"{sl_percentage:.1%}",
                "take_profit": f"{tp_percentage:.1%}",
                "position_size": position_size,
                "time_horizon": time_horizon
            }
            
        except Exception as e:
            logger.error(f"SL/TP hesaplama hatası: {e}")
            return {
                "stop_loss": "10%",
                "take_profit": "10%",
                "position_size": "HALF",
                "time_horizon": "MEDIUM-TERM"
            }
    
    def _calculate_confidence_level(self, financial_rank: Dict, pattern_analysis: Dict, 
                                   ai_prediction: Dict) -> str:
        """
        Genel güven seviyesini hesaplar
        """
        try:
            confidence_scores = []
            
            # Finansal sıralama güveni
            if "error" not in financial_rank:
                confidence_scores.append(0.8)
            else:
                confidence_scores.append(0.3)
            
            # Teknik analiz güveni
            if "error" not in pattern_analysis:
                confidence_scores.append(0.7)
            else:
                confidence_scores.append(0.4)
            
            # AI tahmin güveni
            if "error" not in ai_prediction:
                confidence_scores.append(0.6)
            else:
                confidence_scores.append(0.3)
            
            # Ortalama güven
            avg_confidence = np.mean(confidence_scores)
            
            if avg_confidence >= 0.8:
                return "VERY HIGH"
            elif avg_confidence >= 0.6:
                return "HIGH"
            elif avg_confidence >= 0.4:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception as e:
            return "MEDIUM"
    
    def get_portfolio_recommendations(self, symbols: List[str], max_stocks: int = 10) -> Dict:
        """
        Portföy önerileri üretir
        """
        logger.info(f"Portföy önerileri üretiliyor: {len(symbols)} hisse...")
        
        try:
            portfolio_analysis = []
            
            for symbol in symbols:
                try:
                    # Kapsamlı analiz
                    analysis = self.analyze_stock_comprehensive(symbol)
                    
                    if "error" not in analysis:
                        portfolio_analysis.append({
                            "symbol": symbol,
                            "signal_score": analysis["signal_score"]["total_score"],
                            "recommendation": analysis["final_signal"]["action"],
                            "risk_level": analysis["final_signal"]["risk_level"],
                            "confidence": analysis["confidence_level"]
                        })
                        
                except Exception as e:
                    logger.warning(f"{symbol} analiz hatası: {e}")
                    continue
            
            # Skora göre sırala
            portfolio_analysis.sort(key=lambda x: x["signal_score"], reverse=True)
            
            # En iyi hisseleri seç
            top_stocks = portfolio_analysis[:max_stocks]
            
            # Portföy dağılımı
            portfolio_allocation = self._calculate_portfolio_allocation(top_stocks)
            
            return {
                "top_stocks": top_stocks,
                "portfolio_allocation": portfolio_allocation,
                "total_analysis": len(portfolio_analysis),
                "recommendation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Portföy önerisi hatası: {e}")
            return {"error": str(e)}
    
    def _calculate_portfolio_allocation(self, top_stocks: List[Dict]) -> Dict:
        """
        Portföy dağılımını hesaplar
        """
        try:
            total_score = sum(stock["signal_score"] for stock in top_stocks)
            
            allocation = {}
            for stock in top_stocks:
                # Skor bazlı ağırlık
                weight = stock["signal_score"] / total_score
                
                # Risk seviyesine göre ayarlama
                if stock["risk_level"] == "LOW":
                    risk_multiplier = 1.2
                elif stock["risk_level"] == "MEDIUM-LOW":
                    risk_multiplier = 1.0
                elif stock["risk_level"] == "MEDIUM":
                    risk_multiplier = 0.8
                elif stock["risk_level"] == "MEDIUM-HIGH":
                    risk_multiplier = 0.6
                else:  # HIGH
                    risk_multiplier = 0.4
                
                final_weight = weight * risk_multiplier
                allocation[stock["symbol"]] = {
                    "weight": round(final_weight * 100, 2),
                    "recommendation": stock["recommendation"],
                    "risk_level": stock["risk_level"]
                }
            
            # Normalize (toplam %100)
            total_weight = sum(item["weight"] for item in allocation.values())
            for symbol in allocation:
                allocation[symbol]["weight"] = round(
                    (allocation[symbol]["weight"] / total_weight) * 100, 2
                )
            
            return allocation
            
        except Exception as e:
            logger.error(f"Portföy dağılım hesaplama hatası: {e}")
            return {}

# Test fonksiyonu
if __name__ == "__main__":
    # Test hisseleri
    test_symbols = ["SISE.IS", "EREGL.IS", "TUPRS.IS"]
    
    # Signal engine'i başlat
    engine = SignalEngine()
    
    # Tek hisse analizi
    print("🎯 Tek Hisse Analizi:")
    print("=" * 50)
    
    result = engine.analyze_stock_comprehensive("SISE.IS")
    
    if "error" not in result:
        print(f"✅ {result['symbol']} Analizi Tamamlandı!")
        print(f"📊 Sinyal Skoru: {result['signal_score']['total_score']:.1f}/100 ({result['signal_score']['grade']})")
        print(f"🎯 Öneri: {result['final_signal']['action']}")
        print(f"⚖️ Risk Seviyesi: {result['final_signal']['risk_level']}")
        print(f"🔒 Stop Loss: {result['final_signal']['stop_loss']}")
        print(f"🎯 Take Profit: {result['final_signal']['take_profit']}")
        print(f"📈 Pozisyon Büyüklüğü: {result['final_signal']['position_size']}")
        print(f"⏰ Zaman Ufku: {result['final_signal']['time_horizon']}")
        print(f"🎯 Güven Seviyesi: {result['confidence_level']}")
    else:
        print(f"❌ Hata: {result['error']}")
    
    # Portföy önerileri
    print("\n📊 Portföy Önerileri:")
    print("=" * 50)
    
    portfolio = engine.get_portfolio_recommendations(test_symbols, max_stocks=3)
    
    if "error" not in portfolio:
        print(f"✅ Top {len(portfolio['top_stocks'])} Hisse:")
        for i, stock in enumerate(portfolio['top_stocks'], 1):
            print(f"   {i}. {stock['symbol']}: {stock['signal_score']:.1f} - {stock['recommendation']}")
        
        print(f"\n📈 Portföy Dağılımı:")
        for symbol, alloc in portfolio['portfolio_allocation'].items():
            print(f"   {symbol}: %{alloc['weight']} - {alloc['recommendation']}")
    else:
        print(f"❌ Portföy hatası: {portfolio['error']}")
