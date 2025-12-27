<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div class="min-w-0">
        <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-400">Biblioteca</h1>
        <div class="text-xs text-gray-500 mt-1" v-if="formattedBuiltAt">
          Atualizado em <span class="text-gray-300">{{ formattedBuiltAt }}</span>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <router-link to="/sources">
          <Button variant="outline" class="btn-translucent">Fontes</Button>
        </router-link>
        <Button variant="outline" class="btn-translucent" :disabled="loading" @click="clearImageCache">
          Limpar cache
        </Button>
        <Input v-model="searchQuery" placeholder="Buscar na biblioteca..." class="w-72 bg-gray-900/70 border-cyan-500/30 focus:border-cyan-500/70" />
        <Button variant="outline" class="btn-translucent" :disabled="loading" @click="refreshLibrary">
          <span v-if="loading">⏳</span>
          <span v-else>Atualizar</span>
        </Button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="p-4 bg-gradient-to-br from-amber-900/25 to-orange-900/10 rounded-lg border border-amber-500/20 hover:border-amber-500/40 transition">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-amber-300" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 19V6a2 2 0 012-2h12a2 2 0 012 2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M6 18h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="min-w-0">
            <div class="text-xs text-amber-200/80">Fontes</div>
            <div class="text-2xl font-bold text-amber-300">{{ stats.total_sources }}</div>
          </div>
        </div>
      </div>

      <div class="p-4 bg-gradient-to-br from-cyan-900/25 to-blue-900/10 rounded-lg border border-cyan-500/20 hover:border-cyan-500/40 transition">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-cyan-300" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="min-w-0">
            <div class="text-xs text-cyan-200/80">Itens indexados</div>
            <div class="text-2xl font-bold text-cyan-300">{{ stats.total_items }}</div>
          </div>
        </div>
      </div>

      <div class="p-4 bg-gradient-to-br from-purple-900/25 to-pink-900/10 rounded-lg border border-purple-500/20 hover:border-purple-500/40 transition">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-purple-300" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 7h12M8 12h12M8 17h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M4 7h.01M4 12h.01M4 17h.01" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="min-w-0">
            <div class="text-xs text-purple-200/80">Jogos/entradas</div>
            <div class="text-2xl font-bold text-purple-300">{{ filteredGroups.length }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="p-3 border border-red-500/30 bg-red-900/10 rounded text-red-300 text-sm">
      {{ error }}
    </div>

    <div v-if="loading" class="space-y-4">
      <div class="p-5 rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-900/15 via-gray-900/40 to-gray-900/10">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-cyan-300 animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2a10 10 0 1010 10" stroke="currentColor" stroke-width="3" stroke-linecap="round" opacity="0.9"/>
            </svg>
          </div>

          <div class="min-w-0 flex-1">
            <div class="text-sm font-semibold text-cyan-200">Carregando itens das fontes…</div>
            <div class="text-xs text-gray-400 mt-1">
              Isso pode levar alguns segundos na primeira vez (baixando e agrupando as listas).
            </div>

            <div class="mt-3 h-2 rounded-full bg-gray-900/70 border border-gray-700 overflow-hidden relative">
              <div
                class="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 transition-[width] duration-200"
                :style="{ width: `${loadingProgress}%` }"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="n in 6" :key="n" class="h-full">
          <div class="h-full rounded-xl border border-gray-700 bg-gray-900/60 overflow-hidden">
            <div class="h-40 bg-gradient-to-r from-gray-800/80 via-gray-700/60 to-gray-800/80 animate-pulse" />
            <div class="p-4 space-y-3">
              <div class="h-4 w-3/4 rounded bg-gray-800/80 animate-pulse" />
              <div class="h-3 w-1/2 rounded bg-gray-800/70 animate-pulse" />
              <div class="flex gap-2 pt-2">
                <div class="h-7 w-20 rounded-lg bg-gray-800/80 animate-pulse" />
                <div class="h-7 w-24 rounded-lg bg-gray-800/70 animate-pulse" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else>
      <div ref="itemsTopRef" />
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="group in paginatedGroups" :key="group.key + ':' + cacheBust" class="h-full">
        <SteamGameCard
          :item="toCardItem(group)"
          variant="library"
          :versionsCount="getVersionsCount(group)"
          :showFavorite="getVersionsCount(group) <= 1"
          :autoResolveImage="true"
          @details="() => openItemDetails(group)"
          @versions="() => openVersions(group)"
          @download="(item) => onDownloadClick(group, item)"
        />
      </div>
      </div>
    </div>

    <div v-if="!loading && filteredGroups.length > pageSize" class="flex items-center justify-center gap-3 pt-2">
      <Button variant="outline" class="btn-translucent" :disabled="page <= 1" @click="goPrevPage">Anterior</Button>
      <div class="text-sm text-gray-400">
        Página <span class="text-cyan-300 font-semibold">{{ page }}</span>
        de <span class="text-cyan-300 font-semibold">{{ totalPages }}</span>
      </div>
      <Button variant="outline" class="btn-translucent" :disabled="page >= totalPages" @click="goNextPage">Próxima</Button>
    </div>

    <Modal v-if="showVersionsModal" @close="closeVersions" :showDefaultButtons="false" title="Versões disponíveis" maxWidthClass="max-w-[calc(28rem+50px)]">
      <div v-if="activeGroup" class="space-y-4">
        <div class="p-4 rounded-xl border border-cyan-500/15 bg-gradient-to-br from-gray-900/50 to-gray-900/20">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="text-lg font-bold text-gray-100 truncate">{{ activeGroup.name }}</div>
              <div class="text-xs text-gray-400 mt-1">{{ activeGroup.versions_count }} opções</div>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <Button variant="outline" class="btn-translucent" @click="closeVersions">Fechar</Button>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <div
            v-for="(v, idx) in activeGroup.versions"
            :key="idx"
            class="w-full p-4 rounded-xl border border-gray-700 bg-gray-900/60 hover:bg-gray-900/80 hover:border-cyan-500/40 transition"
          >
            <div class="flex items-start justify-between gap-4">
              <button class="flex-1 text-left min-w-0" @click.prevent.stop="selectVersion(v)">
                <div class="text-sm text-gray-100 font-semibold leading-5">
                  {{ v.name }}
                </div>

                <div class="flex items-center justify-between gap-2 mt-2 whitespace-nowrap">
                  <div class="flex items-center gap-2 min-w-0">
                    <span class="px-2 py-1 rounded-full text-[11px] font-semibold bg-cyan-500/10 border border-cyan-500/20 text-cyan-200 whitespace-nowrap">
                      {{ v.source_title || ('Fonte #' + v.source_id) }}
                    </span>

                    <span v-if="v.uploadDate" class="px-2 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-200">
                      {{ formatRelativeCompact(v.uploadDate) }}
                    </span>
                  </div>

                  <span class="px-2 py-1 rounded-full text-[11px] font-semibold bg-gray-800/70 border border-gray-700 text-gray-200 flex-shrink-0">
                    {{ formatBytes(v.size) }}
                  </span>
                </div>

                <div class="flex items-center gap-2 mt-2 whitespace-nowrap">
                  <span v-if="v.seeders !== undefined && v.seeders !== null" class="px-2 py-1 rounded-full text-[11px] font-semibold bg-amber-500/10 border border-amber-500/20 text-amber-200">
                    S {{ v.seeders }}
                  </span>
                  <span v-if="v.leechers !== undefined && v.leechers !== null" class="px-2 py-1 rounded-full text-[11px] font-semibold bg-purple-500/10 border border-purple-500/20 text-purple-200">
                    P {{ v.leechers }}
                  </span>
                </div>
              </button>

              <div class="flex items-center gap-2 flex-shrink-0">
                <FavoriteToggleButton :item="v" />
                <Button variant="success" @click.prevent.stop="selectVersion(v)">Baixar</Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="showDownloadDialog" @close="showDownloadDialog = false">
      <div>
        <h3 class="text-lg font-bold text-cyan-400 mb-4">⬇️ Baixar Item</h3>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-400">Item:</p>
            <p class="text-cyan-300 font-semibold">{{ selectedItem?.name }}</p>
          </div>

          <div>
            <p class="text-sm text-gray-400">Tamanho:</p>
            <p class="text-cyan-300">
              <span v-if="modalInfo.checking">Verificando...</span>
              <span v-else-if="modalInfo.size">{{ formatBytes(modalInfo.size) }} <span class="text-xs text-gray-400">(ETA ~{{ modalInfo.eta }}s)</span></span>
              <span v-else>{{ formatBytes(selectedItem?.size) }}</span>
            </p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-300 mb-2">Pasta</label>
            <div class="flex gap-2">
              <div class="flex-1 p-3 bg-gray-900 border border-cyan-500/30 rounded">
                <p class="text-sm text-cyan-300 truncate">{{ downloadDestination || 'downloads' }}</p>
              </div>
              <button
                type="button"
                @click.stop="browsePath"
                class="border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 btn-translucent"
              >
                <span v-if="browseLoading">⏳</span>
                <span v-else>...</span>
              </button>
            </div>
          </div>

          <div class="flex gap-2 pt-4 border-t border-gray-700">
            <button
              type="button"
              @click.prevent.stop="showDownloadDialog = false"
              class="flex-1 border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 btn-translucent"
            >
              Cancelar
            </button>
            <button
              type="button"
              @click.prevent.stop="confirmDownload"
              :class="[
                'flex-1 px-4 py-2 rounded-lg font-semibold transform hover:scale-105 active:scale-95 transition-all duration-300',
                downloadStore.loading ? 'opacity-60 cursor-not-allowed bg-gray-700 text-gray-200' : 'bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600 text-white shadow-lg shadow-green-500/50 hover:shadow-green-500/80'
              ]"
              :disabled="downloadStore.loading"
            >
              <span v-if="downloadStore.loading">Aguarde...</span>
              <span v-else>Baixar Agora</span>
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="showManualFolderModal" @close="showManualFolderModal = false" title="Escolher pasta manualmente" :showDefaultButtons="false">
      <div style="pointer-events: auto;">
        <label class="block text-sm font-semibold text-gray-300 mb-2">Caminho da pasta</label>
        <Input v-model="manualFolderPath" placeholder="C:\\Users\\seu usuario\\Downloads" />
        <div class="flex gap-2 pt-4" style="pointer-events: auto;">
          <Button variant="outline" class="flex-1 btn-translucent" @click="showManualFolderModal = false">Cancelar</Button>
          <Button variant="success" class="flex-1" @click="() => { downloadDestination.value = manualFolderPath.value || downloadDestination.value; showManualFolderModal = false }">Usar esta pasta</Button>
        </div>
      </div>
    </Modal>

    <SourceAnalysisModal
      :open="showAnalysisModal"
      :original-item="analysisOriginalItem"
      :candidates="analysisCandidates"
      :original-health="analysisOriginalItem?.health"
      :is-loading="analysisLoading"
      @close="showAnalysisModal = false"
      @confirm="onAnalysisConfirm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useDownloadStore } from '../stores/download'
