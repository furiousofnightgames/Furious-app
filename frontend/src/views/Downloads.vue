<template>
  <div class="space-y-6">
    <!-- Header Stats com SVGs animados -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <!-- Total -->
      <StatCard :title="`Total`" :value="activeJobsCount" color="cyan">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
          <defs>
            <linearGradient id="totalGrad" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" style="stop-color: #0ea5e9" />
              <stop offset="100%" style="stop-color: #0ea5e9" />
            </linearGradient>
          </defs>
          <!-- Barra 1 (esquerda) -->
          <rect x="4" y="12" width="3" height="10" fill="url(#totalGrad)" rx="1" class="animate-bounce" style="animation-delay: 0s"/>
          <!-- Barra 2 (meio-esquerda) -->
          <rect x="9" y="8" width="3" height="14" fill="url(#totalGrad)" rx="1" class="animate-bounce" style="animation-delay: 0.1s"/>
          <!-- Barra 3 (meio-direita) -->
          <rect x="14" y="4" width="3" height="18" fill="url(#totalGrad)" rx="1" class="animate-bounce" style="animation-delay: 0.2s"/>
          <!-- Barra 4 (direita) -->
          <rect x="19" y="10" width="3" height="12" fill="url(#totalGrad)" rx="1" class="animate-bounce" style="animation-delay: 0.3s"/>
        </svg>
      </StatCard>

      <!-- Baixando -->
      <StatCard :title="`Baixando`" :value="downloadStore.activeDownloads.length" color="green">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
          <defs>
            <linearGradient id="downloadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #10b981" />
              <stop offset="100%" style="stop-color: #059669" />
            </linearGradient>
          </defs>
          <!-- Download arrow animada -->
          <line x1="12" y1="2" x2="12" y2="14" stroke="url(#downloadGrad)" stroke-width="2" stroke-linecap="round" class="animate-pulse"/>
          <polyline points="8,10 12,14 16,10" fill="none" stroke="url(#downloadGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="animate-bounce"/>
          <!-- Container -->
          <rect x="3" y="16" width="18" height="4" fill="url(#downloadGrad)" opacity="0.2" stroke="url(#downloadGrad)" stroke-width="1.5" rx="1"/>
        </svg>
      </StatCard>

      <!-- Pausado -->
      <StatCard :title="`Pausado`" :value="pausedCount" color="yellow">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
          <defs>
            <linearGradient id="pauseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #eab308" />
              <stop offset="100%" style="stop-color: #ca8a04" />
            </linearGradient>
          </defs>
          <!-- Barras de pausa -->
          <rect x="7" y="4" width="2.5" height="16" fill="url(#pauseGrad)" rx="1" class="animate-pulse"/>
          <rect x="14.5" y="4" width="2.5" height="16" fill="url(#pauseGrad)" rx="1" class="animate-pulse" style="animation-delay: 0.3s"/>
        </svg>
      </StatCard>

      <!-- Concluído -->
      <StatCard :title="`Concluído`" :value="downloadStore.completedDownloads.length" color="green">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
          <defs>
            <linearGradient id="completeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #10b981" />
              <stop offset="100%" style="stop-color: #059669" />
            </linearGradient>
          </defs>
          <!-- Caixa externa -->
          <rect x="4" y="4" width="16" height="16" fill="none" stroke="url(#completeGrad)" stroke-width="1.5" rx="2"/>
          <!-- Preenchimento animado -->
          <rect x="4" y="4" width="16" height="16" fill="url(#completeGrad)" opacity="0.1" rx="2" class="animate-pulse"/>
          <!-- Checkmark com animação de desenho -->
          <g class="animate-bounce" style="animation-duration: 0.8s">
            <polyline points="7,12 11,16 17,8" fill="none" stroke="url(#completeGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </g>
        </svg>
      </StatCard>

      <!-- Erro -->
      <StatCard :title="`Erro`" :value="downloadStore.failedDownloads.length" color="red">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
          <defs>
            <linearGradient id="errorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #ef4444" />
              <stop offset="100%" style="stop-color: #dc2626" />
            </linearGradient>
          </defs>
          <!-- Círculo externo -->
          <circle cx="12" cy="12" r="9" fill="none" stroke="url(#errorGrad)" stroke-width="1.5"/>
          <!-- X animado -->
          <line x1="8" y1="8" x2="16" y2="16" stroke="url(#errorGrad)" stroke-width="2.5" stroke-linecap="round" class="animate-pulse"/>
          <line x1="16" y1="8" x2="8" y2="16" stroke="url(#errorGrad)" stroke-width="2.5" stroke-linecap="round" class="animate-pulse" style="animation-delay: 0.2s"/>
        </svg>
      </StatCard>
    </div>

    <Card class="bg-gradient-to-r from-cyan-900/20 to-purple-900/20 border border-cyan-500/20">
      <div class="flex items-start gap-3">
        <div class="mt-0.5">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-cyan-400">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
        </div>
        <div class="flex-1">
          <p class="text-sm text-gray-200">
            Alguns downloads podem levar alguns segundos no início para preparar a sessão, obter metadados e realizar a descoberta de peers antes de atingir a velocidade ideal.
          </p>
          <p class="text-xs text-gray-400 mt-1">
            Aguarde essa etapa inicial. Após a sincronização, o download tende a estabilizar e manter desempenho total e contínuo.
          </p>
        </div>
      </div>
    </Card>

    <!-- Active Downloads -->
    <Card v-if="downloadStore.activeDownloads.length > 0">
      <div class="flex items-center gap-2 mb-4">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
          <defs>
            <linearGradient id="activeDownloadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #0ea5e9" />
              <stop offset="100%" style="stop-color: #0ea5e9" />
            </linearGradient>
          </defs>
          <line x1="12" y1="2" x2="12" y2="14" stroke="url(#activeDownloadGrad)" stroke-width="2" stroke-linecap="round"/>
          <polyline points="8,10 12,14 16,10" fill="none" stroke="url(#activeDownloadGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="3" y="16" width="18" height="4" fill="url(#activeDownloadGrad)" opacity="0.2" stroke="url(#activeDownloadGrad)" stroke-width="1.5" rx="1"/>
        </svg>
        <h2 class="text-xl font-bold text-cyan-400">Downloads Ativos</h2>
      </div>
      <div class="space-y-3">
        <div v-for="job in downloadStore.activeDownloads" :key="job.id">
          <div class="flex justify-between items-start mb-2">
            <div class="flex-1">
              <p class="font-semibold text-cyan-300 break-words">{{ job.name || job.item_name || 'Download' }}</p>
              <p class="text-xs text-gray-500">
                <template v-if="job.status === 'queued'">
                  <span class="text-amber-400 font-medium">⏳ Aguardando</span>
                </template>
                <template v-else>
                  {{ job.downloaded ? formatBytes(job.downloaded) : '—' }} {{ job.total ? '/ ' + formatBytes(job.total) : '(desc.)' }}
                </template>
              </p>
              <p v-if="job.phase_label" class="text-xs text-cyan-400 mt-1">
                <span>{{ job.phase_label }}</span>
                <template v-if="job.phase_progress !== null && job.phase_progress !== undefined">
                  <span class="text-cyan-300 font-semibold"> ({{ downloadStore.formatProgress(job.phase_progress) }}%)</span>
                </template>
              </p>
            </div>
            <span class="text-sm font-bold text-green-400">
              <template v-if="job.progress !== null && job.progress !== undefined">{{ downloadStore.formatProgress(Math.min(job.progress, 100)) }}%</template>
              <template v-else-if="job.status === 'running'">Em andamento</template>
              <template v-else>0%</template>
            </span>
          </div>
          <div v-if="spaceWarnings[job.id] || job.status_reason === 'insufficient_space'" class="mb-2 p-2 bg-rose-500/20 border border-rose-500/40 rounded text-[11px] text-rose-300 font-bold animate-pulse flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4"><path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
             {{ spaceWarnings[job.id] || '⚠️ Download pausado: Espaço insuficiente em disco.' }}
          </div>
          <div class="w-full bg-gray-900 rounded-full h-2 mb-2">
            <div 
              class="bg-gradient-to-r from-cyan-500 to-purple-500 h-2 rounded-full transition-all"
              :style="{ width: job.progress ? `${Math.min(job.progress, 100)}%` : (job.status === 'running' ? '6%' : '0%') }"
            />
          </div>
          <div class="flex items-center text-xs text-gray-400 mb-3">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="px-2 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-semibold tracking-wide inline-flex items-center">
                <span>{{ formatSpeed(job.speed) }}</span>
                <span class="ml-2 inline-flex items-end gap-0.5 opacity-80">
                  <span class="w-0.5 h-2 bg-cyan-300 rounded-sm animate-pulse" style="animation-delay: 0ms"></span>
                  <span class="w-0.5 h-3 bg-cyan-300 rounded-sm animate-pulse" style="animation-delay: 120ms"></span>
                  <span class="w-0.5 h-1.5 bg-cyan-300 rounded-sm animate-pulse" style="animation-delay: 240ms"></span>
                </span>
              </span>
              <span class="px-2 py-1 rounded-md bg-purple-500/10 border border-purple-500/30 text-purple-300 font-semibold tracking-wide inline-flex items-center">
                <span>{{ formatMbps(job.speed) }}</span>
                <span class="ml-2 inline-flex items-end gap-0.5 opacity-80">
                  <span class="w-0.5 h-2 bg-purple-300 rounded-sm animate-pulse" style="animation-delay: 60ms"></span>
                  <span class="w-0.5 h-3 bg-purple-300 rounded-sm animate-pulse" style="animation-delay: 180ms"></span>
                  <span class="w-0.5 h-1.5 bg-purple-300 rounded-sm animate-pulse" style="animation-delay: 300ms"></span>
                </span>
              </span>
              <span class="px-2 py-1 rounded-md bg-fuchsia-500/10 border border-fuchsia-500/30 text-fuchsia-300 font-semibold tracking-wide inline-flex items-center gap-1">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="w-4 h-4">
                  <circle cx="12" cy="12" r="9" stroke-width="2" />
                  <path d="M12 7v5l3 2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span>{{ calculateETA(job.downloaded || 0, job.total || 0, job.speed || 0) || '—' }}</span>
              </span>
            </div>
          </div>
          <!-- Peers/Seeders Info -->
          <div v-if="job.peers !== undefined || job.seeders !== undefined" class="flex gap-4 text-xs text-gray-400 mb-3 pb-2 border-b border-gray-800">
            <div class="flex items-center gap-1">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="w-4 h-4 text-purple-400">
                <circle cx="12" cy="12" r="1"></circle>
                <path d="M12 8a4 4 0 0 1 4 4"></path>
                <path d="M12 4a8 8 0 0 1 8 8"></path>
              </svg>
              <span class="text-purple-300 font-semibold">Peers: <span class="text-gray-400">{{ job.peers || 0 }}</span></span>
            </div>
            <div class="flex items-center gap-1">
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-green-400">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
              </svg>
              <span class="text-green-300 font-semibold">Seeds: <span class="text-gray-400">{{ job.seeders || 0 }}</span></span>
            </div>
          </div>
          <div class="flex gap-2 flex-wrap">
            <Button
              @click="pauseDownload(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 min-w-24 border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/10 hover:border-yellow-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
              </svg>
              Pausar
            </Button>
            <Button 
              @click="openDetails(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 min-w-24 border-blue-500/50 text-blue-400 hover:bg-blue-500/10 hover:border-blue-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <circle cx="12" cy="12" r="1"/>
                <path d="M12 5C7.58 5 3.73 7.61 1.97 11.38 3.73 15.16 7.58 17.77 12 17.77s8.27-2.61 10.03-6.39C20.27 7.61 16.42 5 12 5m0 12.5c-2.49 0-4.5-2.01-4.5-4.5s2.01-4.5 4.5-4.5 4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5z" fill="currentColor"/>
              </svg>
              Detalhes
            </Button>
            <Button 
              @click="cancelDownload(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 min-w-24 border-orange-500/50 text-orange-400 hover:bg-orange-500/10 hover:border-orange-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
              Cancelar
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Paused Downloads -->
    <Card v-if="pausedJobs.length > 0" class="bg-gradient-to-br from-yellow-900/30 to-orange-900/20 border border-yellow-500/30 hover:border-yellow-500/50 transition-all">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center shadow-lg shadow-yellow-500/50">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h2 class="text-2xl font-bold text-yellow-300">Downloads Pausados</h2>
          <p class="text-sm text-yellow-200/60">{{ pausedJobs.length }} download{{ pausedJobs.length !== 1 ? 's' : '' }} aguardando</p>
        </div>
      </div>
      <div class="space-y-4">
        <div v-for="job in pausedJobs" :key="job.id" class="p-4 bg-gradient-to-r from-gray-900/50 to-gray-900/30 rounded-lg border border-yellow-500/20 hover:border-yellow-500/40 transition-all">
          <div class="flex justify-between items-start mb-3">
            <div class="flex-1">
              <p class="font-semibold text-yellow-300 break-words">{{ job.name || job.item_name }}</p>
              <p class="text-xs text-gray-400">
                {{ formatBytes(job.downloaded || 0) }} / {{ job.size ? formatBytes(job.size) : '(tam. desconhecido)' }}
              </p>
              <div v-if="job.status_reason === 'insufficient_space'" class="mt-1 text-[10px] text-rose-300/80 font-medium">
                Metadados resolvidos: Tamanho real ({{ formatBytes(job.size) }}) excedeu o espaço livre ({{ formatBytes(job.free_space_at_pause || 0) }}).
              </div>
            </div>
            <span class="text-sm font-bold text-yellow-400 bg-yellow-500/20 px-2 py-1 rounded">{{ downloadStore.formatProgress(Math.min(job.progress, 100)) }}%</span>
          </div>
          <div v-if="job.status_reason === 'insufficient_space'" class="mb-3 p-2 bg-rose-500/20 border border-rose-500/40 rounded text-[11px] text-rose-300 font-bold flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 animate-pulse"><path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
            BLOQUEADO: Espaço insuficiente no disco rígido.
          </div>
          <div class="w-full bg-gray-900/70 rounded-full h-2 mb-4 overflow-hidden">
            <div 
              class="bg-gradient-to-r from-yellow-500 to-orange-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${Math.min(job.progress, 100)}%` }"
            />
          </div>
          <div class="flex gap-2">
            <Button 
              @click="resumeDownload(job.id)"
              variant="primary"
              size="sm"
              class="flex-1 flex items-center justify-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Continuar</span>
            </Button>
            <Button 
              @click="openDetails(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 border-blue-500/50 text-blue-400 hover:bg-blue-500/10 hover:border-blue-500 flex items-center justify-center gap-1 btn-translucent"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Detalhes</span>
            </Button>
            <Button 
              @click="cancelDownload(job.id)"
              variant="danger"
              size="sm"
              class="flex-1 flex items-center justify-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Cancelar</span>
            </Button>
            <Button 
              @click="openDeleteFileDialog(job.id)"
              variant="danger"
              size="sm"
              class="flex-1"
            >
              🗑️ Deletar Arquivo
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Completed Downloads -->
    <Card v-if="downloadStore.completedDownloads.length > 0">
      <div class="flex items-center justify-between gap-2 mb-4">
        <div class="flex items-center gap-2">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
            <defs>
              <linearGradient id="completedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color: #10b981" />
                <stop offset="100%" style="stop-color: #059669" />
              </linearGradient>
            </defs>
            <circle cx="12" cy="12" r="9" fill="none" stroke="url(#completedGrad)" stroke-width="1.5"/>
            <polyline points="7,12 11,16 17,8" fill="none" stroke="url(#completedGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h2 class="text-xl font-bold text-green-400">Downloads Concluídos</h2>
        </div>
        <button 
          @click="forceCheckSetups"
          title="Recarregar Instaladores"
          class="p-2 text-gray-500 hover:text-cyan-400 hover:bg-cyan-500/10 rounded-lg transition-colors group"
        >
          <svg class="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      <div class="space-y-3">
        <div v-for="job in downloadStore.completedDownloads" :key="job.id" class="p-4 bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-lg hover:border-green-500/50 transition-colors">
          <div class="flex justify-between items-start gap-3 mb-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-green-400">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <p class="font-semibold text-green-300 break-words">{{ job.name || job.item_name }}</p>
              </div>
              <div class="flex items-center gap-4 text-sm">
                <span class="text-gray-400">
                  Tamanho:
                  <span class="text-green-300 font-medium">{{ formatBytes(job.size) }}</span>
                </span>
                <span class="text-gray-400">
                  Status:
                  <span class="text-green-300 font-medium">{{ job.status === 'completed_cleaned' ? 'Instalado (Arquivos Removidos)' : 'Concluído' }}</span>
                </span>
              </div>
            </div>
            <div class="flex flex-col items-end gap-1">
              <span class="px-3 py-1 bg-green-500/20 text-green-300 text-sm font-bold rounded-full">100%</span>
              <span class="text-xs text-gray-500">Pronto</span>
            </div>
          </div>
          <div class="flex gap-2">
            <Button 
              @click="openCompletedDetails(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 border-blue-500/50 text-blue-400 hover:bg-blue-500/10 hover:border-blue-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <circle cx="12" cy="12" r="1"/>
                <path d="M12 5C7.58 5 3.73 7.61 1.97 11.38 3.73 15.16 7.58 17.77 12 17.77s8.27-2.61 10.03-6.39C20.27 7.61 16.42 5 12 5m0 12.5c-2.49 0-4.5-2.01-4.5-4.5s2.01-4.5 4.5-4.5 4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5z" fill="currentColor"/>
              </svg>
              Detalhes
            </Button>
            <Button 
              @click="openFolder(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 min-w-fit border-green-500/50 text-green-400 hover:bg-green-500/10 hover:border-green-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V6h5.17l2 2H20v10z"/>
              </svg>
              Abrir Pasta
            </Button>
            <Button 
              v-if="foundSetups[job.id]?.found && !job.is_installing && !foundSetups[job.id]?.is_manual"
              @click="runInstaller(job.id)"
              variant="success"
              size="sm"
              class="flex-1 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:via-blue-500 hover:to-indigo-500 shadow-lg shadow-cyan-500/30 flex items-center justify-center gap-2 transform hover:scale-[1.02] active:scale-[0.98] transition-all font-bold"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M13 3h-2v10l-3-3-1.4 1.4L12 16.8l5.4-5.4L16 10l-3 3V3zM5 18v2h14v-2H5z"/>
              </svg>
              {{ job.setup_executed ? 'Instalar (Novamente)' : 'Instalar' }}
            </Button>
            <Button 
              v-if="job.is_installing"
              disabled
              variant="outline"
              size="sm"
              class="flex-1 border-cyan-500 text-cyan-400 bg-cyan-500/5 flex items-center justify-center gap-2 animate-pulse cursor-wait"
            >
              <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Instalando...
            </Button>

            <!-- Botão para Instalação Manual (RuTracker/Online-Fix) -->
            <Button 
              v-if="foundSetups[job.id]?.is_manual && !job.setup_executed && !job.is_installing && !foundSetups[job.id]?.found"
              @click="markAsInstalled(job.id)"
              variant="primary"
              size="sm"
              class="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
              </svg>
              Marcar como Instalado
            </Button>

            <Button 
              v-if="job.status === 'completed' && job.setup_executed && !job.is_installing"
              @click="cleanupInstaller(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 border-amber-500/50 text-amber-400 hover:bg-amber-500/10 hover:border-amber-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M15 4V3H9v1H4v2h1v13c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V6h1V4h-5zM9 17H7V8h2v9zm4 0h-2V8h2v9zm4 0h-2V8h2v9z"/>
              </svg>
              Limpar Instalador
            </Button>
            <Button 
              @click="openDeleteFileDialog(job.id)"
              variant="outline"
              size="sm"
              class="flex-1 border-red-500/50 text-red-400 hover:bg-red-500/10 hover:border-red-500 flex items-center justify-center gap-2 btn-translucent"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
              </svg>
              {{ job.status === 'completed_cleaned' ? 'Remover do Histórico' : 'Remover' }}
            </Button>
          </div>

          <!-- Dica para Instalação Manual (Abaixo dos botões) -->
          <div v-if="foundSetups[job.id]?.is_manual && !job.setup_executed && !job.is_installing" class="mt-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex gap-3 items-start animate-in fade-in slide-in-from-top-1 shadow-inner">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-blue-400 mt-0.5"><path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>
            <div class="space-y-1 flex-1">
              <p class="text-xs font-bold text-blue-200">
                 Instalação Manual: {{ foundSetups[job.id]?.manual_type === 'online-fix' ? 'Online-Fix' : 'Pronto para Rodar' }}
              </p>
              <p class="text-[10px] text-blue-300/80 leading-tight">
                Este item não possui um instalador automático. Abra a pasta, configure os arquivos e, quando terminar, clique no botão <b>Marcar como Instalado</b> para habilitar a limpeza do lixo residual.
              </p>
            </div>
          </div>
        </div>
      </div>
      <Button
        @click="deleteAllCompleted"
        variant="outline"
        class="w-full mt-4 border-amber-500/50 text-amber-400 hover:bg-amber-500/10 hover:border-amber-500 transition-all flex items-center justify-center gap-2 btn-translucent"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
        </svg>
        Limpar Todos Concluídos
      </Button>
    </Card>

    <!-- Failed Downloads -->
    <Card v-if="downloadStore.failedDownloads.length > 0">
      <div class="flex items-center gap-2 mb-4">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
          <defs>
            <linearGradient id="failedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #ef4444" />
              <stop offset="100%" style="stop-color: #dc2626" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="9" fill="none" stroke="url(#failedGrad)" stroke-width="1.5"/>
          <line x1="8" y1="8" x2="16" y2="16" stroke="url(#failedGrad)" stroke-width="2.5" stroke-linecap="round"/>
          <line x1="16" y1="8" x2="8" y2="16" stroke="url(#failedGrad)" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <h2 class="text-xl font-bold text-red-400">Downloads com Erro</h2>
      </div>
      <div class="space-y-3">
        <div v-for="job in downloadStore.failedDownloads" :key="job.id" class="p-4 bg-gradient-to-r from-red-900/20 to-rose-900/20 border border-red-500/30 rounded-lg hover:border-red-500/50 transition-colors">
          <div class="flex justify-between items-start gap-3 mb-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-red-400">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
                <p class="font-semibold text-red-300 break-words">{{ job.name || job.item_name }}</p>
              </div>
              <div class="flex items-center gap-4 text-sm">
                <span class="text-gray-400">
                  Progresso:
                  <span class="text-red-300 font-medium">{{ downloadStore.formatProgress(Math.min(job.progress || 0, 100)) }}%</span>
                </span>
                <span class="text-gray-400">
                  Tamanho:
                  <span class="text-red-300 font-medium">{{ formatBytes(job.downloaded || 0) }} {{ job.total ? '/ ' + formatBytes(job.total) : '' }}</span>
                </span>
              </div>
            </div>
            <div class="flex flex-col items-end gap-1">
              <span class="px-3 py-1 bg-red-500/20 text-red-300 text-sm font-bold rounded-full">Erro</span>
              <Button
                @click="showErrorModal = job.id"
                size="xs"
                class="text-xs px-2 py-1 border-red-500/50 text-red-400 hover:bg-red-500/10 hover:border-red-500"
                variant="outline"
              >
                Ver Log
              </Button>
            </div>
          </div>
          <div class="flex gap-2 flex-wrap">
            <Button 
              @click="retryDownload(job.id)"
              variant="success"
              size="sm"
              class="flex-1 min-w-fit flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
              </svg>
              Tentar Novamente
            </Button>
            <Button 
              @click="openDeleteFileDialog(job.id)"
              variant="danger"
              size="sm"
              class="flex-1 min-w-fit flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
              </svg>
              Remover
            </Button>
          </div>
        </div>
      </div>
      <Button 
        @click="deleteAllFailed"
        variant="danger"
        class="w-full mt-4 border-red-500/50 text-red-400 hover:bg-red-500/10 hover:border-red-500 transition-all flex items-center justify-center gap-2 btn-translucent"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
        </svg>
        Limpar Todos com Erro
      </Button>
    </Card>

    <!-- Canceled Downloads -->
    <Card v-if="downloadStore.canceledDownloads.length > 0">
      <div class="flex items-center gap-2 mb-4">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
          <defs>
            <linearGradient id="canceledGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color: #f59e0b" />
              <stop offset="100%" style="stop-color: #d97706" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="9" fill="none" stroke="url(#canceledGrad)" stroke-width="1.5"/>
          <line x1="8" y1="12" x2="16" y2="12" stroke="url(#canceledGrad)" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <h2 class="text-xl font-bold text-amber-400">Downloads Cancelados</h2>
      </div>
      <div class="space-y-3">
        <div v-for="job in downloadStore.canceledDownloads" :key="job.id" class="p-4 bg-gradient-to-r from-amber-900/20 to-orange-900/20 border border-amber-500/30 rounded-lg hover:border-amber-500/50 transition-colors">
          <div class="flex justify-between items-start gap-3 mb-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-amber-400">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                </svg>
                <p class="font-semibold text-amber-300 break-words">{{ job.name || job.item_name }}</p>
              </div>
              <div class="flex items-center gap-4 text-sm">
                <span class="text-gray-400">
                  Progresso:
                  <span class="text-amber-300 font-medium">{{ downloadStore.formatProgress(Math.min(job.progress || 0, 100)) }}%</span>
                </span>
                <span class="text-gray-400">
                  Tamanho:
                  <span class="text-amber-300 font-medium">{{ formatBytes(job.downloaded || 0) }} {{ job.total ? '/ ' + formatBytes(job.total) : '' }}</span>
                </span>
              </div>
            </div>
            <div class="flex flex-col items-end gap-1">
              <span class="px-3 py-1 bg-amber-500/20 text-amber-300 text-sm font-bold rounded-full">Cancelado</span>
            </div>
          </div>
          <div class="flex gap-2 flex-wrap">
            <Button 
              @click="retryDownload(job.id)"
              variant="primary"
              size="sm"
              :disabled="retryingJobId !== null"
              class="flex-1 min-w-fit flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
              </svg>
              {{ retryingJobId === job.id ? 'Processando...' : 'Tentar de Novo' }}
            </Button>
            <Button 
              @click="openDeleteFileDialog(job.id)"
              variant="danger"
              size="sm"
              :disabled="retryingJobId !== null"
              class="flex-1 min-w-fit flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
              </svg>
              Remover
            </Button>
          </div>
        </div>
      </div>
      <Button 
        @click="deleteAllCanceled"
        variant="outline"
        class="w-full mt-4 border-amber-500/50 text-amber-400 hover:bg-amber-500/10 hover:border-amber-500 transition-all flex items-center justify-center gap-2 btn-translucent"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
        </svg>
        Limpar Todos Cancelados
      </Button>
    </Card>

    <!-- Empty State -->
    <Card v-if="activeJobsCount === 0" class="text-center py-8">
      <p class="text-gray-400">Nenhum download ativo no histórico.</p>
      <p class="text-sm text-gray-500 mt-2">Acesse a aba "Fontes" para começar a baixar itens.</p>
    </Card>

    <!-- Download Details Modal -->
    <DownloadDetails :job="selectedJobDetails" :show="showDetailsModal" @close="showDetailsModal = false" />

    <!-- Completed Download Details Modal -->
    <CompletedDownloadDetails :job="selectedCompletedJobDetails" :show="showCompletedDetailsModal" @close="showCompletedDetailsModal = false" />

    <!-- Delete Single Download Modal -->
    <Modal 
      :isOpen="showDeleteModal" 
      @close="showDeleteModal = false"
      title="Remover Registro"
      maxWidthClass="max-w-lg"
    >
      <div class="space-y-6">
        <div class="flex items-center gap-4 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl">
          <div class="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center shrink-0 shadow-lg">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-rose-500" stroke="currentColor" stroke-width="2.5">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="text-[11px] font-black text-rose-400 uppercase tracking-widest mb-1">Confirmação Crítica</p>
            <p class="text-sm font-bold text-white">Deseja realmente deletar este acervo do disco?</p>
          </div>
        </div>
        
        <p class="text-xs text-slate-500 uppercase tracking-widest leading-relaxed text-center px-4">
          Esta operação irá apagar permanentemente os dados baixados. O processo não poderá ser revertido.
        </p>
      </div>
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="showDeleteModal = false"
            class="flex-1 h-14 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl transition-all border border-white/10 active:scale-95"
          >
            Cancelar
          </button>
          <button 
            @click="deleteJobFile(jobToDelete)"
            class="flex-1 h-14 bg-rose-600 hover:bg-rose-500 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-rose-900/40 transition-all active:scale-95 flex items-center justify-center gap-2"
          >
            Confirmar Exclusão
          </button>
        </div>
      </template>
    </Modal>

    <!-- Clear All Completed Modal -->
    <Modal 
      :isOpen="showClearAllModal"
      @close="showClearAllModal = false"
      title="Limpar Concluídos"
      maxWidthClass="max-w-lg"
    >
      <div class="space-y-6">
        <div class="flex items-center gap-4 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center shrink-0 shadow-lg">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-emerald-500" stroke="currentColor" stroke-width="2.5">
              <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="text-[11px] font-black text-emerald-400 uppercase tracking-widest mb-1">Manutenção de Banco</p>
            <p class="text-sm font-bold text-white">Remover todos os registros finalizados?</p>
          </div>
        </div>
        
        <div class="bg-black/20 rounded-xl p-4 border border-white/5 space-y-1 text-center">
          <p class="text-sm font-black text-emerald-300 uppercase tracking-tighter">
            {{ downloadStore.completedDownloads.length }} itens serão arquivados
          </p>
          <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Os arquivos em disco não serão afetados.</p>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="showClearAllModal = false"
            class="flex-1 h-14 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl transition-all border border-white/10 active:scale-95"
          >
            Cancelar
          </button>
          <button 
            @click="clearCompleted"
            class="flex-1 h-14 bg-gradient-to-br from-emerald-600 to-teal-700 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-emerald-900/40 transition-all active:scale-95"
          >
            Limpar Histórico
          </button>
        </div>
      </template>
    </Modal>

    <!-- Clear All Failed Modal -->
    <Modal 
      :isOpen="showClearFailedModal"
      @close="showClearFailedModal = false"
      title="Sanear Falhas"
      maxWidthClass="max-w-lg"
    >
      <div class="space-y-6">
        <div class="flex items-center gap-4 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl">
          <div class="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center shrink-0 shadow-lg">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-rose-500" stroke="currentColor" stroke-width="2.5">
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="text-[11px] font-black text-rose-400 uppercase tracking-widest mb-1">Saneamento Técnico</p>
            <p class="text-sm font-bold text-white">Expurgar registros com erro?</p>
          </div>
        </div>
        
        <div class="bg-black/20 rounded-xl p-4 border border-white/5 space-y-1 text-center">
          <p class="text-sm font-black text-rose-300 uppercase tracking-tighter">
            {{ downloadStore.failedDownloads.length }} logs de erro serão excluídos
          </p>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="showClearFailedModal = false"
            class="flex-1 h-14 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl transition-all border border-white/10 active:scale-95"
          >
            Ignorar
          </button>
          <button 
            @click="clearFailed"
            class="flex-1 h-14 bg-rose-600 hover:bg-rose-500 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-rose-900/40 transition-all active:scale-95"
          >
            Limpar Agora
          </button>
        </div>
      </template>
    </Modal>

    <!-- Clear All Canceled Modal -->
    <Modal 
      :isOpen="showClearCanceledModal"
      @close="showClearCanceledModal = false"
      title="Arquivar Cancelados"
      maxWidthClass="max-w-lg"
    >
      <div class="space-y-6">
        <div class="flex items-center gap-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
          <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center shrink-0 shadow-lg">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-blue-500" stroke="currentColor" stroke-width="2.5">
              <path d="M18.364 18.364A9 9 0 105.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="text-[11px] font-black text-blue-400 uppercase tracking-widest mb-1">Limpeza de Estado</p>
            <p class="text-sm font-bold text-white">Deseja remover as tarefas abortadas?</p>
          </div>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="showClearCanceledModal = false"
            class="flex-1 h-14 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl transition-all border border-white/10 active:scale-95"
          >
            Voltar
          </button>
          <button 
            @click="clearCanceled"
            class="flex-1 h-14 bg-blue-600 hover:bg-blue-500 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-blue-900/40 transition-all active:scale-95"
          >
            Confirmar
          </button>
        </div>
      </template>
    </Modal>

    <!-- Cleanup Installer Confirmation Modal -->
    <Modal 
      :isOpen="showCleanupModal"
      @close="showCleanupModal = false"
      title="Otimizar Espaço"
      maxWidthClass="max-w-lg"
    >
      <div class="space-y-6">
        <div class="flex items-center gap-4 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
          <div class="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center shrink-0 shadow-lg">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-amber-500" stroke="currentColor" stroke-width="2.5">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="text-[11px] font-black text-amber-400 uppercase tracking-widest mb-1">Manutenção Pós-Instalação</p>
            <p class="text-sm font-bold text-white">Deseja expurgar o instalador original?</p>
          </div>
        </div>
        
        <div class="bg-black/20 rounded-xl p-4 border border-white/5 space-y-2">
          <div class="flex gap-2">
             <span class="text-emerald-400 font-black">✓</span>
             <p class="text-xs text-slate-300">O jogo continuará instalado e funcional.</p>
          </div>
          <div class="flex gap-2">
             <span class="text-emerald-400 font-black">✓</span>
             <p class="text-xs text-slate-300">Espaço em disco será liberado imediatamente.</p>
          </div>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="showCleanupModal = false"
            class="flex-1 h-14 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl transition-all border border-white/10 active:scale-95"
          >
            Manter Arquivos
          </button>
          <button 
            @click="confirmCleanup"
            class="flex-1 h-14 bg-gradient-to-br from-amber-600 to-orange-700 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-amber-900/40 transition-all active:scale-95 flex items-center justify-center gap-2"
          >
            Executar Limpeza
          </button>
        </div>
      </template>
    </Modal>

    <!-- Error Details Modal -->
    <Modal 
      :isOpen="!!showErrorModal"
      @close="showErrorModal = null"
      title="Console de Erros"
      maxWidthClass="max-w-2xl"
    >
      <div v-if="showErrorModal" class="space-y-6">
        <div class="bg-slate-900/80 border border-rose-500/20 rounded-3xl p-6 shadow-inner overflow-hidden relative">
          <div class="absolute top-0 right-0 p-4 opacity-5">
            <svg viewBox="0 0 24 24" fill="none" class="w-24 h-24 text-rose-500" stroke="currentColor"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>
          <p class="text-xs font-black font-mono text-rose-400 uppercase tracking-widest mb-4">Output Log v3.1</p>
          <div class="bg-black/60 rounded-xl p-5 border border-white/5">
            <p class="text-sm text-rose-100 font-mono whitespace-pre-wrap break-words max-h-96 overflow-y-auto custom-scrollbar leading-relaxed">
              {{ getCurrentErrorLog() }}
            </p>
          </div>
        </div>
        
        <p class="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] text-center">
          Utilize estas informações para suporte técnico ou depuração.
        </p>
      </div>
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="copyErrorToClipboard"
            class="flex-1 h-14 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest rounded-2xl transition-all border border-white/10 active:scale-95 flex items-center justify-center gap-2"
          >
            Copiar Log
          </button>
          <button 
            @click="showErrorModal = null"
            class="flex-1 h-14 bg-rose-600 hover:bg-rose-500 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-rose-900/40 transition-all active:scale-95"
          >
            Fechar Painel
          </button>
        </div>
      </template>
    </Modal>

    <!-- Modal de Ponte: Instalação em Andamento -->
    <Modal 
      v-if="showInstallingModal" 
      @close="showInstallingModal = false" 
      title="Status da Instalação" 
      maxWidthClass="max-w-xl"
    >
      <div class="space-y-8 py-2">
        <!-- Banner de Status Animado -->
        <div class="flex flex-col items-center justify-center p-10 bg-gradient-to-br from-slate-900 to-slate-950 border border-cyan-500/20 rounded-[2rem] relative overflow-hidden shadow-2xl">
          <div class="absolute inset-0 bg-cyan-500/5 blur-3xl opacity-20 animate-pulse"></div>
          
          <!-- Logo/Spinner Interativo -->
          <div class="relative w-24 h-24 mb-6">
            <div class="absolute inset-0 border-4 border-cyan-500/10 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin-slow"></div>
            <div class="absolute inset-4 bg-cyan-500/10 rounded-full flex items-center justify-center">
               <svg viewBox="0 0 24 24" fill="none" class="w-10 h-10 text-cyan-400 animate-pulse" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 22v-5m0-10V2m0 10l5 5m-5-5l-5 5m5-5l5-5m-5 5l-5-5" stroke-linecap="round" stroke-linejoin="round"/>
               </svg>
            </div>
          </div>
          
          <h3 class="text-xl font-black text-white text-center uppercase italic tracking-tighter leading-tight">{{ installingJobName }}</h3>
          <p class="text-cyan-400/60 text-[10px] font-black uppercase tracking-[0.3em] mt-3">Agente de Instalação Ativo</p>
        </div>

        <!-- Guia de Instalação Manual (Didático e Interativo) -->
        <div class="space-y-4 px-2">
          <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4">Checklist de Verificação:</p>
          
          <div class="grid grid-cols-1 gap-3">
            <button 
              v-for="(step, index) in [
                { id: 1, text: 'Defina o <b>Idioma</b> na janela do instalador.' },
                { id: 2, text: 'Aponte a <b>Pasta de Destino</b> (SSD recomendado).' },
                { id: 3, text: 'Execute o <b>Install</b> e aguarde a barra de progresso.' }
              ]"
              :key="step.id"
              @click="toggleStep(step.id)"
              class="w-full flex items-center gap-4 p-4 bg-white/[0.03] border rounded-2xl transition-all text-left group"
              :class="completedSteps.includes(step.id) ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-white/5 hover:border-cyan-500/30'"
            >
              <div class="w-8 h-8 rounded-xl flex-shrink-0 flex items-center justify-center text-xs font-black transition-all border"
                   :class="completedSteps.includes(step.id) ? 'bg-emerald-500 text-white border-emerald-400 shadow-lg shadow-emerald-500/20' : 'bg-slate-900 text-slate-600 border-slate-800 group-hover:border-cyan-500/30'">
                <span v-if="completedSteps.includes(step.id)">✓</span>
                <span v-else>{{ step.id }}</span>
              </div>
              <p class="text-xs font-bold transition-colors" :class="completedSteps.includes(step.id) ? 'text-emerald-200' : 'text-slate-300'" v-html="step.text"></p>
            </button>
          </div>
        </div>
      </div>
      
      <template #actions>
        <div class="flex gap-4 mt-8">
          <button 
            @click="showInstallingModal = false"
            class="flex-1 h-14 bg-cyan-600 hover:bg-cyan-500 text-white font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-cyan-900/40 transition-all active:scale-95"
          >
            Continuar em Segundo Plano
          </button>
        </div>
      </template>
    </Modal>

    <!-- Modal de Verificação de Integridade (Porteiro de Segurança) -->
    <Modal 
      v-if="showIntegrityCheckModal" 
      @close="showIntegrityCheckModal = false" 
      title="Segurança" 
      maxWidthClass="max-w-lg"
    >
      <div class="space-y-8 py-4">
        <!-- 1. LOADING STATE: Analyzing -->
        <div v-if="isCheckingIntegrity" class="flex flex-col items-center justify-center p-12 space-y-6">
           <div class="relative w-20 h-20">
              <div class="absolute inset-0 border-4 border-cyan-500/10 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                 <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-cyan-500" stroke="currentColor" stroke-width="2.5">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round"/>
                 </svg>
              </div>
           </div>
           <div class="text-center space-y-2">
              <h3 class="text-xl font-black text-white uppercase italic tracking-tighter animate-pulse">Escaneando Arquivos...</h3>
              <p class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Verificando integridade e instalador</p>
           </div>
        </div>

        <!-- 2. RESULT STATE: Finished scanning -->
        <div v-else-if="integrityCheckData" class="space-y-6 animate-in fade-in zoom-in-95 duration-500">
           <!-- Health Banner -->
           <div class="flex items-center gap-5 p-6 rounded-3xl border shadow-2xl" 
                :class="{
                  'bg-emerald-500/10 border-emerald-500/30 shadow-emerald-950/20': integrityCheckData.status === 'healthy',
                  'bg-amber-500/10 border-amber-500/30 shadow-amber-950/20': integrityCheckData.status === 'warning',
                  'bg-rose-500/10 border-rose-500/30 shadow-rose-950/20': integrityCheckData.status === 'critical'
                }">
              <div class="w-16 h-16 rounded-2xl flex items-center justify-center shrink-0 shadow-lg"
                   :class="{
                     'bg-emerald-500/20 text-emerald-400': integrityCheckData.status === 'healthy',
                     'bg-amber-500/20 text-amber-400': integrityCheckData.status === 'warning',
                     'bg-rose-500/20 text-rose-500': integrityCheckData.status === 'critical'
                   }">
                 <svg v-if="integrityCheckData.status === 'healthy'" viewBox="0 0 24 24" fill="none" class="w-10 h-10" stroke="currentColor" stroke-width="3">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
                 </svg>
                 <svg v-else viewBox="0 0 24 24" fill="none" class="w-10 h-10" stroke="currentColor" stroke-width="3">
                    <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round"/>
                 </svg>
              </div>
              <div class="flex-1">
                 <h3 class="text-2xl font-black uppercase italic tracking-tighter"
                     :class="{
                       'text-emerald-400': integrityCheckData.status === 'healthy',
                       'text-amber-400': integrityCheckData.status === 'warning',
                       'text-rose-400': integrityCheckData.status === 'critical'
                     }">
                   {{ integrityCheckData.status === 'healthy' ? 'Integridade OK' : 'Falha Detectada' }}
                 </h3>
                 <p class="text-[10px] font-black uppercase tracking-widest opacity-60 text-white">Score de Saúde: {{ integrityCheckData.health_score }}%</p>
              </div>
           </div>

           <!-- Issues List (if any) -->
           <div v-if="integrityCheckData.issues && integrityCheckData.issues.length > 0" class="bg-black/40 p-5 rounded-2xl border border-white/5 space-y-4">
              <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Inconsistências Encontradas:</p>
              <ul class="space-y-2">
                 <li v-for="(issue, i) in integrityCheckData.issues" :key="i" class="text-xs font-bold text-rose-200/80 flex gap-3">
                    <span class="text-rose-500 font-black shrink-0">•</span> {{ issue }}
                 </li>
              </ul>
              <div class="pt-3 border-t border-white/5 space-y-2">
                 <p class="text-[10px] font-black text-slate-600 uppercase tracking-widest leading-relaxed">
                   Dica: Verifique se o seu Antivírus/Defender excluiu arquivos ou tente baixar novamente o item.
                 </p>
              </div>
           </div>

           <!-- Action Area -->
           <div class="flex flex-col gap-3">
              <Button 
                v-if="integrityCheckData.status === 'healthy'" 
                @click="confirmRunInstaller" 
                variant="success" 
                size="lg" 
                class="w-full h-16 bg-gradient-to-r from-emerald-600 to-teal-600 font-black uppercase tracking-widest rounded-2xl shadow-xl shadow-emerald-900/20 active:scale-95"
              >
                 Iniciar Instalação
              </Button>
              <template v-else>
                 <Button @click="confirmRunInstaller" variant="danger" size="lg" class="w-full h-16 bg-rose-600 hover:bg-rose-500 font-black uppercase tracking-widest rounded-2xl shadow-xl shadow-rose-900/30 active:scale-95">
                   Instalar Mesmo Assim
                 </Button>
                 <Button @click="showIntegrityCheckModal = false" variant="outline" size="lg" class="w-full h-14 bg-white/5 border-white/10 font-black uppercase tracking-widest rounded-2xl">
                   Voltar e Corrigir
                 </Button>
              </template>
           </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect, watch } from 'vue'
