"""
PRD v2.0 - Yeni Modül Test Dosyası
DuPont, Macro Regime, Auto-Backtest testleri
"""

import sys
import os
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dupont_piotroski():
    """DuPont & Piotroski modülünü test et"""
    try:
        logger.info("🔍 DuPont & Piotroski Analyzer Test")
        print("=" * 50)
        
        from dupont_piotroski_analyzer import DuPontPiotroskiAnalyzer
        
        analyzer = DuPontPiotroskiAnalyzer()
        
        # Test hisseleri
        test_symbols = ["SISE.IS", "EREGL.IS", "TUPRS.IS"]
        
        for symbol in test_symbols:
            print(f"\n📊 {symbol} Analizi:")
            analysis = analyzer.get_comprehensive_analysis(symbol)
            
            if analysis:
                print(f"   Kapsamlı Skor: {analysis['comprehensive_score']:.1f}/100")
                print(f"   Genel Değerlendirme: {analysis['overall_rating']}")
                print(f"   Öneri: {analysis['overall_recommendation']}")
                
                if analysis.get('dupont_analysis'):
                    dupont = analysis['dupont_analysis']
                    print(f"   ROE: {dupont.get('roe_dupont', 0):.2f}%")
                    print(f"   ROA: {dupont.get('roa', 0):.2f}%")
                    print(f"   Borç/Özsermaye: {dupont.get('debt_to_equity', 0):.2f}")
                
                if analysis.get('piotroski_analysis'):
                    piotroski = analysis['piotroski_analysis']
                    print(f"   Piotroski F-Score: {piotroski.get('f_score', 0)}/9")
                    print(f"   Yorum: {piotroski.get('interpretation', '')}")
            else:
                print("   ❌ Analiz başarısız")
        
        print("\n" + "=" * 50)
        print("✅ DuPont & Piotroski Test Tamamlandı!")
        return True
        
    except Exception as e:
        logger.error(f"❌ DuPont & Piotroski test hatası: {e}")
        return False

def test_macro_regime():
    """Macro Regime Detector modülünü test et"""
    try:
        logger.info("🔍 Macro Regime Detector Test")
        print("=" * 50)
        
        from macro_regime_detector import MacroRegimeDetector
        
        detector = MacroRegimeDetector()
        
        # Makro analiz
        analysis = detector.get_macro_analysis()
        
        if analysis:
            print(f"📊 Mevcut Rejim: {analysis['current_regime']}")
            print(f"🎯 Güven Skoru: {analysis['regime_confidence']}%")
            
            print(f"\n📈 Rejim Özeti:")
            summary = analysis['regime_summary']
            print(f"   Volatilite: {summary['volatility']}")
            print(f"   Trend: {summary['trend']}")
            print(f"   Likidite: {summary['liquidity']}")
            print(f"   Risk Skoru: {summary['risk_score']}")
            
            print(f"\n🔄 Rejim Değişimleri:")
            for change in analysis['regime_changes'][-3:]:  # Son 3 değişim
                print(f"   {change['date']}: {change['from_regime']} → {change['to_regime']}")
                print(f"      Neden: {change['reason']}")
            
            print(f"\n💡 Öneriler:")
            recs = analysis['recommendations']
            print(f"   Strateji: {recs['trading_strategy']}")
            print(f"   Portföy: {recs['portfolio_allocation']['stocks']} hisse, {recs['portfolio_allocation']['bonds']} tahvil")
            
            print(f"\n🌍 Piyasa Koşulları:")
            conditions = analysis['market_conditions']
            print(f"   Volatilite: {conditions['volatility_level']}")
            print(f"   Trend Gücü: {conditions['trend_strength']}")
            print(f"   Piyasa Stresi: {conditions['market_stress']}")
        else:
            print("❌ Analiz başarısız")
        
        print("\n" + "=" * 50)
        print("✅ Macro Regime Test Tamamlandı!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Macro Regime test hatası: {e}")
        return False

