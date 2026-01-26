<template>
  <transition name="modal-fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black/60 backdrop-blur-xl flex items-center justify-center z-[100]"
      @click="close"
      style="pointer-events: auto; position: fixed; top: 0; left: 0; right: 0; bottom: 0;"
    >
      <div
        :class="['bg-slate-950/95 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] p-10 w-full m-4 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.8)] z-[110] relative overflow-hidden transition-all duration-500', maxWidthClass]"
        @click.stop
        ref="dialog"
        style="max-height: 90vh; overflow-y: auto; pointer-events: auto;"
      >
        <!-- Background Accents -->
        <div class="absolute -top-24 -right-24 w-48 h-48 bg-cyan-500/5 blur-3xl rounded-full pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-purple-500/5 blur-3xl rounded-full pointer-events-none"></div>

        <div v-if="$slots.header || title" class="mb-8 relative z-20">
          <slot name="header">
            <h2 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 uppercase italic tracking-tighter drop-shadow-sm leading-none">
              {{ title }}
            </h2>
          </slot>
        </div>
        
        <div style="pointer-events: auto;" class="text-slate-300 relative z-10">
          <slot />
        </div>
        
        <div v-if="showDefaultButtons" class="flex gap-4 mt-10 relative z-10" style="pointer-events: auto;">
          <Button
            v-if="showCancel"
            variant="outline"
            class="flex-1 bg-white/5 border-white/10 text-white font-bold h-14 rounded-2xl hover:bg-white/10 transition-all"
            @click="close"
          >
            {{ cancelLabel }}
          </Button>
          <Button
            variant="primary"
            class="flex-1 bg-gradient-to-br from-cyan-600 to-blue-700 text-white font-bold h-14 rounded-2xl shadow-lg shadow-cyan-500/20 active:scale-95 transition-all"
            @click="confirm"
          >
            {{ confirmLabel }}
          </Button>
        </div>
        
        <div style="pointer-events: auto;" class="relative z-10">
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
    default: 'max-w-2xl'
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

