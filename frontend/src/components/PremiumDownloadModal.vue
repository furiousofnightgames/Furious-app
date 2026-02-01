<template>
  <div v-if="isOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="close">
    <div 
      class="relative w-full max-w-2xl bg-[#0b1120] rounded-2xl border border-cyan-500/30 shadow-[0_0_50px_-12px_rgba(6,182,212,0.25)] overflow-hidden animate-in fade-in zoom-in-95 duration-300 max-h-[calc(100vh-2rem)] flex flex-col"
    >
      <!-- Header Premium -->
      <div class="relative bg-gradient-to-b from-slate-800/50 to-slate-900/50 p-6 pb-6 border-b border-white/5 flex-shrink-0">
        <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"></div>
        
        <div class="flex items-start gap-5">
          <!-- Ícone ou Capa -->
          <div class="relative group flex-shrink-0">
            <div class="absolute -inset-0.5 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl blur opacity-30 group-hover:opacity-60 transition duration-500"></div>
            <div class="relative w-16 h-16 bg-slate-800 rounded-xl flex items-center justify-center overflow-hidden border border-white/10 shadow-xl">
              <img v-if="imageUrl" :src="imageUrl" class="w-full h-full object-cover" alt="Cover" />
              <svg v-else class="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
          </div>

          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold text-white tracking-tight leading-snug line-clamp-2" :title="item?.name">
              {{ item?.name }}
            </h2>
            <div class="flex items-center gap-3 mt-2 text-sm">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                {{ modalInfo.checking ? 'Calculando...' : formatBytes(displaySize) }}
              </span>
              <span v-if="modalInfo.eta" class="text-slate-500 text-xs">
                ~{{ modalInfo.eta }}s est.
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto scrollbar-premium p-6 space-y-6">
        
        <!-- Seleção de Pasta -->
        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-wider pl-1">Destino</label>
          <div class="flex gap-2">
            <div class="flex-1 px-4 py-3 bg-slate-900/80 border border-slate-700/50 rounded-xl text-sm text-cyan-300 font-mono truncate shadow-inner flex items-center">
              {{ destination || 'downloads' }}
            </div>
            <button 
              @click="browse"
              class="px-4 bg-slate-800 hover:bg-slate-700 border border-slate-600/50 hover:border-cyan-500/30 rounded-xl text-white transition-all shadow-lg active:scale-95 flex items-center justify-center group"
              :disabled="browseLoading"
            >
              <svg v-if="!browseLoading" class="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              <svg v-else class="w-5 h-5 animate-spin text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </div>

        <!-- Informações de Disco (Card) -->
        <div 
          v-if="freeSpaceInfo"
          class="relative p-4 rounded-xl border backdrop-blur-md transition-all duration-500"
          :class="hasEnoughSpace ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-red-500/5 border-red-500/20'"
        >
          <div class="flex justify-between items-center mb-2">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full animate-pulse" :class="hasEnoughSpace ? 'bg-emerald-500' : 'bg-red-500'"></div>
              <span class="text-xs font-bold uppercase tracking-wide" :class="hasEnoughSpace ? 'text-emerald-400' : 'text-red-400'">
                {{ hasEnoughSpace ? 'Espaço Disponível' : 'Espaço Insuficiente' }}
              </span>
            </div>
            <span class="text-xs font-mono text-slate-400">Livre: {{ formatBytes(freeSpaceInfo.free) }}</span>
          </div>

          <!-- Barra de Progresso de Espaço -->
          <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mb-2">
            <div 
              class="h-full transition-all duration-700 ease-out"
              :class="hasEnoughSpace ? 'bg-gradient-to-r from-emerald-600 to-emerald-400' : 'bg-red-500'"
              :style="{ width: spaceBarPercent + '%' }"
            ></div>
          </div>

          <div class="flex justify-between items-start text-[10px] sm:text-xs">
            <div class="text-slate-400"> Necessário: <span :class="hasEnoughSpace ? 'text-slate-200' : 'text-red-400 font-bold'">{{ formatBytes(estimatedRequiredSpace) }}</span></div>
            <div class="text-[9px] text-slate-500 italic mt-0.5 text-right w-full block">
              *Estimativa sujeita a variações pós-instalação
            </div>
          </div>

          <!-- Avisos Especiais (Repack/Placeholder) -->
          <div v-if="isPlaceholderSize" class="mt-3 p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg flex gap-3 items-start animate-in fade-in slide-in-from-top-1">
            <svg class="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <div class="space-y-1">
              <p class="text-amber-200 text-xs font-bold">Tamanho Real Oculto</p>
              <p class="text-amber-200/70 text-[10px] leading-relaxed">
                Este item parece ser uma coleção grande. O tamanho exibido ({{ formatBytes(item?.size) }}) pode ser impreciso. O download será pausado se o disco encher.
              </p>
            </div>
          </div>
          <div v-else-if="isRepackDetected" class="mt-2 flex items-start gap-2 text-[10px] text-emerald-400/80">
            <svg class="w-3 h-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <p>Compactado detectado. Espaço extra calculado para instalação segura.</p>
          </div>
        </div>

        <!-- Pre-flight Check (Grid Moderno + Detalhes) -->
        <div class="bg-slate-900/50 border border-slate-700/50 rounded-xl overflow-hidden">
          <div class="px-4 py-3 bg-slate-800/50 border-b border-white/5 flex justify-between items-center">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Diagnóstico de Rede</span>
            <button 
              @click="refreshPreflight" 
              :disabled="preflightLoading"
              class="text-[10px] font-bold uppercase tracking-wide text-cyan-400 hover:text-white transition flex items-center gap-1.5 px-2 py-1 rounded hover:bg-cyan-500/20 disabled:opacity-50"
            >
              <svg :class="preflightLoading ? 'animate-spin' : ''" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              {{ preflightLoading ? 'Verificando...' : 'Recheck' }}
            </button>
          </div>

          <div class="p-4 grid grid-cols-2 gap-4 text-xs">
            <!-- Aria2 -->
            <div class="space-y-1">
              <span class="text-slate-500 font-semibold block text-[10px] uppercase">Motor Downloader</span>
              <div class="flex items-center gap-2">
                <div class="w-1.5 h-1.5 rounded-full" :class="preflightAria2?.available ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'"></div>
                <span class="text-slate-200 font-mono">{{ preflightAria2?.available ? 'Aria2 Online' : 'Indisponível' }}</span>
              </div>
            </div>

            <!-- Protocolo -->
            <div class="space-y-1">
              <span class="text-slate-500 font-semibold block text-[10px] uppercase">Protocolo</span>
              <span class="text-slate-200 font-mono">
                {{ isMagnet ? 'BitTorrent (P2P)' : (preflightResult?.status_code ? `HTTP ${preflightResult.status_code}` : 'Direct Link') }}
              </span>
            </div>

            <!-- Seeds/Peers Premium Dashboard -->
            <div class="col-span-2 bg-gradient-to-br from-slate-900 to-slate-950 rounded-xl border border-white/10 overflow-hidden relative group">
              <!-- Glow effect on hover -->
              <div class="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
              
              <div class="flex relative z-10">
                <!-- Seeds Section -->
                <div class="flex-1 p-3 border-r border-white/5">
                  <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                    Seeds
                  </div>
                  <div class="flex items-baseline gap-1.5 translate-y-0.5">
                    <span class="text-2xl font-bold tracking-tight" :class="healthColorClass">
                      {{ seedersDisplay }}
                    </span>
                    <span v-if="Number(seedersDisplay) > 0" class="text-[9px] font-bold text-emerald-500/80 bg-emerald-500/10 px-1.5 py-0.5 rounded uppercase">
                      Ativos
                    </span>
                  </div>
                </div>

                <!-- Peers Section -->
                <div class="flex-1 p-3 bg-white/[0.01]">
                  <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <div class="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
                    Peers
                  </div>
                  <div class="flex items-baseline gap-1.5 translate-y-0.5">
                    <span class="text-2xl font-bold text-slate-300 tracking-tight">
                      {{ leechersDisplay }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Health Bar Bottom -->
              <div class="h-1 w-full bg-slate-800/50">
                 <div class="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] transition-all duration-1000 ease-out" 
                      :style="{ width: healthPercent + '%' }"
                      :class="Number(seedersDisplay) < 5 ? 'bg-red-500 shadow-red-500/50' : 'bg-emerald-500'"></div>
              </div>
            </div>
            
            <div class="col-span-2 text-center text-[9px] text-slate-600 font-medium tracking-wide -mt-2">
              *Valores globais do swarm; conexões ativas dependerão da sua rede.
            </div>

            <!-- Info Extra / Erro -->
            <div v-if="preflightError" class="col-span-2 text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2 text-[10px]">
              {{ preflightError }}
            </div>
            <div v-else-if="!isMagnet || (preflightResult?.note && !preflightResult.note.includes('Magnet links use aria2'))" class="col-span-2 text-[10px] text-slate-500 italic flex justify-between">
               <span>{{ preflightResult?.note || 'Verificação pronta.' }}</span>
               <span v-if="!isMagnet && preflightResult" class="font-mono">Range: {{ preflightResult?.accept_ranges ? 'YES' : 'NO' }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer Buttons -->
      <div class="p-6 pt-2 flex gap-3 flex-shrink-0 border-t border-white/5 bg-slate-900/30">
        <button 
          @click="close"
          class="flex-1 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl border border-slate-700 hover:border-slate-600 transition-all shadow-lg active:scale-95 text-sm uppercase tracking-wide"
        >
          Cancelar
        </button>
        
        <button 
          @click="confirm"
          :disabled="loading || !hasEnoughSpace"
          class="flex-[1.5] py-3.5 rounded-xl font-bold text-white shadow-lg transition-all transform hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2 relative overflow-hidden group border border-transparent"
          :class="[
            loading || !hasEnoughSpace ? 'bg-slate-800 cursor-not-allowed text-slate-500 border-slate-700' : 'bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 shadow-emerald-500/25 border-emerald-500/20'
          ]"
        >
          <div v-if="!loading && hasEnoughSpace" class="absolute top-0 -inset-full h-full w-1/2 z-5 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-20 group-hover:animate-shine" />
          
          <svg v-if="loading" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span v-else-if="!hasEnoughSpace">Espaço Insuficiente</span>
          <span v-else class="text-sm uppercase tracking-wide">BAIXAR AGORA</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatBytes } from '../utils/format'

