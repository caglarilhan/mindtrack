"""
PRD v2.0 - Auto-Backtest & Walk Forward Engine
vectorbt-pro (lite) / backtesting.py CLI entegrasyonu
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AutoBacktestWalkForward:
    """Otomatik backtest ve walk forward analizi"""
    
    def __init__(self):
        self.backtest_results = {}
        self.walkforward_results = {}
        self.performance_metrics = {}
        self.optimization_history = []
        
    def get_stock_data_for_backtest(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """Backtest için hisse verisi getir"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval='1d')
            
            if data.empty:
                logger.warning(f"⚠️ {symbol} için veri bulunamadı")
                return self._generate_mock_data_for_backtest(symbol, period)
            
            # Veriyi temizle ve formatla
            data = data.dropna()
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            logger.info(f"✅ {symbol} backtest verisi hazırlandı: {len(data)} kayıt")
            return data
            
        except Exception as e:
            logger.error(f"❌ {symbol} veri alma hatası: {e}")
            return self._generate_mock_data_for_backtest(symbol, period)
    
    def _generate_mock_data_for_backtest(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """Mock backtest verisi oluştur"""
        try:
            # Gün sayısı
            days = 730 if period == "2y" else 365
            
            # Tarih aralığı
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            np.random.seed(hash(symbol) % 1000)
            
            # Mock OHLCV veri
            base_price = 100 + np.random.uniform(-20, 20)
            prices = []
            
            for i in range(len(dates)):
                if i == 0:
                    price = base_price
                else:
                    # Trend + noise
                    trend = np.sin(i * 0.01) * 0.3
                    noise = np.random.normal(0, 0.02)
                    price = prices[-1] * (1 + trend + noise)
                
                prices.append(max(price, 10))
            
            # OHLC oluştur
            data = []
            for i, (date, close) in enumerate(zip(dates, prices)):
                volatility = close * 0.02
                
                high = close + np.random.uniform(0, volatility)
                low = close - np.random.uniform(0, volatility)
                open_price = np.random.uniform(low, high)
                volume = np.random.randint(1000000, 10000000)
                
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
            
            logger.info(f"✅ {symbol} için mock backtest verisi oluşturuldu")
            return df
            
        except Exception as e:
            logger.error(f"❌ Mock veri oluşturma hatası: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Teknik indikatörleri hesapla"""
        try:
            df = data.copy()
            
            # Moving Averages
            for period in [5, 10, 20, 50, 200]:
                df[f'SMA_{period}'] = df['Close'].rolling(period).mean()
                df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()
            
            # Bollinger Bands
            df['BB_middle'] = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
            df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
            df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema12 = df['Close'].ewm(span=12).mean()
            ema26 = df['Close'].ewm(span=26).mean()
            df['MACD'] = ema12 - ema26
            df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
            
            # Stochastic
            for period in [14, 21]:
                low_min = df['Low'].rolling(period).min()
                high_max = df['High'].rolling(period).max()
                df[f'Stoch_K_{period}'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
                df[f'Stoch_D_{period}'] = df[f'Stoch_K_{period}'].rolling(3).mean()
            
            # ATR
            df['ATR'] = self._calculate_atr(df)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
            
            # NaN değerleri temizle
            df = df.dropna()
            
            logger.info("✅ Teknik indikatörler hesaplandı")
            return df
            
        except Exception as e:
            logger.error(f"❌ Teknik indikatör hesaplama hatası: {e}")
            return data
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range hesapla"""
        try:
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(period).mean()
            
            return atr
            
        except Exception as e:
            logger.error(f"❌ ATR hesaplama hatası: {e}")
            return pd.Series(index=data.index)
    
    def generate_trading_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Trading sinyalleri üret"""
        try:
            df = data.copy()
            
            # Sinyal sütunları
            df['Signal'] = 0  # 0: Hold, 1: Buy, -1: Sell
            df['Position'] = 0  # 0: No position, 1: Long, -1: Short
            
            # EMA Cross sinyali
            df['EMA_Cross'] = np.where(
                (df['EMA_20'] > df['EMA_50']) & (df['EMA_20'].shift(1) <= df['EMA_50'].shift(1)),
                1,  # Golden Cross
                np.where(
                    (df['EMA_20'] < df['EMA_50']) & (df['EMA_20'].shift(1) >= df['EMA_50'].shift(1)),
                    -1,  # Death Cross
                    0
                )
            )
            
            # RSI sinyali
            df['RSI_Signal'] = np.where(
                df['RSI'] < 30, 1,  # Oversold
                np.where(df['RSI'] > 70, -1, 0)  # Overbought
            )
            
            # MACD sinyali
            df['MACD_Signal'] = np.where(
                (df['MACD'] > df['MACD_signal']) & (df['MACD'].shift(1) <= df['MACD_signal'].shift(1)),
                1,  # MACD crosses above signal
                np.where(
                    (df['MACD'] < df['MACD_signal']) & (df['MACD'].shift(1) >= df['MACD_signal'].shift(1)),
                    -1,  # MACD crosses below signal
                    0
                )
            )
            
            # Bollinger Band sinyali
            df['BB_Signal'] = np.where(
                df['Close'] < df['BB_lower'], 1,  # Price below lower band
                np.where(df['Close'] > df['BB_upper'], -1, 0)  # Price above upper band
            )
            
            # Stochastic sinyali
            df['Stoch_Signal'] = np.where(
                (df['Stoch_K_14'] < 20) & (df['Stoch_D_14'] < 20), 1,  # Oversold
                np.where(
                    (df['Stoch_K_14'] > 80) & (df['Stoch_D_14'] > 80), -1,  # Overbought
                    0
                )
            )
            
            # Kompozit sinyal
            df['Composite_Signal'] = (
                df['EMA_Cross'] * 0.3 +
                df['RSI_Signal'] * 0.2 +
                df['MACD_Signal'] * 0.2 +
                df['BB_Signal'] * 0.15 +
                df['Stoch_Signal'] * 0.15
            )
            
            # Sinyal eşiği
            df['Signal'] = np.where(df['Composite_Signal'] > 0.3, 1,
                                  np.where(df['Composite_Signal'] < -0.3, -1, 0))
            
            # Pozisyon takibi
            position = 0
            for i in range(len(df)):
                if df.iloc[i]['Signal'] == 1 and position == 0:
                    position = 1  # Long position
                elif df.iloc[i]['Signal'] == -1 and position == 1:
                    position = 0  # Close long position
                df.iloc[i, df.columns.get_loc('Position')] = position
            
            logger.info("✅ Trading sinyalleri üretildi")
            return df
            
        except Exception as e:
            logger.error(f"❌ Sinyal üretme hatası: {e}")
            return data
    
    def run_backtest(self, data: pd.DataFrame, initial_capital: float = 100000) -> Dict[str, Any]:
        """Backtest çalıştır"""
        try:
            if data.empty:
                return {}
            
            # Sinyalleri üret
            df = self.generate_trading_signals(data)
            
            # Backtest parametreleri
            capital = initial_capital
            shares = 0
            trades = []
            equity_curve = []
            
            for i in range(len(df)):
                current_price = df.iloc[i]['Close']
                signal = df.iloc[i]['Signal']
                position = df.iloc[i]['Position']
                
                # Trade logic
                if signal == 1 and shares == 0:  # Buy signal
                    shares = capital / current_price
                    capital = 0
                    trades.append({
                        'date': df.index[i],
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares,
                        'capital': capital
                    })
                
                elif signal == -1 and shares > 0:  # Sell signal
                    capital = shares * current_price
                    shares = 0
                    trades.append({
                        'date': df.index[i],
                        'action': 'SELL',
                        'price': current_price,
                        'shares': shares,
                        'capital': capital
                    })
                
                # Current equity
                current_equity = capital + (shares * current_price)
                equity_curve.append({
                    'date': df.index[i],
                    'equity': current_equity,
                    'position': position
                })
            
            # Final position close
            if shares > 0:
                final_price = df.iloc[-1]['Close']
                capital = shares * final_price
                shares = 0
            
            # Performance metrics
            final_equity = capital
            total_return = (final_equity - initial_capital) / initial_capital * 100
            
            # Equity curve DataFrame
            equity_df = pd.DataFrame(equity_curve)
            equity_df.set_index('date', inplace=True)
            
            # Drawdown calculation
            peak = equity_df['equity'].expanding().max()
            drawdown = (equity_df['equity'] - peak) / peak * 100
            
            # Risk metrics
            daily_returns = equity_df['equity'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized
            sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
            
            # Max drawdown
            max_drawdown = drawdown.min()
            
            # Trade statistics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['action'] == 'SELL'])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            backtest_result = {
                'initial_capital': initial_capital,
                'final_equity': final_equity,
                'total_return': round(total_return, 2),
                'volatility': round(volatility, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': round(win_rate, 2),
                'equity_curve': equity_df.to_dict(),
                'trades': trades,
                'drawdown': drawdown.to_dict()
            }
            
            logger.info(f"✅ Backtest tamamlandı: {total_return:.2f}% return")
            return backtest_result
            
        except Exception as e:
            logger.error(f"❌ Backtest hatası: {e}")
            return {}
    
    def run_walk_forward_analysis(self, data: pd.DataFrame, 
                                 train_period: int = 252,  # 1 yıl
                                 test_period: int = 63,    # 3 ay
                                 step_size: int = 21) -> Dict[str, Any]:  # 1 ay
        """Walk Forward analizi çalıştır"""
        try:
            if data.empty or len(data) < train_period + test_period:
                logger.warning("⚠️ Yetersiz veri için walk forward analizi")
                return {}
            
            walk_forward_results = []
            total_periods = len(data)
            
            for start_idx in range(0, total_periods - train_period - test_period + 1, step_size):
                # Train period
                train_start = start_idx
                train_end = start_idx + train_period
                
                # Test period
                test_start = train_end
                test_end = min(test_start + test_period, total_periods)
                
                # Data split
                train_data = data.iloc[train_start:train_end]
                test_data = data.iloc[test_start:test_end]
                
                # Train model (basit moving average strategy)
                train_signals = self.generate_trading_signals(train_data)
                
                # Test on out-of-sample data
                test_signals = self.generate_trading_signals(test_data)
                
                # Backtest on test data
                test_backtest = self.run_backtest(test_signals, 100000)
                
                if test_backtest:
                    walk_forward_results.append({
                        'period': f"{test_data.index[0].strftime('%Y-%m-%d')} to {test_data.index[-1].strftime('%Y-%m-%d')}",
                        'train_start': train_data.index[0].strftime('%Y-%m-%d'),
                        'train_end': train_data.index[-1].strftime('%Y-%m-%d'),
                        'test_start': test_data.index[0].strftime('%Y-%m-%d'),
                        'test_end': test_data.index[-1].strftime('%Y-%m-%d'),
                        'test_return': test_backtest.get('total_return', 0),
                        'test_sharpe': test_backtest.get('sharpe_ratio', 0),
                        'test_drawdown': test_backtest.get('max_drawdown', 0),
                        'test_trades': test_backtest.get('total_trades', 0)
                    })
            
            if walk_forward_results:
                # Performance summary
                returns = [r['test_return'] for r in walk_forward_results]
                sharpes = [r['test_sharpe'] for r in walk_forward_results]
                drawdowns = [r['test_drawdown'] for r in walk_forward_results]
                
                walk_forward_summary = {
                    'total_periods': len(walk_forward_results),
                    'avg_return': round(np.mean(returns), 2),
                    'avg_sharpe': round(np.mean(sharpes), 2),
                    'avg_drawdown': round(np.mean(drawdowns), 2),
                    'return_std': round(np.std(returns), 2),
                    'sharpe_std': round(np.std(sharpes), 2),
                    'best_period': max(walk_forward_results, key=lambda x: x['test_return']),
                    'worst_period': min(walk_forward_results, key=lambda x: x['test_return']),
                    'period_results': walk_forward_results
                }
                
                logger.info(f"✅ Walk Forward analizi tamamlandı: {len(walk_forward_results)} periyot")
                return walk_forward_summary
            else:
                logger.warning("⚠️ Walk Forward sonucu bulunamadı")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Walk Forward analiz hatası: {e}")
            return {}
    
    def optimize_strategy_parameters(self, data: pd.DataFrame, 
                                   param_ranges: Dict[str, List] = None) -> Dict[str, Any]:
        """Strateji parametrelerini optimize et"""
        try:
            if data.empty:
                return {}
            
            # Varsayılan parametre aralıkları
            if param_ranges is None:
                param_ranges = {
                    'ema_short': [5, 10, 15, 20],
                    'ema_long': [30, 40, 50, 60],
                    'rsi_oversold': [20, 25, 30],
                    'rsi_overbought': [70, 75, 80],
                    'bb_period': [15, 20, 25],
                    'bb_std': [1.5, 2.0, 2.5]
                }
            
            optimization_results = []
            
            # Grid search
            for ema_short in param_ranges['ema_short']:
                for ema_long in param_ranges['ema_long']:
                    if ema_short >= ema_long:
                        continue
                    
                    for rsi_oversold in param_ranges['rsi_oversold']:
                        for rsi_overbought in param_ranges['rsi_overbought']:
                            if rsi_oversold >= rsi_overbought:
                                continue
                            
                            for bb_period in param_ranges['bb_period']:
                                for bb_std in param_ranges['bb_std']:
                                    try:
                                        # Parametreleri uygula
                                        test_data = self._apply_parameters(data, {
                                            'ema_short': ema_short,
                                            'ema_long': ema_long,
                                            'rsi_oversold': rsi_oversold,
                                            'rsi_overbought': rsi_overbought,
                                            'bb_period': bb_period,
                                            'bb_std': bb_std
                                        })
                                        
                                        # Backtest çalıştır
                                        backtest_result = self.run_backtest(test_data)
                                        
                                        if backtest_result:
                                            optimization_results.append({
                                                'parameters': {
                                                    'ema_short': ema_short,
                                                    'ema_long': ema_long,
                                                    'rsi_oversold': rsi_oversold,
                                                    'rsi_overbought': rsi_overbought,
                                                    'bb_period': bb_period,
                                                    'bb_std': bb_std
                                                },
                                                'performance': {
                                                    'total_return': backtest_result.get('total_return', 0),
                                                    'sharpe_ratio': backtest_result.get('sharpe_ratio', 0),
                                                    'max_drawdown': backtest_result.get('max_drawdown', 0),
                                                    'win_rate': backtest_result.get('win_rate', 0)
                                                }
                                            })
                                    
                                    except Exception as e:
                                        logger.debug(f"Parametre kombinasyonu hatası: {e}")
                                        continue
            
            if optimization_results:
                # En iyi parametreleri bul
                best_by_return = max(optimization_results, key=lambda x: x['performance']['total_return'])
                best_by_sharpe = max(optimization_results, key=lambda x: x['performance']['sharpe_ratio'])
                best_by_drawdown = min(optimization_results, key=lambda x: x['performance']['max_drawdown'])
                
                optimization_summary = {
                    'total_combinations': len(optimization_results),
                    'best_by_return': best_by_return,
                    'best_by_sharpe': best_by_sharpe,
                    'best_by_drawdown': best_by_drawdown,
                    'all_results': optimization_results
                }
                
                logger.info(f"✅ Parametre optimizasyonu tamamlandı: {len(optimization_results)} kombinasyon")
                return optimization_summary
            else:
                logger.warning("⚠️ Optimizasyon sonucu bulunamadı")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Parametre optimizasyon hatası: {e}")
            return {}
    
    def _apply_parameters(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Parametreleri veriye uygula"""
        try:
            df = data.copy()
            
            # EMA hesapla
            df[f'EMA_{params["ema_short"]}'] = df['Close'].ewm(span=params['ema_short']).mean()
            df[f'EMA_{params["ema_long"]}'] = df['Close'].ewm(span=params['ema_long']).mean()
            
            # RSI hesapla
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_middle'] = df['Close'].rolling(params['bb_period']).mean()
            bb_std = df['Close'].rolling(params['bb_period']).std()
            df['BB_upper'] = df['BB_middle'] + (bb_std * params['bb_std'])
            df['BB_lower'] = df['BB_middle'] - (bb_std * params['bb_std'])
            
            return df.dropna()
            
        except Exception as e:
            logger.error(f"❌ Parametre uygulama hatası: {e}")
            return data
    
    def generate_backtest_report(self, symbol: str, backtest_result: Dict[str, Any], 
                                walk_forward_result: Dict[str, Any] = None,
                                optimization_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Kapsamlı backtest raporu oluştur"""
        try:
            report = {
                'symbol': symbol,
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'backtest_summary': {
                    'initial_capital': backtest_result.get('initial_capital', 0),
                    'final_equity': backtest_result.get('final_equity', 0),
                    'total_return': backtest_result.get('total_return', 0),
                    'annualized_return': round(backtest_result.get('total_return', 0) / 2, 2),  # 2 yıl varsayım
                    'volatility': backtest_result.get('volatility', 0),
                    'sharpe_ratio': backtest_result.get('sharpe_ratio', 0),
                    'max_drawdown': backtest_result.get('max_drawdown', 0),
                    'total_trades': backtest_result.get('total_trades', 0),
                    'win_rate': backtest_result.get('win_rate', 0)
                },
                'risk_metrics': {
                    'calmar_ratio': round(backtest_result.get('total_return', 0) / abs(backtest_result.get('max_drawdown', 1)), 2),
                    'sortino_ratio': 'N/A',  # Basitleştirilmiş
                    'var_95': 'N/A',  # Basitleştirilmiş
                    'cvar_95': 'N/A'  # Basitleştirilmiş
                },
                'walk_forward_analysis': walk_forward_result if walk_forward_result else 'N/A',
                'parameter_optimization': optimization_result if optimization_result else 'N/A',
                'recommendations': self._generate_backtest_recommendations(backtest_result)
            }
            
            logger.info(f"✅ {symbol} için backtest raporu oluşturuldu")
            return report
            
        except Exception as e:
            logger.error(f"❌ Rapor oluşturma hatası: {e}")
            return {}
    
    def _generate_backtest_recommendations(self, backtest_result: Dict[str, Any]) -> List[str]:
        """Backtest sonuçlarına göre öneriler üret"""
        try:
            recommendations = []
            
            total_return = backtest_result.get('total_return', 0)
            sharpe_ratio = backtest_result.get('sharpe_ratio', 0)
            max_drawdown = backtest_result.get('max_drawdown', 0)
            win_rate = backtest_result.get('win_rate', 0)
            
            # Return analizi
            if total_return > 20:
                recommendations.append("🎯 Yüksek getiri: Strateji başarılı, pozisyon büyütülebilir")
            elif total_return > 10:
                recommendations.append("✅ İyi getiri: Strateji çalışıyor, optimize edilebilir")
            elif total_return > 0:
                recommendations.append("⚠️ Düşük getiri: Strateji iyileştirilmeli")
            else:
                recommendations.append("❌ Negatif getiri: Strateji yeniden tasarlanmalı")
            
            # Risk analizi
            if sharpe_ratio > 1.5:
                recommendations.append("🌟 Mükemmel risk-getiri: Strateji çok iyi")
            elif sharpe_ratio > 1.0:
                recommendations.append("👍 İyi risk-getiri: Strateji kabul edilebilir")
            elif sharpe_ratio > 0.5:
                recommendations.append("⚠️ Düşük risk-getiri: Optimizasyon gerekli")
            else:
                recommendations.append("❌ Kötü risk-getiri: Strateji yeniden değerlendirilmeli")
            
            # Drawdown analizi
            if abs(max_drawdown) < 10:
                recommendations.append("🛡️ Düşük drawdown: Risk yönetimi iyi")
            elif abs(max_drawdown) < 20:
                recommendations.append("⚠️ Orta drawdown: Stop-loss sıkılaştırılabilir")
            else:
                recommendations.append("🚨 Yüksek drawdown: Risk yönetimi iyileştirilmeli")
            
            # Win rate analizi
            if win_rate > 60:
                recommendations.append("🎯 Yüksek win rate: Sinyal kalitesi iyi")
            elif win_rate > 50:
                recommendations.append("✅ Orta win rate: Sinyal kalitesi kabul edilebilir")
            else:
                recommendations.append("⚠️ Düşük win rate: Sinyal kalitesi iyileştirilmeli")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Öneri üretme hatası: {e}")
            return ["Analiz hatası"]

# Test fonksiyonu
if __name__ == "__main__":
    backtest_engine = AutoBacktestWalkForward()
    
    print("🔍 Auto-Backtest & Walk Forward Test")
    print("=" * 50)
    
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
            print(f"   En İyi Sharpe: {optimization_result['best_by_sharpe']['performance']['sharpe_ratio']:.2f}")
        
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
    print("✅ Test tamamlandı!")