import Card from '../components/Card.vue'
import SteamGameCard from '../components/SteamGameCard.vue'
import Modal from '../components/Modal.vue'
import Button from '../components/Button.vue'
import Input from '../components/Input.vue'
import FavoriteToggleButton from '../components/FavoriteToggleButton.vue'
import SourceAnalysisModal from '../components/SourceAnalysisModal.vue'
import { formatBytes, formatRelativeDate } from '../utils/format'
import { useToastStore } from '../stores/toast'

const downloadStore = useDownloadStore()
const router = useRouter()

const itemsTopRef = ref(null)

const groups = ref([])
const stats = ref({ total_sources: 0, total_items: 0, built_at: null })
const loading = ref(false)
const error = ref('')

const cacheBust = ref(0)

const loadingProgress = ref(0)
let loadingProgressTimer = null

function startLoadingProgress() {
  try {
    if (loadingProgressTimer) {
      clearInterval(loadingProgressTimer)
      loadingProgressTimer = null
    }
    loadingProgress.value = 0
    loadingProgressTimer = setInterval(() => {
      // Ramp up quickly at first, then slow down; never reach 100% until finished.
      const p = loadingProgress.value
      const cap = 90
      if (p >= cap) return
      const step = p < 30 ? 6 : (p < 60 ? 3 : 1)
      loadingProgress.value = Math.min(cap, p + step)
    }, 180)
  } catch (e) {}
}

