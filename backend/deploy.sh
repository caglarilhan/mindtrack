#!/bin/bash

# PRD v2.0 - BIST AI Smart Trader Production Deployment Script
echo "🚀 BIST AI Smart Trader Production Deployment Başlıyor..."

# Environment check
if [ ! -f .env ]; then
    echo "❌ .env dosyası bulunamadı!"
    echo "📝 env.example dosyasını .env olarak kopyalayın ve gerekli değerleri doldurun."
    exit 1
fi

# Docker check
if ! command -v docker &> /dev/null; then
    echo "❌ Docker bulunamadı! Lütfen Docker'ı kurun."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose bulunamadı! Lütfen Docker Compose'u kurun."
    exit 1
fi

echo "✅ Docker ve Docker Compose mevcut"

# Build and deploy
echo "🔨 Docker image'ları build ediliyor..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Build hatası!"
    exit 1
fi

echo "✅ Build tamamlandı"

# Stop existing containers
echo "🛑 Mevcut container'lar durduruluyor..."
docker-compose down

# Start services
echo "🚀 Servisler başlatılıyor..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Servis başlatma hatası!"
    exit 1
fi

echo "✅ Servisler başlatıldı"

# Wait for services to be ready
echo "⏳ Servislerin hazır olması bekleniyor..."
sleep 30

# Health check
echo "🏥 Health check yapılıyor..."
curl -f http://localhost:8000/health

if [ $? -eq 0 ]; then
    echo "✅ API health check başarılı"
else
    echo "❌ API health check başarısız"
    echo "📊 Container logları:"
    docker-compose logs api
    exit 1
fi

# Show running services
echo "📊 Çalışan servisler:"
docker-compose ps

echo ""
echo "🎉 DEPLOYMENT BAŞARILI!"
echo ""
echo "🌐 Servis URL'leri:"
echo "   API: http://localhost:8000"
echo "   Nginx: http://localhost:80"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000 (admin/admin)"
echo "   Redis: localhost:6379"
echo "   PostgreSQL: localhost:5432"
echo ""
echo "📝 Logları görüntülemek için:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "🛑 Servisleri durdurmak için:"
echo "   docker-compose down"
echo ""
echo "🔄 Servisleri yeniden başlatmak için:"
echo "   docker-compose restart"
