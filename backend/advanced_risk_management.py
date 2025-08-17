"""
PRD v2.0 - Advanced Risk Management
Gelişmiş risk yönetimi: VaR, CVaR, Kelly Criterion, Position Sizing
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedRiskManagement:
    """Gelişmiş risk yönetimi modülü"""
    
    def __init__(self):
        self.risk_metrics = {}
        self.position_sizes = {}
        self.portfolio_risk = {}
        
        # Risk parametreleri
        self.risk_params = {
            "max_portfolio_risk": 0.02,      # %2 maksimum portföy riski
            "max_position_risk": 0.01,       # %1 maksimum pozisyon riski
            "confidence_level": 0.95,        # %95 güven seviyesi
            "risk_free_rate": 0.15,          # %15 risksiz faiz (TCMB)
            "max_drawdown": 0.15,            # %15 maksimum drawdown
            "kelly_fraction": 0.25           # Kelly Criterion fraksiyonu
        }
        
        # Risk metrikleri
        self.risk_metrics_types = {
            "volatility": ["Historical", "EWMA", "GARCH"],
            "var": ["Historical", "Parametric", "Monte Carlo"],
            "cvar": ["Historical", "Parametric"],
            "drawdown": ["Maximum", "Average", "Recovery Time"],
            "correlation": ["Pairwise", "Portfolio", "Market"],
            "beta": ["CAPM", "Multi-Factor", "Conditional"]
        }
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95, method: str = "historical") -> Dict:
        """Value at Risk hesapla"""
        try:
            if method == "historical":
                # Historical VaR
                var = np.percentile(returns, (1 - confidence_level) * 100)
                
            elif method == "parametric":
                # Parametric VaR (normal dağılım varsayımı)
                mean_return = returns.mean()
                std_return = returns.std()
                z_score = stats.norm.ppf(confidence_level)
                var = mean_return - z_score * std_return
                
            elif method == "monte_carlo":
                # Monte Carlo VaR
                n_simulations = 10000
                simulated_returns = np.random.normal(
                    returns.mean(), 
                    returns.std(), 
                    n_simulations
                )
                var = np.percentile(simulated_returns, (1 - confidence_level) * 100)
                
            else:
                raise ValueError(f"Bilinmeyen VaR metodu: {method}")
            
            return {
                "method": method,
                "confidence_level": confidence_level,
                "var": var,
                "var_percentage": abs(var) * 100
            }
            
        except Exception as e:
            logger.error(f"❌ VaR hesaplama hatası: {e}")
            return {"error": str(e)}
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95, method: str = "historical") -> Dict:
        """Conditional Value at Risk hesapla"""
        try:
            if method == "historical":
                # Historical CVaR
                var = np.percentile(returns, (1 - confidence_level) * 100)
                cvar = returns[returns <= var].mean()
                
            elif method == "parametric":
                # Parametric CVaR (normal dağılım varsayımı)
                mean_return = returns.mean()
                std_return = returns.std()
                z_score = stats.norm.ppf(confidence_level)
                var = mean_return - z_score * std_return
                
                # CVaR formülü
                phi_z = stats.norm.pdf(z_score)
                cvar = mean_return - (phi_z / (1 - confidence_level)) * std_return
                
            else:
                raise ValueError(f"Bilinmeyen CVaR metodu: {method}")
            
            return {
                "method": method,
                "confidence_level": confidence_level,
                "var": var,
                "cvar": cvar,
                "cvar_percentage": abs(cvar) * 100
            }
            
        except Exception as e:
            logger.error(f"❌ CVaR hesaplama hatası: {e}")
            return {"error": str(e)}
    
    def calculate_drawdown_metrics(self, prices: pd.Series) -> Dict:
        """Drawdown metrikleri hesapla"""
        try:
            # Cumulative returns
            cumulative_returns = (1 + prices.pct_change()).cumprod()
            
            # Running maximum
            running_max = cumulative_returns.expanding().max()
            
            # Drawdown
            drawdown = (cumulative_returns - running_max) / running_max
            
            # Maximum drawdown
            max_drawdown = drawdown.min()
            
            # Average drawdown
            avg_drawdown = drawdown[drawdown < 0].mean()
            
            # Drawdown duration
            drawdown_periods = (drawdown < 0).sum()
            total_periods = len(drawdown)
            drawdown_frequency = drawdown_periods / total_periods
            
            # Recovery time (basit hesaplama)
            recovery_time = self._calculate_recovery_time(drawdown)
            
            return {
                "max_drawdown": max_drawdown,
                "max_drawdown_percentage": abs(max_drawdown) * 100,
                "avg_drawdown": avg_drawdown,
                "avg_drawdown_percentage": abs(avg_drawdown) * 100,
                "drawdown_frequency": drawdown_frequency,
                "recovery_time_days": recovery_time
            }
            
        except Exception as e:
            logger.error(f"❌ Drawdown hesaplama hatası: {e}")
            return {"error": str(e)}
    
    def _calculate_recovery_time(self, drawdown: pd.Series) -> int:
        """Recovery time hesapla"""
        try:
            recovery_days = 0
            in_drawdown = False
            
            for i, dd in enumerate(drawdown):
                if dd < 0 and not in_drawdown:
                    in_drawdown = True
                    start_idx = i
                elif dd >= 0 and in_drawdown:
                    in_drawdown = False
                    recovery_days = max(recovery_days, i - start_idx)
            
            return recovery_days
        except:
            return 0
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> Dict:
        """Kelly Criterion hesapla"""
        try:
            # Kelly Criterion formülü: f = (bp - q) / b
            # f: optimal position size
            # b: odds received on bet (avg_win / avg_loss)
            # p: probability of winning
            # q: probability of losing (1 - p)
            
            if avg_loss == 0:
                return {"error": "Ortalama kayıp 0 olamaz"}
            
            b = avg_win / avg_loss
            p = win_rate
            q = 1 - p
            
            # Kelly fraction
            kelly_fraction = (b * p - q) / b
            
            # Risk-adjusted Kelly (fractional Kelly)
            risk_adjusted_kelly = kelly_fraction * self.risk_params["kelly_fraction"]
            
            # Position size limits
            max_position = min(risk_adjusted_kelly, self.risk_params["max_position_risk"])
            
            return {
                "win_rate": win_rate,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "odds_ratio": b,
                "kelly_fraction": kelly_fraction,
                "risk_adjusted_kelly": risk_adjusted_kelly,
                "recommended_position_size": max_position,
                "max_position_size": self.risk_params["max_position_risk"]
            }
            
        except Exception as e:
            logger.error(f"❌ Kelly Criterion hatası: {e}")
            return {"error": str(e)}
    
    def calculate_position_sizing(self, symbol: str, confidence: float, risk_per_trade: float) -> Dict:
        """Pozisyon boyutlandırma hesapla"""
        try:
            # Risk-based position sizing
            # Position Size = Risk Amount / (Entry Price - Stop Loss)
            
            # Hisse verisi
            stock = yf.Ticker(symbol)
            data = stock.history(period="6mo")
            
            if data.empty:
                return {"error": "Hisse verisi bulunamadı"}
            
            current_price = data['Close'].iloc[-1]
            
            # ATR-based stop loss
            atr = data['Close'].pct_change().rolling(14).std() * np.sqrt(252)
            atr_value = atr.iloc[-1] * current_price
            
            # Stop loss seviyeleri
            tight_stop = current_price - (atr_value * 1.5)      # Sıkı stop
            normal_stop = current_price - (atr_value * 2.5)     # Normal stop
            wide_stop = current_price - (atr_value * 4.0)       # Geniş stop
            
            # Risk hesaplamaları
            risk_amounts = {}
            for stop_type, stop_price in [("tight", tight_stop), ("normal", normal_stop), ("wide", wide_stop)]:
                if stop_price > 0:
                    risk_per_share = current_price - stop_price
                    if risk_per_share > 0:
                        position_size = risk_per_trade / risk_per_share
                        risk_amounts[stop_type] = {
                            "stop_price": stop_price,
                            "risk_per_share": risk_per_share,
                            "position_size": position_size,
                            "position_value": position_size * current_price
                        }
            
            # Confidence-based adjustment
            confidence_multiplier = confidence / 0.5  # 0.5 = %50 confidence baseline
            adjusted_position_sizes = {}
            
            for stop_type, risk_data in risk_amounts.items():
                adjusted_size = risk_data["position_size"] * confidence_multiplier
                adjusted_position_sizes[stop_type] = {
                    **risk_data,
                    "adjusted_position_size": adjusted_size,
                    "adjusted_position_value": adjusted_size * current_price
                }
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "atr": atr_value,
                "risk_per_trade": risk_per_trade,
                "confidence": confidence,
                "confidence_multiplier": confidence_multiplier,
                "stop_loss_levels": {
                    "tight": tight_stop,
                    "normal": normal_stop,
                    "wide": wide_stop
                },
                "position_sizing": adjusted_position_sizes,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Pozisyon boyutlandırma hatası: {e}")
            return {"error": str(e)}
    
    def calculate_portfolio_risk(self, portfolio: Dict[str, float], symbols: List[str]) -> Dict:
        """Portföy riski hesapla"""
        try:
            # Portföy ağırlıkları
            weights = np.array(list(portfolio.values()))
            
            if len(weights) != len(symbols):
                return {"error": "Portföy ve sembol sayısı uyuşmuyor"}
            
            # Normalize weights
            weights = weights / weights.sum()
            
            # Correlation matrix
            returns_data = {}
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    data = stock.history(period="1y")
                    if not data.empty:
                        returns_data[symbol] = data['Close'].pct_change().dropna()
                except:
                    continue
            
            if len(returns_data) < 2:
                return {"error": "Yeterli veri bulunamadı"}
            
            # Returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 30:
                return {"error": "Yeterli veri noktası yok"}
            
            # Correlation matrix
            correlation_matrix = returns_df.corr()
            
            # Covariance matrix
            covariance_matrix = returns_df.cov()
            
            # Portfolio variance
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Portfolio VaR
            portfolio_var = self.calculate_var(returns_df.dot(weights), self.risk_params["confidence_level"])
            
            # Portfolio CVaR
            portfolio_cvar = self.calculate_cvar(returns_df.dot(weights), self.risk_params["confidence_level"])
            
            # Beta calculation (market proxy olarak XU030)
            try:
                xu030 = yf.Ticker("^XU030")
                xu030_data = xu030.history(period="1y")
                if not xu030_data.empty:
                    market_returns = xu030_data['Close'].pct_change().dropna()
                    
                    # Portfolio returns
                    portfolio_returns = returns_df.dot(weights)
                    portfolio_returns = portfolio_returns.dropna()
                    
                    # Align data
                    common_index = portfolio_returns.index.intersection(market_returns.index)
                    if len(common_index) > 30:
                        portfolio_returns = portfolio_returns[common_index]
                        market_returns = market_returns[common_index]
                        
                        # Beta calculation
                        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
                        market_variance = np.var(market_returns)
                        portfolio_beta = covariance / market_variance
                    else:
                        portfolio_beta = 1.0
                else:
                    portfolio_beta = 1.0
            except:
                portfolio_beta = 1.0
            
            # Risk-adjusted returns
            risk_free_rate = self.risk_params["risk_free_rate"]
            portfolio_return = returns_df.dot(weights).mean() * 252  # Annualized
            
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Maximum position concentration
            max_concentration = weights.max()
            
            return {
                "portfolio_weights": dict(zip(symbols, weights)),
                "portfolio_volatility": portfolio_volatility,
                "portfolio_var": portfolio_var,
                "portfolio_cvar": portfolio_cvar,
                "portfolio_beta": portfolio_beta,
                "portfolio_return": portfolio_return,
                "sharpe_ratio": sharpe_ratio,
                "max_concentration": max_concentration,
                "correlation_matrix": correlation_matrix.to_dict(),
                "risk_metrics": {
                    "volatility": portfolio_volatility,
                    "var": portfolio_var.get("var", 0),
                    "cvar": portfolio_cvar.get("cvar", 0),
                    "beta": portfolio_beta,
                    "sharpe": sharpe_ratio
                },
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Portföy riski hatası: {e}")
            return {"error": str(e)}
    
    def optimize_portfolio_weights(self, symbols: List[str], target_return: float = None, max_risk: float = None) -> Dict:
        """Portföy ağırlıklarını optimize et"""
        try:
            # Returns data
            returns_data = {}
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    data = stock.history(period="1y")
                    if not data.empty:
                        returns_data[symbol] = data['Close'].pct_change().dropna()
                except:
                    continue
            
            if len(returns_data) < 2:
                return {"error": "Yeterli veri bulunamadı"}
            
            # Returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 30:
                return {"error": "Yeterli veri noktası yok"}
            
            # Expected returns
            expected_returns = returns_df.mean() * 252
            
            # Covariance matrix
            covariance_matrix = returns_df.cov() * 252
            
            # Optimization function
            def portfolio_volatility(weights):
                return np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            
            def portfolio_return(weights):
                return np.sum(expected_returns * weights)
            
            # Constraints
            n_assets = len(symbols)
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            if target_return is not None:
                constraints.append({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target_return})
            
            # Bounds (0 <= weight <= 1)
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Initial guess (equal weights)
            initial_weights = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                portfolio_volatility,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                return {"error": "Optimizasyon başarısız"}
            
            optimal_weights = result.x
            optimal_volatility = portfolio_volatility(optimal_weights)
            optimal_return = portfolio_return(optimal_weights)
            
            # Risk metrics
            portfolio_risk = self.calculate_portfolio_risk(
                dict(zip(symbols, optimal_weights)),
                symbols
            )
            
            return {
                "optimization_success": True,
                "optimal_weights": dict(zip(symbols, optimal_weights)),
                "optimal_volatility": optimal_volatility,
                "optimal_return": optimal_return,
                "sharpe_ratio": (optimal_return - self.risk_params["risk_free_rate"]) / optimal_volatility,
                "portfolio_risk": portfolio_risk,
                "constraints": {
                    "target_return": target_return,
                    "max_risk": max_risk
                },
                "optimization_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Portföy optimizasyon hatası: {e}")
            return {"error": str(e)}

# Test fonksiyonu
if __name__ == "__main__":
    risk_manager = AdvancedRiskManagement()
    
    # Test hissesi
    symbol = "GARAN.IS"
    logger.info(f"🧪 {symbol} için risk yönetimi test ediliyor...")
    
    # Test portföy
    test_portfolio = {"GARAN.IS": 0.4, "AKBNK.IS": 0.3, "ASELS.IS": 0.3}
    test_symbols = list(test_portfolio.keys())
    
    # Risk metrikleri
    logger.info("✅ Advanced Risk Management modülü hazır!")
    logger.info(f"📊 Risk parametreleri: {risk_manager.risk_params}")
    logger.info(f"🔧 Risk metrik türleri: {list(risk_manager.risk_metrics_types.keys())}")
    
    # Portföy riski test
    portfolio_risk = risk_manager.calculate_portfolio_risk(test_portfolio, test_symbols)
    if "error" not in portfolio_risk:
        logger.info(f"📈 Portföy volatilitesi: {portfolio_risk['portfolio_volatility']:.4f}")
        logger.info(f"📊 Portföy Sharpe oranı: {portfolio_risk['sharpe_ratio']:.4f}")
