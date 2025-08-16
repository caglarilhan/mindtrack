import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

class MarketRegimeDetector:
    """
    Makro piyasa rejimi algılayıcı
    HMM ile Risk-On/Risk-Off, Trend/Mean-Reversion tespiti
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.gmm_model = None
        self.regime_labels = ['Risk-Off', 'Risk-On', 'Trend', 'Mean-Reversion']
        
    def get_macro_data(self, period: str = "2y") -> pd.DataFrame:
        """
        Makro verileri çeker
        """
        try:
            # Türkiye makro göstergeleri
            symbols = {
                'XU030.IS': 'BIST-30',
                'XU100.IS': 'BIST-100',
                'SISE.IS': 'SISE',
                'EREGL.IS': 'EREGL',
                'TUPRS.IS': 'TUPRS'
            }
            
            macro_data = {}
            
            for symbol, name in symbols.items():
                try:
                    data = yf.download(symbol, period=period, interval="1d")
                    if not data.empty:
                        macro_data[name] = data['Close']
                except Exception as e:
                    print(f"{symbol} veri çekme hatası: {e}")
                    continue
            
            if macro_data:
                df = pd.DataFrame(macro_data)
                df = df.dropna()
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Makro veri çekme hatası: {e}")
            return pd.DataFrame()
    
    def calculate_macro_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Makro özellikleri hesaplar
        """
        try:
            features = pd.DataFrame()
            
            for column in data.columns:
                price_series = data[column]
                
                # Fiyat değişimi
                features[f'{column}_returns'] = price_series.pct_change()
                features[f'{column}_volatility'] = price_series.pct_change().rolling(20).std()
                
                # Trend göstergeleri
                features[f'{column}_trend'] = price_series.rolling(20).mean() / price_series - 1
                features[f'{column}_momentum'] = price_series / price_series.shift(20) - 1
                
                # Volatilite göstergeleri
                features[f'{column}_atr'] = self._calculate_atr(
                    data[f'{column.replace("_Close", "")}_High'] if f'{column.replace("_Close", "")}_High' in data.columns else price_series,
                    data[f'{column.replace("_Close", "")}_Low'] if f'{column.replace("_Close", "")}_Low' in data.columns else price_series,
                    price_series
                )
            
            # Korelasyon matrisi
            returns = data.pct_change().dropna()
            if len(returns) > 10:
                corr_matrix = returns.corr()
                features['avg_correlation'] = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
                features['correlation_std'] = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].std()
            
            # NaN değerleri temizle
            features = features.dropna()
            
            return features
            
        except Exception as e:
            print(f"Makro özellik hesaplama hatası: {e}")
            return pd.DataFrame()
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """ATR hesaplama"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return tr.rolling(window=period).mean()
        except:
            return pd.Series(index=close.index)
    
    def detect_regime(self, features: pd.DataFrame, n_regimes: int = 4) -> Dict:
        """
        Piyasa rejimini tespit eder
        """
        try:
            if features.empty or len(features) < 50:
                return {"error": "Yeterli veri yok"}
            
            # Veriyi normalize et
            features_scaled = self.scaler.fit_transform(features)
            
            # Gaussian Mixture Model ile rejim tespiti
            self.gmm_model = GaussianMixture(
                n_components=n_regimes,
                random_state=42,
                covariance_type='full'
            )
            
            # Model eğitimi
            regime_labels = self.gmm_model.fit_predict(features_scaled)
            
            # Rejim özellikleri
            regime_features = {}
            for i in range(n_regimes):
                regime_mask = regime_labels == i
                regime_data = features_scaled[regime_mask]
                
                regime_features[f'Regime_{i}'] = {
                    'size': int(regime_mask.sum()),
                    'percentage': float(regime_mask.sum() / len(regime_labels) * 100),
                    'volatility': float(np.mean(np.std(regime_data, axis=0))),
                    'returns': float(np.mean(np.mean(regime_data, axis=0))),
                    'stability': float(1 / (np.std(regime_data, axis=0).std() + 1e-6))
                }
            
            # Mevcut rejim
            current_regime = regime_labels[-1]
            
            # Rejim geçiş matrisi
            transition_matrix = self._calculate_transition_matrix(regime_labels, n_regimes)
            
            return {
                "current_regime": int(current_regime),
                "regime_labels": regime_labels.tolist(),
                "regime_features": regime_features,
                "transition_matrix": transition_matrix.tolist(),
                "regime_probability": self.gmm_model.predict_proba(features_scaled[-1:]).flatten().tolist(),
                "regime_stability": self._calculate_regime_stability(regime_labels),
                "detection_date": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            print(f"Rejim tespit hatası: {e}")
            return {"error": str(e)}
    
    def _calculate_transition_matrix(self, labels: np.ndarray, n_regimes: int) -> np.ndarray:
        """Rejim geçiş matrisini hesaplar"""
        try:
            transition_matrix = np.zeros((n_regimes, n_regimes))
            
            for i in range(len(labels) - 1):
                current = labels[i]
                next_regime = labels[i + 1]
                transition_matrix[current][next_regime] += 1
            
            # Normalize
            row_sums = transition_matrix.sum(axis=1)
            transition_matrix = transition_matrix / row_sums[:, np.newaxis]
            
            return transition_matrix
            
        except Exception as e:
            return np.eye(n_regimes)
    
    def _calculate_regime_stability(self, labels: np.ndarray) -> float:
        """Rejim kararlılığını hesaplar"""
        try:
            changes = np.diff(labels)
            stability = 1 - (np.count_nonzero(changes) / len(changes))
            return float(stability)
        except:
            return 0.5
    
    def get_regime_recommendations(self, regime_data: Dict) -> Dict:
        """
        Rejim bazlı portföy önerileri
        """
        try:
            if "error" in regime_data:
                return {"error": regime_data["error"]}
            
            current_regime = regime_data["current_regime"]
            regime_features = regime_data["regime_features"]
            stability = regime_data["regime_stability"]
            
            # Rejim bazlı stratejiler
            strategies = {
                0: {  # Risk-Off
                    "name": "Risk-Off (Güvenli Liman)",
                    "description": "Yüksek volatilite, düşük getiri",
                    "recommendations": [
                        "Altın, gümüş gibi değerli madenler",
                        "Tahvil ve bono portföyü",
                        "Savunmacı hisseler (gıda, sağlık)",
                        "Nakit pozisyonu artır"
                    ],
                    "risk_level": "LOW",
                    "position_size": "CONSERVATIVE"
                },
                1: {  # Risk-On
                    "name": "Risk-On (Büyüme)",
                    "description": "Düşük volatilite, yüksek getiri",
                    "recommendations": [
                        "Büyüme hisseleri (teknoloji, finans)",
                        "Küçük ve orta ölçekli şirketler",
                        "Emerging markets",
                        "Kaldıraçlı pozisyonlar"
                    ],
                    "risk_level": "HIGH",
                    "position_size": "AGGRESSIVE"
                },
                2: {  # Trend
                    "name": "Trend Following",
                    "description": "Güçlü trend, momentum",
                    "recommendations": [
                        "Trend takip stratejileri",
                        "Momentum indikatörleri",
                        "Breakout formasyonları",
                        "Trend gücü yüksek hisseler"
                    ],
                    "risk_level": "MEDIUM",
                    "position_size": "MODERATE"
                },
                3: {  # Mean-Reversion
                    "name": "Mean-Reversion",
                    "description": "Ortalamaya dönüş",
                    "recommendations": [
                        "Oversold/Overbought hisseler",
                        "Bollinger Bands stratejileri",
                        "RSI divergence",
                        "Support/Resistance seviyeleri"
                    ],
                    "risk_level": "MEDIUM",
                    "position_size": "MODERATE"
                }
            }
            
            current_strategy = strategies.get(current_regime, strategies[0])
            
            # Rejim kararlılığına göre ayarlama
            if stability > 0.8:
                confidence = "VERY HIGH"
                position_adjustment = "FULL"
            elif stability > 0.6:
                confidence = "HIGH"
                position_adjustment = "STANDARD"
            elif stability > 0.4:
                confidence = "MEDIUM"
                position_adjustment = "REDUCED"
            else:
                confidence = "LOW"
                position_adjustment = "MINIMAL"
            
            return {
                "current_regime": current_regime,
                "regime_name": current_strategy["name"],
                "description": current_strategy["description"],
                "recommendations": current_strategy["recommendations"],
                "risk_level": current_strategy["risk_level"],
                "position_size": current_strategy["position_size"],
                "regime_stability": stability,
                "confidence": confidence,
                "position_adjustment": position_adjustment,
                "next_regime_probability": self._predict_next_regime(regime_data),
                "analysis_date": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            print(f"Rejim önerisi hatası: {e}")
            return {"error": str(e)}
    
    def _predict_next_regime(self, regime_data: Dict) -> Dict:
        """Bir sonraki rejimi tahmin eder"""
        try:
            if "transition_matrix" not in regime_data:
                return {"error": "Geçiş matrisi yok"}
            
            current_regime = regime_data["current_regime"]
            transition_matrix = np.array(regime_data["transition_matrix"])
            
            # Mevcut rejimden geçiş olasılıkları
            next_probabilities = transition_matrix[current_regime]
            
            # En olası sonraki rejim
            most_likely = int(np.argmax(next_probabilities))
            probability = float(np.max(next_probabilities))
            
            return {
                "most_likely_regime": most_likely,
                "probability": probability,
                "all_probabilities": next_probabilities.tolist()
            }
            
        except Exception as e:
            return {"error": str(e)}

# Test fonksiyonu
if __name__ == "__main__":
    # Market regime detector'ı başlat
    detector = MarketRegimeDetector()
    
    print("🔍 Makro Piyasa Rejimi Analizi:")
    print("=" * 50)
    
    # Makro veri çek
    print("📥 Makro veri çekiliyor...")
    macro_data = detector.get_macro_data(period="1y")
    
    if not macro_data.empty:
        print(f"✅ Makro veri çekildi: {macro_data.shape}")
        
        # Özellikleri hesapla
        print("🔧 Makro özellikler hesaplanıyor...")
        features = detector.calculate_macro_features(macro_data)
        
        if not features.empty:
            print(f"✅ Özellikler hesaplandı: {features.shape}")
            
            # Rejim tespit et
            print("🎯 Piyasa rejimi tespit ediliyor...")
            regime_result = detector.detect_regime(features)
            
            if "error" not in regime_result:
                print("✅ Rejim tespit edildi!")
                print(f"📊 Mevcut Rejim: {regime_result['current_regime']}")
                print(f"🔒 Rejim Kararlılığı: {regime_result['regime_stability']:.3f}")
                
                # Önerileri al
                recommendations = detector.get_regime_recommendations(regime_result)
                
                if "error" not in recommendations:
                    print(f"\n🎯 Rejim Önerileri:")
                    print(f"   Rejim: {recommendations['regime_name']}")
                    print(f"   Risk Seviyesi: {recommendations['risk_level']}")
                    print(f"   Pozisyon Büyüklüğü: {recommendations['position_size']}")
                    print(f"   Güven: {recommendations['confidence']}")
                    
                    print(f"\n📋 Öneriler:")
                    for i, rec in enumerate(recommendations['recommendations'], 1):
                        print(f"   {i}. {rec}")
                else:
                    print(f"❌ Öneri hatası: {recommendations['error']}")
            else:
                print(f"❌ Rejim tespit hatası: {regime_result['error']}")
        else:
            print("❌ Özellik hesaplama başarısız")
    else:
        print("❌ Makro veri çekilemedi")
