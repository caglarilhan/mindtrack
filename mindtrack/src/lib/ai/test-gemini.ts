/**
 * Gemini servisini test etmek için basit bir script
 * Kullanım: Bu dosyayı import edip test edebilirsin
 */

import { getGeminiService } from "./gemini-service";

export async function testGeminiSOAP() {
  console.log("🧪 Gemini SOAP testi başlatılıyor...");

  const gemini = getGeminiService();

  if (!gemini.isAvailable()) {
    console.error("❌ Gemini servisi kullanılamıyor. API key kontrol edin.");
    return null;
  }

  // Test transkripti
  const testTranscript = `
  Terapist: Merhaba, bugün nasıl hissediyorsun?
  
  Danışan: İyi değilim. Son birkaç gündür çok kaygılıyım. Uyuyamıyorum, sürekli endişeleniyorum.
  
  Terapist: Ne hakkında endişeleniyorsun?
  
  Danışan: İş yerinde bir sunum yapmam gerekiyor ve çok korkuyorum. Her şeyin kötü gideceğini düşünüyorum.
  
  Terapist: Bu endişeleri daha önce de yaşadın mı?
  
  Danışan: Evet, benzer durumlarda hep böyle oluyor. Ama bu sefer daha kötü.
  
  Terapist: Anlıyorum. Bugünkü seansımızda nefes egzersizleri yapalım mı?
  
  Danışan: Evet, lütfen.
  `;

  try {
    const soap = await gemini.generateSOAP(testTranscript);
    console.log("✅ SOAP notu başarıyla oluşturuldu:");
    console.log("\n📝 Subjective:", soap.subjective);
    console.log("\n👁️ Objective:", soap.objective);
    console.log("\n🔍 Assessment:", soap.assessment);
    console.log("\n📋 Plan:", soap.plan);

    return soap;
  } catch (error) {
    console.error("❌ Test hatası:", error);
    return null;
  }
}

export async function testGeminiSummary() {
  console.log("🧪 Gemini özetleme testi başlatılıyor...");

  const gemini = getGeminiService();

  if (!gemini.isAvailable()) {
    console.error("❌ Gemini servisi kullanılamıyor. API key kontrol edin.");
    return null;
  }

  // Test verisi
  const testData = `
  Hasta: Ahmet Yılmaz, 35 yaşında
  
  Seans 1 (2024-01-15):
  - İlk seans, kaygı bozukluğu şikayeti
  - İş yerinde stres yaşıyor
  - Uyku problemi var
  
  Seans 2 (2024-01-22):
  - Nefes egzersizleri öğretildi
  - İlerleme kaydedildi
  - Uyku düzeni biraz düzeldi
  
  Seans 3 (2024-01-29):
  - Sunum kaygısı devam ediyor
  - Aile ilişkilerinde sorunlar var
  - İlaç kullanımı önerildi ama reddetti
  `;

  try {
    const summary = await gemini.summarizePatientData(testData);
    console.log("✅ Özet başarıyla oluşturuldu:");
    console.log("\n📅 Timeline:", summary.timeline);
    console.log("\n🔑 Key Findings:", summary.keyFindings);
    console.log("\n💊 Medication History:", summary.medicationHistory);
    console.log("\n⚠️ Risk Factors:", summary.riskFactors);

    return summary;
  } catch (error) {
    console.error("❌ Test hatası:", error);
    return null;
  }
}





