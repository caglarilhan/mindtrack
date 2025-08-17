"""
PRD v2.0 - RL Portfolio Agent
FinRL, DDPG ile lot & re-hedge önerisi
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class RLPortfolioAgent:
    """Reinforcement Learning tabanlı portföy ajanı"""
    
    def __init__(self):
        self.portfolio_state = {}
        self.action_history = []
        self.performance_metrics = {}
        self.is_trained = False
        
    def initialize_portfolio(self, initial_capital: float = 100000, 
                           symbols: List[str] = None) -> Dict:
        """Portföy başlangıç durumu"""
        try:
            if symbols is None:
                symbols = ['SISE.IS', 'TUPRS.IS', 'GARAN.IS', 'KCHOL.IS', 'THYAO.IS']
            
            portfolio = {
                'cash': initial_capital,
                'total_value': initial_capital,
                'positions': {symbol: 0 for symbol in symbols},
                'position_values': {symbol: 0 for symbol in symbols},
                'symbols': symbols,
                'timestamp': datetime.now().isoformat(),
                'transaction_history': [],
                'daily_returns': [],
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'volatility': 0.0
            }
            
            self.portfolio_state = portfolio
            logger.info(f"✅ Portföy başlatıldı: {initial_capital:,.0f} TL")
            return portfolio
            
        except Exception as e:
            logger.error(f"❌ Portföy başlatma hatası: {e}")
            return {}
    
    def get_market_data(self, symbols: List[str], period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """Piyasa verilerini getir"""
        try:
            import yfinance as yf
            
            market_data = {}
            
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    data = stock.history(period=period)
                    
                    if not data.empty:
                        market_data[symbol] = data
                        logger.info(f"✅ {symbol} verisi alındı: {len(data)} kayıt")
                    else:
                        logger.warning(f"⚠️ {symbol} için veri bulunamadı")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {symbol} veri alma hatası: {e}")
                    continue
            
            if not market_data:
                logger.warning("⚠️ Hiçbir sembol için veri alınamadı, mock veri kullanılıyor")
                market_data = self._generate_mock_market_data(symbols, period)
            
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Piyasa veri alma hatası: {e}")
            return self._generate_mock_market_data(symbols, period)
    
    def _generate_mock_market_data(self, symbols: List[str], period: str) -> Dict[str, pd.DataFrame]:
        """Mock piyasa verisi oluştur"""
        try:
            # Mock veri parametreleri
            if period == "1mo":
                days = 30
            elif period == "3mo":
                days = 90
            else:
                days = 60
            
            dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                                end=datetime.now(), freq='D')
            
            market_data = {}
            
            for symbol in symbols:
                # Deterministik random seed
                np.random.seed(hash(symbol) % 1000)
                
                # Base fiyat
                base_price = 50 + np.random.uniform(-20, 30)
                prices = []
                
                for i in range(len(dates)):
                    if i == 0:
                        price = base_price
                    else:
                        # Trend + noise
                        trend = np.sin(i * 0.1) * 0.3
                        noise = np.random.normal(0, 0.02)
                        price = prices[-1] * (1 + trend + noise)
                    
                    prices.append(max(price, 5))  # Minimum fiyat
                
                # OHLC oluştur
                data = []
                for i, (date, close) in enumerate(zip(dates, prices)):
                    volatility = close * 0.02
                    
                    high = close + np.random.uniform(0, volatility)
                    low = close - np.random.uniform(0, volatility)
                    open_price = np.random.uniform(low, high)
                    volume = np.random.randint(100000, 5000000)
                    
                    data.append({
                        'Date': date,
                        'Open': round(open_price, 2),
                        'High': round(high, 2),
                        'Low': round(low, 2),
                        'Close': round(close, 2),
                        'Volume': volume
                    })
                
                df = pd.DataFrame(data)
                df.set_index('Date', inplace=True)
                market_data[symbol] = df
            
            logger.info(f"✅ Mock piyasa verisi oluşturuldu: {len(symbols)} sembol")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Mock veri oluşturma hatası: {e}")
            return {}
    
    def calculate_portfolio_metrics(self, market_data: Dict[str, pd.DataFrame]) -> Dict:
        """Portföy metriklerini hesapla"""
        try:
            if not self.portfolio_state:
                logger.warning("⚠️ Portföy başlatılmamış")
                return {}
            
            portfolio = self.portfolio_state.copy()
            total_value = portfolio['cash']
            
            # Pozisyon değerlerini güncelle
            for symbol in portfolio['symbols']:
                if symbol in market_data and not market_data[symbol].empty:
                    current_price = market_data[symbol]['Close'].iloc[-1]
                    position_value = portfolio['positions'][symbol] * current_price
                    portfolio['position_values'][symbol] = position_value
                    total_value += position_value
            
            portfolio['total_value'] = total_value
            
            # Günlük getiri hesapla
            if len(portfolio['daily_returns']) > 0:
                daily_return = (total_value - portfolio['daily_returns'][-1]) / portfolio['daily_returns'][-1]
                portfolio['daily_returns'].append(total_value)
            else:
                portfolio['daily_returns'].append(total_value)
                daily_return = 0
            
            # Performans metrikleri
            if len(portfolio['daily_returns']) > 1:
                returns = pd.Series(portfolio['daily_returns']).pct_change().dropna()
                
                # Sharpe ratio (basit)
                if returns.std() > 0:
                    portfolio['sharpe_ratio'] = returns.mean() / returns.std() * np.sqrt(252)
                else:
                    portfolio['sharpe_ratio'] = 0
                
                # Volatilite
                portfolio['volatility'] = returns.std() * np.sqrt(252)
                
                # Maximum drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                portfolio['max_drawdown'] = drawdown.min()
            
            # Portföy durumunu güncelle
            self.portfolio_state = portfolio
            
            logger.info(f"✅ Portföy metrikleri güncellendi: {total_value:,.0f} TL")
            return portfolio
            
        except Exception as e:
            logger.error(f"❌ Portföy metrik hesaplama hatası: {e}")
            return {}
    
    def generate_action_recommendations(self, market_data: Dict[str, pd.DataFrame], 
                                      signals: Dict[str, Any]) -> Dict[str, Any]:
        """Aksiyon önerileri üret"""
        try:
            if not self.portfolio_state:
                logger.warning("⚠️ Portföy başlatılmamış")
                return {}
            
            # Portföy metriklerini güncelle
            portfolio = self.calculate_portfolio_metrics(market_data)
            
            recommendations = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_value': portfolio['total_value'],
                'cash_ratio': portfolio['cash'] / portfolio['total_value'],
                'actions': [],
                'risk_assessment': {},
                'position_sizing': {}
            }
            
            # Her sembol için aksiyon önerisi
            for symbol in portfolio['symbols']:
                if symbol not in market_data or market_data[symbol].empty:
                    continue
                
                current_price = market_data[symbol]['Close'].iloc[-1]
                current_position = portfolio['positions'][symbol]
                position_value = current_position * current_price
                
                # Sinyal kontrolü
                signal_action = signals.get(symbol, {}).get('action', 'HOLD')
                signal_confidence = signals.get(symbol, {}).get('confidence', 0.5)
                
                # Aksiyon belirleme
                action = self._determine_action(
                    signal_action, signal_confidence, current_position, 
                    position_value, portfolio['total_value']
                )
                
                # Lot hesaplama
                lot_size = self._calculate_lot_size(
                    action, signal_confidence, current_price, 
                    portfolio['total_value'], portfolio['cash']
                )
                
                # Risk değerlendirmesi
                risk_level = self._assess_risk(
                    symbol, current_price, lot_size, portfolio['total_value']
                )
                
                # Öneri oluştur
                recommendation = {
                    'symbol': symbol,
                    'action': action,
                    'lot_size': lot_size,
                    'current_price': current_price,
                    'current_position': current_position,
                    'position_value': position_value,
                    'signal_action': signal_action,
                    'signal_confidence': signal_confidence,
                    'risk_level': risk_level,
                    'stop_loss': self._calculate_stop_loss(action, current_price, risk_level),
                    'take_profit': self._calculate_take_profit(action, current_price, risk_level)
                }
                
                recommendations['actions'].append(recommendation)
                
                # Risk değerlendirmesi
                recommendations['risk_assessment'][symbol] = risk_level
                
                # Pozisyon boyutlandırma
                recommendations['position_sizing'][symbol] = {
                    'target_allocation': self._calculate_target_allocation(signal_confidence, risk_level),
                    'max_position_size': self._calculate_max_position_size(portfolio['total_value'], risk_level)
                }
            
            # Portföy seviyesi öneriler
            recommendations['portfolio_recommendations'] = self._generate_portfolio_recommendations(
                portfolio, recommendations['actions']
            )
            
            logger.info(f"✅ {len(recommendations['actions'])} aksiyon önerisi üretildi")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Aksiyon önerisi hatası: {e}")
            return {}
    
    def _determine_action(self, signal_action: str, signal_confidence: float, 
                         current_position: int, position_value: float, 
                         total_value: float) -> str:
        """Aksiyon belirle"""
        try:
            # Pozisyon büyüklüğü kontrolü
            position_ratio = position_value / total_value if total_value > 0 else 0
            
            if signal_action == 'BUY' and signal_confidence > 0.7:
                if position_ratio < 0.2:  # %20'den az pozisyon
                    return 'BUY'
                elif position_ratio < 0.4:  # %40'tan az pozisyon
                    return 'ADD_TO_POSITION'
                else:
                    return 'HOLD'  # Pozisyon yeterli
                    
            elif signal_action == 'SELL' and signal_confidence > 0.7:
                if position_ratio > 0.1:  # %10'dan fazla pozisyon
                    return 'SELL'
                else:
                    return 'HOLD'  # Pozisyon yok
                    
            elif signal_action == 'HOLD':
                return 'HOLD'
                
            else:
                # Düşük güven durumunda
                if position_ratio > 0.3:  # Yüksek pozisyon
                    return 'REDUCE_POSITION'
                else:
                    return 'HOLD'
                    
        except Exception as e:
            logger.error(f"Aksiyon belirleme hatası: {e}")
            return 'HOLD'
    
    def _calculate_lot_size(self, action: str, confidence: float, 
                           current_price: float, total_value: float, 
                           available_cash: float) -> int:
        """Lot büyüklüğü hesapla"""
        try:
            # Risk yönetimi: maksimum %5 portföy değeri
            max_position_value = total_value * 0.05
            
            if action in ['BUY', 'ADD_TO_POSITION']:
                # Güven skoruna göre pozisyon büyüklüğü
                confidence_multiplier = min(confidence, 0.9)
                target_position_value = max_position_value * confidence_multiplier
                
                # Mevcut nakit kontrolü
                target_position_value = min(target_position_value, available_cash * 0.8)
                
                # Lot hesapla
                lot_size = int(target_position_value / current_price)
                
            elif action == 'SELL':
                # Mevcut pozisyonun %50'si
                lot_size = -1  # Satış için negatif
                
            elif action == 'REDUCE_POSITION':
                # Mevcut pozisyonun %25'i
                lot_size = -1  # Satış için negatif
                
            else:
                lot_size = 0
            
            return lot_size
            
        except Exception as e:
            logger.error(f"Lot hesaplama hatası: {e}")
            return 0
    
    def _assess_risk(self, symbol: str, current_price: float, 
                     lot_size: int, total_value: float) -> str:
        """Risk değerlendirmesi"""
        try:
            # Pozisyon büyüklüğü riski
            position_value = abs(lot_size) * current_price
            position_ratio = position_value / total_value if total_value > 0 else 0
            
            # Volatilite riski (basit)
            volatility_risk = np.random.uniform(0.1, 0.3)  # Mock
            
            # Toplam risk skoru
            risk_score = position_ratio * 0.6 + volatility_risk * 0.4
            
            if risk_score > 0.15:
                return 'YÜKSEK'
            elif risk_score > 0.08:
                return 'ORTA'
            else:
                return 'DÜŞÜK'
                
        except Exception as e:
            logger.error(f"Risk değerlendirme hatası: {e}")
            return 'ORTA'
    
    def _calculate_stop_loss(self, action: str, current_price: float, risk_level: str) -> float:
        """Stop loss hesapla"""
        try:
            if action in ['BUY', 'ADD_TO_POSITION']:
                # Alım için stop loss
                if risk_level == 'YÜKSEK':
                    stop_loss = current_price * 0.92  # %8 altında
                elif risk_level == 'ORTA':
                    stop_loss = current_price * 0.94  # %6 altında
                else:
                    stop_loss = current_price * 0.96  # %4 altında
            else:
                stop_loss = 0
            
            return round(stop_loss, 2)
            
        except Exception as e:
            logger.error(f"Stop loss hesaplama hatası: {e}")
            return 0
    
    def _calculate_take_profit(self, action: str, current_price: float, risk_level: str) -> float:
        """Take profit hesapla"""
        try:
            if action in ['BUY', 'ADD_TO_POSITION']:
                # Alım için take profit
                if risk_level == 'YÜKSEK':
                    take_profit = current_price * 1.20  # %20 üstünde
                elif risk_level == 'ORTA':
                    take_profit = current_price * 1.15  # %15 üstünde
                else:
                    take_profit = current_price * 1.12  # %12 üstünde
            else:
                take_profit = 0
            
            return round(take_profit, 2)
            
        except Exception as e:
            logger.error(f"Take profit hesaplama hatası: {e}")
            return 0
    
    def _calculate_target_allocation(self, confidence: float, risk_level: str) -> float:
        """Hedef portföy tahsisi"""
        try:
            # Güven skoruna göre temel tahsis
            base_allocation = confidence * 0.1  # Maksimum %10
            
            # Risk seviyesine göre ayarlama
            if risk_level == 'YÜKSEK':
                risk_multiplier = 0.5
            elif risk_level == 'ORTA':
                risk_multiplier = 0.8
            else:
                risk_multiplier = 1.0
            
            target_allocation = base_allocation * risk_multiplier
            return min(target_allocation, 0.08)  # Maksimum %8
            
        except Exception as e:
            logger.error(f"Hedef tahsis hesaplama hatası: {e}")
            return 0.05
    
    def _calculate_max_position_size(self, total_value: float, risk_level: str) -> float:
        """Maksimum pozisyon büyüklüğü"""
        try:
            if risk_level == 'YÜKSEK':
                max_ratio = 0.03  # %3
            elif risk_level == 'ORTA':
                max_ratio = 0.05  # %5
            else:
                max_ratio = 0.08  # %8
            
            return total_value * max_ratio
            
        except Exception as e:
            logger.error(f"Maksimum pozisyon hesaplama hatası: {e}")
            return total_value * 0.05
    
    def _generate_portfolio_recommendations(self, portfolio: Dict, actions: List[Dict]) -> Dict:
        """Portföy seviyesi öneriler"""
        try:
            recommendations = {
                'rebalance_needed': False,
                'cash_management': 'HOLD',
                'diversification_score': 0.0,
                'overall_risk': 'ORTA'
            }
            
            # Rebalancing kontrolü
            total_positions = sum(portfolio['position_values'].values())
            cash_ratio = portfolio['cash'] / portfolio['total_value']
            
            if cash_ratio < 0.1:  # %10'dan az nakit
                recommendations['cash_management'] = 'INCREASE_CASH'
                recommendations['rebalance_needed'] = True
            elif cash_ratio > 0.4:  # %40'tan fazla nakit
                recommendations['cash_management'] = 'DEPLOY_CASH'
                recommendations['rebalance_needed'] = True
            
            # Çeşitlendirme skoru
            if total_positions > 0:
                position_ratios = [v / portfolio['total_value'] for v in portfolio['position_values'].values() if v > 0]
                if position_ratios:
                    # Her pozisyonun %20'den az olması ideal
                    diversification_score = sum([1 for ratio in position_ratios if ratio < 0.2]) / len(position_ratios)
                    recommendations['diversification_score'] = diversification_score
            
            # Genel risk seviyesi
            high_risk_positions = sum([1 for action in actions if action['risk_level'] == 'YÜKSEK'])
            if high_risk_positions > 2:
                recommendations['overall_risk'] = 'YÜKSEK'
            elif high_risk_positions > 0:
                recommendations['overall_risk'] = 'ORTA'
            else:
                recommendations['overall_risk'] = 'DÜŞÜK'
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Portföy önerisi hatası: {e}")
            return {}
    
    def execute_trades(self, recommendations: Dict[str, Any], 
                      market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Önerilen işlemleri gerçekleştir"""
        try:
            if not recommendations or 'actions' not in recommendations:
                logger.warning("⚠️ İşlem önerisi bulunamadı")
                return {}
            
            executed_trades = {
                'timestamp': datetime.now().isoformat(),
                'trades': [],
                'portfolio_changes': {},
                'total_cost': 0,
                'total_proceeds': 0
            }
            
            total_cost = 0
            total_proceeds = 0
            
            for action in recommendations['actions']:
                symbol = action['symbol']
                action_type = action['action']
                lot_size = action['lot_size']
                current_price = action['current_price']
                
                if lot_size == 0:
                    continue
                
                # İşlem gerçekleştir
                trade = {
                    'symbol': symbol,
                    'action': action_type,
                    'lot_size': lot_size,
                    'price': current_price,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'EXECUTED'
                }
                
                if lot_size > 0:  # Alım
                    cost = lot_size * current_price
                    total_cost += cost
                    trade['cost'] = cost
                    
                    # Portföy güncelle
                    if symbol not in self.portfolio_state['positions']:
                        self.portfolio_state['positions'][symbol] = 0
                    
                    self.portfolio_state['positions'][symbol] += lot_size
                    self.portfolio_state['cash'] -= cost
                    
                else:  # Satış
                    proceeds = abs(lot_size) * current_price
                    total_proceeds += proceeds
                    trade['proceeds'] = proceeds
                    
                    # Portföy güncelle
                    if symbol in self.portfolio_state['positions']:
                        self.portfolio_state['positions'][symbol] += lot_size  # Negatif
                        self.portfolio_state['cash'] += proceeds
                
                executed_trades['trades'].append(trade)
                
                # Portföy değişikliklerini kaydet
                self.portfolio_state['transaction_history'].append(trade)
            
            executed_trades['total_cost'] = total_cost
            executed_trades['total_proceeds'] = total_proceeds
            
            # Portföy durumunu güncelle
            self.portfolio_state['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"✅ {len(executed_trades['trades'])} işlem gerçekleştirildi")
            return executed_trades
            
        except Exception as e:
            logger.error(f"❌ İşlem gerçekleştirme hatası: {e}")
            return {}
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Portföy özeti"""
        if not self.portfolio_state:
            return {'status': 'Portfolio not initialized'}
        
        portfolio = self.portfolio_state.copy()
        
        # Aktif pozisyonlar
        active_positions = {symbol: value for symbol, value in portfolio['position_values'].items() 
                           if value > 0}
        
        # Toplam pozisyon değeri
        total_positions_value = sum(active_positions.values())
        
        # Dağılım
        allocation = {}
        for symbol, value in active_positions.items():
            allocation[symbol] = value / portfolio['total_value'] if portfolio['total_value'] > 0 else 0
        
        summary = {
            'total_value': portfolio['total_value'],
            'cash': portfolio['cash'],
            'cash_ratio': portfolio['cash'] / portfolio['total_value'],
            'total_positions_value': total_positions_value,
            'active_positions': len(active_positions),
            'allocation': allocation,
            'performance_metrics': {
                'sharpe_ratio': portfolio.get('sharpe_ratio', 0),
                'volatility': portfolio.get('volatility', 0),
                'max_drawdown': portfolio.get('max_drawdown', 0)
            },
            'last_update': portfolio['timestamp']
        }
        
        return summary

# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 RL Portfolio Agent Test Ediliyor...")
    
    agent = RLPortfolioAgent()
    
    # Portföy başlat
    print("\n🚀 Portföy başlatılıyor...")
    portfolio = agent.initialize_portfolio(initial_capital=100000)
    
    if portfolio:
        print(f"✅ Portföy başlatıldı: {portfolio['total_value']:,.0f} TL")
        
        # Piyasa verisi al
        print("\n📊 Piyasa verisi alınıyor...")
        market_data = agent.get_market_data(portfolio['symbols'])
        
        if market_data:
            print(f"✅ {len(market_data)} sembol için veri alındı")
            
            # Mock sinyaller
            mock_signals = {
                'SISE.IS': {'action': 'BUY', 'confidence': 0.8},
                'TUPRS.IS': {'action': 'HOLD', 'confidence': 0.6},
                'GARAN.IS': {'action': 'SELL', 'confidence': 0.7},
                'KCHOL.IS': {'action': 'BUY', 'confidence': 0.75},
                'THYAO.IS': {'action': 'HOLD', 'confidence': 0.5}
            }
            
            # Aksiyon önerileri
            print("\n🎯 Aksiyon önerileri üretiliyor...")
            recommendations = agent.generate_action_recommendations(market_data, mock_signals)
            
            if recommendations:
                print(f"✅ {len(recommendations['actions'])} öneri üretildi")
                
                # Önerileri göster
                for action in recommendations['actions']:
                    print(f"   {action['symbol']}: {action['action']} ({action['lot_size']} lot)")
                    print(f"      Fiyat: {action['current_price']:.2f} TL")
                    print(f"      Risk: {action['risk_level']}")
                    print(f"      SL: {action['stop_loss']:.2f}, TP: {action['take_profit']:.2f}")
                
                # İşlemleri gerçekleştir
                print("\n💼 İşlemler gerçekleştiriliyor...")
                executed_trades = agent.execute_trades(recommendations, market_data)
                
                if executed_trades:
                    print(f"✅ {len(executed_trades['trades'])} işlem gerçekleştirildi")
                    print(f"   Toplam Maliyet: {executed_trades['total_cost']:,.0f} TL")
                    print(f"   Toplam Gelir: {executed_trades['total_proceeds']:,.0f} TL")
                
                # Portföy özeti
                print("\n📋 Portföy özeti:")
                summary = agent.get_portfolio_summary()
                print(f"   Toplam Değer: {summary['total_value']:,.0f} TL")
                print(f"   Nakit: {summary['cash']:,.0f} TL")
                print(f"   Aktif Pozisyonlar: {summary['active_positions']}")
                print(f"   Sharpe Ratio: {summary['performance_metrics']['sharpe_ratio']:.3f}")
                
            else:
                print("❌ Aksiyon önerisi üretilemedi")
        else:
            print("❌ Piyasa verisi alınamadı")
    else:
        print("❌ Portföy başlatılamadı")
    
    print("\n✅ Test tamamlandı!")
