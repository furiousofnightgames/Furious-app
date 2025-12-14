<template>
  <button
    type="button"
    class="p-2 rounded-full bg-black/40 hover:bg-black/60 border border-gray-700 hover:border-cyan-500/40 transition"
    :title="favorited ? 'Remover dos favoritos' : 'Adicionar aos favoritos'"
    @click.stop="toggle"
  >
    <svg
      viewBox="0 0 24 24"
      class="w-5 h-5"
      :fill="favorited ? 'currentColor' : 'none'"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      :class="favorited ? 'text-amber-400' : 'text-gray-300'"
    >
      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
    </svg>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useFavoritesStore } from '../stores/favorites'

const props = defineProps({
  item: { type: Object, required: true }
})

const favoritesStore = useFavoritesStore()

const favorited = computed(() => {
  const sourceId = props.item?.source_id
  const itemId = props.item?.id
  if (sourceId == null || itemId == null) return false
  return favoritesStore.isFavorited(sourceId, itemId)
})

async function toggle() {
  await favoritesStore.toggleFavoriteFromItem(props.item)
}
</script>
