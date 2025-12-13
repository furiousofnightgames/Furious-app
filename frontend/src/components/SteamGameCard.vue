<template>
  <div class="group relative bg-gray-900 border border-gray-700 hover:border-cyan-500 rounded-xl overflow-hidden shadow-lg h-full flex flex-col cursor-pointer" @click="goToDetails" style="will-change: border-color;">
    <!-- Image Area - Dimensões explícitas para compatibilidade PyQt5 -->
    <div class="relative overflow-hidden bg-gray-800 w-full" style="height: 180px; min-height: 180px; will-change: auto;">
      <img 
        v-if="displayImage" 
        :src="displayImage" 
        class="w-full h-full object-cover"
        @error="handleImageError"
        loading="lazy"
        style="will-change: auto;"
      />
      <!-- Placeholder Simples e Leve -->
      <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900 p-4">
        <!-- Ícone simples -->
        <svg viewBox="0 0 24 24" fill="none" class="w-12 h-12 mb-2 text-cyan-500 opacity-60" stroke="currentColor" stroke-width="1.5">
          <path d="M4 12a8 8 0 018-8v8H4z" fill="currentColor" opacity="0.3"/>
          <path d="M12 4a8 8 0 110 16 8 8 0 010-16z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        
        <!-- Texto simples -->
        <p class="text-xs text-gray-400 text-center line-clamp-2 mt-2">{{ item.name }}</p>
      </div>
      
      <!-- Loading Overlay -->
      <div v-if="loading" class="absolute inset-0 bg-black/30 flex items-center justify-center z-20">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400" style="animation: spin 1s linear infinite;"></div>
      </div>
      
      <!-- Overlay Gradient on Hover - Otimizado -->
      <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent opacity-0 group-hover:opacity-80" style="pointer-events: none;"></div>

      <!-- Quick Action Overlay - Otimizado -->
      <div class="absolute bottom-0 left-0 right-0 p-4 space-y-2 group-hover:block hidden" style="pointer-events: auto;">
         <button 
            @click.stop="goToDetails"
            class="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded font-bold shadow-lg shadow-purple-600/50 flex items-center justify-center gap-2"
        >
            <span>ℹ️</span> Ver Detalhes
        </button>
         <button 
            @click.stop="$emit('download', item)"
            class="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-bold shadow-lg shadow-cyan-600/50 flex items-center justify-center gap-2"
        >
            <span>⬇️</span> Baixar Agora
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4 flex-1 flex flex-col relative bg-gray-900">
        <!-- Title -->
        <h3 class="font-bold text-gray-100 mb-2 leading-tight line-clamp-3" :title="item.name">{{ item.name }}</h3>
        
        <!-- Metadata -->
        <div class="flex flex-wrap gap-2 text-xs text-gray-400 mb-3 mt-auto">
             <span class="bg-gray-800 px-1.5 py-0.5 rounded border border-gray-700">{{ formatBytes(item.size) }}</span>
             <span v-if="item.uploadDate" 
                class="px-1.5 py-0.5 rounded border"
                :class="isRecent ? 'bg-green-900/30 text-green-400 border-green-500/30 font-medium' : 'bg-gray-800 text-gray-400 border-gray-700'"
             >
                {{ formatRelativeDate(item.uploadDate) }}
             </span>
             <span v-if="item.category" class="bg-purple-900/30 text-purple-300 px-1.5 py-0.5 rounded border border-purple-500/30">{{ item.category }}</span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { formatBytes as fmtBytes, formatRelativeDate as fmtDate } from '../utils/format'
import api from '../services/api'

const router = useRouter()

// Utilitários de formatação re-exportados ou wrappers locais
const formatBytes = fmtBytes
const formatRelativeDate = fmtDate

const props = defineProps({
  item: { type: Object, required: true }
})

const emit = defineEmits(['download'])

const fetchedImage = ref(null)
const loading = ref(false)
const errorOccurred = ref(false)

// Cache de imagens em localStorage para persistência
const getImageCache = () => {
    try {
        const cache = localStorage.getItem('imageCache')
        return cache ? JSON.parse(cache) : {}
    } catch {
        return {}
    }
}

const setImageCache = (key, value) => {
    try {
        const cache = getImageCache()
        cache[key] = value
        localStorage.setItem('imageCache', JSON.stringify(cache))
    } catch {
        // Ignorar erros de localStorage
    }
}

const displayImage = computed(() => {
    if (errorOccurred.value) return null
    return fetchedImage.value || props.item.image || props.item.header_image || props.item.thumbnail
})

const handleImageError = () => {
    errorOccurred.value = true
    fetchedImage.value = null
}

const fetchImage = async () => {
    // Se já buscamos e deu erro, não tenta denovo
    if (errorOccurred.value) return

    // Se já tem imagem, não precisa buscar
    if (props.item.image || props.item.header_image || props.item.thumbnail) {
        return
    }

    // Verificar cache primeiro
    const cacheKey = `img_${props.item.name}`
    const imageCache = getImageCache()
    if (imageCache[cacheKey]) {
        fetchedImage.value = imageCache[cacheKey]
        return
    }

    loading.value = true
    try {
        // Busca resolver para obter imagem de alta qualidade
        const params = new URLSearchParams()
        params.append('game_name', props.item.name)
        
        const res = await api.post(`/api/resolver?${params.toString()}`)
        
        if (res.data && res.data.found) {
            // Armazena o appId para uso posterior (detalhes do jogo)
            if (res.data.appId) {
                props.item.appId = res.data.appId
            }
            
            // Prioridade: header > capsule > hero > grid
            const imageUrl = res.data.header || res.data.capsule || res.data.hero || res.data.grid
            if (imageUrl) {
                // Validar URL antes de usar
                if (imageUrl.startsWith('http')) {
                    fetchedImage.value = imageUrl
                    // Armazenar em cache
                    setImageCache(cacheKey, imageUrl)
                }
            }
        }
    } catch (e) {
        console.error(`[SteamGameCard] Erro ao carregar imagem para ${props.item.name}:`, e)
        errorOccurred.value = true
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchImage()
})

const isRecent = computed(() => {
    if (!props.item.uploadDate) return false
    const date = new Date(props.item.uploadDate)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) 
    return diffDays <= 30
})

// Se o item mudar (reciclagem de componente no v-for?), busca de novo
watch(() => props.item.name, (newName, oldName) => {
    if (newName !== oldName) {
        fetchedImage.value = null
        errorOccurred.value = false
        loading.value = false
        fetchImage()
    }
}, { immediate: false })

const goToDetails = () => {
    // Armazena o item no sessionStorage para recuperar na página de detalhes
    sessionStorage.setItem('itemDetails', JSON.stringify(props.item))
    router.push({
        name: 'ItemDetails',
        params: { id: props.item.id || props.item.name }
    })
}
</script>

<style scoped>
/* Otimizações de performance */
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Desabilitar transições pesadas durante scroll */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(6, 182, 212, 0.3);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(6, 182, 212, 0.5);
}

/* Otimizar renderização de imagens */
img {
    backface-visibility: hidden;
    -webkit-font-smoothing: antialiased;
}

/* Otimizar hover sem transições pesadas */
.group:hover {
    /* Sem transition-all pesado */
}
</style>
