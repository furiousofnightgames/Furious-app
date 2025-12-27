<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-br from-gray-950 via-gray-900 to-black">
    <!-- Navigation -->
    <nav class="bg-gradient-to-r from-gray-900/90 to-black/90 border-b border-cyan-500/30 shadow-lg shadow-cyan-500/10 sticky top-0 z-40" style="will-change: auto;">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 py-3 sm:py-4">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2 sm:gap-3 min-w-0">
              <HamburgerButton @toggle="favoritesStore.toggleDrawer" />
              <div class="w-7 h-7 sm:w-8 sm:h-8 flex-shrink-0">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color: #06b6d4; stop-opacity: 1" />
                      <stop offset="100%" style="stop-color: #ec4899; stop-opacity: 1" />
                    </linearGradient>
                    <filter id="logoGlow" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                  <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="url(#logoGrad)" filter="url(#logoGlow)" class="animate-pulse"/>
                  <circle cx="12" cy="12" r="10" stroke="url(#logoGrad)" stroke-width="0.5" fill="none"/>
                </svg>
                </div>
                <h1 class="text-base sm:text-2xl font-bold text-cyan-300 uppercase tracking-widest truncate">fURIOUS APP</h1>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0 sm:hidden">
                <div :class="['w-2 h-2 rounded-full transition-all', isConnected ? 'bg-green-500 shadow-lg shadow-green-500/50 animate-pulse' : 'bg-red-500 shadow-lg shadow-red-500/50 animate-pulse']" />
              </div>
            </div>

            <div class="flex items-center gap-3 sm:gap-6">
              <div class="flex-1 overflow-x-auto sm:overflow-visible">
                <div class="flex items-center gap-2 md:gap-6 w-max sm:w-auto">
                  <router-link
                    v-for="link in navLinks"
                    :key="link.path"
                    :to="link.path"
                    :class="[
                      'shrink-0 whitespace-nowrap px-2 sm:px-3 md:px-4 py-1.5 sm:py-2 rounded-lg font-semibold transition-all duration-300 text-sm md:text-base flex items-center gap-2',
                      isActiveLink(link.path)
                        ? 'bg-cyan-500/30 text-cyan-300 border border-cyan-500/50 shadow-lg shadow-cyan-500/20' 
                        : 'text-gray-400 hover:text-cyan-300 hover:border hover:border-cyan-500/30'
                    ]"
                  >
            <!-- Dashboard Icon -->
            <svg v-if="link.path === '/'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 svg-icon">
              <defs>
                <linearGradient id="dashGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #06b6d4" />
                  <stop offset="100%" style="stop-color: #8b5cf6" />
                </linearGradient>
              </defs>
              <rect x="3" y="11" width="5" height="10" fill="url(#dashGrad)" opacity="0.8" rx="1" class="animate-bounce" style="animation-delay: 0s"/>
              <rect x="12" y="3" width="5" height="18" fill="url(#dashGrad)" opacity="0.8" rx="1" class="animate-bounce" style="animation-delay: 0.1s"/>
              <rect x="21" y="7" width="5" height="14" fill="url(#dashGrad)" opacity="0.8" rx="1" class="animate-bounce" style="animation-delay: 0.2s"/>
            </svg>
            
            <!-- Sources Icon -->
            <svg v-else-if="link.path === '/sources'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 svg-icon">
              <defs>
                <linearGradient id="sourceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #f59e0b" />
                  <stop offset="100%" style="stop-color: #ec4899" />
                </linearGradient>
              </defs>
              <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" 
                    stroke="url(#sourceGrad)" stroke-width="1.5" fill="none"/>
              <path d="M2 8H22" stroke="url(#sourceGrad)" stroke-width="1" opacity="0.5"/>
              <circle cx="8" cy="6" r="1.5" fill="url(#sourceGrad)" opacity="0.6" class="animate-pulse"/>
              <circle cx="13" cy="6" r="1.5" fill="url(#sourceGrad)" opacity="0.6" class="animate-pulse" style="animation-delay: 0.2s"/>
              <circle cx="18" cy="6" r="1.5" fill="url(#sourceGrad)" opacity="0.6" class="animate-pulse" style="animation-delay: 0.4s"/>
            </svg>
            
            <!-- Downloads Icon -->
            <svg v-else-if="link.path === '/downloads'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 svg-icon">
              <defs>
                <linearGradient id="downloadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #06b6d4" />
                  <stop offset="100%" style="stop-color: #0ea5e9" />
                </linearGradient>
              </defs>
              <line x1="12" y1="2" x2="12" y2="14" stroke="url(#downloadGrad)" stroke-width="2.5" stroke-linecap="round" class="animate-bounce"/>
              <polyline points="18,12 12,18 6,12" stroke="url(#downloadGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="animate-bounce" style="animation-delay: 0.1s"/>
              <rect x="2" y="20" width="20" height="2" fill="url(#downloadGrad)" rx="1" opacity="0.8"/>
            </svg>
            
            <!-- New Download Icon -->
            <svg v-else-if="link.path === '/new-download'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 svg-icon">
              <defs>
                <linearGradient id="newGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #10b981" />
                  <stop offset="100%" style="stop-color: #34d399" />
                </linearGradient>
              </defs>
              <!-- Central dot -->
              <circle cx="12" cy="12" r="2" fill="url(#newGrad)" class="animate-pulse"/>
              <!-- Pulsing rings -->
              <circle cx="12" cy="12" r="6" stroke="url(#newGrad)" stroke-width="1" fill="none" class="animate-ping" style="animation-duration: 1.5s"/>
              <circle cx="12" cy="12" r="4" stroke="url(#newGrad)" stroke-width="1" fill="none" opacity="0.6"/>
            </svg>
            
            {{ link.label }}
                  </router-link>
                </div>
              </div>

              <div class="hidden sm:flex items-center gap-2 flex-shrink-0">
                <div :class="['w-2 h-2 md:w-3 md:h-3 rounded-full transition-all', isConnected ? 'bg-green-500 shadow-lg shadow-green-500/50 animate-pulse' : 'bg-red-500 shadow-lg shadow-red-500/50 animate-pulse']" />
                <span class="text-xs text-gray-400">{{ isConnected ? 'Online' : 'Offline' }}</span>
              </div>
            </div>
          </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto p-4 md:p-6">
      <div class="max-w-7xl mx-auto">
        <router-view v-slot="{ Component }">
          <keep-alive :include="['Sources']">
            <component :is="Component" :key="route.name === 'ItemDetails' ? route.fullPath : route.path" />
          </keep-alive>
        </router-view>
      </div>
    </main>

    <!-- Toast Notifications -->
    <FavoritesDrawer :open="favoritesStore.drawerOpen" :items="favoritesStore.items" @close="favoritesStore.closeDrawer" />
    <Toast />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useDownloadStore } from './stores/download'
