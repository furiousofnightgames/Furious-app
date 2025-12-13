<template>
  <div class="fixed right-4 bottom-6 z-50 flex flex-col gap-2">
    <transition-group name="toast" tag="div">
      <div v-for="t in toasts" :key="t.id" class="bg-gray-900 border border-cyan-500/30 text-white px-4 py-2 rounded shadow-lg">
        <div class="font-semibold">{{ t.title }}</div>
        <div class="text-sm text-gray-300">{{ t.message }}</div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from '../stores/toast'

const store = useToastStore()
const toasts = computed(() => store.toasts)
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all .3s ease }
.toast-enter-from { opacity: 0; transform: translateY(8px) }
.toast-leave-to { opacity: 0; transform: translateY(8px) }
</style>
