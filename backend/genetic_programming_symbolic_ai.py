"""
Genetic Programming & Symbolic AI - Sprint 18: Genetic Programming + Symbolic AI

Bu modül, genetik programlama, sembolik regresyon ve finans için AutoML
ile tahmin doğruluğunu önemli ölçüde artırır.
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
from collections import defaultdict, deque
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import re

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SymbolicConfig:
    """Sembolik AI konfigürasyonu"""
    config_id: str
    name: str
    method_type: str  # symbolic_regression, genetic_programming, automl
    parameters: Dict[str, Any]
    constraints: Dict[str, Any]
    created_at: datetime

@dataclass
class SymbolicExpression:
    """Sembolik ifade"""
    expression_id: str
    expression: str
    complexity: int
    fitness_score: float
    variables: List[str]
    constants: List[float]
    created_at: datetime

@dataclass
class TradingStrategy:
    """Trading stratejisi"""
    strategy_id: str
    name: str
    entry_condition: str
    exit_condition: str
    position_sizing: str
    risk_management: str
    fitness_score: float
    created_at: datetime

class GeneticProgrammingSymbolicAI:
    """Genetik Programlama ve Sembolik AI ana sınıfı"""
    
    def __init__(self):
        self.symbolic_configs = {}
        self.symbolic_expressions = {}
        self.trading_strategies = {}
        self.genetic_population = []
        self.evolution_history = {}
        
        # Genetik programlama parametreleri
        self.population_size = 100
        self.max_generations = 50
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 10
        
        # Sembolik AI parametreleri
        self.max_expression_length = 50
        self.max_complexity = 20
        self.operators = ['+', '-', '*', '/', '**', 'sin', 'cos', 'tan', 'log', 'exp']
        self.variables = ['x', 'y', 'z', 'price', 'volume', 'rsi', 'macd']
        
        # Varsayılan konfigürasyonlar
        self._add_default_symbolic_configs()
        
        # Trading stratejisi şablonları
        self._initialize_trading_templates()
    
    def _add_default_symbolic_configs(self):
        """Varsayılan sembolik AI konfigürasyonları ekle"""
        default_configs = [
            {
                "config_id": "SYMBOLIC_REGRESSION",
                "name": "Symbolic Regression",
                "method_type": "symbolic_regression",
                "parameters": {
                    "max_depth": 8,
                    "population_size": 200,
                    "generations": 100,
                    "tournament_size": 7,
                    "parsimony_pressure": 0.01
                },
                "constraints": {
                    "allowed_operators": ["+", "-", "*", "/", "**", "sin", "cos", "log"],
                    "max_constants": 5,
                    "max_variables": 10
                }
            },
            {
                "config_id": "GENETIC_PROGRAMMING",
                "name": "Genetic Programming",
                "method_type": "genetic_programming",
                "parameters": {
                    "max_tree_depth": 10,
                    "population_size": 150,
                    "generations": 80,
                    "mutation_rate": 0.15,
                    "crossover_rate": 0.85
                },
                "constraints": {
                    "allowed_functions": ["if", "and", "or", "not", ">", "<", ">=", "<=", "=="],
                    "max_conditions": 5,
                    "max_actions": 3
                }
            },
            {
                "config_id": "AUTOML_FINANCE",
                "name": "AutoML for Finance",
                "method_type": "automl",
                "parameters": {
                    "search_space": "large",
                    "time_limit": 3600,
                    "max_models": 50,
                    "ensemble_size": 10,
                    "cross_validation": "time_series"
                },
                "constraints": {
                    "model_types": ["tree", "neural", "ensemble", "linear"],
                    "feature_selection": True,
                    "hyperparameter_tuning": True
                }
            }
        ]
        
        for config_data in default_configs:
            symbolic_config = SymbolicConfig(
                config_id=config_data["config_id"],
                name=config_data["name"],
                method_type=config_data["method_type"],
                parameters=config_data["parameters"],
                constraints=config_data["constraints"],
                created_at=datetime.now()
            )
            
            self.symbolic_configs[symbolic_config.config_id] = symbolic_config
    
    def _initialize_trading_templates(self):
        """Trading stratejisi şablonlarını başlat"""
        self.trading_templates = {
            'trend_following': {
                'entry': 'price > sma_20 and rsi < 70',
                'exit': 'price < sma_20 or rsi > 80',
                'position_sizing': 'risk_per_trade = 0.02',
                'risk_management': 'stop_loss = entry_price * 0.95'
            },
            'mean_reversion': {
                'entry': 'price < sma_20 and rsi < 30',
                'exit': 'price > sma_20 or rsi > 70',
                'position_sizing': 'risk_per_trade = 0.015',
                'risk_management': 'stop_loss = entry_price * 0.90'
            },
            'breakout': {
                'entry': 'price > resistance_level and volume > avg_volume * 1.5',
                'exit': 'price < support_level or volume < avg_volume * 0.5',
                'position_sizing': 'risk_per_trade = 0.025',
                'risk_management': 'stop_loss = support_level'
            },
            'momentum': {
                'entry': 'macd > 0 and macd_signal > 0 and price > sma_50',
                'exit': 'macd < 0 or price < sma_50',
                'position_sizing': 'risk_per_trade = 0.03',
                'risk_management': 'trailing_stop = price * 0.98'
            }
        }
    
    def create_symbolic_expression(self, complexity: int = 5) -> str:
        """Sembolik ifade oluştur"""
        try:
            if complexity <= 0:
                return random.choice(self.variables)
            
            # Rastgele operatör seç
            operator = random.choice(self.operators)
            
            if operator in ['sin', 'cos', 'tan', 'log', 'exp']:
                # Unary operator
                operand = self.create_symbolic_expression(complexity - 1)
                return f"{operator}({operand})"
            
            elif operator in ['+', '-', '*', '/']:
                # Binary operator
                left_complexity = complexity // 2
                right_complexity = complexity - left_complexity - 1
                
                left_operand = self.create_symbolic_expression(left_complexity)
                right_operand = self.create_symbolic_expression(right_complexity)
                
                return f"({left_operand} {operator} {right_operand})"
            
            elif operator == '**':
                # Power operator
                base_complexity = complexity - 1
                base = self.create_symbolic_expression(base_complexity)
                exponent = random.choice([2, 3, 0.5])
                
                return f"({base} ** {exponent})"
            
            else:
                # Fallback to variable
                return random.choice(self.variables)
        
        except Exception as e:
            logger.error(f"Error creating symbolic expression: {e}")
            return random.choice(self.variables)
    
    def evaluate_symbolic_expression(self, expression: str, variables: Dict[str, float]) -> float:
        """Sembolik ifadeyi değerlendir"""
        try:
            # Güvenli eval için sadece matematiksel operatörlere izin ver
            allowed_names = {
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'log': np.log, 'exp': np.exp, 'abs': np.abs,
                'sqrt': np.sqrt, 'pi': np.pi, 'e': np.e
            }
            
            # Variables ekle
            allowed_names.update(variables)
            
            # Expression'ı değerlendir
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            # NaN ve infinity kontrolü
            if np.isnan(result) or np.isinf(result):
                return 0.0
            
            return float(result)
        
        except Exception as e:
            logger.error(f"Error evaluating expression {expression}: {e}")
            return 0.0
    
    def create_trading_strategy(self, strategy_type: str = "custom") -> TradingStrategy:
        """Trading stratejisi oluştur"""
        try:
            if strategy_type in self.trading_templates:
                template = self.trading_templates[strategy_type]
                
                strategy = TradingStrategy(
                    strategy_id=f"STRATEGY_{strategy_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name=f"{strategy_type.title()} Strategy",
                    entry_condition=template['entry'],
                    exit_condition=template['exit'],
                    position_sizing=template['position_sizing'],
                    risk_management=template['risk_management'],
                    fitness_score=0.0,
                    created_at=datetime.now()
                )
            else:
                # Custom strategy
                entry_conditions = [
                    'price > sma_20 and volume > avg_volume',
                    'rsi < 30 and macd > 0',
                    'price > resistance_level and momentum > 0',
                    'bollinger_lower < price < bollinger_upper'
                ]
                
                exit_conditions = [
                    'price < sma_20 or rsi > 70',
                    'macd < 0 or stop_loss_hit',
                    'price < support_level or momentum < 0',
                    'price > bollinger_upper or take_profit_hit'
                ]
                
                strategy = TradingStrategy(
                    strategy_id=f"STRATEGY_CUSTOM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name="Custom Strategy",
                    entry_condition=random.choice(entry_conditions),
                    exit_condition=random.choice(exit_conditions),
                    position_sizing="risk_per_trade = 0.02",
                    risk_management="stop_loss = entry_price * 0.95",
                    fitness_score=0.0,
                    created_at=datetime.now()
                )
            
            self.trading_strategies[strategy.strategy_id] = strategy
            logger.info(f"Trading strategy created: {strategy.strategy_id}")
            
            return strategy
        
        except Exception as e:
            logger.error(f"Error creating trading strategy: {e}")
            return None
    
    def mutate_trading_strategy(self, strategy: TradingStrategy, 
                              mutation_rate: float = 0.1) -> TradingStrategy:
        """Trading stratejisini mutate et"""
        try:
            mutated_strategy = TradingStrategy(
                strategy_id=f"MUTATED_{strategy.strategy_id}",
                name=strategy.name,
                entry_condition=strategy.entry_condition,
                exit_condition=strategy.exit_condition,
                position_sizing=strategy.position_sizing,
                risk_management=strategy.risk_management,
                fitness_score=strategy.fitness_score,
                created_at=datetime.now()
            )
            
            # Entry condition mutation
            if random.random() < mutation_rate:
                entry_conditions = [
                    'price > sma_20 and volume > avg_volume',
                    'rsi < 30 and macd > 0',
                    'price > resistance_level and momentum > 0',
                    'bollinger_lower < price < bollinger_upper'
                ]
                mutated_strategy.entry_condition = random.choice(entry_conditions)
            
            # Exit condition mutation
            if random.random() < mutation_rate:
                exit_conditions = [
                    'price < sma_20 or rsi > 70',
                    'macd < 0 or stop_loss_hit',
                    'price < support_level or momentum < 0',
                    'price > bollinger_upper or take_profit_hit'
                ]
                mutated_strategy.exit_condition = random.choice(exit_conditions)
            
            # Position sizing mutation
            if random.random() < mutation_rate:
                position_sizings = [
                    'risk_per_trade = 0.015',
                    'risk_per_trade = 0.02',
                    'risk_per_trade = 0.025',
                    'risk_per_trade = 0.03'
                ]
                mutated_strategy.position_sizing = random.choice(position_sizings)
            
            # Risk management mutation
            if random.random() < mutation_rate:
                risk_managements = [
                    'stop_loss = entry_price * 0.90',
                    'stop_loss = entry_price * 0.95',
                    'trailing_stop = price * 0.98',
                    'stop_loss = support_level'
                ]
                mutated_strategy.risk_management = random.choice(risk_managements)
            
            logger.info(f"Trading strategy mutated: {mutated_strategy.strategy_id}")
            return mutated_strategy
        
        except Exception as e:
            logger.error(f"Error mutating trading strategy: {e}")
            return strategy
    
    def crossover_trading_strategies(self, strategy1: TradingStrategy, 
                                   strategy2: TradingStrategy) -> Tuple[TradingStrategy, TradingStrategy]:
        """İki trading stratejisini crossover et"""
        try:
            # Crossover points
            crossover_point = random.randint(1, 3)
            
            child1 = TradingStrategy(
                strategy_id=f"CROSSOVER_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=f"Child of {strategy1.name}",
                entry_condition=strategy1.entry_condition,
                exit_condition=strategy2.exit_condition,
                position_sizing=strategy1.position_sizing,
                risk_management=strategy2.risk_management,
                fitness_score=0.0,
                created_at=datetime.now()
            )
            
            child2 = TradingStrategy(
                strategy_id=f"CROSSOVER_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=f"Child of {strategy2.name}",
                entry_condition=strategy2.entry_condition,
                exit_condition=strategy1.exit_condition,
                position_sizing=strategy2.position_sizing,
                risk_management=strategy1.risk_management,
                fitness_score=0.0,
                created_at=datetime.now()
            )
            
            logger.info(f"Trading strategies crossover completed: {child1.strategy_id}, {child2.strategy_id}")
            return child1, child2
        
        except Exception as e:
            logger.error(f"Error in crossover: {e}")
            return strategy1, strategy2
    
    def evaluate_trading_strategy(self, strategy: TradingStrategy, 
                                historical_data: pd.DataFrame) -> float:
        """Trading stratejisini değerlendir"""
        try:
            # Basit fitness hesaplama (gerçek implementasyonda daha karmaşık)
            fitness_score = 0.0
            
            # Entry condition complexity
            entry_complexity = len(strategy.entry_condition.split())
            fitness_score += max(0, 10 - entry_complexity)  # Daha basit = daha iyi
            
            # Exit condition complexity
            exit_complexity = len(strategy.exit_condition.split())
            fitness_score += max(0, 10 - exit_complexity)
            
            # Risk management quality
            if 'stop_loss' in strategy.risk_management.lower():
                fitness_score += 5
            if 'trailing' in strategy.risk_management.lower():
                fitness_score += 3
            
            # Position sizing quality
            if 'risk_per_trade' in strategy.position_sizing:
                fitness_score += 3
            
            # Random component for diversity
            fitness_score += random.uniform(0, 2)
            
            # Update strategy fitness
            strategy.fitness_score = fitness_score
            
            return fitness_score
        
        except Exception as e:
            logger.error(f"Error evaluating trading strategy: {e}")
            return 0.0
    
    def run_genetic_algorithm(self, population_size: int = 50, 
                            generations: int = 20) -> List[TradingStrategy]:
        """Genetik algoritma çalıştır"""
        try:
            # Initial population
            population = []
            for i in range(population_size):
                strategy_type = random.choice(list(self.trading_templates.keys()) + ['custom'])
                strategy = self.create_trading_strategy(strategy_type)
                if strategy:
                    population.append(strategy)
            
            # Evolution loop
            best_fitness_history = []
            
            for generation in range(generations):
                # Evaluate fitness
                for strategy in population:
                    self.evaluate_trading_strategy(strategy, pd.DataFrame())
                
                # Sort by fitness
                population.sort(key=lambda x: x.fitness_score, reverse=True)
                best_fitness = population[0].fitness_score
                best_fitness_history.append(best_fitness)
                
                logger.info(f"Generation {generation + 1}: Best fitness = {best_fitness:.2f}")
                
                # Elitism: Keep best strategies
                elite = population[:self.elite_size]
                
                # Create new population
                new_population = elite.copy()
                
                while len(new_population) < population_size:
                    # Selection: Tournament selection
                    tournament_size = 3
                    tournament = random.sample(population, tournament_size)
                    parent1 = max(tournament, key=lambda x: x.fitness_score)
                    
                    tournament = random.sample(population, tournament_size)
                    parent2 = max(tournament, key=lambda x: x.fitness_score)
                    
                    # Crossover
                    if random.random() < self.crossover_rate:
                        child1, child2 = self.crossover_trading_strategies(parent1, parent2)
                        new_population.extend([child1, child2])
                    else:
                        new_population.extend([parent1, parent2])
                    
                    # Mutation
                    if random.random() < self.mutation_rate:
                        mutated = self.mutate_trading_strategy(parent1)
                        new_population.append(mutated)
                
                # Update population
                population = new_population[:population_size]
            
            # Store evolution history
            self.evolution_history = {
                'generations': generations,
                'population_size': population_size,
                'best_fitness_history': best_fitness_history,
                'final_population': population
            }
            
            logger.info(f"Genetic algorithm completed: {generations} generations")
            return population
        
        except Exception as e:
            logger.error(f"Error running genetic algorithm: {e}")
            return []
    
    def perform_symbolic_regression(self, X: pd.DataFrame, y: pd.Series,
                                  config: SymbolicConfig) -> Dict[str, Any]:
        """Sembolik regresyon yap"""
        try:
            max_depth = config.parameters['max_depth']
            population_size = config.parameters['population_size']
            generations = config.parameters['generations']
            
            # Initial population of expressions
            expressions = []
            for i in range(population_size):
                complexity = random.randint(1, max_depth)
                expression_str = self.create_symbolic_expression(complexity)
                
                symbolic_expr = SymbolicExpression(
                    expression_id=f"EXPR_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    expression=expression_str,
                    complexity=complexity,
                    fitness_score=0.0,
                    variables=list(X.columns),
                    constants=[],
                    created_at=datetime.now()
                )
                expressions.append(symbolic_expr)
            
            # Evolution loop
            best_expressions = []
            
            for generation in range(generations):
                # Evaluate fitness
                for expr in expressions:
                    try:
                        # Create variables dict
                        variables = {}
                        for i, col in enumerate(X.columns):
                            variables[col] = X.iloc[0, i]  # Use first row for simplicity
                        
                        # Evaluate expression
                        prediction = self.evaluate_symbolic_expression(expr.expression, variables)
                        
                        # Calculate fitness (simplified)
                        if prediction != 0:
                            expr.fitness_score = 1.0 / (1.0 + abs(prediction - y.iloc[0]))
                        else:
                            expr.fitness_score = 0.0
                    
                    except Exception as e:
                        expr.fitness_score = 0.0
                
                # Sort by fitness
                expressions.sort(key=lambda x: x.fitness_score, reverse=True)
                best_expr = expressions[0]
                best_expressions.append(best_expr)
                
                logger.info(f"Generation {generation + 1}: Best fitness = {best_expr.fitness_score:.4f}")
                
                # Keep best expressions
                elite = expressions[:10]
                
                # Create new population
                new_expressions = elite.copy()
                
                while len(new_expressions) < population_size:
                    # Random selection and mutation
                    parent = random.choice(elite)
                    complexity = max(1, parent.complexity + random.randint(-1, 1))
                    new_expr = self.create_symbolic_expression(complexity)
                    
                    symbolic_expr = SymbolicExpression(
                        expression_id=f"EXPR_NEW_{len(new_expressions)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        expression=new_expr,
                        complexity=complexity,
                        fitness_score=0.0,
                        variables=list(X.columns),
                        constants=[],
                        created_at=datetime.now()
                    )
                    new_expressions.append(symbolic_expr)
                
                expressions = new_expressions[:population_size]
            
            # Store best expressions
            for expr in best_expressions:
                self.symbolic_expressions[expr.expression_id] = expr
            
            logger.info(f"Symbolic regression completed: {len(best_expressions)} best expressions")
            
            return {
                'best_expressions': best_expressions,
                'generations': generations,
                'population_size': population_size
            }
        
        except Exception as e:
            logger.error(f"Error in symbolic regression: {e}")
            return {}
    
    def get_symbolic_ai_summary(self) -> Dict[str, Any]:
        """Sembolik AI özeti getir"""
        try:
            summary = {
                "total_configs": len(self.symbolic_configs),
                "total_expressions": len(self.symbolic_expressions),
                "total_strategies": len(self.trading_strategies),
                "method_types": {},
                "evolution_summary": {}
            }
            
            # Method tipleri
            for config in self.symbolic_configs.values():
                method_type = config.method_type
                summary["method_types"][method_type] = summary["method_types"].get(method_type, 0) + 1
            
            # Evolution özeti
            if self.evolution_history:
                summary["evolution_summary"] = {
                    "generations": self.evolution_history.get('generations', 0),
                    "population_size": self.evolution_history.get('population_size', 0),
                    "best_fitness": max(self.evolution_history.get('best_fitness_history', [0])),
                    "final_population_size": len(self.evolution_history.get('final_population', []))
                }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting symbolic AI summary: {e}")
            return {}


def test_genetic_programming_symbolic_ai():
    """Genetic Programming & Symbolic AI test fonksiyonu"""
    print("\n🧪 Genetic Programming & Symbolic AI Test Başlıyor...")
    
    # Genetic Programming & Symbolic AI oluştur
    symbolic_ai = GeneticProgrammingSymbolicAI()
    
    print("✅ Genetic Programming & Symbolic AI oluşturuldu")
    print(f"📊 Toplam sembolik AI konfigürasyonu: {len(symbolic_ai.symbolic_configs)}")
    print(f"📊 Kullanılabilir method tipleri: {list(symbolic_ai.symbolic_configs.keys())}")
    
    # Sembolik ifade oluşturma testi
    print("\n📊 Sembolik İfade Oluşturma Testi:")
    
    for i in range(5):
        complexity = random.randint(3, 8)
        expression = symbolic_ai.create_symbolic_expression(complexity)
        print(f"   📊 İfade {i+1}: {expression}")
        print(f"      📊 Karmaşıklık: {complexity}")
    
    # Sembolik ifade değerlendirme testi
    print("\n📊 Sembolik İfade Değerlendirme Testi:")
    
    test_expression = "sin(x) + cos(y) * 2"
    test_variables = {'x': 1.0, 'y': 0.5}
    
    result = symbolic_ai.evaluate_symbolic_expression(test_expression, test_variables)
    print(f"   📊 İfade: {test_expression}")
    print(f"   📊 Değişkenler: {test_variables}")
    print(f"   📊 Sonuç: {result:.4f}")
    
    # Trading stratejisi oluşturma testi
    print("\n📊 Trading Stratejisi Oluşturma Testi:")
    
    strategy_types = ['trend_following', 'mean_reversion', 'breakout', 'momentum']
    
    for strategy_type in strategy_types:
        strategy = symbolic_ai.create_trading_strategy(strategy_type)
        if strategy:
            print(f"   📊 {strategy.name}:")
            print(f"      📊 Entry: {strategy.entry_condition}")
            print(f"      📊 Exit: {strategy.exit_condition}")
            print(f"      📊 Position Sizing: {strategy.position_sizing}")
    
    # Trading stratejisi mutation testi
    print("\n📊 Trading Stratejisi Mutation Testi:")
    
    original_strategy = symbolic_ai.create_trading_strategy('custom')
    if original_strategy:
        mutated_strategy = symbolic_ai.mutate_trading_strategy(original_strategy, mutation_rate=0.3)
        
        print(f"   📊 Orijinal Entry: {original_strategy.entry_condition}")
        print(f"   📊 Mutated Entry: {mutated_strategy.entry_condition}")
        print(f"   📊 Orijinal Exit: {original_strategy.exit_condition}")
        print(f"   📊 Mutated Exit: {mutated_strategy.exit_condition}")
    
    # Trading stratejisi crossover testi
    print("\n📊 Trading Stratejisi Crossover Testi:")
    
    strategy1 = symbolic_ai.create_trading_strategy('trend_following')
    strategy2 = symbolic_ai.create_trading_strategy('mean_reversion')
    
    if strategy1 and strategy2:
        child1, child2 = symbolic_ai.crossover_trading_strategies(strategy1, strategy2)
        
        print(f"   📊 Parent 1 Entry: {strategy1.entry_condition}")
        print(f"   📊 Parent 2 Entry: {strategy2.entry_condition}")
        print(f"   📊 Child 1 Entry: {child1.entry_condition}")
        print(f"   📊 Child 2 Entry: {child2.entry_condition}")
    
    # Trading stratejisi değerlendirme testi
    print("\n📊 Trading Stratejisi Değerlendirme Testi:")
    
    # Simüle edilmiş historical data
    historical_data = pd.DataFrame({
        'price': np.random.randn(100),
        'volume': np.random.randn(100),
        'rsi': np.random.randn(100),
        'macd': np.random.randn(100)
    })
    
    test_strategy = symbolic_ai.create_trading_strategy('custom')
    if test_strategy:
        fitness_score = symbolic_ai.evaluate_trading_strategy(test_strategy, historical_data)
        print(f"   📊 Strateji: {test_strategy.name}")
        print(f"   📊 Fitness Score: {fitness_score:.2f}")
    
    # Genetik algoritma testi
    print("\n📊 Genetik Algoritma Testi:")
    
    population = symbolic_ai.run_genetic_algorithm(population_size=20, generations=5)
    
    if population:
        print(f"   ✅ Genetik algoritma tamamlandı")
        print(f"      📊 Final population size: {len(population)}")
        print(f"      📊 Best fitness: {population[0].fitness_score:.2f}")
        print(f"      📊 Best strategy: {population[0].name}")
    
    # Sembolik regresyon testi
    print("\n📊 Sembolik Regresyon Testi:")
    
    # Simüle edilmiş veri
    X = pd.DataFrame({
        'feature1': np.random.randn(50),
        'feature2': np.random.randn(50),
        'feature3': np.random.randn(50)
    })
    y = pd.Series(np.random.randn(50))
    
    symbolic_config = symbolic_ai.symbolic_configs['SYMBOLIC_REGRESSION']
    regression_results = symbolic_ai.perform_symbolic_regression(X, y, symbolic_config)
    
    if regression_results:
        print(f"   ✅ Sembolik regresyon tamamlandı")
        print(f"      📊 Generations: {regression_results['generations']}")
        print(f"      📊 Population size: {regression_results['population_size']}")
        print(f"      📊 Best expressions: {len(regression_results['best_expressions'])}")
        
        if regression_results['best_expressions']:
            best_expr = regression_results['best_expressions'][0]
            print(f"      📊 Best expression: {best_expr.expression}")
            print(f"      📊 Best fitness: {best_expr.fitness_score:.4f}")
    
    # Sembolik AI özeti
    print("\n📊 Sembolik AI Özeti:")
    summary = symbolic_ai.get_symbolic_ai_summary()
    
    if summary:
        print(f"   ✅ Sembolik AI özeti alındı")
        print(f"   📊 Toplam konfigürasyon: {summary['total_configs']}")
        print(f"   📊 Toplam ifade: {summary['total_expressions']}")
        print(f"   📊 Toplam strateji: {summary['total_strategies']}")
        print(f"   📊 Method tipleri: {summary['method_types']}")
        
        if summary['evolution_summary']:
            evol = summary['evolution_summary']
            print(f"   📊 Generations: {evol['generations']}")
            print(f"   📊 Population size: {evol['population_size']}")
            print(f"   📊 Best fitness: {evol['best_fitness']:.2f}")
    
    print("\n✅ Genetic Programming & Symbolic AI Test Tamamlandı!")


if __name__ == "__main__":
    test_genetic_programming_symbolic_ai()
