<template>
  <div class="flex items-center gap-2 p-4 rounded-xl" :class="bgColor">
    <div :class="iconColor">
      <slot name="icon" />
    </div>
    <div class="flex-1">
      <p class="text-sm font-semibold" :class="titleColor">{{ title }}</p>
      <p v-if="message" class="text-xs" :class="messageColor">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: v => ['success', 'error', 'warning', 'info'].includes(v)
  },
  title: String,
  message: String
})

const bgColor = computed(() => {
  const colors = {
    success: 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700/50',
    error: 'bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-700/50',
    warning: 'bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700/50',
    info: 'bg-sky-50 dark:bg-sky-900/20 border border-sky-200 dark:border-sky-700/50'
  }
  return colors[props.type]
})

const iconColor = computed(() => {
  const colors = {
    success: 'text-emerald-600 dark:text-emerald-400',
    error: 'text-rose-600 dark:text-rose-400',
    warning: 'text-amber-600 dark:text-amber-400',
    info: 'text-sky-600 dark:text-sky-400'
  }
  return colors[props.type]
})

const titleColor = computed(() => {
  const colors = {
    success: 'text-emerald-900 dark:text-emerald-200',
    error: 'text-rose-900 dark:text-rose-200',
    warning: 'text-amber-900 dark:text-amber-200',
    info: 'text-sky-900 dark:text-sky-200'
  }
  return colors[props.type]
})

const messageColor = computed(() => {
  const colors = {
    success: 'text-emerald-700 dark:text-emerald-300',
    error: 'text-rose-700 dark:text-rose-300',
    warning: 'text-amber-700 dark:text-amber-300',
    info: 'text-sky-700 dark:text-sky-300'
  }
  return colors[props.type]
})
</script>
