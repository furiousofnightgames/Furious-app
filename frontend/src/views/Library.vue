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

    <div v-if="!loading && filteredGroups.length > pageSize" class="flex flex-wrap items-center justify-center gap-2 pt-4 pb-8">
      <!-- Botão Anterior -->
      <button 
        @click="goPrevPage" 
        :disabled="page <= 1"
        class="px-3 py-2 rounded-lg border border-cyan-500/30 bg-gray-900/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Números das Páginas -->
      <template v-for="(p, index) in visiblePages" :key="index">
        <span v-if="p === '...'" class="px-2 text-gray-500">...</span>
        
        <button 
          v-else
          @click="libraryStore.setPage(p); scrollToItemsTop()"
          :class="[
            'min-w-[40px] h-10 px-3 rounded-lg font-semibold transition border',
            page === p 
              ? 'bg-cyan-500 text-white border-cyan-400 shadow-lg shadow-cyan-500/30' 
              : 'bg-gray-900/50 text-gray-400 border-gray-700 hover:text-cyan-300 hover:border-cyan-500/30'
          ]"
        >
          {{ p }}
        </button>
      </template>

      <!-- Botão Próxima -->
      <button 
        @click="goNextPage" 
        :disabled="page >= totalPages"
        class="px-3 py-2 rounded-lg border border-cyan-500/30 bg-gray-900/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
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

          <div class="p-3 bg-gray-900/40 border border-cyan-500/20 rounded space-y-2">
            <div class="flex items-center justify-between gap-3">
              <div class="text-sm font-bold text-cyan-300">Pré-flight Check</div>
              <div class="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  class="btn-translucent text-xs"
                  :disabled="preflightLoading"
                  @click="runPreflightForce"
                >
                  <span v-if="preflightLoading">Analisando...</span>
                  <span v-else>Forçar nova sondagem</span>
                </Button>
              </div>
            </div>

            <div v-if="preflightError" class="text-xs text-red-300 border border-red-500/30 bg-red-900/10 rounded p-2">
              {{ preflightError }}
            </div>

            <div v-else-if="preflightResult" class="text-xs text-gray-300 space-y-1">
              <div v-if="preflightAria2" class="text-gray-300">
                <span class="text-gray-400">aria2:</span>
                <span class="text-cyan-300 font-semibold"> {{ preflightAria2.available ? 'Disponível' : 'Indisponível' }} </span>
              </div>
              <div v-if="preflightHealth" class="text-gray-300">
                <span class="text-gray-400">Saúde:</span>
                <span class="text-cyan-300 font-semibold"> {{ preflightHealthLabel }} </span>
                <span v-if="preflightHealth.seeders !== null && preflightHealth.seeders !== undefined" class="ml-2 text-amber-200">Seeders {{ preflightHealth.seeders }}</span>
              </div>
              <div>
                <span class="text-gray-400">Range:</span>
                <span class="text-cyan-300 font-semibold"> {{ ((selectedItem?.url || '').startsWith('magnet:') || String(preflightResult.note || '').toLowerCase().includes('magnet')) ? 'N/A (Magnet/aria2)' : (preflightResult.accept_ranges ? 'Suportado' : 'Não suportado') }} </span>
              </div>
              <div v-if="preflightResult.size !== null && preflightResult.size !== undefined">
                <span class="text-gray-400">Tamanho:</span>
                <span class="text-cyan-300 font-semibold"> {{ formatBytes(preflightResult.size) }} </span>
              </div>
              <div v-if="preflightResult.status_code !== null && preflightResult.status_code !== undefined">
                <span class="text-gray-400">HTTP:</span>
                <span class="text-cyan-300 font-semibold"> {{ preflightResult.status_code }} </span>
              </div>
              <div v-if="preflightResult.note" class="text-gray-400">
                {{ preflightResult.note }}
              </div>
            </div>
            <div v-else class="text-xs text-gray-500">
              Opcional: analisa rapidamente a URL antes de iniciar.
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
import { storeToRefs } from 'pinia'
import api from '../services/api'
import { useDownloadStore } from '../stores/download'
import { useLibraryStore } from '../stores/library'
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
const libraryStore = useLibraryStore()
const { groups, stats, loading, error, page, searchQuery } = storeToRefs(libraryStore)
const router = useRouter()

const itemsTopRef = ref(null)

// groups, stats, loading, error managed by store

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
// searchQuery is in store

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

const preflightLoading = ref(false)
const preflightResult = ref(null)
const preflightError = ref(null)
const preflightAria2 = ref(null)
const preflightHealth = ref(null)
const preflightHealthLabel = computed(() => {
  const h = preflightHealth.value
  if (!h) return ''
  const s = Number(h.seeders ?? 0)
  if (Number.isFinite(s)) {
    if (s >= 20) return 'Saudável'
    if (s >= 5) return 'Ok'
    if (s >= 1) return 'Baixa'
    return 'Crítica'
  }
  return 'Desconhecida'
})
const manualFolderPath = ref('')
const browseLoading = ref(false)
const modalInfo = ref({ size: null, accept_range: false, eta: null, checking: false })

const pageSize = 21

// page and searchQuery are now in the store (mapped above)

