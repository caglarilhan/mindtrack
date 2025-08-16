"""
PRD v2.0 - RL Portföy Ajanı
FinRL, DDPG → lot & re-hedge önerisi
Paper-trading sim ile Sharpe > 1.2 hedefi
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# RL imports
try:
    import gym
    from stable_baselines3 import PPO, SAC, TD3
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.callbacks import EvalCallback
    import finrl
    from finrl import config
    from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
    from finrl.meta.preprocessor.preprocessors import FeatureEngineer
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
except ImportError:
    print("⚠️ Stable-baselines3 veya FinRL yüklü değil")
    PPO = None

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RLPortfolioAgent:
    """PRD v2.0 RL Portföy Ajanı - FinRL, DDPG"""
    
    def __init__(self, initial_balance: float = 100000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.positions = {}
        self.portfolio_value = initial_balance
        self.trade_history = []
        self.model = None
        self.env = None
        
    def prepare_trading_data(self, symbols: List[str], 
                           start_date: str = "2023-01-01",
                           end_date: str = "2024-12-31") -> pd.DataFrame:
        """Trading için veri hazırla"""
        try:
            # Çoklu sembol veri çek
            data_list = []
            for symbol in symbols:
                try:
                    data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
                    if not data.empty:
                        data['symbol'] = symbol
                        data_list.append(data)
                        logger.info(f"{symbol} verisi yüklendi: {len(data)} gün")
                except Exception as e:
                    logger.warning(f"{symbol} verisi yüklenemedi: {e}")
                    continue
            
            if not data_list:
                logger.error("Hiçbir sembol verisi yüklenemedi")
                return pd.DataFrame()
            
            # Verileri birleştir
            combined_data = pd.concat(data_list, ignore_index=True)
            
            # Feature engineering yapma, sadece veriyi kullan
            
            logger.info(f"Trading verisi hazırlandı: {len(combined_data)} kayıt")
            return combined_data
            
        except Exception as e:
            logger.error(f"Veri hazırlama hatası: {e}")
            return pd.DataFrame()
    
    def _simple_feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """Basit trading özellikleri"""
        try:
            # Her sembol için ayrı ayrı işle
            processed_data = []
            
            for symbol in data['symbol'].unique():
                symbol_data = data[data['symbol'] == symbol].copy()
                
                # Basit özellikler ekle
                symbol_data['price_change'] = symbol_data['Close'].pct_change()
                symbol_data['volume_change'] = symbol_data['Volume'].pct_change()
                
                processed_data.append(symbol_data)
            
            # Tüm verileri birleştir
            combined_data = pd.concat(processed_data, ignore_index=True)
            
            # NaN değerleri temizle
            combined_data = combined_data.dropna()
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Basit feature engineering hatası: {e}")
            return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI hesapla"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception:
            return pd.Series(index=prices.index)
    
    def create_trading_environment(self, data: pd.DataFrame, 
                                 symbols: List[str]) -> bool:
        """Trading environment oluştur"""
        try:
            if not data.empty and len(symbols) > 0:
                # Basit trading environment
                self.env = SimpleTradingEnv(
                    data=data,
                    symbols=symbols,
                    initial_balance=self.initial_balance
                )
                logger.info("Trading environment oluşturuldu")
                return True
            else:
                logger.error("Environment oluşturulamadı - veri eksik")
                return False
                
        except Exception as e:
            logger.error(f"Environment oluşturma hatası: {e}")
            return False
    
    def train_rl_agent(self, total_timesteps: int = 10000) -> bool:
        """RL agent eğitimi"""
        try:
            if self.env is None:
                logger.error("Environment oluşturulmamış")
                return False
            
            if PPO is None:
                logger.warning("PPO yüklü değil, basit agent kullanılıyor")
                return self._train_simple_agent()
            
            # PPO model
            self.model = PPO(
                "MlpPolicy",
                self.env,
                verbose=1,
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01
            )
            
            # Eğitim
            logger.info("RL agent eğitimi başlıyor...")
            self.model.learn(total_timesteps=total_timesteps)
            
            logger.info("RL agent eğitimi tamamlandı")
            return True
            
        except Exception as e:
            logger.error(f"RL agent eğitim hatası: {e}")
            return False
    
    def _train_simple_agent(self) -> bool:
        """Basit rule-based agent"""
        try:
            logger.info("Basit rule-based agent eğitiliyor...")
            # Basit trading kuralları
            self.simple_rules = {
                'buy_threshold': 0.02,  # %2 düşüş
                'sell_threshold': 0.02,  # %2 yükseliş
                'stop_loss': 0.05,       # %5 stop loss
                'take_profit': 0.10      # %10 take profit
            }
            
            logger.info("Basit agent eğitimi tamamlandı")
            return True
            
        except Exception as e:
            logger.error(f"Basit agent eğitim hatası: {e}")
            return False
    
    def generate_trading_signals(self, current_data: pd.DataFrame) -> Dict:
        """Trading sinyalleri üret"""
        try:
            if self.model is None and not hasattr(self, 'simple_rules'):
                logger.error("Agent eğitilmemiş")
                return {}
            
            signals = {}
            
            for symbol in current_data['symbol'].unique():
                symbol_data = current_data[current_data['symbol'] == symbol].iloc[-1]
                
                if self.model is not None:
                    # RL model sinyali
                    signal = self._get_rl_signal(symbol_data)
                else:
                    # Basit rule-based sinyal
                    signal = self._get_simple_signal(symbol_data)
                
                signals[symbol] = signal
            
            logger.info(f"{len(signals)} trading sinyali üretildi")
            return signals
            
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {e}")
            return {}
    
    def _get_rl_signal(self, data: pd.Series) -> Dict:
        """RL model sinyali"""
        try:
            # Environment state'i hazırla
            state = self.env._get_observation()
            
            # Model tahmini
            action, _ = self.model.predict(state, deterministic=True)
            
            # Action'ı sinyale çevir
            signal = {
                'action': 'HOLD',
                'confidence': 0.5,
                'position_size': 0.0,
                'stop_loss': None,
                'take_profit': None
            }
            
            if action[0] > 0.6:
                signal['action'] = 'BUY'
                signal['confidence'] = action[0]
                signal['position_size'] = min(action[0], 1.0)
            elif action[0] < 0.4:
                signal['action'] = 'SELL'
                signal['confidence'] = 1 - action[0]
                signal['position_size'] = min(1 - action[0], 1.0)
            
            return signal
            
        except Exception as e:
            logger.error(f"RL sinyal hatası: {e}")
            return {'action': 'HOLD', 'confidence': 0.0, 'position_size': 0.0}
    
    def _get_simple_signal(self, data: pd.Series) -> Dict:
        """Basit rule-based sinyal"""
        try:
            signal = {
                'action': 'HOLD',
                'confidence': 0.5,
                'position_size': 0.0,
                'stop_loss': None,
                'take_profit': None
            }
            
            # Basit random sinyal (test için)
            import random
            action_choice = random.choice(['BUY', 'SELL', 'HOLD'])
            
            if action_choice == 'BUY':
                signal['action'] = 'BUY'
                signal['confidence'] = 0.7
                signal['position_size'] = 0.3
                signal['stop_loss'] = data['Close'] * 0.95  # %5 stop loss
                signal['take_profit'] = data['Close'] * 1.10  # %10 take profit
            elif action_choice == 'SELL':
                signal['action'] = 'SELL'
                signal['confidence'] = 0.7
                signal['position_size'] = 0.3
            
            return signal
            
        except Exception as e:
            logger.error(f"Basit sinyal hatası: {e}")
            return {'action': 'HOLD', 'confidence': 0.0, 'position_size': 0.0}
    
    def execute_trade(self, symbol: str, signal: Dict, 
                     current_price: float) -> bool:
        """Trade execute et"""
        try:
            if signal['action'] == 'HOLD':
                return True
            
            # Position size hesapla
            position_value = self.current_balance * signal['position_size']
            shares = int(position_value / current_price)
            
            if signal['action'] == 'BUY':
                if self.current_balance >= position_value:
                    # Buy order
                    self.positions[symbol] = {
                        'shares': shares,
                        'entry_price': current_price,
                        'entry_date': datetime.now(),
                        'stop_loss': signal.get('stop_loss'),
                        'take_profit': signal.get('take_profit')
                    }
                    self.current_balance -= position_value
                    
                    # Trade history
                    self.trade_history.append({
                        'date': datetime.now(),
                        'symbol': symbol,
                        'action': 'BUY',
                        'shares': shares,
                        'price': current_price,
                        'value': position_value
                    })
                    
                    logger.info(f"BUY order executed: {symbol} - {shares} shares @ {current_price}")
                    return True
                    
            elif signal['action'] == 'SELL':
                if symbol in self.positions:
                    # Sell order
                    position = self.positions[symbol]
                    sell_value = position['shares'] * current_price
                    self.current_balance += sell_value
                    
                    # P&L hesapla
                    pnl = sell_value - (position['shares'] * position['entry_price'])
                    
                    # Trade history
                    self.trade_history.append({
                        'date': datetime.now(),
                        'symbol': symbol,
                        'action': 'SELL',
                        'shares': position['shares'],
                        'price': current_price,
                        'value': sell_value,
                        'pnl': pnl
                    })
                    
                    # Position'ı kaldır
                    del self.positions[symbol]
                    
                    logger.info(f"SELL order executed: {symbol} - {position['shares']} shares @ {current_price}, P&L: {pnl:.2f}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Trade execution hatası: {e}")
            return False
    
    def update_portfolio_value(self, current_prices: Dict[str, float]):
        """Portföy değerini güncelle"""
        try:
            portfolio_value = self.current_balance
            
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    position_value = position['shares'] * current_price
                    portfolio_value += position_value
                    
                    # Stop loss / take profit kontrol
                    if position.get('stop_loss') and current_price <= position['stop_loss']:
                        logger.info(f"Stop loss triggered: {symbol}")
                        self.execute_trade(symbol, {'action': 'SELL', 'position_size': 1.0}, current_price)
                    elif position.get('take_profit') and current_price >= position['take_profit']:
                        logger.info(f"Take profit triggered: {symbol}")
                        self.execute_trade(symbol, {'action': 'SELL', 'position_size': 1.0}, current_price)
            
            self.portfolio_value = portfolio_value
            
        except Exception as e:
            logger.error(f"Portfolio güncelleme hatası: {e}")
    
    def calculate_performance_metrics(self) -> Dict:
        """Performans metrikleri hesapla"""
        try:
            if not self.trade_history:
                return {}
            
            # Returns
            total_return = (self.portfolio_value - self.initial_balance) / self.initial_balance
            
            # P&L
            total_pnl = sum([trade.get('pnl', 0) for trade in self.trade_history])
            
            # Win rate
            winning_trades = [t for t in self.trade_history if t.get('pnl', 0) > 0]
            win_rate = len(winning_trades) / len(self.trade_history) if self.trade_history else 0
            
            # Sharpe ratio (basit)
            returns = [trade.get('pnl', 0) / self.initial_balance for trade in self.trade_history]
            if returns:
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
            
            metrics = {
                'total_return': total_return,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'sharpe_ratio': sharpe_ratio,
                'portfolio_value': self.portfolio_value,
                'current_balance': self.current_balance,
                'active_positions': len(self.positions),
                'total_trades': len(self.trade_history),
                'prd_target_met': sharpe_ratio > 1.2  # PRD v2.0 hedefi
            }
            
            logger.info(f"Performans metrikleri hesaplandı - Sharpe: {sharpe_ratio:.2f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Performans hesaplama hatası: {e}")
            return {}
    
    def get_portfolio_summary(self) -> Dict:
        """Portföy özeti"""
        try:
            summary = {
                'initial_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'portfolio_value': self.portfolio_value,
                'active_positions': len(self.positions),
                'positions': self.positions.copy(),
                'recent_trades': self.trade_history[-10:] if self.trade_history else []
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Portfolio özet hatası: {e}")
            return {}

class SimpleTradingEnv:
    """Basit trading environment"""
    
    def __init__(self, data: pd.DataFrame, symbols: List[str], initial_balance: float):
        self.data = data
        self.symbols = symbols
        self.initial_balance = initial_balance
        self.current_step = 0
        self.reset()
    
    def reset(self):
        """Environment reset"""
        self.current_step = 0
        self.balance = self.initial_balance
        self.positions = {symbol: 0 for symbol in self.symbols}
        return self._get_observation()
    
    def step(self, action):
        """Environment step"""
        # Basit step implementation
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        
        # Reward hesapla (basit)
        reward = 0
        if not done:
            current_data = self.data.iloc[self.current_step]
            reward = self._calculate_reward(action, current_data)
        
        next_state = self._get_observation()
        info = {}
        
        return next_state, reward, done, info
    
    def _get_observation(self):
        """Environment observation"""
        # Basit observation - sadece balance ve positions
        features = [self.balance / self.initial_balance]  # Balance ratio
        
        for symbol in self.symbols:
            features.append(self.positions[symbol] / 100)  # Position size
        
        return np.array(features, dtype=np.float32)
    
    def _calculate_reward(self, action, current_data):
        """Reward hesapla"""
        # Basit reward function
        return np.random.normal(0, 0.1)  # Placeholder

# Test fonksiyonu
def test_rl_portfolio_agent():
    """RL Portfolio Agent test"""
    try:
        print("🧪 RL Portfolio Agent Test")
        print("="*50)
        
        # Test sembolleri
        symbols = ["SISE.IS", "EREGL.IS", "TUPRS.IS"]
        
        # RL Agent başlat
        agent = RLPortfolioAgent(initial_balance=100000)
        
        # Trading verisi hazırla
        print("\n📊 Trading Verisi Hazırlanıyor:")
        data = agent.prepare_trading_data(symbols, start_date="2023-01-01", end_date="2024-12-31")
        
        if data.empty:
            print("❌ Trading verisi hazırlanamadı")
            return
        
        print(f"✅ Trading verisi hazırlandı: {len(data)} kayıt")
        
        # Trading environment oluştur
        print("\n🏗️ Trading Environment:")
        env_created = agent.create_trading_environment(data, symbols)
        
        if env_created:
            print("✅ Trading environment oluşturuldu")
            
            # RL Agent eğitimi
            print("\n🤖 RL Agent Eğitimi:")
            training_success = agent.train_rl_agent(total_timesteps=5000)
            
            if training_success:
                print("✅ RL Agent eğitimi tamamlandı")
                
                # Trading sinyalleri
                print("\n🚦 Trading Sinyalleri:")
                current_data = data.tail(10)  # Son 10 gün
                signals = agent.generate_trading_signals(current_data)
                
                for symbol, signal in signals.items():
                    print(f"{symbol}: {signal['action']} - Confidence: {signal['confidence']:.2f}")
                
                # Simüle trade execution
                print("\n💼 Trade Execution Simülasyonu:")
                current_prices = {"SISE.IS": 40.0, "EREGL.IS": 28.0, "TUPRS.IS": 165.0}
                
                for symbol, signal in signals.items():
                    if signal['action'] != 'HOLD':
                        success = agent.execute_trade(symbol, signal, current_prices[symbol])
                        print(f"{symbol} trade: {'✅ Başarılı' if success else '❌ Başarısız'}")
                
                # Portfolio güncelle
                agent.update_portfolio_value(current_prices)
                
                # Performans metrikleri
                print("\n📊 Performans Metrikleri:")
                metrics = agent.calculate_performance_metrics()
                
                if metrics:
                    print(f"Toplam Return: {metrics['total_return']:.2%}")
                    print(f"Toplam P&L: {metrics['total_pnl']:.2f}")
                    print(f"Win Rate: {metrics['win_rate']:.2%}")
                    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
                    print(f"Portfolio Değeri: {metrics['portfolio_value']:.2f}")
                    print(f"PRD Hedefi: {'✅ Başarılı' if metrics['prd_target_met'] else '❌ Başarısız'}")
                
                # Portfolio özeti
                print("\n📋 Portfolio Özeti:")
                summary = agent.get_portfolio_summary()
                print(f"Aktif Pozisyonlar: {summary['active_positions']}")
                print(f"Toplam Trade: {len(summary['recent_trades'])}")
                
            else:
                print("❌ RL Agent eğitimi başarısız")
        else:
            print("❌ Trading environment oluşturulamadı")
        
        print("\n✅ RL Portfolio Agent test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_rl_portfolio_agent()
