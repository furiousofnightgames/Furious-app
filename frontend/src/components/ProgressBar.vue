<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">{{ label }}</span>
      <span class="text-xs text-slate-600 dark:text-slate-400">{{ percentage }}%</span>
    </div>
    <div class="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-sky-500 to-sky-600 transition-all duration-500 shadow-soft"
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