function finishLoadingProgress() {
  try {
    if (loadingProgressTimer) {
      clearInterval(loadingProgressTimer)
      loadingProgressTimer = null
    }
    loadingProgress.value = 100
    setTimeout(() => {
      loadingProgress.value = 0
    }, 350)
  } catch (e) {}
}

function formatRelativeCompact(dateStr) {
  if (!dateStr) return ''
  try {
    const dt = new Date(dateStr)
    const t = dt.getTime()
    if (isNaN(t)) {
      // fallback to original formatter if it's not an ISO date
      return formatRelativeDate(dateStr) || String(dateStr)
    }
    const now = Date.now()
    const diffSec = Math.max(0, Math.floor((now - t) / 1000))

    const minute = 60
    const hour = 60 * minute
    const day = 24 * hour
    const week = 7 * day
    const month = 30 * day
    const year = 365 * day

    if (diffSec < minute) return `há ${diffSec}s`
    if (diffSec < hour) return `há ${Math.floor(diffSec / minute)}m`
    if (diffSec < day) return `há ${Math.floor(diffSec / hour)}h`
    if (diffSec < week) return `há ${Math.floor(diffSec / day)}d`
    if (diffSec < month) return `há ${Math.floor(diffSec / week)}sem`
    if (diffSec < year) {
      const n = Math.floor(diffSec / month)
      return `há ${n} ${n === 1 ? 'mês' : 'meses'}`
    }
    const y = Math.floor(diffSec / year)
    return `há ${y} ${y === 1 ? 'ano' : 'anos'}`
  } catch (e) {
    return formatRelativeDate(dateStr) || String(dateStr)
  }
}