import { useDownloadStore } from '../stores/download'
import { useToastStore } from '../stores/toast'
import api from '../services/api'
import Card from '../components/Card.vue'
import Button from '../components/Button.vue'
import StatCard from '../components/StatCard.vue'
import Modal from '../components/Modal.vue'
import DownloadDetails from '../components/DownloadDetails.vue'
import CompletedDownloadDetails from '../components/CompletedDownloadDetails.vue'
import { formatBytes, formatSpeed, formatMbps, calculateETA } from '../utils/format'

const downloadStore = useDownloadStore()
const toastStore = useToastStore()
const showDetailsModal = ref(false)
const selectedJobDetails = ref(null)
const showCompletedDetailsModal = ref(false)
const selectedCompletedJobDetails = ref(null)
const showDeleteModal = ref(false)
const showClearAllModal = ref(false)
const showClearFailedModal = ref(false)
const showClearCanceledModal = ref(false)
const showCleanupModal = ref(false)
const showErrorModal = ref(null)
const errorLogCache = ref({})
const jobToDelete = ref(null)
const jobToCleanup = ref(null)
const retryingJobId = ref(null)
const jobStatusHistory = ref({})
const foundSetups = ref({}) // jobId -> { found, setup_path }
const spaceWarnings = ref({}) // jobId -> message
const showInstallingModal = ref(false)
const installingJobName = ref('')
const installingJobPID = ref(null)
const installingJobPath = ref('')
const installingJobID = ref(null)
const completedSteps = ref([])
const showIntegrityCheckModal = ref(false)
const isCheckingIntegrity = ref(false)
const integrityCheckData = ref(null)
const pendingJobToInstall = ref(null)
let installCheckInterval = null

