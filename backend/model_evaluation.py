"""
PRD v2.0 - BIST AI Smart Trader
Model Evaluation Module

Model değerlendirme modülü:
- Performance metrics
- Cross validation
- Model comparison
- Bias analysis
- Feature importance
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                            roc_auc_score, confusion_matrix, classification_report,
                            mean_squared_error, mean_absolute_error, r2_score)
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

@dataclass
class EvaluationMetrics:
    """Değerlendirme metrikleri"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: np.ndarray
    classification_report: str

@dataclass
class CrossValidationResult:
    """Çapraz doğrulama sonucu"""
    mean_score: float
    std_score: float
    scores: List[float]
    cv_folds: int
    scoring_method: str

@dataclass
class ModelComparisonResult:
    """Model karşılaştırma sonucu"""
    model_name: str
    metrics: EvaluationMetrics
    cv_result: CrossValidationResult
    training_time: float
    prediction_time: float
    model_size: float

@dataclass
class BiasAnalysisResult:
    """Yanlılık analizi sonucu"""
    demographic_parity: float
    equalized_odds: float
    calibration: float
    bias_score: float
    fairness_metrics: Dict[str, float]

@dataclass
class FeatureImportanceResult:
    """Özellik önem sırası sonucu"""
    feature_names: List[str]
    importance_scores: List[float]
    importance_ranks: List[int]
    cumulative_importance: List[float]
    top_features: List[str]

