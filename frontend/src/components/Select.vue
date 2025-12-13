<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-sm font-semibold text-cyan-300">{{ label }}</label>
    <select
      :class="[
        'px-4 py-2 rounded-lg',
        'bg-slate-900/80 border border-cyan-500/30',
        'text-white',
        'focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed'
      ]"
      :value="modelValue"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  label: String,
  placeholder: String,
  options: Array,
  disabled: Boolean
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2306b6d4' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2.5rem;
}
</style>
