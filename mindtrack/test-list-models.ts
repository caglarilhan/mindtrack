/**
 * Mevcut Gemini modellerini listelemek için script
 */
import { config } from 'dotenv';
import { resolve } from 'path';
import { GoogleGenerativeAI } from '@google/generative-ai';

config({ path: resolve(process.cwd(), '.env.local') });

async function listModels() {
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  if (!apiKey) {
    console.error('❌ API key bulunamadı!');
    return;
  }

  const client = new GoogleGenerativeAI(apiKey);
  
  try {
    // Modelleri listele
    const models = await client.listModels();
    console.log('📋 Mevcut modeller:');
    console.log(JSON.stringify(models, null, 2));
  } catch (error: any) {
    console.error('❌ Hata:', error.message);
    
    // Alternatif: Direkt test et
    console.log('\n🔄 Alternatif modelleri test ediyorum...\n');
    
    const testModels = [
      'gemini-1.5-flash',
      'gemini-1.5-pro',
      'gemini-pro',
      'gemini-1.0-pro',
    ];
    
    for (const modelName of testModels) {
      try {
        const model = client.getGenerativeModel({ model: modelName });
        const result = await model.generateContent('Test');
        console.log(`✅ ${modelName} çalışıyor!`);
        break;
      } catch (e: any) {
        console.log(`❌ ${modelName} çalışmıyor: ${e.message.substring(0, 50)}...`);
      }
    }
  }
}

listModels();