async function markAsInstalled(jobId) {
  try {
    await downloadStore.markInstalled(jobId)
    // Forçar re-check pra atualizar dicas se necessário
    nextTick(() => checkJobSetups())
  } catch (e) {}
}

function toggleStep(step) {
  if (completedSteps.value.includes(step)) {
    completedSteps.value = completedSteps.value.filter(s => s !== step)
  } else {
    completedSteps.value.push(step)
  }
}

onMounted(() => {
  downloadStore.fetchJobs().then(() => {
    checkJobSetups()
  })
})

async function checkJobSetups() {
  const completed = downloadStore.completedDownloads
  for (const job of completed) {
    // Só checar se ainda não temos NENHUM dado para esse ID (evita re-scan de falhas/manuais)
    if (foundSetups.value[job.id] === undefined) {
      const res = await downloadStore.checkSetup(job.id)
      if (res) {
        foundSetups.value[job.id] = res
      }
    }
  }
}

async function forceCheckSetups() {
  // Limpar detecções negativas para forçar re-scan
  Object.keys(foundSetups.value).forEach(id => {
    if (!foundSetups.value[id].found) {
      delete foundSetups.value[id]
    }
  })
  await checkJobSetups()
}

// Monitora mudanças de tamanho (metadata resolvido)
watch(() => downloadStore.jobs.map(j => `${j.id}:${j.total}`), async (newVals, oldVals) => {
  if (!oldVals) return
  
  for (let i = 0; i < newVals.length; i++) {
    const [id, totalStr] = newVals[i].split(':')
    const total = parseInt(totalStr)
    const oldVal = oldVals.find(v => v.startsWith(`${id}:`))
    
    if (oldVal) {
      const oldTotal = parseInt(oldVal.split(':')[1])
      // Se o tamanho aumentou significativamente (ex: metadata)
      if (total > oldTotal * 2 && total > 1024 * 1024 * 50) {
        console.log(`[Downloads] Tamanho do job ${id} aumentou drasticamente: ${oldTotal} -> ${total}`)
        const job = downloadStore.jobs.find(j => j.id === parseInt(id))
        if (job) {
          const disk = await downloadStore.getDiskSpace(job.dest)
          if (disk && disk.free < total * 1.5) { // 1.5x por segurança pra baixar + unpack inicial
            spaceWarnings.value[id] = `⚠️ O tamanho real foi detectado (${formatBytes(total)}). Seu disco pode não ter espaço suficiente.`
            toastStore.push('Aviso de Espaço', `O download de "${job.name}" foi pausado pois o tamanho real (${formatBytes(total)}) excede o espaço seguro disponível.`)
            // INTERROMPER O DOWNLOAD IMEDIATAMENTE
            downloadStore.pauseJob(job.id)
          }
        }
      }
    }
  }
}, { deep: true })


