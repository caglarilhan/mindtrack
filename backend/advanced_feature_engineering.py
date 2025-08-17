"""
Advanced Feature Engineering - Sprint 18: Advanced Feature Engineering + Graph Neural Networks

Bu modül, gelişmiş özellik mühendisliği (Graph Neural Networks, Market Microstructure,
Alternative Data, Economic Indicators) ile tahmin doğruluğunu önemli ölçüde artırır.
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
from sklearn.metrics import mutual_info_score
from sklearn.feature_selection import f_classif
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import SelectKBest, RFE
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import re

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FeatureConfig:
    """Özellik konfigürasyonu"""
    config_id: str
    name: str
    feature_type: str  # graph_nn, market_microstructure, alternative_data, economic_indicators
    parameters: Dict[str, Any]
    dependencies: List[str]
    created_at: datetime

@dataclass
class GraphData:
    """Graf veri yapısı"""
    graph_id: str
    nodes: List[str]  # Hisse senedi sembolleri
    edges: List[Tuple[str, str, float]]  # (node1, node2, weight)
    adjacency_matrix: np.ndarray
    node_features: Dict[str, np.ndarray]
    created_at: datetime

@dataclass
class MarketMicrostructure:
    """Piyasa mikro yapısı verisi"""
    data_id: str
    timestamp: datetime
    symbol: str
    order_book: Dict[str, np.ndarray]
    spread: float
    depth: float
    volume_profile: Dict[str, float]
    created_at: datetime

class AdvancedFeatureEngineering:
    """Gelişmiş Özellik Mühendisliği ana sınıfı"""
    
    def __init__(self):
        self.feature_configs = {}
        self.graph_data = {}
        self.market_microstructure = {}
        self.alternative_data = {}
        self.economic_indicators = {}
        self.feature_history = {}
        
        # Özellik parametreleri
        self.max_graph_nodes = 100
        self.max_feature_dim = 1000
        self.correlation_threshold = 0.8
        
        # Varsayılan konfigürasyonlar
        self._add_default_feature_configs()
        
        # Ekonomik gösterge parametreleri
        self.economic_indicators_config = {
            'cds_spreads': ['TR_5Y', 'TR_10Y'],
            'yield_curves': ['TR_2Y', 'TR_5Y', 'TR_10Y', 'TR_30Y'],
            'volatility_surfaces': ['VIX', 'TR_VIX'],
            'currency_pairs': ['USDTRY', 'EURTRY', 'GBPTRY']
        }
    
    def _add_default_feature_configs(self):
        """Varsayılan özellik konfigürasyonları ekle"""
        default_configs = [
            {
                "config_id": "GRAPH_NEURAL_NETWORK",
                "name": "Graph Neural Network Features",
                "feature_type": "graph_nn",
                "parameters": {
                    "num_layers": 3,
                    "hidden_dim": 64,
                    "aggregation": "mean",
                    "activation": "relu",
                    "dropout": 0.1
                },
                "dependencies": ["correlation_matrix", "volume_data"]
            },
            {
                "config_id": "MARKET_MICROSTRUCTURE",
                "name": "Market Microstructure Features",
                "feature_type": "market_microstructure",
                "parameters": {
                    "order_book_depth": 10,
                    "spread_calculation": "bid_ask",
                    "volume_profile_bins": 20,
                    "time_decay": 0.95
                },
                "dependencies": ["order_book", "trade_data"]
            },
            {
                "config_id": "ALTERNATIVE_DATA",
                "name": "Alternative Data Features",
                "feature_type": "alternative_data",
                "parameters": {
                    "satellite_indicators": ["parking_lots", "shipping_activity"],
                    "social_sentiment": ["twitter", "reddit", "news"],
                    "weather_data": ["temperature", "precipitation"],
                    "economic_calendar": ["earnings", "fed_meetings"]
                },
                "dependencies": ["external_apis", "data_sources"]
            },
            {
                "config_id": "ECONOMIC_INDICATORS",
                "name": "Economic Indicators Features",
                "feature_type": "economic_indicators",
                "parameters": {
                    "cds_spreads": ["5Y", "10Y"],
                    "yield_curves": ["2Y", "5Y", "10Y", "30Y"],
                    "volatility_surfaces": ["VIX", "local_vol"],
                    "currency_pairs": ["USDTRY", "EURTRY"]
                },
                "dependencies": ["bloomberg", "reuters", "tcmb"]
            }
        ]
        
        for config_data in default_configs:
            feature_config = FeatureConfig(
                config_id=config_data["config_id"],
                name=config_data["name"],
                feature_type=config_data["feature_type"],
                parameters=config_data["parameters"],
                dependencies=config_data["dependencies"],
                created_at=datetime.now()
            )
            
            self.feature_configs[feature_config.config_id] = feature_config
    
    def create_correlation_graph(self, price_data: pd.DataFrame, 
                               correlation_threshold: float = 0.7) -> GraphData:
        """Fiyat verilerinden korelasyon grafiği oluştur"""
        try:
            # Korelasyon matrisi hesapla
            returns = price_data.pct_change().dropna()
            correlation_matrix = returns.corr()
            
            # Threshold altındaki korelasyonları filtrele
            filtered_corr = correlation_matrix.copy()
            filtered_corr[filtered_corr < correlation_threshold] = 0
            
            # Node'ları al
            nodes = list(correlation_matrix.columns)
            
            # Edge'leri oluştur
            edges = []
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    if filtered_corr.iloc[i, j] > 0:
                        edges.append((nodes[i], nodes[j], filtered_corr.iloc[i, j]))
            
            # Adjacency matrix oluştur
            adjacency_matrix = filtered_corr.values
            
            # Node özellikleri (basit: ortalama return ve volatility)
            node_features = {}
            for node in nodes:
                node_returns = returns[node]
                node_features[node] = np.array([
                    node_returns.mean(),
                    node_returns.std(),
                    node_returns.skew(),
                    node_returns.kurtosis()
                ])
            
            graph_data = GraphData(
                graph_id=f"GRAPH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                nodes=nodes,
                edges=edges,
                adjacency_matrix=adjacency_matrix,
                node_features=node_features,
                created_at=datetime.now()
            )
            
            self.graph_data[graph_data.graph_id] = graph_data
            logger.info(f"Correlation graph created: {graph_data.graph_id} with {len(nodes)} nodes and {len(edges)} edges")
            
            return graph_data
        
        except Exception as e:
            logger.error(f"Error creating correlation graph: {e}")
            return None
    
    def create_graph_neural_network_features(self, graph_data: GraphData, 
                                          config: FeatureConfig) -> Dict[str, np.ndarray]:
        """Graph Neural Network özellikleri oluştur"""
        try:
            num_layers = config.parameters['num_layers']
            hidden_dim = config.parameters['hidden_dim']
            aggregation = config.parameters['aggregation']
            
            # Node feature matrix
            node_features = np.array([graph_data.node_features[node] for node in graph_data.nodes])
            num_nodes = len(graph_data.nodes)
            
            # Normalize adjacency matrix
            adj_matrix = graph_data.adjacency_matrix.copy()
            adj_matrix = adj_matrix / (adj_matrix.sum(axis=1, keepdims=True) + 1e-8)
            
            # Graph convolution layers
            current_features = node_features
            layer_outputs = []
            
            for layer in range(num_layers):
                # Graph convolution: H = σ(D^(-1/2) * A * D^(-1/2) * H * W)
                # Basit implementasyon: H = A * H * W
                
                # Message passing
                messages = adj_matrix @ current_features
                
                # Linear transformation (basit: random weights)
                weights = np.random.randn(current_features.shape[1], hidden_dim) * 0.1
                transformed = messages @ weights
                
                # Activation function
                if config.parameters['activation'] == 'relu':
                    transformed = np.maximum(0, transformed)
                elif config.parameters['activation'] == 'tanh':
                    transformed = np.tanh(transformed)
                
                # Dropout
                if config.parameters['dropout'] > 0:
                    mask = np.random.rand(*transformed.shape) > config.parameters['dropout']
                    transformed = transformed * mask
                
                current_features = transformed
                layer_outputs.append(current_features)
            
            # Aggregate features across layers
            if aggregation == 'mean':
                final_features = np.mean(layer_outputs, axis=0)
            elif aggregation == 'concat':
                final_features = np.concatenate(layer_outputs, axis=1)
            elif aggregation == 'last':
                final_features = layer_outputs[-1]
            else:
                final_features = layer_outputs[-1]
            
            # Node-level features
            node_features_dict = {}
            for i, node in enumerate(graph_data.nodes):
                node_features_dict[node] = final_features[i]
            
            # Graph-level features
            graph_features = {
                'node_count': num_nodes,
                'edge_count': len(graph_data.edges),
                'avg_degree': np.mean(adj_matrix.sum(axis=1)),
                'density': len(graph_data.edges) / (num_nodes * (num_nodes - 1) / 2),
                'clustering_coefficient': self._calculate_clustering_coefficient(adj_matrix)
            }
            
            logger.info(f"Graph Neural Network features created for {num_nodes} nodes")
            
            return {
                'node_features': node_features_dict,
                'graph_features': graph_features,
                'layer_outputs': layer_outputs
            }
        
        except Exception as e:
            logger.error(f"Error creating Graph Neural Network features: {e}")
            return {}
    
    def _calculate_clustering_coefficient(self, adj_matrix: np.ndarray) -> float:
        """Clustering coefficient hesapla"""
        try:
            num_nodes = adj_matrix.shape[0]
            total_triangles = 0
            total_triplets = 0
            
            for i in range(num_nodes):
                for j in range(i+1, num_nodes):
                    for k in range(j+1, num_nodes):
                        if adj_matrix[i, j] > 0 and adj_matrix[j, k] > 0 and adj_matrix[i, k] > 0:
                            total_triangles += 1
                        if adj_matrix[i, j] > 0 or adj_matrix[j, k] > 0 or adj_matrix[i, k] > 0:
                            total_triplets += 1
            
            if total_triplets == 0:
                return 0.0
            
            return total_triangles / total_triplets
        
        except Exception as e:
            logger.error(f"Error calculating clustering coefficient: {e}")
            return 0.0
    
    def create_market_microstructure_features(self, order_book_data: Dict[str, Any],
                                           config: FeatureConfig) -> Dict[str, float]:
        """Piyasa mikro yapısı özellikleri oluştur"""
        try:
            features = {}
            
            # Spread hesaplama
            if 'bid' in order_book_data and 'ask' in order_book_data:
                best_bid = max(order_book_data['bid'].keys())
                best_ask = min(order_book_data['ask'].keys())
                spread = best_ask - best_bid
                spread_bps = (spread / best_bid) * 10000  # Basis points
                
                features['spread'] = spread
                features['spread_bps'] = spread_bps
                features['mid_price'] = (best_bid + best_ask) / 2
            
            # Order book depth
            if 'bid' in order_book_data and 'ask' in order_book_data:
                bid_depth = sum(order_book_data['bid'].values())
                ask_depth = sum(order_book_data['ask'].values())
                total_depth = bid_depth + ask_depth
                
                features['bid_depth'] = bid_depth
                features['ask_depth'] = ask_depth
                features['total_depth'] = total_depth
                features['depth_imbalance'] = (bid_depth - ask_depth) / total_depth
            
            # Volume profile
            if 'volume_profile' in order_book_data:
                volume_profile = order_book_data['volume_profile']
                features['volume_weighted_price'] = sum(price * vol for price, vol in volume_profile.items()) / sum(volume_profile.values())
                features['volume_concentration'] = max(volume_profile.values()) / sum(volume_profile.values())
            
            # Time decay features
            if 'timestamp' in order_book_data:
                time_diff = (datetime.now() - order_book_data['timestamp']).total_seconds()
                features['time_decay'] = config.parameters['time_decay'] ** time_diff
            
            # Order flow imbalance
            if 'order_flow' in order_book_data:
                buy_orders = order_book_data['order_flow'].get('buy', 0)
                sell_orders = order_book_data['order_flow'].get('sell', 0)
                total_orders = buy_orders + sell_orders
                
                if total_orders > 0:
                    features['order_imbalance'] = (buy_orders - sell_orders) / total_orders
                    features['buy_pressure'] = buy_orders / total_orders
                    features['sell_pressure'] = sell_orders / total_orders
            
            logger.info(f"Market microstructure features created: {len(features)} features")
            return features
        
        except Exception as e:
            logger.error(f"Error creating market microstructure features: {e}")
            return {}
    
    def create_alternative_data_features(self, external_data: Dict[str, Any],
                                       config: FeatureConfig) -> Dict[str, float]:
        """Alternative data özellikleri oluştur"""
        try:
            features = {}
            
            # Satellite indicators
            if 'satellite_data' in external_data:
                satellite = external_data['satellite_data']
                
                if 'parking_lots' in satellite:
                    features['parking_occupancy'] = satellite['parking_lots'].get('occupancy_rate', 0)
                    features['parking_trend'] = satellite['parking_lots'].get('trend', 0)
                
                if 'shipping_activity' in satellite:
                    features['shipping_volume'] = satellite['shipping_activity'].get('container_volume', 0)
                    features['shipping_frequency'] = satellite['shipping_activity'].get('frequency', 0)
            
            # Social sentiment
            if 'social_data' in external_data:
                social = external_data['social_data']
                
                for platform in config.parameters['social_sentiment']:
                    if platform in social:
                        platform_data = social[platform]
                        features[f'{platform}_sentiment'] = platform_data.get('sentiment_score', 0)
                        features[f'{platform}_volume'] = platform_data.get('mention_volume', 0)
                        features[f'{platform}_trend'] = platform_data.get('trend', 0)
            
            # Weather data
            if 'weather_data' in external_data:
                weather = external_data['weather_data']
                
                for metric in config.parameters['weather_data']:
                    if metric in weather:
                        features[f'weather_{metric}'] = weather[metric].get('value', 0)
                        features[f'weather_{metric}_trend'] = weather[metric].get('trend', 0)
            
            # Economic calendar
            if 'economic_calendar' in external_data:
                calendar = external_data['economic_calendar']
                
                for event_type in config.parameters['economic_calendar']:
                    if event_type in calendar:
                        events = calendar[event_type]
                        features[f'{event_type}_count'] = len(events)
                        features[f'{event_type}_impact'] = sum(event.get('impact_score', 0) for event in events)
            
            logger.info(f"Alternative data features created: {len(features)} features")
            return features
        
        except Exception as e:
            logger.error(f"Error creating alternative data features: {e}")
            return {}
    
    def create_economic_indicator_features(self, economic_data: Dict[str, Any],
                                        config: FeatureConfig) -> Dict[str, float]:
        """Ekonomik gösterge özellikleri oluştur"""
        try:
            features = {}
            
            # CDS Spreads
            if 'cds_spreads' in economic_data:
                cds = economic_data['cds_spreads']
                
                for tenor in config.parameters['cds_spreads']:
                    if tenor in cds:
                        cds_data = cds[tenor]
                        features[f'cds_{tenor}'] = cds_data.get('spread', 0)
                        features[f'cds_{tenor}_change'] = cds_data.get('change', 0)
                        features[f'cds_{tenor}_trend'] = cds_data.get('trend', 0)
            
            # Yield Curves
            if 'yield_curves' in economic_data:
                yields = economic_data['yield_curves']
                
                for tenor in config.parameters['yield_curves']:
                    if tenor in yields:
                        yield_data = yields[tenor]
                        features[f'yield_{tenor}'] = yield_data.get('yield', 0)
                        features[f'yield_{tenor}_change'] = yield_data.get('change', 0)
                        features[f'yield_{tenor}_spread'] = yield_data.get('spread_to_benchmark', 0)
                
                # Yield curve slope
                if '2Y' in yields and '10Y' in yields:
                    features['yield_curve_slope'] = yields['10Y'].get('yield', 0) - yields['2Y'].get('yield', 0)
            
            # Volatility Surfaces
            if 'volatility_surfaces' in economic_data:
                vol = economic_data['volatility_surfaces']
                
                for vol_type in config.parameters['volatility_surfaces']:
                    if vol_type in vol:
                        vol_data = vol[vol_type]
                        features[f'vol_{vol_type}'] = vol_data.get('volatility', 0)
                        features[f'vol_{vol_type}_change'] = vol_data.get('change', 0)
                        features[f'vol_{vol_type}_skew'] = vol_data.get('skew', 0)
            
            # Currency Pairs
            if 'currency_pairs' in economic_data:
                fx = economic_data['currency_pairs']
                
                for pair in config.parameters['currency_pairs']:
                    if pair in fx:
                        fx_data = fx[pair]
                        features[f'fx_{pair}_rate'] = fx_data.get('rate', 0)
                        features[f'fx_{pair}_change'] = fx_data.get('change', 0)
                        features[f'fx_{pair}_volatility'] = fx_data.get('volatility', 0)
            
            logger.info(f"Economic indicator features created: {len(features)} features")
            return features
        
        except Exception as e:
            logger.error(f"Error creating economic indicator features: {e}")
            return {}
    
    def perform_feature_selection(self, features: pd.DataFrame, target: pd.Series,
                                method: str = "mutual_info", k: int = 50) -> Dict[str, Any]:
        """Özellik seçimi yap"""
        try:
            selection_results = {}
            
            if method == "mutual_info":
                # Mutual information
                mi_scores = {}
                for col in features.columns:
                    mi_scores[col] = mutual_info_score(features[col], target)
                
                # Top k features
                top_features = sorted(mi_scores.items(), key=lambda x: x[1], reverse=True)[:k]
                selected_features = [feature for feature, score in top_features]
                
                selection_results = {
                    'method': 'mutual_info',
                    'selected_features': selected_features,
                    'feature_scores': mi_scores,
                    'top_k_features': top_features
                }
            
            elif method == "f_classif":
                # F-statistic
                f_scores, p_values = f_classif(features, target)
                
                # Top k features
                feature_scores = dict(zip(features.columns, f_scores))
                top_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:k]
                selected_features = [feature for feature, score in top_features]
                
                selection_results = {
                    'method': 'f_classif',
                    'selected_features': selected_features,
                    'feature_scores': feature_scores,
                    'p_values': dict(zip(features.columns, p_values)),
                    'top_k_features': top_features
                }
            
            elif method == "rfe":
                # Recursive Feature Elimination
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
                selector = RFE(estimator, n_features_to_select=k)
                selector.fit(features, target)
                
                selected_features = features.columns[selector.support_].tolist()
                
                selection_results = {
                    'method': 'rfe',
                    'selected_features': selected_features,
                    'feature_ranking': dict(zip(features.columns, selector.ranking_))
                }
            
            logger.info(f"Feature selection completed using {method}: {len(selected_features)} features selected")
            return selection_results
        
        except Exception as e:
            logger.error(f"Error in feature selection: {e}")
            return {}
    
    def perform_dimensionality_reduction(self, features: pd.DataFrame, 
                                       method: str = "pca", n_components: int = 50) -> Dict[str, Any]:
        """Boyut azaltma yap"""
        try:
            reduction_results = {}
            
            if method == "pca":
                # Principal Component Analysis
                pca = PCA(n_components=min(n_components, features.shape[1]))
                reduced_features = pca.fit_transform(features)
                
                # Explained variance
                explained_variance_ratio = pca.explained_variance_ratio_
                cumulative_variance = np.cumsum(explained_variance_ratio)
                
                reduction_results = {
                    'method': 'pca',
                    'reduced_features': reduced_features,
                    'explained_variance_ratio': explained_variance_ratio,
                    'cumulative_variance': cumulative_variance,
                    'n_components': pca.n_components_,
                    'feature_names': [f'PC_{i+1}' for i in range(pca.n_components_)]
                }
            
            logger.info(f"Dimensionality reduction completed using {method}: {reduction_features.shape[1]} components")
            return reduction_results
        
        except Exception as e:
            logger.error(f"Error in dimensionality reduction: {e}")
            return {}
    
    def get_feature_engineering_summary(self) -> Dict[str, Any]:
        """Özellik mühendisliği özeti getir"""
        try:
            summary = {
                "total_configs": len(self.feature_configs),
                "total_graphs": len(self.graph_data),
                "feature_types": {},
                "performance_summary": {}
            }
            
            # Feature tipleri
            for config in self.feature_configs.values():
                feature_type = config.feature_type
                summary["feature_types"][feature_type] = summary["feature_types"].get(feature_type, 0) + 1
            
            # Graph özeti
            if self.graph_data:
                total_nodes = sum(len(graph.nodes) for graph in self.graph_data.values())
                total_edges = sum(len(graph.edges) for graph in self.graph_data.values())
                
                summary["graph_summary"] = {
                    "total_graphs": len(self.graph_data),
                    "total_nodes": total_nodes,
                    "total_edges": total_edges,
                    "avg_nodes_per_graph": total_nodes / len(self.graph_data),
                    "avg_edges_per_graph": total_edges / len(self.graph_data)
                }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting feature engineering summary: {e}")
            return {}


def test_advanced_feature_engineering():
    """Advanced Feature Engineering test fonksiyonu"""
    print("\n🧪 Advanced Feature Engineering Test Başlıyor...")
    
    # Advanced Feature Engineering oluştur
    feature_eng = AdvancedFeatureEngineering()
    
    print("✅ Advanced Feature Engineering oluşturuldu")
    print(f"📊 Toplam özellik konfigürasyonu: {len(feature_eng.feature_configs)}")
    print(f"📊 Kullanılabilir özellik tipleri: {list(feature_eng.feature_configs.keys())}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    np.random.seed(42)
    n_samples = 100
    n_stocks = 10
    
    # Simüle edilmiş fiyat verisi
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='D')
    stock_symbols = [f'STOCK_{i+1}' for i in range(n_stocks)]
    
    price_data = pd.DataFrame(index=dates)
    for symbol in stock_symbols:
        # Simüle edilmiş fiyat serisi
        base_price = 100 + np.random.randn() * 20
        returns = np.random.randn(n_samples) * 0.02
        prices = base_price * np.exp(np.cumsum(returns))
        price_data[symbol] = prices
    
    print(f"   ✅ Test verisi oluşturuldu: {len(price_data)} örnek, {len(price_data.columns)} hisse")
    
    # Korelasyon grafiği oluşturma testi
    print("\n📊 Korelasyon Grafiği Testi:")
    
    graph_data = feature_eng.create_correlation_graph(price_data, correlation_threshold=0.6)
    
    if graph_data:
        print(f"   ✅ Korelasyon grafiği oluşturuldu")
        print(f"      📊 Node sayısı: {len(graph_data.nodes)}")
        print(f"      📊 Edge sayısı: {len(graph_data.edges)}")
        print(f"      📊 Ortalama korelasyon: {np.mean([edge[2] for edge in graph_data.edges]):.3f}")
    
    # Graph Neural Network özellikleri testi
    print("\n📊 Graph Neural Network Özellikleri Testi:")
    
    if graph_data:
        gnn_config = feature_eng.feature_configs['GRAPH_NEURAL_NETWORK']
        gnn_features = feature_eng.create_graph_neural_network_features(graph_data, gnn_config)
        
        if gnn_features:
            print(f"   ✅ GNN özellikleri oluşturuldu")
            print(f"      📊 Node özellik sayısı: {len(gnn_features['node_features'])}")
            print(f"      📊 Graph özellik sayısı: {len(gnn_features['graph_features'])}")
            print(f"      📊 Layer sayısı: {len(gnn_features['layer_outputs'])}")
    
    # Market Microstructure özellikleri testi
    print("\n📊 Market Microstructure Özellikleri Testi:")
    
    # Simüle edilmiş order book verisi
    order_book_data = {
        'bid': {95.0: 1000, 94.5: 1500, 94.0: 2000},
        'ask': {96.0: 1200, 96.5: 1800, 97.0: 2500},
        'volume_profile': {95.5: 500, 96.0: 800, 96.5: 600},
        'order_flow': {'buy': 2500, 'sell': 1800},
        'timestamp': datetime.now()
    }
    
    mm_config = feature_eng.feature_configs['MARKET_MICROSTRUCTURE']
    mm_features = feature_eng.create_market_microstructure_features(order_book_data, mm_config)
    
    if mm_features:
        print(f"   ✅ Market microstructure özellikleri oluşturuldu")
        print(f"      📊 Özellik sayısı: {len(mm_features)}")
        print(f"      📊 Spread: {mm_features.get('spread', 0):.2f}")
        print(f"      📊 Depth imbalance: {mm_features.get('depth_imbalance', 0):.3f}")
    
    # Alternative Data özellikleri testi
    print("\n📊 Alternative Data Özellikleri Testi:")
    
    # Simüle edilmiş external data
    external_data = {
        'satellite_data': {
            'parking_lots': {'occupancy_rate': 0.75, 'trend': 0.05},
            'shipping_activity': {'container_volume': 1200, 'frequency': 15}
        },
        'social_data': {
            'twitter': {'sentiment_score': 0.6, 'mention_volume': 5000, 'trend': 0.1},
            'reddit': {'sentiment_score': 0.4, 'mention_volume': 2000, 'trend': -0.05}
        },
        'weather_data': {
            'temperature': {'value': 25, 'trend': 2},
            'precipitation': {'value': 0.1, 'trend': -0.5}
        }
    }
    
    alt_config = feature_eng.feature_configs['ALTERNATIVE_DATA']
    alt_features = feature_eng.create_alternative_data_features(external_data, alt_config)
    
    if alt_features:
        print(f"   ✅ Alternative data özellikleri oluşturuldu")
        print(f"      📊 Özellik sayısı: {len(alt_features)}")
        print(f"      📊 Parking occupancy: {alt_features.get('parking_occupancy', 0):.2f}")
        print(f"      📊 Twitter sentiment: {alt_features.get('twitter_sentiment', 0):.2f}")
    
    # Feature selection testi
    print("\n📊 Feature Selection Testi:")
    
    # Simüle edilmiş feature matrix
    feature_matrix = pd.DataFrame(
        np.random.randn(100, 20),
        columns=[f'feature_{i+1}' for i in range(20)]
    )
    target = pd.Series(np.random.randint(0, 2, 100))
    
    # Mutual info selection
    mi_selection = feature_eng.perform_feature_selection(feature_matrix, target, "mutual_info", k=10)
    
    if mi_selection:
        print(f"   ✅ Feature selection tamamlandı")
        print(f"      📊 Seçilen özellik sayısı: {len(mi_selection['selected_features'])}")
        print(f"      📊 En yüksek skor: {max(mi_selection['feature_scores'].values()):.4f}")
    
    # Dimensionality reduction testi
    print("\n📊 Dimensionality Reduction Testi:")
    
    pca_reduction = feature_eng.perform_dimensionality_reduction(feature_matrix, "pca", n_components=10)
    
    if pca_reduction:
        print(f"   ✅ Dimensionality reduction tamamlandı")
        print(f"      📊 Bileşen sayısı: {pca_reduction['n_components']}")
        print(f"      📊 Açıklanan varyans oranı: {np.sum(pca_reduction['explained_variance_ratio']):.3f}")
    
    # Özellik mühendisliği özeti
    print("\n📊 Özellik Mühendisliği Özeti:")
    summary = feature_eng.get_feature_engineering_summary()
    
    if summary:
        print(f"   ✅ Özellik mühendisliği özeti alındı")
        print(f"   📊 Toplam konfigürasyon: {summary['total_configs']}")
        print(f"   📊 Toplam grafik: {summary['total_graphs']}")
        print(f"   📊 Özellik tipleri: {summary['feature_types']}")
        
        if 'graph_summary' in summary:
            graph_sum = summary['graph_summary']
            print(f"   📊 Toplam node: {graph_sum['total_nodes']}")
            print(f"   📊 Toplam edge: {graph_sum['total_edges']}")
            print(f"   📊 Ortalama node/grafik: {graph_sum['avg_nodes_per_graph']:.1f}")
    
    print("\n✅ Advanced Feature Engineering Test Tamamlandı!")


if __name__ == "__main__":
    test_advanced_feature_engineering()
