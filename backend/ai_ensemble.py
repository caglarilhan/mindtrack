"""
PRD v2.0 - BIST AI Smart Trader
AI Ensemble Module

AI topluluk sistemi modülü:
- Multiple models
- Ensemble methods
- Dynamic weighting
- Performance monitoring
- Auto-ensemble
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from sklearn.ensemble import VotingClassifier, VotingRegressor, StackingClassifier, StackingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
import joblib
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class EnsembleModel:
    """Topluluk model"""
    name: str
    base_models: Dict[str, Any]
    ensemble_method: str
    weights: Optional[Dict[str, float]] = None
    performance_history: List[Dict] = None
    created_at: datetime = None
    last_updated: datetime = None

@dataclass
class EnsemblePrediction:
    """Topluluk tahmin sonucu"""
    final_prediction: Union[int, float]
    individual_predictions: Dict[str, Union[int, float]]
    ensemble_weights: Dict[str, float]
    confidence: float
    agreement_score: float
    model_contributions: Dict[str, float]

@dataclass
class EnsemblePerformance:
    """Topluluk performans metrikleri"""
    accuracy: float
    f1_score: float
    ensemble_score: float
    individual_scores: Dict[str, float]
    weight_optimization_score: float
    last_evaluation: datetime

class AIEnsemble:
    """
    AI Topluluk Sistemi
    
    PRD v2.0 gereksinimleri:
    - Çoklu model desteği
    - Topluluk yöntemleri
    - Dinamik ağırlıklandırma
    - Performans izleme
    - Otomatik topluluk oluşturma
    """
    
    def __init__(self, random_state: int = 42):
        """
        AI Ensemble başlatıcı
        
        Args:
            random_state: Rastgele sayı üreteci
        """
        self.random_state = random_state
        
        # Topluluk yöntemleri
        self.ENSEMBLE_METHODS = {
            "VOTING": "Voting",
            "STACKING": "Stacking",
            "BAGGING": "Bagging",
            "BOOSTING": "Boosting",
            "BLENDING": "Blending"
        }
        
        # Varsayılan topluluk ağırlıkları
        self.DEFAULT_WEIGHTS = {
            "RandomForest": 0.3,
            "GradientBoosting": 0.3,
            "LogisticRegression": 0.2,
            "SVM": 0.1,
            "NeuralNetwork": 0.1
        }
        
        # Topluluk modelleri
        self.ensemble_models = {}
        
        # Performans geçmişi
        self.performance_history = {}
        
        # Ağırlık optimizasyon parametreleri
        self.WEIGHT_OPTIMIZATION_ITERATIONS = 100
        self.WEIGHT_OPTIMIZATION_LEARNING_RATE = 0.01
    
    def create_voting_ensemble(self, name: str, models: Dict[str, Any],
                              weights: Optional[Dict[str, float]] = None,
                              voting: str = "soft") -> bool:
        """
        Voting topluluk oluşturma
        
        Args:
            name: Topluluk adı
            models: Model sözlüğü
            weights: Model ağırlıkları
            voting: Oylama türü
            
        Returns:
            bool: Oluşturma başarı durumu
        """
        try:
            # Model listesi oluştur
            estimators = [(model_name, model) for model_name, model in models.items()]
            
            # Voting classifier oluştur
            if len(estimators) > 1:
                ensemble = VotingClassifier(
                    estimators=estimators,
                    voting=voting,
                    weights=list(weights.values()) if weights else None
                )
            else:
                # Tek model varsa direkt kullan
                ensemble = list(models.values())[0]
            
            # Topluluk modeli kaydet
            ensemble_model = EnsembleModel(
                name=name,
                base_models=models,
                ensemble_method="VOTING",
                weights=weights,
                performance_history=[],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.ensemble_models[name] = {
                "ensemble": ensemble,
                "metadata": ensemble_model
            }
            
            return True
            
        except Exception as e:
            print(f"Voting topluluk oluşturma hatası: {str(e)}")
            return False
    
    def create_stacking_ensemble(self, name: str, models: Dict[str, Any],
                                meta_model: Optional[Any] = None,
                                cv_folds: int = 5) -> bool:
        """
        Stacking topluluk oluşturma
        
        Args:
            name: Topluluk adı
            models: Model sözlüğü
            meta_model: Meta model
            cv_folds: CV kat sayısı
            
        Returns:
            bool: Oluşturma başarı durumu
        """
        try:
            # Model listesi oluştur
            estimators = [(model_name, model) for model_name, model in models.items()]
            
            # Meta model seç
            if meta_model is None:
                if len(np.unique([model.predict([np.zeros(len(models))])[0] for model in models.values()])) <= 2:
                    meta_model = LogisticRegression(random_state=self.random_state)
                else:
                    meta_model = LinearRegression()
            
            # Stacking ensemble oluştur
            if len(estimators) > 1:
                ensemble = StackingClassifier(
                    estimators=estimators,
                    final_estimator=meta_model,
                    cv=cv_folds,
                    n_jobs=-1
                )
            else:
                ensemble = list(models.values())[0]
            
            # Topluluk modeli kaydet
            ensemble_model = EnsembleModel(
                name=name,
                base_models=models,
                ensemble_method="STACKING",
                weights=None,  # Stacking'de ağırlık yok
                performance_history=[],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.ensemble_models[name] = {
                "ensemble": ensemble,
                "metadata": ensemble_model
            }
            
            return True
            
        except Exception as e:
            print(f"Stacking topluluk oluşturma hatası: {str(e)}")
            return False
    
    def create_blending_ensemble(self, name: str, models: Dict[str, Any],
                                validation_split: float = 0.2) -> bool:
        """
        Blending topluluk oluşturma
        
        Args:
            name: Topluluk adı
            models: Model sözlüğü
            validation_split: Doğrulama bölme oranı
            
        Returns:
            bool: Oluşturma başarı durumu
        """
        try:
            # Blending için özel sınıf oluştur
            class BlendingEnsemble:
                def __init__(self, models, validation_split=0.2):
                    self.models = models
                    self.validation_split = validation_split
                    self.meta_model = None
                    self.is_fitted = False
                
                def fit(self, X, y):
                    # Veriyi böl
                    split_idx = int(len(X) * (1 - self.validation_split))
                    X_train, X_val = X[:split_idx], X[split_idx:]
                    y_train, y_val = y[:split_idx], y[split_idx:]
                    
                    # Base modelleri eğit
                    for model_name, model in self.models.items():
                        model.fit(X_train, y_train)
                    
                    # Validation set üzerinde tahminler
                    val_predictions = []
                    for model_name, model in self.models.items():
                        if hasattr(model, 'predict_proba'):
                            pred = model.predict_proba(X_val)[:, 1]
                        else:
                            pred = model.predict(X_val)
                        val_predictions.append(pred)
                    
                    # Meta model eğit
                    val_predictions = np.column_stack(val_predictions)
                    if len(np.unique(y_val)) <= 2:
                        self.meta_model = LogisticRegression(random_state=42)
                    else:
                        self.meta_model = LinearRegression()
                    
                    self.meta_model.fit(val_predictions, y_val)
                    self.is_fitted = True
                    return self
                
                def predict(self, X):
                    if not self.is_fitted:
                        raise ValueError("Model henüz eğitilmemiş")
                    
                    # Base model tahminleri
                    base_predictions = []
                    for model_name, model in self.models.items():
                        if hasattr(model, 'predict_proba'):
                            pred = model.predict_proba(X)[:, 1]
                        else:
                            pred = model.predict(X)
                        base_predictions.append(pred)
                    
                    # Meta model ile final tahmin
                    base_predictions = np.column_stack(base_predictions)
                    return self.meta_model.predict(base_predictions)
            
            # Blending ensemble oluştur
            ensemble = BlendingEnsemble(models, validation_split)
            
            # Topluluk modeli kaydet
            ensemble_model = EnsembleModel(
                name=name,
                base_models=models,
                ensemble_method="BLENDING",
                weights=None,
                performance_history=[],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.ensemble_models[name] = {
                "ensemble": ensemble,
                "metadata": ensemble_model
            }
            
            return True
            
        except Exception as e:
            print(f"Blending topluluk oluşturma hatası: {str(e)}")
            return False
    
    def make_ensemble_prediction(self, ensemble_name: str, X: np.ndarray,
                                return_individual: bool = True) -> EnsemblePrediction:
        """
        Topluluk tahmin yapma
        
        Args:
            ensemble_name: Topluluk adı
            X: Özellik matrisi
            return_individual: Bireysel tahminleri döndür
            
        Returns:
            EnsemblePrediction: Topluluk tahmin sonucu
        """
        if ensemble_name not in self.ensemble_models:
            raise ValueError(f"Topluluk bulunamadı: {ensemble_name}")
        
        ensemble_info = self.ensemble_models[ensemble_name]
        ensemble = ensemble_info["ensemble"]
        metadata = ensemble_info["metadata"]
        
        try:
            # Final tahmin
            final_prediction = ensemble.predict(X)
            
            # Bireysel tahminler
            individual_predictions = {}
            if return_individual:
                for model_name, model in metadata.base_models.items():
                    try:
                        if hasattr(model, 'predict_proba'):
                            pred = model.predict_proba(X)[:, 1]
                        else:
                            pred = model.predict(X)
                        individual_predictions[model_name] = pred[0] if hasattr(pred, '__len__') else pred
                    except Exception as e:
                        print(f"Bireysel tahmin hatası ({model_name}): {str(e)}")
                        individual_predictions[model_name] = 0.0
            
            # Ağırlıklar
            ensemble_weights = metadata.weights or self.DEFAULT_WEIGHTS
            
            # Güvenilirlik hesapla
            if len(individual_predictions) > 1:
                predictions_array = np.array(list(individual_predictions.values()))
                confidence = 1.0 - np.std(predictions_array) / (np.max(predictions_array) - np.min(predictions_array) + 1e-8)
                confidence = max(0.0, min(1.0, confidence))
            else:
                confidence = 1.0
            
            # Anlaşma skoru
            if len(individual_predictions) > 1:
                predictions_array = np.array(list(individual_predictions.values()))
                agreement_score = 1.0 - (np.std(predictions_array) / np.mean(np.abs(predictions_array) + 1e-8))
                agreement_score = max(0.0, min(1.0, agreement_score))
            else:
                agreement_score = 1.0
            
            # Model katkıları
            model_contributions = {}
            if metadata.weights:
                total_weight = sum(metadata.weights.values())
                for model_name, weight in metadata.weights.items():
                    model_contributions[model_name] = weight / total_weight
            
            return EnsemblePrediction(
                final_prediction=final_prediction[0] if hasattr(final_prediction, '__len__') else final_prediction,
                individual_predictions=individual_predictions,
                ensemble_weights=ensemble_weights,
                confidence=confidence,
                agreement_score=agreement_score,
                model_contributions=model_contributions
            )
            
        except Exception as e:
            print(f"Topluluk tahmin hatası: {str(e)}")
            return EnsemblePrediction(
                final_prediction=0.0,
                individual_predictions={},
                ensemble_weights={},
                confidence=0.0,
                agreement_score=0.0,
                model_contributions={}
            )
    
    def optimize_weights(self, ensemble_name: str, X: np.ndarray, y: np.ndarray,
                        optimization_method: str = "gradient") -> Dict[str, float]:
        """
        Topluluk ağırlıklarını optimize etme
        
        Args:
            ensemble_name: Topluluk adı
            X: Özellik matrisi
            y: Hedef değişken
            optimization_method: Optimizasyon metodu
            
        Returns:
            Dict: Optimize edilmiş ağırlıklar
        """
        if ensemble_name not in self.ensemble_models:
            raise ValueError(f"Topluluk bulunamadı: {ensemble_name}")
        
        ensemble_info = self.ensemble_models[ensemble_name]
        metadata = ensemble_info["metadata"]
        
        if not metadata.weights:
            print("Bu topluluk türünde ağırlık optimizasyonu desteklenmiyor")
            return {}
        
        try:
            if optimization_method == "gradient":
                # Gradient-based ağırlık optimizasyonu
                weights = np.array(list(metadata.weights.values()))
                model_names = list(metadata.weights.keys())
                
                # Bireysel tahminler
                individual_predictions = []
                for model_name in model_names:
                    model = metadata.base_models[model_name]
                    if hasattr(model, 'predict_proba'):
                        pred = model.predict_proba(X)[:, 1]
                    else:
                        pred = model.predict(X)
                    individual_predictions.append(pred)
                
                individual_predictions = np.array(individual_predictions)
                
                # Gradient descent ile ağırlık optimizasyonu
                for iteration in range(self.WEIGHT_OPTIMIZATION_ITERATIONS):
                    # Ağırlıklı tahmin
                    weighted_pred = np.sum(weights[:, np.newaxis] * individual_predictions, axis=0)
                    
                    # Hata hesapla
                    if len(np.unique(y)) <= 2:  # Sınıflandırma
                        error = 1 - accuracy_score(y, (weighted_pred > 0.5).astype(int))
                    else:  # Regresyon
                        error = mean_squared_error(y, weighted_pred)
                    
                    # Gradient hesapla
                    gradients = []
                    for i in range(len(weights)):
                        # Ağırlık değişimi
                        weights_temp = weights.copy()
                        weights_temp[i] += 0.01
                        weighted_pred_temp = np.sum(weights_temp[:, np.newaxis] * individual_predictions, axis=0)
                        
                        if len(np.unique(y)) <= 2:
                            error_temp = 1 - accuracy_score(y, (weighted_pred_temp > 0.5).astype(int))
                        else:
                            error_temp = mean_squared_error(y, weighted_pred_temp)
                        
                        gradient = (error_temp - error) / 0.01
                        gradients.append(gradient)
                    
                    # Ağırlıkları güncelle
                    gradients = np.array(gradients)
                    weights -= self.WEIGHT_OPTIMIZATION_LEARNING_RATE * gradients
                    
                    # Ağırlıkları normalize et
                    weights = np.maximum(weights, 0)  # Negatif ağırlık yok
                    weights = weights / np.sum(weights)  # Toplam 1
                
                # Sonuçları döndür
                optimized_weights = dict(zip(model_names, weights))
                
                # Metadata'yı güncelle
                metadata.weights = optimized_weights
                metadata.last_updated = datetime.now()
                
                return optimized_weights
                
            else:
                print(f"Desteklenmeyen optimizasyon metodu: {optimization_method}")
                return metadata.weights
                
        except Exception as e:
            print(f"Ağırlık optimizasyonu hatası: {str(e)}")
            return metadata.weights
    
    def evaluate_ensemble(self, ensemble_name: str, X: np.ndarray, y: np.ndarray) -> EnsemblePerformance:
        """
        Topluluk performansını değerlendirme
        
        Args:
            ensemble_name: Topluluk adı
            X: Özellik matrisi
            y: Hedef değişken
            
        Returns:
            EnsemblePerformance: Topluluk performans metrikleri
        """
        if ensemble_name not in self.ensemble_models:
            raise ValueError(f"Topluluk bulunamadı: {ensemble_name}")
        
        ensemble_info = self.ensemble_models[ensemble_name]
        ensemble = ensemble_info["ensemble"]
        metadata = ensemble_info["metadata"]
        
        try:
            # Topluluk tahminleri
            ensemble_pred = ensemble.predict(X)
            
            # Bireysel model performansları
            individual_scores = {}
            for model_name, model in metadata.base_models.items():
                try:
                    model_pred = model.predict(X)
                    if len(np.unique(y)) <= 2:  # Sınıflandırma
                        score = f1_score(y, model_pred, average='weighted')
                    else:  # Regresyon
                        score = r2_score(y, model_pred)
                    individual_scores[model_name] = score
                except Exception as e:
                    print(f"Bireysel model değerlendirme hatası ({model_name}): {str(e)}")
                    individual_scores[model_name] = 0.0
            
            # Topluluk performansı
            if len(np.unique(y)) <= 2:  # Sınıflandırma
                accuracy = accuracy_score(y, ensemble_pred)
                f1 = f1_score(y, ensemble_pred, average='weighted')
            else:  # Regresyon
                accuracy = r2_score(y, ensemble_pred)
                f1 = 0.0  # Regresyonda F1 yok
            
            # Ağırlık optimizasyon skoru
            weight_optimization_score = 0.0
            if metadata.weights:
                # Ağırlıklı ortalama performans
                weighted_performance = 0.0
                total_weight = 0.0
                for model_name, weight in metadata.weights.items():
                    if model_name in individual_scores:
                        weighted_performance += weight * individual_scores[model_name]
                        total_weight += weight
                
                if total_weight > 0:
                    weight_optimization_score = weighted_performance / total_weight
            
            # Performans sonucu
            performance = EnsemblePerformance(
                accuracy=accuracy,
                f1_score=f1,
                ensemble_score=accuracy,  # Ana skor
                individual_scores=individual_scores,
                weight_optimization_score=weight_optimization_score,
                last_evaluation=datetime.now()
            )
            
            # Performans geçmişini güncelle
            metadata.performance_history.append({
                "accuracy": accuracy,
                "f1_score": f1,
                "ensemble_score": accuracy,
                "individual_scores": individual_scores,
                "weight_optimization_score": weight_optimization_score,
                "timestamp": datetime.now().isoformat()
            })
            
            # Genel performans geçmişini güncelle
            if ensemble_name not in self.performance_history:
                self.performance_history[ensemble_name] = []
            self.performance_history[ensemble_name].append(performance)
            
            return performance
            
        except Exception as e:
            print(f"Topluluk değerlendirme hatası: {str(e)}")
            return EnsemblePerformance(
                accuracy=0.0,
                f1_score=0.0,
                ensemble_score=0.0,
                individual_scores={},
                weight_optimization_score=0.0,
                last_evaluation=datetime.now()
            )
    
    def auto_create_ensemble(self, name: str, models: Dict[str, Any],
                            X: np.ndarray, y: np.ndarray,
                            method: str = "auto") -> bool:
        """
        Otomatik topluluk oluşturma
        
        Args:
            name: Topluluk adı
            models: Model sözlüğü
            X: Özellik matrisi
            y: Hedef değişken
            method: Topluluk yöntemi
            
        Returns:
            bool: Oluşturma başarı durumu
        """
        try:
            if method == "auto":
                # Otomatik yöntem seçimi
                if len(models) <= 2:
                    method = "voting"
                elif len(np.unique(y)) <= 2:  # Sınıflandırma
                    method = "stacking"
                else:  # Regresyon
                    method = "blending"
            
            # Topluluk oluştur
            if method == "voting":
                success = self.create_voting_ensemble(name, models)
            elif method == "stacking":
                success = self.create_stacking_ensemble(name, models)
            elif method == "blending":
                success = self.create_blending_ensemble(name, models)
            else:
                print(f"Desteklenmeyen yöntem: {method}")
                return False
            
            if success:
                # Performansı değerlendir
                performance = self.evaluate_ensemble(name, X, y)
                print(f"Otomatik topluluk oluşturuldu: {name} ({method})")
                print(f"Performans: {performance.ensemble_score:.4f}")
                
                # Ağırlık optimizasyonu (destekleniyorsa)
                if method == "voting":
                    optimized_weights = self.optimize_weights(name, X, y)
                    if optimized_weights:
                        print(f"Optimize edilmiş ağırlıklar: {optimized_weights}")
            
            return success
            
        except Exception as e:
            print(f"Otomatik topluluk oluşturma hatası: {str(e)}")
            return False
    
    def generate_ensemble_report(self) -> Dict:
        """
        Topluluk raporu oluşturma
        
        Returns:
            Dict: Topluluk raporu
        """
        print("🤖 AI Ensemble Raporu Oluşturuluyor...")
        
        if not self.ensemble_models:
            return {"error": "Henüz topluluk oluşturulmamış"}
        
        # Topluluk özeti
        ensemble_summary = {}
        for name, info in self.ensemble_models.items():
            metadata = info["metadata"]
            performance = None
            
            if metadata.performance_history:
                latest_performance = metadata.performance_history[-1]
                performance = {
                    "accuracy": latest_performance["accuracy"],
                    "f1_score": latest_performance["f1_score"],
                    "ensemble_score": latest_performance["ensemble_score"]
                }
            
            ensemble_summary[name] = {
                "method": metadata.ensemble_method,
                "base_models": list(metadata.base_models.keys()),
                "weights": metadata.weights,
                "performance": performance,
                "created_at": metadata.created_at.isoformat(),
                "last_updated": metadata.last_updated.isoformat()
            }
        
        # Performans analizi
        performance_analysis = {}
        for name, history in self.performance_history.items():
            if history:
                latest = history[-1]
                performance_analysis[name] = {
                    "current_score": latest.ensemble_score,
                    "individual_scores": latest.individual_scores,
                    "weight_optimization_score": latest.weight_optimization_score,
                    "evaluation_count": len(history)
                }
        
        # Rapor oluştur
        report = {
            "ensemble_summary": {
                "total_ensembles": len(self.ensemble_models),
                "methods_used": list(set(info["metadata"].ensemble_method for info in self.ensemble_models.values())),
                "total_base_models": sum(len(info["metadata"].base_models) for info in self.ensemble_models.values())
            },
            "ensemble_details": ensemble_summary,
            "performance_analysis": performance_analysis,
            "recommendations": {
                "best_ensemble": max(performance_analysis.items(), key=lambda x: x[1]["current_score"])[0] if performance_analysis else None,
                "weight_optimization_needed": any(info["metadata"].weights for info in self.ensemble_models.values()),
                "performance_trends": "stable" if len(self.performance_history) > 1 else "insufficient_data"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print("✅ AI Ensemble Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_ai_ensemble():
    """AI Ensemble test fonksiyonu"""
    print("🧪 AI Ensemble Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_samples = 500
    n_features = 15
    
    # Özellik matrisi
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    
    # Hedef değişken (sınıflandırma)
    y = ((X.iloc[:, 0] + X.iloc[:, 1] + X.iloc[:, 2]) > 0).astype(int)
    
    # Test modelleri
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    
    rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
    gb_model = GradientBoostingClassifier(n_estimators=50, random_state=42)
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    svm_model = SVC(random_state=42, probability=True)
    
    # Modelleri eğit
    models = {
        "RandomForest": rf_model,
        "GradientBoosting": gb_model,
        "LogisticRegression": lr_model,
        "SVM": svm_model
    }
    
    for name, model in models.items():
        model.fit(X, y)
    
    # AI Ensemble başlat
    ensemble = AIEnsemble(random_state=42)
    
    # Voting topluluk test
    print("\n🗳️ Voting Topluluk Test:")
    # Voting için ağırlıklı modeller
    voting_models = {
        "RandomForest": RandomForestClassifier(n_estimators=50, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=50, random_state=42),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000)
    }
    
    # Modelleri eğit
    for name, model in voting_models.items():
        model.fit(X, y)
    
    # Ağırlıkları tanımla
    voting_weights = {
        "RandomForest": 0.4,
        "GradientBoosting": 0.4,
        "LogisticRegression": 0.2
    }
    
    voting_success = ensemble.create_voting_ensemble("voting_ensemble", voting_models, voting_weights)
    print(f"   Voting topluluk oluşturuldu: {voting_success}")
    
    if voting_success:
        # Voting topluluğunu eğit
        ensemble_info = ensemble.ensemble_models["voting_ensemble"]
        voting_ensemble = ensemble_info["ensemble"]
        voting_ensemble.fit(X, y)
        
        # Voting tahmin test
        voting_pred = ensemble.make_ensemble_prediction("voting_ensemble", X.iloc[:5])
        print(f"   Final tahmin: {voting_pred.final_prediction}")
        print(f"   Güvenilirlik: {voting_pred.confidence:.4f}")
        print(f"   Anlaşma skoru: {voting_pred.agreement_score:.4f}")
    
    # Stacking topluluk test
    print("\n🏗️ Stacking Topluluk Test:")
    # Stacking için modelleri yeniden oluştur (feature dimension uyumluluğu için)
    stacking_models = {
        "RandomForest": RandomForestClassifier(n_estimators=50, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=50, random_state=42),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000)
    }
    
    # Modelleri eğit
    for name, model in stacking_models.items():
        model.fit(X, y)
    
    stacking_success = ensemble.create_stacking_ensemble("stacking_ensemble", stacking_models)
    print(f"   Stacking topluluk oluşturuldu: {stacking_success}")
    
    if stacking_success:
        # Stacking topluluğunu eğit
        ensemble_info = ensemble.ensemble_models["stacking_ensemble"]
        stacking_ensemble = ensemble_info["ensemble"]
        stacking_ensemble.fit(X, y)
        
        # Stacking tahmin test
        stacking_pred = ensemble.make_ensemble_prediction("stacking_ensemble", X.iloc[:5])
        print(f"   Final tahmin: {stacking_pred.final_prediction}")
        print(f"   Güvenilirlik: {stacking_pred.confidence:.4f}")
    
    # Blending topluluk test
    print("\n🥤 Blending Topluluk Test:")
    blending_success = ensemble.create_blending_ensemble("blending_ensemble", models)
    print(f"   Blending topluluk oluşturuldu: {blending_success}")
    
    if blending_success:
        # Blending topluluğunu eğit
        ensemble_info = ensemble.ensemble_models["blending_ensemble"]
        blending_ensemble = ensemble_info["ensemble"]
        blending_ensemble.fit(X, y)
        
        # Blending tahmin test
        blending_pred = ensemble.make_ensemble_prediction("blending_ensemble", X.iloc[:5])
        print(f"   Final tahmin: {blending_pred.final_prediction}")
        print(f"   Güvenilirlik: {blending_pred.confidence:.4f}")
    
    # Topluluk performans değerlendirme test
    print("\n📊 Topluluk Performans Değerlendirme Test:")
    if voting_success:
        voting_performance = ensemble.evaluate_ensemble("voting_ensemble", X, y)
        print(f"   Voting performans: {voting_performance.ensemble_score:.4f}")
        print(f"   F1 skor: {voting_performance.f1_score:.4f}")
    
    if stacking_success:
        stacking_performance = ensemble.evaluate_ensemble("stacking_ensemble", X, y)
        print(f"   Stacking performans: {stacking_performance.ensemble_score:.4f}")
    
    # Ağırlık optimizasyonu test
    print("\n⚖️ Ağırlık Optimizasyonu Test:")
    if voting_success:
        optimized_weights = ensemble.optimize_weights("voting_ensemble", X, y)
        if optimized_weights:
            print(f"   Optimize edilmiş ağırlıklar: {optimized_weights}")
        else:
            print("   Ağırlık optimizasyonu başarısız")
    
    # Otomatik topluluk oluşturma test
    print("\n🤖 Otomatik Topluluk Oluşturma Test:")
    # Otomatik topluluk için basit modeller
    auto_models = {
        "RandomForest": RandomForestClassifier(n_estimators=30, random_state=42),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000)
    }
    
    # Modelleri eğit
    for name, model in auto_models.items():
        model.fit(X, y)
    
    auto_success = ensemble.auto_create_ensemble("auto_ensemble", auto_models, X, y)
    print(f"   Otomatik topluluk oluşturuldu: {auto_success}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Topluluk Raporu Test:")
    ensemble_report = ensemble.generate_ensemble_report()
    print(f"   Toplam topluluk: {ensemble_report['ensemble_summary']['total_ensembles']}")
    print(f"   Kullanılan yöntemler: {ensemble_report['ensemble_summary']['methods_used']}")
    if ensemble_report['recommendations']['best_ensemble']:
        print(f"   En iyi topluluk: {ensemble_report['recommendations']['best_ensemble']}")
    else:
        print("   En iyi topluluk: Henüz değerlendirilmemiş")
    
    print("\n✅ AI Ensemble Test Tamamlandı!")
    
    # Test sonrası temizlik
    print("\n🧹 Test Temizliği:")
    print(f"   Toplam topluluk oluşturuldu: {len(ensemble.ensemble_models)}")
    print(f"   Performans geçmişi kayıtları: {len(ensemble.performance_history)}")
    
    return ensemble

if __name__ == "__main__":
    test_ai_ensemble()
