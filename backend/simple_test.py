#!/usr/bin/env python3
"""Çok basit test scripti - sadece temel fonksiyonları test et"""

import sys
import traceback

def test_basic_imports():
    """Temel import'ları test et"""
    try:
        print("🔍 Import testleri...")
        
        import pandas as pd
        print("✅ pandas OK")
        
        import numpy as np
        print("✅ numpy OK")
        
        import yfinance as yf
        print("✅ yfinance OK")
        
        import ta
        print("✅ ta OK")
        
        from sklearn.linear_model import LogisticRegression
        print("✅ sklearn.linear_model OK")
        
        from sklearn.calibration import CalibratedClassifierCV
        print("✅ sklearn.calibration OK")
        
        print("🎉 Tüm import'lar başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Import hatası: {e}")
        traceback.print_exc()
        return False

def test_mock_data():
    """Mock veri oluşturmayı test et"""
    try:
        print("\n🔍 Mock veri testi...")
        
        import numpy as np
        import pandas as pd
        from datetime import datetime
        
        # Basit mock veri
        n_days = 100
        prices = [100.0]
        
        for i in range(n_days - 1):
            price = prices[-1] * (1 + np.random.normal(0, 0.02))
            prices.append(price)
        
        idx = pd.date_range(end=datetime.now().date(), periods=n_days, freq="B")
        df = pd.DataFrame({
            "Open": prices,
            "High": [p * 1.01 for p in prices],
            "Low": [p * 0.99 for p in prices],
            "Close": prices,
            "Volume": np.random.randint(1000000, 5000000, n_days)
        }, index=idx)
        
        print(f"✅ Mock veri oluşturuldu: {df.shape}")
        print(f"   İlk fiyat: {df['Close'].iloc[0]:.2f}")
        print(f"   Son fiyat: {df['Close'].iloc[-1]:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Mock veri hatası: {e}")
        traceback.print_exc()
        return False

def test_basic_features():
    """Temel feature engineering'i test et"""
    try:
        print("\n🔍 Feature engineering testi...")
        
        import numpy as np
        import pandas as pd
        import ta
        
        # Basit veri
        n_days = 100
        prices = [100.0]
        for i in range(n_days - 1):
            price = prices[-1] * (1 + np.random.normal(0, 0.02))
            prices.append(price)
        
        idx = pd.date_range(end=pd.Timestamp.now().date(), periods=n_days, freq="B")
        df = pd.DataFrame({
            "Open": prices,
            "High": [p * 1.01 for p in prices],
            "Low": [p * 0.99 for p in prices],
            "Close": prices,
            "Volume": np.random.randint(1000000, 5000000, n_days)
        }, index=idx)
        
        # Basit features
        c = df['Close'].astype(float)
        out = pd.DataFrame(index=df.index)
        
        out['ret_1'] = c.pct_change()
        out['ema20'] = ta.trend.ema_indicator(c, window=20)
        out['rsi14'] = ta.momentum.rsi(c, window=14)
        
        # Clean
        out = out.replace([np.inf, -np.inf], np.nan)
        out = out.dropna()
        
        print(f"✅ Feature engineering tamamlandı: {out.shape}")
        print(f"   Features: {list(out.columns)}")
        print(f"   Veri noktaları: {len(out)}")
        return True
        
    except Exception as e:
        print(f"❌ Feature engineering hatası: {e}")
        traceback.print_exc()
        return False

def test_simple_model():
    """Basit model eğitimini test et"""
    try:
        print("\n🔍 Basit model testi...")
        
        import numpy as np
        import pandas as pd
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score
        
        # Basit veri
        n_samples = 200
        X = np.random.randn(n_samples, 5)  # 5 features
        y = (np.random.rand(n_samples) > 0.5).astype(int)  # Binary labels
        
        # Model
        model = LogisticRegression(random_state=42, max_iter=100)
        model.fit(X, y)
        
        # Prediction
        y_pred = model.predict_proba(X)[:, 1]
        auc = roc_auc_score(y, y_pred)
        
        print(f"✅ Model eğitimi tamamlandı")
        print(f"   AUC: {auc:.3f}")
        print(f"   Coefficients: {model.coef_[0][:3]}...")
        return True
        
    except Exception as e:
        print(f"❌ Model hatası: {e}")
        traceback.print_exc()
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 Çok Basit Test Başlatılıyor...")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_mock_data,
        test_basic_features,
        test_simple_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test hatası: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Sonuçları: {passed}/{total} başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Sistem çalışıyor.")
    else:
        print("⚠️ Bazı testler başarısız. Detayları yukarıda.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
