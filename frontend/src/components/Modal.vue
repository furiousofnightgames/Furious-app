<template>
  <transition name="fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-center justify-center z-40"
      @click="close"
      style="pointer-events: auto; position: fixed; top: 0; left: 0; right: 0; bottom: 0;"
    >
      <div
        :class="['bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/50 rounded-3xl p-8 w-full m-4 shadow-2xl z-50 relative', maxWidthClass]"
        @click.stop
        ref="dialog"
        style="max-height: 90vh; overflow-y: auto; pointer-events: auto;"
      >
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-4 font-display">{{ title }}</h2>
        <div style="pointer-events: auto;" class="text-slate-600 dark:text-slate-300">
          <slot />
        </div>
        <div v-if="showDefaultButtons" class="flex gap-3 mt-6" style="pointer-events: auto;">
          <Button
            v-if="showCancel"
            variant="outline"
            class="flex-1"
            @click="close"
          >
            {{ cancelLabel }}
          </Button>
          <Button
            variant="primary"
            class="flex-1"
            @click="confirm"
          >
            {{ confirmLabel }}
          </Button>
        </div>
        <div style="pointer-events: auto;">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Button from './Button.vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: true
  },
  maxWidthClass: {
    type: String,
    default: 'max-w-md'
  },
  title: String,
  showCancel: {
    type: Boolean,
    default: true
  },
   // don't render default footer buttons unless explicitly requested
   showDefaultButtons: {
     type: Boolean,
     default: false
   },
  cancelLabel: {
    type: String,
    default: 'Cancelar'
  },
  confirmLabel: {
    type: String,
    default: 'Confirmar'
  }
})

const emit = defineEmits(['close', 'confirm'])

const overlay = ref(null)
const dialog = ref(null)

const close = () => emit('close')
const confirm = () => emit('confirm')

function onEsc() {
  emit('close')
}

function trapFocus(e) {
  const focusable = dialog.value?.querySelectorAll('a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])') || []
  if (focusable.length === 0) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (e.key !== 'Tab') return
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
}

onMounted(() => {
  nextTick(() => {
    // focus the dialog for keyboard events
    try { dialog.value?.focus() } catch (e) {}
    window.addEventListener('keydown', trapFocus)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', trapFocus)
})
</script>

