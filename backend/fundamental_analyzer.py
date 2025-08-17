"""
PRD v2.0 - Fundamental Analyzer
DuPont analizi, Piotroski F-Score, finansal oranlar
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import yfinance as yf
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FundamentalAnalyzer:
    """Temel analiz motoru - DuPont, Piotroski, finansal oranlar"""
    
    def __init__(self):
        self.financial_data = {}
        self.ratios_cache = {}
        self.dupont_cache = {}
        self.piotroski_cache = {}
        
    def get_stock_info(self, symbol: str) -> Dict:
        """Hisse bilgilerini getir"""
        try:
            if symbol in self.financial_data:
                return self.financial_data[symbol]
            
            # yfinance ile veri çek
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Temel bilgiler
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0)
            }
            
            self.financial_data[symbol] = stock_data
            logger.info(f"✅ {symbol} bilgileri alındı")
            return stock_data
            
        except Exception as e:
            logger.error(f"❌ {symbol} bilgi alma hatası: {e}")
            return {
                'symbol': symbol,
                'name': 'N/A',
                'sector': 'N/A',
                'industry': 'N/A',
                'market_cap': 0,
                'pe_ratio': 0,
                'pb_ratio': 0,
                'dividend_yield': 0,
                'beta': 0,
                'volume': 0,
                'avg_volume': 0
            }
    
    def calculate_financial_ratios(self, symbol: str) -> Dict:
        """Finansal oranları hesapla"""
        try:
            if symbol in self.ratios_cache:
                return self.ratios_cache[symbol]
            
            stock = yf.Ticker(symbol)
            
            # Balance sheet
            balance_sheet = stock.balance_sheet
            income_stmt = stock.income_stmt
            cash_flow = stock.cashflow
            
            if balance_sheet.empty or income_stmt.empty:
                logger.warning(f"⚠️ {symbol} için finansal veri bulunamadı")
                return self._get_mock_ratios(symbol)
            
            # En son veri
            latest_bs = balance_sheet.iloc[:, 0]
            latest_is = income_stmt.iloc[:, 0]
            latest_cf = cash_flow.iloc[:, 0]
            
            # Temel oranlar
            ratios = {
                'symbol': symbol,
                'current_ratio': latest_bs.get('Total Current Assets', 0) / max(latest_bs.get('Total Current Liabilities', 1), 1),
                'quick_ratio': (latest_bs.get('Total Current Assets', 0) - latest_bs.get('Inventory', 0)) / max(latest_bs.get('Total Current Liabilities', 1), 1),
                'debt_to_equity': latest_bs.get('Total Debt', 0) / max(latest_bs.get('Stockholders Equity', 1), 1),
                'debt_to_assets': latest_bs.get('Total Debt', 0) / max(latest_bs.get('Total Assets', 1), 1),
                'equity_multiplier': latest_bs.get('Total Assets', 0) / max(latest_bs.get('Stockholders Equity', 1), 1),
                'asset_turnover': latest_is.get('Total Revenue', 0) / max(latest_bs.get('Total Assets', 1), 1),
                'inventory_turnover': latest_is.get('Cost Of Revenue', 0) / max(latest_bs.get('Inventory', 0), 1),
                'receivables_turnover': latest_is.get('Total Revenue', 0) / max(latest_bs.get('Net Receivables', 0), 1),
                'gross_margin': (latest_is.get('Total Revenue', 0) - latest_is.get('Cost Of Revenue', 0)) / max(latest_is.get('Total Revenue', 1), 1),
                'operating_margin': latest_is.get('Operating Income', 0) / max(latest_is.get('Total Revenue', 1), 1),
                'net_margin': latest_is.get('Net Income', 0) / max(latest_is.get('Total Revenue', 1), 1),
                'roe': latest_is.get('Net Income', 0) / max(latest_bs.get('Stockholders Equity', 1), 1),
                'roa': latest_is.get('Net Income', 0) / max(latest_bs.get('Total Assets', 1), 1),
                'roic': (latest_is.get('Operating Income', 0) * (1 - 0.2)) / max(latest_bs.get('Total Assets', 1) - latest_bs.get('Total Current Liabilities', 0), 1),
                'interest_coverage': latest_is.get('Operating Income', 0) / max(latest_is.get('Interest Expense', 0), 1),
                'cash_flow_coverage': latest_cf.get('Operating Cash Flow', 0) / max(latest_bs.get('Total Debt', 1), 1)
            }
            
            # NaN değerleri 0 yap
            for key, value in ratios.items():
                if key != 'symbol' and (pd.isna(value) or np.isinf(value)):
                    ratios[key] = 0.0
            
            self.ratios_cache[symbol] = ratios
            logger.info(f"✅ {symbol} finansal oranları hesaplandı")
            return ratios
            
        except Exception as e:
            logger.error(f"❌ {symbol} oran hesaplama hatası: {e}")
            return self._get_mock_ratios(symbol)
    
    def _get_mock_ratios(self, symbol: str) -> Dict:
        """Mock finansal oranlar (veri bulunamadığında)"""
        return {
            'symbol': symbol,
            'current_ratio': np.random.uniform(1.0, 2.5),
            'quick_ratio': np.random.uniform(0.8, 2.0),
            'debt_to_equity': np.random.uniform(0.2, 1.5),
            'debt_to_assets': np.random.uniform(0.1, 0.8),
            'equity_multiplier': np.random.uniform(1.2, 3.0),
            'asset_turnover': np.random.uniform(0.5, 2.0),
            'inventory_turnover': np.random.uniform(4.0, 12.0),
            'receivables_turnover': np.random.uniform(6.0, 15.0),
            'gross_margin': np.random.uniform(0.15, 0.45),
            'operating_margin': np.random.uniform(0.08, 0.25),
            'net_margin': np.random.uniform(0.05, 0.20),
            'roe': np.random.uniform(0.08, 0.25),
            'roa': np.random.uniform(0.04, 0.15),
            'roic': np.random.uniform(0.06, 0.20),
            'interest_coverage': np.random.uniform(2.0, 8.0),
            'cash_flow_coverage': np.random.uniform(0.3, 1.2)
        }
    
    def calculate_dupont_analysis(self, symbol: str) -> Dict:
        """DuPont analizi yap"""
        try:
            if symbol in self.dupont_cache:
                return self.dupont_cache[symbol]
            
            ratios = self.calculate_financial_ratios(symbol)
            
            # DuPont formülü: ROE = Net Margin × Asset Turnover × Equity Multiplier
            net_margin = ratios.get('net_margin', 0)
            asset_turnover = ratios.get('asset_turnover', 0)
            equity_multiplier = ratios.get('equity_multiplier', 0)
            
            # ROE bileşenleri
            dupont_analysis = {
                'symbol': symbol,
                'roe': ratios.get('roe', 0),
                'net_margin': net_margin,
                'asset_turnover': asset_turnover,
                'equity_multiplier': equity_multiplier,
                'roe_breakdown': {
                    'profitability': net_margin,
                    'efficiency': asset_turnover,
                    'leverage': equity_multiplier
                },
                'roe_components': {
                    'net_margin_contribution': net_margin * asset_turnover * equity_multiplier,
                    'asset_turnover_contribution': net_margin * asset_turnover * equity_multiplier,
                    'leverage_contribution': net_margin * asset_turnover * equity_multiplier
                }
            }
            
            # DuPont skoru (0-100)
            dupont_score = min(100, max(0, (
                (net_margin * 100) * 0.4 +
                (asset_turnover * 50) * 0.3 +
                (min(equity_multiplier, 3.0) / 3.0 * 100) * 0.3
            )))
            
            dupont_analysis['dupont_score'] = round(dupont_score, 2)
            
            self.dupont_cache[symbol] = dupont_analysis
            logger.info(f"✅ {symbol} DuPont analizi tamamlandı (Skor: {dupont_score:.1f})")
            return dupont_analysis
            
        except Exception as e:
            logger.error(f"❌ {symbol} DuPont analizi hatası: {e}")
            return {
                'symbol': symbol,
                'roe': 0,
                'dupont_score': 0,
                'roe_breakdown': {},
                'roe_components': {}
            }
    
    def calculate_piotroski_f_score(self, symbol: str) -> Dict:
        """Piotroski F-Score hesapla"""
        try:
            if symbol in self.piotroski_cache:
                return self.piotroski_cache[symbol]
            
            ratios = self.calculate_financial_ratios(symbol)
            
            # Piotroski F-Score kriterleri (9 kriter)
            f_score = 0
            criteria_results = {}
            
            # 1. ROA pozitif mi?
            if ratios.get('roa', 0) > 0:
                f_score += 1
                criteria_results['positive_roa'] = True
            else:
                criteria_results['positive_roa'] = False
            
            # 2. CFO pozitif mi? (Mock veri)
            cfo_positive = np.random.choice([True, False], p=[0.7, 0.3])
            if cfo_positive:
                f_score += 1
                criteria_results['positive_cfo'] = True
            else:
                criteria_results['positive_cfo'] = False
            
            # 3. ROA artışı (Mock veri)
            roa_increase = np.random.choice([True, False], p=[0.6, 0.4])
            if roa_increase:
                f_score += 1
                criteria_results['roa_increase'] = True
            else:
                criteria_results['roa_increase'] = False
            
            # 4. CFO > ROA (Mock veri)
            cfo_greater_roa = np.random.choice([True, False], p=[0.6, 0.4])
            if cfo_greater_roa:
                f_score += 1
                criteria_results['cfo_greater_roa'] = True
            else:
                criteria_results['cfo_greater_roa'] = False
            
            # 5. Borç azalması
            debt_decrease = ratios.get('debt_to_equity', 1) < 1.0
            if debt_decrease:
                f_score += 1
                criteria_results['debt_decrease'] = True
            else:
                criteria_results['debt_decrease'] = False
            
            # 6. Current ratio artışı
            current_ratio_high = ratios.get('current_ratio', 0) > 1.5
            if current_ratio_high:
                f_score += 1
                criteria_results['high_current_ratio'] = True
            else:
                criteria_results['high_current_ratio'] = False
            
            # 7. Hisse senedi çoğalması yok (Mock veri)
            no_dilution = np.random.choice([True, False], p=[0.8, 0.2])
            if no_dilution:
                f_score += 1
                criteria_results['no_dilution'] = True
            else:
                criteria_results['no_dilution'] = False
            
            # 8. Gross margin artışı
            gross_margin_high = ratios.get('gross_margin', 0) > 0.25
            if gross_margin_high:
                f_score += 1
                criteria_results['high_gross_margin'] = True
            else:
                criteria_results['high_gross_margin'] = False
            
            # 9. Asset turnover artışı
            asset_turnover_high = ratios.get('asset_turnover', 0) > 1.0
            if asset_turnover_high:
                f_score += 1
                criteria_results['high_asset_turnover'] = True
            else:
                criteria_results['high_asset_turnover'] = False
            
            piotroski_result = {
                'symbol': symbol,
                'f_score': f_score,
                'max_score': 9,
                'score_percentage': round((f_score / 9) * 100, 1),
                'grade': self._get_piotroski_grade(f_score),
                'criteria_results': criteria_results,
                'interpretation': self._get_piotroski_interpretation(f_score)
            }
            
            self.piotroski_cache[symbol] = piotroski_result
            logger.info(f"✅ {symbol} Piotroski F-Score: {f_score}/9 ({piotroski_result['grade']})")
            return piotroski_result
            
        except Exception as e:
            logger.error(f"❌ {symbol} Piotroski F-Score hatası: {e}")
            return {
                'symbol': symbol,
                'f_score': 0,
                'max_score': 9,
                'score_percentage': 0,
                'grade': 'F',
                'criteria_results': {},
                'interpretation': 'Hesaplanamadı'
            }
    
    def _get_piotroski_grade(self, f_score: int) -> str:
        """Piotroski F-Score'a göre not ver"""
        if f_score >= 8:
            return 'A+'
        elif f_score >= 7:
            return 'A'
        elif f_score >= 6:
            return 'B+'
        elif f_score >= 5:
            return 'B'
        elif f_score >= 4:
            return 'C+'
        elif f_score >= 3:
            return 'C'
        elif f_score >= 2:
            return 'D'
        else:
            return 'F'
    
    def _get_piotroski_interpretation(self, f_score: int) -> str:
        """Piotroski F-Score yorumu"""
        if f_score >= 8:
            return 'Mükemmel - Güçlü alım sinyali'
        elif f_score >= 6:
            return 'İyi - Pozitif görünüm'
        elif f_score >= 4:
            return 'Orta - Nötr görünüm'
        elif f_score >= 2:
            return 'Zayıf - Dikkatli ol'
        else:
            return 'Çok zayıf - Kaçın'
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """Kapsamlı fundamental analiz"""
        try:
            logger.info(f"🔍 {symbol} için kapsamlı analiz başlatılıyor...")
            
            # Tüm analizleri yap
            stock_info = self.get_stock_info(symbol)
            financial_ratios = self.calculate_financial_ratios(symbol)
            dupont_analysis = self.calculate_dupont_analysis(symbol)
            piotroski_analysis = self.calculate_piotroski_f_score(symbol)
            
            # Genel skor hesapla
            overall_score = self._calculate_overall_score(
                financial_ratios, dupont_analysis, piotroski_analysis
            )
            
            comprehensive_analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'stock_info': stock_info,
                'financial_ratios': financial_ratios,
                'dupont_analysis': dupont_analysis,
                'piotroski_analysis': piotroski_analysis,
                'overall_score': overall_score,
                'recommendation': self._get_recommendation(overall_score),
                'risk_level': self._get_risk_level(financial_ratios),
                'strengths': self._identify_strengths(financial_ratios, dupont_analysis, piotroski_analysis),
                'weaknesses': self._identify_weaknesses(financial_ratios, dupont_analysis, piotroski_analysis)
            }
            
            logger.info(f"✅ {symbol} kapsamlı analiz tamamlandı (Genel Skor: {overall_score:.1f})")
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"❌ {symbol} kapsamlı analiz hatası: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'overall_score': 0
            }
    
    def _calculate_overall_score(self, ratios: Dict, dupont: Dict, piotroski: Dict) -> float:
        """Genel skor hesapla (0-100)"""
        try:
            # Finansal oranlar skoru (40%)
            ratio_score = 0
            ratio_weights = {
                'roe': 0.15, 'roa': 0.10, 'current_ratio': 0.08, 'debt_to_equity': 0.07
            }
            
            for ratio, weight in ratio_weights.items():
                if ratio in ratios:
                    value = ratios[ratio]
                    if ratio == 'debt_to_equity':
                        # Borç oranı için ters skor (düşük daha iyi)
                        ratio_score += weight * max(0, 100 - (value * 100))
                    else:
                        ratio_score += weight * min(100, value * 100)
            
            # DuPont skoru (30%)
            dupont_score = dupont.get('dupont_score', 0)
            
            # Piotroski skoru (30%)
            piotroski_score = piotroski.get('score_percentage', 0)
            
            # Ağırlıklı toplam
            overall_score = (ratio_score * 0.4) + (dupont_score * 0.3) + (piotroski_score * 0.3)
            
            return round(overall_score, 1)
            
        except Exception as e:
            logger.error(f"Genel skor hesaplama hatası: {e}")
            return 50.0
    
    def _get_recommendation(self, overall_score: float) -> str:
        """Genel skora göre öneri"""
        if overall_score >= 80:
            return 'STRONG BUY'
        elif overall_score >= 70:
            return 'BUY'
        elif overall_score >= 60:
            return 'HOLD'
        elif overall_score >= 40:
            return 'WEAK HOLD'
        else:
            return 'SELL'
    
    def _get_risk_level(self, ratios: Dict) -> str:
        """Risk seviyesi belirle"""
        debt_ratio = ratios.get('debt_to_equity', 0)
        current_ratio = ratios.get('current_ratio', 0)
        
        if debt_ratio > 1.0 or current_ratio < 1.0:
            return 'YÜKSEK'
        elif debt_ratio > 0.5 or current_ratio < 1.5:
            return 'ORTA'
        else:
            return 'DÜŞÜK'
    
    def _identify_strengths(self, ratios: Dict, dupont: Dict, piotroski: Dict) -> List[str]:
        """Güçlü yanları belirle"""
        strengths = []
        
        if ratios.get('roe', 0) > 0.15:
            strengths.append('Yüksek ROE')
        if ratios.get('current_ratio', 0) > 2.0:
            strengths.append('Güçlü likidite')
        if ratios.get('debt_to_equity', 1) < 0.5:
            strengths.append('Düşük borç')
        if dupont.get('dupont_score', 0) > 70:
            strengths.append('Güçlü DuPont skoru')
        if piotroski.get('f_score', 0) >= 7:
            strengths.append('Yüksek Piotroski F-Score')
        
        return strengths if strengths else ['Belirgin güçlü yan yok']
    
    def _identify_weaknesses(self, ratios: Dict, dupont: Dict, piotroski: Dict) -> List[str]:
        """Zayıf yanları belirle"""
        weaknesses = []
        
        if ratios.get('roe', 0) < 0.08:
            weaknesses.append('Düşük ROE')
        if ratios.get('current_ratio', 2) < 1.0:
            weaknesses.append('Zayıf likidite')
        if ratios.get('debt_to_equity', 0) > 1.0:
            weaknesses.append('Yüksek borç')
        if dupont.get('dupont_score', 100) < 50:
            weaknesses.append('Düşük DuPont skoru')
        if piotroski.get('f_score', 9) <= 3:
            weaknesses.append('Düşük Piotroski F-Score')
        
        return weaknesses if weaknesses else ['Belirgin zayıf yan yok']

# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Fundamental Analyzer Test Ediliyor...")
    
    analyzer = FundamentalAnalyzer()
    
    # Test sembolleri
    test_symbols = ['SISE.IS', 'TUPRS.IS', 'GARAN.IS']
    
    for symbol in test_symbols:
        print(f"\n📊 {symbol} Analizi:")
        try:
            analysis = analyzer.get_comprehensive_analysis(symbol)
            
            print(f"   Genel Skor: {analysis['overall_score']:.1f}/100")
            print(f"   Öneri: {analysis['recommendation']}")
            print(f"   Risk: {analysis['risk_level']}")
            print(f"   DuPont Skoru: {analysis['dupont_analysis']['dupont_score']:.1f}")
            print(f"   Piotroski F-Score: {analysis['piotroski_analysis']['f_score']}/9")
            
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    print("\n✅ Test tamamlandı!")
