<template>
  <button
    type="button"
    @click="$emit('toggle')"
    class="p-2 rounded-lg text-cyan-300 hover:bg-cyan-500/10 hover:text-cyan-200 transition"
    aria-label="Abrir favoritos"
    title="Favoritos"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="w-6 h-6">
      <path d="M4 6h16" />
      <path d="M4 12h16" />
      <path d="M4 18h16" />
    </svg>
  </button>
</template>

<script setup>
defineEmits(['toggle'])
</script>
