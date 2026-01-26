<template>
  <div v-if="open" class="fixed inset-0 z-[100] flex items-center justify-center p-2 sm:p-4">
    <!-- Backdrop with Progressive Blur -->
    <div 
      class="absolute inset-0 bg-black/60 backdrop-blur-md transition-all duration-500" 
      @click="$emit('close')"
    ></div>

    <!-- Modal Container: Premium Glass UI -->
    <div class="relative w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-500 ease-out sm:rounded-3xl rounded-xl">
      
      <!-- Outer Glow & Border Effect -->
      <div class="absolute inset-0 p-[1.5px] bg-gradient-to-br from-cyan-500/50 via-purple-500/30 to-blue-600/50 opacity-100 shadow-[0_0_50px_-12px_rgba(6,182,212,0.3)] pointer-events-none"></div>
      
      <!-- Inner Background -->
      <div class="relative flex flex-col w-full h-full bg-[#0a0f1d]/95 backdrop-blur-2xl overflow-hidden border border-white/5">
        
        <!-- Header Section -->
        <div class="p-4 sm:p-8 border-b border-white/5 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3 sm:gap-5">
            <div class="relative shrink-0">
              <div class="absolute inset-0 bg-cyan-500 blur-xl opacity-20 animate-pulse"></div>
              <div class="relative w-10 h-10 sm:w-14 sm:h-14 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center shadow-lg transition-transform duration-300">
                <svg class="w-6 h-6 sm:w-8 sm:h-8 text-white drop-shadow-md" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <div class="min-w-0">
              <h2 class="text-lg sm:text-2xl font-black text-white tracking-tight uppercase italic flex items-center gap-1">
                Análise de <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">Fontes</span>
              </h2>
              <p class="text-slate-400 text-[10px] sm:text-sm font-medium mt-1 flex items-center gap-2 truncate">
                <span class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-cyan-400 animate-pulse shrink-0"></span>
                Opções otimizadas para o seu download.
              </p>
            </div>
          </div>
          <button 
            @click="$emit('close')" 
            class="group p-2 hover:bg-white/5 rounded-xl transition-all duration-300 shrink-0"
          >
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-slate-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Scrollable Body -->
        <div class="p-4 sm:p-8 overflow-auto custom-scrollbar flex-1">
          
          <!-- Loading State: Premium Spinner -->
          <div v-if="isLoading" class="flex flex-col items-center justify-center py-10 sm:py-20">
            <div class="relative w-16 h-16 sm:w-24 sm:h-24 mb-6">
              <div class="absolute inset-0 border-4 border-cyan-500/10 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-cyan-400 rounded-full border-t-transparent animate-spin-slow shadow-[0_0_20px_rgba(34,211,238,0.4)]"></div>
              <div class="absolute inset-4 border-2 border-purple-500/20 rounded-full animate-pulse"></div>
            </div>
            <div class="text-center animate-pulse">
              <h3 class="text-lg sm:text-xl font-bold text-white mb-2">Escaneando Redes...</h3>
              <p class="text-slate-400 text-[10px] sm:text-sm max-w-xs mx-auto">Verificando disponibilidade em tempo real.</p>
            </div>
          </div>

          <!-- Content -->
          <div v-else class="space-y-6 sm:space-y-10">
            
            <!-- Original Choice Card -->
            <section>
              <h3 class="text-[10px] sm:text-xs font-black text-slate-500 uppercase tracking-widest mb-3 sm:mb-4 ml-1">Sua Escolha Original</h3>
              <div class="group relative">
                <!-- Background Glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl blur opacity-10 group-hover:opacity-30 transition duration-500"></div>
                
                <div class="relative bg-white/[0.03] border border-white/10 rounded-xl p-4 sm:p-6 flex flex-col items-start justify-between gap-4 sm:gap-6 backdrop-blur-sm lg:flex-row lg:items-center">
                  <div class="flex items-start sm:items-center gap-4 sm:gap-6 w-full">
                    <div class="p-3 sm:p-4 bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-white/5 shadow-inner shrink-0">
                      <svg class="w-6 h-6 sm:w-8 sm:h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-base sm:text-xl font-bold text-white whitespace-normal break-words leading-tight uppercase tracking-tight group-hover:text-cyan-400 transition-colors">
                        {{ originalItem?.name || 'Carregando...' }}
                      </div>
                      <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1.5">
                        <span class="px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/30 rounded-md text-[10px] sm:text-xs font-black text-cyan-400 uppercase tracking-wider">
                          {{ originalItem?.source_title || originalItem?.source || 'FONTE' }}
                        </span>
                        <div class="h-1 w-1 bg-slate-700 rounded-full shrink-0"></div>
                        <span class="text-[10px] sm:text-sm font-semibold text-cyan-400/80 font-mono">{{ formatSize(originalItem?.size) }}</span>
                        <div class="h-1 w-1 bg-slate-700 rounded-full shrink-0"></div>
                        <span class="text-[10px] sm:text-sm font-medium text-slate-500">{{ formatUploadDate(originalItem?.uploadDate) }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="flex items-center gap-3 sm:gap-4 w-full lg:w-auto shrink-0 mt-2 lg:mt-0">
                     <!-- Health Badge Original -->
                      <div :class="getHealthBadgeClass(originalHealth)" class="flex-1 lg:flex-none flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 rounded-lg sm:rounded-xl border-2 shadow-[0_0_15px_-5px_currentColor]">
                          <div class="w-2 h-2 rounded-full bg-current animate-pulse shrink-0"></div>
                          <div class="flex flex-col leading-none">
                            <span class="text-[11px] sm:text-xs font-black uppercase">{{ originalHealth?.label || '...' }}</span>
                            <span class="text-[10px] sm:text-[11px] font-bold opacity-80 font-mono mt-0.5 uppercase tracking-tighter">{{ originalHealth?.seeders || 0 }} SEEDS</span>
                          </div>
                      </div>
                      
                      <button 
                        @click="$emit('confirm', originalItem)"
                        class="flex-1 lg:flex-none px-4 sm:px-8 py-2.5 sm:py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg sm:rounded-xl transition-all duration-300 text-xs sm:text-sm font-black uppercase tracking-wider border border-white/10 active:scale-95"
                      >
                        Manter
                      </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- Alternatives Section -->
            <section>
              <div class="flex items-center justify-between mb-4 px-1">
                <h3 class="text-[10px] sm:text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                  Alternativas Encontradas
                </h3>
                <span class="px-2 sm:px-3 py-0.5 sm:py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[9px] sm:text-xs font-black rounded-full shadow-inner">{{ candidates.length }} OPÇÕES</span>
              </div>
              
              <div v-if="candidates.length === 0" class="flex flex-col items-center justify-center py-12 bg-white/[0.02] border-2 border-dashed border-white/5 rounded-2xl sm:rounded-3xl">
                <svg class="w-10 h-10 sm:w-12 sm:h-12 text-slate-700 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-slate-500 text-xs sm:text-sm font-bold italic tracking-wide text-center px-4">Nenhuma alternativa otimizada encontrada para este arquivo.</div>
              </div>

              <div v-else class="space-y-3 sm:space-y-4">
                <div 
                  v-for="(cand, idx) in candidates" 
                  :key="idx" 
                  class="group relative overflow-hidden bg-white/[0.02] border border-white/5 hover:border-cyan-500/30 hover:bg-white/[0.04] rounded-xl sm:rounded-2xl p-3 sm:p-5 transition-all duration-300 flex flex-col lg:flex-row lg:items-center gap-4 animate-in slide-in-from-bottom-2 duration-500"
                  :style="{ transitionDelay: `${idx * 80}ms` }"
                >
                  <!-- Label/Name Column -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-2">
                      <span class="text-[8px] sm:text-[10px] font-black uppercase px-2 py-0.5 bg-cyan-500/10 text-cyan-400 rounded border border-cyan-500/20 shadow-sm shrink-0">{{ cand.source_title }}</span>
                      <span class="text-[9px] sm:text-[10px] text-slate-500 font-mono">{{ formatUploadDate(cand.item?.uploadDate) }}</span>
                    </div>
                    <div class="font-bold text-slate-200 group-hover:text-white transition-colors whitespace-normal break-words leading-tight uppercase tracking-tight text-sm sm:text-base">
                      {{ cand.item.name }}
                    </div>
                  </div>

                  <!-- Metrics Group -->
                  <div class="flex items-center gap-4 sm:gap-6 shrink-0 w-full lg:w-auto mt-2 lg:mt-0 justify-between lg:justify-end">
                    <!-- Size -->
                    <div class="flex flex-col items-start lg:items-end">
                      <span class="text-[8px] sm:text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Tamanho</span>
                      <span class="text-xs sm:text-sm font-mono font-bold text-slate-300">{{ formatSize(cand.item.size) }}</span>
                    </div>

                    <!-- Health -->
                    <div class="flex justify-center min-w-[100px] sm:min-w-[140px]">
                        <div :class="getHealthBadgeClass(cand.health)" class="w-full flex items-center gap-2 px-3 py-2 rounded-lg border-2 shadow-[0_0_10px_-4px_currentColor] justify-center">
                            <div class="w-1.5 h-1.5 rounded-full bg-current animate-pulse shrink-0"></div>
                            <div class="flex flex-col leading-none text-center">
                              <span class="text-[10px] sm:text-[11px] font-black uppercase tracking-tight">{{ cand.health.label || '??' }}</span>
                              <span class="text-[9px] sm:text-[10px] font-black opacity-80 font-mono mt-0.5 uppercase tracking-tighter">{{ cand.health.seeders || 0 }} SEEDS</span>
                            </div>
                        </div>
                    </div>

                    <!-- Action -->
                    <button 
                      @click="$emit('confirm', cand.item)"
                      class="px-4 sm:px-6 py-2 sm:py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg sm:rounded-xl transition-all duration-300 text-[10px] sm:text-xs font-black uppercase tracking-widest shadow-lg shadow-cyan-500/10 group-hover:shadow-cyan-400/30 active:scale-95 shrink-0"
                    >
                      Trocar
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- Discrepancy Note -->
            <div class="relative group p-4 sm:p-6 overflow-hidden rounded-2xl sm:rounded-3xl bg-gradient-to-br from-white/[0.03] to-white/[0.01] border border-white/10 shrink-0">
                <div class="flex gap-3 sm:gap-4 items-start relative z-10">
                    <div class="p-1.5 sm:p-2 bg-slate-800 rounded-lg border border-white/10 text-cyan-400 shrink-0">
                        <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div class="min-w-0">
                        <span class="block text-[10px] sm:text-sm font-black text-white uppercase tracking-wider mb-1">Nota Técnica sobre Conectividade</span> 
                        <p class="text-[9px] sm:text-xs text-slate-400 leading-relaxed font-medium">
                          O número de "Seeds" reflete a saúde global da rede. Pequenas oscilações iniciais são normais enquanto o sistema otimiza as rotas para sua localidade.
                        </p>
                    </div>
                </div>
            </div>

          </div>
        </div>

        <!-- Sticky Footer Actions -->
        <div v-if="!isLoading" class="p-4 sm:p-6 border-t border-white/5 bg-black/40 backdrop-blur-md flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4 shrink-0">
          <button 
            @click="$emit('close')"
            class="order-2 sm:order-1 w-full sm:w-auto px-6 py-2 text-slate-500 hover:text-white transition-colors text-[10px] sm:text-xs font-black uppercase tracking-widest border border-transparent hover:border-white/10 rounded-lg sm:rounded-xl"
          >
            Sair e Cancelar
          </button>
          
          <div class="order-1 sm:order-2 flex items-center gap-3 w-full sm:w-auto">
            <button 
              @click="$emit('confirm', originalItem)"
              class="w-full sm:px-8 py-2.5 sm:py-3 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white rounded-lg sm:rounded-2xl transition-all duration-300 text-[11px] sm:text-sm font-black uppercase tracking-wider shadow-xl border border-white/5 active:scale-95"
            >
              Ignorar e Baixar Original
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  open: Boolean,
  originalItem: Object,
  candidates: { type: Array, default: () => [] },
  originalHealth: Object, // { score, seeders }
  isLoading: Boolean
})

const emit = defineEmits(['close', 'confirm'])

function formatSize(bytes) {
  if (!bytes) return '0.0 GB'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(1)} ${units[i]}`
}

function formatUploadDate(v) {
  if (!v) return '—'
  const s = String(v).trim()
  if (!s) return '—'
  if (s.includes('ago') || s.includes('há')) return s
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  try {
    return d.toLocaleDateString('pt-BR')
  } catch (e) {
    return s
  }
}

function getHealthBadgeClass(health) {
    if (!health) return 'bg-slate-800/50 text-slate-500 border-white/10'
    const s = health.score
    
    // Premium Health Colors with glow contrast
    if (s >= 90) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' // Excellent
    if (s >= 70) return 'bg-green-500/10 text-green-400 border-green-500/30'     // Good
    if (s >= 40) return 'bg-amber-500/10 text-amber-400 border-amber-500/30'     // Regular
    if (s >= 0) return 'bg-rose-500/10 text-rose-500 border-rose-500/30'         // Poor
    
    if (health.label === 'Excelente') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
    return 'bg-slate-800/50 text-slate-400 border-white/10'
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
@media (min-width: 640px) {
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(34, 211, 238, 0.2);
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spin-slow 2s linear infinite;
}
</style>


