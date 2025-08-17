# 📑 PRD v2.0 - Yeni Modüller Dokümantasyonu

## 🎯 Genel Bakış

Bu dokümantasyon, PRD v2.0'da eklenen yeni modüllerin kullanımını ve özelliklerini açıklar. Tüm modüller PRD v2.0 gereksinimlerine uygun olarak tasarlanmıştır.

## 🚀 Eklenen Yeni Modüller

### 1. 📊 DuPont & Piotroski F-Score Analyzer
**Dosya:** `dupont_piotroski_analyzer.py`

**Amaç:** ROE bileşen ayrıştırma + doğan skor hesaplama

**Özellikler:**
- DuPont analizi (ROE = Net Margin × Asset Turnover × Financial Leverage)
- Piotroski F-Score (9 kriterli finansal sağlık skoru)
- Kapsamlı finansal analiz ve öneriler
- Mock veri desteği (veri bulunamadığında)

**Kullanım:**
```python
from dupont_piotroski_analyzer import DuPontPiotroskiAnalyzer

analyzer = DuPontPiotroskiAnalyzer()
analysis = analyzer.get_comprehensive_analysis("SISE.IS")

print(f"Kapsamlı Skor: {analysis['comprehensive_score']}/100")
print(f"Genel Değerlendirme: {analysis['overall_rating']}")
print(f"Öneri: {analysis['overall_recommendation']}")
```

**API Endpoint:** `GET /dupont-piotroski/{symbol}`

---

### 2. 🌍 Macro Regime Detector
**Dosya:** `macro_regime_detector.py`

**Amaç:** Hidden Markov Model ile makro piyasa rejimi tespiti

**Özellikler:**
- Risk-On/Risk-Off/Neutral rejim tespiti
- Volatilite, trend ve likidite rejimi analizi
- USDTRY, XU030, VIX, TNX, Altın korelasyon analizi
- Rejim değişim tespiti ve neden analizi
- Portföy önerileri (rejime göre)

**Kullanım:**
```python
from macro_regime_detector import MacroRegimeDetector

detector = MacroRegimeDetector()
analysis = detector.get_macro_analysis()

print(f"Mevcut Rejim: {analysis['current_regime']}")
print(f"Güven Skoru: {analysis['regime_confidence']}%")
print(f"Portföy Önerisi: {analysis['recommendations']['portfolio_allocation']}")
```

**API Endpoint:** `GET /macro-regime?symbols=USDTRY=X,^XU030,^VIX`

---

### 3. 🔄 Auto-Backtest & Walk Forward Engine
**Dosya:** `auto_backtest_walkforward.py`

**Amaç:** Otomatik backtest ve walk forward analizi

**Özellikler:**
- Teknik indikatör hesaplama (EMA, RSI, MACD, Bollinger Bands)
- Trading sinyal üretimi
- Backtest çalıştırma ve performans metrikleri
- Walk Forward analizi (out-of-sample test)
- Parametre optimizasyonu (grid search)
- Kapsamlı raporlama

**Kullanım:**
```python
from auto_backtest_walkforward import AutoBacktestWalkForward

engine = AutoBacktestWalkForward()

# Veri al ve indikatörleri hesapla
data = engine.get_stock_data_for_backtest("SISE.IS")
data_with_indicators = engine.calculate_technical_indicators(data)

# Backtest çalıştır
backtest_result = engine.run_backtest(data_with_indicators)

# Walk Forward analizi
walk_forward_result = engine.run_walk_forward_analysis(data_with_indicators)

# Parametre optimizasyonu
optimization_result = engine.optimize_strategy_parameters(data_with_indicators)
```

**API Endpoint:** `POST /backtest` ve `GET /backtest/{symbol}`

---

## 🔧 Kurulum ve Gereksinimler

### Gerekli Python Paketleri
```bash
pip install -r requirements.txt
```

### Önemli Bağımlılıklar
- `yfinance` - Finansal veri
- `pandas` - Veri işleme
- `numpy` - Matematiksel işlemler
- `scikit-learn` - Makine öğrenmesi
- `matplotlib` - Görselleştirme

---

## 🧪 Test Etme

### Otomatik Test
```bash
cd backend
python test_prd_v2_modules.py
```

### Manuel Test
```bash
# DuPont & Piotroski
python dupont_piotroski_analyzer.py

# Macro Regime
python macro_regime_detector.py

# Auto Backtest
python auto_backtest_walkforward.py
```