import { useFavoritesStore } from './stores/favorites'
import Toast from './components/Toast.vue'
import HamburgerButton from './components/HamburgerButton.vue'
import FavoritesDrawer from './components/FavoritesDrawer.vue'

const route = useRoute()
const downloadStore = useDownloadStore()
const favoritesStore = useFavoritesStore()

const navLinks = [
  { path: '/', label: 'Dashboard' },
  { path: '/library', label: 'Biblioteca' },
  { path: '/sources', label: 'Fontes' },
  { path: '/downloads', label: 'Histórico' },
  { path: '/new-download', label: 'Download' }
]

const isConnected = computed(() => downloadStore.isConnected)

function isActiveLink(path) {
  return route.path === path || (path === '/' && route.path === '')
}

onMounted(() => {
  downloadStore.fetchJobs()
  downloadStore.fetchSources()
  favoritesStore.fetchFavorites()
})

onUnmounted(() => {
  downloadStore.disconnectWebSocket()
})
</script>

<style scoped>
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
  background: #0891b2;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #06b6d4;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-bounce {
  animation: bounce 1s infinite;
}

.animate-spin {
  animation: spin 3s linear infinite;
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.svg-icon {
  filter: drop-shadow(0 0 2px rgba(6, 182, 212, 0.3));
}
</style>
