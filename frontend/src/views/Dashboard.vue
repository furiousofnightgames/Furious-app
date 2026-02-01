<template>
  <div class="space-y-6">
    <!-- Main Stats with SVG Icons -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="p-4 bg-gradient-to-br from-sky-50 dark:from-sky-900/30 to-sky-50/50 dark:to-sky-900/10 rounded-lg border border-sky-200 dark:border-sky-500/20 hover:border-sky-300 dark:hover:border-sky-500/50 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10">
            <DashboardIcon type="speed" />
          </div>
          <h3 class="text-sm font-semibold text-sky-700 dark:text-sky-400">Velocidade</h3>
        </div>
        <div class="flex flex-col">
          <p class="text-2xl font-bold text-sky-600 dark:text-sky-300">{{ formatMbps(downloadStore.totalSpeed) }}</p>
          <p class="text-xs font-mono text-sky-500/60">{{ formatSpeed(downloadStore.totalSpeed) }}</p>
        </div>
      </div>

      <div class="p-4 bg-gradient-to-br from-violet-50 dark:from-violet-900/30 to-violet-50/50 dark:to-violet-900/10 rounded-lg border border-violet-200 dark:border-violet-500/20 hover:border-violet-300 dark:hover:border-violet-500/50 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10">
            <DashboardIcon type="progress" />
          </div>
          <h3 class="text-sm font-semibold text-violet-700 dark:text-violet-400">Progresso Total</h3>
        </div>
        <p class="text-2xl font-bold text-violet-600 dark:text-violet-300">{{ downloadStore.totalProgress }}%</p>
      </div>

      <div class="p-4 bg-gradient-to-br from-blue-50 dark:from-blue-900/30 to-blue-50/50 dark:to-blue-900/10 rounded-lg border border-blue-200 dark:border-blue-500/20 hover:border-blue-300 dark:hover:border-blue-500/50 transition">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10">
            <DashboardIcon type="downloads" />
          </div>
          <h3 class="text-sm font-semibold text-blue-700 dark:text-blue-400">Downloads Ativos</h3>
        </div>
        <p class="text-2xl font-bold text-blue-600 dark:text-blue-300">{{ downloadStore.activeDownloads.length }}</p>
      </div>

      <div class="p-4 bg-gradient-to-br" :class="downloadStore.isConnected ? 'from-emerald-50 dark:from-emerald-900/30 to-emerald-50/50 dark:to-emerald-900/10 border-emerald-200 dark:border-emerald-500/20 hover:border-emerald-300 dark:hover:border-emerald-500/50' : 'from-rose-50 dark:from-rose-900/30 to-rose-50/50 dark:to-rose-900/10 border-rose-200 dark:border-rose-500/20 hover:border-rose-300 dark:hover:border-rose-500/50'" >
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10">
            <DashboardIcon type="connection" :isConnected="downloadStore.isConnected" />
          </div>
          <h3 :class="downloadStore.isConnected ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-700 dark:text-rose-400'" class="text-sm font-semibold">Status</h3>
        </div>
        <p :class="downloadStore.isConnected ? 'text-emerald-600 dark:text-emerald-300' : 'text-rose-600 dark:text-rose-300'" class="text-2xl font-bold">{{ downloadStore.isConnected ? 'Online' : 'Offline' }}</p>
      </div>
    </div>

    <!-- Overall Progress -->
    <Card v-if="downloadStore.activeDownloads.length > 0">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-6 h-6">
          <DashboardIcon type="progress" />
        </div>
        <h2 class="text-lg font-bold text-sky-600 dark:text-sky-400">Progresso Geral</h2>
      </div>
      <div class="flex justify-between items-center mb-2">
        <p class="text-slate-600 dark:text-slate-400 font-medium">
          {{ downloadStore.totalProgress }}% 
          <span v-if="downloadStore.totalSpeed > 0" class="text-xs text-emerald-500 dark:text-emerald-400 ml-2 animate-pulse inline-flex items-center gap-1">
            ⚡ {{ formatSpeed(downloadStore.totalSpeed) }}
            <span class="opacity-80 text-[10px]">({{ formatMbps(downloadStore.totalSpeed) }})</span>
          </span>
        </p>
        <p class="text-sm text-slate-500 dark:text-slate-500">{{ formatBytes(totalDownloaded) }} / {{ formatBytes(totalSize) }}</p>
      </div>
      <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3">
        <div 
          class="bg-gradient-to-r from-sky-500 via-violet-500 to-rose-500 h-3 rounded-full transition-all"
          :style="{ width: `${Math.min(downloadStore.totalProgress, 100)}%` }"
        />
      </div>
    </Card>

    <!-- Active Downloads Summary -->
    <Card v-if="downloadStore.activeDownloads.length > 0">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-6 h-6">
          <DashboardIcon type="active" />
        </div>
        <h2 class="text-lg font-bold text-sky-600 dark:text-sky-400">Downloads Ativos</h2>
      </div>
      <div class="space-y-3">
        <div 
          v-for="job in downloadStore.activeDownloads.slice(0, 3)" 
          :key="job.id"
          class="p-3 bg-slate-50 dark:bg-slate-800/50 rounded border border-slate-200 dark:border-slate-700/50 hover:border-sky-300 dark:hover:border-sky-500/50 transition"
        >
          <div class="flex justify-between items-center mb-2">
            <p class="font-semibold text-slate-900 dark:text-slate-100 truncate">{{ job.name }}</p>
            <span class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{{ downloadStore.formatProgress(Math.min(job.progress, 100)) }}%</span>
          </div>
          <div class="w-full bg-slate-300 dark:bg-slate-600 rounded-full h-1.5 mb-2">
            <div 
              class="bg-gradient-to-r from-sky-500 to-violet-500 h-1.5 rounded-full"
              :style="{ width: `${Math.min(job.progress, 100)}%` }"
            />
          </div>
          <div class="flex justify-between text-xs text-slate-600 dark:text-slate-400">
            <span>{{ formatBytes(job.downloaded) }} {{ (job.size || job.total) ? '/ ' + formatBytes(job.size || job.total) : '(desconhecido)' }}</span>
            <div class="flex items-center gap-1.5">
              <span class="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-1.5 py-0.5 rounded">{{ formatSpeed(job.speed) }}</span>
              <span class="text-[9px] text-slate-400/80 uppercase tracking-wider">{{ formatMbps(job.speed) }}</span>
            </div>
          </div>
        </div>
        
        <router-link v-if="downloadStore.activeDownloads.length > 3" to="/downloads">
          <Button variant="outline" class="w-full">
            Ver Todos os Downloads ({{ downloadStore.activeDownloads.length }})
          </Button>
        </router-link>
      </div>
    </Card>

    <!-- Quick Actions -->
    <Card>
      <div class="flex items-center gap-2 mb-4">
        <div class="w-6 h-6">
          <DashboardIcon type="speed" />
        </div>
        <h2 class="text-lg font-bold text-purple-400">Ações Rápidas</h2>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
        <!-- Fontes JSON - Laranja -->
        <router-link to="/sources">
          <div class="p-3 bg-gradient-to-br from-amber-900/30 to-orange-900/10 rounded-lg border border-amber-500/40 hover:border-amber-500/70 hover:shadow-lg hover:shadow-amber-500/20 transition cursor-pointer text-center">
            <div class="w-7 h-7 mx-auto mb-1.5">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
                <defs>
                  <linearGradient id="sourceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color: #f59e0b" />
                    <stop offset="100%" style="stop-color: #d97706" />
                  </linearGradient>
                </defs>
                <!-- Círculo externo pulsante -->
                <circle cx="12" cy="12" r="10" stroke="url(#sourceGrad)" stroke-width="1" fill="none" opacity="0.4" class="animate-pulse"/>
                <!-- Estrela interna centralizada e menor -->
                <path d="M12 8.5L13.8 11.5H17.2L14.7 13.5L15.5 16.5L12 14.4L8.5 16.5L9.3 13.5L6.8 11.5H10.2L12 8.5Z" 
                      fill="url(#sourceGrad)" opacity="0.7" class="animate-pulse" style="animation-delay: 0.1s"/>
              </svg>
            </div>
            <p class="font-bold text-amber-300 text-sm">Fontes JSON</p>
          </div>
        </router-link>

        <!-- Novo Download - Verde -->
        <router-link to="/new-download">
          <div class="p-3 bg-gradient-to-br from-emerald-900/30 to-green-900/10 rounded-lg border border-emerald-500/40 hover:border-emerald-500/70 hover:shadow-lg hover:shadow-emerald-500/20 transition cursor-pointer text-center">
            <div class="w-7 h-7 mx-auto mb-1.5">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
                <defs>
                  <linearGradient id="newGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color: #10b981" />
                    <stop offset="100%" style="stop-color: #059669" />
                  </linearGradient>
                </defs>
                <circle cx="12" cy="12" r="10" stroke="url(#newGrad)" stroke-width="1.5" fill="none" opacity="0.6" class="animate-pulse" style="animation-delay: 0.2s"/>
                <line x1="10" y1="10" x2="14" y2="14" stroke="url(#newGrad)" stroke-width="2" stroke-linecap="round" class="animate-pulse" style="animation-delay: 0.1s"/>
                <line x1="14" y1="10" x2="10" y2="14" stroke="url(#newGrad)" stroke-width="2" stroke-linecap="round" class="animate-pulse" style="animation-delay: 0.2s"/>
              </svg>
            </div>
            <p class="font-bold text-emerald-300 text-sm">Novo Download</p>
          </div>
        </router-link>

        <!-- Histórico - Azul -->
        <router-link to="/downloads">
          <div class="p-3 bg-gradient-to-br from-blue-900/30 to-cyan-900/10 rounded-lg border border-blue-500/40 hover:border-blue-500/70 hover:shadow-lg hover:shadow-blue-500/20 transition cursor-pointer text-center">
            <div class="w-7 h-7 mx-auto mb-1.5">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
                <defs>
                  <linearGradient id="histGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color: #3b82f6" />
                    <stop offset="100%" style="stop-color: #0ea5e9" />
                  </linearGradient>
                </defs>
                <line x1="12" y1="2" x2="12" y2="14" stroke="url(#histGrad)" stroke-width="2.5" stroke-linecap="round" class="animate-bounce"/>
                <polyline points="18,12 12,18 6,12" stroke="url(#histGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="animate-bounce" style="animation-delay: 0.1s"/>
                <rect x="2" y="20" width="20" height="2" fill="url(#histGrad)" rx="1" opacity="0.8"/>
              </svg>
            </div>
            <p class="font-bold text-blue-300 text-sm">Histórico</p>
          </div>
        </router-link>

        <!-- Biblioteca - Sky -->
        <router-link to="/library">
          <div class="p-3 bg-gradient-to-br from-sky-50 dark:from-sky-900/30 to-sky-50/50 dark:to-sky-900/10 rounded-lg border border-sky-200 dark:border-sky-500/40 hover:border-sky-300 dark:hover:border-sky-500/70 hover:shadow-lg hover:shadow-sky-500/20 transition cursor-pointer text-center">
            <div class="w-7 h-7 mx-auto mb-1.5">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
                <defs>
                  <linearGradient id="libGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color: #0ea5e9" />
                    <stop offset="100%" style="stop-color: #0284c7" />
                  </linearGradient>
                </defs>
                <path d="M6 4h12a2 2 0 012 2v14H6a2 2 0 01-2-2V6a2 2 0 012-2z" stroke="url(#libGrad)" stroke-width="1.5" opacity="0.9"/>
                <path d="M8 8h8M8 12h8M8 16h6" stroke="url(#libGrad)" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
              </svg>
            </div>
            <p class="font-bold text-sky-600 dark:text-sky-300 text-sm">Biblioteca</p>
          </div>
        </router-link>

        <!-- Reconectar - Violet -->
        <button @click="downloadStore.connectWebSocket(true)" class="p-3 bg-gradient-to-br from-violet-50 dark:from-violet-900/30 to-violet-50/50 dark:to-violet-900/10 rounded-lg border border-violet-200 dark:border-violet-500/40 hover:border-violet-300 dark:hover:border-violet-500/70 hover:shadow-lg hover:shadow-violet-500/20 transition cursor-pointer text-center w-full">
          <div class="w-7 h-7 mx-auto mb-1.5">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
              <defs>
                <linearGradient id="connGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" :style="`stop-color: ${downloadStore.isConnected ? '#8b5cf6' : '#f43f5e'}`" />
                  <stop offset="100%" :style="`stop-color: ${downloadStore.isConnected ? '#a78bfa' : '#f87171'}`" />
                </linearGradient>
              </defs>
              <circle cx="12" cy="12" r="2" fill="url(#connGrad)" class="animate-pulse"/>
              <circle cx="12" cy="12" r="6" stroke="url(#connGrad)" stroke-width="1" fill="none" class="animate-ping" style="animation-duration: 1.5s"/>
              <circle cx="12" cy="12" r="10" stroke="url(#connGrad)" stroke-width="0.5" fill="none" opacity="0.4"/>
            </svg>
          </div>
          <p class="font-bold text-sm" :class="downloadStore.isConnected ? 'text-purple-300' : 'text-red-300'">Reconectar</p>
        </button>
      </div>
    </Card>

    <!-- Recently Completed -->
    <Card v-if="downloadStore.completedDownloads.length > 0">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-6 h-6">
          <DashboardIcon type="completed" />
        </div>
        <h2 class="text-lg font-bold text-green-400">Concluídos Recentemente</h2>
      </div>
      <div class="space-y-2">
        <div 
          v-for="job in downloadStore.completedDownloads.slice(0, 5)" 
          :key="job.id"
          class="group relative p-3 bg-gradient-to-br from-green-500/10 via-emerald-500/5 to-transparent rounded-lg border border-green-500/40 hover:border-green-500/70 hover:shadow-lg hover:shadow-green-500/20 transition-all duration-300"
        >
          <!-- Brilho de hover -->
          <div class="absolute inset-0 bg-gradient-to-r from-green-500/0 via-green-500/10 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          
          <!-- Conteúdo -->
          <div class="relative z-10">
            <!-- Primeira linha: Nome com ícone + Tamanho -->
            <div class="flex justify-between items-start gap-2 mb-1.5">
              <div class="flex items-start gap-2 flex-1 min-w-0">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <p class="font-semibold text-green-300 text-sm truncate">{{ job.item_name || job.name }}</p>
              </div>
              <span class="text-xs font-bold text-cyan-300 flex-shrink-0 px-2 py-1 bg-cyan-500/20 rounded">{{ formatBytes((job.size || job.total || job.downloaded || 0)) }}</span>
            </div>

            <!-- Segunda linha: Datas e hora compactas com visual melhor -->
            <div class="flex justify-between items-center text-xs gap-2">
              <div class="flex items-center gap-1 text-slate-400">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-3 h-3 text-green-400/70">
                  <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>
                </svg>
                <span class="font-mono">{{ formatShortDate(job.created_at) }}</span>
              </div>
              <div class="h-4 w-px bg-slate-600/30" />
              <div class="flex items-center gap-1 text-slate-400">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-3 h-3 text-green-400/70">
                  <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/>
                </svg>
                <span class="font-mono">{{ formatShortDate(job.updated_at || job.completed_at) }}</span>
              </div>
              <div class="h-4 w-px bg-slate-600/30" />
              <span class="text-green-400 font-bold">{{ formatBytes(job.size || job.total || job.downloaded || 0) }}</span>
            </div>
          </div>

          <!-- Barra de progresso sutil no fundo -->
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-slate-900/30 rounded-b-lg overflow-hidden pointer-events-none">
            <div 
              class="h-full bg-gradient-to-r from-green-500 via-emerald-400 to-green-500 transition-all duration-300"
              style="width: 100%"
            />
          </div>
        </div>
        
        <router-link v-if="downloadStore.completedDownloads.length > 5" to="/downloads">
          <Button variant="outline" size="sm" class="w-full mt-2 btn-translucent">
            Ver Todos ({{ downloadStore.completedDownloads.length }})
          </Button>
        </router-link>
      </div>
    </Card>

    <!-- Failed Downloads Alert -->
    <Card v-if="downloadStore.failedDownloads.length > 0" class="border border-red-500/30 bg-red-900/10">
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 flex-shrink-0 mt-0.5">
          <DashboardIcon type="failed" />
        </div>
        <div class="flex-1">
          <h3 class="font-bold text-red-400 mb-2">{{ downloadStore.failedDownloads.length }} Download(s) com Erro</h3>
          <p class="text-sm text-gray-400 mb-3">Clique em um para tentar novamente ou deletar.</p>
          <router-link to="/downloads">
            <Button variant="danger" size="sm">Ver Downloads com Erro</Button>
          </router-link>
        </div>
      </div>
    </Card>

    <!-- Info Section -->
    <Card class="bg-purple-900/20 border border-purple-500/30">
      <div class="flex items-start gap-3">
        <div class="w-6 h-6 flex-shrink-0 mt-0.5">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#a855f7" stroke-width="1.5"/>
            <text x="12" y="15" text-anchor="middle" fill="#a855f7" font-size="12" font-weight="bold">i</text>
          </svg>
        </div>
        <div>
          <h3 class="font-bold text-purple-300 mb-2">Como Usar</h3>
          <ol class="text-sm text-gray-400 space-y-1 list-decimal list-inside">
            <li>Acesse <strong>Fontes JSON</strong> e adicione um link JSON</li>
            <li>Escolha um item da fonte para baixar</li>
            <li>Acompanhe o progresso no <strong>Histórico</strong></li>
            <li>Pause, retome ou cancele downloads conforme necessário</li>
            <li>Limpe o histórico de concluídos ou com erro</li>
          </ol>
        </div>
      </div>
    </Card>

    <!-- Promotional Footer -->
    <div class="mt-8 relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 border border-slate-700/50 shadow-2xl">
      <!-- Glow Effects -->
      <div class="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 -ml-20 -mb-20 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl pointer-events-none"></div>

      <div class="relative z-10 p-8 flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
        <div class="space-y-2">
          <h3 class="text-xl font-bold bg-gradient-to-r from-cyan-300 via-white to-purple-200 bg-clip-text text-transparent">
            O Launcher Definitivo para sua Coleção
          </h3>
          <p class="text-slate-400 max-w-2xl text-sm leading-relaxed">
            Uma plataforma robusta, gratuita e desenhada para entusiastas. Conheça todos os recursos e tecnologias que elevam sua experiência.
          </p>
        </div>

        <router-link to="/about" class="flex-shrink-0">
          <button class="group relative px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl border border-slate-600 hover:border-cyan-500/50 transition-all duration-300 shadow-lg hover:shadow-cyan-500/20 overflow-hidden">
            <span class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></span>
            <span class="relative flex items-center gap-2">
              <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Sobre o Projeto
            </span>
          </button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useDownloadStore } from '../stores/download'
import Card from '../components/Card.vue'
import Button from '../components/Button.vue'
import DashboardIcon from '../components/icons/DashboardIcons.vue'
import { formatBytes, formatSpeed, formatMbps } from '../utils/format'

const downloadStore = useDownloadStore()

onMounted(() => {
  downloadStore.fetchJobs()
})

const totalDownloaded = computed(() => {
  return downloadStore.activeDownloads.reduce((sum, job) => sum + (job.downloaded || 0), 0)
})

const totalSize = computed(() => {
  return downloadStore.activeDownloads.reduce((sum, job) => sum + (job.size || 0), 0)
})

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR')
  } catch {
    return dateStr
  }
}

function formatShortDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR', { 
      month: '2-digit', 
      day: '2-digit', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-0.5rem);
  }
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-bounce {
  animation: bounce 1s infinite;
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}
</style>