---

## 📡 API Endpoint'leri

### Yeni Eklenen Endpoint'ler

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/dupont-piotroski/{symbol}` | GET | DuPont & Piotroski analizi |
| `/macro-regime` | GET | Makro piyasa rejimi analizi |
| `/backtest` | POST | Backtest ve walk forward analizi |
| `/backtest/{symbol}` | GET | Mevcut backtest raporu |

### Örnek API Kullanımı

#### DuPont & Piotroski Analizi
```bash
curl "http://localhost:8000/dupont-piotroski/SISE.IS"
```

#### Makro Rejim Analizi
```bash
curl "http://localhost:8000/macro-regime"
```

#### Backtest Çalıştırma
```bash
curl -X POST "http://localhost:8000/backtest" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "SISE.IS", "period": "2y", "initial_capital": 100000}'
```

---

## 🏗️ Mimari ve Entegrasyon

### Modül Bağımlılıkları
```
FastAPI Main App
├── DuPont & Piotroski Analyzer
├── Macro Regime Detector
├── Auto Backtest Engine
├── Grey TOPSIS Ranking
├── Technical Pattern Engine
├── AI Ensemble
├── RL Portfolio Agent
└── Sentiment XAI Engine
```

### Veri Akışı
1. **Veri Toplama:** yfinance, mock data
2. **Analiz:** DuPont, Piotroski, Macro Regime
3. **Backtest:** Teknik indikatörler, sinyaller
4. **Raporlama:** JSON format, API response

---

## 📊 Performans ve Ölçümler

### DuPont & Piotroski
- **Hedef:** Finansal sağlık skoru 0-100
- **Metrik:** ROE, ROA, Borç/Özsermaye, Current Ratio
- **Çıktı:** STRONG BUY, BUY, HOLD, SELL, STRONG SELL

### Macro Regime
- **Hedef:** Risk-On/Risk-Off tespiti
- **Metrik:** Volatilite, trend, likidite rejimi
- **Çıktı:** Portföy önerileri, risk yönetimi

### Auto Backtest
- **Hedef:** Strateji performans değerlendirmesi
- **Metrik:** Total Return, Sharpe Ratio, Max Drawdown
- **Çıktı:** Walk Forward analizi, parametre optimizasyonu

---

## 🚨 Hata Yönetimi

### Genel Hata Türleri
1. **Veri Hatası:** API rate limit, veri bulunamadı
2. **Hesaplama Hatası:** NaN değerler, sıfıra bölme
3. **Bağımlılık Hatası:** Modül import hatası

### Hata Çözümleri
- Mock veri kullanımı
- Try-catch blokları
- Graceful degradation
- Detaylı logging

---

## 🔮 Gelecek Geliştirmeler

### v2.1 Planlanan Özellikler
- [ ] FinBERT-TR entegrasyonu (Türkçe sentiment)
- [ ] Gerçek broker API entegrasyonu
- [ ] Advanced HMM modeli
- [ ] Real-time backtest dashboard

### v2.2 Planlanan Özellikler
- [ ] Multi-asset backtesting
- [ ] Machine learning tabanlı parametre optimizasyonu
- [ ] Cloud deployment (Railway, AWS)
- [ ] Mobile app entegrasyonu

---

## 📞 Destek ve İletişim

### Dokümantasyon
- [PRD v2.0 Ana Dokümanı](../README_PRD.md)
- [Production Guide](../README_PRODUCTION.md)

### Hata Raporlama
- GitHub Issues kullanın
- Detaylı hata logları ekleyin
- Test case'leri paylaşın

---

## 🎉 Sonuç

PRD v2.0'da eklenen bu modüller ile BIST AI Smart Trader:

✅ **DuPont & Piotroski** ile fundamental analiz gücü  
✅ **Macro Regime** ile piyasa rejimi tespiti  
✅ **Auto Backtest** ile strateji validasyonu  
✅ **Walk Forward** ile overfitting önleme  
✅ **Parametre Optimizasyonu** ile performans artırma  

Bu modüller sayesinde sistem hem temel analiz hem teknik analiz hem de makro piyasa analizi yapabilir hale gelmiştir.

---

*Son güncelleme: 2024-12-19*  
*Versiyon: 2.0.0*  
*Durum: Production Ready* 🚀