// Watch completed downloads to check for new ones
watch(() => downloadStore.completedDownloads.length, () => {
  checkJobSetups()
})

// Atualiza detalhes em tempo real enquanto o modal está aberto
watchEffect(() => {
  if (showDetailsModal.value && selectedJobDetails.value) {
    const live = downloadStore.jobs.find(j => j.id === selectedJobDetails.value.id)
    if (live) {
      Object.keys(live).forEach(key => {
        const val = live[key]
        if (val !== null && val !== undefined) {
          selectedJobDetails.value[key] = val
        }
      })
    }
  }
})

// Monitora mudancas de status para exibir toasts
watchEffect(() => {
  downloadStore.jobs.forEach(job => {
    const previousStatus = jobStatusHistory.value[job.id]
    
    // Se o status mudou
    if (previousStatus && previousStatus !== job.status) {
      // Download passou para "running" a partir de "queued"
      if (previousStatus === 'queued' && job.status === 'running') {
        try { toastStore.push('Fila', `Download "${job.name}" iniciado`) } catch (e) {}
      }

      // Download falhou
      if (job.status === 'failed') {
        try {
          if (job.last_error) {
            const info = parseErrorInfo(job.last_error)
            const title = info.code ? `Erro (${info.code})` : 'Erro'
            const msg = info.summary ? `${job.name || 'Download'}: ${info.summary}` : `${job.name || 'Download'} falhou. Veja o log.`
            toastStore.push(title, msg)
          } else {
            downloadStore.getJobDetails(job.id).then(details => {
              const lastError = details?.last_error || details?.error
              if (lastError) {
                job.last_error = lastError
                errorLogCache.value[job.id] = lastError
                const info = parseErrorInfo(lastError)
                const title = info.code ? `Erro (${info.code})` : 'Erro'
                const msg = info.summary ? `${job.name || 'Download'}: ${info.summary}` : `${job.name || 'Download'} falhou. Veja o log.`
                toastStore.push(title, msg)
              } else {
                toastStore.push('Erro', `${job.name || 'Download'} falhou. Veja o log.`)
              }
            }).catch(() => {
              try { toastStore.push('Erro', `${job.name || 'Download'} falhou. Veja o log.`) } catch (e) {}
            })
          }
        } catch (e) {}
      }
      
      // Download foi concluido
if (job.status === 'completed' && (previousStatus === 'running' || previousStatus === 'paused')) {
  try {
    const name = job.name || 'Download'
    const sizeGB = job.size ? (job.size / 1024 / 1024 / 1024).toFixed(2) + ' GB' : ''
    const speedMBs = job.speed ? (job.speed / 1024 / 1024).toFixed(1) + ' MB/s' : ''
    
    let message = `"${name}" concluído`
    if (sizeGB && speedMBs) {
      message += ` (${sizeGB} @ ${speedMBs})`
    } else if (sizeGB) {
      message += ` (${sizeGB})`
    }
    
    toastStore.push(' Concluído', message)
    
    // CRÍTICO: Disparar verificação de instalador IMEDIATAMENTE após concluir
    setTimeout(() => checkJobSetups(), 500)
    setTimeout(() => checkJobSetups(), 3000) // Double-check caso o IO demore
  } catch (e) {}
}
    }
    
    // Atualiza historico de status
    jobStatusHistory.value[job.id] = job.status
  })
})

