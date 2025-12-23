import { notFound } from 'next/navigation';
import { getRequestConfig } from 'next-intl/server';

export const locales = ['en', 'es', 'tr', 'de'] as const;
export type Locale = typeof locales[number];
export const defaultLocale: Locale = 'tr';

export const localeInfo = {
  en: { name: 'English (US)', flag: '🇺🇸', nativeName: 'English' },
  es: { name: 'Spanish', flag: '🇪🇸', nativeName: 'Español' },
  tr: { name: 'Turkish', flag: '🇹🇷', nativeName: 'Türkçe' },
  de: { name: 'German', flag: '🇩🇪', nativeName: 'Deutsch' }
};

export default getRequestConfig(async ({ locale }) => {
  const current = (locale || defaultLocale) as Locale;
  if (!locales.includes(current)) notFound();
  return {
    locale: current,
    messages: (await import(`./messages/${current}.json`)).default
  };
});