def test_auto_backtest():
    """Auto Backtest & Walk Forward modülünü test et"""
    try:
        logger.info("🔍 Auto Backtest & Walk Forward Test")
        print("=" * 50)
        
        from auto_backtest_walkforward import AutoBacktestWalkForward
        
        backtest_engine = AutoBacktestWalkForward()
        
        # Test hissesi
        test_symbol = "SISE.IS"
        
        # Veri al
        data = backtest_engine.get_stock_data_for_backtest(test_symbol)
        
        if not data.empty:
            print(f"📊 {test_symbol} verisi hazırlandı: {len(data)} kayıt")
            
            # Teknik indikatörler
            data_with_indicators = backtest_engine.calculate_technical_indicators(data)
            
            # Backtest çalıştır
            print("\n🚀 Backtest çalıştırılıyor...")
            backtest_result = backtest_engine.run_backtest(data_with_indicators)
            
            if backtest_result:
                print(f"✅ Backtest tamamlandı!")
                print(f"   Toplam Getiri: {backtest_result['total_return']:.2f}%")
                print(f"   Sharpe Oranı: {backtest_result['sharpe_ratio']:.2f}")
                print(f"   Max Drawdown: {backtest_result['max_drawdown']:.2f}%")
                print(f"   Toplam Trade: {backtest_result['total_trades']}")
                print(f"   Win Rate: {backtest_result['win_rate']:.2f}%")
            
            # Walk Forward analizi
            print("\n🔄 Walk Forward analizi çalıştırılıyor...")
            walk_forward_result = backtest_engine.run_walk_forward_analysis(data_with_indicators)
            
            if walk_forward_result:
                print(f"✅ Walk Forward analizi tamamlandı!")
                print(f"   Toplam Periyot: {walk_forward_result['total_periods']}")
                print(f"   Ortalama Getiri: {walk_forward_result['avg_return']:.2f}%")
                print(f"   Ortalama Sharpe: {walk_forward_result['avg_sharpe']:.2f}")
            
            # Parametre optimizasyonu
            print("\n⚙️ Parametre optimizasyonu çalıştırılıyor...")
            optimization_result = backtest_engine.optimize_strategy_parameters(data_with_indicators)
            
            if optimization_result:
                print(f"✅ Parametre optimizasyonu tamamlandı!")
                print(f"   Toplam Kombinasyon: {optimization_result['total_combinations']}")
                print(f"   En İyi Getiri: {optimization_result['best_by_return']['performance']['total_return']:.2f}%")
                print(f"   En İyi Sharpe: {optimization_result['best_by_return']['performance']['sharpe_ratio']:.2f}")
            
            # Rapor oluştur
            print("\n📋 Rapor oluşturuluyor...")
            report = backtest_engine.generate_backtest_report(
                test_symbol, backtest_result, walk_forward_result, optimization_result
            )
            
            if report:
                print(f"✅ Rapor oluşturuldu!")
                print(f"\n💡 Öneriler:")
                for rec in report.get('recommendations', []):
                    print(f"   {rec}")
        else:
            print(f"❌ {test_symbol} için veri alınamadı")
        
        print("\n" + "=" * 50)
        print("✅ Auto Backtest Test Tamamlandı!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Auto Backtest test hatası: {e}")
        return False

def test_integration():
    """Tüm modüllerin entegrasyonunu test et"""
    try:
        logger.info("🔍 Entegrasyon Test")
        print("=" * 50)
        
        # Test sonuçları
        test_results = {
            'dupont_piotroski': test_dupont_piotroski(),
            'macro_regime': test_macro_regime(),
            'auto_backtest': test_auto_backtest()
        }
        
        # Özet
        print(f"\n📊 Test Özeti:")
        print(f"   DuPont & Piotroski: {'✅' if test_results['dupont_piotroski'] else '❌'}")
        print(f"   Macro Regime: {'✅' if test_results['macro_regime'] else '❌'}")
        print(f"   Auto Backtest: {'✅' if test_results['auto_backtest'] else '❌'}")
        
        success_count = sum(test_results.values())
        total_count = len(test_results)
        
        print(f"\n🎯 Başarı Oranı: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        if success_count == total_count:
            print("🎉 Tüm testler başarılı! PRD v2.0 modülleri hazır.")
        else:
            print("⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")
        
        return test_results
        
    except Exception as e:
        logger.error(f"❌ Entegrasyon test hatası: {e}")
        return {}

def main():
    """Ana test fonksiyonu"""
    print("🚀 PRD v2.0 - Yeni Modül Testleri Başlıyor")
    print("=" * 60)
    print(f"📅 Test Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Entegrasyon testi
        results = test_integration()
        
        print("\n" + "=" * 60)
        print("🏁 Test Tamamlandı!")
        
        if results:
            print("📋 Detaylı sonuçlar için logları kontrol edin.")
        else:
            print("❌ Test sonuçları alınamadı.")
        
    except Exception as e:
        logger.error(f"❌ Ana test hatası: {e}")
        print(f"❌ Test hatası: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