function parseErrorInfo(lastError) {
  if (!lastError || typeof lastError !== 'string') return { code: null, summary: null }
  const lines = lastError.split('\n').map(l => (l || '').trim()).filter(Boolean)
  let code = null
  if (lines.length > 0) {
    const m = lines[0].match(/^\[C[oó]digo:\s*([^\]]+)\]$/i)
    if (m) code = m[1].trim()
  }
  let summary = null
  if (lines.length > 1) summary = lines[1]
  return { code, summary }
}

watch(showErrorModal, (jobId) => {
  if (!jobId) return
  try {
    const job = downloadStore.failedDownloads.find(j => j.id === jobId)
    if (job && job.last_error) {
      errorLogCache.value[jobId] = job.last_error
      return
    }
    if (errorLogCache.value[jobId]) return

    downloadStore.getJobDetails(jobId).then(details => {
      const lastError = details?.last_error || details?.error
      if (lastError) {
        errorLogCache.value[jobId] = lastError
        const inStore = downloadStore.jobs.find(j => j.id === jobId)
        if (inStore) inStore.last_error = lastError
      }
    }).catch(() => {})
  } catch (e) {}
})

const pausedJobs = computed(() => 
  downloadStore.jobs.filter(j => j.status === 'paused')
)

const pausedCount = computed(() => pausedJobs.value.length)

