"""
PRD v2.0 - BIST AI Smart Trader
Prediction Engine Module

Tahmin motoru modülü:
- Real-time predictions
- Batch predictions
- Prediction confidence
- Model ensembling
- Prediction pipeline
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import pickle
import json
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PredictionResult:
    """Tahmin sonucu"""
    prediction: Union[int, float]
    confidence: float
    model_name: str
    timestamp: datetime
    features_used: List[str]
    prediction_probability: Optional[float] = None

@dataclass
class BatchPredictionResult:
    """Toplu tahmin sonucu"""
    predictions: List[Union[int, float]]
    confidences: List[float]
    model_names: List[str]
    timestamps: List[datetime]
    success_count: int
    error_count: int
    processing_time: float

@dataclass
class EnsemblePrediction:
    """Topluluk tahmin sonucu"""
    final_prediction: Union[int, float]
    individual_predictions: Dict[str, Union[int, float]]
    ensemble_weights: Dict[str, float]
    confidence: float
    agreement_score: float

@dataclass
class PredictionPipeline:
    """Tahmin boru hattı"""
    name: str
    models: List[str]
    preprocessing_steps: List[str]
    postprocessing_steps: List[str]
    is_active: bool

class PredictionEngine:
    """
    Tahmin Motoru
    
    PRD v2.0 gereksinimleri:
    - Gerçek zamanlı tahminler
    - Toplu tahminler
    - Tahmin güvenilirliği
    - Model topluluk sistemi
    - Tahmin boru hattı
    """
    
    def __init__(self, models_directory: str = "models/"):
        """
        Prediction Engine başlatıcı
        
        Args:
            models_directory: Model dosyalarının bulunduğu dizin
        """
        self.models_directory = models_directory
        
        # Yüklenen modeller
        self.loaded_models = {}
        
        # Model performans geçmişi
        self.model_performance_history = {}
        
        # Tahmin boru hatları
        self.prediction_pipelines = {}
        
        # Varsayılan topluluk ağırlıkları
        self.default_ensemble_weights = {
            "RANDOM_FOREST": 0.3,
            "GRADIENT_BOOSTING": 0.3,
            "LOGISTIC_REGRESSION": 0.2,
            "SVM": 0.1,
            "NEURAL_NETWORK": 0.1
        }
        
        # Tahmin güvenilirlik eşikleri
        self.confidence_thresholds = {
            "HIGH": 0.8,
            "MEDIUM": 0.6,
            "LOW": 0.4
        }
    
    def load_model(self, model_name: str, model_path: str, format: str = "joblib") -> bool:
        """
        Model yükleme
        
        Args:
            model_name: Model adı
            model_path: Model dosya yolu
            format: Model formatı
            
        Returns:
            bool: Yükleme başarı durumu
        """
        try:
            if format == "joblib":
                model = joblib.load(model_path)
            elif format == "pickle":
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            else:
                raise ValueError(f"Desteklenmeyen format: {format}")
            
            # Konfigürasyon dosyasını da yükle
            config_path = model_path.replace(f".{format}", "_config.json")
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            self.loaded_models[model_name] = {
                "model": model,
                "config": config,
                "load_time": datetime.now(),
                "prediction_count": 0,
                "last_used": None
            }
            
            return True
            
        except Exception as e:
            print(f"Model yükleme hatası ({model_name}): {str(e)}")
            return False
    
    def preprocess_features(self, features: pd.DataFrame, model_name: str) -> pd.DataFrame:
        """
        Özellik ön işleme
        
        Args:
            features: Özellik matrisi
            model_name: Model adı
            
        Returns:
            pd.DataFrame: Ön işlenmiş özellikler
        """
        if model_name not in self.loaded_models:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        model_info = self.loaded_models[model_name]
        config = model_info["config"]
        
        features_processed = features.copy()
        
        # Eksik değerleri işle
        if config.get("preprocessing", {}).get("handle_missing") == "impute":
            features_processed = features_processed.fillna(features_processed.mean())
        elif config.get("preprocessing", {}).get("handle_missing") == "drop":
            features_processed = features_processed.dropna()
        
        # Ölçeklendirme
        if config.get("preprocessing", {}).get("scaler") == "standard":
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_processed)
            features_processed = pd.DataFrame(
                features_scaled,
                columns=features_processed.columns,
                index=features_processed.index
            )
        
        # Özellik seçimi
        if "feature_selection" in config.get("preprocessing", {}):
            selected_features = config["preprocessing"]["feature_selection"]
            if isinstance(selected_features, list):
                available_features = [f for f in selected_features if f in features_processed.columns]
                features_processed = features_processed[available_features]
        
        return features_processed
    
    def make_prediction(self, features: pd.DataFrame, model_name: str) -> PredictionResult:
        """
        Tek tahmin yapma
        
        Args:
            features: Özellik matrisi
            model_name: Model adı
            
        Returns:
            PredictionResult: Tahmin sonucu
        """
        if model_name not in self.loaded_models:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        model_info = self.loaded_models[model_name]
        model = model_info["model"]
        
        # Özellik ön işleme
        features_processed = self.preprocess_features(features, model_name)
        
        # Tahmin yap
        try:
            if hasattr(model, 'predict_proba'):
                prediction_proba = model.predict_proba(features_processed)
                prediction = model.predict(features_processed)[0]
                confidence = np.max(prediction_proba[0])
            else:
                prediction = model.predict(features_processed)[0]
                confidence = 1.0  # Varsayılan güvenilirlik
            
            # Model kullanım istatistiklerini güncelle
            model_info["prediction_count"] += 1
            model_info["last_used"] = datetime.now()
            
            return PredictionResult(
                prediction=prediction,
                confidence=confidence,
                model_name=model_name,
                timestamp=datetime.now(),
                features_used=list(features_processed.columns),
                prediction_probability=confidence if hasattr(model, 'predict_proba') else None
            )
            
        except Exception as e:
            print(f"Tahmin hatası ({model_name}): {str(e)}")
            return PredictionResult(
                prediction=0,
                confidence=0.0,
                model_name=model_name,
                timestamp=datetime.now(),
                features_used=[],
                prediction_probability=0.0
            )
    
    def make_batch_predictions(self, features_batch: pd.DataFrame, 
                              model_names: Optional[List[str]] = None) -> BatchPredictionResult:
        """
        Toplu tahmin yapma
        
        Args:
            features_batch: Toplu özellik matrisi
            model_names: Kullanılacak model adları
            
        Returns:
            BatchPredictionResult: Toplu tahmin sonucu
        """
        import time
        
        start_time = time.time()
        
        if model_names is None:
            model_names = list(self.loaded_models.keys())
        
        predictions = []
        confidences = []
        model_names_used = []
        timestamps = []
        success_count = 0
        error_count = 0
        
        for _, row in features_batch.iterrows():
            row_df = pd.DataFrame([row])
            
            for model_name in model_names:
                try:
                    result = self.make_prediction(row_df, model_name)
                    
                    if result.confidence > 0:
                        predictions.append(result.prediction)
                        confidences.append(result.confidence)
                        model_names_used.append(model_name)
                        timestamps.append(result.timestamp)
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"Toplu tahmin hatası ({model_name}): {str(e)}")
                    error_count += 1
        
        processing_time = time.time() - start_time
        
        return BatchPredictionResult(
            predictions=predictions,
            confidences=confidences,
            model_names=model_names_used,
            timestamps=timestamps,
            success_count=success_count,
            error_count=error_count,
            processing_time=processing_time
        )
    
    def make_ensemble_prediction(self, features: pd.DataFrame,
                                model_names: Optional[List[str]] = None,
                                weights: Optional[Dict[str, float]] = None) -> EnsemblePrediction:
        """
        Topluluk tahmin yapma
        
        Args:
            features: Özellik matrisi
            model_names: Kullanılacak model adları
            weights: Model ağırlıkları
            
        Returns:
            EnsemblePrediction: Topluluk tahmin sonucu
        """
        if model_names is None:
            model_names = list(self.loaded_models.keys())
        
        if weights is None:
            weights = self.default_ensemble_weights
        
        # Her modelden tahmin al
        individual_predictions = {}
        valid_models = []
        
        for model_name in model_names:
            if model_name in self.loaded_models:
                try:
                    result = self.make_prediction(features, model_name)
                    individual_predictions[model_name] = result.prediction
                    valid_models.append(model_name)
                except Exception as e:
                    print(f"Topluluk tahmin hatası ({model_name}): {str(e)}")
                    continue
        
        if not valid_models:
            raise ValueError("Hiçbir modelden tahmin alınamadı")
        
        # Ağırlıklı ortalama hesapla
        weighted_sum = 0
        total_weight = 0
        
        for model_name in valid_models:
            weight = weights.get(model_name, 1.0)
            weighted_sum += individual_predictions[model_name] * weight
            total_weight += weight
        
        final_prediction = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Güvenilirlik hesapla
        if len(valid_models) > 1:
            predictions_array = np.array(list(individual_predictions.values()))
            confidence = 1.0 - np.std(predictions_array) / (np.max(predictions_array) - np.min(predictions_array) + 1e-8)
            confidence = max(0.0, min(1.0, confidence))
        else:
            confidence = 1.0
        
        # Anlaşma skoru hesapla
        if len(valid_models) > 1:
            predictions_array = np.array(list(individual_predictions.values()))
            agreement_score = 1.0 - (np.std(predictions_array) / np.mean(np.abs(predictions_array) + 1e-8))
            agreement_score = max(0.0, min(1.0, agreement_score))
        else:
            agreement_score = 1.0
        
        return EnsemblePrediction(
            final_prediction=final_prediction,
            individual_predictions=individual_predictions,
            ensemble_weights={name: weights.get(name, 1.0) for name in valid_models},
            confidence=confidence,
            agreement_score=agreement_score
        )
    
    def create_prediction_pipeline(self, name: str, models: List[str],
                                  preprocessing_steps: Optional[List[str]] = None,
                                  postprocessing_steps: Optional[List[str]] = None) -> bool:
        """
        Tahmin boru hattı oluşturma
        
        Args:
            name: Boru hattı adı
            models: Kullanılacak modeller
            preprocessing_steps: Ön işleme adımları
            postprocessing_steps: Son işleme adımları
            
        Returns:
            bool: Oluşturma başarı durumu
        """
        if preprocessing_steps is None:
            preprocessing_steps = ["handle_missing", "scale_features"]
        
        if postprocessing_steps is None:
            postprocessing_steps = ["confidence_filter", "ensemble_aggregation"]
        
        # Model varlığını kontrol et
        for model_name in models:
            if model_name not in self.loaded_models:
                print(f"Uyarı: Model bulunamadı: {model_name}")
                return False
        
        pipeline = PredictionPipeline(
            name=name,
            models=models,
            preprocessing_steps=preprocessing_steps,
            postprocessing_steps=postprocessing_steps,
            is_active=True
        )
        
        self.prediction_pipelines[name] = pipeline
        return True
    
    def execute_pipeline(self, pipeline_name: str, features: pd.DataFrame) -> Dict:
        """
        Tahmin boru hattını çalıştırma
        
        Args:
            pipeline_name: Boru hattı adı
            features: Özellik matrisi
            
        Returns:
            Dict: Boru hattı sonucu
        """
        if pipeline_name not in self.prediction_pipelines:
            raise ValueError(f"Boru hattı bulunamadı: {pipeline_name}")
        
        pipeline = self.prediction_pipelines[pipeline_name]
        
        if not pipeline.is_active:
            raise ValueError(f"Boru hattı aktif değil: {pipeline_name}")
        
        # Ön işleme
        features_processed = features.copy()
        for step in pipeline.preprocessing_steps:
            if step == "handle_missing":
                features_processed = features_processed.fillna(features_processed.mean())
            elif step == "scale_features":
                scaler = StandardScaler()
                features_scaled = scaler.fit_transform(features_processed)
                features_processed = pd.DataFrame(
                    features_scaled,
                    columns=features_processed.columns,
                    index=features_processed.index
                )
        
        # Model tahminleri
        individual_results = {}
        for model_name in pipeline.models:
            try:
                result = self.make_prediction(features_processed, model_name)
                individual_results[model_name] = result
            except Exception as e:
                print(f"Boru hattı tahmin hatası ({model_name}): {str(e)}")
        
        # Son işleme
        final_results = {}
        for step in pipeline.postprocessing_steps:
            if step == "confidence_filter":
                # Düşük güvenilirlikli tahminleri filtrele
                filtered_results = {
                    name: result for name, result in individual_results.items()
                    if result.confidence > self.confidence_thresholds["MEDIUM"]
                }
                final_results = filtered_results
                
            elif step == "ensemble_aggregation":
                # Topluluk tahmin yap
                if len(individual_results) > 1:
                    ensemble_result = self.make_ensemble_prediction(
                        features_processed, list(individual_results.keys())
                    )
                    final_results["ensemble"] = ensemble_result
        
        return {
            "pipeline_name": pipeline_name,
            "individual_results": individual_results,
            "final_results": final_results,
            "execution_time": datetime.now().isoformat(),
            "success": len(final_results) > 0
        }
    
    def update_model_performance(self, model_name: str, actual_value: Union[int, float],
                                predicted_value: Union[int, float], confidence: float):
        """
        Model performansını güncelleme
        
        Args:
            model_name: Model adı
            actual_value: Gerçek değer
            predicted_value: Tahmin edilen değer
            confidence: Tahmin güvenilirliği
        """
        if model_name not in self.model_performance_history:
            self.model_performance_history[model_name] = {
                "predictions": [],
                "actuals": [],
                "confidences": [],
                "errors": [],
                "accuracy": 0.0,
                "last_updated": datetime.now()
            }
        
        performance = self.model_performance_history[model_name]
        
        # Performans verilerini ekle
        performance["predictions"].append(predicted_value)
        performance["actuals"].append(actual_value)
        performance["confidences"].append(confidence)
        performance["errors"].append(abs(actual_value - predicted_value))
        
        # Performans metriklerini güncelle
        if len(performance["predictions"]) > 0:
            # Basit accuracy (sınıflandırma için)
            if isinstance(actual_value, (int, bool)) and isinstance(predicted_value, (int, bool)):
                accuracy = sum(1 for a, p in zip(performance["actuals"], performance["predictions"]) if a == p)
                performance["accuracy"] = accuracy / len(performance["predictions"])
            
            # Son güncelleme zamanını güncelle
            performance["last_updated"] = datetime.now()
    
    def get_model_performance_summary(self) -> Dict:
        """
        Model performans özeti alma
        
        Returns:
            Dict: Model performans özeti
        """
        summary = {}
        
        for model_name, performance in self.model_performance_history.items():
            if len(performance["predictions"]) > 0:
                summary[model_name] = {
                    "total_predictions": len(performance["predictions"]),
                    "accuracy": performance["accuracy"],
                    "avg_confidence": np.mean(performance["confidences"]),
                    "avg_error": np.mean(performance["errors"]),
                    "last_updated": performance["last_updated"].isoformat()
                }
        
        return summary
    
    def generate_prediction_report(self, features: pd.DataFrame,
                                 model_names: Optional[List[str]] = None) -> Dict:
        """
        Tahmin raporu oluşturma
        
        Args:
            features: Özellik matrisi
            model_names: Kullanılacak model adları
            
        Returns:
            Dict: Tahmin raporu
        """
        print("🔮 Tahmin Raporu Oluşturuluyor...")
        
        if model_names is None:
            model_names = list(self.loaded_models.keys())
        
        # Her modelden tahmin al
        individual_predictions = {}
        ensemble_prediction = None
        
        for model_name in model_names:
            if model_name in self.loaded_models:
                try:
                    result = self.make_prediction(features, model_name)
                    individual_predictions[model_name] = {
                        "prediction": result.prediction,
                        "confidence": result.confidence,
                        "features_used": result.features_used
                    }
                except Exception as e:
                    print(f"Tahmin hatası ({model_name}): {str(e)}")
        
        # Topluluk tahmin yap
        if len(individual_predictions) > 1:
            try:
                ensemble_result = self.make_ensemble_prediction(features, model_names)
                ensemble_prediction = {
                    "final_prediction": ensemble_result.final_prediction,
                    "confidence": ensemble_result.confidence,
                    "agreement_score": ensemble_result.agreement_score,
                    "individual_predictions": ensemble_result.individual_predictions
                }
            except Exception as e:
                print(f"Topluluk tahmin hatası: {str(e)}")
        
        # Model performans özeti
        performance_summary = self.get_model_performance_summary()
        
        # Rapor oluştur
        report = {
            "prediction_summary": {
                "total_models": len(self.loaded_models),
                "active_models": len(individual_predictions),
                "ensemble_available": ensemble_prediction is not None
            },
            "individual_predictions": individual_predictions,
            "ensemble_prediction": ensemble_prediction,
            "model_performance": performance_summary,
            "pipeline_status": {
                name: pipeline.is_active
                for name, pipeline in self.prediction_pipelines.items()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print("✅ Tahmin Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_prediction_engine():
    """Prediction Engine test fonksiyonu"""
    print("🧪 Prediction Engine Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_samples = 100
    n_features = 10
    
    # Özellik matrisi
    features = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    
    # Basit model oluştur (test amaçlı)
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    
    # Test modelleri
    rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    
    # Basit hedef değişken
    target = (features.iloc[:, 0] + features.iloc[:, 1] > 0).astype(int)
    
    # Modelleri eğit
    rf_model.fit(features, target)
    lr_model.fit(features, target)
    
    # Prediction Engine başlat
    engine = PredictionEngine()
    
    # Modelleri kaydet (geçici)
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp:
        joblib.dump(rf_model, tmp.name)
        rf_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp:
        joblib.dump(lr_model, tmp.name)
        lr_path = tmp.name
    
    # Modelleri yükle
    print("\n📥 Model Yükleme Test:")
    rf_loaded = engine.load_model("RandomForest", rf_path)
    lr_loaded = engine.load_model("LogisticRegression", lr_path)
    print(f"   RandomForest yüklendi: {rf_loaded}")
    print(f"   LogisticRegression yüklendi: {lr_loaded}")
    
    # Tek tahmin test
    print("\n🔮 Tek Tahmin Test:")
    test_features = features.iloc[:1]
    rf_prediction = engine.make_prediction(test_features, "RandomForest")
    print(f"   RandomForest tahmin: {rf_prediction.prediction}, güven: {rf_prediction.confidence:.4f}")
    
    lr_prediction = engine.make_prediction(test_features, "LogisticRegression")
    print(f"   LogisticRegression tahmin: {lr_prediction.prediction}, güven: {lr_prediction.confidence:.4f}")
    
    # Topluluk tahmin test
    print("\n🤖 Topluluk Tahmin Test:")
    ensemble_result = engine.make_ensemble_prediction(test_features)
    print(f"   Topluluk tahmin: {ensemble_result.final_prediction:.4f}")
    print(f"   Güvenilirlik: {ensemble_result.confidence:.4f}")
    print(f"   Anlaşma skoru: {ensemble_result.agreement_score:.4f}")
    
    # Toplu tahmin test
    print("\n📊 Toplu Tahmin Test:")
    batch_features = features.iloc[:5]
    batch_result = engine.make_batch_predictions(batch_features, ["RandomForest"])
    print(f"   Başarılı tahmin: {batch_result.success_count}")
    print(f"   Hatalı tahmin: {batch_result.error_count}")
    print(f"   İşlem süresi: {batch_result.processing_time:.4f} saniye")
    
    # Tahmin boru hattı test
    print("\n🔧 Tahmin Boru Hattı Test:")
    pipeline_created = engine.create_prediction_pipeline(
        "test_pipeline", ["RandomForest", "LogisticRegression"]
    )
    print(f"   Boru hattı oluşturuldu: {pipeline_created}")
    
    if pipeline_created:
        pipeline_result = engine.execute_pipeline("test_pipeline", test_features)
        print(f"   Boru hattı çalıştırıldı: {pipeline_result['success']}")
    
    # Model performans güncelleme test
    print("\n📈 Model Performans Güncelleme Test:")
    engine.update_model_performance("RandomForest", 1, rf_prediction.prediction, rf_prediction.confidence)
    engine.update_model_performance("LogisticRegression", 1, lr_prediction.prediction, lr_prediction.confidence)
    
    performance_summary = engine.get_model_performance_summary()
    print(f"   Güncellenen model sayısı: {len(performance_summary)}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Tahmin Raporu Test:")
    prediction_report = engine.generate_prediction_report(test_features)
    print(f"   Toplam model: {prediction_report['prediction_summary']['total_models']}")
    print(f"   Aktif model: {prediction_report['prediction_summary']['active_models']}")
    print(f"   Topluluk mevcut: {prediction_report['prediction_summary']['ensemble_available']}")
    
    # Test dosyalarını temizle
    os.unlink(rf_path)
    os.unlink(lr_path)
    
    print("\n✅ Prediction Engine Test Tamamlandı!")
    return engine

if __name__ == "__main__":
    test_prediction_engine()
