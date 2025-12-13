<template>
  <div class="flex items-center gap-2 p-3 rounded-lg" :class="bgColor">
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
    success: 'bg-green-500/20 border border-green-500/50',
    error: 'bg-red-500/20 border border-red-500/50',
    warning: 'bg-yellow-500/20 border border-yellow-500/50',
    info: 'bg-blue-500/20 border border-blue-500/50'
  }
  return colors[props.type]
})

const iconColor = computed(() => {
  const colors = {
    success: 'text-green-400',
    error: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  }
  return colors[props.type]
})

const titleColor = computed(() => {
  const colors = {
    success: 'text-green-300',
    error: 'text-red-300',
    warning: 'text-yellow-300',
    info: 'text-blue-300'
  }
  return colors[props.type]
})

const messageColor = computed(() => {
  const colors = {
    success: 'text-green-200',
    error: 'text-red-200',
    warning: 'text-yellow-200',
    info: 'text-blue-200'
  }
  return colors[props.type]
})
</script>