class ModelEvaluation:
    """
    Model Değerlendirme Motoru
    
    PRD v2.0 gereksinimleri:
    - Performans metrikleri hesaplama
    - Çapraz doğrulama
    - Model karşılaştırması
    - Yanlılık analizi
    - Özellik önem sırası analizi
    """
    
    def __init__(self, random_state: int = 42):
        """
        Model Evaluation başlatıcı
        
        Args:
            random_state: Rastgele sayı üreteci
        """
        self.random_state = random_state
        
        # Değerlendirme metrikleri
        self.CLASSIFICATION_METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        self.REGRESSION_METRICS = ["mse", "mae", "r2", "rmse"]
        
        # Çapraz doğrulama parametreleri
        self.DEFAULT_CV_FOLDS = 5
        self.DEFAULT_CV_STRATEGY = "stratified"  # "stratified", "kfold"
        
        # Yanlılık analizi parametreleri
        self.BIAS_THRESHOLD = 0.1
        self.FAIRNESS_METRICS = ["demographic_parity", "equalized_odds", "calibration"]
        
        # Özellik önem analizi parametreleri
        self.FEATURE_IMPORTANCE_METHODS = ["permutation", "tree_based", "correlation"]
        self.TOP_FEATURES_COUNT = 10
    
    def calculate_classification_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                                      y_pred_proba: Optional[np.ndarray] = None) -> EvaluationMetrics:
        """
        Sınıflandırma metrikleri hesaplama
        
        Args:
            y_true: Gerçek değerler
            y_pred: Tahmin edilen değerler
            y_pred_proba: Tahmin olasılıkları
            
        Returns:
            EvaluationMetrics: Sınıflandırma metrikleri
        """
        # Temel metrikler
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # ROC AUC (olasılık varsa)
        roc_auc = 0.0
        if y_pred_proba is not None and len(np.unique(y_true)) == 2:
            try:
                roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1])
            except:
                roc_auc = 0.0
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Classification report
        report = classification_report(y_true, y_pred, output_dict=False)
        
        return EvaluationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            roc_auc=roc_auc,
            confusion_matrix=cm,
            classification_report=report
        )
    
    def calculate_regression_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Regresyon metrikleri hesaplama
        
        Args:
            y_true: Gerçek değerler
            y_pred: Tahmin edilen değerler
            
        Returns:
            Dict: Regresyon metrikleri
        """
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        rmse = np.sqrt(mse)
        
        return {
            "mse": mse,
            "mae": mae,
            "r2": r2,
            "rmse": rmse
        }
    
    def perform_cross_validation(self, model: Any, X: np.ndarray, y: np.ndarray,
                                cv_folds: int = None, cv_strategy: str = None,
                                scoring: str = "accuracy") -> CrossValidationResult:
        """
        Çapraz doğrulama yapma
        
        Args:
            model: Model nesnesi
            X: Özellik matrisi
            y: Hedef değişken
            cv_folds: CV kat sayısı
            cv_strategy: CV stratejisi
            scoring: Skorlama metodu
            
        Returns:
            CrossValidationResult: CV sonucu
        """
        if cv_folds is None:
            cv_folds = self.DEFAULT_CV_FOLDS
        
        if cv_strategy is None:
            cv_strategy = self.DEFAULT_CV_STRATEGY
        
        # CV stratejisi seç
        if cv_strategy == "stratified" and len(np.unique(y)) > 1:
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        else:
            cv = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        # CV skorları
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        
        return CrossValidationResult(
            mean_score=cv_scores.mean(),
            std_score=cv_scores.std(),
            scores=cv_scores.tolist(),
            cv_folds=cv_folds,
            scoring_method=scoring
        )
    
    def compare_models(self, models: Dict[str, Any], X: np.ndarray, y: np.ndarray,
                      cv_folds: int = 5) -> List[ModelComparisonResult]:
        """
        Modelleri karşılaştırma
        
        Args:
            models: Model sözlüğü
            X: Özellik matrisi
            y: Hedef değişken
            cv_folds: CV kat sayısı
            
        Returns:
            List: Model karşılaştırma sonuçları
        """
        import time
        
        comparison_results = []
        
        for model_name, model in models.items():
            try:
                # Model eğitimi
                start_time = time.time()
                model.fit(X, y)
                training_time = time.time() - start_time
                
                # Tahmin
                start_time = time.time()
                y_pred = model.predict(X)
                prediction_time = time.time() - start_time
                
                # Tahmin olasılıkları
                y_pred_proba = None
                if hasattr(model, 'predict_proba'):
                    y_pred_proba = model.predict_proba(X)
                
                # Metrikler
                metrics = self.calculate_classification_metrics(y, y_pred, y_pred_proba)
                
                # CV
                cv_result = self.perform_cross_validation(model, X, y, cv_folds)
                
                # Model boyutu (basit yaklaşım)
                model_size = 0.0
                if hasattr(model, 'n_estimators'):
                    model_size = model.n_estimators * 0.001  # MB cinsinden
                elif hasattr(model, 'coef_'):
                    model_size = len(model.coef_[0]) * 0.0001
                else:
                    model_size = 0.1
                
                # Sonuç oluştur
                result = ModelComparisonResult(
                    model_name=model_name,
                    metrics=metrics,
                    cv_result=cv_result,
                    training_time=training_time,
                    prediction_time=prediction_time,
                    model_size=model_size
                )
                
                comparison_results.append(result)
                
            except Exception as e:
                print(f"Model karşılaştırma hatası ({model_name}): {str(e)}")
                continue
        
        # Sonuçları F1 skoruna göre sırala
        comparison_results.sort(key=lambda x: x.metrics.f1_score, reverse=True)
        
        return comparison_results
    
    def analyze_bias(self, model: Any, X: np.ndarray, y: np.ndarray,
                     sensitive_features: List[str]) -> BiasAnalysisResult:
        """
        Model yanlılık analizi
        
        Args:
            model: Model nesnesi
            X: Özellik matrisi
            y: Hedef değişken
            sensitive_features: Hassas özellikler
            
        Returns:
            BiasAnalysisResult: Yanlılık analizi sonucu
        """
        # Model tahminleri
        y_pred = model.predict(X)
        y_pred_proba = None
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X)
        
        # Hassas özellik değerlerini al
        sensitive_values = {}
        for feature in sensitive_features:
            if feature in X.columns:
                sensitive_values[feature] = X[feature].values
        
        # Yanlılık metrikleri hesapla
        bias_metrics = {}
        
        for feature_name, feature_values in sensitive_values.items():
            unique_values = np.unique(feature_values)
            
            if len(unique_values) == 2:  # Binary sensitive feature
                # Demographic parity
                group_0_pred = np.mean(y_pred[feature_values == unique_values[0]])
                group_1_pred = np.mean(y_pred[feature_values == unique_values[1]])
                demographic_parity = abs(group_0_pred - group_1_pred)
                
                # Equalized odds
                if y_pred_proba is not None:
                    group_0_tpr = np.mean(y_pred_proba[feature_values == unique_values[0]][y[feature_values == unique_values[0]] == 1])
                    group_1_tpr = np.mean(y_pred_proba[feature_values == unique_values[1]][y[feature_values == unique_values[1]] == 1])
                    equalized_odds = abs(group_0_tpr - group_1_tpr)
                else:
                    equalized_odds = 0.0
                
                bias_metrics[feature_name] = {
                    "demographic_parity": demographic_parity,
                    "equalized_odds": equalized_odds
                }
        
        # Genel yanlılık skoru
        if bias_metrics:
            avg_demographic_parity = np.mean([m["demographic_parity"] for m in bias_metrics.values()])
            avg_equalized_odds = np.mean([m["equalized_odds"] for m in bias_metrics.values()])
        else:
            avg_demographic_parity = 0.0
            avg_equalized_odds = 0.0
        
        # Calibration (basit yaklaşım)
        calibration = 0.0
        if y_pred_proba is not None:
            # Basit calibration hesaplama
            prob_bins = np.linspace(0, 1, 11)
            calibration_scores = []
            
            for i in range(len(prob_bins) - 1):
                mask = (y_pred_proba[:, 1] >= prob_bins[i]) & (y_pred_proba[:, 1] < prob_bins[i + 1])
                if np.sum(mask) > 0:
                    expected_prob = (prob_bins[i] + prob_bins[i + 1]) / 2
                    actual_prob = np.mean(y[mask])
                    calibration_scores.append(abs(expected_prob - actual_prob))
            
            if calibration_scores:
                calibration = np.mean(calibration_scores)
        
        # Genel yanlılık skoru
        bias_score = (avg_demographic_parity + avg_equalized_odds + calibration) / 3
        
        return BiasAnalysisResult(
            demographic_parity=avg_demographic_parity,
            equalized_odds=avg_equalized_odds,
            calibration=calibration,
            bias_score=bias_score,
            fairness_metrics=bias_metrics
        )
    
    def analyze_feature_importance(self, model: Any, X: np.ndarray, y: np.ndarray,
                                 method: str = "permutation") -> FeatureImportanceResult:
        """
        Özellik önem sırası analizi
        
        Args:
            model: Model nesnesi
            X: Özellik matrisi
            y: Hedef değişken
            method: Analiz metodu
            
        Returns:
            FeatureImportanceResult: Özellik önem sırası sonucu
        """
        feature_names = list(X.columns) if hasattr(X, 'columns') else [f"feature_{i}" for i in range(X.shape[1])]
        
        if method == "permutation":
            # Permutation importance
            if hasattr(model, 'feature_importances_'):
                importance_scores = model.feature_importances_
            else:
                # Permutation importance hesapla
                baseline_score = model.score(X, y)
                importance_scores = []
                
                for i in range(X.shape[1]):
                    X_permuted = X.copy()
                    np.random.shuffle(X_permuted[:, i])
                    permuted_score = model.score(X_permuted, y)
                    importance_scores.append(baseline_score - permuted_score)
                
                importance_scores = np.array(importance_scores)
        
        elif method == "tree_based":
            # Tree-based importance
            if hasattr(model, 'feature_importances_'):
                importance_scores = model.feature_importances_
            else:
                importance_scores = np.ones(len(feature_names))
        
        elif method == "correlation":
            # Correlation-based importance
            importance_scores = []
            for i in range(X.shape[1]):
                corr = np.corrcoef(X[:, i], y)[0, 1]
                importance_scores.append(abs(corr) if not np.isnan(corr) else 0.0)
            importance_scores = np.array(importance_scores)
        
        else:
            raise ValueError(f"Desteklenmeyen metod: {method}")
        
        # Özellik önem sırası
        feature_importance_pairs = list(zip(feature_names, importance_scores))
        feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
        
        sorted_features = [pair[0] for pair in feature_importance_pairs]
        sorted_scores = [pair[1] for pair in feature_importance_pairs]
        
        # Kümülatif önem
        cumulative_importance = np.cumsum(sorted_scores) / np.sum(sorted_scores)
        
        # Top özellikler
        top_features = sorted_features[:self.TOP_FEATURES_COUNT]
        
        return FeatureImportanceResult(
            feature_names=sorted_features,
            importance_scores=sorted_scores,
            importance_ranks=list(range(1, len(sorted_features) + 1)),
            cumulative_importance=cumulative_importance.tolist(),
            top_features=top_features
        )
    
    def create_evaluation_report(self, model: Any, X: np.ndarray, y: np.ndarray,
                                model_name: str = "Unknown Model",
                                sensitive_features: Optional[List[str]] = None) -> Dict:
        """
        Kapsamlı değerlendirme raporu oluşturma
        
        Args:
            model: Model nesnesi
            X: Özellik matrisi
            y: Hedef değişken
            model_name: Model adı
            sensitive_features: Hassas özellikler
            
        Returns:
            Dict: Değerlendirme raporu
        """
        print("📊 Model Değerlendirme Raporu Oluşturuluyor...")
        
        # Model tahminleri
        y_pred = model.predict(X)
        y_pred_proba = None
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X)
        
        # Temel metrikler
        if len(np.unique(y)) <= 10:  # Sınıflandırma
            metrics = self.calculate_classification_metrics(y, y_pred, y_pred_proba)
            task_type = "classification"
        else:  # Regresyon
            metrics = self.calculate_regression_metrics(y, y_pred)
            task_type = "regression"
        
        # Çapraz doğrulama
        cv_result = self.perform_cross_validation(model, X, y)
        
        # Yanlılık analizi
        bias_result = None
        if sensitive_features:
            try:
                bias_result = self.analyze_bias(model, X, y, sensitive_features)
            except Exception as e:
                print(f"Yanlılık analizi hatası: {str(e)}")
        
        # Özellik önem sırası
        feature_importance = None
        try:
            feature_importance = self.analyze_feature_importance(model, X, y)
        except Exception as e:
            print(f"Özellik önem analizi hatası: {str(e)}")
        
        # Rapor oluştur
        report = {
            "model_info": {
                "name": model_name,
                "task_type": task_type,
                "evaluation_date": datetime.now().isoformat()
            },
            "performance_metrics": {
                "classification": metrics if task_type == "classification" else None,
                "regression": metrics if task_type == "regression" else None
            },
            "cross_validation": {
                "mean_score": cv_result.mean_score,
                "std_score": cv_result.std_score,
                "cv_folds": cv_result.cv_folds,
                "scoring_method": cv_result.scoring_method
            },
            "bias_analysis": {
                "demographic_parity": bias_result.demographic_parity if bias_result else None,
                "equalized_odds": bias_result.equalized_odds if bias_result else None,
                "calibration": bias_result.calibration if bias_result else None,
                "bias_score": bias_result.bias_score if bias_result else None,
                "fairness_metrics": bias_result.fairness_metrics if bias_result else None
            } if bias_result else None,
            "feature_importance": {
                "top_features": feature_importance.top_features if feature_importance else None,
                "importance_scores": feature_importance.importance_scores[:10] if feature_importance else None,
                "cumulative_importance": feature_importance.cumulative_importance[:10] if feature_importance else None
            } if feature_importance else None,
            "summary": {
                "overall_performance": "GOOD" if (cv_result.mean_score > 0.8 if task_type == "classification" else cv_result.mean_score > 0.7) else "POOR",
                "bias_level": "LOW" if (bias_result and bias_result.bias_score < self.BIAS_THRESHOLD) else "HIGH" if bias_result else "UNKNOWN",
                "feature_importance_available": feature_importance is not None
            }
        }
        
        print("✅ Model Değerlendirme Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_model_evaluation():
    """Model Evaluation test fonksiyonu"""
    print("🧪 Model Evaluation Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    # Özellik matrisi
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    
    # Hassas özellik ekle
    X['sensitive_feature'] = np.random.choice([0, 1], n_samples)
    
    # Hedef değişken (sınıflandırma)
    y = ((X.iloc[:, 0] + X.iloc[:, 1] + X.iloc[:, 2]) > 0).astype(int)
    
    # Test modelleri
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    
    rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    
    # Modelleri eğit
    rf_model.fit(X, y)
    lr_model.fit(X, y)
    
    # Model Evaluation başlat
    evaluator = ModelEvaluation(random_state=42)
    
    # Tek model değerlendirme test
    print("\n📊 Tek Model Değerlendirme Test:")
    rf_report = evaluator.create_evaluation_report(
        rf_model, X, y, "RandomForest", ["sensitive_feature"]
    )
    print(f"   Model: {rf_report['model_info']['name']}")
    print(f"   Görev türü: {rf_report['model_info']['task_type']}")
    print(f"   Genel performans: {rf_report['summary']['overall_performance']}")
    
    # Model karşılaştırması test
    print("\n📈 Model Karşılaştırması Test:")
    models = {"RandomForest": rf_model, "LogisticRegression": lr_model}
    comparison_results = evaluator.compare_models(models, X.values, y.values)
    
    for result in comparison_results:
        print(f"   {result.model_name}: F1={result.metrics.f1_score:.4f}, CV={result.cv_result.mean_score:.4f}")
    
    # Yanlılık analizi test
    print("\n⚖️ Yanlılık Analizi Test:")
    bias_result = evaluator.analyze_bias(rf_model, X, y, ["sensitive_feature"])
    print(f"   Yanlılık skoru: {bias_result.bias_score:.4f}")
    print(f"   Demographic parity: {bias_result.demographic_parity:.4f}")
    print(f"   Equalized odds: {bias_result.equalized_odds:.4f}")
    
    # Özellik önem sırası test
    print("\n🎯 Özellik Önem Sırası Test:")
    feature_importance = evaluator.analyze_feature_importance(rf_model, X, y)
    print(f"   Top özellikler: {feature_importance.top_features[:5]}")
    print(f"   En önemli özellik: {feature_importance.top_features[0]}")
    
    # Çapraz doğrulama test
    print("\n🔄 Çapraz Doğrulama Test:")
    cv_result = evaluator.perform_cross_validation(rf_model, X.values, y.values, cv_folds=5)
    print(f"   CV ortalama skor: {cv_result.mean_score:.4f}")
    print(f"   CV standart sapma: {cv_result.std_score:.4f}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Değerlendirme Raporu Test:")
    comprehensive_report = evaluator.create_evaluation_report(
        rf_model, X, y, "RandomForest_Comprehensive", ["sensitive_feature"]
    )
    print(f"   Performans: {comprehensive_report['summary']['overall_performance']}")
    print(f"   Yanlılık seviyesi: {comprehensive_report['summary']['bias_level']}")
    print(f"   Özellik önem mevcut: {comprehensive_report['summary']['feature_importance_available']}")
    
    print("\n✅ Model Evaluation Test Tamamlandı!")
    return evaluator

if __name__ == "__main__":
    test_model_evaluation()
