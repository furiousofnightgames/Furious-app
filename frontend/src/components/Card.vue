<template>
  <div
    :class="[
      'bg-gradient-to-br from-slate-800/50 to-slate-900/50',
      'border border-cyan-500/30 rounded-xl p-6',
      'backdrop-blur-sm shadow-2xl',
      'hover:border-cyan-500/60 transition-all duration-300',
      'hover:shadow-lg hover:shadow-cyan-500/20',
      className,
      interactive ? 'cursor-pointer hover:scale-[1.02]' : ''
    ]"
  >
    <slot />
  </div>
</template>

<script setup>
defineProps({
  className: String,
  interactive: {
    type: Boolean,
    default: false
  }
})
</script>
