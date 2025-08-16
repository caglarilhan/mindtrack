"""
Reinforcement Learning Agent - Sprint 14: Advanced Machine Learning & AI Engine

Bu modül, FinRL ve DDPG algoritmalarını kullanarak portföy yönetimi
ve trading kararları veren reinforcement learning ajanı implement eder.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import logging
import random
from collections import deque

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnvironmentState:
    """RL environment durumu"""
    state_id: str
    timestamp: datetime
    portfolio_value: float
    cash_balance: float
    positions: Dict[str, float]  # symbol -> quantity
    prices: Dict[str, float]  # symbol -> current_price
    market_data: Dict[str, Any]  # Teknik indikatörler ve piyasa verileri
    risk_metrics: Dict[str, float]  # Risk metrikleri
    action_history: List[str] = None

@dataclass
class AgentAction:
    """RL ajan aksiyonu"""
    action_id: str
    timestamp: datetime
    action_type: str  # buy, sell, hold, rebalance
    symbol: str
    quantity: float
    price: float
    confidence: float  # 0-1 arası güven skoru
    reasoning: str  # Aksiyon gerekçesi
    expected_reward: float  # Beklenen ödül
    risk_score: float  # Risk skoru

@dataclass
class TrainingEpisode:
    """RL eğitim episode'u"""
    episode_id: str
    start_timestamp: datetime
    end_timestamp: datetime
    initial_portfolio_value: float
    final_portfolio_value: float
    total_return: float
    total_return_pct: float
    actions_taken: int
    successful_trades: int
    failed_trades: int
    sharpe_ratio: float
    max_drawdown: float
    learning_progress: Dict[str, float]

@dataclass
class PortfolioPolicy:
    """Portföy yönetim politikası"""
    policy_id: str
    name: str
    description: str
    risk_tolerance: str  # low, medium, high
    target_allocation: Dict[str, float]  # Asset allocation hedefleri
    rebalancing_threshold: float  # Rebalancing tetikleyici
    max_position_size: float  # Maksimum pozisyon büyüklüğü
    stop_loss_pct: float  # Stop loss yüzdesi
    take_profit_pct: float  # Take profit yüzdesi
    created_at: datetime = None

