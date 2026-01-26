<template>
  <Modal v-if="job" :isOpen="show" @close="$emit('close')" maxWidthClass="max-w-3xl" class="modal-premium-blur">
    <template #header>
      <div class="flex items-center gap-4">
        <div class="relative shrink-0">
          <div class="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full animate-pulse"></div>
          <svg viewBox="0 0 24 24" fill="none" class="w-10 h-10 text-cyan-400 relative z-10 animate-[bounce_3s_infinite]" stroke="currentColor" stroke-width="2.5">
            <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h2 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 uppercase italic tracking-[0.15em] drop-shadow-sm leading-none">
          Detalhes
        </h2>
      </div>
    </template>
    <div class="space-y-6 max-h-[80vh] overflow-y-auto pr-3 custom-scrollbar">
      <!-- Header: Dynamic Title & Aura -->
      <div 
        class="relative p-6 rounded-3xl border border-white/10 overflow-hidden shadow-2xl transition-all duration-700"
        :class="getThemeClasses(job.status).bg"
      >
        <div class="absolute -right-8 -bottom-8 w-40 h-40 blur-3xl opacity-20 rounded-full" :class="getThemeClasses(job.status).glow"></div>
        
        <div class="flex items-start justify-between gap-4 relative z-10">
          <div class="space-y-1">
            <h3 class="text-2xl font-black text-white uppercase italic tracking-tighter leading-tight drop-shadow-lg">
              {{ job.item_name || job.name || 'Download' }}
            </h3>
            <p class="text-[10px] font-black uppercase tracking-[0.2em] opacity-50 text-white line-clamp-1">
              Origem: {{ formatUrl(job.item_url || job.url) }}
            </p>
          </div>
          <div 
            class="px-4 py-2 rounded-xl border border-white/20 backdrop-blur-md shadow-xl flex flex-col items-center justify-center min-w-[80px]"
            :class="getThemeClasses(job.status).badge"
          >
            <span class="text-[9px] font-black uppercase tracking-tighter opacity-70">Progress</span>
            <span class="text-xl font-black tabular-nums tracking-tighter">{{ (Math.min(job.progress || 0, 100)).toFixed(1) }}%</span>
          </div>
        </div>

        <!-- Progress Bar (Internal) -->
        <div class="mt-6 h-1.5 w-full bg-black/30 rounded-full overflow-hidden border border-white/5 p-[1px]">
          <div 
            class="h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(255,255,255,0.3)]"
            :class="getThemeClasses(job.status).bar"
            :style="{ width: `${Math.min(job.progress || 0, 100)}%` }"
          ></div>
        </div>
      </div>

      <!-- Alerta de Jogo Não Encontrado (Placeholder) -->
      <div v-if="job.not_found_on_store || job.best?.not_found_on_store || job.metadata?.not_found_on_store" class="bg-rose-500/10 border border-rose-500/20 rounded-3xl p-5 flex items-start gap-4 animate-in">
        <div class="p-2 bg-rose-500/20 rounded-full text-rose-500 shrink-0 mt-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <h3 class="font-bold text-rose-200 text-sm">Informações de Loja Não Encontradas</h3>
          <p class="text-rose-200/60 text-[11px] mt-1 leading-tight">
            Não existem dados oficiais para este título no momento.
          </p>
        </div>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-xl transition-transform hover:scale-[1.02]">
          <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Velocidade</p>
          <div class="flex items-center gap-2">
            <span class="text-lg font-black text-purple-400 tabular-nums">{{ formatMbps(job.speed || 0) }}</span>
          </div>
        </div>
        <div class="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-xl transition-transform hover:scale-[1.02]">
          <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Estimativa</p>
          <span class="text-lg font-black text-cyan-400 tabular-nums">{{ calculateETA(job.downloaded || 0, job.total || 0, job.speed || 0) || '∞' }}</span>
        </div>
        <div class="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-xl transition-transform hover:scale-[1.02]">
          <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Duração</p>
          <span class="text-lg font-black text-amber-400 tabular-nums">{{ calculateSpeedMultiplier(job.speed) }}</span>
        </div>
        <div class="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-xl transition-transform hover:scale-[1.02]">
          <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Status</p>
          <span class="text-[11px] font-black uppercase text-white tracking-tighter" :style="{ color: getStatusColor(job.status) }">
            {{ getStatusLabel(job.status) }}
          </span>
        </div>
      </div>

      <!-- Data Details Card -->
      <div class="bg-slate-900/40 backdrop-blur-3xl border border-white/10 rounded-3xl p-6 space-y-5 shadow-inner">
        <div class="flex items-center gap-2 border-b border-white/5 pb-4">
          <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5 text-slate-500" stroke="currentColor" stroke-width="2">
            <path d="M4 7v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2z" />
            <path d="M4 7h16" />
          </svg>
          <h4 class="text-xs font-black text-slate-300 uppercase tracking-widest">Informações de Tráfego</h4>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-5 gap-x-10">
          <div class="flex justify-between items-center bg-black/20 p-3 rounded-xl border border-white/5">
            <span class="text-xs text-slate-500 font-bold uppercase tracking-tighter">Baixado</span>
            <span class="text-sm font-black text-emerald-400 tabular-nums font-mono">{{ formatBytes(job.downloaded || 0) }}</span>
          </div>
          <div class="flex justify-between items-center bg-black/20 p-3 rounded-xl border border-white/5">
            <span class="text-xs text-slate-500 font-bold uppercase tracking-tighter">Tamanho</span>
            <span class="text-sm font-black text-white tabular-nums font-mono">{{ formatBytes(job.total || 0) }}</span>
          </div>
          <div class="flex justify-between items-center bg-black/20 p-3 rounded-xl border border-white/5">
            <span class="text-xs text-slate-500 font-bold uppercase tracking-tighter">Iniciado em</span>
            <span class="text-xs font-black text-slate-300">{{ formatDate(job.started_at) || 'Aguardando...' }}</span>
          </div>
          <div class="flex justify-between items-center bg-black/20 p-3 rounded-xl border border-white/5">
            <span class="text-xs text-slate-500 font-bold uppercase tracking-tighter">Última Atualização</span>
            <span class="text-xs font-black text-slate-300">{{ formatDate(job.updated_at) || 'Sincronizando...' }}</span>
          </div>
        </div>
      </div>

      <!-- Config & System Notes -->
      <div class="bg-black/20 rounded-3xl border border-white/5 p-6 space-y-4">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-1.5 h-6 bg-cyan-500 rounded-full shadow-[0_0_10px_#0ea5e9]"></div>
          <h4 class="text-xs font-black text-white uppercase tracking-widest">Parâmetros de Sistema</h4>
        </div>
        
        <div class="grid grid-cols-1 gap-3">
          <div class="flex justify-between text-xs py-2 border-b border-white/[0.03]">
            <span class="text-slate-500 font-bold uppercase tracking-tighter">Diretório de Destino</span>
            <span class="text-slate-300 font-mono font-medium break-all text-right max-w-[200px]">{{ job.dest || '—' }}</span>
          </div>
          <div class="flex justify-between text-xs py-2 border-b border-white/[0.03]">
            <span class="text-slate-500 font-bold uppercase tracking-tighter">Verificação SSL</span>
            <span :class="job.verify_ssl ? 'text-emerald-400' : 'text-rose-500'" class="font-black uppercase">{{ job.verify_ssl ? '✓ Protegido' : '✗ Desativado' }}</span>
          </div>
          <div class="flex justify-between text-xs py-2">
            <span class="text-slate-500 font-bold uppercase tracking-tighter">Protocolo de Retomada</span>
            <span class="text-cyan-400 font-black uppercase">{{ job.resume_on_start ? 'Ativado' : 'Incompatível' }}</span>
          </div>
        </div>
      </div>

      <!-- Error Console (Condition) -->
      <div v-if="job.last_error" class="bg-rose-500/10 border-2 border-rose-500/20 rounded-3xl p-6 animate-pulse">
        <div class="flex items-center gap-3 mb-3">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-rose-500"><path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
          <span class="text-[11px] font-black text-rose-500 uppercase tracking-[0.2em]">Depuração de Erros</span>
        </div>
        <div class="bg-black/40 rounded-xl p-4 font-mono text-[10px] text-rose-200 leading-relaxed border border-rose-500/10">
          {{ job.last_error }}
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
          Fechar Painel
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { computed } from 'vue'
import Modal from './Modal.vue'
import Button from './Button.vue'
import { formatBytes, formatSpeed, formatMbps, calculateETA, calculateSpeedMultiplier, getStatusColor, getStatusLabel } from '../utils/format'

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

function getThemeClasses(status) {
  if (['failed', 'error'].includes(status)) {
    return {
      bg: 'bg-gradient-to-br from-rose-950/80 to-slate-950/90 shadow-rose-900/10',
      glow: 'bg-rose-500',
      badge: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
      bar: 'bg-gradient-to-r from-rose-600 to-rose-400 shadow-[0_0_15px_#ef4444]'
    }
  }
  if (['paused', 'queued'].includes(status)) {
    return {
      bg: 'bg-gradient-to-br from-amber-950/80 to-slate-950/90 shadow-amber-900/10',
      glow: 'bg-amber-500',
      badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      bar: 'bg-gradient-to-r from-amber-600 to-amber-400 shadow-[0_0_15px_#f59e0b]'
    }
  }
  // Running/Default
  return {
    bg: 'bg-gradient-to-br from-slate-900/90 to-slate-950/95 shadow-cyan-900/10',
    glow: 'bg-cyan-500',
    badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-400/30',
    bar: 'bg-gradient-to-r from-cyan-600 to-blue-500 shadow-[0_0_15px_#0ea5e9]'
  }
}

function formatDate(dateStr) {
  if (!dateStr) return null
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
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
    return 'Hyperlink Magnet'
  }
  try {
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return 'Link Externo'
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