// Total excludes canceled downloads from the count
const activeJobsCount = computed(() => 
  downloadStore.jobs.filter(j => j.status !== 'canceled').length
)

function openDeleteFileDialog(jobId) {
  console.log(`[Downloads] openDeleteFileDialog(${jobId}) - Abrindo confirmação`)
  jobToDelete.value = jobId
  showDeleteModal.value = true
}

async function deleteJobFile(jobId) {
  try {
    console.log(`[Downloads] deleteJobFile(${jobId}) iniciado`)
    await downloadStore.deleteJobFile(jobId)
    console.log(`[Downloads] deleteJobFile(${jobId}) concluido`)
    showDeleteModal.value = false
    jobToDelete.value = null
  } catch (e) {
    console.error(`[Downloads] Erro ao deletar arquivo ${jobId}:`, e)
  }
}

async function pauseDownload(jobId) {
  try {
    await downloadStore.pauseJob(jobId)
  } catch (e) {
    console.error('Erro ao pausar:', e)
  }
}

async function resumeDownload(jobId) {
  try {
    await downloadStore.resumeJob(jobId)
  } catch (e) {
    console.error('Erro ao continuar:', e)
  }
}

async function cancelDownload(jobId) {
  try {
    await downloadStore.cancelJob(jobId)
  } catch (e) {
    console.error('Erro ao cancelar:', e)
  }
}

