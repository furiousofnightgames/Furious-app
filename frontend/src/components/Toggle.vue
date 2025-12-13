<template>
  <div class="flex items-center gap-3">
    <button
      type="button"
      @click="emit('update:modelValue', !modelValue)"
      :class="[
        'relative w-12 h-6 rounded-full transition-all duration-300',
        'focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-900',
        modelValue 
          ? 'bg-gradient-to-r from-green-500 to-green-600 shadow-lg shadow-green-500/50' 
          : 'bg-gradient-to-r from-red-500 to-red-600 shadow-lg shadow-red-500/50'
      ]"
      role="switch"
      :aria-checked="modelValue"
    >
      <div 
        :class="[
          'absolute top-0.5 left-0.5 w-5 h-5 rounded-full transition-all duration-300',
          'bg-white shadow-md flex items-center justify-center',
          modelValue ? 'translate-x-6' : 'translate-x-0'
        ]"
      >
        <svg v-if="modelValue" class="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        <svg v-else class="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    </button>
    <label class="text-sm font-semibold transition-colors cursor-pointer" :class="modelValue ? 'text-green-300' : 'text-red-400'">
      <slot />
    </label>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])
</script>