const formattedBuiltAt = computed(() => {
  const v = stats.value?.built_at
  if (!v) return ''
  try {
    const dt = new Date(v)
    if (!isNaN(dt.getTime())) {
      return dt.toLocaleString()
    }
  } catch (e) {}
  return String(v)
})
const searchQuery = ref('')

const showVersionsModal = ref(false)
const activeGroup = ref(null)

const showAnalysisModal = ref(false)
const analysisCandidates = ref([])
const analysisOriginalItem = ref(null)
const analysisLoading = ref(false)
const analysisPendingItem = ref(null)

const showDownloadDialog = ref(false)
const selectedItem = ref(null)
const downloadDestination = ref('downloads')
const downloadVerifySsl = ref({})
const showManualFolderModal = ref(false)
const manualFolderPath = ref('')
const browseLoading = ref(false)
const modalInfo = ref({ size: null, accept_range: false, eta: null, checking: false })

const pageSize = 21
const page = ref(1)

async function fetchLibrary(refresh = false) {
  try {
    loading.value = true
    startLoadingProgress()
    error.value = ''
    const resp = await api.get('/api/library' + (refresh ? '?refresh=true' : ''))
    const data = resp.data || {}
    groups.value = data.groups || []
    page.value = 1
    stats.value = {
      total_sources: data.total_sources || 0,
      total_items: data.total_items || 0,
      built_at: data.built_at || null
    }
  } catch (e) {
    error.value = e.message || 'Erro ao carregar biblioteca'
  } finally {
    loading.value = false
    finishLoadingProgress()
  }
}