async function openDetails(jobId) {
  try {
    selectedJobDetails.value = await downloadStore.getJobDetails(jobId)
    showDetailsModal.value = true
  } catch (e) {
    console.error('Erro ao carregar detalhes:', e)
  }
}

async function openCompletedDetails(jobId) {
  try {
    const job = downloadStore.jobs.find(j => j.id === jobId)
    if (job) {
      selectedCompletedJobDetails.value = job
      showCompletedDetailsModal.value = true
    }
  } catch (e) {
    console.error('Erro ao carregar detalhes do download concluído:', e)
  }
}

async function retryDownload(jobId) {
  try {
    // Evitar múltiplos cliques
    if (retryingJobId.value !== null) {
      console.log('[Downloads] Já há um retry em progresso')
      return
    }
    
    retryingJobId.value = jobId
    console.log(`[Downloads] Retrying job #${jobId}`)
    await downloadStore.retryJob(jobId)
  } catch (e) {
    console.error('Erro ao tentar novamente:', e)
  } finally {
    retryingJobId.value = null
  }
}

function deleteAllCompleted() {
  showClearAllModal.value = true
}

async function clearCompleted() {
  try {
    await downloadStore.clearCompletedJobs()
    showClearAllModal.value = false
  } catch (e) {
    console.error('Erro ao limpar concluídos:', e)
  }
}

