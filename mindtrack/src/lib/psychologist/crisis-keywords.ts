export const CRISIS_KEYWORDS = {
  suicide: {
    tr: ["intihar", "kendimi öldürmek", "yaşamak istemiyorum", "ölmek istiyorum", "intihar planı"],
    en: ["suicide", "kill myself", "don't want to live", "want to die", "suicide plan"],
    severity: "high" as const,
  },
  selfHarm: {
    tr: ["kendime zarar vermek", "kesmek", "yanmak", "kendimi yaralamak"],
    en: ["self harm", "cut myself", "burn myself", "hurt myself"],
    severity: "high" as const,
  },
  violence: {
    tr: ["öldürmek", "zarar vermek", "şiddet", "saldırmak"],
    en: ["kill", "harm", "violence", "attack"],
    severity: "high" as const,
  },
  hopelessness: {
    tr: ["umutsuz", "çaresiz", "hiçbir şey işe yaramıyor", "sonu yok"],
    en: ["hopeless", "helpless", "nothing works", "no end"],
    severity: "medium" as const,
  },
  substance: {
    tr: ["aşırı alkol", "uyuşturucu", "overdose", "aşırı doz"],
    en: ["excessive alcohol", "drugs", "overdose", "over dose"],
    severity: "medium" as const,
  },
  anxiety: {
    tr: ["kaygı", "panik", "çarpıntı", "nefes darlığı", "gergin"],
    en: ["anxiety", "panic", "palpitations", "shortness of breath", "tense"],
    severity: "low" as const,
  },
  depression: {
    tr: ["depresyon", "üzgün", "mutsuz", "enerjisiz", "isteksiz"],
    en: ["depression", "sad", "unhappy", "low energy", "unmotivated"],
    severity: "low" as const,
  },
};

export function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[ıİ]/g, "i")
    .replace(/[ğĞ]/g, "g")
    .replace(/[üÜ]/g, "u")
    .replace(/[şŞ]/g, "s")
    .replace(/[öÖ]/g, "o")
    .replace(/[çÇ]/g, "c");
}





