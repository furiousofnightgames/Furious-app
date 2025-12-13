import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  function push(title, message, timeout = 4000) {
    const id = Date.now() + Math.random()
    toasts.value.push({ id, title, message })
    setTimeout(() => {
      remove(id)
    }, timeout)
  }

  function remove(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  return { toasts, push, remove }
})