function refreshLibrary() {
  return fetchLibrary(true)
}

function clearImageCache() {
  try {
    localStorage.removeItem('imageCache')
  } catch (e) {
    // ignore
  }
  cacheBust.value = (cacheBust.value || 0) + 1
  try {
    const ts = useToastStore()
    ts.push('Cache limpo', 'Cache de imagens removido. Recarregando capas...')
  } catch (e) {}
}

const filteredGroups = computed(() => {
  const q = (searchQuery.value || '').trim().toLowerCase()
  if (!q) return groups.value
  return groups.value.filter(g => (g.name || '').toLowerCase().includes(q))
})

const totalPages = computed(() => {
  const total = filteredGroups.value.length
  return Math.max(1, Math.ceil(total / pageSize))
})

const paginatedGroups = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredGroups.value.slice(start, start + pageSize)
})

function scrollToItemsTop() {
  try {
    nextTick(() => {
      const el = itemsTopRef.value
      if (el && typeof el.scrollIntoView === 'function') {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        return
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })
  } catch (e) {}
}

function goPrevPage() {
  page.value = Math.max(1, page.value - 1)
  scrollToItemsTop()
}

function goNextPage() {
  page.value = Math.min(totalPages.value, page.value + 1)
  scrollToItemsTop()
}

watch(searchQuery, () => {
  page.value = 1
  scrollToItemsTop()
})

function toCardItem(group) {
  const best = group?.best || {}
  return {
    ...best,
    name: group?.name || best?.name || 'Item',
    size: best?.size,
    category: best?.category,
    uploadDate: best?.uploadDate,
    // Provide the same image fields Sources cards rely on.
    // SteamGameCard prefers: image -> header_image -> thumbnail, and caches by item.name.
    image: best?.image || best?.header_image || best?.thumbnail,
    header_image: best?.header_image || best?.image || best?.thumbnail,
    thumbnail: best?.thumbnail || best?.image || best?.header_image,
    icon: best?.icon,
    // Preserve any detected Steam appId so SteamGameCard can use the cheap header.jpg fallback.
    appId: best?.appId || best?.appid || best?.steam_appid
  }
}

function getVersionsCount(group) {
  const vc = group?.versions_count
  if (typeof vc === 'number' && !Number.isNaN(vc)) return vc
  const asNum = Number(vc)
  if (!Number.isNaN(asNum) && isFinite(asNum)) return asNum
  const v = group?.versions
  return Array.isArray(v) ? v.length : 0
}

function openVersions(group) {
  activeGroup.value = group
  showVersionsModal.value = true
}

function openItemDetails(group) {
  const item = toCardItem(group)
  try {
    sessionStorage.setItem('itemDetails', JSON.stringify(item))
  } catch (e) {
    // ignore
  }
  router.push({ name: 'ItemDetails', params: { id: item.id || item.name } })
}

function closeVersions() {
  showVersionsModal.value = false
  activeGroup.value = null
}

function selectVersion(v) {
  closeVersions()
  startDownloadFlow(v)
}

function onDownloadClick(group, emittedItem) {
  if (!group) return
  const vc = getVersionsCount(group)
  if (vc > 1) {
    openVersions(group)
    return
  }

  const item = emittedItem || group.best
  startDownloadFlow(item)
}

async function startDownloadFlow(item) {
  if (!item) return

  analysisPendingItem.value = item
  analysisOriginalItem.value = item
  analysisCandidates.value = []
  analysisLoading.value = true
  showAnalysisModal.value = true

  try {
    const resp = await api.post('/api/analysis/pre-job', { item })
    if (resp.data && resp.data.candidates && resp.data.candidates.length > 0) {
      analysisCandidates.value = resp.data.candidates

      const enrichedOriginal = { ...item }
      if (resp.data.original_health) {
        enrichedOriginal.health = resp.data.original_health
        if (resp.data.original_health.seeders !== undefined) {
          enrichedOriginal.seeders = resp.data.original_health.seeders
          enrichedOriginal.leechers = resp.data.original_health.leechers
        }
      }
      analysisOriginalItem.value = enrichedOriginal
      analysisLoading.value = false
      return
    }
  } catch (e) {
    // fallback to direct download
  }

  showAnalysisModal.value = false
  analysisLoading.value = false
  openDownloadConfigurationDialog(item)
}

function onAnalysisConfirm(selectedItem) {
  const item = selectedItem || analysisPendingItem.value
  showAnalysisModal.value = false
  analysisLoading.value = false
  analysisPendingItem.value = null
  openDownloadConfigurationDialog(item)
}

function openDownloadConfigurationDialog(item) {
  if (!item) return

  selectedItem.value = item
  downloadDestination.value = 'downloads'

  const sourceId = item.source_id
  if (sourceId !== undefined && sourceId !== null && !(sourceId in downloadVerifySsl.value)) {
    Object.assign(downloadVerifySsl.value, { [sourceId]: true })
  }

  modalInfo.value = { size: null, accept_range: false, eta: null, checking: true }

  try {
    const url = encodeURIComponent(item.url)
    api.get(`/api/supports_range?url=${url}`).then(({ data }) => {
      modalInfo.value.size = data.size || null
      modalInfo.value.accept_range = !!data.accept_ranges
      if (data.size && modalInfo.value.accept_range) {
        const baseline = 1024 * 1024
        modalInfo.value.eta = Math.round((data.size / baseline))
      }
    }).catch(() => {}).finally(() => {
      modalInfo.value.checking = false
    })
  } catch (e) {
    modalInfo.value.checking = false
  }

  showDownloadDialog.value = true
}

async function browsePath() {
  browseLoading.value = true
  try {
    if (window.electronAPI?.selectFolder) {
      const folder = await window.electronAPI.selectFolder()
      if (folder) downloadDestination.value = folder
      browseLoading.value = false
      return
    }
    const resp = await api.post('/api/dialog/select_folder')
    if (resp.data && resp.data.path) {
      downloadDestination.value = resp.data.path
      return
    }
    manualFolderPath.value = downloadDestination.value || ''
    showManualFolderModal.value = true
  } catch (e) {
    manualFolderPath.value = downloadDestination.value || ''
    showManualFolderModal.value = true
  } finally {
    browseLoading.value = false
  }
}

async function confirmDownload() {
  if (!selectedItem.value) return

  try {
    let destCandidate = (downloadDestination.value || 'downloads').toString()
    const destLower = destCandidate.toLowerCase()
    const suspicious = destLower.startsWith('http') || destLower.startsWith('magnet:') || destCandidate.includes('%25') || destCandidate.includes('announce')
    if (suspicious) destCandidate = 'downloads'

    const sourceId = selectedItem.value.source_id
    const verifySsl = (downloadVerifySsl.value[sourceId] !== false) ?? true

    const jobData = {
      url: selectedItem.value.url,
      name: selectedItem.value.name,
      destination: destCandidate,
      verify_ssl: verifySsl,
      size: selectedItem.value.size || null
    }

    const result = await downloadStore.createJob(jobData)
    if (result && result.job_id) {
      showDownloadDialog.value = false
      selectedItem.value = null
      try {
        const ts = useToastStore()
        ts.push('Download', `Download #${result.job_id} iniciado`)
      } catch (e) {}
    }
  } catch (e) {
    const msg = e.message || 'Erro ao criar job'
    try {
      const ts = useToastStore()
      ts.push('Erro', msg)
    } catch (ee) {}
  }
}

onMounted(() => {
  fetchLibrary(false)
})
</script>
