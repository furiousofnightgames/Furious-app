<template>
  <div ref="rootEl" :class="rootClass" @click="onCardClick" style="will-change: border-color;">
    <!-- Image Area - Dimensões explícitas para compatibilidade PyQt5 -->
    <div class="relative overflow-hidden bg-gray-800 w-full" style="height: 180px; min-height: 180px; will-change: auto;">
      <div v-if="isLibrary && (versionsCount || 0) > 1" class="absolute top-3 left-3 z-30 px-2.5 py-1 rounded-full text-[11px] font-bold bg-gray-950/80 border border-cyan-300/70 text-cyan-100 shadow-lg shadow-black/40 backdrop-blur-md">
        {{ versionsCount }} versões
      </div>
      <div class="absolute top-2 right-2 z-30">
        <FavoriteToggleButton v-if="showFavorite" :item="item" />
      </div>
      <img 
        v-if="displayImage" 
        :src="displayImage" 
        class="w-full h-full object-contain object-center"
        @error="handleImageError"
        @load="handleImageLoad"
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
      
      <div v-if="effectiveShowHoverOverlay" class="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent opacity-0 group-hover:opacity-80" style="pointer-events: none;"></div>

      <div v-if="effectiveShowQuickActions" class="absolute bottom-0 left-0 right-0 p-4 space-y-2 group-hover:block hidden" style="pointer-events: auto;">
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

        <div v-if="isLibrary" class="pt-3 mt-1 border-t border-gray-800/80 grid grid-cols-2 gap-2">
          <button
            type="button"
            class="px-4 py-2 rounded-lg border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 btn-translucent"
            @click.prevent.stop="$emit('details', item)"
          >
            Detalhes
          </button>

          <button
            v-if="(versionsCount || 0) > 1"
            type="button"
            class="px-4 py-2 rounded-lg font-semibold bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transform hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 flex items-center justify-center"
            @click.prevent.stop="$emit('versions', item)"
          >
            Escolher versão
          </button>

          <button
            v-else
            type="button"
            class="px-4 py-2 rounded-lg font-semibold bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600 text-white shadow-lg shadow-green-500/20 hover:shadow-green-500/40 transform hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 flex items-center justify-center"
            @click.prevent.stop="$emit('download', item)"
          >
            Baixar
          </button>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { formatBytes as fmtBytes, formatRelativeDate as fmtDate } from '../utils/format'
import api from '../services/api'
import FavoriteToggleButton from './FavoriteToggleButton.vue'

const __resolverThrottle = (() => {
    const maxConcurrent = 4
    const minIntervalMs = 175
    let active = 0
    let lastStart = 0
    const queue = []

    const pump = () => {
        if (active >= maxConcurrent) return
        if (queue.length === 0) return
        const now = Date.now()
        const wait = Math.max(0, minIntervalMs - (now - lastStart))
        if (wait > 0) {
            setTimeout(pump, wait)
            return
        }
        const task = queue.shift()
        active += 1
        lastStart = Date.now()
        task()
    }

    const run = (fn) => new Promise((resolve, reject) => {
        const task = async () => {
            try {
                const res = await fn()
                resolve(res)
            } catch (e) {
                reject(e)
            } finally {
                active = Math.max(0, active - 1)
                pump()
            }
        }
        queue.push(task)
        pump()
    })

    return { run }
})()

const router = useRouter()

// Utilitários de formatação re-exportados ou wrappers locais
const formatBytes = fmtBytes
const formatRelativeDate = fmtDate

const props = defineProps({
  item: { type: Object, required: true },
  showFavorite: { type: Boolean, default: true },
  autoResolveImage: { type: Boolean, default: true },
  enableNavigation: { type: Boolean, default: true },
  showQuickActions: { type: Boolean, default: true },
  showHoverOverlay: { type: Boolean, default: true },
  variant: { type: String, default: 'default' },
  versionsCount: { type: Number, default: 1 }
})

const emit = defineEmits(['download', 'details', 'versions'])

const rootEl = ref(null)
const isVisible = ref(false)
const fetchDebounceTimer = ref(null)
let io = null

const badImageUrls = new Set()

const fetchedImage = ref(null)
const loading = ref(false)
const imageErrorCount = ref(0)
const fetchAttemptCount = ref(0)
const triedAppIdHeaderImage = ref(false)

const isLibrary = computed(() => props.variant === 'library')

const effectiveShowQuickActions = computed(() => {
    if (isLibrary.value) return false
    return props.showQuickActions
})

const effectiveShowHoverOverlay = computed(() => {
    if (isLibrary.value) return false
    return props.showHoverOverlay
})

const rootClass = computed(() => {
    const base = 'group relative bg-gray-900 border border-gray-700 rounded-xl overflow-hidden shadow-lg h-full flex flex-col'
    const hover = (!isLibrary.value && (props.showHoverOverlay || props.showQuickActions)) ? ' hover:border-cyan-500' : ''
    const cursor = (!isLibrary.value && props.enableNavigation) ? ' cursor-pointer' : ''
    return base + hover + cursor
})

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

