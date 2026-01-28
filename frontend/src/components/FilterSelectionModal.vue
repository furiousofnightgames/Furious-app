<template>
  <div v-if="isOpen" class="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-300" @click.self="$emit('close')">
    <div 
      class="relative w-full max-w-4xl bg-[#0b1120]/95 rounded-3xl border border-white/10 shadow-[0_0_80px_-20px_rgba(6,182,212,0.3)] overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-500"
    >
      <!-- Premium Glow Background -->
      <div class="absolute -top-24 -right-24 w-64 h-64 bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-500/10 blur-[100px] rounded-full pointer-events-none"></div>

      <!-- Header -->
      <div class="relative p-8 border-b border-white/5 flex-shrink-0 bg-slate-900/50">
        <div class="flex flex-col gap-6">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <div class="flex items-center gap-3 mb-1">
                <div :class="['w-2 h-2 rounded-full shadow-[0_0_10px]', variantColorClass]"></div>
                <span :class="['text-[10px] font-black uppercase tracking-[0.3em]', variantTextClass]">{{ label }}</span>
              </div>
              <h2 class="text-3xl font-black text-white uppercase italic tracking-tight">Selecionar {{ title }}</h2>
              <p class="text-xs text-slate-500 font-medium uppercase tracking-widest">Escolha múltiplos itens para filtrar sua coleção.</p>
            </div>

            <button 
              @click="$emit('close')"
              class="w-12 h-12 bg-slate-800/50 hover:bg-slate-700/50 border border-white/10 rounded-2xl text-slate-400 hover:text-white transition-all active:scale-90 flex items-center justify-center group"
            >
              <svg class="w-6 h-6 group-hover:rotate-90 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Search & Controls -->
          <div class="flex flex-col sm:flex-row gap-4">
            <div class="relative flex-1">
              <div class="absolute inset-y-0 left-5 flex items-center pointer-events-none text-slate-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input 
                v-model="searchQuery"
                type="text"
                placeholder="PROCURAR..."
                class="w-full h-14 bg-slate-950/50 border border-white/10 rounded-2xl pl-14 pr-6 text-white text-xs font-black uppercase tracking-widest focus:outline-none focus:border-cyan-500/50 transition-all placeholder:text-slate-700"
              />
            </div>

            <div class="flex gap-2">
              <button 
                @click="selectAll"
                class="px-6 h-14 bg-slate-800/30 hover:bg-slate-700/30 border border-white/5 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white transition-all active:scale-95"
              >
                Todos
              </button>
              <button 
                @click="clearAll"
                class="px-6 h-14 bg-slate-800/30 hover:bg-slate-700/30 border border-white/5 rounded-2xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-rose-400 transition-all active:scale-95"
              >
                Nenhum
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Content: Grid of items -->
      <div class="flex-1 overflow-y-auto p-8 scrollbar-premium bg-black/20">
        <div v-if="filteredOptions.length === 0" class="flex flex-col items-center justify-center py-20 text-slate-600">
           <svg class="w-16 h-16 mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 9.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
           </svg>
           <span class="text-[11px] font-black uppercase tracking-[0.3em]">Nenhum item encontrado</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div 
            v-for="item in filteredOptions" 
            :key="item"
            @click="toggleItem(item)"
            :class="[
              'group relative p-4 rounded-2xl border transition-all cursor-pointer select-none active:scale-95',
              isSelected(item) 
                ? 'bg-gradient-to-br from-cyan-500/20 to-blue-500/10 border-cyan-500/40 shadow-lg shadow-cyan-500/10' 
                : 'bg-white/[0.02] border-white/5 hover:border-white/10 hover:bg-white/[0.04]'
            ]"
          >
            <div class="flex items-center gap-4">
              <!-- Custom Checkbox -->
              <div :class="[
                'w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all',
                isSelected(item) ? 'bg-cyan-500 border-cyan-400 scale-110' : 'border-white/10'
              ]">
                <svg v-if="isSelected(item)" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              
              <span :class="[
                'text-[11px] font-black uppercase tracking-wider transition-colors truncate flex-1',
                isSelected(item) ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
              ]">
                {{ translate ? translate(item) : item }}
              </span>
            </div>
            
            <!-- Glow effect on hover/active -->
            <div class="absolute inset-0 rounded-2xl bg-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
          </div>
        </div>
      </div>

      <!-- Footer: Confirm -->
      <div class="p-8 border-t border-white/5 bg-slate-900/50 flex-shrink-0">
        <div class="flex items-center justify-between gap-6">
          <div class="hidden sm:block">
            <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Ativos agora:</span>
            <span class="ml-2 text-sm font-black text-cyan-400 uppercase tracking-tighter">{{ internalSelected.length }} selecionados</span>
          </div>

          <div class="flex-1 sm:flex-none flex gap-3">
             <button 
              @click="$emit('close')"
              class="flex-1 sm:px-10 h-14 rounded-2xl border border-white/10 text-[11px] font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/5 transition-all active:scale-95"
            >
              Cancelar
            </button>
            <button 
              @click="confirmSelection"
              class="flex-1 sm:px-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-700 text-white border border-cyan-400/30 text-[11px] font-black uppercase tracking-widest shadow-[0_8px_25px_-5px_rgba(6,182,212,0.5)] transition-all active:scale-95 flex items-center justify-center gap-2 group/btn"
            >
              Confirmar
              <svg class="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  title: String,
  label: String,
  options: {
    type: Array,
    default: () => []
  },
  selected: {
    type: Array,
    default: () => []
  },
  variant: {
    type: String,
    default: 'cyan' // 'cyan', 'purple', 'amber'
  },
  translate: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['close', 'confirm'])

