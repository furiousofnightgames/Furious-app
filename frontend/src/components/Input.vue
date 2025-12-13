<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-sm font-semibold text-cyan-300">{{ label }}</label>
    <input
      :class="[
        'px-4 py-2 rounded-lg',
        'bg-slate-900/80 border border-cyan-500/30',
        'text-white placeholder-slate-400',
        'focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed'
      ]"
      :type="type"
      :placeholder="placeholder"
      :value="modelValue"
      :disabled="disabled"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="text-xs text-red-400">{{ error }}</span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text'
  },
  label: String,
  placeholder: String,
  error: String,
  disabled: Boolean
})

defineEmits(['update:modelValue'])
</script>
