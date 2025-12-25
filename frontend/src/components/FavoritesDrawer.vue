<template>
  <div v-if="open" class="fixed inset-0 z-50">
    <div class="absolute inset-0 bg-black/60" @click="$emit('close')" />

    <aside
      class="absolute left-0 top-0 h-full w-[320px] bg-gradient-to-b from-gray-950 via-gray-900 to-black border-r border-cyan-500/30 shadow-2xl shadow-cyan-500/10 flex flex-col"
      @click.stop
    >
      <div class="p-4 border-b border-cyan-500/20 flex items-center justify-between">
        <h2 class="text-lg font-bold text-cyan-300">Favoritos</h2>
        <button
          type="button"
          class="p-2 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition"
          @click="$emit('close')"
          aria-label="Fechar favoritos"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="w-5 h-5">
            <path d="M18 6L6 18" />
            <path d="M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-auto p-3">
        <div v-if="!items || items.length === 0" class="text-sm text-gray-400 p-2">
          Nenhum favorito ainda.
        </div>

        <div
          v-for="fav in items"
          :key="fav.id"
          class="relative"
        >
          <button
            type="button"
            class="w-full text-left p-3 pr-10 rounded-lg bg-gray-900/40 hover:bg-gray-800/60 border border-gray-800 hover:border-cyan-500/40 transition"
            @click="openFavorite(fav)"
          >
            <div class="text-sm font-semibold text-gray-100 truncate">{{ cleanName(fav.name) }}</div>
          </button>

          <button
            type="button"
            class="absolute top-2 right-2 p-1 rounded-md text-gray-400 hover:text-white hover:bg-gray-800/80 transition"
            aria-label="Remover favorito"
            title="Remover favorito"
            @click.stop="removeFavorite(fav)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="w-4 h-4">
              <path d="M18 6L6 18" />
              <path d="M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '../stores/favorites'
import { useDownloadStore } from '../stores/download'
import api from '../services/api'

const router = useRouter()
const favoritesStore = useFavoritesStore()
const downloadStore = useDownloadStore()

const props = defineProps({
  open: { type: Boolean, default: false },
  items: { type: Array, default: () => [] }
})

const emit = defineEmits(['close'])

function cleanName(name) {
  const normalized = favoritesStore.normalizeFavoriteName(name)
  if (!normalized) return String(name || '').trim()
  return normalized.length > 48 ? `${normalized.slice(0, 48)}...` : normalized
}

async function openFavorite(fav) {
  // Tentar encontrar o item completo na store de downloads para garantir que temos a URL e outros metadados
  const fullItem = downloadStore.items.find(i => i.source_id === fav.source_id && i.id === fav.item_id)
  
  let item
  
  if (fullItem) {
    // Clone para evitar mutação direta na store se algo mudar na visualização
    item = { ...fullItem }
    console.log('[FavoritesDrawer] Item completo encontrado na store:', item.name)
  } else {
    // Se não estiver na store (ex: outra fonte), buscar na API
    try {
      console.log('[FavoritesDrawer] Buscando detalhes na API para:', fav.name)
      const resp = await api.get(`/api/sources/${fav.source_id}/items/${fav.item_id}`)
      if (resp.data) {
        item = resp.data
        console.log('[FavoritesDrawer] Detalhes recuperados da API')
      }
    } catch (e) {
      console.warn('[FavoritesDrawer] Falha ao buscar na API:', e)
    }

    if (!item) {
      // Fallback: usar dados parciais do favorito
      console.warn('[FavoritesDrawer] Item não encontrado, usando dados parciais do favorito')
      const normalizedName = favoritesStore.normalizeFavoriteName(fav.name)
      item = {
        id: fav.item_id,
        name: normalizedName || String(fav.name || '').trim(),
        url: fav.url,
        source_id: fav.source_id
      }
    }
  }

  try {
    sessionStorage.setItem('itemDetails', JSON.stringify(item))
  } catch (e) {
    console.error('[FavoritesDrawer] Erro ao salvar item no sessionStorage:', e)
  }

  emit('close')

  router.push({
    name: 'ItemDetails',
    params: { id: fav.item_id },
    state: { item }
  })
}

async function removeFavorite(fav) {
  await favoritesStore.removeFavoriteByItem(fav.source_id, fav.item_id)
}
</script>
