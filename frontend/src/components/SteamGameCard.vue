<template>
  <div 
    ref="rootEl" 
    :class="[
      'group relative bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-2xl overflow-hidden shadow-[0_8px_32px_-12px_rgba(0,0,0,0.6)] transition-all duration-500 ease-out flex flex-col h-full',
      isLibrary ? '' : 'hover:-translate-y-2 hover:shadow-[0_24px_50px_-12px_rgba(0,0,0,0.7)] hover:border-cyan-500/40 hover:bg-slate-900',
      !isLibrary && props.enableNavigation ? 'cursor-pointer' : ''
    ]"
    @click="onCardClick"
  >
    <!-- Card Inner Glow Overlay -->
    <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

    <!-- Image Area - Fixed for PyQt5 -->
    <div class="relative overflow-hidden bg-slate-950/60 w-full h-auto aspect-[460/215] shrink-0">
      <div class="absolute inset-0 bg-slate-950/40"></div>

      <!-- Version Badge -->
      <div v-if="isLibrary && (versionsCount || 0) > 1" class="absolute top-3 left-3 z-30 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter bg-cyan-500/30 border border-cyan-400/50 text-cyan-200 shadow-[0_0_20px_-5px_#0ea5e9] backdrop-blur-md">
        {{ versionsCount }} Versões
      </div>
      
      <!-- Blurred Background Fill -->
      <img 
        v-if="displayImage" 
        :src="displayImage" 
        class="absolute inset-0 w-full h-full object-cover blur-2xl opacity-30 scale-110 pointer-events-none"
        aria-hidden="true"
      />

      <!-- Favorite Toggle -->
      <div class="absolute top-3 right-3 z-30">
        <FavoriteToggleButton v-if="showFavorite" :item="item" />
      </div>

      <!-- Main Game Image -->
      <img 
        v-if="displayImage" 
        :src="displayImage" 
        class="relative w-full h-full object-contain group-hover:scale-105 transition-transform duration-700 ease-out z-10"
        @error="handleImageError"
        @load="handleImageLoad"
        loading="lazy"
        draggable="false"
      />

      <!-- Premium Placeholder -->
      <div v-else class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
        <div class="relative">
          <div class="absolute inset-0 bg-cyan-400 blur-xl opacity-20 animate-pulse"></div>
          <svg viewBox="0 0 24 24" fill="none" class="relative w-12 h-12 text-cyan-500/40" stroke="currentColor" stroke-width="1.5">
            <path d="M4 12a8 8 0 018-8v8H4z" fill="currentColor" opacity="0.3"/>
            <path d="M12 4a8 8 0 110 16 8 8 0 010-16z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest text-center mt-4 line-clamp-1 opacity-50">{{ item.name }}</p>
      </div>
      
      <!-- Gradient Fade Over Image -->
      <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-90"></div>
      
      <!-- Loading Spinner -->
      <div v-if="loading" class="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-20">
        <div class="relative w-10 h-10">
          <div class="absolute inset-0 border-2 border-cyan-500/10 rounded-full"></div>
          <div class="absolute inset-0 border-2 border-cyan-400 rounded-full border-t-transparent animate-spin"></div>
        </div>
      </div>
      
      <!-- Quick Actions Overlay (Non-Library) -->
      <div v-if="effectiveShowQuickActions" class="absolute bottom-0 left-0 right-0 p-4 space-y-2 translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-out z-40 hidden md:block">
         <button 
            @click.stop="goToDetails"
            class="w-full py-2.5 bg-white/10 hover:bg-white/20 backdrop-blur-md text-white rounded-xl font-black text-[11px] uppercase tracking-wider border border-white/10 shadow-xl transition-all"
        >
            Ver Detalhes
        </button>
         <button 
            @click.stop="$emit('download', item)"
            class="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl font-black text-[11px] uppercase tracking-wider shadow-[0_8px_30px_-5px_rgba(6,182,212,0.5)] transition-all active:scale-95"
        >
            Baixar Agora
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="p-5 flex-1 flex flex-col relative bg-slate-900/50">
        <!-- Title -->
        <h3 class="font-black text-white mb-4 leading-tight line-clamp-2 text-base sm:text-[17px] tracking-tight group-hover:text-cyan-400 transition-colors" :title="item.name">
          {{ item.name }}
        </h3>
        
        <!-- Metadata Badges -->
        <div class="flex flex-wrap gap-2 text-[11px] font-mono font-bold mb-4 mt-auto">
             <span class="bg-white/10 px-2.5 py-1 rounded-md border border-white/10 text-slate-300 uppercase shadow-inner">
               {{ formatBytes(item.size) }}
             </span>
             <span v-if="item.uploadDate" 
                class="px-2.5 py-1 rounded-md border uppercase shadow-inner"
                :class="isRecent ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-white/10 text-slate-400 border-white/10'"
             >
                {{ formatRelativeDate(item.uploadDate) }}
             </span>
             <span v-if="item.category" class="bg-purple-500/20 text-purple-300 px-2.5 py-1 rounded-md border border-purple-500/40 uppercase shadow-inner">
               {{ translateGenre(item.category) }}
             </span>
             <span v-if="item.source" class="bg-amber-500/20 text-amber-300 px-2.5 py-1 rounded-md border border-amber-500/40 uppercase shadow-inner font-bold tracking-wider">
               {{ item.source }}
             </span>
        </div>

        <!-- Library Controls -->
        <div v-if="isLibrary" class="pt-4 border-t border-white/10 grid grid-cols-2 gap-3">
          <button
            type="button"
            class="px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-slate-300 font-black text-[10px] uppercase tracking-widest hover:bg-white/10 hover:text-white transition-all text-center shadow-lg"
            @click.prevent.stop="$emit('details', item)"
          >
            Detalhes
          </button>

          <button
            v-if="(versionsCount || 0) > 1"
            type="button"
            class="px-4 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-[0_0_20px_-5px_rgba(6,182,212,0.4)] hover:shadow-cyan-400/50 hover:scale-[1.03] active:scale-95 transition-all text-center"
            @click.prevent.stop="$emit('versions', item)"
          >
            Escolher
          </button>

          <button
            v-else
            type="button"
            class="px-4 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest bg-gradient-to-br from-emerald-400 to-teal-600 text-white shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)] hover:shadow-emerald-400/50 hover:scale-[1.03] active:scale-95 transition-all text-center"
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
import { formatBytes as fmtBytes, formatRelativeDate as fmtDate, translateGenre } from '../utils/format'
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