const props = defineProps({
  isOpen: Boolean,
  item: Object,
  imageUrl: String,
  destination: String,
  browseLoading: Boolean,
  loading: Boolean,
  
  // Dados de Espaço
  freeSpaceInfo: Object,
  estimatedRequiredSpace: Number,
  isRepackDetected: Boolean,
  isPlaceholderSize: Boolean,
  hasEnoughSpace: Boolean,

  // Dados de Modal Info (Size/Checks)
  modalInfo: {
    type: Object,
    default: () => ({ size: null, check: false, eta: null })
  },

  // Dados de Preflight
  preflightLoading: Boolean,
  preflightError: String,
  preflightResult: Object,
  preflightAria2: Object,
  preflightHealth: Object
})

const emit = defineEmits(['close', 'confirm', 'browse', 'refresh-preflight'])

function close() { emit('close') }
function confirm() { emit('confirm') }
function browse() { emit('browse') }
function refreshPreflight() { emit('refresh-preflight') }

const displaySize = computed(() => {
  return props.modalInfo?.size || props.item?.size || 0
})

const spaceBarPercent = computed(() => {
  if (!props.freeSpaceInfo?.free) return 0
  const req = props.estimatedRequiredSpace || 0
  const total = props.freeSpaceInfo.free
  return Math.min((req / total) * 100, 100)
})

