<template>
  <div v-if="open" class="fixed inset-0 z-[10000]">
    <div class="absolute inset-0 bg-black/60" @click="$emit('close')" />

    <aside
      class="absolute left-0 top-0 h-full w-[420px] bg-gradient-to-b from-gray-950 via-gray-900 to-black border-r border-cyan-500/30 shadow-2xl shadow-cyan-500/10 flex flex-col"
      @click.stop
    >
      <div class="p-4 border-b border-cyan-500/20 flex items-center justify-between">
        <div class="flex items-center gap-2">
           <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-cyan-400">
             <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
           </svg>
           <h2 class="text-lg font-bold text-cyan-300">Favoritos</h2>
        </div>
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
        <div v-if="!items || items.length === 0" class="flex flex-col items-center justify-center py-10 text-gray-500 opacity-60">
           <svg viewBox="0 0 24 24" fill="none" class="w-12 h-12 mb-2 stroke-current" stroke-width="1.5">
             <path d="M12 5v14M5 12h14" />
           </svg>
           <span class="text-sm">Adicione jogos aos favoritos</span>
        </div>

        <div
          v-for="fav in items"
          :key="fav.id"
          class="relative group mb-2"
        >
          <button
            type="button"
            class="w-full flex items-center gap-3 p-2 rounded-lg bg-gray-900/40 hover:bg-gray-800/80 border border-gray-800 hover:border-cyan-500/30 transition-all duration-200 group-hover:pl-3"
            @click="openFavorite(fav)"
          >
            <!-- Avatar / Icon -->
            <div class="w-14 h-10 flex-shrink-0 bg-gray-800 rounded border border-gray-700 shadow-lg">
               <img 
                 v-if="getImageUrl(fav)" 
                 :src="getImageUrl(fav)" 
                 class="w-full h-full object-cover rounded" 
                 loading="lazy"
                 @error="e => e.target.style.display='none'"
               />
               <!-- Fallback Icon if no image -->
               <div class="absolute inset-0 flex items-center justify-center text-gray-600 bg-gray-800 -z-10">
                 <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
                    <path d="M21 6H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-10 7H8v3H6v-3H3v-2h3V8h2v3h3v2zm4.5 2c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm4-3c-.83 0-1.5-.67-1.5-1.5S18.67 9 19.5 9s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                 </svg>
               </div>
            </div>

            <div class="flex-1 min-w-0 pr-8">
               <div class="text-sm font-bold text-gray-200 group-hover:text-cyan-300 transition-colors truncate leading-tight">{{ cleanName(fav.name) }}</div>
               <div class="text-[10px] text-gray-500 truncate mt-0.5">Clique para detalhes</div>
            </div>
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
import { ref, watch } from 'vue'
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

// Mapa local de imagens resolvidas para favoritos
const resolvedImages = ref({})

function cleanName(name) {
  const normalized = favoritesStore.normalizeFavoriteName(name)
  if (!normalized) return String(name || '').trim()
  return normalized.length > 48 ? `${normalized.slice(0, 48)}...` : normalized
}

function getImageUrl(fav) {
  // Prioridade: imagem salva no DB > imagem resolvida localmente > null
  if (fav.image) return fav.image
  const key = `${fav.source_id}_${fav.item_id}`
  return resolvedImages.value[key] || null
}

async function resolveImageForFavorite(fav) {
  // Se já tem imagem ou já tentamos resolver, pular
  const key = `${fav.source_id}_${fav.item_id}`
  if (fav.image || resolvedImages.value[key]) return

  try {
    const params = new URLSearchParams()
    params.append('game_name', fav.name)
    const res = await api.post(`/api/resolver?${params.toString()}`)
    
    if (res.data && res.data.found) {
      const imageUrl = res.data.header || res.data.capsule || res.data.hero || res.data.grid
      if (imageUrl) {
        resolvedImages.value[key] = imageUrl
        // Atualizar no backend para persistir
        try {
          await api.post('/api/favorites', {
            source_id: fav.source_id,
            item_id: fav.item_id,
            name: fav.name,
            url: fav.url,
            image: imageUrl
          })
        } catch (e) {
          console.warn('[FavoritesDrawer] Falha ao atualizar imagem no backend:', e)
        }
      }
    }
  } catch (e) {
    console.warn('[FavoritesDrawer] Falha ao resolver imagem para:', fav.name, e)
  }
}

// Resolver imagens faltantes quando a gaveta abre
watch(() => props.open, async (isOpen) => {
  if (!isOpen || !props.items) return
  
  // Resolver imagens em lote (throttled)
  const missingImages = props.items.filter(f => !f.image && !resolvedImages.value[`${f.source_id}_${f.item_id}`])
  
  for (const fav of missingImages) {
    // Pequeno delay para não sobrecarregar a API
    await new Promise(resolve => setTimeout(resolve, 200))
    resolveImageForFavorite(fav)
  }
})


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
