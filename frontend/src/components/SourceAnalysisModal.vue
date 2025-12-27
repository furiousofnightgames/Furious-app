<template>
  <div v-if="open" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="$emit('close')"></div>

    <!-- Modal Content -->
    <div class="relative bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
      
      <!-- Header -->
      <div class="p-6 border-b border-slate-700/50 bg-slate-900/50 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-white flex items-center gap-2">
            <span class="text-cyan-400">⚡</span> Análise de Fontes
          </h2>
          <p class="text-slate-400 text-sm mt-1">
            Encontramos outras fontes para este download. Compare e escolha a melhor opção.
          </p>
        </div>
        <button @click="$emit('close')" class="text-slate-400 hover:text-white transition">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-auto">
        
        <!-- Loading State -->
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-12 space-y-4">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 border-4 border-slate-700/50 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-cyan-500 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <div class="text-center">
                <h3 class="text-lg font-bold text-white mb-1">Analisando Fontes...</h3>
                <p class="text-slate-400 text-sm">Buscando as melhores opções de download em tempo real.</p>
            </div>
        </div>

        <!-- content -->
        <div v-else>
            <!-- Original Item (Highlighted) -->
            <div class="mb-8">
              <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Sua Escolha Original</h3>
              <div class="bg-slate-800/50 border border-slate-700 rounded-lg p-4 flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="p-3 bg-slate-700/50 rounded-lg">
                    <svg class="w-6 h-6 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </div>
                  <div>
                    <div class="font-medium text-white whitespace-normal break-words">{{ originalItem?.name || 'Carregando...' }}</div>
                    <div class="text-sm text-slate-400 flex items-center gap-3">
                      <span>{{ originalItem?.source || '...' }}</span>
                      <span class="w-1 h-1 bg-slate-600 rounded-full"></span>
                      <span>{{ formatSize(originalItem?.size) }}</span>
                      <span class="w-1 h-1 bg-slate-600 rounded-full"></span>
                      <span>{{ formatUploadDate(originalItem?.uploadDate) }}</span>
                    </div>
                  </div>
                </div>
                <!-- ... rest of original item ... -->
                <div class="flex items-center gap-4">
                   <!-- Health Badge Original -->
                    <div :class="getHealthBadgeClass(originalHealth)" class="px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-2">
                        <span>{{ originalHealth?.label || '...' }}</span>
                        <span class="opacity-70 font-normal">({{ originalHealth?.seeders || 0 }} seeds)</span>
                    </div>
                    <button 
                      @click="$emit('confirm', originalItem)"
                      class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition text-sm font-medium"
                    >
                      Manter
                    </button>
                </div>
              </div>
            </div>

            <!-- Candidates Table -->
            <div>
              <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                Alternativas Encontradas
                <span class="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">{{ candidates.length }}</span>
              </h3>
              
              <div v-if="candidates.length === 0" class="text-center py-8 text-slate-500 italic border border-dashed border-slate-800 rounded-lg">
                Nenhuma alternativa encontrada para este item.
              </div>

              <div v-else class="border border-slate-700 rounded-lg overflow-hidden">
                <table class="w-full text-left text-sm">
                  <thead class="bg-slate-800/50 text-slate-400 font-medium">
                    <tr>
                      <th class="p-4">Fonte / Nome</th>
                      <th class="p-4 text-center">Data</th>
                      <th class="p-4 text-right">Tamanho</th>
                      <th class="p-4 text-center">Saúde (Seeds)</th>
                      <th class="p-4 text-right">Ação</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-700/50">
                    <tr v-for="(cand, idx) in candidates" :key="idx" class="hover:bg-slate-800/30 transition group">
                      <td class="p-4">
                        <div class="font-medium text-white group-hover:text-cyan-400 transition">{{ cand.source_title }}</div>
                        <div class="text-xs text-slate-200 group-hover:text-cyan-200 whitespace-normal break-words transition" :title="cand.item.name">{{ cand.item.name }}</div>
                      </td>
                      <td class="p-4 text-center text-slate-300">
                        {{ formatUploadDate(cand.item?.uploadDate) }}
                      </td>
                      <td class="p-4 text-right text-slate-300 font-mono">
                        {{ formatSize(cand.item.size) }}
                      </td>
                      <td class="p-4">
                        <div class="flex justify-center">
                            <div :class="getHealthBadgeClass(cand.health)" class="px-2 py-1 rounded-full text-xs font-bold border w-24 text-center">
                                {{ cand.health.label || 'Desconhecido' }}
                                <span class="block text-[10px] font-normal opacity-70">{{ cand.health.seeders }} seeds</span>
                            </div>
                        </div>
                      </td>
                      <td class="p-4 text-right">
                        <button 
                          @click="$emit('confirm', cand.item)"
                          class="px-3 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:border-cyan-400 rounded-lg transition text-xs font-semibold uppercase tracking-wide"
                        >
                          Trocar
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Discrepancy Note -->
            <div class="mt-6 p-3 bg-slate-800/30 border border-slate-700/50 rounded-lg flex gap-3">
                <div class="text-slate-400 mt-0.5">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div class="text-xs text-slate-400 leading-relaxed">
                    <span class="font-semibold text-slate-300">Nota sobre Conexões:</span> 
                    O número de "Seeds" indica a saúde global da rede (potencial total). 
                    Ao iniciar o download, é normal ver menos conexões no início enquanto o gerenciador negocia com os pares disponíveis.
                </div>
            </div>

        </div>
      </div>

      <!-- Footer -->
      <div v-if="!isLoading" class="p-4 border-t border-slate-800 bg-slate-900/50 flex justify-end gap-3">
        <button 
          @click="$emit('close')"
          class="px-4 py-2 text-slate-400 hover:text-white transition text-sm"
        >
          Cancelar Download
        </button>
        <button 
          @click="$emit('confirm', originalItem)"
          class="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition text-sm font-medium shadow-lg"
        >
          Ignorar e Baixar Original
        </button>
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
  if (!bytes) return 'N/A'
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
  // If backend sends relative strings, keep them.
  if (s.includes('ago') || s.includes('há')) return s
  // Try ISO parsing
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  try {
    return d.toLocaleDateString('pt-BR')
  } catch (e) {
    return s
  }
}

function getHealthBadgeClass(health) {
    if (!health) return 'bg-slate-700 text-slate-300 border-slate-600'
    // Backend returns numeric score: 100, 75, 50, 25
    const s = health.score
    if (s >= 90) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' // Excellent
    if (s >= 70) return 'bg-green-500/10 text-green-400 border-green-500/30'     // Good
    if (s >= 40) return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'  // Regular
    if (s >= 0) return 'bg-red-500/10 text-red-500 border-red-500/30'            // Poor
    
    // Fallback for label strings if old cache
    if (health.label === 'Excelente') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
    return 'bg-slate-700 text-slate-300 border-slate-600'
}
</script>
