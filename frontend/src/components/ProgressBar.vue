<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-semibold text-cyan-300">{{ label }}</span>
      <span class="text-xs text-cyan-400">{{ percentage }}%</span>
    </div>
    <div class="w-full h-2 rounded-full bg-slate-800 border border-cyan-500/30 overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all duration-500 shadow-lg shadow-cyan-500/50"
        :style="{ width: percentage + '%' }"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  percentage: {
    type: Number,
    default: 0,
    validator: v => v >= 0 && v <= 100
  },
  label: String
})
</script>
