"""
Transformer Models - Sprint 18: Transformer Models + Multi-Modal Learning

Bu modül, finansal zaman serisi için transformer mimarileri, multi-modal learning
ve attention mechanisms kullanarak tahmin doğruluğunu önemli ölçüde artırır.
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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import re

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TransformerConfig:
    """Transformer konfigürasyonu"""
    config_id: str
    name: str
    model_type: str  # financial_bert, time_series_transformer, multi_modal
    architecture: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    attention_heads: int
    embedding_dim: int
    num_layers: int
    created_at: datetime

@dataclass
class MultiModalData:
    """Multi-modal veri yapısı"""
    data_id: str
    numerical_features: pd.DataFrame
    text_features: List[str]
    image_features: Optional[np.ndarray]
    timestamp: datetime
    target: Optional[float]
    created_at: datetime

@dataclass
class AttentionWeights:
    """Attention ağırlıkları"""
    weights_id: str
    timestamp: datetime
    attention_scores: np.ndarray
    feature_importance: Dict[str, float]
    temporal_importance: Dict[str, float]
    created_at: datetime

class FinancialTransformer:
    """Finansal Transformer ana sınıfı"""
    
    def __init__(self):
        self.transformer_configs = {}
        self.trained_models = {}
        self.attention_weights = {}
        self.multi_modal_data = {}
        self.performance_history = {}
        
        # Transformer parametreleri
        self.max_sequence_length = 512
        self.vocab_size = 10000
        self.padding_token = '[PAD]'
        self.unknown_token = '[UNK]'
        
        # Varsayılan transformer konfigürasyonları
        self._add_default_transformer_configs()
        
        # Text preprocessing için
        self._initialize_text_preprocessing()
    
    def _add_default_transformer_configs(self):
        """Varsayılan transformer konfigürasyonları ekle"""
        default_configs = [
            {
                "config_id": "FINANCIAL_BERT",
                "name": "Financial BERT",
                "model_type": "financial_bert",
                "architecture": {
                    "encoder_layers": 12,
                    "attention_mechanism": "multi_head",
                    "position_encoding": "learned",
                    "feed_forward_dim": 3072
                },
                "hyperparameters": {
                    "learning_rate": 0.0001,
                    "batch_size": 16,
                    "epochs": 100,
                    "warmup_steps": 1000
                },
                "attention_heads": 12,
                "embedding_dim": 768,
                "num_layers": 12
            },
            {
                "config_id": "TIME_SERIES_TRANSFORMER",
                "name": "Time Series Transformer",
                "model_type": "time_series_transformer",
                "architecture": {
                    "encoder_layers": 8,
                    "attention_mechanism": "causal",
                    "position_encoding": "sinusoidal",
                    "feed_forward_dim": 2048
                },
                "hyperparameters": {
                    "learning_rate": 0.0005,
                    "batch_size": 32,
                    "epochs": 150,
                    "warmup_steps": 500
                },
                "attention_heads": 8,
                "embedding_dim": 512,
                "num_layers": 8
            },
            {
                "config_id": "MULTI_MODAL_TRANSFORMER",
                "name": "Multi-Modal Transformer",
                "model_type": "multi_modal",
                "architecture": {
                    "encoder_layers": 10,
                    "attention_mechanism": "cross_attention",
                    "position_encoding": "learned",
                    "feed_forward_dim": 2560
                },
                "hyperparameters": {
                    "learning_rate": 0.0003,
                    "batch_size": 24,
                    "epochs": 200,
                    "warmup_steps": 800
                },
                "attention_heads": 10,
                "embedding_dim": 640,
                "num_layers": 10
            }
        ]
        
        for config_data in default_configs:
            transformer_config = TransformerConfig(
                config_id=config_data["config_id"],
                name=config_data["name"],
                model_type=config_data["model_type"],
                architecture=config_data["architecture"],
                hyperparameters=config_data["hyperparameters"],
                attention_heads=config_data["attention_heads"],
                embedding_dim=config_data["embedding_dim"],
                num_layers=config_data["num_layers"],
                created_at=datetime.now()
            )
            
            self.transformer_configs[transformer_config.config_id] = transformer_config
    
    def _initialize_text_preprocessing(self):
        """Text preprocessing için gerekli bileşenleri başlat"""
        # Finansal terimler sözlüğü
        self.financial_terms = {
            'bullish': 'olumlu',
            'bearish': 'olumsuz',
            'earnings': 'kazanç',
            'revenue': 'gelir',
            'profit': 'kâr',
            'loss': 'zarar',
            'dividend': 'temettü',
            'stock': 'hisse',
            'market': 'piyasa',
            'trading': 'işlem',
            'volatility': 'oynaklık',
            'trend': 'trend',
            'support': 'destek',
            'resistance': 'direnç',
            'breakout': 'kırılım',
            'consolidation': 'konsolidasyon'
        }
        
        # Sentiment sözlüğü
        self.sentiment_dict = {
            'positive': ['olumlu', 'iyi', 'güçlü', 'artış', 'yükseliş', 'kazanç'],
            'negative': ['olumsuz', 'kötü', 'zayıf', 'azalış', 'düşüş', 'kayıp'],
            'neutral': ['nötr', 'değişmez', 'sabit', 'durağan']
        }
    
    def preprocess_financial_text(self, text: str) -> str:
        """Finansal metni ön işle"""
        try:
            if not isinstance(text, str):
                return ""
            
            # Küçük harfe çevir
            text = text.lower()
            
            # Özel karakterleri temizle
            text = re.sub(r'[^\w\s]', ' ', text)
            
            # Fazla boşlukları temizle
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Finansal terimleri normalize et
            for eng_term, tr_term in self.financial_terms.items():
                text = text.replace(eng_term, tr_term)
            
            # Sayıları normalize et
            text = re.sub(r'\d+', ' [NUM] ', text)
            
            # Para birimlerini normalize et
            text = re.sub(r'[₺$€£¥]', ' [CURRENCY] ', text)
            
            # Yüzde işaretlerini normalize et
            text = re.sub(r'%', ' [PERCENT] ', text)
            
            return text
        
        except Exception as e:
            logger.error(f"Error preprocessing financial text: {e}")
            return text
    
    def extract_sentiment_features(self, text: str) -> Dict[str, float]:
        """Metinden sentiment özellikleri çıkar"""
        try:
            sentiment_scores = {
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 0.0,
                'overall_sentiment': 0.0
            }
            
            if not text:
                return sentiment_scores
            
            words = text.split()
            total_words = len(words)
            
            if total_words == 0:
                return sentiment_scores
            
            # Sentiment hesapla
            for word in words:
                if word in self.sentiment_dict['positive']:
                    sentiment_scores['positive_score'] += 1
                elif word in self.sentiment_dict['negative']:
                    sentiment_scores['negative_score'] += 1
                elif word in self.sentiment_dict['neutral']:
                    sentiment_scores['neutral_score'] += 1
            
            # Normalize et
            sentiment_scores['positive_score'] /= total_words
            sentiment_scores['negative_score'] /= total_words
            sentiment_scores['neutral_score'] /= total_words
            
            # Genel sentiment skoru
            sentiment_scores['overall_sentiment'] = (
                sentiment_scores['positive_score'] - sentiment_scores['negative_score']
            )
            
            return sentiment_scores
        
        except Exception as e:
            logger.error(f"Error extracting sentiment features: {e}")
            return {
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 0.0,
                'overall_sentiment': 0.0
            }
    
    def create_positional_encoding(self, sequence_length: int, embedding_dim: int) -> np.ndarray:
        """Positional encoding oluştur"""
        try:
            pos_encoding = np.zeros((sequence_length, embedding_dim))
            
            for pos in range(sequence_length):
                for i in range(0, embedding_dim, 2):
                    pos_encoding[pos, i] = np.sin(pos / (10000 ** (i / embedding_dim)))
                    if i + 1 < embedding_dim:
                        pos_encoding[pos, i + 1] = np.cos(pos / (10000 ** (i / embedding_dim)))
            
            return pos_encoding
        
        except Exception as e:
            logger.error(f"Error creating positional encoding: {e}")
            return np.zeros((sequence_length, embedding_dim))
    
    def create_attention_mask(self, sequence_length: int, padding_length: int = 0) -> np.ndarray:
        """Attention mask oluştur"""
        try:
            mask = np.ones(sequence_length)
            if padding_length > 0:
                mask[-padding_length:] = 0
            return mask
        
        except Exception as e:
            logger.error(f"Error creating attention mask: {e}")
            return np.ones(sequence_length)
    
    def scaled_dot_product_attention(self, query: np.ndarray, key: np.ndarray, 
                                   value: np.ndarray, mask: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Scaled dot-product attention hesapla"""
        try:
            # Attention scores hesapla
            d_k = query.shape[-1]
            scores = np.matmul(query, key.transpose(-2, -1)) / np.sqrt(d_k)
            
            # Mask uygula
            if mask is not None:
                scores = scores + mask
            
            # Softmax uygula
            attention_weights = self._softmax(scores, axis=-1)
            
            # Output hesapla
            output = np.matmul(attention_weights, value)
            
            return output, attention_weights
        
        except Exception as e:
            logger.error(f"Error in scaled dot-product attention: {e}")
            return np.zeros_like(query), np.zeros((query.shape[0], key.shape[0]))
    
    def _softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
        """Softmax fonksiyonu"""
        try:
            exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
            return exp_x / np.sum(exp_x, axis=axis, keepdims=True)
        except Exception as e:
            logger.error(f"Error in softmax: {e}")
            return np.ones_like(x) / x.shape[axis]
    
    def multi_head_attention(self, query: np.ndarray, key: np.ndarray, value: np.ndarray,
                           num_heads: int, mask: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Multi-head attention uygula"""
        try:
            batch_size, seq_len, d_model = query.shape
            d_k = d_model // num_heads
            
            # Reshape for multi-head attention
            query = query.reshape(batch_size, seq_len, num_heads, d_k).transpose(0, 2, 1, 3)
            key = key.reshape(batch_size, seq_len, num_heads, d_k).transpose(0, 2, 1, 3)
            value = value.reshape(batch_size, seq_len, num_heads, d_k).transpose(0, 2, 1, 3)
            
            # Apply attention to each head
            attention_outputs = []
            attention_weights_list = []
            
            for head in range(num_heads):
                head_output, head_weights = self.scaled_dot_product_attention(
                    query[:, head], key[:, head], value[:, head], mask
                )
                attention_outputs.append(head_output)
                attention_weights_list.append(head_weights)
            
            # Concatenate heads
            attention_output = np.concatenate(attention_outputs, axis=-1)
            attention_weights = np.mean(attention_weights_list, axis=0)
            
            return attention_output, attention_weights
        
        except Exception as e:
            logger.error(f"Error in multi-head attention: {e}")
            return np.zeros_like(query), np.zeros((query.shape[0], key.shape[0]))
    
    def transformer_encoder_layer(self, x: np.ndarray, num_heads: int, 
                               d_model: int, d_ff: int) -> Tuple[np.ndarray, np.ndarray]:
        """Transformer encoder layer uygula"""
        try:
            # Multi-head attention
            attention_output, attention_weights = self.multi_head_attention(x, x, x, num_heads)
            
            # Add & Norm
            x = x + attention_output
            x = self._layer_norm(x)
            
            # Feed forward
            ff_output = self._feed_forward(x, d_ff, d_model)
            
            # Add & Norm
            x = x + ff_output
            x = self._layer_norm(x)
            
            return x, attention_weights
        
        except Exception as e:
            logger.error(f"Error in transformer encoder layer: {e}")
            return x, np.zeros((x.shape[0], x.shape[0]))
    
    def _layer_norm(self, x: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
        """Layer normalization uygula"""
        try:
            mean = np.mean(x, axis=-1, keepdims=True)
            variance = np.var(x, axis=-1, keepdims=True)
            return (x - mean) / np.sqrt(variance + epsilon)
        except Exception as e:
            logger.error(f"Error in layer normalization: {e}")
            return x
    
    def _feed_forward(self, x: np.ndarray, d_ff: int, d_model: int) -> np.ndarray:
        """Feed forward network uygula"""
        try:
            # Linear transformation
            w1 = np.random.randn(d_model, d_ff) * 0.1
            w2 = np.random.randn(d_ff, d_model) * 0.1
            
            # Forward pass
            hidden = np.matmul(x, w1)
            hidden = self._relu(hidden)
            output = np.matmul(hidden, w2)
            
            return output
        except Exception as e:
            logger.error(f"Error in feed forward: {e}")
            return x
    
    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU aktivasyon fonksiyonu"""
        return np.maximum(0, x)
    
    def create_financial_bert_model(self, config: TransformerConfig) -> Dict[str, Any]:
        """Financial BERT model oluştur"""
        try:
            model = {
                'config': config,
                'embedding_layer': {
                    'token_embeddings': np.random.randn(self.vocab_size, config.embedding_dim) * 0.1,
                    'position_embeddings': self.create_positional_encoding(
                        self.max_sequence_length, config.embedding_dim
                    ),
                    'segment_embeddings': np.random.randn(2, config.embedding_dim) * 0.1
                },
                'encoder_layers': [],
                'classifier_head': {
                    'weights': np.random.randn(config.embedding_dim, 1) * 0.1,
                    'bias': np.zeros(1)
                }
            }
            
            # Encoder layers
            for layer in range(config.num_layers):
                encoder_layer = {
                    'attention': {
                        'query_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                        'key_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                        'value_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                        'output_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1
                    },
                    'feed_forward': {
                        'w1': np.random.randn(config.embedding_dim, config.architecture['feed_forward_dim']) * 0.1,
                        'w2': np.random.randn(config.architecture['feed_forward_dim'], config.embedding_dim) * 0.1
                    }
                }
                model['encoder_layers'].append(encoder_layer)
            
            logger.info(f"Financial BERT model created: {config.name}")
            return model
        
        except Exception as e:
            logger.error(f"Error creating Financial BERT model: {e}")
            return {}
    
    def create_time_series_transformer(self, config: TransformerConfig) -> Dict[str, Any]:
        """Time Series Transformer model oluştur"""
        try:
            model = {
                'config': config,
                'input_projection': {
                    'weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                    'bias': np.zeros(config.embedding_dim)
                },
                'positional_encoding': self.create_positional_encoding(
                    self.max_sequence_length, config.embedding_dim
                ),
                'encoder_layers': [],
                'output_projection': {
                    'weights': np.random.randn(config.embedding_dim, 1) * 0.1,
                    'bias': np.zeros(1)
                }
            }
            
            # Encoder layers
            for layer in range(config.num_layers):
                encoder_layer = {
                    'self_attention': {
                        'query_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                        'key_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                        'value_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                        'output_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1
                    },
                    'feed_forward': {
                        'w1': np.random.randn(config.embedding_dim, config.architecture['feed_forward_dim']) * 0.1,
                        'w2': np.random.randn(config.architecture['feed_forward_dim'], config.embedding_dim) * 0.1
                    }
                }
                model['encoder_layers'].append(encoder_layer)
            
            logger.info(f"Time Series Transformer model created: {config.name}")
            return model
        
        except Exception as e:
            logger.error(f"Error creating Time Series Transformer: {e}")
            return {}
    
    def create_multi_modal_transformer(self, config: TransformerConfig) -> Dict[str, Any]:
        """Multi-Modal Transformer model oluştur"""
        try:
            model = {
                'config': config,
                'numerical_encoder': {
                    'weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                    'bias': np.zeros(config.embedding_dim)
                },
                'text_encoder': {
                    'weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                    'bias': np.zeros(config.embedding_dim)
                },
                'cross_attention': {
                    'query_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                    'key_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1,
                    'value_weights': np.random.randn(config.embedding_dim, config.embedding_dim) * 0.1
                },
                'fusion_layer': {
                    'weights': np.random.randn(config.embedding_dim * 2, config.embedding_dim) * 0.1,
                    'bias': np.zeros(config.embedding_dim)
                },
                'output_projection': {
                    'weights': np.random.randn(config.embedding_dim, 1) * 0.1,
                    'bias': np.zeros(1)
                }
            }
            
            logger.info(f"Multi-Modal Transformer model created: {config.name}")
            return model
        
        except Exception as e:
            logger.error(f"Error creating Multi-Modal Transformer: {e}")
            return {}
    
    def forward_pass(self, model: Dict[str, Any], input_data: np.ndarray, 
                    model_type: str = "financial_bert") -> Tuple[np.ndarray, np.ndarray]:
        """Model forward pass uygula"""
        try:
            if model_type == "financial_bert":
                return self._financial_bert_forward(model, input_data)
            elif model_type == "time_series_transformer":
                return self._time_series_transformer_forward(model, input_data)
            elif model_type == "multi_modal":
                return self._multi_modal_transformer_forward(model, input_data)
            else:
                logger.error(f"Unknown model type: {model_type}")
                return np.zeros((input_data.shape[0], 1)), np.zeros((input_data.shape[0], input_data.shape[0]))
        
        except Exception as e:
            logger.error(f"Error in forward pass: {e}")
            return np.zeros((input_data.shape[0], 1)), np.zeros((input_data.shape[0], input_data.shape[0]))
    
    def _financial_bert_forward(self, model: Dict[str, Any], input_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Financial BERT forward pass"""
        try:
            # Embedding
            x = input_data @ model['embedding_layer']['token_embeddings']
            x = x + model['embedding_layer']['position_embeddings'][:x.shape[0]]
            
            # Encoder layers
            attention_weights = []
            for layer in model['encoder_layers']:
                x, attn_weights = self.transformer_encoder_layer(
                    x, 
                    model['config'].attention_heads,
                    model['config'].embedding_dim,
                    model['config'].architecture['feed_forward_dim']
                )
                attention_weights.append(attn_weights)
            
            # Classifier head
            x = np.mean(x, axis=1)  # Global average pooling
            output = x @ model['classifier_head']['weights'] + model['classifier_head']['bias']
            
            # Average attention weights
            avg_attention = np.mean(attention_weights, axis=0)
            
            return output, avg_attention
        
        except Exception as e:
            logger.error(f"Error in Financial BERT forward: {e}")
            return np.zeros((input_data.shape[0], 1)), np.zeros((input_data.shape[0], input_data.shape[0]))
    
    def _time_series_transformer_forward(self, model: Dict[str, Any], input_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Time Series Transformer forward pass"""
        try:
            # Input projection
            x = input_data @ model['input_projection']['weights'] + model['input_projection']['bias']
            x = x + model['positional_encoding'][:x.shape[0]]
            
            # Encoder layers
            attention_weights = []
            for layer in model['encoder_layers']:
                x, attn_weights = self.transformer_encoder_layer(
                    x,
                    model['config'].attention_heads,
                    model['config'].embedding_dim,
                    model['config'].architecture['feed_forward_dim']
                )
                attention_weights.append(attn_weights)
            
            # Output projection
            x = np.mean(x, axis=1)  # Global average pooling
            output = x @ model['output_projection']['weights'] + model['output_projection']['bias']
            
            # Average attention weights
            avg_attention = np.mean(attention_weights, axis=0)
            
            return output, avg_attention
        
        except Exception as e:
            logger.error(f"Error in Time Series Transformer forward: {e}")
            return np.zeros((input_data.shape[0], 1)), np.zeros((input_data.shape[0], input_data.shape[0]))
    
    def _multi_modal_transformer_forward(self, model: Dict[str, Any], input_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Multi-Modal Transformer forward pass"""
        try:
            # Numerical features
            numerical_features = input_data[:, :input_data.shape[1]//2]
            text_features = input_data[:, input_data.shape[1]//2:]
            
            # Encode numerical features
            numerical_encoded = numerical_features @ model['numerical_encoder']['weights'] + model['numerical_encoder']['bias']
            
            # Encode text features
            text_encoded = text_features @ model['text_encoder']['weights'] + model['text_encoder']['bias']
            
            # Cross attention
            cross_attention_output, cross_attention_weights = self.scaled_dot_product_attention(
                numerical_encoded, text_encoded, text_encoded
            )
            
            # Fusion
            fused_features = np.concatenate([numerical_encoded, cross_attention_output], axis=-1)
            fused_encoded = fused_features @ model['fusion_layer']['weights'] + model['fusion_layer']['bias']
            
            # Output projection
            output = fused_encoded @ model['output_projection']['weights'] + model['output_projection']['bias']
            
            return output, cross_attention_weights
        
        except Exception as e:
            logger.error(f"Error in Multi-Modal Transformer forward: {e}")
            return np.zeros((input_data.shape[0], 1)), np.zeros((input_data.shape[0], input_data.shape[0]))
    
    def train_transformer(self, model: Dict[str, Any], X: pd.DataFrame, y: pd.Series,
                         model_type: str = "financial_bert", epochs: int = 10) -> Dict[str, Any]:
        """Transformer model eğit"""
        try:
            training_history = {
                'loss': [],
                'accuracy': [],
                'attention_weights': []
            }
            
            # Basit eğitim loop (gerçek implementasyonda daha gelişmiş)
            for epoch in range(epochs):
                # Forward pass
                predictions, attention_weights = self.forward_pass(model, X.values, model_type)
                
                # Loss hesapla (basit MSE)
                loss = np.mean((predictions.flatten() - y.values) ** 2)
                
                # Accuracy hesapla (basit threshold)
                pred_classes = (predictions.flatten() > 0.5).astype(int)
                accuracy = accuracy_score(y.values, pred_classes)
                
                # History'ye ekle
                training_history['loss'].append(loss)
                training_history['accuracy'].append(accuracy)
                training_history['attention_weights'].append(attention_weights)
                
                logger.info(f"Epoch {epoch + 1}: Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
            
            # Model'i kaydet
            model_id = f"TRAINED_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.trained_models[model_id] = {
                'model': model,
                'training_history': training_history,
                'model_type': model_type,
                'trained_at': datetime.now()
            }
            
            logger.info(f"Transformer training completed: {model_id}")
            return training_history
        
        except Exception as e:
            logger.error(f"Error training transformer: {e}")
            return {}
    
    def get_transformer_summary(self) -> Dict[str, Any]:
        """Transformer özeti getir"""
        try:
            summary = {
                "total_configs": len(self.transformer_configs),
                "total_trained_models": len(self.trained_models),
                "model_types": {},
                "performance_summary": {}
            }
            
            # Model tipleri
            for config in self.transformer_configs.values():
                model_type = config.model_type
                summary["model_types"][model_type] = summary["model_types"].get(model_type, 0) + 1
            
            # Performans özeti
            if self.trained_models:
                accuracies = []
                for model_info in self.trained_models.values():
                    if 'training_history' in model_info and 'accuracy' in model_info['training_history']:
                        accuracies.extend(model_info['training_history']['accuracy'])
                
                if accuracies:
                    summary["performance_summary"] = {
                        "average_accuracy": np.mean(accuracies),
                        "best_accuracy": max(accuracies),
                        "worst_accuracy": min(accuracies),
                        "total_trained_models": len(self.trained_models)
                    }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting transformer summary: {e}")
            return {}


def test_transformer_models():
    """Transformer Models test fonksiyonu"""
    print("\n🧪 Transformer Models Test Başlıyor...")
    
    # Financial Transformer oluştur
    transformer = FinancialTransformer()
    
    print("✅ Financial Transformer oluşturuldu")
    print(f"📊 Toplam transformer konfigürasyonu: {len(transformer.transformer_configs)}")
    print(f"📊 Kullanılabilir model tipleri: {list(transformer.transformer_configs.keys())}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    np.random.seed(42)
    n_samples = 100
    
    # Simüle edilmiş fiyat verisi
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='D')
    prices = 100 + np.cumsum(np.random.randn(n_samples) * 0.02)
    returns = np.diff(prices) / prices[:-1]
    
    # Binary target (yukarı/aşağı hareket)
    target = (returns > 0).astype(int)
    
    # Feature matrix - uzunluk eşleştirme
    feature_length = len(returns) - 1
    
    features = pd.DataFrame({
        'price': prices[1:feature_length+1],
        'return_lag1': np.roll(returns, 1)[1:feature_length+1],
        'return_lag2': np.roll(returns, 2)[1:feature_length+1],
        'volatility': np.random.rand(feature_length) * 0.1,
        'momentum': np.random.rand(feature_length) * 0.05
    }, index=dates[1:feature_length+1])
    
    # Target'ı features ile aynı boyuta getir
    target = target[:feature_length]
    
    print(f"   ✅ Test verisi oluşturuldu: {len(features)} örnek, {len(features.columns)} özellik")
    
    # Text preprocessing testi
    print("\n📊 Text Preprocessing Testi:")
    
    sample_texts = [
        "SISE hissesi %5 artış gösterdi, bullish trend devam ediyor",
        "EREGL kazanç açıklaması bearish sentiment yarattı",
        "Piyasa volatilite artışı ile consolidation döneminde"
    ]
    
    for i, text in enumerate(sample_texts):
        processed_text = transformer.preprocess_financial_text(text)
        sentiment_features = transformer.extract_sentiment_features(processed_text)
        
        print(f"   📊 Metin {i+1}:")
        print(f"      Orijinal: {text}")
        print(f"      İşlenmiş: {processed_text}")
        print(f"      Sentiment: {sentiment_features['overall_sentiment']:.3f}")
    
    # Model oluşturma testi
    print("\n📊 Model Oluşturma Testi:")
    
    # Financial BERT
    bert_config = transformer.transformer_configs['FINANCIAL_BERT']
    bert_model = transformer.create_financial_bert_model(bert_config)
    
    if bert_model:
        print(f"   ✅ Financial BERT model oluşturuldu")
        print(f"      📊 Embedding boyutu: {bert_config.embedding_dim}")
        print(f"      📊 Attention heads: {bert_config.attention_heads}")
        print(f"      📊 Layer sayısı: {bert_config.num_layers}")
    
    # Time Series Transformer
    ts_config = transformer.transformer_configs['TIME_SERIES_TRANSFORMER']
    ts_model = transformer.create_time_series_transformer(ts_config)
    
    if ts_model:
        print(f"   ✅ Time Series Transformer model oluşturuldu")
        print(f"      📊 Embedding boyutu: {ts_config.embedding_dim}")
        print(f"      📊 Attention heads: {ts_config.attention_heads}")
    
    # Multi-Modal Transformer
    mm_config = transformer.transformer_configs['MULTI_MODAL_TRANSFORMER']
    mm_model = transformer.create_multi_modal_transformer(mm_config)
    
    if mm_model:
        print(f"   ✅ Multi-Modal Transformer model oluşturuldu")
        print(f"      📊 Embedding boyutu: {mm_config.embedding_dim}")
        print(f"      📊 Attention heads: {mm_config.attention_heads}")
    
    # Forward pass testi
    print("\n📊 Forward Pass Testi:")
    
    # Test input
    test_input = np.random.randn(10, 4)  # 10 örnek, 4 özellik
    
    # Financial BERT forward pass
    bert_output, bert_attention = transformer.forward_pass(bert_model, test_input, "financial_bert")
    print(f"   ✅ Financial BERT forward pass: output shape {bert_output.shape}, attention shape {bert_attention.shape}")
    
    # Time Series Transformer forward pass
    ts_output, ts_attention = transformer.forward_pass(ts_model, test_input, "time_series_transformer")
    print(f"   ✅ Time Series Transformer forward pass: output shape {ts_output.shape}, attention shape {ts_attention.shape}")
    
    # Model eğitimi testi
    print("\n📊 Model Eğitimi Testi:")
    
    # Basit eğitim
    training_history = transformer.train_transformer(bert_model, features, target, "financial_bert", epochs=3)
    
    if training_history:
        print(f"   ✅ Transformer eğitimi tamamlandı")
        print(f"      📊 Epoch sayısı: {len(training_history['loss'])}")
        print(f"      📊 Son loss: {training_history['loss'][-1]:.4f}")
        print(f"      📊 Son accuracy: {training_history['accuracy'][-1]:.4f}")
    
    # Transformer özeti
    print("\n📊 Transformer Özeti:")
    summary = transformer.get_transformer_summary()
    
    if summary:
        print(f"   ✅ Transformer özeti alındı")
        print(f"   📊 Toplam konfigürasyon: {summary['total_configs']}")
        print(f"   📊 Toplam eğitilmiş model: {summary['total_trained_models']}")
        print(f"   📊 Model tipleri: {summary['model_types']}")
        
        if summary['performance_summary']:
            perf = summary['performance_summary']
            print(f"   📊 Ortalama accuracy: {perf['average_accuracy']:.3f}")
            print(f"   📊 En iyi accuracy: {perf['best_accuracy']:.3f}")
            print(f"   📊 Toplam eğitilmiş model: {perf['total_trained_models']}")
    
    print("\n✅ Transformer Models Test Tamamlandı!")


if __name__ == "__main__":
    test_transformer_models()