const searchQuery = ref('')
const internalSelected = ref([])

// Sync internal selection when modal opens
watch(() => props.isOpen, (val) => {
  if (val) {
    internalSelected.value = [...props.selected]
    searchQuery.value = ''
  }
})

const variantColorClass = computed(() => {
  if (props.variant === 'purple') return 'bg-purple-500 shadow-purple-500/50'
  if (props.variant === 'amber') return 'bg-amber-500 shadow-amber-500/50'
  return 'bg-cyan-500 shadow-cyan-500/50'
})

const variantTextClass = computed(() => {
  if (props.variant === 'purple') return 'text-purple-400/80'
  if (props.variant === 'amber') return 'text-amber-400/80'
  return 'text-cyan-400/80'
})

const filteredOptions = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.options
  return props.options.filter(o => {
    const original = o.toLowerCase()
    const translated = props.translate ? props.translate(o).toLowerCase() : ''
    return original.includes(q) || translated.includes(q)
  })
})

function isSelected(item) {
  return internalSelected.value.includes(item)
}

function toggleItem(item) {
  const idx = internalSelected.value.indexOf(item)
  if (idx === -1) {
    internalSelected.value.push(item)
  } else {
    internalSelected.value.splice(idx, 1)
  }
}

function selectAll() {
  // Only select items that match current filter for better UX
  const toAdd = filteredOptions.value.filter(o => !isSelected(o))
  internalSelected.value = [...internalSelected.value, ...toAdd]
}

function clearAll() {
  if (!searchQuery.value) {
    internalSelected.value = []
  } else {
    // Only clear filtered items
    internalSelected.value = internalSelected.value.filter(o => !filteredOptions.value.includes(o))
  }
}

function confirmSelection() {
  emit('confirm', [...internalSelected.value])
}
</script>

<style scoped>
.animate-in {
  animation-duration: 0.3s;
  animation-fill-mode: both;
}
.zoom-in-95 {
  --tw-enter-scale: 0.95;
}

/* Scrollbar Premium */
.scrollbar-premium::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-premium::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.3);
}
.scrollbar-premium::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}
.scrollbar-premium::-webkit-scrollbar-thumb:hover {
  background: rgba(6, 182, 212, 0.2);
}
</style>
