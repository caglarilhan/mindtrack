#!/usr/bin/env python3
"""BIST AI Smart Trader - Çalışan Ana Uygulama"""

import json
import pandas as pd
import numpy as np
from datetime import datetime

class BISTSmartTrader:
    """BIST AI Smart Trader - Ana Sınıf"""
    
    def __init__(self):
        self.symbols = [
            'SISE.IS', 'TUPRS.IS', 'ASELS.IS', 'GARAN.IS', 'KCHOL.IS',
            'THYAO.IS', 'FROTO.IS', 'EKGYO.IS', 'ISCTR.IS', 'BIMAS.IS'
        ]
        self.results = {}
        
    def generate_mock_data(self):
        """Mock veri oluştur"""
        print("🔧 Mock veri oluşturuluyor...")
        
        for symbol in self.symbols:
            # Gerçekçi mock veri
            base_score = np.random.uniform(0.4, 0.9)
            
            # Trend faktörü
            trend_factor = np.random.choice([0.8, 1.0, 1.2], p=[0.3, 0.4, 0.3])
            
            # Volatilite faktörü
            vol_factor = np.random.uniform(0.9, 1.1)
            
            # Final skor
            final_score = min(0.95, base_score * trend_factor * vol_factor)
            
            # Aksiyon belirleme
            if final_score >= 0.75:
                action = "BUY"
                confidence = int(final_score * 100)
            elif final_score >= 0.60:
                action = "HOLD"
                confidence = int(final_score * 80)
            else:
                action = "SELL"
                confidence = int(final_score * 60)
            
            # Risk seviyesi
            risk_levels = ["DÜŞÜK", "ORTA", "YÜKSEK"]
            risk_weights = [0.4, 0.4, 0.2]
            risk_level = np.random.choice(risk_levels, p=risk_weights)
            
            self.results[symbol] = {
                "score": round(final_score, 3),
                "action": action,
                "confidence": confidence,
                "risk_level": risk_level,
                "trend": "YÜKSELIŞ" if final_score > 0.6 else "DÜŞÜŞ",
                "target_price": round(100 * (1 + final_score * 0.1), 2),
                "stop_loss": round(100 * (1 - final_score * 0.05), 2)
            }
        
        print(f"✅ {len(self.symbols)} sembol için mock veri oluşturuldu")
    
    def analyze_portfolio(self):
        """Portföy analizi yap"""
        print("\n📊 Portföy Analizi...")
        
        buy_signals = [s for s, r in self.results.items() if r['action'] == 'BUY']
        hold_signals = [s for s, r in self.results.items() if r['action'] == 'HOLD']
        sell_signals = [s for s, r in self.results.items() if r['action'] == 'SELL']
        
        print(f"🟢 BUY Sinyalleri ({len(buy_signals)}): {', '.join(buy_signals[:5])}")
        print(f"🟡 HOLD Sinyalleri ({len(hold_signals)}): {', '.join(hold_signals[:5])}")
        print(f"🔴 SELL Sinyalleri ({len(sell_signals)}): {', '.join(sell_signals[:5])}")
        
        # Top 5 BUY adayları
        buy_candidates = sorted(
            [(s, r) for s, r in self.results.items() if r['action'] == 'BUY'],
            key=lambda x: x[1]['score'],
            reverse=True
        )[:5]
        
        print(f"\n🏆 TOP 5 BUY ADAYLARI:")
        for i, (symbol, result) in enumerate(buy_candidates, 1):
            print(f"   {i}. {symbol}: {result['score']:.1%} (Güven: {result['confidence']}%)")
    
    def save_results(self):
        """Sonuçları JSON dosyasına kaydet"""
        print("\n💾 Sonuçlar kaydediliyor...")
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "total_symbols": len(self.symbols),
            "results": self.results,
            "summary": {
                "buy_signals": len([r for r in self.results.values() if r['action'] == 'BUY']),
                "hold_signals": len([r for r in self.results.values() if r['action'] == 'HOLD']),
                "sell_signals": len([r for r in self.results.values() if r['action'] == 'SELL']),
                "avg_score": round(np.mean([r['score'] for r in self.results.values()]), 3)
            }
        }
        
        # JSON dosyasına kaydet
        with open('bist_signals.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print("✅ Sonuçlar bist_signals.json dosyasına kaydedildi")
        return output
    
    def run_analysis(self):
        """Ana analiz fonksiyonu"""
        print("🚀 BIST AI Smart Trader - Analiz Başlatılıyor")
        print("=" * 60)
        
        # 1. Mock veri oluştur
        self.generate_mock_data()
        
        # 2. Portföy analizi
        self.analyze_portfolio()
        
        # 3. Sonuçları kaydet
        output = self.save_results()
        
        print("\n" + "=" * 60)
        print("🎉 ANALİZ TAMAMLANDI!")
        print(f"📊 Toplam Sembol: {output['summary']['total_symbols']}")
        print(f"🟢 BUY Sinyalleri: {output['summary']['buy_signals']}")
        print(f"🟡 HOLD Sinyalleri: {output['summary']['hold_signals']}")
        print(f"🔴 SELL Sinyalleri: {output['summary']['sell_signals']}")
        print(f"📈 Ortalama Skor: {output['summary']['avg_score']:.1%}")
        print("=" * 60)
        
        return output

def main():
    """Ana fonksiyon"""
    try:
        trader = BISTSmartTrader()
        results = trader.run_analysis()
        return results
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

if __name__ == "__main__":
    main()
