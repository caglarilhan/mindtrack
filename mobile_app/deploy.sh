#!/bin/bash

# PRD v2.0 - BIST AI Smart Trader Flutter App Deployment Script
echo "🚀 BIST AI Smart Trader Flutter App Deployment Başlıyor..."

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter bulunamadı! Lütfen Flutter'ı kurun."
    exit 1
fi

echo "✅ Flutter mevcut: $(flutter --version | head -n 1)"

# Clean previous builds
echo "🧹 Önceki build'ler temizleniyor..."
flutter clean

# Get dependencies
echo "📦 Dependencies yükleniyor..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "❌ Dependencies yükleme hatası!"
    exit 1
fi

echo "✅ Dependencies yüklendi"

# Analyze code
echo "🔍 Kod analizi yapılıyor..."
flutter analyze

if [ $? -ne 0 ]; then
    echo "⚠️ Kod analizinde uyarılar var, ama devam ediliyor..."
else
    echo "✅ Kod analizi başarılı"
fi

# Build for different platforms
echo "🔨 Platform build'leri yapılıyor..."

# Web Build
echo "🌐 Web build yapılıyor..."
flutter build web --release

if [ $? -ne 0 ]; then
    echo "❌ Web build hatası!"
    exit 1
fi

echo "✅ Web build tamamlandı"

# Android Build (if needed)
if [ "$1" = "--android" ] || [ "$1" = "--all" ]; then
    echo "🤖 Android build yapılıyor..."
    flutter build apk --release
    
    if [ $? -ne 0 ]; then
        echo "❌ Android build hatası!"
        exit 1
    fi
    
    echo "✅ Android build tamamlandı"
fi

# iOS Build (if needed)
if [ "$1" = "--ios" ] || [ "$1" = "--all" ]; then
    echo "🍎 iOS build yapılıyor..."
    flutter build ios --release --no-codesign
    
    if [ $? -ne 0 ]; then
        echo "❌ iOS build hatası!"
        exit 1
    fi
    
    echo "✅ iOS build tamamlandı"
fi

# Desktop Build (if needed)
if [ "$1" = "--desktop" ] || [ "$1" = "--all" ]; then
    echo "💻 Desktop build yapılıyor..."
    
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        flutter build macos --release
        if [ $? -eq 0 ]; then
            echo "✅ macOS build tamamlandı"
        else
            echo "❌ macOS build hatası!"
        fi
    fi
    
    # Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        flutter build linux --release
        if [ $? -eq 0 ]; then
            echo "✅ Linux build tamamlandı"
        else
            echo "❌ Linux build hatası!"
        fi
    fi
    
    # Windows
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        flutter build windows --release
        if [ $? -eq 0 ]; then
            echo "✅ Windows build tamamlandı"
        else
            echo "❌ Windows build hatası!"
        fi
    fi
fi

# Show build results
echo ""
echo "🎉 BUILD TAMAMLANDI!"
echo ""
echo "📁 Build dosyaları:"
echo "   Web: build/web/"
echo "   Android: build/app/outputs/flutter-apk/"
echo "   iOS: build/ios/Release-iphoneos/"
echo "   macOS: build/macos/Build/Products/Release/"
echo "   Linux: build/linux/x64/release/bundle/"
echo "   Windows: build/windows/runner/Release/"
echo ""

# Deployment options
echo "🚀 Deployment seçenekleri:"
echo ""
echo "🌐 Web (Vercel/Netlify):"
echo "   cd build/web && vercel --prod"
echo "   veya"
echo "   cd build/web && netlify deploy --prod --dir=."
echo ""

echo "📱 Mobile:"
echo "   Android: build/app/outputs/flutter-apk/app-release.apk"
echo "   iOS: Xcode ile build/ios/Release-iphoneos/ klasörünü açın"
echo ""

echo "💻 Desktop:"
echo "   macOS: build/macos/Build/Products/Release/ klasöründeki .app dosyası"
echo "   Linux: build/linux/x64/release/bundle/ klasöründeki executable"
echo "   Windows: build/windows/runner/Release/ klasöründeki .exe dosyası"
echo ""

echo "📊 Build boyutları:"
if [ -d "build/web" ]; then
    echo "   Web: $(du -sh build/web | cut -f1)"
fi

if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
    echo "   Android APK: $(du -sh build/app/outputs/flutter-apk/app-release.apk | cut -f1)"
fi

echo ""
echo "✅ Deployment script tamamlandı!"
