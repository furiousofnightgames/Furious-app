import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
    // Theme color validated: Blue-600 (Final Fix)
    const currentTheme = ref('cyberpunk')
    const availableThemes = [
        { id: 'cyberpunk', name: 'PADRAO', color: '#2563eb' },
        { id: 'matrix', name: 'Matrix', color: '#00ff41' },
        { id: 'ocean', name: 'Ocean', color: '#38bdf8' },
        { id: 'dracula', name: 'Dracula', color: '#ff79c6' }
    ]

    function setTheme(themeId) {
        if (availableThemes.find(t => t.id === themeId)) {
            currentTheme.value = themeId
            localStorage.setItem('furious-theme', themeId)
            applyTheme(themeId)
        }
    }

    function applyTheme(themeId) {
        // Apply data-theme to HTML root or #app
        // Applying to documentElement allows variables to be global
        document.documentElement.setAttribute('data-theme', themeId)
    }

    function initTheme() {
        const saved = localStorage.getItem('furious-theme')
        if (saved && availableThemes.find(t => t.id === saved)) {
            currentTheme.value = saved
        } else {
            currentTheme.value = 'cyberpunk'
        }
        applyTheme(currentTheme.value)
    }

    return {
        currentTheme,
        availableThemes,
        setTheme,
        initTheme
    }
})
