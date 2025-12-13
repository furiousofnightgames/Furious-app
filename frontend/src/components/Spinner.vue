<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <div class="inline-block">
        <div class="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
      </div>
      <p class="mt-4 text-cyan-300 font-semibold">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Carregando...'
  }
})
</script>
