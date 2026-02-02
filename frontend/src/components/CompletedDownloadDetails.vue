<template>
  <Modal v-if="job" :isOpen="show" @close="$emit('close')" maxWidthClass="max-w-3xl">
    <template #header>
      <div class="flex items-center gap-4">
        <div class="relative shrink-0">
          <div class="absolute inset-0 bg-emerald-500/20 blur-xl rounded-full animate-pulse"></div>
          <svg viewBox="0 0 24 24" fill="none" class="w-10 h-10 text-emerald-400 relative z-10 animate-[bounce_3s_infinite]" stroke="currentColor" stroke-width="2.5">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h2 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 uppercase italic tracking-[0.15em] drop-shadow-sm leading-none">
          Detalhes
        </h2>
      </div>
    </template>
    <div class="space-y-6 max-h-[80vh] overflow-y-auto pr-3 custom-scrollbar">
      <!-- Header: Success Aura -->
      <div class="relative p-6 rounded-3xl border border-white/10 bg-gradient-to-br from-emerald-950/80 to-slate-950/90 overflow-hidden shadow-2xl shadow-emerald-900/10">
        <div class="absolute -right-8 -bottom-8 w-40 h-40 bg-emerald-500 blur-3xl opacity-20 rounded-full"></div>
        
        <div class="flex items-start justify-between gap-4 relative z-10">
          <div class="space-y-1">
             <div class="flex items-center gap-2 mb-2">
                <span class="px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[9px] font-black uppercase tracking-widest">
                  Processamento Concluído
                </span>
             </div>
            <h3 class="text-2xl font-black text-white uppercase italic tracking-tighter leading-tight drop-shadow-lg">
              {{ job.item_name || job.name || 'Download' }}
            </h3>
            <p class="text-[10px] font-black uppercase tracking-[0.2em] opacity-50 text-white line-clamp-1">
              Origem: {{ formatUrl(job.item_url || job.url) }}
            </p>
          </div>
          <div class="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center shrink-0 shadow-lg shadow-emerald-500/20">
            <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-emerald-400" stroke="currentColor" stroke-width="3">
              <path d="M20 6L9 17L4 12" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- Progress Bar (Always 100%) -->
        <div class="mt-6 h-1 w-full bg-black/30 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-emerald-600 to-teal-400 w-full shadow-[0_0_15px_#10b981]"></div>
        </div>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-5 rounded-2xl shadow-xl flex flex-col justify-center min-h-[85px]">
          <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1 text-center">Tamanho em Disco</p>
          <p class="text-xl font-black text-white tabular-nums tracking-tighter text-center">
            {{ formatBytes(job.size || job.total || job.downloaded || 0) }}
          </p>
        </div>

        <div class="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-5 rounded-2xl shadow-xl text-center flex flex-col justify-center min-h-[85px]">
          <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1 text-center">Status de Saúde</p>
          
          <div v-if="loadingIntegrity" class="flex items-center justify-center gap-2 py-1">
             <div class="w-3 h-3 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
             <span class="text-[10px] font-bold text-cyan-500 uppercase animate-pulse">Analisando...</span>
          </div>
          
          <div v-else-if="integrityData" class="space-y-0.5">
            <p 
              class="text-sm font-black uppercase tracking-tighter"
              :class="{
                'text-emerald-400': integrityData.status === 'healthy',
                'text-amber-400': integrityData.status === 'warning',
                'text-rose-500': integrityData.status === 'critical'
              }"
            >
              {{ integrityData.status === 'healthy' ? 'Integridade OK' : (integrityData.status === 'warning' ? 'Atenção' : 'Falha Crítica') }}
            </p>
            <p class="text-[10px] font-mono font-bold opacity-60">Score: {{ integrityData.health_score }}%</p>
          </div>
          
          <span v-else class="text-sm font-black text-slate-600 uppercase tracking-tighter opacity-50 italic">Pendente</span>
        </div>
      </div>

      <!-- Integrity Issues Alert -->
      <div v-if="integrityData && integrityData.issues && integrityData.issues.length > 0" class="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 space-y-3 animate-in fade-in slide-in-from-top-2">
         <div class="flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" class="w-4 h-4 text-rose-500" stroke="currentColor" stroke-width="3">
               <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span class="text-[10px] font-black text-rose-300 uppercase tracking-widest">Inconsistências Detectadas</span>
         </div>
         <ul class="space-y-1.5 list-disc list-inside">
            <li v-for="(issue, i) in integrityData.issues" :key="i" class="text-[11px] font-bold text-rose-100/70 leading-tight">
               {{ issue }}
            </li>
         </ul>
      </div>

      <!-- Path & Location Card -->
      <div class="bg-slate-900/40 backdrop-blur-3xl border border-white/10 rounded-3xl p-6 space-y-4 shadow-inner">
        <div class="flex items-center gap-2 border-b border-white/5 pb-4">
          <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5 text-slate-500" stroke="currentColor" stroke-width="2">
            <path d="M3 7v10c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2h-6l-2-2H5c-1.1 0-2 .9-2 2z" />
          </svg>
          <h4 class="text-xs font-black text-slate-300 uppercase tracking-widest">Localização dos Arquivos</h4>
        </div>

        <div class="space-y-3">
           <div class="bg-black/30 p-4 rounded-xl border border-white/5 group transition-all hover:border-cyan-500/30">
              <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">Caminho do Diretório</p>
              <p class="text-xs text-slate-300 font-mono break-all leading-relaxed select-all cursor-text">
                {{ job.dest || '—' }}
              </p>
           </div>
        </div>
      </div>

      <!-- History Timestamps -->
      <div class="bg-black/20 rounded-3xl border border-white/5 p-6">
        <div class="grid grid-cols-2 gap-6">
          <div class="space-y-1">
            <p class="text-[9px] font-black text-slate-600 uppercase tracking-widest">Data de Criação</p>
            <p class="text-xs font-black text-slate-300">{{ formatDate(job.created_at) }}</p>
          </div>
          <div class="space-y-1">
            <p class="text-[9px] font-black text-slate-600 uppercase tracking-widest">Finalização</p>
            <p class="text-xs font-black text-emerald-400">{{ formatDate(job.completed_at || job.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="pt-6 border-t border-white/10">
        <Button 
          @click="$emit('close')" 
          variant="outline" 
          size="lg" 
          class="w-full bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl h-16 shadow-2xl transition-all active:scale-95 border-white/10"
        >
          Fechar Detalhes
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import Modal from './Modal.vue'
import Button from './Button.vue'
import { formatBytes } from '../utils/format'
import api from '../services/api'

const props = defineProps({
  job: {
    type: Object,
    default: null
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const integrityData = ref(null)
const loadingIntegrity = ref(false)

async function checkIntegrity() {
  if (!props.job || !props.job.id) return
  
  loadingIntegrity.value = true
  try {
    const res = await api.get(`/api/jobs/${props.job.id}/integrity`)
    integrityData.value = res.data
  } catch (e) {
    console.error('[IntegrityCheck] Failed:', e)
  } finally {
    loadingIntegrity.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    checkIntegrity()
  } else {
    integrityData.value = null
  }
})

onMounted(() => {
  if (props.show) checkIntegrity()
})

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

function formatUrl(url) {
  if (!url) return '—'
  if (url.startsWith('magnet:')) {
    const match = url.match(/dn=([^&]+)/)
    if (match) return decodeURIComponent(match[1])
    return 'Acervo Magnet'
  }
  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return 'Biblioteca Digital'
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
