<template>
  <div v-if="isElectron" class="electron-titlebar select-none flex items-center justify-between px-4 bg-slate-950/95 border-b border-white/5 backdrop-blur-md" style="height: 32px; -webkit-app-region: drag;">
    <!-- Left: App Title (draggable) -->
    <div class="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
      <div class="w-3 h-3 flex-shrink-0">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="titleLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #0ea5e9; stop-opacity: 1" />
              <stop offset="100%" style="stop-color: #0284c7; stop-opacity: 1" />
            </linearGradient>
          </defs>
          <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="url(#titleLogoGrad)" opacity="0.8"/>
        </svg>
      </div>
      <span>Furious App</span>
    </div>

    <!-- Right: Window Controls (non-draggable) -->
    <div class="flex items-center gap-1" style="-webkit-app-region: no-drag;">
      <!-- Minimize Button -->
      <button 
        @click="minimizeWindow"
        class="window-control-btn hover:bg-white/10 active:bg-white/20"
        title="Minimizar"
      >
        <svg class="w-3 h-3" viewBox="0 0 12 12" fill="none">
          <rect x="2" y="5.5" width="8" height="1" fill="currentColor" rx="0.5"/>
        </svg>
      </button>

      <!-- Maximize/Restore Button -->
      <button 
        @click="toggleMaximize"
        class="window-control-btn hover:bg-white/10 active:bg-white/20"
        :title="isMaximized ? 'Restaurar' : 'Maximizar'"
      >
        <svg v-if="!isMaximized" class="w-3 h-3" viewBox="0 0 12 12" fill="none">
          <rect x="2" y="2" width="8" height="8" stroke="currentColor" stroke-width="1" fill="none" rx="0.5"/>
        </svg>
        <svg v-else class="w-3 h-3" viewBox="0 0 12 12" fill="none">
          <rect x="2.5" y="3.5" width="6" height="6" stroke="currentColor" stroke-width="1" fill="none" rx="0.5"/>
          <path d="M4 2.5 H9.5 V8" stroke="currentColor" stroke-width="1" fill="none"/>
        </svg>
      </button>

      <!-- Close Button -->
      <button 
        @click="closeWindow"
        class="window-control-btn hover:bg-rose-600 active:bg-rose-700"
        title="Fechar"
      >
        <svg class="w-3 h-3" viewBox="0 0 12 12" fill="none">
          <path d="M2 2L10 10M2 10L10 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isElectron = computed(() => !!window.electronAPI)
const isMaximized = ref(false)

const minimizeWindow = () => {
  if (window.electronAPI?.minimizeWindow) {
    window.electronAPI.minimizeWindow()
  }
}

const toggleMaximize = () => {
  if (window.electronAPI?.toggleMaximize) {
    window.electronAPI.toggleMaximize()
  }
}

const closeWindow = () => {
  if (window.electronAPI?.closeWindow) {
    window.electronAPI.closeWindow()
  }
}

// Listen for maximize state changes from Electron
const handleMaximizeChange = (event, maximized) => {
  isMaximized.value = maximized
}

onMounted(() => {
  if (window.electronAPI?.onMaximizeChange) {
    window.electronAPI.onMaximizeChange(handleMaximizeChange)
  }
  
  // Get initial maximize state
  if (window.electronAPI?.isMaximized) {
    window.electronAPI.isMaximized().then(maximized => {
      isMaximized.value = maximized
    })
  }
})

onUnmounted(() => {
  if (window.electronAPI?.removeMaximizeListener) {
    window.electronAPI.removeMaximizeListener(handleMaximizeChange)
  }
})
</script>

<style scoped>
.electron-titlebar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
}

.window-control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 32px;
  color: #94a3b8;
  transition: all 0.15s ease;
  border: none;
  background: transparent;
  cursor: pointer;
}

.window-control-btn:hover {
  color: white;
}

.window-control-btn:active {
  transform: scale(0.95);
}
</style>
