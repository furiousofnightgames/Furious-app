<template>
  <div :class="['flex flex-col gap-2 justify-center', $attrs.class]">
    <label v-if="label" class="text-sm font-semibold text-slate-700 dark:text-slate-300">{{ label }}</label>
    <div class="relative w-full flex items-center">
      <!-- Search Icon (Optional) -->
      <div v-if="showSearch" class="absolute left-4 z-10 pointer-events-none text-slate-500/40">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <input
        v-bind="filteredAttrs"
        :class="[
          'px-4 py-2 rounded-lg w-full',
          'bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700',
          'text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500',
          'focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent',
          'transition-all duration-200',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          showSearch ? 'pl-11' : '',
          clearable && modelValue ? 'pr-11' : '',
          inputClass
        ]"
        :type="type"
        :placeholder="placeholder"
        :value="modelValue"
        :disabled="disabled"
        @input="$emit('update:modelValue', $event.target.value)"
      />

      <!-- Clear Button (SVG Static "Clean" Effect) -->
      <button 
        v-if="clearable && modelValue"
        type="button"
        @click="$emit('update:modelValue', '')"
        class="absolute right-3.5 p-1 rounded-md hover:bg-rose-500/10 text-slate-500 hover:text-rose-500 transition-all active:scale-90 z-20 group/clear"
        title="Limpar"
      >
        <svg class="w-4 h-4 group-hover/clear:rotate-90 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <span v-if="error" class="text-xs text-rose-600 dark:text-rose-400">{{ error }}</span>
  </div>
</template>

<script>
export default {
  inheritAttrs: false
}
</script>

<script setup>
import { computed, useAttrs } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text'
  },
  label: String,
  placeholder: String,
  error: String,
  disabled: Boolean,
  inputClass: String,
  clearable: Boolean,
  showSearch: Boolean
})

defineEmits(['update:modelValue'])

const attrs = useAttrs()
const filteredAttrs = computed(() => {
  const { class: _, ...rest } = attrs
  return rest
})
</script>
