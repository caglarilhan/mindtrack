/**
 * Gemini servisini direkt test etmek için script
 * Kullanım: npx tsx test-gemini-direct.ts
 */

import { config } from 'dotenv';
import { resolve } from 'path';

// .env.local dosyasını yükle
config({ path: resolve(process.cwd(), '.env.local') });

import { getGeminiService } from './src/lib/ai/gemini-service';

async function testGemini() {
  console.log('🧪 Gemini servisi testi başlatılıyor...\n');
  
  // API key kontrolü
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  if (!apiKey) {
    console.error('❌ GOOGLE_GEMINI_API_KEY bulunamadı!');
    console.log('💡 .env.local dosyasında GOOGLE_GEMINI_API_KEY olduğundan emin olun.');
    process.exit(1);
  }
  
  console.log('✅ API Key bulundu:', apiKey.substring(0, 20) + '...');
  console.log('');
  
  const gemini = getGeminiService();
  
  if (!gemini.isAvailable()) {
    console.error('❌ Gemini servisi kullanılamıyor!');
    process.exit(1);
  }
  
  console.log('✅ Gemini servisi hazır!\n');
  
  // Test transkripti
  const testTranscript = `
Terapist: Merhaba, bugün nasılsın?

Danışan: İyi değilim, çok kaygılıyım. Son birkaç gündür uyuyamıyorum.

Terapist: Ne hakkında endişeleniyorsun?

Danışan: İş yerinde bir sunum yapmam gerekiyor ve çok korkuyorum. Her şeyin kötü gideceğini düşünüyorum.

Terapist: Bu endişeleri daha önce de yaşadın mı?

Danışan: Evet, benzer durumlarda hep böyle oluyor. Ama bu sefer daha kötü.

Terapist: Anlıyorum. Bugünkü seansımızda nefes egzersizleri yapalım mı?

Danışan: Evet, lütfen.
  `;
  
  console.log('📝 Test transkripti:');
  console.log(testTranscript);
  console.log('\n🔄 SOAP notu oluşturuluyor...\n');
  
  try {
    const startTime = Date.now();
    const soap = await gemini.generateSOAP(testTranscript);
    const duration = Date.now() - startTime;
    
    console.log('✅ SOAP notu başarıyla oluşturuldu!');
    console.log(`⏱️  Süre: ${duration}ms\n`);
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📋 SUBJECTIVE (S):');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(soap.subjective || '(Boş)');
    console.log('');
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('👁️  OBJECTIVE (O):');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(soap.objective || '(Boş)');
    console.log('');
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🔍 ASSESSMENT (A):');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(soap.assessment || '(Boş)');
    console.log('');
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📋 PLAN (P):');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(soap.plan || '(Boş)');
    console.log('');
    
    console.log('✅ Test başarılı! 🎉');
    
  } catch (error: any) {
    console.error('❌ Test hatası:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
}

testGemini();

