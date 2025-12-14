<template>
  <div class="space-y-6">
    <!-- Header Stats com SVGs animados -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <!-- Total -->
      <StatCard :title="`Total`" :value="activeJobsCount" color="cyan">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-12 h-12">
          <defs>
            <linearGradient id="totalGrad" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" style="stop-color: #06b6d4" />
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
            Alguns downloads grandes podem apresentar um breve atraso inicial para preparar a sessão e coletar peers/seeders, especialmente via magnet ou fontes como JSON, FitGirl, DODI e OnlineFix.
          </p>
          <p class="text-xs text-gray-400 mt-1">
            Aguarde. Ao iniciar, o download entrará em tração total, mantendo velocidade contínua e estável
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
              <stop offset="0%" style="stop-color: #06b6d4" />
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
              <p class="font-semibold text-cyan-300">{{ job.name }}</p>
              <p class="text-xs text-gray-500">
                <template v-if="job.status === 'queued'">
                  <span class="text-amber-400 font-medium">⏳ Aguardando</span>
                </template>
                <template v-else>
                  {{ job.downloaded ? formatBytes(job.downloaded) : '—' }} {{ job.total ? '/ ' + formatBytes(job.total) : '(desc.)' }}
                </template>
              </p>
            </div>
            <span class="text-sm font-bold text-green-400">
              <template v-if="job.progress !== null && job.progress !== undefined">{{ downloadStore.formatProgress(Math.min(job.progress, 100)) }}%</template>
              <template v-else-if="job.status === 'running'">Em andamento</template>
              <template v-else>0%</template>
            </span>
          </div>
          <div class="w-full bg-gray-900 rounded-full h-2 mb-2">
            <div 
              class="bg-gradient-to-r from-cyan-500 to-purple-500 h-2 rounded-full transition-all"
              :style="{ width: job.progress ? `${Math.min(job.progress, 100)}%` : (job.status === 'running' ? '6%' : '0%') }"
            />
          </div>
          <div class="flex justify-between items-center text-xs text-gray-400 mb-3">
            <span>{{ formatSpeed(job.speed) }}</span>
            <span>{{ calculateETA(job) }}</span>
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
              <p class="font-semibold text-yellow-300">{{ job.name }}</p>
              <p class="text-xs text-gray-400">{{ formatBytes(job.downloaded) }} {{ job.size ? '/ ' + formatBytes(job.size) : '(desc.)' }}</p>
            </div>
            <span class="text-sm font-bold text-yellow-400 bg-yellow-500/20 px-2 py-1 rounded">{{ downloadStore.formatProgress(Math.min(job.progress, 100)) }}%</span>
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
      <div class="flex items-center gap-2 mb-4">
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
      <div class="space-y-3">
        <div v-for="job in downloadStore.completedDownloads" :key="job.id" class="p-4 bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-lg hover:border-green-500/50 transition-colors">
          <div class="flex justify-between items-start gap-3 mb-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-green-400">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <p class="font-semibold text-green-300 truncate">{{ job.name }}</p>
              </div>
              <div class="flex items-center gap-4 text-sm">
                <span class="text-gray-400">
                  Tamanho:
                  <span class="text-green-300 font-medium">{{ formatBytes(job.size) }}</span>
                </span>
                <span class="text-gray-400">
                  Status:
                  <span class="text-green-300 font-medium">Concluído</span>
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
              variant="primary"
              size="sm"
              class="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 shadow-lg shadow-green-500/20 flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V6h5.17l2 2H20v10z"/>
              </svg>
              Abrir Pasta
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
              Remover
            </Button>
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
                <p class="font-semibold text-red-300 truncate">{{ job.name }}</p>
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
                <p class="font-semibold text-amber-300 truncate">{{ job.name }}</p>
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
      title="Remover Download"
    >
      <div class="space-y-4">
        <p class="text-gray-300">
          Tem certeza que deseja <span class="text-red-400 font-semibold">deletar os arquivos</span> deste download?
        </p>
        <p class="text-sm text-gray-500 bg-gray-900/50 p-3 rounded border border-gray-700">
          Esta ação não pode ser desfeita.
        </p>
      </div>
      <template #actions>
        <div class="flex gap-6 mt-6">
          <Button 
            @click="showDeleteModal = false"
            variant="outline"
            class="flex-1 border-gray-600 text-gray-300 hover:bg-gray-900/50 btn-translucent"
          >
            Cancelar
          </Button>
          <Button 
            @click="deleteJobFile(jobToDelete)"
            variant="danger"
            class="flex-1 bg-red-600 hover:bg-red-700 text-white"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 inline mr-2">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
            </svg>
            Deletar
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Clear All Completed Modal -->
    <Modal 
      :isOpen="showClearAllModal"
      @close="showClearAllModal = false"
      title="Limpar Downloads Concluídos"
    >
      <div class="space-y-4">
        <p class="text-gray-300">
          Tem certeza que deseja <span class="text-amber-400 font-semibold">deletar TODOS os downloads concluídos</span>?
        </p>
        <div class="bg-amber-900/20 border border-amber-500/30 rounded p-3 space-y-1">
          <p class="text-sm text-amber-300 font-medium">
            {{ downloadStore.completedDownloads.length }} item{{ downloadStore.completedDownloads.length !== 1 ? 's' : '' }} será{{ downloadStore.completedDownloads.length !== 1 ? 'ão' : '' }} removido{{ downloadStore.completedDownloads.length !== 1 ? 's' : '' }}
          </p>
          <p class="text-xs text-gray-500">
            Esta ação não pode ser desfeita.
          </p>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-6 mt-6">
          <Button 
            @click="showClearAllModal = false"
            variant="outline"
            class="flex-1 border-gray-600 text-gray-300 hover:bg-gray-900/50 btn-translucent"
          >
            Cancelar
          </Button>
          <Button 
            @click="clearCompleted"
            variant="danger"
            class="flex-1 bg-amber-600 hover:bg-amber-700 text-white"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 inline mr-2">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
            </svg>
            Limpar Tudo
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Clear All Failed Modal -->
    <Modal 
      :isOpen="showClearFailedModal"
      @close="showClearFailedModal = false"
      title="Limpar Downloads com Erro"
    >
      <div class="space-y-4">
        <p class="text-gray-300">
          Tem certeza que deseja <span class="text-red-400 font-semibold">deletar TODOS os downloads com erro</span>?
        </p>
        <div class="bg-red-900/20 border border-red-500/30 rounded p-3 space-y-1">
          <p class="text-sm text-red-300 font-medium">
            {{ downloadStore.failedDownloads.length }} item{{ downloadStore.failedDownloads.length !== 1 ? 's' : '' }} será{{ downloadStore.failedDownloads.length !== 1 ? 'ão' : '' }} removido{{ downloadStore.failedDownloads.length !== 1 ? 's' : '' }}
          </p>
          <p class="text-xs text-gray-500">
            Esta ação não pode ser desfeita.
          </p>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-6 mt-6">
          <Button 
            @click="showClearFailedModal = false"
            variant="outline"
            class="flex-1 border-gray-600 text-gray-300 hover:bg-gray-900/50 btn-translucent"
          >
            Cancelar
          </Button>
          <Button 
            @click="clearFailed"
            variant="danger"
            class="flex-1 bg-red-600 hover:bg-red-700 text-white"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 inline mr-2">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
            </svg>
            Limpar Tudo
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Clear All Canceled Modal -->
    <Modal 
      :isOpen="showClearCanceledModal"
      @close="showClearCanceledModal = false"
      title="Limpar Downloads Cancelados"
    >
      <div class="space-y-4">
        <p class="text-gray-300">
          Tem certeza que deseja <span class="text-blue-400 font-semibold">deletar TODOS os downloads cancelados</span>?
        </p>
        <div class="bg-blue-900/20 border border-blue-500/30 rounded p-3 space-y-1">
          <p class="text-sm text-blue-300 font-medium">
            {{ downloadStore.canceledDownloads.length }} item{{ downloadStore.canceledDownloads.length !== 1 ? 's' : '' }} será{{ downloadStore.canceledDownloads.length !== 1 ? 'ão' : '' }} removido{{ downloadStore.canceledDownloads.length !== 1 ? 's' : '' }}
          </p>
          <p class="text-xs text-gray-500">
            Esta ação não pode ser desfeita.
          </p>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-6 mt-6">
          <Button 
            @click="showClearCanceledModal = false"
            variant="outline"
            class="flex-1 border-gray-600 text-gray-300 hover:bg-gray-900/50 btn-translucent"
          >
            Cancelar
          </Button>
          <Button 
            @click="clearCanceled"
            variant="danger"
            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 inline mr-2">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
            </svg>
            Limpar Tudo
          </Button>
        </div>
      </template>
    </Modal>

    <!-- Error Details Modal -->
    <Modal 
      :isOpen="!!showErrorModal"
      @close="showErrorModal = null"
      title="Detalhes do Erro"
    >
      <div v-if="showErrorModal" class="space-y-4">
        <div class="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <p class="text-sm text-gray-300 font-mono whitespace-pre-wrap break-words max-h-96 overflow-y-auto">
            {{ getCurrentErrorLog() }}
          </p>
        </div>
        <div class="flex items-center gap-2 text-xs text-gray-500">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <span>Use este log para diagnosticar o problema</span>
        </div>
      </div>
      <template #actions>
        <div class="flex gap-6 mt-6">
          <Button 
            @click="copyErrorToClipboard"
            variant="secondary"
            class="flex-1"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 inline mr-2">
              <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
            </svg>
            Copiar
          </Button>
          <Button 
            @click="showErrorModal = null"
            variant="outline"
            class="flex-1"
          >
            Fechar
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import { useDownloadStore } from '../stores/download'
import { useToastStore } from '../stores/toast'
import api from '../services/api'
import Card from '../components/Card.vue'
import Button from '../components/Button.vue'
import StatCard from '../components/StatCard.vue'
import Modal from '../components/Modal.vue'
import DownloadDetails from '../components/DownloadDetails.vue'
import CompletedDownloadDetails from '../components/CompletedDownloadDetails.vue'
import { formatBytes, formatSpeed, calculateETA } from '../utils/format'

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
const showErrorModal = ref(null)
const jobToDelete = ref(null)
const retryingJobId = ref(null)
const jobStatusHistory = ref({})

onMounted(() => {
  downloadStore.fetchJobs()
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
  } catch (e) {}
}
    }
    
    // Atualiza historico de status
    jobStatusHistory.value[job.id] = job.status
  })
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
  
  // Se tem erro específico, mostrar
  if (job.last_error) return job.last_error
  
  // Fallback: construir mensagem informativa
  const name = job.name || 'Download'
  const url = job.url || 'URL desconhecida'
  return `Falha no download de "${name}"\n\nURL: ${url}\n\nNenhum detalhe de erro foi registrado pelo servidor.`
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