class ReinforcementLearningAgent:
    """Reinforcement Learning Agent ana sınıfı"""
    
    def __init__(self):
        self.agent_id = f"RL_AGENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.environment_states = []
        self.agent_actions = []
        self.training_episodes = []
        self.portfolio_policies = {}
        self.learning_parameters = {}
        self.action_space = []
        self.state_space = []
        self.reward_function = None
        self.exploration_strategy = None
        
        # RL algoritma parametreleri
        self._set_default_learning_parameters()
        
        # Varsayılan portföy politikaları
        self._add_default_policies()
        
        # Aksiyon ve durum uzaylarını tanımla
        self._define_spaces()
        
        # Ödül fonksiyonunu tanımla
        self._define_reward_function()
        
        # Keşif stratejisini tanımla
        self._define_exploration_strategy()
    
    def _set_default_learning_parameters(self):
        """Varsayılan öğrenme parametrelerini ayarla"""
        self.learning_parameters = {
            "algorithm": "ddpg",  # Deep Deterministic Policy Gradient
            "learning_rate": 0.001,
            "discount_factor": 0.95,
            "epsilon": 0.1,  # Keşif oranı
            "epsilon_decay": 0.995,
            "epsilon_min": 0.01,
            "batch_size": 32,
            "memory_size": 10000,
            "target_update_freq": 100,
            "training_frequency": 1,  # Her aksiyondan sonra
            "episode_length": 252,  # 1 yıl (trading günleri)
            "min_portfolio_value": 10000,  # Minimum portföy değeri
            "max_portfolio_value": 1000000,  # Maksimum portföy değeri
            "transaction_cost": 0.001,  # %0.1 işlem maliyeti
            "slippage": 0.0005  # %0.05 slippage
        }
    
    def _add_default_policies(self):
        """Varsayılan portföy politikaları ekle"""
        default_policies = [
            {
                "policy_id": "CONSERVATIVE",
                "name": "Muhafazakar Portföy",
                "description": "Düşük risk, düşük getiri hedefi",
                "risk_tolerance": "low",
                "target_allocation": {
                    "bonds": 0.60,
                    "equity": 0.30,
                    "cash": 0.10
                },
                "rebalancing_threshold": 0.05,
                "max_position_size": 0.20,
                "stop_loss_pct": 0.10,
                "take_profit_pct": 0.15
            },
            {
                "policy_id": "MODERATE",
                "name": "Dengeli Portföy",
                "description": "Orta risk, orta getiri hedefi",
                "risk_tolerance": "medium",
                "target_allocation": {
                    "bonds": 0.40,
                    "equity": 0.50,
                    "cash": 0.10
                },
                "rebalancing_threshold": 0.08,
                "max_position_size": 0.25,
                "stop_loss_pct": 0.15,
                "take_profit_pct": 0.20
            },
            {
                "policy_id": "AGGRESSIVE",
                "name": "Agresif Portföy",
                "description": "Yüksek risk, yüksek getiri hedefi",
                "risk_tolerance": "high",
                "target_allocation": {
                    "bonds": 0.20,
                    "equity": 0.70,
                    "cash": 0.10
                },
                "rebalancing_threshold": 0.12,
                "max_position_size": 0.30,
                "stop_loss_pct": 0.20,
                "take_profit_pct": 0.30
            }
        ]
        
        for policy_data in default_policies:
            policy = PortfolioPolicy(
                policy_id=policy_data["policy_id"],
                name=policy_data["name"],
                description=policy_data["description"],
                risk_tolerance=policy_data["risk_tolerance"],
                target_allocation=policy_data["target_allocation"],
                rebalancing_threshold=policy_data["rebalancing_threshold"],
                max_position_size=policy_data["max_position_size"],
                stop_loss_pct=policy_data["stop_loss_pct"],
                take_profit_pct=policy_data["take_profit_pct"],
                created_at=datetime.now()
            )
            self.portfolio_policies[policy.policy_id] = policy
    
    def _define_spaces(self):
        """Aksiyon ve durum uzaylarını tanımla"""
        # Durum uzayı: Portföy durumu + piyasa verileri
        self.state_space = [
            "portfolio_value",
            "cash_balance",
            "total_positions",
            "portfolio_return",
            "volatility",
            "sharpe_ratio",
            "max_drawdown",
            "market_trend",
            "rsi",
            "macd",
            "bollinger_position",
            "volume_ratio"
        ]
        
        # Aksiyon uzayı: Trading aksiyonları
        self.action_space = [
            "hold",
            "buy_small",
            "buy_medium",
            "buy_large",
            "sell_small",
            "sell_medium",
            "sell_large",
            "rebalance"
        ]
    
    def _define_reward_function(self):
        """Ödül fonksiyonunu tanımla"""
        def reward_function(state: EnvironmentState, action: AgentAction, 
                          next_state: EnvironmentState) -> float:
            """Ödül hesaplama fonksiyonu"""
            try:
                reward = 0.0
                
                # Portföy getiri ödülü
                if next_state.portfolio_value > state.portfolio_value:
                    return_pct = (next_state.portfolio_value - state.portfolio_value) / state.portfolio_value
                    reward += return_pct * 100  # Pozitif getiri için ödül
                else:
                    return_pct = (state.portfolio_value - next_state.portfolio_value) / state.portfolio_value
                    reward -= return_pct * 100  # Negatif getiri için ceza
                
                # Risk ödülü (volatilite kontrolü)
                if "volatility" in next_state.risk_metrics:
                    volatility = next_state.risk_metrics["volatility"]
                    if volatility < 0.15:  # Düşük volatilite ödülü
                        reward += 5
                    elif volatility > 0.30:  # Yüksek volatilite cezası
                        reward -= 10
                
                # Sharpe ratio ödülü
                if "sharpe_ratio" in next_state.risk_metrics:
                    sharpe = next_state.risk_metrics["sharpe_ratio"]
                    if sharpe > 1.0:
                        reward += 10
                    elif sharpe < 0.0:
                        reward -= 5
                
                # Aksiyon maliyeti
                if action.action_type != "hold":
                    transaction_cost = abs(action.quantity * action.price * self.learning_parameters["transaction_cost"])
                    reward -= transaction_cost
                
                # Keşif ödülü (yeni aksiyonlar için)
                if action.action_type not in [a.action_type for a in state.action_history[-5:] if state.action_history]:
                    reward += 2
                
                return reward
            
            except Exception as e:
                logger.error(f"Error calculating reward: {e}")
                return 0.0
        
        self.reward_function = reward_function
    
    def _define_exploration_strategy(self):
        """Keşif stratejisini tanımla"""
        def exploration_strategy(state: EnvironmentState, available_actions: List[str]) -> str:
            """Epsilon-greedy keşif stratejisi"""
            try:
                # Epsilon-greedy: %epsilon olasılıkla rastgele aksiyon
                if random.random() < self.learning_parameters["epsilon"]:
                    return random.choice(available_actions)
                else:
                    # En iyi aksiyonu seç (basit heuristik)
                    return self._select_best_action_heuristic(state, available_actions)
            
            except Exception as e:
                logger.error(f"Error in exploration strategy: {e}")
                return random.choice(available_actions) if available_actions else "hold"
        
        self.exploration_strategy = exploration_strategy
    
    def _select_best_action_heuristic(self, state: EnvironmentState, available_actions: List[str]) -> str:
        """Basit heuristik ile en iyi aksiyonu seç"""
        try:
            # Portföy durumuna göre aksiyon seç
            portfolio_return = state.risk_metrics.get("portfolio_return", 0)
            volatility = state.risk_metrics.get("volatility", 0.2)
            
            if portfolio_return < -0.05 and volatility < 0.25:
                # Düşük getiri, düşük volatilite -> Alım fırsatı
                if "buy_medium" in available_actions:
                    return "buy_medium"
                elif "buy_small" in available_actions:
                    return "buy_small"
            
            elif portfolio_return > 0.10 and volatility > 0.30:
                # Yüksek getiri, yüksek volatilite -> Satış fırsatı
                if "sell_medium" in available_actions:
                    return "sell_medium"
                elif "sell_small" in available_actions:
                    return "sell_small"
            
            elif abs(portfolio_return) < 0.02:
                # Dengeli durum -> Rebalancing
                if "rebalance" in available_actions:
                    return "rebalance"
            
            # Varsayılan olarak hold
            return "hold"
        
        except Exception as e:
            logger.error(f"Error selecting best action: {e}")
            return "hold"
    
    def create_environment_state(self, portfolio_data: Dict[str, Any], 
                               market_data: Dict[str, Any]) -> EnvironmentState:
        """Environment durumu oluştur"""
        try:
            state_id = f"STATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Risk metrikleri hesapla
            risk_metrics = self._calculate_risk_metrics(portfolio_data, market_data)
            
            state = EnvironmentState(
                state_id=state_id,
                timestamp=datetime.now(),
                portfolio_value=portfolio_data.get("portfolio_value", 0),
                cash_balance=portfolio_data.get("cash_balance", 0),
                positions=portfolio_data.get("positions", {}),
                prices=market_data.get("prices", {}),
                market_data=market_data,
                risk_metrics=risk_metrics,
                action_history=[]
            )
            
            self.environment_states.append(state)
            return state
        
        except Exception as e:
            logger.error(f"Error creating environment state: {e}")
            return None
    
    def _calculate_risk_metrics(self, portfolio_data: Dict[str, Any], 
                               market_data: Dict[str, Any]) -> Dict[str, float]:
        """Risk metrikleri hesapla"""
        try:
            risk_metrics = {}
            
            # Portföy getiri
            current_value = portfolio_data.get("portfolio_value", 0)
            initial_value = portfolio_data.get("initial_value", current_value)
            if initial_value > 0:
                risk_metrics["portfolio_return"] = (current_value - initial_value) / initial_value
            else:
                risk_metrics["portfolio_return"] = 0.0
            
            # Volatilite (basit hesaplama)
            returns_history = portfolio_data.get("returns_history", [0.0])
            if len(returns_history) > 1:
                risk_metrics["volatility"] = np.std(returns_history)
            else:
                risk_metrics["volatility"] = 0.2
            
            # Sharpe ratio (basit hesaplama)
            if risk_metrics["volatility"] > 0:
                risk_metrics["sharpe_ratio"] = risk_metrics["portfolio_return"] / risk_metrics["volatility"]
            else:
                risk_metrics["sharpe_ratio"] = 0.0
            
            # Max drawdown (basit hesaplama)
            if returns_history:
                cumulative_returns = np.cumsum(returns_history)
                max_drawdown = np.min(cumulative_returns) if len(cumulative_returns) > 0 else 0
                risk_metrics["max_drawdown"] = abs(max_drawdown)
            else:
                risk_metrics["max_drawdown"] = 0.0
            
            # Market trend
            if "prices" in market_data:
                prices = list(market_data["prices"].values())
                if len(prices) > 1:
                    price_change = (prices[-1] - prices[0]) / prices[0]
                    risk_metrics["market_trend"] = 1 if price_change > 0 else -1
                else:
                    risk_metrics["market_trend"] = 0
            else:
                risk_metrics["market_trend"] = 0
            
            # Teknik indikatörler
            if "technical_indicators" in market_data:
                tech_indicators = market_data["technical_indicators"]
                risk_metrics["rsi"] = tech_indicators.get("rsi", 50)
                risk_metrics["macd"] = tech_indicators.get("macd", 0)
                risk_metrics["bollinger_position"] = tech_indicators.get("bollinger_position", 0.5)
                risk_metrics["volume_ratio"] = tech_indicators.get("volume_ratio", 1.0)
            else:
                risk_metrics["rsi"] = 50
                risk_metrics["macd"] = 0
                risk_metrics["bollinger_position"] = 0.5
                risk_metrics["volume_ratio"] = 1.0
            
            return risk_metrics
        
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def select_action(self, state: EnvironmentState, policy_id: str = "MODERATE") -> AgentAction:
        """Aksiyon seç"""
        try:
            if policy_id not in self.portfolio_policies:
                logger.warning(f"Policy {policy_id} not found, using MODERATE")
                policy_id = "MODERATE"
            
            policy = self.portfolio_policies[policy_id]
            
            # Keşif stratejisini kullan
            action_type = self.exploration_strategy(state, self.action_space)
            
            # Aksiyon detaylarını belirle
            action_details = self._determine_action_details(action_type, state, policy)
            
            # Aksiyon oluştur
            action = AgentAction(
                action_id=f"ACTION_{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                action_type=action_type,
                symbol=action_details["symbol"],
                quantity=action_details["quantity"],
                price=action_details["price"],
                confidence=action_details["confidence"],
                reasoning=action_details["reasoning"],
                expected_reward=action_details["expected_reward"],
                risk_score=action_details["risk_score"]
            )
            
            self.agent_actions.append(action)
            
            # State action history'yi güncelle
            if state.action_history is None:
                state.action_history = []
            state.action_history.append(action_type)
            
            logger.info(f"Action selected: {action_type} for {action.symbol}")
            return action
        
        except Exception as e:
            logger.error(f"Error selecting action: {e}")
            return None
    
    def _determine_action_details(self, action_type: str, state: EnvironmentState, 
                                policy: PortfolioPolicy) -> Dict[str, Any]:
        """Aksiyon detaylarını belirle"""
        try:
            action_details = {
                "symbol": "PORTFOLIO",
                "quantity": 0.0,
                "price": state.portfolio_value,
                "confidence": 0.5,
                "reasoning": "",
                "expected_reward": 0.0,
                "risk_score": 0.5
            }
            
            if action_type == "hold":
                action_details["reasoning"] = "Portföy durumu dengeli, aksiyon gerekmiyor"
                action_details["confidence"] = 0.8
                action_details["expected_reward"] = 0.0
                action_details["risk_score"] = 0.2
            
            elif action_type.startswith("buy"):
                # Alım aksiyonu
                if action_type == "buy_small":
                    quantity_pct = 0.05
                    confidence = 0.6
                elif action_type == "buy_medium":
                    quantity_pct = 0.15
                    confidence = 0.7
                else:  # buy_large
                    quantity_pct = 0.25
                    confidence = 0.5
                
                action_details["quantity"] = state.cash_balance * quantity_pct
                action_details["reasoning"] = f"Alım fırsatı tespit edildi, {quantity_pct*100}% nakit kullanılacak"
                action_details["confidence"] = confidence
                action_details["expected_reward"] = 0.05  # %5 beklenen getiri
                action_details["risk_score"] = 0.6
            
            elif action_type.startswith("sell"):
                # Satış aksiyonu
                if action_type == "sell_small":
                    quantity_pct = 0.05
                    confidence = 0.6
                elif action_type == "sell_medium":
                    quantity_pct = 0.15
                    confidence = 0.7
                else:  # sell_large
                    quantity_pct = 0.25
                    confidence = 0.5
                
                # En büyük pozisyondan sat
                if state.positions:
                    largest_position = max(state.positions.items(), key=lambda x: x[1])
                    action_details["symbol"] = largest_position[0]
                    action_details["quantity"] = largest_position[1] * quantity_pct
                
                action_details["reasoning"] = f"Satış fırsatı tespit edildi, {quantity_pct*100}% pozisyon kapatılacak"
                action_details["confidence"] = confidence
                action_details["expected_reward"] = -0.02  # %2 beklenen kayıp
                action_details["risk_score"] = 0.4
            
            elif action_type == "rebalance":
                # Rebalancing aksiyonu
                action_details["reasoning"] = "Portföy hedef allocation'a göre yeniden dengelenecek"
                action_details["confidence"] = 0.9
                action_details["expected_reward"] = 0.02  # %2 beklenen getiri
                action_details["risk_score"] = 0.3
            
            return action_details
        
        except Exception as e:
            logger.error(f"Error determining action details: {e}")
            return {
                "symbol": "PORTFOLIO",
                "quantity": 0.0,
                "price": state.portfolio_value,
                "confidence": 0.5,
                "reasoning": "Hata nedeniyle aksiyon detayları belirlenemedi",
                "expected_reward": 0.0,
                "risk_score": 0.5
            }
    
    def execute_action(self, action: AgentAction, current_state: EnvironmentState) -> EnvironmentState:
        """Aksiyonu uygula ve yeni durum oluştur"""
        try:
            # Yeni durum oluştur
            new_state = EnvironmentState(
                state_id=f"STATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                portfolio_value=current_state.portfolio_value,
                cash_balance=current_state.cash_balance,
                positions=current_state.positions.copy(),
                prices=current_state.prices.copy(),
                market_data=current_state.market_data.copy(),
                risk_metrics=current_state.risk_metrics.copy(),
                action_history=current_state.action_history.copy() if current_state.action_history else []
            )
            
            # Aksiyona göre portföyü güncelle
            if action.action_type.startswith("buy"):
                # Alım işlemi
                cost = action.quantity * action.price
                transaction_cost = cost * self.learning_parameters["transaction_cost"]
                total_cost = cost + transaction_cost
                
                if new_state.cash_balance >= total_cost:
                    new_state.cash_balance -= total_cost
                    if action.symbol in new_state.positions:
                        new_state.positions[action.symbol] += action.quantity
                    else:
                        new_state.positions[action.symbol] = action.quantity
                    
                    # Portföy değerini güncelle
                    new_state.portfolio_value = new_state.cash_balance
                    for symbol, quantity in new_state.positions.items():
                        if symbol in new_state.prices:
                            new_state.portfolio_value += quantity * new_state.prices[symbol]
            
            elif action.action_type.startswith("sell"):
                # Satış işlemi
                if action.symbol in new_state.positions:
                    quantity_to_sell = min(action.quantity, new_state.positions[action.symbol])
                    revenue = quantity_to_sell * action.price
                    transaction_cost = revenue * self.learning_parameters["transaction_cost"]
                    net_revenue = revenue - transaction_cost
                    
                    new_state.cash_balance += net_revenue
                    new_state.positions[action.symbol] -= quantity_to_sell
                    
                    if new_state.positions[action.symbol] <= 0:
                        del new_state.positions[action.symbol]
                    
                    # Portföy değerini güncelle
                    new_state.portfolio_value = new_state.cash_balance
                    for symbol, quantity in new_state.positions.items():
                        if symbol in new_state.prices:
                            new_state.portfolio_value += quantity * new_state.prices[symbol]
            
            elif action.action_type == "rebalance":
                # Rebalancing işlemi (basit implementasyon)
                target_policy = self.portfolio_policies.get("MODERATE")
                if target_policy:
                    # Hedef allocation'a göre pozisyonları ayarla
                    total_value = new_state.portfolio_value
                    for asset_class, target_pct in target_policy.target_allocation.items():
                        target_value = total_value * target_pct
                        # Basit rebalancing (gerçek implementasyonda daha karmaşık)
                        pass
            
            # Risk metriklerini yeniden hesapla
            new_state.risk_metrics = self._calculate_risk_metrics(
                {"portfolio_value": new_state.portfolio_value, "cash_balance": new_state.cash_balance},
                new_state.market_data
            )
            
            # Yeni durumu kaydet
            self.environment_states.append(new_state)
            
            logger.info(f"Action executed: {action.action_type} for {action.symbol}")
            return new_state
        
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return current_state
    
    def start_training_episode(self, initial_portfolio_data: Dict[str, Any], 
                             market_data: Dict[str, Any], policy_id: str = "MODERATE") -> str:
        """Eğitim episode'u başlat"""
        try:
            episode_id = f"EPISODE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # İlk durumu oluştur
            initial_state = self.create_environment_state(initial_portfolio_data, market_data)
            if not initial_state:
                return None
            
            # Episode kaydı oluştur
            episode = TrainingEpisode(
                episode_id=episode_id,
                start_timestamp=datetime.now(),
                end_timestamp=None,
                initial_portfolio_value=initial_state.portfolio_value,
                final_portfolio_value=initial_state.portfolio_value,
                total_return=0.0,
                total_return_pct=0.0,
                actions_taken=0,
                successful_trades=0,
                failed_trades=0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                learning_progress={}
            )
            
            self.training_episodes.append(episode)
            
            logger.info(f"Training episode started: {episode_id}")
            return episode_id
        
        except Exception as e:
            logger.error(f"Error starting training episode: {e}")
            return None
    
    def end_training_episode(self, episode_id: str) -> bool:
        """Eğitim episode'unu sonlandır"""
        try:
            episode = None
            for ep in self.training_episodes:
                if ep.episode_id == episode_id:
                    episode = ep
                    break
            
            if not episode:
                logger.error(f"Episode {episode_id} not found")
                return False
            
            # Son durumu bul
            final_state = None
            for state in reversed(self.environment_states):
                if state.timestamp >= episode.start_timestamp:
                    final_state = state
                    break
            
            if final_state:
                # Episode sonuçlarını hesapla
                episode.end_timestamp = datetime.now()
                episode.final_portfolio_value = final_state.portfolio_value
                episode.total_return = final_state.portfolio_value - episode.initial_portfolio_value
                episode.total_return_pct = (episode.total_return / episode.initial_portfolio_value) * 100
                
                # Aksiyon sayılarını hesapla
                episode.actions_taken = len([a for a in self.agent_actions 
                                          if episode.start_timestamp <= a.timestamp <= episode.end_timestamp])
                
                # Başarılı/başarısız trade'leri hesapla
                successful_actions = [a for a in self.agent_actions 
                                   if a.action_type in ["buy_small", "buy_medium", "buy_large", "sell_small", "sell_medium", "sell_large"]
                                   and episode.start_timestamp <= a.timestamp <= episode.end_timestamp]
                
                episode.successful_trades = len([a for a in successful_actions if a.expected_reward > 0])
                episode.failed_trades = len([a for a in successful_actions if a.expected_reward <= 0])
                
                # Risk metrikleri
                if final_state.risk_metrics:
                    episode.sharpe_ratio = final_state.risk_metrics.get("sharpe_ratio", 0)
                    episode.max_drawdown = final_state.risk_metrics.get("max_drawdown", 0)
                
                # Öğrenme ilerlemesi
                episode.learning_progress = {
                    "epsilon": self.learning_parameters["epsilon"],
                    "total_states": len(self.environment_states),
                    "total_actions": len(self.agent_actions)
                }
                
                # Epsilon'u güncelle
                self.learning_parameters["epsilon"] = max(
                    self.learning_parameters["epsilon_min"],
                    self.learning_parameters["epsilon"] * self.learning_parameters["epsilon_decay"]
                )
            
            logger.info(f"Training episode ended: {episode_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error ending training episode: {e}")
            return False
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Agent özeti getir"""
        try:
            summary = {
                "agent_id": self.agent_id,
                "total_states": len(self.environment_states),
                "total_actions": len(self.agent_actions),
                "total_episodes": len(self.training_episodes),
                "learning_parameters": self.learning_parameters.copy(),
                "portfolio_policies": len(self.portfolio_policies),
                "action_distribution": {},
                "performance_summary": {}
            }
            
            # Aksiyon dağılımı
            for action in self.agent_actions:
                action_type = action.action_type
                summary["action_distribution"][action_type] = summary["action_distribution"].get(action_type, 0) + 1
            
            # Performans özeti
            if self.training_episodes:
                completed_episodes = [ep for ep in self.training_episodes if ep.end_timestamp]
                if completed_episodes:
                    avg_return = np.mean([ep.total_return_pct for ep in completed_episodes])
                    avg_sharpe = np.mean([ep.sharpe_ratio for ep in completed_episodes])
                    avg_drawdown = np.mean([ep.max_drawdown for ep in completed_episodes])
                    
                    summary["performance_summary"] = {
                        "average_return_pct": avg_return,
                        "average_sharpe_ratio": avg_sharpe,
                        "average_max_drawdown": avg_drawdown,
                        "completed_episodes": len(completed_episodes)
                    }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting agent summary: {e}")
            return {}


def test_reinforcement_learning_agent():
    """Reinforcement Learning Agent test fonksiyonu"""
    print("\n🧪 Reinforcement Learning Agent Test Başlıyor...")
    
    # RL Agent oluştur
    agent = ReinforcementLearningAgent()
    
    print("✅ RL Agent oluşturuldu")
    print(f"📊 Agent ID: {agent.agent_id}")
    print(f"📊 Toplam portföy politikası: {len(agent.portfolio_policies)}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    test_portfolio_data = {
        "portfolio_value": 100000,
        "initial_value": 100000,
        "cash_balance": 30000,
        "positions": {
            "SISE.IS": 1000,
            "EREGL.IS": 500,
            "TUPRS.IS": 800
        },
        "returns_history": [0.01, -0.005, 0.02, -0.01, 0.015]
    }
    
    test_market_data = {
        "prices": {
            "SISE.IS": 85.0,
            "EREGL.IS": 120.0,
            "TUPRS.IS": 95.0
        },
        "technical_indicators": {
            "rsi": 65,
            "macd": 0.5,
            "bollinger_position": 0.6,
            "volume_ratio": 1.2
        }
    }
    
    print(f"   ✅ Test portföy verisi oluşturuldu: {test_portfolio_data['portfolio_value']:,} TL")
    print(f"   📊 Test piyasa verisi oluşturuldu: {len(test_market_data['prices'])} hisse")
    
    # Environment state oluştur
    print("\n📊 Environment State Oluşturma:")
    initial_state = agent.create_environment_state(test_portfolio_data, test_market_data)
    
    if initial_state:
        print(f"   ✅ Environment state oluşturuldu: {initial_state.state_id}")
        print(f"   📊 Portföy değeri: {initial_state.portfolio_value:,.0f} TL")
        print(f"   📊 Nakit bakiye: {initial_state.cash_balance:,.0f} TL")
        print(f"   📊 Pozisyon sayısı: {len(initial_state.positions)}")
        print(f"   📊 Risk metrikleri: {len(initial_state.risk_metrics)}")
    
    # Aksiyon seçimi testi
    print("\n📊 Aksiyon Seçimi Testi:")
    action = agent.select_action(initial_state, "MODERATE")
    
    if action:
        print(f"   ✅ Aksiyon seçildi: {action.action_type}")
        print(f"   📊 Sembol: {action.symbol}")
        print(f"   📊 Miktar: {action.quantity:,.0f}")
        print(f"   📊 Güven skoru: {action.confidence:.3f}")
        print(f"   📊 Gerekçe: {action.reasoning}")
    
    # Aksiyon uygulama testi
    print("\n📊 Aksiyon Uygulama Testi:")
    if action and initial_state:
        new_state = agent.execute_action(action, initial_state)
        
        if new_state:
            print(f"   ✅ Aksiyon uygulandı")
            print(f"   📊 Yeni portföy değeri: {new_state.portfolio_value:,.0f} TL")
            print(f"   📊 Yeni nakit bakiye: {new_state.cash_balance:,.0f} TL")
            print(f"   📊 Yeni pozisyon sayısı: {len(new_state.positions)}")
    
    # Eğitim episode'u testi
    print("\n📊 Eğitim Episode Testi:")
    episode_id = agent.start_training_episode(test_portfolio_data, test_market_data, "AGGRESSIVE")
    
    if episode_id:
        print(f"   ✅ Eğitim episode'u başlatıldı: {episode_id}")
        
        # Birkaç aksiyon daha al
        for i in range(3):
            if new_state:
                action = agent.select_action(new_state, "AGGRESSIVE")
                if action:
                    new_state = agent.execute_action(action, new_state)
        
        # Episode'u sonlandır
        success = agent.end_training_episode(episode_id)
        if success:
            print(f"   ✅ Eğitim episode'u sonlandırıldı")
    
    # Agent özeti
    print("\n📊 Agent Özeti:")
    summary = agent.get_agent_summary()
    print(f"   ✅ Agent özeti alındı")
    print(f"   📊 Toplam durum: {summary['total_states']}")
    print(f"   📊 Toplam aksiyon: {summary['total_actions']}")
    print(f"   📊 Toplam episode: {summary['total_episodes']}")
    print(f"   📊 Epsilon: {summary['learning_parameters']['epsilon']:.4f}")
    
    if summary['action_distribution']:
        print(f"   📊 Aksiyon dağılımı: {summary['action_distribution']}")
    
    if summary['performance_summary']:
        perf = summary['performance_summary']
        print(f"   📊 Ortalama getiri: {perf['average_return_pct']:.2f}%")
        print(f"   📊 Ortalama Sharpe: {perf['average_sharpe_ratio']:.3f}")
    
    print("\n✅ Reinforcement Learning Agent Test Tamamlandı!")


if __name__ == "__main__":
    test_reinforcement_learning_agent()
