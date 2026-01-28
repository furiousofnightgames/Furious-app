<template>
  <div class="relative group">
    <button 
      class="flex items-center space-x-1 px-2 py-2 rounded-lg transition-all duration-300
             bg-gray-800/50 hover:bg-gray-700/50 border border-transparent hover:border-neon group/theme"
      title="Alterar Tema"
    >
      <!-- Premium Animated Palette Icon -->
      <div class="relative w-5 h-5 flex items-center justify-center transition-transform duration-500 group-hover/theme:scale-110">
        <svg xmlns="http://www.w3.org/2000/svg" 
          class="w-full h-full transition-all duration-700 animate-orbit group-hover/theme:animate-none" 
          fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"
          :style="{ color: currentThemeInfo?.color || '#2563eb', filter: `drop-shadow(0 0 8px ${currentThemeInfo?.color}80)` }"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
        </svg>
        
        <!-- Center Dot that pulses separately -->
        <div 
          class="absolute inset-0 m-auto w-1 h-1 rounded-full animate-pulse-fast transition-colors duration-500 shadow-glow"
          :style="{ backgroundColor: currentThemeInfo?.color || '#2563eb' }"
        ></div>
      </div>

      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-gray-400 opacity-50 group-hover/theme:opacity-100 transition-opacity" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>

    <!-- Dropdown -->
    <div class="absolute right-0 top-full mt-2 w-48 rounded-md shadow-lg py-1 bg-[#1e293b] ring-1 ring-black ring-opacity-5 
                border border-gray-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible 
                transition-all duration-200 z-50 transform origin-top-right">
      <div class="px-2 py-1 text-xs text-gray-500 uppercase font-bold tracking-wider">Selecionar Visual</div>
      <a 
        v-for="theme in store.availableThemes" 
        :key="theme.id"
        href="#" 
        @click.prevent="store.setTheme(theme.id)"
        class="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
        :class="{ 'bg-gray-700/50 text-white': store.currentTheme === theme.id }"
      >
        <span 
          class="w-3 h-3 rounded-full mr-3"
          :style="{ backgroundColor: theme.color, boxShadow: `0 0 8px ${theme.color}` }"
        ></span>
        {{ theme.name }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '../stores/theme'

const store = useThemeStore()

const currentThemeInfo = computed(() => {
  return store.availableThemes.find(t => t.id === store.currentTheme)
})
</script>

<style scoped>
.border-neon {
  border-color: var(--primary);
  box-shadow: var(--glow-primary);
}

.shadow-glow {
  box-shadow: 0 0 12px currentColor;
}

@keyframes orbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse-fast {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.7; }
}

.animate-orbit {
  animation: orbit 10s linear infinite;
}

.animate-pulse-fast {
  animation: pulse-fast 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