async function fetchLibrary(refresh = false) {
  if (refresh || !libraryStore.isLoaded) {
    startLoadingProgress()
  } else {
    // Debug log to verify cache usage
    console.log('Library cache hit! Not reloading.')
  }
  
  await libraryStore.fetchLibrary(refresh)
  
  if (refresh) {
    libraryStore.setPage(1)
  }
  
  finishLoadingProgress()
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

const visiblePages = computed(() => {
  const current = page.value
  const total = totalPages.value
  const delta = 2 // Numbers to show on each side of current
  const range = []
  const rangeWithDots = []
  let l

  range.push(1)

  if (total <= 1) return [1]

  for (let i = current - delta; i <= current + delta; i++) {
    if (i < total && i > 1) {
      range.push(i)
    }
  }

  range.push(total)

  for (const i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1)
      } else if (i - l !== 1) {
        rangeWithDots.push('...')
      }
    }
    rangeWithDots.push(i)
    l = i
  }

  return rangeWithDots
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
  if (page.value > 1) {
    libraryStore.setPage(page.value - 1)
    scrollToItemsTop()
  }
}

function goNextPage() {
  if (page.value < totalPages.value) {
    libraryStore.setPage(page.value + 1)
    scrollToItemsTop()
  }
}

// Update store when search query changes (handled by v-model on input which should map to store)
// However, since we used storeToRefs, searchQuery is a ref.
// But to trigger side effects like page reset, we should watch it or use the action.
// Better: use a writable computed for the input.
// For now, let's watch the ref and ensure page is reset if it wasn't done by the setter.

watch(searchQuery, (newVal) => {
  // If we change search, we usually want to go to page 1.
  // The store action setSearchQuery does this, but v-model bypasses action.
  // So we watch here.
  if (page.value !== 1) {
    libraryStore.setPage(1)
  }
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
    const resp = await api.post('/api/analysis/pre-job/with-recommendations', { item })
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

  preflightError.value = null
  preflightResult.value = null
  preflightAria2.value = null
  preflightHealth.value = null

  const sourceId = item.source_id
  if (!(sourceId in downloadVerifySsl.value)) {
    Object.assign(downloadVerifySsl.value, { [sourceId]: true })
  }

  modalInfo.value = { size: null, accept_range: false, eta: null, checking: true }

  const urlRaw = (item.url || '').toString().trim()
  if (urlRaw.startsWith('magnet:')) {
    // Magnet: always run pre-flight with real probe, even if coming from pre-job flow.
    modalInfo.value.checking = false
    preflightLoading.value = true
    ;(async () => {
      try {
        const aria2Resp = await api.get('/api/aria2/status')
        preflightAria2.value = aria2Resp.data || null
      } catch (e) {
        preflightAria2.value = null
      }

      try {
        const healthResp = await api.post('/api/magnet/health', { url: urlRaw })
        preflightHealth.value = healthResp.data || null
      } catch (e) {
        preflightHealth.value = { seeders: item?.seeders ?? null, leechers: item?.leechers ?? null }
      }

      preflightResult.value = { accept_ranges: false, size: null, status_code: null, note: 'Magnet links use aria2' }
      preflightError.value = null
      preflightLoading.value = false
    })().catch(() => {
      preflightLoading.value = false
    })
  } else {
    // HTTP/HTTPS: keep existing behavior for size/range.
    try {
      const url = encodeURIComponent(urlRaw)
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
  }

  showDownloadDialog.value = true
}

async function runPreflightForce() {
  preflightError.value = null
  preflightResult.value = null
  preflightAria2.value = null
  preflightHealth.value = null

  const urlRaw = (selectedItem.value?.url || '').toString().trim()
  if (!urlRaw) {
    preflightError.value = 'URL inválida para análise.'
    return
  }

  preflightLoading.value = true
  try {
    if (urlRaw.startsWith('magnet:')) {
      const aria2Resp = await api.get('/api/aria2/status')
      preflightAria2.value = aria2Resp.data || null

      const healthResp = await api.post('/api/magnet/health', { url: urlRaw, force_refresh: true })
      console.log('[LIBRARY] Resposta force_refresh:', healthResp.data)
      preflightHealth.value = healthResp.data || null
      preflightResult.value = { accept_ranges: false, size: null, status_code: null, note: 'Magnet links use aria2' }
    } else {
      const resp = await api.get('/api/supports_range', { params: { url: urlRaw } })
      preflightResult.value = resp.data || null
    }
  } catch (e) {
    preflightError.value = e?.message || 'Falha ao analisar URL'
  } finally {
    preflightLoading.value = false
  }
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
      
      console.log('[Library] Job criado com sucesso, redirecionando para /downloads')
      await nextTick()
      router.push('/downloads')
    }
  } catch (e) {
    const msg = e.message || 'Erro ao criar job'
    try {
      const ts = useToastStore()
      ts.push('Erro', msg)
    } catch (ee) {}
  }
}

// Save scroll position before leaving -> REMOVED
// onBeforeRouteLeave -> REMOVED

onMounted(() => {
  console.log('[Library] Montado - carregando biblioteca')
  fetchLibrary(false)
})


</script>