const emit = defineEmits(['download', 'details', 'versions', 'resolved'])

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
            
            // EMIT RESOLVED: Notify parent that we found something (helps enrichment queue)
            emit('resolved', res.data)

            // Prioridade: header > capsule > hero > grid
            const imageUrl = res.data.header || res.data.capsule || res.data.hero || res.data.grid
            if (imageUrl) {
                // Validar URL antes de usar
                if (isProbablyValidImageUrl(imageUrl)) {
                    fetchedImage.value = imageUrl
                    // ATUALIZA O ITEM ORIGINAL para que o Favorito possa usar esta imagem!
                    props.item.image = imageUrl 
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
                }, { root: null, rootMargin: '600px 0px', threshold: 0.01 }) // Aumentado para 600px para carregar antes do scroll
                io.observe(rootEl.value)
                
                // FORCE RETRY: Captura imagens que falharam no mount inicial devido ao estresse de renderização.
                setTimeout(() => {
                    if (!fetchedImage.value && isVisible.value) {
                         scheduleFetchImage()
                    }
                }, 3000)

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

/* Scrollbar Premium */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.01);
}

::-webkit-scrollbar-thumb {
    background: rgba(6, 182, 212, 0.2);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(6, 182, 212, 0.4);
}

/* Otimizar renderização de imagens */
img {
    backface-visibility: hidden;
    -webkit-font-smoothing: antialiased;
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