const getApiBaseUrl = () => {
    return api.defaults.baseURL || 'http://127.0.0.1:8001'
}

const getCacheKey = () => {
    const appId = props.item?.appId || props.item?.appid || props.item?.steam_appid
    if (appId) return `img_v2_app_${appId}`
    return `img_v2_${props.item.name}`
}

const normalizeImageUrl = (url) => {
    if (!url || typeof url !== 'string') return null
    const s = url.trim()
    if (!s) return null
    if (s.startsWith('//')) return `https:${s}`
    return s
}

const maybeMarkBadAndRetry = (url) => {
    try {
        const key = (url || '').trim()
        if (key) badImageUrls.add(key)

        const cacheKey = getCacheKey()
        const cache = getImageCache()
        if (cache && cache[cacheKey]) {
            delete cache[cacheKey]
            localStorage.setItem('imageCache', JSON.stringify(cache))
        }
    } catch {
        // ignore
    }

    fetchedImage.value = null
    imageErrorCount.value = (imageErrorCount.value || 0) + 1
    if (!loading.value && imageErrorCount.value < 2) {
        scheduleFetchImage()
    }
}

const isProbablyVideoUrl = (url) => {
    if (!url || typeof url !== 'string') return false
    const s = (normalizeImageUrl(url) || '').toLowerCase()
    if (!s) return false
    const noQuery = s.split('?')[0]
    return noQuery.endsWith('.webm') || noQuery.endsWith('.mp4') || noQuery.endsWith('.mkv') || noQuery.endsWith('.avi') || noQuery.endsWith('.mov')
}

const isProbablyValidImageUrl = (url) => {
    if (!url || typeof url !== 'string') return false
    const s = normalizeImageUrl(url)
    if (!s) return false
    if (isProbablyVideoUrl(s)) return false
    if (s.startsWith('http://') || s.startsWith('https://')) return true
    if (s.startsWith('data:image/')) return true
    if (s.startsWith('/') || s.startsWith('./') || s.startsWith('../')) return true
    return false
}

const toProxiedImageUrl = (url) => {
    if (!url || typeof url !== 'string') return null
    const s = normalizeImageUrl(url)
    if (!s) return null

    if (s.includes('/api/proxy/image?url=')) {
        return s
    }

    if (s.startsWith('http://') || s.startsWith('https://')) {
        const baseUrl = getApiBaseUrl()
        return `${baseUrl}/api/proxy/image?url=${encodeURIComponent(s)}`
    }

    return s
}

const displayImage = computed(() => {
    if (imageErrorCount.value >= 2) return null
    const raw = fetchedImage.value || props.item.image || props.item.header_image || props.item.thumbnail
    if (!isProbablyValidImageUrl(raw)) return null
    return toProxiedImageUrl(raw)
})

const handleImageError = () => {
    fetchedImage.value = null
    imageErrorCount.value = (imageErrorCount.value || 0) + 1
    try {
        const cacheKey = getCacheKey()
        const cache = getImageCache()
        if (cache && cache[cacheKey]) {
            delete cache[cacheKey]
            localStorage.setItem('imageCache', JSON.stringify(cache))
        }
    } catch {
        // Ignorar erros de localStorage
    }
    if (!loading.value && imageErrorCount.value < 2) {
        fetchImage()
    }
}

const handleImageLoad = async (ev) => {
    try {
        if (!ev || !ev.target) return
        const img = ev.target
        const src = (img.currentSrc || img.src || '').trim()
        if (!src) return

        // Only analyze same-origin proxied images to avoid CORS canvas taint.
        if (!src.includes('/api/proxy/image?url=')) return

        // SteamGridDB covers can be legitimately very dark.
        // Our heuristic is meant to catch Steam placeholders/invalid art, so skip it for SGDB.
        try {
            const urlParam = src.split('/api/proxy/image?url=')[1] || ''
            const decoded = decodeURIComponent(urlParam)
            if ((decoded || '').includes('steamgriddb.com')) {
                return
            }
        } catch (e) {}

        const w = img.naturalWidth || 0
        const h = img.naturalHeight || 0
        if (w <= 2 || h <= 2) {
            maybeMarkBadAndRetry(src)
            return
        }

        const sampleW = 32
        const sampleH = 32
        const canvas = document.createElement('canvas')
        canvas.width = sampleW
        canvas.height = sampleH
        const ctx = canvas.getContext('2d', { willReadFrequently: true })
        if (!ctx) return

        ctx.drawImage(img, 0, 0, sampleW, sampleH)
        const data = ctx.getImageData(0, 0, sampleW, sampleH).data
        let dark = 0
        let sum = 0
        let opaque = 0
        const px = sampleW * sampleH
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i]
            const g = data[i + 1]
            const b = data[i + 2]
            const a = data[i + 3]
            if (a < 32) continue
            opaque += 1
            const v = (r + g + b) / 3
            sum += v
            if (v <= 10) dark += 1
        }
        if (opaque < Math.max(16, Math.floor(px * 0.1))) return

        const avg = sum / opaque
        const darkRatio = dark / opaque

        // Heuristic: almost entirely black and very low average brightness.
        if (darkRatio >= 0.96 && avg <= 12) {
            if (!badImageUrls.has(src)) {
                maybeMarkBadAndRetry(src)
            }
        }
    } catch (e) {
        // ignore
    }
}

