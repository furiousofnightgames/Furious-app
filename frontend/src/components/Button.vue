<template>
  <component
    :is="as"
    :class="[
      'px-4 py-2 rounded-lg font-semibold transition-all duration-300',
      'transform hover:scale-105 active:scale-95',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      variantClasses,
      sizeClasses,
      className
    ]"
    :disabled="disabled"
    @click="emit('click')"
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
    primary: 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/50 hover:shadow-cyan-500/80',
    secondary: 'bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-lg shadow-purple-500/50',
    danger: 'bg-gradient-to-r from-red-600 to-pink-600 text-white shadow-lg shadow-red-500/50',
    success: 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/50',
    outline: 'border-2 border-cyan-500 text-cyan-300 hover:bg-cyan-500/10',
    ghost: 'bg-cyan-500/20 backdrop-blur-md border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 hover:border-cyan-500/60 shadow-lg shadow-cyan-500/20'
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-5 py-2 text-base',
    xl: 'px-6 py-3 text-lg'
  }
  return sizes[props.size]
})
</script>
