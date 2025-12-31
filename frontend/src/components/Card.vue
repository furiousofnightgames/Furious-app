<template>
  <div
    :class="[
      'bg-white dark:bg-slate-800',
      'border border-slate-200 dark:border-slate-700/50',
      'rounded-2xl p-6',
      'shadow-subtle dark:shadow-soft',
      'hover:shadow-soft dark:hover:shadow-soft transition-all duration-200',
      'backdrop-blur-sm',
      className,
      interactive ? 'cursor-pointer hover:shadow-glow/20 hover:scale-[1.01]' : ''
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