async function runInstaller(jobId) {
  try {
    const job = downloadStore.jobs.find(j => j.id === jobId)
    const setup = foundSetups.value[jobId]
    if (!job || !setup) return

    // 🛡️ ABRIR GATEKEEPER VISÍVEL IMEDIATAMENTE (Requisito do Usuário)
    pendingJobToInstall.value = { id: jobId, path: setup.setup_path, name: job.name }
    integrityCheckData.value = null
    isCheckingIntegrity.value = true
    showIntegrityCheckModal.value = true
    
    // Realizar verificação em background com delay artificial para ser visível e "dramático"
    try {
      const [res] = await Promise.all([
        api.get(`/api/jobs/${jobId}/integrity`),
        new Promise(resolve => setTimeout(resolve, 2500)) // Aumentado para 2.5s para ser bem perceptível
      ])
      integrityCheckData.value = res.data
    } catch (intErr) {
      console.error('[Integrity] Erro na verificação pré-instalação:', intErr)
      // Fallback em caso de erro técnico na API
      integrityCheckData.value = { status: 'warning', health_score: 50, issues: ['Falha técnica no sistema de verificação. Prossiga com cautela.'] }
    } finally {
      isCheckingIntegrity.value = false
    }
    
  } catch (e) {
    console.error('Erro ao iniciar instalador:', e)
  }
}

function confirmRunInstaller() {
  if (pendingJobToInstall.value) {
    const { id, path, name } = pendingJobToInstall.value
    showIntegrityCheckModal.value = false
    proceedToRunInstaller(id, path, name)
    pendingJobToInstall.value = null
  }
}

async function proceedToRunInstaller(jobId, setupPath, jobName) {
  try {
    // Se já estiver instalando ESTE mesmo job, não lana de novo, apenas abre o modal
    if (showInstallingModal.value && installingJobID.value === jobId) {
      return
    }

    installingJobName.value = jobName
    installingJobID.value = jobId
    installingJobPath.value = setupPath
    installingJobPID.value = null
    completedSteps.value = [] // Reset checklist
    
    // Abrir o modal imediatamente
    showInstallingModal.value = true
    
    // Iniciar no backend
    const res = await downloadStore.runSetup(jobId, setupPath)
    if (res && res.pid) {
      installingJobPID.value = res.pid
      startInstallerMonitor(res.pid)
    }
  } catch (err) {
    console.error('[Installer] Falha ao executar subprocesso:', err)
    showInstallingModal.value = false
  }
}

async function reFocusInstaller() {
  if (!installingJobPID.value) return
  try {
     const res = await api.post(`/api/system/process/${installingJobPID.value}/focus`)
     if (res.data && res.data.success) {
       console.log('[Focus] Comando de foco enviado com sucesso')
     }
  } catch (e) {
     console.error('[Focus] Erro ao enviar comando de foco:', e)
  }
}

function startInstallerMonitor(pid) {
  if (installCheckInterval) clearInterval(installCheckInterval)
  
  installCheckInterval = setInterval(async () => {
    try {
      const res = await api.get(`/api/system/process/${pid}`)
      if (res.data && res.data.running === false) {
        console.log(`[Installer] Processo ${pid} finalizado.`)
        stopInstallerMonitor()
      }
    } catch (e) {
      // Se der erro na API, para o monitor por segurança
      stopInstallerMonitor()
    }
  }, 3000)
}

function stopInstallerMonitor() {
  if (installCheckInterval) {
    clearInterval(installCheckInterval)
    installCheckInterval = null
  }
  showInstallingModal.value = false
}

function deleteAllFailed() {
  console.log('[Downloads] deleteAllFailed() chamado')
  showClearFailedModal.value = true
}

async function clearFailed() {
  try {
    console.log('[Downloads] Limpando jobs com falha...')
    const result = await downloadStore.clearFailedJobs()
    showClearFailedModal.value = false
    console.log('[Downloads] Jobs com falha limpados:', result)
  } catch (e) {
    console.error('[Downloads] Erro ao limpar erros:', e)
  }
}

async function openFolder(jobId) {
  try {
    console.log(`[Downloads] Abrindo pasta do download #${jobId}`)
    const job = downloadStore.jobs.find(j => j.id === jobId)
    
    if (!job) {
      console.error(`[Downloads] Job ${jobId} não encontrado na lista`)
      alert('Download não encontrado')
      return
    }
    
    console.log(`[Downloads] Job encontrado:`, job)
    
    // Verificar dest (é o campo usado no backend)
    const downloadPath = job.dest || job.path
    
    if (!downloadPath) {
      console.error(`[Downloads] Job ${jobId} não tem caminho. Campos disponíveis:`, Object.keys(job))
      alert('Caminho do download não foi definido. Tente atualizar a página.')
      return
    }
    
    console.log(`[Downloads] Abrindo: ${downloadPath}`)
    
    // Use api.post instead of fetch to get correct baseURL
    const response = await api.post('/api/jobs/open-folder', { path: downloadPath })
    
    console.log(`[Downloads] ✓ Pasta aberta com sucesso`)
  } catch (e) {
    console.error(`[Downloads] Erro ao abrir pasta:`, e)
    alert(`Erro ao abrir pasta: ${e.message}`)
  }
}

function deleteAllCanceled() {
  showClearCanceledModal.value = true
}

async function clearCanceled() {
  try {
    console.log('[Downloads] Limpando jobs cancelados...')
    await downloadStore.clearCanceledJobs()
    showClearCanceledModal.value = false
    console.log('[Downloads] Jobs cancelados limpados')
  } catch (e) {
    console.error('[Downloads] Erro ao limpar cancelados:', e)
  }
}

function getCurrentErrorLog() {
  if (!showErrorModal.value) return 'Nenhum erro'
  const job = downloadStore.failedDownloads.find(j => j.id === showErrorModal.value)
  
  if (!job) return 'Job não encontrado'

  const cached = errorLogCache.value[showErrorModal.value]
  if (cached) return cached
  
  // Se tem erro específico, mostrar
  if (job.last_error) return job.last_error
  
  // Fallback: construir mensagem informativa
  const name = job.name || 'Download'
  const url = job.url || 'URL desconhecida'
  return `Falha no download de "${name}"\n\nURL: ${url}\n\nNenhum detalhe de erro foi registrado pelo servidor.`
}

async function cleanupInstaller(jobId) {
  jobToCleanup.value = jobId
  showCleanupModal.value = true
}

async function confirmCleanup() {
  if (!jobToCleanup.value) return
  try {
    const id = jobToCleanup.value
    await downloadStore.cleanupJob(id)
    showCleanupModal.value = false
    jobToCleanup.value = null
  } catch (e) {
    console.error('Erro na limpeza:', e)
  }
}

function copyErrorToClipboard() {
  const errorLog = getCurrentErrorLog()
  navigator.clipboard.writeText(errorLog).then(() => {
    alert('Log de erro copiado para a área de transferência')
  }).catch(() => {
    alert('Erro ao copiar log')
  })
}
</script>
