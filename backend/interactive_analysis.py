"""
PRD v2.0 - BIST AI Smart Trader
Interactive Analysis Module

Etkileşimli analiz modülü:
- Real-time analysis
- Interactive filters
- Dynamic calculations
- User input handling
- Analysis workflows
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AnalysisFilter:
    """Analiz filtresi"""
    field: str
    operator: str  # '==', '!=', '>', '<', '>=', '<=', 'in', 'not_in', 'contains'
    value: Any
    description: str = ""

@dataclass
class AnalysisWorkflow:
    """Analiz iş akışı"""
    name: str
    steps: List[Dict[str, Any]]
    description: str = ""
    created_at: datetime = None
    last_modified: datetime = None

@dataclass
class AnalysisResult:
    """Analiz sonucu"""
    data: pd.DataFrame
    summary: Dict[str, Any]
    filters_applied: List[AnalysisFilter]
    calculations: Dict[str, Any]
    timestamp: datetime = None

class InteractiveAnalysis:
    """
    Etkileşimli Analiz Sistemi
    
    PRD v2.0 gereksinimleri:
    - Gerçek zamanlı analiz
    - Etkileşimli filtreler
    - Dinamik hesaplamalar
    - Kullanıcı girişi işleme
    - Analiz iş akışları
    """
    
    def __init__(self):
        """Interactive Analysis başlatıcı"""
        # Desteklenen operatörler
        self.SUPPORTED_OPERATORS = {
            '==': 'Eşit',
            '!=': 'Eşit değil',
            '>': 'Büyük',
            '<': 'Küçük',
            '>=': 'Büyük eşit',
            '<=': 'Küçük eşit',
            'in': 'İçinde',
            'not_in': 'İçinde değil',
            'contains': 'İçeriyor',
            'not_contains': 'İçermiyor',
            'starts_with': 'İle başlıyor',
            'ends_with': 'İle bitiyor',
            'between': 'Arasında',
            'is_null': 'Boş',
            'is_not_null': 'Boş değil'
        }
        
        # Analiz iş akışları
        self.workflows = {}
        
        # Dinamik hesaplama fonksiyonları
        self.calculation_functions = {}
        
        # Varsayılan hesaplama fonksiyonlarını ekle
        self._add_default_calculations()
    
    def _add_default_calculations(self):
        """Varsayılan hesaplama fonksiyonlarını ekle"""
        # Teknik indikatörler
        self.calculation_functions['sma'] = self._calculate_sma
        self.calculation_functions['ema'] = self._calculate_ema
        self.calculation_functions['rsi'] = self._calculate_rsi
        self.calculation_functions['macd'] = self._calculate_macd
        self.calculation_functions['bollinger_bands'] = self._calculate_bollinger_bands
        
        # İstatistiksel hesaplamalar
        self.calculation_functions['z_score'] = self._calculate_z_score
        self.calculation_functions['percentile'] = self._calculate_percentile
        self.calculation_functions['rolling_stats'] = self._calculate_rolling_stats
        
        # Finansal hesaplamalar
        self.calculation_functions['returns'] = self._calculate_returns
        self.calculation_functions['volatility'] = self._calculate_volatility
        self.calculation_functions['sharpe_ratio'] = self._calculate_sharpe_ratio
        self.calculation_functions['max_drawdown'] = self._calculate_max_drawdown
    
    def apply_filters(self, data: pd.DataFrame, filters: List[AnalysisFilter]) -> pd.DataFrame:
        """
        Veriye filtreleri uygula
        
        Args:
            data: Filtrelenecek veri
            filters: Uygulanacak filtreler
            
        Returns:
            pd.DataFrame: Filtrelenmiş veri
        """
        filtered_data = data.copy()
        
        for filter_obj in filters:
            if filter_obj.field not in filtered_data.columns:
                print(f"⚠️ Alan bulunamadı: {filter_obj.field}")
                continue
            
            try:
                if filter_obj.operator == '==':
                    filtered_data = filtered_data[filtered_data[filter_obj.field] == filter_obj.value]
                elif filter_obj.operator == '!=':
                    filtered_data = filtered_data[filtered_data[filter_obj.field] != filter_obj.value]
                elif filter_obj.operator == '>':
                    filtered_data = filtered_data[filtered_data[filter_obj.field] > filter_obj.value]
                elif filter_obj.operator == '<':
                    filtered_data = filtered_data[filtered_data[filter_obj.field] < filter_obj.value]
                elif filter_obj.operator == '>=':
                    filtered_data = filtered_data[filtered_data[filter_obj.field] >= filter_obj.value]
                elif filter_obj.operator == '<=':
                    filtered_data = filtered_data[filtered_data[filter_obj.field] <= filter_obj.value]
                elif filter_obj.operator == 'in':
                    filtered_data = filtered_data[filtered_data[filter_obj.field].isin(filter_obj.value)]
                elif filter_obj.operator == 'not_in':
                    filtered_data = filtered_data[~filtered_data[filter_obj.field].isin(filter_obj.value)]
                elif filter_obj.operator == 'contains':
                    filtered_data = filtered_data[filtered_data[filter_obj.field].str.contains(filter_obj.value, na=False)]
                elif filter_obj.operator == 'not_contains':
                    filtered_data = filtered_data[~filtered_data[filter_obj.field].str.contains(filter_obj.value, na=False)]
                elif filter_obj.operator == 'starts_with':
                    filtered_data = filtered_data[filtered_data[filter_obj.field].str.startswith(filter_obj.value, na=False)]
                elif filter_obj.operator == 'ends_with':
                    filtered_data = filtered_data[filtered_data[filter_obj.field].str.endswith(filter_obj.value, na=False)]
                elif filter_obj.operator == 'between':
                    if isinstance(filter_obj.value, (list, tuple)) and len(filter_obj.value) == 2:
                        filtered_data = filtered_data[
                            (filtered_data[filter_obj.field] >= filter_obj.value[0]) &
                            (filtered_data[filter_obj.field] <= filter_obj.value[1])
                        ]
                elif filter_obj.operator == 'is_null':
                    filtered_data = filtered_data[filtered_data[filter_obj.field].isnull()]
                elif filter_obj.operator == 'is_not_null':
                    filtered_data = filtered_data[filtered_data[filter_obj.field].notnull()]
                
            except Exception as e:
                print(f"❌ Filtre uygulama hatası ({filter_obj.field} {filter_obj.operator} {filter_obj.value}): {str(e)}")
        
        return filtered_data
    
    def add_calculation(self, name: str, function: Callable, description: str = ""):
        """
        Yeni hesaplama fonksiyonu ekle
        
        Args:
            name: Hesaplama adı
            function: Hesaplama fonksiyonu
            description: Açıklama
        """
        self.calculation_functions[name] = function
        print(f"✅ Hesaplama eklendi: {name} - {description}")
    
    def calculate_dynamic_metrics(self, data: pd.DataFrame, 
                                  calculations: List[str],
                                  params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Dinamik metrikleri hesapla
        
        Args:
            data: Veri
            calculations: Hesaplanacak metrikler
            params: Hesaplama parametreleri
            
        Returns:
            pd.DataFrame: Hesaplamalar eklenmiş veri
        """
        result_data = data.copy()
        
        for calc_name in calculations:
            if calc_name in self.calculation_functions:
                try:
                    if params and calc_name in params:
                        result_data = self.calculation_functions[calc_name](result_data, **params[calc_name])
                    else:
                        result_data = self.calculation_functions[calc_name](result_data)
                except Exception as e:
                    print(f"❌ Hesaplama hatası ({calc_name}): {str(e)}")
            else:
                print(f"⚠️ Hesaplama fonksiyonu bulunamadı: {calc_name}")
        
        return result_data
    
    def create_analysis_workflow(self, name: str, steps: List[Dict[str, Any]], 
                                 description: str = "") -> bool:
        """
        Analiz iş akışı oluştur
        
        Args:
            name: İş akışı adı
            steps: İş akışı adımları
            description: Açıklama
            
        Returns:
            bool: Başarı durumu
        """
        try:
            workflow = AnalysisWorkflow(
                name=name,
                steps=steps,
                description=description,
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            
            self.workflows[name] = workflow
            print(f"✅ Analiz iş akışı oluşturuldu: {name}")
            return True
            
        except Exception as e:
            print(f"❌ İş akışı oluşturma hatası: {str(e)}")
            return False
    
    def execute_workflow(self, workflow_name: str, data: pd.DataFrame,
                         parameters: Optional[Dict[str, Any]] = None) -> Optional[AnalysisResult]:
        """
        İş akışını çalıştır
        
        Args:
            workflow_name: İş akışı adı
            data: Giriş verisi
            parameters: Parametreler
            
        Returns:
            Optional[AnalysisResult]: Analiz sonucu
        """
        if workflow_name not in self.workflows:
            print(f"❌ İş akışı bulunamadı: {workflow_name}")
            return None
        
        workflow = self.workflows[workflow_name]
        current_data = data.copy()
        applied_filters = []
        calculations = {}
        
        try:
            for step in workflow.steps:
                step_type = step.get('type', '')
                
                if step_type == 'filter':
                    # Filtre uygula
                    filter_obj = AnalysisFilter(**step['filter'])
                    current_data = self.apply_filters(current_data, [filter_obj])
                    applied_filters.append(filter_obj)
                    
                elif step_type == 'calculation':
                    # Hesaplama yap
                    calc_name = step['calculation']
                    calc_params = step.get('parameters', {})
                    
                    if calc_name in self.calculation_functions:
                        current_data = self.calculation_functions[calc_name](current_data, **calc_params)
                        calculations[calc_name] = calc_params
                    
                elif step_type == 'aggregation':
                    # Toplama işlemi
                    group_by = step.get('group_by', [])
                    agg_funcs = step.get('aggregations', {})
                    
                    if group_by and agg_funcs:
                        current_data = current_data.groupby(group_by).agg(agg_funcs).reset_index()
                
                elif step_type == 'sorting':
                    # Sıralama
                    sort_by = step.get('sort_by', [])
                    ascending = step.get('ascending', True)
                    
                    if sort_by:
                        current_data = current_data.sort_values(sort_by, ascending=ascending)
                
                elif step_type == 'limit':
                    # Limit
                    limit = step.get('limit', 100)
                    current_data = current_data.head(limit)
            
            # Sonuç oluştur
            result = AnalysisResult(
                data=current_data,
                summary=self._generate_summary(current_data),
                filters_applied=applied_filters,
                calculations=calculations,
                timestamp=datetime.now()
            )
            
            print(f"✅ İş akışı çalıştırıldı: {workflow_name}")
            return result
            
        except Exception as e:
            print(f"❌ İş akışı çalıştırma hatası: {str(e)}")
            return None
    
    def _generate_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Veri özeti oluştur"""
        summary = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'memory_usage': data.memory_usage(deep=True).sum(),
            'data_types': data.dtypes.to_dict(),
            'missing_values': data.isnull().sum().to_dict(),
            'numeric_columns': data.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': data.select_dtypes(include=['object']).columns.tolist()
        }
        
        # Sayısal sütunlar için istatistikler
        if summary['numeric_columns']:
            numeric_stats = data[summary['numeric_columns']].describe()
            summary['numeric_statistics'] = numeric_stats.to_dict()
        
        return summary
    
    def get_available_calculations(self) -> List[str]:
        """Mevcut hesaplama fonksiyonlarını listele"""
        return list(self.calculation_functions.keys())
    
    def get_available_workflows(self) -> List[str]:
        """Mevcut iş akışlarını listele"""
        return list(self.workflows.keys())
    
    def export_workflow(self, workflow_name: str, format: str = 'json') -> Optional[str]:
        """
        İş akışını dışa aktar
        
        Args:
            workflow_name: İş akışı adı
            format: Dışa aktarma formatı
            
        Returns:
            Optional[str]: Dışa aktarılan veri
        """
        if workflow_name not in self.workflows:
            print(f"❌ İş akışı bulunamadı: {workflow_name}")
            return None
        
        workflow = self.workflows[workflow_name]
        
        try:
            if format == 'json':
                import json
                workflow_dict = {
                    'name': workflow.name,
                    'description': workflow.description,
                    'steps': workflow.steps,
                    'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
                    'last_modified': workflow.last_modified.isoformat() if workflow.last_modified else None
                }
                return json.dumps(workflow_dict, indent=2, ensure_ascii=False)
            else:
                print(f"⚠️ Desteklenmeyen format: {format}")
                return None
                
        except Exception as e:
            print(f"❌ Dışa aktarma hatası: {str(e)}")
            return None
    
    # Varsayılan hesaplama fonksiyonları
    def _calculate_sma(self, data: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.DataFrame:
        """Simple Moving Average hesapla"""
        result = data.copy()
        result[f'SMA_{window}'] = result[column].rolling(window=window).mean()
        return result
    
    def _calculate_ema(self, data: pd.DataFrame, span: int = 20, column: str = 'Close') -> pd.DataFrame:
        """Exponential Moving Average hesapla"""
        result = data.copy()
        result[f'EMA_{span}'] = result[column].ewm(span=span).mean()
        return result
    
    def _calculate_rsi(self, data: pd.DataFrame, window: int = 14, column: str = 'Close') -> pd.DataFrame:
        """RSI hesapla"""
        result = data.copy()
        delta = result[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        result[f'RSI_{window}'] = 100 - (100 / (1 + rs))
        return result
    
    def _calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, 
                        signal: int = 9, column: str = 'Close') -> pd.DataFrame:
        """MACD hesapla"""
        result = data.copy()
        ema_fast = result[column].ewm(span=fast).mean()
        ema_slow = result[column].ewm(span=slow).mean()
        result[f'MACD_{fast}_{slow}'] = ema_fast - ema_slow
        result[f'MACD_Signal_{signal}'] = result[f'MACD_{fast}_{slow}'].ewm(span=signal).mean()
        result[f'MACD_Histogram'] = result[f'MACD_{fast}_{slow}'] - result[f'MACD_Signal_{signal}']
        return result
    
    def _calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20, 
                                   std_dev: int = 2, column: str = 'Close') -> pd.DataFrame:
        """Bollinger Bands hesapla"""
        result = data.copy()
        sma = result[column].rolling(window=window).mean()
        std = result[column].rolling(window=window).std()
        result[f'BB_Upper_{window}'] = sma + (std * std_dev)
        result[f'BB_Lower_{window}'] = sma - (std * std_dev)
        result[f'BB_Middle_{window}'] = sma
        return result
    
    def _calculate_z_score(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """Z-score hesapla"""
        result = data.copy()
        result[f'{column}_ZScore'] = (result[column] - result[column].mean()) / result[column].std()
        return result
    
    def _calculate_percentile(self, data: pd.DataFrame, column: str, 
                             window: int = 20) -> pd.DataFrame:
        """Percentile hesapla"""
        result = data.copy()
        result[f'{column}_Percentile'] = result[column].rolling(window=window).rank(pct=True) * 100
        return result
    
    def _calculate_rolling_stats(self, data: pd.DataFrame, column: str, 
                                window: int = 20) -> pd.DataFrame:
        """Rolling istatistikler hesapla"""
        result = data.copy()
        result[f'{column}_Rolling_Mean'] = result[column].rolling(window=window).mean()
        result[f'{column}_Rolling_Std'] = result[column].rolling(window=window).std()
        result[f'{column}_Rolling_Min'] = result[column].rolling(window=window).min()
        result[f'{column}_Rolling_Max'] = result[column].rolling(window=window).max()
        return result
    
    def _calculate_returns(self, data: pd.DataFrame, column: str = 'Close') -> pd.DataFrame:
        """Getiri hesapla"""
        result = data.copy()
        result[f'{column}_Returns'] = result[column].pct_change()
        result[f'{column}_Log_Returns'] = np.log(result[column] / result[column].shift(1))
        return result
    
    def _calculate_volatility(self, data: pd.DataFrame, column: str = 'Close', 
                              window: int = 20, annualized: bool = True) -> pd.DataFrame:
        """Volatilite hesapla"""
        result = data.copy()
        returns = result[column].pct_change()
        volatility = returns.rolling(window=window).std()
        
        if annualized:
            # Yıllık volatilite (252 iş günü)
            volatility = volatility * np.sqrt(252)
        
        result[f'{column}_Volatility_{window}'] = volatility
        return result
    
    def _calculate_sharpe_ratio(self, data: pd.DataFrame, column: str = 'Close', 
                                window: int = 20, risk_free_rate: float = 0.02) -> pd.DataFrame:
        """Sharpe ratio hesapla"""
        result = data.copy()
        returns = result[column].pct_change()
        excess_returns = returns - risk_free_rate / 252  # Günlük risk-free rate
        
        rolling_mean = excess_returns.rolling(window=window).mean()
        rolling_std = returns.rolling(window=window).std()
        
        result[f'{column}_Sharpe_{window}'] = rolling_mean / rolling_std * np.sqrt(252)
        return result
    
    def _calculate_max_drawdown(self, data: pd.DataFrame, column: str = 'Close') -> pd.DataFrame:
        """Maximum drawdown hesapla"""
        result = data.copy()
        rolling_max = result[column].expanding().max()
        drawdown = (result[column] - rolling_max) / rolling_max * 100
        result[f'{column}_Drawdown'] = drawdown
        result[f'{column}_Max_Drawdown'] = drawdown.expanding().min()
        return result

# Test fonksiyonu
def test_interactive_analysis():
    """Interactive Analysis test fonksiyonu"""
    print("🧪 Interactive Analysis Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    test_data = pd.DataFrame({
        'Date': dates,
        'Symbol': ['SISE.IS'] * 100,
        'Open': 100 + np.cumsum(np.random.randn(100) * 0.02),
        'High': 100 + np.cumsum(np.random.randn(100) * 0.02) + np.random.rand(100) * 2,
        'Low': 100 + np.cumsum(np.random.randn(100) * 0.02) - np.random.rand(100) * 2,
        'Close': 100 + np.cumsum(np.random.randn(100) * 0.02),
        'Volume': np.random.randint(1000000, 10000000, 100),
        'Sector': ['INDUSTRIAL'] * 100,
        'Market_Cap': np.random.randint(10000000000, 100000000000, 100)
    })
    
    # Interactive Analysis başlat
    analysis = InteractiveAnalysis()
    
    # Filtre test
    print("\n🔍 Filtre Test:")
    filters = [
        AnalysisFilter('Volume', '>', 5000000, 'Yüksek hacim'),
        AnalysisFilter('Sector', '==', 'INDUSTRIAL', 'Endüstriyel sektör'),
        AnalysisFilter('Market_Cap', 'between', [20000000000, 80000000000], 'Orta büyüklük')
    ]
    
    filtered_data = analysis.apply_filters(test_data, filters)
    print(f"   ✅ Filtre uygulandı: {len(filtered_data)} kayıt kaldı")
    
    # Dinamik hesaplama test
    print("\n🧮 Dinamik Hesaplama Test:")
    calculations = ['sma', 'rsi', 'returns', 'volatility']
    params = {
        'sma': {'window': 20, 'column': 'Close'},
        'rsi': {'window': 14, 'column': 'Close'},
        'volatility': {'window': 20, 'column': 'Close', 'annualized': True}
    }
    
    calculated_data = analysis.calculate_dynamic_metrics(test_data, calculations, params)
    print(f"   ✅ Hesaplamalar eklendi: {len(calculated_data.columns)} sütun")
    
    # İş akışı test
    print("\n🔄 İş Akışı Test:")
    workflow_steps = [
        {
            'type': 'filter',
            'filter': {'field': 'Volume', 'operator': '>', 'value': 5000000, 'description': 'Yüksek hacim'}
        },
        {
            'type': 'calculation',
            'calculation': 'sma',
            'parameters': {'window': 20, 'column': 'Close'}
        },
        {
            'type': 'calculation',
            'calculation': 'rsi',
            'parameters': {'window': 14, 'column': 'Close'}
        },
        {
            'type': 'sorting',
            'sort_by': ['Volume'],
            'ascending': False
        },
        {
            'type': 'limit',
            'limit': 20
        }
    ]
    
    workflow_created = analysis.create_analysis_workflow(
        'test_workflow',
        workflow_steps,
        'Test iş akışı - Yüksek hacimli hisseler'
    )
    
    if workflow_created:
        # İş akışını çalıştır
        result = analysis.execute_workflow('test_workflow', test_data)
        
        if result:
            print(f"   ✅ İş akışı çalıştırıldı: {len(result.data)} sonuç")
            print(f"   📊 Özet: {result.summary['total_rows']} satır, {result.summary['total_columns']} sütun")
    
    # Dışa aktarma test
    print("\n💾 Dışa Aktarma Test:")
    if 'test_workflow' in analysis.workflows:
        exported = analysis.export_workflow('test_workflow', 'json')
        if exported:
            print("   ✅ İş akışı dışa aktarıldı")
    
    # Mevcut hesaplamalar ve iş akışları
    print("\n📋 Mevcut Özellikler:")
    print(f"   Hesaplama fonksiyonları: {len(analysis.get_available_calculations())}")
    print(f"   İş akışları: {len(analysis.get_available_workflows())}")
    
    print("\n✅ Interactive Analysis Test Tamamlandı!")
    
    return analysis

if __name__ == "__main__":
    test_interactive_analysis()
