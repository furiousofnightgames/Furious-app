<template>
  <component
    :is="as"
    :class="[
      'font-semibold transition-all duration-200',
      'transform hover:scale-105 active:scale-95',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500',
      variantClasses,
      sizeClasses,
      className
    ]"
    :type="as === 'button' ? 'button' : undefined"
    :disabled="disabled"
    @click="emit('click', $event)"
    role="button"
    :aria-disabled="disabled ? 'true' : 'false'"
  >
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: v => ['primary', 'secondary', 'danger', 'success', 'outline', 'ghost'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg', 'xl'].includes(v)
  },
  disabled: Boolean,
  as: {
    type: String,
    default: 'button'
  },
  className: String
})

const emit = defineEmits(['click'])

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-sky-500 text-white hover:bg-sky-600 shadow-soft hover:shadow-glow',
    secondary: 'bg-violet-600 text-white hover:bg-violet-700 shadow-soft hover:shadow-glow-violet',
    danger: 'bg-rose-600 text-white hover:bg-rose-700 shadow-soft hover:shadow-glow-rose',
    success: 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-soft',
    outline: 'border-2 border-sky-300 dark:border-sky-500 text-sky-700 dark:text-sky-400 hover:bg-sky-50 dark:hover:bg-sky-950/30 hover:border-sky-500',
    ghost: 'text-slate-600 dark:text-slate-300 hover:text-sky-600 dark:hover:text-sky-400 hover:bg-sky-50 dark:hover:bg-sky-950/20'
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'px-3 py-1.5 text-xs rounded-md',
    md: 'px-4 py-2 text-sm rounded-lg',
    lg: 'px-5 py-2.5 text-base rounded-lg',
    xl: 'px-6 py-3 text-lg rounded-xl'
  }
  return sizes[props.size]
})
</script>
