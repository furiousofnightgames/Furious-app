<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-sm font-semibold text-slate-700 dark:text-slate-300">{{ label }}</label>
    <input
      :class="[
        'px-4 py-2 rounded-lg',
        'bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700',
        'text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500',
        'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed'
      ]"
      :type="type"
      :placeholder="placeholder"
      :value="modelValue"
      :disabled="disabled"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="text-xs text-rose-600 dark:text-rose-400">{{ error }}</span>
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
