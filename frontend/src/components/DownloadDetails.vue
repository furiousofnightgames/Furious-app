<template>
  <Modal v-if="job" :isOpen="show" @close="$emit('close')" title="Detalhes do Download">
    <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
      <!-- Header -->
      <div class="border-b border-slate-700 pb-4">
        <h3 class="text-xl font-bold text-cyan-300">{{ job.item_name || job.name || 'Download' }}</h3>
        <p class="text-xs text-slate-400 mt-2 break-all">{{ formatUrl(job.item_url || job.url) }}</p>
      </div>

      <!-- Status e Progresso -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-xs text-slate-400 mb-1">Status</p>
          <p :style="{ color: getStatusColor(job.status) }" class="text-sm font-bold">
            {{ getStatusLabel(job.status) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-slate-400 mb-1">Progresso</p>
          <p class="text-sm font-bold text-cyan-300">{{ (Math.min(job.progress || 0, 100)).toFixed(2) }}%</p>
        </div>
      </div>

      <!-- Progresso Visual -->
      <div>
        <div class="w-full bg-slate-900 rounded-full h-3">
          <div
            class="bg-gradient-to-r from-cyan-500 to-purple-500 h-3 rounded-full transition-all"
            :style="{ width: `${Math.min(job.progress || 0, 100)}%` }"
          />
        </div>
      </div>

      <!-- Detalhes de Tamanho -->
      <div class="grid grid-cols-3 gap-4 p-3 bg-slate-900/50 rounded">
        <div>
          <p class="text-xs text-slate-400">Baixado</p>
          <p class="text-sm font-bold text-green-400">{{ formatBytes(job.downloaded || 0) }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-400">Total</p>
          <p class="text-sm font-bold text-cyan-300">{{ formatBytes(job.total || 0) }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-400">Restante</p>
          <p class="text-sm font-bold text-yellow-400">{{ formatBytes((job.total || 0) - (job.downloaded || 0)) }}</p>
        </div>
      </div>

      <!-- Velocidade e Tempo -->
      <div class="grid grid-cols-3 gap-4 p-3 bg-slate-900/50 rounded">
        <div>
          <p class="text-xs text-slate-400">Velocidade</p>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="px-2 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-semibold tracking-wide">
              {{ formatSpeed(job.speed || 0) }}
            </span>
            <span class="px-2 py-1 rounded-md bg-purple-500/10 border border-purple-500/30 text-purple-300 font-semibold tracking-wide">
              {{ formatMbps(job.speed || 0) }}
            </span>
          </div>
        </div>
        <div>
          <p class="text-xs text-slate-400">ETA</p>
          <p class="text-sm font-bold text-purple-400">{{ calculateETA(job.downloaded || 0, job.total || 0, job.speed || 0) || '—' }}</p>
        </div>
        <div>
          <p class="text-xs text-slate-400">Taxa</p>
          <p class="text-sm font-bold text-orange-400">{{ calculateSpeedMultiplier(job.speed) }}</p>
        </div>
      </div>

      <!-- Timestamps -->
      <div class="grid grid-cols-2 gap-4 text-xs">
        <div>
          <p class="text-slate-400">Criado</p>
          <p class="text-slate-300 mt-1">{{ formatDate(job.created_at) }}</p>
        </div>
        <div>
          <p class="text-slate-400">Atualizado</p>
          <p class="text-slate-300 mt-1">{{ formatDate(job.updated_at) }}</p>
        </div>
      </div>

      <!-- Configurações -->
      <div class="p-3 bg-slate-900/50 rounded space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-slate-400">Destino</span>
          <span class="text-slate-300 break-all text-right">{{ job.dest || '—' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Resumível</span>
          <span class="text-slate-300">{{ job.resume_on_start ? '✓ Sim' : '✗ Não' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Verificar SSL</span>
          <span class="text-slate-300">{{ job.verify_ssl ? '✓ Ativado' : '✗ Desativado' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">ID do Job</span>
          <span class="text-slate-300 font-mono">{{ job.id }}</span>
        </div>
      </div>

      <!-- Erro (se houver) -->
      <div v-if="job.last_error" class="p-3 bg-red-500/20 border border-red-500/50 rounded">
        <p class="text-xs text-red-400 font-bold mb-1">Último Erro:</p>
        <p class="text-sm text-red-200 break-all">{{ job.last_error }}</p>
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
import { formatBytes, formatSpeed, formatMbps, calculateETA, calculateSpeedMultiplier, getStatusColor, getStatusLabel } from '../utils/format'

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
