#!/usr/bin/env python3
"""Ultra basit test scripti - sadece temel işlemler"""

print("🚀 Ultra Basit Test Başlatılıyor...")

try:
    print("1️⃣ Import testleri...")
    import pandas as pd
    print("   ✅ pandas OK")
    
    import numpy as np
    print("   ✅ numpy OK")
    
    print("2️⃣ Basit hesaplama...")
    a = 10
    b = 20
    c = a + b
    print(f"   ✅ {a} + {b} = {c}")
    
    print("3️⃣ Basit DataFrame...")
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    print(f"   ✅ DataFrame oluşturuldu: {df.shape}")
    
    print("4️⃣ Basit numpy işlem...")
    arr = np.array([1, 2, 3, 4, 5])
    mean_val = np.mean(arr)
    print(f"   ✅ Array mean: {mean_val}")
    
    print("\n🎉 TÜM TESTLER BAŞARILI!")
    print("✅ Sistem çalışıyor!")
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    print("❌ Sistem çalışmıyor!")
    import traceback
    traceback.print_exc()
