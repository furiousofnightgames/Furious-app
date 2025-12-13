<template>
  <div class="flex items-center justify-center">
    <div class="relative w-20 h-20">
      <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        <!-- Background circle -->
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="text-slate-800"
        />
        <!-- Progress circle -->
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="url(#gradient)"
          stroke-width="2"
          stroke-dasharray="282.7"
          :stroke-dashoffset="282.7 * (1 - percentage / 100)"
          class="transition-all duration-500"
          stroke-linecap="round"
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#06b6d4" />
            <stop offset="100%" stop-color="#2563eb" />
          </linearGradient>
        </defs>
      </svg>
      <div class="absolute inset-0 flex items-center justify-center">
        <span class="text-xl font-bold text-cyan-400">{{ percentage }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  percentage: {
    type: Number,
    default: 0
  }
})
</script>
