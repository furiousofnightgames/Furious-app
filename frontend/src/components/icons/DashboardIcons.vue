<template>
  <!-- Speed Icon (Lightning Bolt) -->
  <svg v-if="type === 'speed'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="speedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #06b6d4; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #ec4899; stop-opacity: 1" />
      </linearGradient>
      <filter id="speedGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="url(#speedGrad)" filter="url(#speedGlow)" class="animate-pulse"/>
    <circle cx="12" cy="12" r="10" stroke="url(#speedGrad)" stroke-width="0.5" fill="none" class="animate-spin" style="animation-duration: 3s;"/>
  </svg>

  <!-- Progress Icon (Pie Chart) -->
  <svg v-else-if="type === 'progress'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="progressGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #8b5cf6; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #ec4899; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="9" stroke="#1f2937" stroke-width="2" fill="none"/>
    <path d="M12 3 A 9 9 0 0 1 20.196 20.196" stroke="url(#progressGrad)" stroke-width="2.5" fill="none" stroke-linecap="round" class="animate-pulse"/>
    <circle cx="12" cy="12" r="5" fill="url(#progressGrad)"/>
  </svg>

  <!-- Downloads Icon (Download arrows) -->
  <svg v-else-if="type === 'downloads'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="downloadsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #06b6d4; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #0ea5e9; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- First arrow -->
    <line x1="12" y1="2" x2="12" y2="14" stroke="url(#downloadsGrad)" stroke-width="2.5" stroke-linecap="round" class="animate-bounce" style="animation-delay: 0s;"/>
    <polyline points="18,12 12,18 6,12" stroke="url(#downloadsGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="animate-bounce" style="animation-delay: 0s;"/>
    
    <!-- Second arrow -->
    <line x1="12" y1="8" x2="12" y2="20" stroke="url(#downloadsGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.6" class="animate-bounce" style="animation-delay: 0.2s;"/>
    
    <!-- Base -->
    <rect x="2" y="20" width="20" height="2" fill="url(#downloadsGrad)" rx="1"/>
  </svg>

  <!-- Connection Icon (Network) -->
  <svg v-else-if="type === 'connection'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="connGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" :style="`stop-color: ${isConnected ? '#10b981' : '#ef4444'}; stop-opacity: 1`" />
        <stop offset="100%" :style="`stop-color: ${isConnected ? '#34d399' : '#f87171'}; stop-opacity: 1`" />
      </linearGradient>
    </defs>
    <!-- Circles with animation -->
    <circle cx="12" cy="12" r="2" fill="url(#connGrad)" class="animate-pulse"/>
    <circle cx="12" cy="12" r="6" stroke="url(#connGrad)" stroke-width="1" fill="none" class="animate-ping" style="animation-duration: 2s;"/>
    <circle cx="12" cy="12" r="10" stroke="url(#connGrad)" stroke-width="0.5" fill="none" opacity="0.4" class="animate-ping" style="animation-duration: 3s;"/>
  </svg>

  <!-- Active Downloads Icon (Circular progress) -->
  <svg v-else-if="type === 'active'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="activeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #06b6d4; stop-opacity: 1" />
        <stop offset="50%" style="stop-color: #8b5cf6; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #ec4899; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- Background circle -->
    <circle cx="12" cy="12" r="9" stroke="#1f2937" stroke-width="2" fill="none"/>
    <!-- Animated circle -->
    <circle cx="12" cy="12" r="9" stroke="url(#activeGrad)" stroke-width="2" fill="none" stroke-dasharray="56.5 56.5" class="animate-spin" style="animation-duration: 2s;"/>
    <!-- Center content -->
    <text x="12" y="15" text-anchor="middle" fill="url(#activeGrad)" font-size="8" font-weight="bold" class="animate-pulse">•••</text>
  </svg>

  <!-- Completed Icon (Checkmark) -->
  <svg v-else-if="type === 'completed'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="completeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #10b981; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #34d399; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- Background circle -->
    <circle cx="12" cy="12" r="10" fill="url(#completeGrad)" opacity="0.1" stroke="url(#completeGrad)" stroke-width="1"/>
    <!-- Checkmark -->
    <path d="M7 12.5L10 15.5L17 8" stroke="url(#completeGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse"/>
  </svg>

  <!-- Failed Icon (X) -->
  <svg v-else-if="type === 'failed'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="failGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #ef4444; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #f87171; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- Background circle -->
    <circle cx="12" cy="12" r="10" fill="url(#failGrad)" opacity="0.1" stroke="url(#failGrad)" stroke-width="1"/>
    <!-- X -->
    <line x1="8" y1="8" x2="16" y2="16" stroke="url(#failGrad)" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="16" y1="8" x2="8" y2="16" stroke="url(#failGrad)" stroke-width="2.5" stroke-linecap="round"/>
  </svg>

  <!-- Paused Icon (Bars) -->
  <svg v-else-if="type === 'paused'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="pauseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #f59e0b; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #fbbf24; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- First bar -->
    <rect x="6" y="4" width="3" height="16" fill="url(#pauseGrad)" rx="1.5" class="animate-pulse"/>
    <!-- Second bar -->
    <rect x="15" y="4" width="3" height="16" fill="url(#pauseGrad)" rx="1.5" class="animate-pulse" style="animation-delay: 0.3s;"/>
  </svg>

  <!-- Running Icon (Play) -->
  <svg v-else-if="type === 'running'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="runGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #10b981; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #06b6d4; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- Background circle -->
    <circle cx="12" cy="12" r="10" fill="none" stroke="url(#runGrad)" stroke-width="1"/>
    <!-- Play triangle -->
    <path d="M9 7L9 17L17 12Z" fill="url(#runGrad)" class="animate-pulse"/>
  </svg>

  <!-- Folder Icon (Custom name) -->
  <svg v-else-if="type === 'folder'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="folderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #fbbf24; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #f59e0b; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- Folder -->
    <path d="M3 6H10L12 4H21C22.1 4 23 4.9 23 6V18C23 19.1 22.1 20 21 20H3C1.9 20 1 19.1 1 18V8C1 6.9 1.9 6 3 6Z" 
          fill="url(#folderGrad)" opacity="0.2" stroke="url(#folderGrad)" stroke-width="1.5"/>
  </svg>

  <!-- File Icon (Default download) -->
  <svg v-else-if="type === 'file'" class="w-full h-full" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="fileGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #3b82f6; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #06b6d4; stop-opacity: 1" />
      </linearGradient>
    </defs>
    <!-- File -->
    <path d="M4 2H14L20 8V22C20 23.1 19.1 24 18 24H4C2.9 24 2 23.1 2 22V4C2 2.9 2.9 2 4 2Z" 
          fill="url(#fileGrad)" opacity="0.2" stroke="url(#fileGrad)" stroke-width="1.5"/>
    <!-- Lines -->
    <line x1="7" y1="12" x2="17" y2="12" stroke="url(#fileGrad)" stroke-width="1"/>
    <line x1="7" y1="16" x2="17" y2="16" stroke="url(#fileGrad)" stroke-width="1"/>
  </svg>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => [
      'speed', 'progress', 'downloads', 'connection', 'active',
      'completed', 'failed', 'paused', 'running', 'folder', 'file'
    ].includes(value)
  },
  isConnected: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-bounce {
  animation: bounce 1s infinite;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}
</style>
