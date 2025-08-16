"""
PRD v2.0 - BIST AI Smart Trader
Market Data Integration Module

Piyasa veri entegrasyonu:
- Real-time data feeds
- Historical data retrieval
- Data validation and cleaning
- Market data storage
- Data synchronization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MarketDataPoint:
    """Piyasa veri noktası"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    spread: Optional[float] = None
    source: str = "unknown"

@dataclass
class DataFeed:
    """Veri akışı"""
    feed_id: str
    name: str
    description: str
    symbols: List[str]
    update_frequency: str  # real-time, 1min, 5min, 15min, 1hour, daily
    data_types: List[str]  # OHLCV, bid/ask, level2, news
    status: str = "active"  # active, inactive, error
    last_update: datetime = None
    created_at: datetime = None

@dataclass
class DataQuality:
    """Veri kalitesi"""
    symbol: str
    timestamp: datetime
    completeness: float  # 0-1
    accuracy: float  # 0-1
    latency: float  # milisaniye
    gaps: int
    outliers: int
    quality_score: float  # 0-100
    issues: List[str]

@dataclass
class MarketDataRequest:
    """Piyasa veri isteği"""
    request_id: str
    symbol: str
    data_type: str  # real-time, historical, intraday
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    interval: str = "1min"
    fields: List[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = None

class MarketDataIntegration:
    """
    Piyasa Veri Entegrasyonu
    
    PRD v2.0 gereksinimleri:
    - Gerçek zamanlı veri akışları
    - Geçmiş veri alma
    - Veri doğrulama ve temizleme
    - Piyasa veri depolama
    - Veri senkronizasyonu
    """
    
    def __init__(self):
        """Market Data Integration başlatıcı"""
        # Veri akışları
        self.data_feeds = {}
        
        # Piyasa verileri
        self.market_data = {}
        
        # Veri kalitesi
        self.data_quality = {}
        
        # Veri istekleri
        self.data_requests = {}
        
        # Veri kaynakları
        self.data_sources = {
            'finnhub': 'Finnhub API',
            'yfinance': 'Yahoo Finance',
            'investing': 'Investing.com',
            'kap': 'KAP',
            'tcmb': 'TCMB',
            'borsa_istanbul': 'Borsa İstanbul'
        }
        
        # Varsayılan veri akışlarını ekle
        self._add_default_feeds()
        
        # Veri depolama
        self.data_storage = {}
        
        # Senkronizasyon durumu
        self.sync_status = {
            'last_sync': None,
            'sync_interval': 60,  # saniye
            'auto_sync': True
        }
    
    def _add_default_feeds(self):
        """Varsayılan veri akışlarını ekle"""
        feeds = {
            'bist_realtime': DataFeed(
                feed_id='bist_realtime',
                name='BIST Gerçek Zamanlı',
                description='BIST hisseleri gerçek zamanlı veri',
                symbols=['SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'GARAN.IS', 'AKBNK.IS'],
                update_frequency='real-time',
                data_types=['OHLCV', 'bid/ask'],
                created_at=datetime.now()
            ),
            'bist_intraday': DataFeed(
                feed_id='bist_intraday',
                name='BIST Gün İçi',
                description='BIST hisseleri gün içi veri',
                symbols=['SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'GARAN.IS', 'AKBNK.IS'],
                update_frequency='1min',
                data_types=['OHLCV'],
                created_at=datetime.now()
            ),
            'bist_daily': DataFeed(
                feed_id='bist_daily',
                name='BIST Günlük',
                description='BIST hisseleri günlük veri',
                symbols=['SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'GARAN.IS', 'AKBNK.IS'],
                update_frequency='daily',
                data_types=['OHLCV'],
                created_at=datetime.now()
            ),
            'forex_realtime': DataFeed(
                feed_id='forex_realtime',
                name='Döviz Gerçek Zamanlı',
                description='Döviz kurları gerçek zamanlı',
                symbols=['USDTRY', 'EURTRY', 'GBPTRY', 'EURUSD'],
                update_frequency='real-time',
                data_types=['bid/ask'],
                created_at=datetime.now()
            )
        }
        
        self.data_feeds.update(feeds)
        print("✅ Varsayılan veri akışları eklendi")
    
    def create_data_feed(self, feed: DataFeed) -> bool:
        """
        Veri akışı oluştur
        
        Args:
            feed: Veri akışı
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if feed.feed_id in self.data_feeds:
                print(f"⚠️ Veri akışı zaten mevcut: {feed.feed_id}")
                return False
            
            self.data_feeds[feed.feed_id] = feed
            print(f"✅ Veri akışı oluşturuldu: {feed.name}")
            return True
            
        except Exception as e:
            print(f"❌ Veri akışı oluşturma hatası: {str(e)}")
            return False
    
    def get_data_feed(self, feed_id: str) -> Optional[DataFeed]:
        """
        Veri akışını al
        
        Args:
            feed_id: Akış ID
            
        Returns:
            Optional[DataFeed]: Veri akışı
        """
        return self.data_feeds.get(feed_id)
    
    def update_market_data(self, symbol: str, data: Dict[str, Any], source: str = "unknown") -> bool:
        """
        Piyasa verisini güncelle
        
        Args:
            symbol: Sembol
            data: Veri
            source: Kaynak
            
        Returns:
            bool: Başarı durumu
        """
        try:
            timestamp = datetime.now()
            
            # Veri noktası oluştur
            data_point = MarketDataPoint(
                symbol=symbol,
                timestamp=timestamp,
                open=data.get('open', 0.0),
                high=data.get('high', 0.0),
                low=data.get('low', 0.0),
                close=data.get('close', 0.0),
                volume=data.get('volume', 0.0),
                bid=data.get('bid'),
                ask=data.get('ask'),
                last=data.get('last'),
                spread=data.get('spread'),
                source=source
            )
            
            # Veriyi kaydet
            if symbol not in self.market_data:
                self.market_data[symbol] = []
            
            self.market_data[symbol].append(data_point)
            
            # Veri kalitesini kontrol et
            self._check_data_quality(symbol, data_point)
            
            # Veri akışını güncelle
            self._update_feed_status(symbol)
            
            return True
            
        except Exception as e:
            print(f"❌ Piyasa verisi güncelleme hatası: {str(e)}")
            return False
    
    def get_market_data(self, symbol: str, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None, limit: Optional[int] = None) -> List[MarketDataPoint]:
        """
        Piyasa verisini al
        
        Args:
            symbol: Sembol
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            limit: Limit
            
        Returns:
            List[MarketDataPoint]: Piyasa veri listesi
        """
        try:
            if symbol not in self.market_data:
                return []
            
            data_points = self.market_data[symbol]
            
            # Zaman filtresi
            if start_time:
                data_points = [dp for dp in data_points if dp.timestamp >= start_time]
            
            if end_time:
                data_points = [dp for dp in data_points if dp.timestamp <= end_time]
            
            # Limit
            if limit:
                data_points = data_points[-limit:]
            
            return data_points
            
        except Exception as e:
            print(f"❌ Piyasa verisi alma hatası: {str(e)}")
            return []
    
    def get_latest_data(self, symbol: str) -> Optional[MarketDataPoint]:
        """
        En son veriyi al
        
        Args:
            symbol: Sembol
            
        Returns:
            Optional[MarketDataPoint]: En son veri
        """
        try:
            if symbol not in self.market_data or not self.market_data[symbol]:
                return None
            
            return self.market_data[symbol][-1]
            
        except Exception:
            return None
    
    def get_historical_data(self, symbol: str, days: int = 30, interval: str = "daily") -> pd.DataFrame:
        """
        Geçmiş veriyi al
        
        Args:
            symbol: Sembol
            days: Gün sayısı
            interval: Aralık
            
        Returns:
            pd.DataFrame: Geçmiş veri
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            data_points = self.get_market_data(symbol, start_time, end_time)
            
            if not data_points:
                return pd.DataFrame()
            
            # DataFrame'e dönüştür
            data = []
            for dp in data_points:
                data.append({
                    'timestamp': dp.timestamp,
                    'open': dp.open,
                    'high': dp.high,
                    'low': dp.low,
                    'close': dp.close,
                    'volume': dp.volume,
                    'bid': dp.bid,
                    'ask': dp.ask,
                    'last': dp.last,
                    'spread': dp.spread,
                    'source': dp.source
                })
            
            df = pd.DataFrame(data)
            
            # Zaman sıralaması
            if not df.empty:
                df = df.sort_values('timestamp')
                df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Geçmiş veri alma hatası: {str(e)}")
            return pd.DataFrame()
    
    def create_data_request(self, symbol: str, data_type: str, start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None, interval: str = "1min",
                            fields: Optional[List[str]] = None) -> str:
        """
        Veri isteği oluştur
        
        Args:
            symbol: Sembol
            data_type: Veri türü
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            interval: Aralık
            fields: Alanlar
            
        Returns:
            str: İstek ID
        """
        try:
            request_id = f"req_{symbol}_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if fields is None:
                fields = ['open', 'high', 'low', 'close', 'volume']
            
            request = MarketDataRequest(
                request_id=request_id,
                symbol=symbol,
                data_type=data_type,
                start_time=start_time,
                end_time=end_time,
                interval=interval,
                fields=fields,
                created_at=datetime.now()
            )
            
            self.data_requests[request_id] = request
            print(f"✅ Veri isteği oluşturuldu: {request_id}")
            
            return request_id
            
        except Exception as e:
            print(f"❌ Veri isteği oluşturma hatası: {str(e)}")
            return ""
    
    def process_data_request(self, request_id: str) -> bool:
        """
        Veri isteğini işle
        
        Args:
            request_id: İstek ID
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if request_id not in self.data_requests:
                print(f"❌ Veri isteği bulunamadı: {request_id}")
                return False
            
            request = self.data_requests[request_id]
            request.status = "processing"
            
            # Simüle edilmiş veri işleme
            if request.data_type == "historical":
                # Geçmiş veri simülasyonu
                days = 30
                if request.start_time and request.end_time:
                    days = (request.end_time - request.start_time).days
                
                historical_data = self.get_historical_data(request.symbol, days, request.interval)
                
                if not historical_data.empty:
                    request.status = "completed"
                    print(f"✅ Geçmiş veri isteği tamamlandı: {request_id}")
                    return True
                else:
                    request.status = "failed"
                    print(f"❌ Geçmiş veri isteği başarısız: {request_id}")
                    return False
            
            elif request.data_type == "real-time":
                # Gerçek zamanlı veri simülasyonu
                latest_data = self.get_latest_data(request.symbol)
                
                if latest_data:
                    request.status = "completed"
                    print(f"✅ Gerçek zamanlı veri isteği tamamlandı: {request_id}")
                    return True
                else:
                    request.status = "failed"
                    print(f"❌ Gerçek zamanlı veri isteği başarısız: {request_id}")
                    return False
            
            else:
                request.status = "failed"
                print(f"❌ Bilinmeyen veri türü: {request.data_type}")
                return False
                
        except Exception as e:
            print(f"❌ Veri isteği işleme hatası: {str(e)}")
            if request_id in self.data_requests:
                self.data_requests[request_id].status = "failed"
            return False
    
    def _check_data_quality(self, symbol: str, data_point: MarketDataPoint):
        """Veri kalitesini kontrol et"""
        try:
            # Basit kalite kontrolleri
            completeness = 1.0
            accuracy = 1.0
            latency = 0.0
            gaps = 0
            outliers = 0
            issues = []
            
            # Eksik veri kontrolü
            if data_point.open == 0 or data_point.high == 0 or data_point.low == 0 or data_point.close == 0:
                completeness -= 0.25
                issues.append("Eksik OHLC verisi")
            
            # Mantık kontrolü
            if data_point.high < data_point.low:
                accuracy -= 0.5
                issues.append("High < Low")
            
            if data_point.high < data_point.open or data_point.high < data_point.close:
                accuracy -= 0.25
                issues.append("High < Open/Close")
            
            if data_point.low > data_point.open or data_point.low > data_point.close:
                accuracy -= 0.25
                issues.append("Low > Open/Close")
            
            # Latency hesaplama
            latency = (datetime.now() - data_point.timestamp).total_seconds() * 1000
            
            # Gap kontrolü
            if symbol in self.market_data and len(self.market_data[symbol]) > 1:
                prev_timestamp = self.market_data[symbol][-2].timestamp
                time_diff = (data_point.timestamp - prev_timestamp).total_seconds()
                
                if time_diff > 300:  # 5 dakikadan fazla
                    gaps += 1
                    issues.append(f"Veri boşluğu: {time_diff:.0f} saniye")
            
            # Outlier kontrolü (basit)
            if symbol in self.market_data and len(self.market_data[symbol]) > 10:
                recent_prices = [dp.close for dp in self.market_data[symbol][-10:]]
                mean_price = np.mean(recent_prices)
                std_price = np.std(recent_prices)
                
                if abs(data_point.close - mean_price) > 3 * std_price:
                    outliers += 1
                    issues.append("Aykırı fiyat")
            
            # Kalite skoru
            quality_score = (completeness + accuracy) * 50
            
            # Veri kalitesi kaydet
            data_quality = DataQuality(
                symbol=symbol,
                timestamp=data_point.timestamp,
                completeness=completeness,
                accuracy=accuracy,
                latency=latency,
                gaps=gaps,
                outliers=outliers,
                quality_score=quality_score,
                issues=issues
            )
            
            self.data_quality[f"{symbol}_{data_point.timestamp.strftime('%Y%m%d_%H%M%S')}"] = data_quality
            
        except Exception as e:
            print(f"❌ Veri kalitesi kontrol hatası: {str(e)}")
    
    def _update_feed_status(self, symbol: str):
        """Veri akışı durumunu güncelle"""
        try:
            for feed_id, feed in self.data_feeds.items():
                if symbol in feed.symbols:
                    feed.last_update = datetime.now()
                    feed.status = "active"
                    
        except Exception as e:
            print(f"❌ Veri akışı durum güncelleme hatası: {str(e)}")
    
    def get_data_quality_report(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Veri kalitesi raporu al
        
        Args:
            symbol: Sembol
            days: Gün sayısı
            
        Returns:
            Dict[str, Any]: Kalite raporu
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Kalite verilerini filtrele
            quality_data = []
            for quality_id, quality in self.data_quality.items():
                if quality.symbol == symbol and start_time <= quality.timestamp <= end_time:
                    quality_data.append(quality)
            
            if not quality_data:
                return {'error': 'Kalite verisi bulunamadı'}
            
            # İstatistikler
            report = {
                'symbol': symbol,
                'period_days': days,
                'total_records': len(quality_data),
                'average_completeness': np.mean([q.completeness for q in quality_data]),
                'average_accuracy': np.mean([q.accuracy for q in quality_data]),
                'average_latency': np.mean([q.latency for q in quality_data]),
                'total_gaps': sum([q.gaps for q in quality_data]),
                'total_outliers': sum([q.outliers for q in quality_data]),
                'average_quality_score': np.mean([q.quality_score for q in quality_data]),
                'issues_summary': {}
            }
            
            # Sorun özeti
            for quality in quality_data:
                for issue in quality.issues:
                    if issue not in report['issues_summary']:
                        report['issues_summary'][issue] = 0
                    report['issues_summary'][issue] += 1
            
            return report
            
        except Exception as e:
            print(f"❌ Veri kalitesi raporu alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Entegrasyon özetini al"""
        try:
            summary = {
                'total_feeds': len(self.data_feeds),
                'active_feeds': len([f for f in self.data_feeds.values() if f.status == "active"]),
                'total_symbols': len(set([symbol for feed in self.data_feeds.values() for symbol in feed.symbols])),
                'total_data_points': sum([len(data) for data in self.market_data.values()]),
                'total_requests': len(self.data_requests),
                'completed_requests': len([r for r in self.data_requests.values() if r.status == "completed"]),
                'failed_requests': len([r for r in self.data_requests.values() if r.status == "failed"]),
                'data_sources': list(self.data_sources.keys()),
                'sync_status': self.sync_status.copy()
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Entegrasyon özeti alma hatası: {str(e)}")
            return {'error': str(e)}

# Test fonksiyonu
def test_market_data_integration():
    """Market Data Integration test fonksiyonu"""
    print("🧪 Market Data Integration Test Başlıyor...")
    
    # Market Data Integration başlat
    mdi = MarketDataIntegration()
    
    # Veri akışları test
    print("\n📡 Veri Akışları Test:")
    feeds = mdi.data_feeds
    print(f"   ✅ {len(feeds)} veri akışı mevcut")
    for feed_id, feed in feeds.items():
        print(f"     {feed.name}: {feed.description}")
        print(f"       Semboller: {len(feed.symbols)}, Güncelleme: {feed.update_frequency}")
    
    # Yeni veri akışı oluştur test
    print("\n🏗️ Yeni Veri Akışı Test:")
    custom_feed = DataFeed(
        feed_id='custom_feed',
        name='Özel Veri Akışı',
        description='Özel semboller için veri akışı',
        symbols=['CUSTOM1', 'CUSTOM2'],
        update_frequency='5min',
        data_types=['OHLCV']
    )
    
    feed_created = mdi.create_data_feed(custom_feed)
    print(f"   Yeni veri akışı oluşturuldu: {feed_created}")
    
    # Piyasa verisi güncelleme test
    print("\n📊 Piyasa Verisi Güncelleme Test:")
    test_data = {
        'open': 45.00,
        'high': 45.75,
        'low': 44.80,
        'close': 45.50,
        'volume': 1000000,
        'bid': 45.45,
        'ask': 45.55,
        'last': 45.50,
        'spread': 0.10
    }
    
    data_updated = mdi.update_market_data("SISE.IS", test_data, "test_source")
    print(f"   Piyasa verisi güncellendi: {data_updated}")
    
    # Piyasa verisi alma test
    print("\n📥 Piyasa Verisi Alma Test:")
    market_data = mdi.get_market_data("SISE.IS")
    print(f"   ✅ Piyasa verisi alındı: {len(market_data)} kayıt")
    
    if market_data:
        latest_data = market_data[-1]
        print(f"   📊 Son veri: {latest_data.symbol} @ {latest_data.timestamp}")
        print(f"   📈 OHLC: {latest_data.open:.2f}/{latest_data.high:.2f}/{latest_data.low:.2f}/{latest_data.close:.2f}")
        print(f"   📊 Hacim: {latest_data.volume:,.0f}")
    
    # En son veri test
    print("\n🕐 En Son Veri Test:")
    latest_data = mdi.get_latest_data("SISE.IS")
    if latest_data:
        print(f"   ✅ En son veri alındı: {latest_data.symbol}")
        print(f"   📅 Zaman: {latest_data.timestamp}")
        print(f"   📊 Kapanış: {latest_data.close:.2f}")
    
    # Geçmiş veri test
    print("\n📚 Geçmiş Veri Test:")
    historical_data = mdi.get_historical_data("SISE.IS", days=7, interval="daily")
    if not historical_data.empty:
        print(f"   ✅ Geçmiş veri alındı: {len(historical_data)} kayıt")
        print(f"   📅 Dönem: {historical_data['timestamp'].min()} - {historical_data['timestamp'].max()}")
        print(f"   📊 Veri şekli: {historical_data.shape}")
    else:
        print("   ⚠️ Geçmiş veri bulunamadı")
    
    # Veri isteği oluşturma test
    print("\n📋 Veri İsteği Oluşturma Test:")
    request_id = mdi.create_data_request(
        symbol="SISE.IS",
        data_type="historical",
        start_time=datetime.now() - timedelta(days=30),
        end_time=datetime.now(),
        interval="daily"
    )
    
    print(f"   ✅ Veri isteği oluşturuldu: {request_id}")
    
    # Veri isteği işleme test
    print("\n⚙️ Veri İsteği İşleme Test:")
    request_processed = mdi.process_data_request(request_id)
    print(f"   Veri isteği işlendi: {request_processed}")
    
    # Veri kalitesi raporu test
    print("\n🔍 Veri Kalitesi Raporu Test:")
    quality_report = mdi.get_data_quality_report("SISE.IS", days=7)
    if 'error' not in quality_report:
        print(f"   ✅ Veri kalitesi raporu alındı")
        print(f"   📊 Toplam kayıt: {quality_report['total_records']}")
        print(f"   ✅ Ortalama tamlık: {quality_report['average_completeness']:.3f}")
        print(f"   ✅ Ortalama doğruluk: {quality_report['average_accuracy']:.3f}")
        print(f"   ⚠️ Toplam boşluk: {quality_report['total_gaps']}")
        print(f"   ⚠️ Toplam aykırı: {quality_report['total_outliers']}")
        print(f"   📊 Ortalama kalite skoru: {quality_report['average_quality_score']:.1f}/100")
    
    # Entegrasyon özeti test
    print("\n📊 Entegrasyon Özeti Test:")
    integration_summary = mdi.get_integration_summary()
    if 'error' not in integration_summary:
        print(f"   ✅ Entegrasyon özeti alındı")
        print(f"   📡 Toplam akış: {integration_summary['total_feeds']}")
        print(f"   ✅ Aktif akış: {integration_summary['active_feeds']}")
        print(f"   📊 Toplam sembol: {integration_summary['total_symbols']}")
        print(f"   📈 Toplam veri noktası: {integration_summary['total_data_points']}")
        print(f"   📋 Toplam istek: {integration_summary['total_requests']}")
        print(f"   ✅ Tamamlanan istek: {integration_summary['completed_requests']}")
        print(f"   ❌ Başarısız istek: {integration_summary['failed_requests']}")
    
    # Veri akışı durumu test
    print("\n📡 Veri Akışı Durumu Test:")
    for feed_id, feed in mdi.data_feeds.items():
        print(f"   {feed.name}: {feed.status}")
        if feed.last_update:
            print(f"     Son güncelleme: {feed.last_update}")
    
    print("\n✅ Market Data Integration Test Tamamlandı!")
    
    return mdi

if __name__ == "__main__":
    test_market_data_integration()