const isMagnet = computed(() => {
  return (props.item?.url || '').startsWith('magnet:') || 
         String(props.preflightResult?.note || '').toLowerCase().includes('magnet')
})

const seedersDisplay = computed(() => {
  if (props.preflightHealth && props.preflightHealth.seeders !== undefined) {
    return props.preflightHealth.seeders
  }
  return '-'
})

const leechersDisplay = computed(() => {
  if (props.preflightHealth && props.preflightHealth.leechers !== undefined) {
    return props.preflightHealth.leechers
  }
  return '-'
})

const healthColorClass = computed(() => {
  const s = Number(seedersDisplay.value)
  if (!Number.isFinite(s)) return 'text-slate-500'
  if (s >= 20) return 'text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]'
  if (s >= 5) return 'text-amber-400'
  return 'text-red-400'
})

const healthPercent = computed(() => {
  const s = Number(seedersDisplay.value) || 0
  // Satura a barra em 20 seeds
  return Math.min((s / 20) * 100, 100)
})
</script>

<style scoped>
.animate-in {
  animation-duration: 0.2s;
  animation-fill-mode: both;
}
.zoom-in-95 {
  --tw-enter-scale: 0.95;
}
@keyframes shine {
  100% {
    left: 125%;
  }
}
.animate-shine {
  animation: shine 1.5s;
}

/* Scrollbar Premium */
.scrollbar-premium::-webkit-scrollbar {
  width: 5px;
}
.scrollbar-premium::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
}
.scrollbar-premium::-webkit-scrollbar-thumb {
  background: rgba(6, 182, 212, 0.2);
  border-radius: 10px;
  border: 1px solid rgba(6, 182, 212, 0.1);
}
.scrollbar-premium::-webkit-scrollbar-thumb:hover {
  background: rgba(6, 182, 212, 0.4);
}
</style>
