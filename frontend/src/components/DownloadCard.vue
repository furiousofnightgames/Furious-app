<template>
  <Card class="overflow-hidden">
    <!-- Header Section with Status -->
    <div class="bg-gradient-to-r from-slate-900 to-slate-800 p-4 -m-4 mb-0 border-b border-slate-700/50">
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <span :style="{ backgroundColor: getStatusColor(job.status) + '30', color: getStatusColor(job.status) }" 
                  class="text-xs font-bold px-3 py-1 rounded-full border" 
                  :style="{ borderColor: getStatusColor(job.status) + '50' }">
              {{ getStatusLabel(job.status) }}
            </span>
            <span class="text-xs text-slate-500">{{ job.id }}</span>
          </div>
          <h3 class="text-base font-bold text-white line-clamp-2">{{ job.item_name || 'Download' }}</h3>
          <p class="text-xs text-slate-400 mt-1 break-all line-clamp-1">{{ job.item_url }}</p>
        </div>
        <div class="text-right shrink-0">
          <p class="text-3xl font-bold bg-gradient-to-br from-cyan-300 to-blue-400 bg-clip-text text-transparent">
            {{ downloadStore.formatProgress(Math.min(job.progress || 0, 100)) }}%
          </p>
          <p class="text-xs text-slate-400 mt-1">{{ formatBytes(job.downloaded || 0) }} / {{ formatBytes(job.total || 0) }}</p>
        </div>
      </div>
    </div>

    <div class="p-4 space-y-4">
      <!-- Progress Bar -->
      <ProgressBar :percentage="Math.min(job.progress || 0, 100)" label="Progresso" />

      <!-- Stats Grid -->
      <div class="grid grid-cols-3 gap-3 bg-gradient-to-br from-slate-900/50 to-slate-800/50 rounded-lg p-3 border border-slate-700/30">
        <div class="text-center">
          <div class="flex justify-center mb-1">
            <svg class="w-4 h-4 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 1a1 1 0 011-1h12a1 1 0 011 1H3zm0 4h14v2H3V5zm0 4h14v2H3V9zm0 4h14v2H3v-2zm0 4h14v2H3v-2z"/>
            </svg>
          </div>
          <p class="text-xs text-slate-400 mb-0.5">Velocidade</p>
          <p class="text-sm font-bold text-cyan-300">{{ formatSpeed(job.speed) }}</p>
        </div>
        <div class="text-center border-l border-r border-slate-700/30">
          <div class="flex justify-center mb-1">
            <svg class="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.5H7a1 1 0 100 2h4a1 1 0 001-1V7z"/>
            </svg>
          </div>
          <p class="text-xs text-slate-400 mb-0.5">Tempo</p>
          <p class="text-sm font-bold text-amber-300">{{ calculateETA(job.downloaded || 0, job.total || 0, job.speed || 0) }}</p>
        </div>
        <div class="text-center">
          <div class="flex justify-center mb-1">
            <svg class="w-4 h-4 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
            </svg>
          </div>
          <p class="text-xs text-slate-400 mb-0.5">Taxa</p>
          <p class="text-sm font-bold text-emerald-300">{{ calculateSpeedMultiplier(job.speed) }}</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2 flex-wrap">
        <Button
          variant="primary"
          size="sm"
          class="flex-1 min-w-fit flex items-center justify-center gap-1"
          @click="$emit('details')"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"/>
          </svg>
          Detalhes
        </Button>
        <Button
          v-if="['queued', 'running'].includes(job.status)"
          variant="secondary"
          size="sm"
          class="flex-1 min-w-fit flex items-center justify-center gap-1"
          @click="$emit('pause')"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5.75 1.5H3.5a1.5 1.5 0 00-1.5 1.5v14a1.5 1.5 0 001.5 1.5h2.25a1.5 1.5 0 001.5-1.5V3a1.5 1.5 0 00-1.5-1.5zm8.5 0h-2.25a1.5 1.5 0 00-1.5 1.5v14a1.5 1.5 0 001.5 1.5h2.25a1.5 1.5 0 001.5-1.5V3a1.5 1.5 0 00-1.5-1.5z"/>
          </svg>
          Pausar
        </Button>
        <Button
          v-if="['paused', 'failed'].includes(job.status)"
          variant="success"
          size="sm"
          class="flex-1 min-w-fit flex items-center justify-center gap-1"
          @click="$emit('resume')"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
          </svg>
          Retomar
        </Button>
        <Button
          v-if="['queued', 'running', 'paused'].includes(job.status)"
          variant="danger"
          size="sm"
          class="flex-1 min-w-fit flex items-center justify-center gap-1 btn-translucent"
          @click="$emit('cancel')"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
          Cancelar
        </Button>
      </div>

      <!-- Error Message -->
      <div v-if="job.last_error" class="mt-2 p-3 bg-gradient-to-r from-red-500/20 to-red-600/20 border border-red-500/50 rounded-lg text-xs text-red-200">
        <div class="flex gap-2">
          <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          <span>{{ job.last_error }}</span>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup>
import { defineProps } from 'vue'
import Card from './Card.vue'
import Button from './Button.vue'
import ProgressBar from './ProgressBar.vue'
import { useDownloadStore } from '../stores/download'
import { formatBytes, formatSpeed, calculateETA, calculateSpeedMultiplier, getStatusColor, getStatusLabel } from '../utils/format'

defineProps({
  job: {
    type: Object,
    required: true,
    validator: (val) => val && typeof val === 'object' && val.id !== undefined
  }
})

defineEmits(['pause', 'resume', 'cancel', 'details'])

const downloadStore = useDownloadStore()
</script>
