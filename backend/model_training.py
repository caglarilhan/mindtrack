"""
PRD v2.0 - BIST AI Smart Trader
Model Training Module

Model eğitimi modülü:
- Multiple algorithms
- Hyperparameter tuning
- Cross validation
- Model persistence
- Training monitoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ModelConfig:
    """Model konfigürasyonu"""
    algorithm: str
    hyperparameters: Dict[str, Any]
    preprocessing: Dict[str, Any]
    validation: Dict[str, Any]

@dataclass
class TrainingResult:
    """Eğitim sonucu"""
    model: Any
    config: ModelConfig
    metrics: Dict[str, float]
    training_time: float
    validation_scores: List[float]
    feature_importance: Optional[Dict[str, float]] = None

@dataclass
class ModelComparison:
    """Model karşılaştırması"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    training_time: float

class ModelTraining:
    """
    Model Eğitim Motoru
    
    PRD v2.0 gereksinimleri:
    - Çoklu algoritma desteği
    - Hiperparametre optimizasyonu
    - Çapraz doğrulama
    - Model kalıcılığı
    - Eğitim izleme
    """
    
    def __init__(self, random_state: int = 42):
        """
        Model Training başlatıcı
        
        Args:
            random_state: Rastgele sayı üreteci
        """
        self.random_state = random_state
        
        # Desteklenen algoritmalar
        self.SUPPORTED_ALGORITHMS = {
            "RANDOM_FOREST": "Random Forest",
            "GRADIENT_BOOSTING": "Gradient Boosting",
            "LOGISTIC_REGRESSION": "Logistic Regression",
            "SVM": "Support Vector Machine",
            "NEURAL_NETWORK": "Neural Network",
            "RIDGE_CLASSIFIER": "Ridge Classifier",
            "VOTING_ENSEMBLE": "Voting Ensemble"
        }
        
        # Varsayılan hiperparametreler
        self.DEFAULT_HYPERPARAMETERS = {
            "RANDOM_FOREST": {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4]
            },
            "GRADIENT_BOOSTING": {
                "n_estimators": [100, 200, 300],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "subsample": [0.8, 0.9, 1.0]
            },
            "LOGISTIC_REGRESSION": {
                "C": [0.1, 1.0, 10.0],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"]
            },
            "SVM": {
                "C": [0.1, 1.0, 10.0],
                "kernel": ["rbf", "linear"],
                "gamma": ["scale", "auto"]
            },
            "NEURAL_NETWORK": {
                "hidden_layer_sizes": [(50,), (100,), (50, 25)],
                "activation": ["relu", "tanh"],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate": ["constant", "adaptive"]
            },
            "RIDGE_CLASSIFIER": {
                "alpha": [0.1, 1.0, 10.0],
                "solver": ["auto", "svd", "cholesky"]
            }
        }
        
        # Varsayılan ön işleme
        self.DEFAULT_PREPROCESSING = {
            "scaler": "standard",  # "standard", "minmax", "robust"
            "handle_missing": "drop",  # "drop", "impute", "forward_fill"
            "feature_selection": "correlation",  # "correlation", "variance", "mutual_info"
            "feature_selection_threshold": 0.1
        }
        
        # Varsayılan doğrulama
        self.DEFAULT_VALIDATION = {
            "test_size": 0.2,
            "cv_folds": 5,
            "stratify": True,
            "random_state": random_state
        }
        
        # Eğitilen modeller
        self.trained_models = {}
        self.training_history = []
    
    def create_model(self, algorithm: str, hyperparameters: Optional[Dict] = None) -> Any:
        """
        Model oluşturma
        
        Args:
            algorithm: Algoritma adı
            hyperparameters: Hiperparametreler
            
        Returns:
            Any: Model nesnesi
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Desteklenmeyen algoritma: {algorithm}")
        
        if hyperparameters is None:
            hyperparameters = {}
        
        if algorithm == "RANDOM_FOREST":
            model = RandomForestClassifier(
                random_state=self.random_state,
                **hyperparameters
            )
        elif algorithm == "GRADIENT_BOOSTING":
            model = GradientBoostingClassifier(
                random_state=self.random_state,
                **hyperparameters
            )
        elif algorithm == "LOGISTIC_REGRESSION":
            model = LogisticRegression(
                random_state=self.random_state,
                max_iter=1000,
                **hyperparameters
            )
        elif algorithm == "SVM":
            model = SVC(
                random_state=self.random_state,
                probability=True,
                **hyperparameters
            )
        elif algorithm == "NEURAL_NETWORK":
            model = MLPClassifier(
                random_state=self.random_state,
                max_iter=1000,
                **hyperparameters
            )
        elif algorithm == "RIDGE_CLASSIFIER":
            model = RidgeClassifier(
                random_state=self.random_state,
                **hyperparameters
            )
        elif algorithm == "VOTING_ENSEMBLE":
            # Voting ensemble oluştur
            estimators = []
            for i, (name, model_obj) in enumerate([
                ("rf", RandomForestClassifier(random_state=self.random_state)),
                ("gb", GradientBoostingClassifier(random_state=self.random_state)),
                ("lr", LogisticRegression(random_state=self.random_state, max_iter=1000))
            ]):
                estimators.append((name, model_obj))
            
            model = VotingClassifier(
                estimators=estimators,
                voting="soft"
            )
        else:
            raise ValueError(f"Bilinmeyen algoritma: {algorithm}")
        
        return model
    
    def preprocess_data(self, features: pd.DataFrame, target: pd.Series,
                       preprocessing_config: Optional[Dict] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Veri ön işleme
        
        Args:
            features: Özellik matrisi
            target: Hedef değişken
            preprocessing_config: Ön işleme konfigürasyonu
            
        Returns:
            Tuple: Ön işlenmiş özellikler ve hedef
        """
        if preprocessing_config is None:
            preprocessing_config = self.DEFAULT_PREPROCESSING
        
        features_processed = features.copy()
        target_processed = target.copy()
        
        # Eksik değerleri işle
        if preprocessing_config["handle_missing"] == "drop":
            # NaN değerleri olan satırları kaldır
            mask = ~(features_processed.isnull().any(axis=1) | target_processed.isnull())
            features_processed = features_processed[mask]
            target_processed = target_processed[mask]
        elif preprocessing_config["handle_missing"] == "impute":
            # Eksik değerleri ortalama ile doldur
            features_processed = features_processed.fillna(features_processed.mean())
            target_processed = target_processed.fillna(target_processed.mean())
        elif preprocessing_config["handle_missing"] == "forward_fill":
            # Eksik değerleri önceki değer ile doldur
            features_processed = features_processed.fillna(method='ffill')
            target_processed = target_processed.fillna(method='ffill')
        
        # Özellik seçimi
        if preprocessing_config["feature_selection"] == "correlation":
            # Korelasyon bazlı özellik seçimi
            correlations = features_processed.corrwith(target_processed).abs()
            selected_features = correlations[correlations > preprocessing_config["feature_selection_threshold"]].index
            features_processed = features_processed[selected_features]
        
        elif preprocessing_config["feature_selection"] == "variance":
            # Varyans bazlı özellik seçimi
            variances = features_processed.var()
            selected_features = variances[variances > preprocessing_config["feature_selection_threshold"]].index
            features_processed = features_processed[selected_features]
        
        # Ölçeklendirme
        if preprocessing_config["scaler"] == "standard":
            scaler = StandardScaler()
        elif preprocessing_config["scaler"] == "minmax":
            scaler = MinMaxScaler()
        else:
            scaler = None
        
        if scaler is not None:
            features_scaled = scaler.fit_transform(features_processed)
            features_processed = pd.DataFrame(
                features_scaled,
                columns=features_processed.columns,
                index=features_processed.index
            )
        
        return features_processed, target_processed
    
    def train_model(self, features: pd.DataFrame, target: pd.Series,
                   algorithm: str, hyperparameters: Optional[Dict] = None,
                   preprocessing_config: Optional[Dict] = None,
                   validation_config: Optional[Dict] = None) -> TrainingResult:
        """
        Model eğitimi
        
        Args:
            features: Özellik matrisi
            target: Hedef değişken
            algorithm: Algoritma adı
            hyperparameters: Hiperparametreler
            preprocessing_config: Ön işleme konfigürasyonu
            validation_config: Doğrulama konfigürasyonu
            
        Returns:
            TrainingResult: Eğitim sonucu
        """
        import time
        
        start_time = time.time()
        
        # Konfigürasyonları ayarla
        if preprocessing_config is None:
            preprocessing_config = self.DEFAULT_PREPROCESSING
        if validation_config is None:
            validation_config = self.DEFAULT_VALIDATION
        if hyperparameters is None:
            hyperparameters = {}
        
        # Veri ön işleme
        features_processed, target_processed = self.preprocess_data(
            features, target, preprocessing_config
        )
        
        # Veri bölme
        if validation_config["stratify"] and len(target_processed.unique()) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                features_processed, target_processed,
                test_size=validation_config["test_size"],
                stratify=target_processed,
                random_state=validation_config["random_state"]
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                features_processed, target_processed,
                test_size=validation_config["test_size"],
                random_state=validation_config["random_state"]
            )
        
        # Model oluştur
        model = self.create_model(algorithm, hyperparameters)
        
        # Model eğitimi
        model.fit(X_train, y_train)
        
        # Tahminler
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Metrikler hesapla
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
            "f1_score": f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        
        if y_pred_proba is not None:
            try:
                metrics["roc_auc"] = roc_auc_score(y_test, y_pred_proba)
            except:
                metrics["roc_auc"] = 0.0
        
        # Çapraz doğrulama
        cv_scores = cross_val_score(
            model, features_processed, target_processed,
            cv=validation_config["cv_folds"],
            scoring='accuracy'
        )
        
        # Özellik önem sırası
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(features_processed.columns, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            feature_importance = dict(zip(features_processed.columns, np.abs(model.coef_[0])))
        
        # Eğitim süresi
        training_time = time.time() - start_time
        
        # Sonuç oluştur
        result = TrainingResult(
            model=model,
            config=ModelConfig(
                algorithm=algorithm,
                hyperparameters=hyperparameters,
                preprocessing=preprocessing_config,
                validation=validation_config
            ),
            metrics=metrics,
            training_time=training_time,
            validation_scores=cv_scores.tolist(),
            feature_importance=feature_importance
        )
        
        # Modeli kaydet
        model_name = f"{algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.trained_models[model_name] = result
        self.training_history.append({
            "model_name": model_name,
            "algorithm": algorithm,
            "metrics": metrics,
            "training_time": training_time,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def hyperparameter_tuning(self, features: pd.DataFrame, target: pd.Series,
                             algorithm: str, param_grid: Optional[Dict] = None,
                             method: str = "grid", n_iter: int = 100,
                             cv_folds: int = 5) -> Dict:
        """
        Hiperparametre optimizasyonu
        
        Args:
            features: Özellik matrisi
            target: Hedef değişken
            algorithm: Algoritma adı
            param_grid: Parametre ızgarası
            method: Optimizasyon metodu
            n_iter: Random search iterasyon sayısı
            cv_folds: Çapraz doğrulama katları
            
        Returns:
            Dict: Optimizasyon sonucu
        """
        if param_grid is None:
            param_grid = self.DEFAULT_HYPERPARAMETERS.get(algorithm, {})
        
        # Veri ön işleme
        features_processed, target_processed = self.preprocess_data(features, target)
        
        # Model oluştur
        model = self.create_model(algorithm)
        
        # Hiperparametre optimizasyonu
        if method == "grid":
            search = GridSearchCV(
                model, param_grid,
                cv=cv_folds,
                scoring='accuracy',
                n_jobs=-1,
                verbose=0
            )
        elif method == "random":
            search = RandomizedSearchCV(
                model, param_grid,
                n_iter=n_iter,
                cv=cv_folds,
                scoring='accuracy',
                n_jobs=-1,
                verbose=0,
                random_state=self.random_state
            )
        else:
            raise ValueError(f"Desteklenmeyen metod: {method}")
        
        # Optimizasyon çalıştır
        search.fit(features_processed, target_processed)
        
        return {
            "best_params": search.best_params_,
            "best_score": search.best_score_,
            "best_estimator": search.best_estimator_,
            "cv_results": search.cv_results_,
            "method": method
        }
    
    def compare_models(self, features: pd.DataFrame, target: pd.Series,
                      algorithms: Optional[List[str]] = None) -> List[ModelComparison]:
        """
        Modelleri karşılaştırma
        
        Args:
            features: Özellik matrisi
            target: Hedef değişken
            algorithms: Karşılaştırılacak algoritmalar
            
        Returns:
            List: Model karşılaştırma sonuçları
        """
        if algorithms is None:
            algorithms = list(self.SUPPORTED_ALGORITHMS.keys())[:5]  # İlk 5 algoritma
        
        comparisons = []
        
        for algorithm in algorithms:
            try:
                # Model eğitimi
                result = self.train_model(features, target, algorithm)
                
                # Karşılaştırma sonucu
                comparison = ModelComparison(
                    model_name=algorithm,
                    accuracy=result.metrics["accuracy"],
                    precision=result.metrics["precision"],
                    recall=result.metrics["recall"],
                    f1_score=result.metrics["f1_score"],
                    roc_auc=result.metrics.get("roc_auc", 0.0),
                    training_time=result.training_time
                )
                
                comparisons.append(comparison)
                
            except Exception as e:
                print(f"Hata: {algorithm} eğitimi başarısız - {str(e)}")
                continue
        
        # Sonuçları performansa göre sırala
        comparisons.sort(key=lambda x: x.f1_score, reverse=True)
        
        return comparisons
    
    def save_model(self, model_name: str, filepath: str, format: str = "joblib") -> bool:
        """
        Model kaydetme
        
        Args:
            model_name: Model adı
            filepath: Dosya yolu
            format: Kaydetme formatı
            
        Returns:
            bool: Başarı durumu
        """
        if model_name not in self.trained_models:
            return False
        
        try:
            model_result = self.trained_models[model_name]
            
            if format == "joblib":
                joblib.dump(model_result.model, filepath)
            elif format == "pickle":
                with open(filepath, 'wb') as f:
                    pickle.dump(model_result.model, f)
            else:
                raise ValueError(f"Desteklenmeyen format: {format}")
            
            # Konfigürasyonu da kaydet
            config_filepath = filepath.replace(f".{format}", "_config.json")
            with open(config_filepath, 'w') as f:
                json.dump({
                    "algorithm": model_result.config.algorithm,
                    "hyperparameters": model_result.config.hyperparameters,
                    "preprocessing": model_result.config.preprocessing,
                    "validation": model_result.config.validation,
                    "metrics": model_result.metrics,
                    "training_time": model_result.training_time,
                    "validation_scores": model_result.validation_scores,
                    "feature_importance": model_result.feature_importance
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Model kaydetme hatası: {str(e)}")
            return False
    
    def load_model(self, filepath: str, config_filepath: Optional[str] = None, format: str = "joblib") -> Optional[TrainingResult]:
        """
        Model yükleme
        
        Args:
            filepath: Model dosya yolu
            config_filepath: Konfigürasyon dosya yolu
            format: Yükleme formatı
            
        Returns:
            Optional[TrainingResult]: Yüklenen model sonucu
        """
        try:
            # Model yükle
            if format == "joblib":
                model = joblib.load(filepath)
            elif format == "pickle":
                with open(filepath, 'rb') as f:
                    model = pickle.load(f)
            else:
                raise ValueError(f"Desteklenmeyen format: {format}")
            
            # Konfigürasyon yükle
            if config_filepath is None:
                config_filepath = filepath.replace(f".{format}", "_config.json")
            
            with open(config_filepath, 'r') as f:
                config_data = json.load(f)
            
            # TrainingResult oluştur
            result = TrainingResult(
                model=model,
                config=ModelConfig(
                    algorithm=config_data["algorithm"],
                    hyperparameters=config_data["hyperparameters"],
                    preprocessing=config_data["preprocessing"],
                    validation=config_data["validation"]
                ),
                metrics=config_data["metrics"],
                training_time=config_data["training_time"],
                validation_scores=config_data["validation_scores"],
                feature_importance=config_data.get("feature_importance")
            )
            
            return result
            
        except Exception as e:
            print(f"Model yükleme hatası: {str(e)}")
            return None
    
    def generate_training_report(self) -> Dict:
        """
        Eğitim raporu oluşturma
        
        Returns:
            Dict: Eğitim raporu
        """
        print("📊 Eğitim Raporu Oluşturuluyor...")
        
        if not self.training_history:
            return {"error": "Henüz eğitim yapılmamış"}
        
        # En iyi model
        best_model = max(self.training_history, key=lambda x: x["metrics"]["f1_score"])
        
        # Algoritma performansları
        algorithm_performance = {}
        for record in self.training_history:
            algo = record["algorithm"]
            if algo not in algorithm_performance:
                algorithm_performance[algo] = []
            algorithm_performance[algo].append(record["metrics"]["f1_score"])
        
        # Ortalama performanslar
        avg_performance = {}
        for algo, scores in algorithm_performance.items():
            avg_performance[algo] = {
                "mean_f1": np.mean(scores),
                "std_f1": np.std(scores),
                "count": len(scores)
            }
        
        # Rapor oluştur
        report = {
            "training_summary": {
                "total_models_trained": len(self.training_history),
                "unique_algorithms": len(set(record["algorithm"] for record in self.training_history)),
                "best_model": best_model["model_name"],
                "best_algorithm": best_model["algorithm"],
                "best_f1_score": best_model["metrics"]["f1_score"]
            },
            "algorithm_performance": avg_performance,
            "training_history": self.training_history,
            "model_inventory": {
                name: {
                    "algorithm": result.config.algorithm,
                    "metrics": result.metrics,
                    "training_time": result.training_time
                }
                for name, result in self.trained_models.items()
            }
        }
        
        print("✅ Eğitim Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_model_training():
    """Model Training test fonksiyonu"""
    print("🧪 Model Training Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    # Özellik matrisi
    features = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    
    # Hedef değişken (basit kural)
    target = ((features.iloc[:, 0] + features.iloc[:, 1] + features.iloc[:, 2]) > 0).astype(int)
    
    # Model Training başlat
    trainer = ModelTraining(random_state=42)
    
    # Tek model eğitimi test
    print("\n🤖 Tek Model Eğitimi Test:")
    result = trainer.train_model(features, target, "RANDOM_FOREST")
    print(f"   Model: {result.config.algorithm}")
    print(f"   Accuracy: {result.metrics['accuracy']:.4f}")
    print(f"   F1 Score: {result.metrics['f1_score']:.4f}")
    print(f"   Eğitim süresi: {result.training_time:.2f} saniye")
    
    # Hiperparametre optimizasyonu test
    print("\n🔧 Hiperparametre Optimizasyonu Test:")
    tuning_result = trainer.hyperparameter_tuning(
        features, target, "RANDOM_FOREST", method="random", n_iter=10
    )
    print(f"   En iyi skor: {tuning_result['best_score']:.4f}")
    print(f"   En iyi parametreler: {tuning_result['best_params']}")
    
    # Model karşılaştırması test
    print("\n📊 Model Karşılaştırması Test:")
    algorithms = ["RANDOM_FOREST", "GRADIENT_BOOSTING", "LOGISTIC_REGRESSION"]
    comparisons = trainer.compare_models(features, target, algorithms)
    
    for comp in comparisons:
        print(f"   {comp.model_name}: F1={comp.f1_score:.4f}, Time={comp.training_time:.2f}s")
    
    # Model kaydetme test
    print("\n💾 Model Kaydetme Test:")
    save_success = trainer.save_model(
        list(trainer.trained_models.keys())[0],
        "test_model.joblib"
    )
    print(f"   Kaydetme başarılı: {save_success}")
    
    # Model yükleme test
    print("\n📥 Model Yükleme Test:")
    loaded_model = trainer.load_model("test_model.joblib")
    if loaded_model:
        print(f"   Yüklenen model: {loaded_model.config.algorithm}")
        print(f"   Model metrikleri: {loaded_model.metrics}")
    
    # Eğitim raporu test
    print("\n📋 Eğitim Raporu Test:")
    training_report = trainer.generate_training_report()
    print(f"   Toplam eğitilen model: {training_report['training_summary']['total_models_trained']}")
    print(f"   En iyi F1 skoru: {training_report['training_summary']['best_f1_score']:.4f}")
    
    # Test dosyasını temizle
    import os
    if os.path.exists("test_model.joblib"):
        os.remove("test_model.joblib")
    if os.path.exists("test_model_config.json"):
        os.remove("test_model_config.json")
    
    print("\n✅ Model Training Test Tamamlandı!")
    return trainer

if __name__ == "__main__":
    test_model_training()
