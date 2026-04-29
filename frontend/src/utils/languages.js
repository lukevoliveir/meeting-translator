export const FLAG_MAP = {
  pt: '🇧🇷',
  en: '🇺🇸',
  es: '🇪🇸',
  fr: '🇫🇷',
  de: '🇩🇪',
  it: '🇮🇹',
  ja: '🇯🇵',
  zh: '🇨🇳',
  ko: '🇰🇷',
  ar: '🇸🇦',
}

export const NAME_MAP = {
  pt: 'Português',
  en: 'English',
  es: 'Español',
  fr: 'Français',
  de: 'Deutsch',
  it: 'Italiano',
  ja: '日本語',
  zh: '中文',
  ko: '한국어',
  ar: 'العربية',
}

export function getFlag(code) {
  return FLAG_MAP[code] ?? '🌐'
}

export function getName(code) {
  return NAME_MAP[code] ?? code
}
