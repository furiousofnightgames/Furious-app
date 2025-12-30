import { createI18n } from 'vue-i18n'
import pt from './locales/pt'
import en from './locales/en'

// Detectar idioma do navegador
const getBrowserLocale = () => {
    const navigatorLocale = window.navigator.language || window.navigator.userLanguage
    if (navigatorLocale?.startsWith('en')) {
        return 'en'
    }
    return 'pt' // Fallback e padrão
}

const i18n = createI18n({
    legacy: false, // Compatiilidade com Composition API
    locale: getBrowserLocale(), // Idioma inicial
    fallbackLocale: 'pt',
    messages: {
        pt,
        en
    }
})

export default i18n