const fetchImage = async () => {
    if (fetchAttemptCount.value >= 2) return
    if (isLibrary.value && !isVisible.value) return

    // Se já tem imagem, não precisa buscar
    const existing = props.item.image || props.item.header_image || props.item.thumbnail
    if (imageErrorCount.value === 0 && isProbablyValidImageUrl(existing)) {
        return
    }

    // Verificar cache primeiro
    const cacheKey = getCacheKey()
    const imageCache = getImageCache()
    if (imageCache[cacheKey]) {
        const cachedUrl = imageCache[cacheKey]
        if (imageErrorCount.value === 0 && isProbablyValidImageUrl(cachedUrl) && !badImageUrls.has(cachedUrl)) {
            fetchedImage.value = cachedUrl
            return
        }
        try {
            delete imageCache[cacheKey]
            localStorage.setItem('imageCache', JSON.stringify(imageCache))
        } catch {
            // Ignorar erros de localStorage
        }
    }

    if (!props.autoResolveImage) {
        return
    }

    loading.value = true
    try {
        fetchAttemptCount.value = (fetchAttemptCount.value || 0) + 1
        // Busca resolver para obter imagem de alta qualidade
        const params = new URLSearchParams()
        params.append('game_name', props.item.name)

        const res = await __resolverThrottle.run(() => api.post(`/api/resolver?${params.toString()}`))
        
        if (res.data && res.data.found) {
            // Armazena o appId para uso posterior (detalhes do jogo)
            if (res.data.appId) {
                props.item.appId = res.data.appId
            }
            
            // Prioridade: header > capsule > hero > grid
            const imageUrl = res.data.header || res.data.capsule || res.data.hero || res.data.grid
            if (imageUrl) {
                // Validar URL antes de usar
                if (isProbablyValidImageUrl(imageUrl)) {
                    fetchedImage.value = imageUrl
                    // Armazenar em cache
                    setImageCache(cacheKey, imageUrl)
                    return
                }
            }
        }

        // Fallback leve: se o resolver não retornou nenhuma URL válida, tentar header.jpg via appId.
        // Mantém performance e evita "ficar sem imagem" quando só existe appId.
        const appId = props.item?.appId || props.item?.appid || props.item?.steam_appid
        if (!triedAppIdHeaderImage.value && appId) {
            triedAppIdHeaderImage.value = true
            const url = `https://cdn.akamai.steamstatic.com/steam/apps/${appId}/header.jpg`
            if (!badImageUrls.has(url)) {
                fetchedImage.value = url
                return
            }
        }
    } catch (e) {
        console.error(`[SteamGameCard] Erro ao carregar imagem para ${props.item.name}:`, e)
        imageErrorCount.value = (imageErrorCount.value || 0) + 1
    } finally {
        loading.value = false
    }
}

const scheduleFetchImage = () => {
    if (fetchDebounceTimer.value) {
        clearTimeout(fetchDebounceTimer.value)
        fetchDebounceTimer.value = null
    }
    fetchDebounceTimer.value = setTimeout(() => {
        fetchDebounceTimer.value = null
        fetchImage()
    }, isLibrary.value ? 250 : 0)
}

onMounted(() => {
    if (isLibrary.value) {
        try {
            if ('IntersectionObserver' in window && rootEl.value) {
                io = new IntersectionObserver((entries) => {
                    const ent = entries && entries[0]
                    const vis = !!(ent && ent.isIntersecting)
                    if (vis !== isVisible.value) {
                        isVisible.value = vis
                    }
                    if (vis) {
                        scheduleFetchImage()
                    }
                }, { root: null, rootMargin: '200px 0px', threshold: 0.01 })
                io.observe(rootEl.value)
                return
            }
        } catch (e) {}
        isVisible.value = true
        scheduleFetchImage()
        return
    }
    scheduleFetchImage()
})

onBeforeUnmount(() => {
    try {
        if (io) io.disconnect()
    } catch (e) {}
    io = null
    if (fetchDebounceTimer.value) {
        clearTimeout(fetchDebounceTimer.value)
        fetchDebounceTimer.value = null
    }
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
        imageErrorCount.value = 0
        fetchAttemptCount.value = 0
        loading.value = false
        scheduleFetchImage()
    }
}, { immediate: false })

const goToDetails = () => {
    if (!props.enableNavigation) return
    // Armazena o item no sessionStorage para recuperar na página de detalhes
    sessionStorage.setItem('itemDetails', JSON.stringify(props.item))
    router.push({
        name: 'ItemDetails',
        params: { id: props.item.id || props.item.name }
    })
}

const onCardClick = () => {
    if (isLibrary.value) return
    if (!props.enableNavigation) return
    goToDetails()
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
