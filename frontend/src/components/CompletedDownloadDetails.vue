<template>
  <Modal v-if="job" :isOpen="show" @close="$emit('close')" title="Detalhes do Download Concluído">
    <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
      <!-- Header -->
      <div class="border-b border-slate-700 pb-4">
        <h3 class="text-xl font-bold text-green-400">{{ job.item_name || job.name || 'Download' }}</h3>
        <p class="text-xs text-slate-400 mt-2 break-all">{{ formatUrl(job.item_url || job.url) }}</p>
      </div>

      <!-- Status Badge -->
      <div class="p-3 bg-green-500/20 border border-green-500/50 rounded-lg flex items-center gap-2">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-green-400">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <div>
          <p class="text-xs text-slate-400">Status</p>
          <p class="text-sm font-bold text-green-400">Concluído com Sucesso</p>
        </div>
      </div>

      <!-- Informações de Tamanho -->
      <div class="grid grid-cols-2 gap-4 p-3 bg-slate-900/50 rounded">
        <div>
          <p class="text-xs text-slate-400 mb-1">Tamanho Total</p>
          <p class="text-sm font-bold text-cyan-300">{{ formatBytes(job.size || job.total || job.downloaded || 0) }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-400 mb-1">Progresso</p>
          <p class="text-sm font-bold text-green-400">100%</p>
        </div>
      </div>

      <!-- Barra de progresso (sempre 100%) -->
      <div>
        <div class="w-full bg-slate-900 rounded-full h-3 overflow-hidden">
          <div
            class="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full"
            style="width: 100%"
          />
        </div>
      </div>

      <!-- Informações de Tempo -->
      <div class="grid grid-cols-2 gap-4 p-3 bg-slate-900/50 rounded text-sm">
        <div>
          <p class="text-xs text-slate-400 mb-1">Criado em</p>
          <p class="text-slate-300">{{ formatDate(job.created_at) }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-400 mb-1">Concluído em</p>
          <p class="text-slate-300">{{ formatDate(job.updated_at || job.completed_at) }}</p>
        </div>
      </div>

      <!-- Localização -->
      <div class="p-3 bg-slate-900/50 rounded">
        <p class="text-xs text-slate-400 mb-2">Salvo em</p>
        <p class="text-sm text-slate-300 break-all font-mono bg-slate-900 p-2 rounded border border-slate-700">
          {{ job.dest || '—' }}
        </p>
      </div>

      <!-- ID do Job -->
      <div class="p-3 bg-slate-900/50 rounded">
        <p class="text-xs text-slate-400 mb-1">ID do Download</p>
        <p class="text-sm text-slate-300 font-mono">{{ job.id }}</p>
      </div>

      <!-- Botões de Ação -->
      <div class="flex gap-2 pt-4 border-t border-slate-700">
        <Button @click="$emit('close')" variant="outline" size="md" class="flex-1 flex items-center justify-center gap-1 whitespace-nowrap btn-translucent">
          Fechar
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import Modal from './Modal.vue'
import Button from './Button.vue'
import { formatBytes } from '../utils/format'

defineProps({
  job: {
    type: Object,
    default: null
  },
  show: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR')
  } catch {
    return dateStr
  }
}

function formatUrl(url) {
  if (!url) return '—'
  
  // Se for um magnet link, extrai apenas o nome (dn=)
  if (url.startsWith('magnet:')) {
    const match = url.match(/dn=([^&]+)/)
    if (match) {
      return decodeURIComponent(match[1])
    }
    return 'Magnet Link'
  }
  
  // Para URLs normais, mostra apenas o domínio
  try {
    const urlObj = new URL(url)
    return urlObj.hostname + urlObj.pathname
  } catch {
    return url.substring(0, 50) + (url.length > 50 ? '...' : '')
  }
}
</script>
