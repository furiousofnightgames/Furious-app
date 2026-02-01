<template>
  <div v-if="isOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="$emit('close')">
    <div 
      class="relative w-full max-w-2xl bg-[#0b1120] rounded-2xl border border-cyan-500/30 shadow-[0_0_50px_-12px_rgba(6,182,212,0.25)] overflow-hidden animate-in fade-in zoom-in-95 duration-300 max-h-[calc(100vh-2rem)] flex flex-col"
    >
      <!-- Header Premium -->
      <div class="relative bg-gradient-to-b from-slate-800/50 to-slate-900/50 p-6 border-b border-white/5 flex-shrink-0">
        <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"></div>
        
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
             <div class="flex items-center gap-2 mb-1">
                <div class="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]"></div>
                <span class="text-[10px] font-bold text-cyan-400/80 uppercase tracking-[0.2em]">Versões Disponíveis</span>
             </div>
            <h2 class="text-2xl font-bold text-white tracking-tight leading-tight truncate pr-2" :title="groupName">
              {{ groupName }}
            </h2>
            <p class="text-xs text-slate-400 mt-1 font-medium">
              {{ versionsCount }} opções filtradas encontradas
            </p>
          </div>
          
          <button 
            @click="$emit('close')"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/30 rounded-xl text-slate-300 text-sm font-semibold transition-all active:scale-95 shadow-lg flex items-center gap-2 group"
          >
            <span>Fechar</span>
            <svg class="w-4 h-4 group-hover:rotate-90 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Versions List -->
      <div class="flex-1 overflow-y-auto scrollbar-premium p-6 space-y-4 bg-slate-950/20">
        <div
          v-for="(v, idx) in versions"
          :key="idx"
          class="relative group rounded-2xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900/80 hover:border-cyan-500/40 transition-all duration-300 overflow-hidden"
        >
          <!-- Hover Glow -->
          <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          
          <div class="p-5 relative z-10 flex flex-col sm:flex-row items-center gap-6">
            <!-- Item Info -->
            <div class="flex-1 min-w-0 w-full text-center sm:text-left">
              <h3 class="text-base font-bold text-slate-100 leading-snug mb-3 group-hover:text-white transition-colors">
                {{ v.name }}
              </h3>
              
              <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2 mb-4">
                <span class="px-2.5 py-0.5 rounded-lg text-[10px] font-bold bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 uppercase tracking-wide">
                  {{ v.source_title || ('Fonte #' + v.source_id) }}
                </span>
                
                <span v-if="v.uploadDate" class="px-2.5 py-0.5 rounded-lg text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                  {{ formatRelativeCompact(v.uploadDate) }}
                </span>

                <span class="px-2.5 py-0.5 rounded-lg text-[10px] font-bold bg-slate-800/80 border border-slate-700 text-slate-300">
                  {{ formatBytes(v.size) }}
                </span>
              </div>

            </div>

            <!-- Actions -->
            <div class="flex flex-row sm:flex-col items-center gap-3 w-full sm:w-auto">
                <FavoriteToggleButton :item="v" class="flex-shrink-0" />
                <button 
                @click.prevent.stop="$emit('select', v)"
                class="flex-1 sm:w-28 py-2.5 rounded-xl font-bold text-white shadow-lg transition-all transform hover:scale-[1.05] active:scale-95 flex items-center justify-center gap-2 relative overflow-hidden group/btn bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 shadow-emerald-500/25 border border-emerald-500/20"
                >
                    <div class="absolute top-0 -inset-full h-full w-1/2 z-5 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-20 group-hover/btn:animate-shine" />
                    <span class="text-xs uppercase tracking-widest">Baixar</span>
                </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Scroll Tip -->
      <div class="px-6 py-2 bg-slate-900/50 text-[10px] text-center text-slate-500 italic flex justify-center items-center gap-2 flex-shrink-0 border-t border-white/5">
         <svg class="w-3 h-3 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 14l-7 7-7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
         Role para ver todas as versões disponíveis
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatBytes, formatRelativeDate } from '../utils/format'
import FavoriteToggleButton from './FavoriteToggleButton.vue'

const props = defineProps({
  isOpen: Boolean,
  groupName: String,
  versionsCount: [Number, String],
  versions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['close', 'select'])

function formatRelativeCompact(dateStr) {
  if (!dateStr) return ''
  try {
    const dt = new Date(dateStr)
    const t = dt.getTime()
    if (isNaN(t)) {
      return formatRelativeDate(dateStr) || String(dateStr)
    }
    const now = Date.now()
    const diffSec = Math.max(0, Math.floor((now - t) / 1000))

    const minute = 60
    const hour = 60 * minute
    const day = 24 * hour
    const week = 7 * day

    if (diffSec < minute) return `há ${diffSec}s`
    if (diffSec < hour) return `há ${Math.floor(diffSec / minute)}m`
    if (diffSec < day) return `há ${Math.floor(diffSec / hour)}h`
    if (diffSec < week) return `há ${Math.floor(diffSec / day)}d`
    
    return formatRelativeDate(dateStr)
  } catch (e) {
    return String(dateStr)
  }
}
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
