import { NextResponse, NextRequest } from 'next/server';
import { locales, defaultLocale } from './src/i18n';

function pickLocale(acceptLanguageHeader: string | null): string {
  if (!acceptLanguageHeader) return defaultLocale;
  const header = acceptLanguageHeader.toLowerCase();
  // Basit eşleştirme: en, en-US, de, de-DE, es, es-ES, tr
  for (const loc of locales) {
    if (header.includes(loc.toLowerCase())) return loc;
  }
  // Bölgesel varyantlar için kısa kod eşleşmesi
  if (header.includes('en')) return 'en';
  return defaultLocale;
}

// Basit bellek içi rate limit (demo); prod için KV/Redis önerilir
// @ts-ignore
const rlStore: Map<string, { ts: number; count: number }> = (globalThis.__rl2 ||= new Map());

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Statik dosyalar ve API isteklerini atla
  const { pathname } = request.nextUrl;
  if (pathname.startsWith('/_next') || pathname.startsWith('/favicon')) {
    return response;
  }

  // Rate limiting (genel sayfa istekleri için basit throttle)
  const ip = request.ip || request.headers.get('x-forwarded-for') || 'unknown';
  const key = `rl:${ip}`;
  const now = Date.now();
  const rec = rlStore.get(key);
  if (rec && now - rec.ts < 1000) {
    rec.count += 1;
    if (rec.count > 10) {
      return new NextResponse('Too Many Requests', { status: 429 });
    }
  } else {
    rlStore.set(key, { ts: now, count: 1 });
  }

  const existing = request.cookies.get('locale')?.value;
  if (!existing) {
    const detected = pickLocale(request.headers.get('accept-language'));
    response.cookies.set('locale', detected, { path: '/', httpOnly: false, sameSite: 'lax' });
  }

  return response;
}

export const config = {
  matcher: ['/:path*']
};




