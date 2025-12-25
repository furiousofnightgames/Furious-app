<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
    <!-- Header simples com uma única imagem grande (sem duplicação) -->
    <div class="relative overflow-hidden pb-0">
      <!-- Botão voltar -->
      <div class="absolute top-4 left-4 z-10">
        <button 
          @click="goBack"
          class="flex items-center gap-2 px-4 py-2 bg-slate-800/80 hover:bg-slate-700 rounded-lg transition text-cyan-400"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Voltar
        </button>
      </div>

      <!-- Imagem principal do header ocupando bem o espaço disponível -->
      <div v-if="headerImageUrl" class="pt-16 px-4 md:px-8 flex justify-center">
        <img
          :src="headerImageUrl"
          alt="Header do jogo"
          class="w-full max-w-6xl max-h-[500px] rounded-2xl shadow-2xl border border-slate-700/80 object-contain object-center"
        />
      </div>

      <!-- Placeholder se não tiver imagem nenhuma -->
      <div v-if="!headerImageUrl && !item?.gameDetails?.header_image && !item?.image && !item?.header_image" class="pt-20 pb-10 flex items-center justify-center">
        <div class="text-center">
          <svg class="w-24 h-24 mx-auto text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="text-slate-400">Imagem não disponível</p>
        </div>
      </div>
    </div>

    <!-- Conteúdo principal -->
    <div class="relative mt-[3px] z-10 px-4 md:px-8 pb-12">
      <div class="max-w-6xl mx-auto">
        <!-- Card principal -->
        <div class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
          <!-- Título e informações básicas -->
          <div class="mb-8">
            <!-- Alerta de Fonte Alternativa (SteamGridDB) -->
            <div v-if="item?.gameDetails?.source === 'steamgriddb'" class="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-start gap-4 animate-in">
              <div class="p-2 bg-amber-500/20 rounded-full text-amber-500 shrink-0">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-amber-200">Informações Limitadas</h3>
                <p class="text-amber-200/70 text-sm mt-1">
                  Este jogo não foi encontrado na loja oficial da Steam. As imagens foram obtidas via <strong>SteamGridDB</strong>, mas detalhes como descrição, vídeos e requisitos podem não estar disponíveis.
                </p>
              </div>
            </div>

            <div class="flex items-start justify-between gap-4 mb-4">
              <h1 class="text-4xl font-bold text-white">{{ item?.name }}</h1>
              <div class="flex-shrink-0">
                <FavoriteToggleButton v-if="item" :item="item" />
              </div>
            </div>
            
            <!-- Badges de informação -->
            <div class="flex flex-wrap gap-3 mb-6">
              <span v-if="item?.category" class="px-3 py-1 bg-cyan-500/20 border border-cyan-500/50 rounded-full text-cyan-300 text-sm">
                {{ item.category }}
              </span>
              <span v-if="item?.uploadDate" class="px-3 py-1 bg-purple-500/20 border border-purple-500/50 rounded-full text-purple-300 text-sm">
                {{ formatDate(item.uploadDate) }}
              </span>
              <span v-if="item?.size" class="px-3 py-1 bg-amber-500/20 border border-amber-500/50 rounded-full text-amber-300 text-sm">
                {{ formatSize(item.size) }}
              </span>
            </div>

            <!-- Descrição -->
            <p v-if="item?.description" class="text-slate-300 text-lg leading-relaxed mb-6">
              {{ item.description }}
            </p>
          </div>

          <!-- Grid de informações -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 pb-8 border-b border-slate-700">
            <!-- Informações da esquerda -->
            <div class="space-y-4">
              <div v-if="item?.source" class="flex items-start gap-3">
                <div class="w-6 h-6 text-cyan-400 flex-shrink-0 mt-1">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.658 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <div>
                  <p class="text-slate-400 text-sm">Fonte</p>
                  <p class="text-white font-medium">{{ item.source }}</p>
                </div>
              </div>

              <div v-if="item?.magnet" class="flex items-start gap-3">
                <div class="w-6 h-6 text-purple-400 flex-shrink-0 mt-1">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.658 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <div>
                  <p class="text-slate-400 text-sm">Magnet Link</p>
                  <button 
                    @click="copyToClipboard(item.magnet)"
                    class="text-cyan-400 hover:text-cyan-300 text-sm font-mono truncate max-w-xs transition"
                  >
                    {{ item.magnet.substring(0, 50) }}...
                  </button>
                </div>
              </div>

              <div v-if="item?.torrent" class="flex items-start gap-3">
                <div class="w-6 h-6 text-pink-400 flex-shrink-0 mt-1">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-slate-400 text-sm">Arquivo Torrent</p>
                  <a 
                    :href="item.torrent"
                    target="_blank"
                    class="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition"
                  >
                    Download Torrent
                  </a>
                </div>
              </div>
            </div>

            <!-- Informações da direita -->
            <div class="space-y-4">


              <div v-if="item?.language" class="flex items-start gap-3">
                <div class="w-6 h-6 text-blue-400 flex-shrink-0 mt-1">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10m-5 10l-4-8m9-5h4m0 0h4m-4 0v4m0-4v-4" />
                  </svg>
                </div>
                <div>
                  <p class="text-slate-400 text-sm">Idioma</p>
                  <p class="text-white font-medium">{{ item.language }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Ações -->
          <div class="flex flex-wrap gap-4">
            <button 
              v-if="item?.magnet"
              @click="downloadTorrent"
              class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 rounded-lg font-semibold text-white transition transform hover:scale-105"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Baixar via Torrent
            </button>

            <!-- Botão Baixar Direto (Sistema Interno) -->
            <button 
              v-if="item?.url || item?.magnet"
              @click="startDownloadFlow"
              :disabled="analysisLoading"
              class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:opacity-70 disabled:cursor-wait rounded-lg font-semibold text-white transition transform hover:scale-105 shadow-lg shadow-green-500/20"
            >
              <svg v-if="!analysisLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <svg v-else class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ analysisLoading ? 'Analisando...' : 'Baixar Jogo' }}
            </button>

            <button 
              v-if="item?.magnet"
              @click="copyToClipboard(item.magnet)"
              class="flex items-center gap-2 px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold text-white transition"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copiar Magnet
            </button>
          </div>
        </div>

        <!-- Vídeos da Steam -->
        <div v-if="item?.gameDetails?.movies && item.gameDetails.movies.length > 0" class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-6">Vídeos ({{ item.gameDetails.movies.length }})</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="(video, idx) in item.gameDetails.movies"
              :key="idx"
              class="group cursor-pointer"
              @click="openVideo(video)"
            >
              <!-- Debug: mostrar dados do vídeo -->
              <div style="display: none;">
                {{ console.log(`[Template] Renderizando vídeo ${idx}:`, video) }}
              </div>
              <div class="relative overflow-hidden rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 aspect-video mb-3">
                <img 
                  v-if="video.thumbnail"
                  :src="getVideoThumbnailUrl(video.thumbnail)" 
                  :alt="video.name"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
                <div v-else class="w-full h-full flex items-center justify-center bg-slate-700">
                  <svg class="w-12 h-12 text-slate-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
                <div class="absolute inset-0 flex items-center justify-center bg-black/40 group-hover:bg-black/20 transition-colors">
                  <svg class="w-16 h-16 text-white opacity-80 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
              <p class="text-white font-semibold text-sm">{{ video.name }}</p>
            </div>
          </div>
        </div>

        <!-- Screenshots da Steam - Carousel Horizontal -->
        <div v-if="item?.gameDetails?.screenshots && item.gameDetails.screenshots.length > 0" class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-6">Screenshots</h2>
          <div class="relative">
            <!-- Seta esquerda -->
            <button 
              @click="scrollScreenshots('left')"
              class="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 hover:bg-black/80 text-white p-2 rounded-full transition"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <!-- Container do carousel -->
            <div ref="screenshotScrollRef" class="overflow-x-auto pb-4 scrollbar-hide">
              <div class="flex gap-4 min-w-max px-12">
                <div v-for="(screenshot, idx) in item.gameDetails.screenshots" :key="idx" class="group cursor-pointer flex-shrink-0">
                  <div class="relative overflow-hidden rounded-lg bg-slate-700 w-96 h-56">
                    <img 
                      :src="getScreenshotUrl(screenshot)" 
                      :alt="`Screenshot ${idx + 1}`"
                      class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Seta direita -->
            <button 
              @click="scrollScreenshots('right')"
              class="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 hover:bg-black/80 text-white p-2 rounded-full transition"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Detalhes do Jogo da Steam -->
        <div v-if="loadingDetails" class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8 animate-pulse">
           <div class="h-8 bg-slate-700 rounded w-1/3 mb-6"></div>
           <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div class="h-24 bg-slate-700 rounded col-span-2"></div>
             <div class="h-6 bg-slate-700 rounded"></div>
             <div class="h-6 bg-slate-700 rounded"></div>
           </div>
        </div>

        <div v-else-if="item?.gameDetails?.found" class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-6">Detalhes do Jogo</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div v-if="item.gameDetails.description_short" class="md:col-span-2">
              <p class="text-slate-400 text-sm mb-2">Descrição</p>
              <p class="text-white leading-relaxed">{{ item.gameDetails.description_short }}</p>
            </div>

            <div v-if="item.gameDetails.developers && item.gameDetails.developers.length > 0">
              <p class="text-slate-400 text-sm mb-2">Desenvolvedora</p>
              <p class="text-white font-medium">{{ item.gameDetails.developers.join(', ') }}</p>
            </div>

            <div v-if="item.gameDetails.publishers && item.gameDetails.publishers.length > 0">
              <p class="text-slate-400 text-sm mb-2">Publicadora</p>
              <p class="text-white font-medium">{{ item.gameDetails.publishers.join(', ') }}</p>
            </div>

            <div v-if="item.gameDetails.genres && item.gameDetails.genres.length > 0">
              <p class="text-slate-400 text-sm mb-2">Gêneros</p>
              <div class="flex flex-wrap gap-2">
                <span v-for="genre in item.gameDetails.genres" :key="genre" class="px-3 py-1 bg-cyan-500/20 border border-cyan-500/50 rounded-full text-cyan-300 text-sm">
                  {{ genre }}
                </span>
              </div>
            </div>

            <div v-if="item.gameDetails.release_date">
              <p class="text-slate-400 text-sm mb-2">Data de Lançamento</p>
              <p class="text-white font-medium">{{ item.gameDetails.release_date }}</p>
            </div>

            <div v-if="item.gameDetails.metacritic_score">
              <p class="text-slate-400 text-sm mb-2">Metacritic</p>
              <p class="text-white font-medium">{{ item.gameDetails.metacritic_score }}/100</p>
            </div>
          </div>
        </div>

        <!-- Modal para reproduzir vídeo da Steam -->
        <!-- Modal para reproduzir vídeo da Steam -->
        <div v-if="showVideoModal && currentVideo" class="fixed inset-0 z-50 flex items-center justify-center bg-black/95" @click.self="closeVideo">
          
          <!-- Botão Anterior (Overlay) -->
          <button 
            v-if="hasPrev"
            @click.stop="prevVideo"
            class="absolute left-4 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition backdrop-blur-md group"
          >
            <svg class="w-8 h-8 opacity-70 group-hover:opacity-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div class="relative w-full max-w-4xl mx-4 aspect-video bg-black rounded-lg shadow-2xl overflow-hidden border border-slate-800">
            <!-- Botão Fechar (X) -->
            <button
              class="absolute top-4 right-4 text-white/70 hover:text-white z-20 bg-black/50 hover:bg-black/80 rounded-full p-2 transition backdrop-blur-sm"
              @click="closeVideo"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <!-- Título do Vídeo (Overlay sutil) -->
            <div class="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/80 to-transparent z-10 pointer-events-none">
              <h3 class="text-lg font-medium text-white/90 drop-shadow-md px-2">{{ currentVideo.name }}</h3>
            </div>
            
            <!-- Player de Vídeo -->
            <div :key="currentVideo.name" v-if="currentVideo.mp4 || currentVideo.webm" class="w-full h-full flex items-center justify-center bg-black">
              <iframe
                v-if="videoIframeHtml"
                :srcDoc="videoIframeHtml"
                class="w-full h-full"
                style="border: none;"
                allow="autoplay"
                allowfullscreen
              ></iframe>
              
              <video
                v-else
                ref="videoElement"
                class="w-full h-full object-contain"
                controls
                preload="metadata"
                crossorigin="anonymous"
                playsinline
                @error="onVideoError"
                @loadstart="onVideoLoadStart"
                @canplay="onVideoCanPlay"
              >
                <source v-if="currentVideo.mp4" :src="getProxyVideoUrl(currentVideo.mp4)" type="video/mp4" />
                <source v-if="currentVideo.webm" :src="getProxyVideoUrl(currentVideo.webm)" type="video/webm" />
                Seu navegador não suporta reprodução de vídeo.
              </video>
            </div>
            <div v-else class="w-full h-full flex items-center justify-center text-slate-400">
              <p>Nenhum vídeo disponível para reprodução.</p>
            </div>
          </div>

          <!-- Botão Próximo (Overlay) -->
          <button 
            v-if="hasNext"
            @click.stop="nextVideo"
            class="absolute right-4 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition backdrop-blur-md group"
          >
            <svg class="w-8 h-8 opacity-70 group-hover:opacity-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

      </div>
    </div>
  </div>

  <!-- MODAL DE DOWNLOAD -->
  <Modal v-if="showDownloadDialog" @close="showDownloadDialog = false">
      <div>
        <h3 class="text-lg font-bold text-cyan-400 mb-4">⬇️ Baixar Item</h3>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-400">Item:</p>
            <p class="text-cyan-300 font-semibold">{{ item?.name }}</p>
          </div>
          
          <div>
            <p class="text-sm text-gray-400">Tamanho:</p>
            <p class="text-cyan-300">
              <span v-if="modalInfo.checking">Verificando...</span>
              <span v-else-if="modalInfo.size">{{ formatBytes(modalInfo.size) }} <span class="text-xs text-gray-400">(ETA ~{{ modalInfo.eta }}s)</span></span>
              <span v-else>{{ formatBytes(item?.size) }}</span>
            </p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-300 mb-2">Pasta</label>
            <div class="flex gap-2">
              <div class="flex-1 p-3 bg-gray-900 border border-cyan-500/30 rounded">
                <p class="text-sm text-cyan-300 truncate">
                  {{ downloadDestination || 'downloads' }}
                </p>
              </div>
              <button 
                type="button"
                @click.stop="browsePath"
                class="border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 px-3 rounded border"
              >
                <span v-if="browseLoading">⏳</span>
                <span v-else>...</span>
              </button>
            </div>
          </div>

          <div class="flex gap-2 pt-4 border-t border-gray-700">
            <button 
              type="button"
              @click.prevent.stop="showDownloadDialog = false"
              class="flex-1 py-2 rounded border border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10"
            >
              Cancelar
            </button>
            <button 
              type="button"
              @click.prevent.stop="confirmDownload"
              :class="[
                'flex-1 px-4 py-2 rounded-lg font-semibold transform hover:scale-105 active:scale-95 transition-all duration-300',
                downloadStore.loading ? 'opacity-60 cursor-not-allowed bg-gray-700 text-gray-200' : 'bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600 text-white shadow-lg shadow-green-500/50 hover:shadow-green-500/80'
              ]"
              :disabled="downloadStore.loading"
            >
              <span v-if="downloadStore.loading">Aguarde...</span>
              <span v-else>Baixar Agora</span>
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <!-- Manual folder input fallback -->
    <Modal v-if="showManualFolderModal" @close="showManualFolderModal = false" title="Escolher pasta manualmente" :showDefaultButtons="false">
      <div style="pointer-events: auto;">
        <label class="block text-sm font-semibold text-gray-300 mb-2">Caminho da pasta</label>
        <Input v-model="manualFolderPath" placeholder="C:\\Users\\seu usuario\\Downloads" />
        <div class="flex gap-2 pt-4" style="pointer-events: auto;">
          <Button variant="outline" class="flex-1" @click="showManualFolderModal = false">
            Cancelar
          </Button>
          <Button variant="success" class="flex-1" @click="() => { downloadDestination = manualFolderPath || downloadDestination; showManualFolderModal = false }">
            Usar esta pasta
          </Button>
        </div>
      </div>
    </Modal>

    <!-- Modal de Análise de Fontes (Pré-Job) -->
    <SourceAnalysisModal
      :open="showAnalysisModal"
      :original-item="analysisOriginalItem"
      :candidates="analysisCandidates"
      :original-health="analysisOriginalItem?.health"
      :is-loading="analysisLoading"
      @close="showAnalysisModal = false"
      @confirm="onAnalysisConfirm"
    />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import { useDownloadStore } from '../stores/download'
import { useToastStore } from '../stores/toast'
import { formatBytes } from '../utils/format'
import Modal from '../components/Modal.vue'
import Input from '../components/Input.vue'
import Button from '../components/Button.vue'
import FavoriteToggleButton from '../components/FavoriteToggleButton.vue'

// Obter base URL da API para usar em URLs absolutas
const getApiBaseUrl = () => {
  // Usar a mesma base URL do axios
  return api.defaults.baseURL || 'http://127.0.0.1:8001'
}

const route = useRoute()
const router = useRouter()
const item = ref(null)
const loadingDetails = ref(true)
const copied = ref(false)
const screenshotScrollRef = ref(null)
const showVideoModal = ref(false)
const currentVideo = ref(null)
const headerImageUrl = ref(null)

const videoIframeHtml = ref(null)

// Download Refs
const downloadStore = useDownloadStore()
const showDownloadDialog = ref(false)
const downloadDestination = ref('downloads')
const downloadVerifySsl = ref({}) 
const showManualFolderModal = ref(false)
const manualFolderPath = ref('')
const browseLoading = ref(false)
const modalInfo = ref({ size: null, accept_range: false, eta: null, checking: false })


// Detectar se está rodando no .exe (PyQt5)
// IMPORTANTE: Executar FORA do onMounted para que as funções de proxy funcionem no template
// Estratégia atual:
// - Se userAgent indicar PyQt/QtWebEngine → considerar .exe
// - Se hostname for localhost/127.0.0.1 (qualquer porta) → considerar ambiente "embutido" (.exe ou dev local)
// Isso garante que o proxy de imagem/vídeo seja usado mesmo quando o backend
// estiver em portas diferentes (8001-8009) dentro do launcher.
const isExeEnv = (() => {
  try {
    const ua = navigator.userAgent || ''
    const hostname = window.location.hostname || ''
    const port = window.location.port || ''
    const protocol = window.location.protocol || ''

    // 1) Detecção direta por user agent (PyQt5 / QtWebEngine)
    if (ua.includes('PyQt') || ua.includes('QtWebEngine')) {
      console.log('[ItemDetails] Detectado PyQt/QtWebEngine via user agent')
      return true
    }

    // 2) Host local (127.0.0.1 / localhost) em qualquer porta
    //    No launcher, o backend sobe em 8001-8009 e o WebEngine aponta para essa URL.
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === ''
    if (isLocalhost && protocol === 'http:') {
      console.log('[ItemDetails] Ambiente local detectado (hostname + protocolo http):', { hostname, port })
      return true
    }

    // 3) Acesso via file:// (fallback para cenários específicos)
    const isFile = protocol === 'file:'
    if (isFile) {
      console.log('[ItemDetails] Detectado ambiente baseado em file:// protocol')
      return true
    }

    console.log('[ItemDetails] Ambiente detectado como navegador normal', { hostname, port, protocol })
    return false
  } catch (e) {
    console.warn('[ItemDetails] Falha ao detectar ambiente, assumindo navegador normal:', e)
    return false
  }
})()

// Função para detecção (mantida para compatibilidade)
const isExe = () => isExeEnv

onMounted(async () => {
  // Debug: Log de detecção de ambiente
  console.log('[ItemDetails] Ambiente detectado:', {
    isExe: isExeEnv,
    hostname: window.location.hostname,
    port: window.location.port,
    protocol: window.location.protocol,
    userAgent: navigator.userAgent.substring(0, 100)
  })
  
  // Tenta recuperar do router state primeiro
  if (router.currentRoute.value.state?.item) {
    item.value = router.currentRoute.value.state.item
  } 
  // Depois tenta do history.state
  else if (window.history.state?.item) {
    item.value = window.history.state.item
  }
  // Se ainda não tiver, tenta do sessionStorage
  else {
    const stored = sessionStorage.getItem('itemDetails')
    if (stored) {
      item.value = JSON.parse(stored)
      sessionStorage.removeItem('itemDetails')
    }
  }
  
  // Se ainda não tiver item, volta
  if (!item.value) {
    goBack()
    return
  }
  
  console.log('[ItemDetails] Item carregado:', item.value.name)

  // CRITICAL: Tentar buscar dados completos da fonte (URL, Size) se tivermos source_id
  // Isso corrige problemas onde o item vem de favoritos (partial) e a fonte não está carregada
  if (item.value.source_id && item.value.id) {
    try {
      console.log(`[ItemDetails] Tentando atualizar dados da fonte #${item.value.source_id} item #${item.value.id}`)
      const sourceResp = await api.get(`/api/sources/${item.value.source_id}/items/${item.value.id}`)
      if (sourceResp.data) {
        console.log('[ItemDetails] Dados da fonte atualizados com sucesso!', sourceResp.data)
        // Atualizar item com dados frescos (URL, Size, etc), mantendo o que já tinhamos
        item.value = { ...item.value, ...sourceResp.data }
      }
    } catch (e) {
      console.warn('[ItemDetails] Erro ao buscar dados frescos da fonte (pode ser normal se offline):', e)
    }
  }
  
  // Buscar detalhes completos de metadados (Steam/SteamGridDB)
  try {
    const detailsEndpoint = item.value.appId 
      ? `/api/game-details/${item.value.appId}`
      : `/api/game-details/${encodeURIComponent(item.value.name)}`
    
    console.log('[ItemDetails] Buscando detalhes em:', detailsEndpoint)
    
    const res = await api.get(detailsEndpoint)
    console.log('[ItemDetails] Resposta recebida (detalhes):', {
      found: res.data?.found,
      hasHeaderImage: !!res.data?.header_image,
      hasMovies: !!res.data?.movies && res.data.movies.length > 0,
      moviesCount: res.data?.movies?.length || 0
    })
    if (res.data?.movies && Array.isArray(res.data.movies)) {
      console.log('[ItemDetails] Lista bruta de filmes recebida da Steam:',
        res.data.movies.map((m, idx) => ({
          idx,
          name: m?.name,
          hasThumbnail: !!m?.thumbnail,
          thumbnail: m?.thumbnail,
          hasMp4: !!m?.mp4,
          mp4: m?.mp4,
          hasWebm: !!m?.webm,
          webm: m?.webm
        }))
      )
      console.log('[ItemDetails] CRÍTICO: Vídeos recebidos do backend:', res.data.movies.length)
      res.data.movies.forEach((v, i) => {
        console.log(`[ItemDetails] Vídeo ${i}: ${v.name} - MP4: ${v.mp4 ? 'SIM' : 'NÃO'} - Thumbnail: ${v.thumbnail ? 'SIM' : 'NÃO'}`)
      })
    } else {
      console.log('[ItemDetails] Nenhuma lista de filmes presente em res.data.movies')
      console.log('[ItemDetails] res.data:', res.data)
    }
    
    if (res.data && res.data.found) {
      console.log('[ItemDetails] ANTES de atribuir gameDetails:', {
        hasGameDetails: !!item.value.gameDetails,
        moviesCount: item.value.gameDetails?.movies?.length || 0
      })
      
      // CRÍTICO: Usar Object.assign para forçar reatividade Vue no .exe
      if (!item.value.gameDetails) {
        item.value.gameDetails = {}
      }
      Object.assign(item.value.gameDetails, res.data)
      
      console.log('[ItemDetails] DEPOIS de atribuir gameDetails (via Object.assign):', {
        hasGameDetails: !!item.value.gameDetails,
        moviesCount: item.value.gameDetails?.movies?.length || 0,
        movies: item.value.gameDetails?.movies
      })
      
      // Armazenar appId se conseguir
      if (res.data.app_id && !item.value.appId) {
        item.value.appId = res.data.app_id
      }
      
      // Carregar imagem de header
      const headerImg = res.data.header_image || res.data.image || item.value.header_image
      console.log('[ItemDetails] Header image:', {
        found: !!headerImg,
        isHttp: headerImg?.startsWith('http'),
        isExe: isExeEnv,
        willUseProxy: isExeEnv && headerImg?.startsWith('http')
      })
      
      if (headerImg) {
        // Sempre usar proxy para URLs externas http/https (unifica navegador e .exe)
        if (headerImg.startsWith('http')) {
          const baseUrl = getApiBaseUrl()
          headerImageUrl.value = `${baseUrl}/api/proxy/image?url=${encodeURIComponent(headerImg)}`
          console.log('[ItemDetails] Header image URL (proxy):', headerImageUrl.value.substring(0, 100))
        } else {
          headerImageUrl.value = headerImg
          console.log('[ItemDetails] Header image URL (direto/local):', headerImageUrl.value?.substring(0, 100))
        }
      }
    } else {
      console.warn('[ItemDetails] Detalhes não encontrados:', res.data)

    }
  } catch (e) {
    console.error('[ItemDetails] Erro ao buscar detalhes do jogo:', e)
  } finally {
    loadingDetails.value = false
  }
})

const additionalInfo = computed(() => {
  if (!item.value) return {}
  
  const excluded = [
    'name', 'description', 'image', 'header_image', 'category', 'uploadDate', 'size', 
    'source', 'magnet', 'torrent', 'seeders', 'leechers', 'language',
    'id', 'url', 'source_id', 'sourceId', 'source id', 'item_id', 'itemId'
  ]
  const info = {}
  
  for (const [key, value] of Object.entries(item.value)) {
    // Exclui campos na lista
    if (excluded.includes(key)) continue
    
    // Exclui valores vazios, null, undefined
    if (!value || value === '') continue
    
    // Exclui URLs/magnet links muito longas
    if (typeof value === 'string' && value.length > 200) continue
    
    // Exclui campos que parecem ser IDs
    if (typeof value === 'number' && value > 1000000000) continue
    
    info[key] = value
  }
  
  return info
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatSize = (bytes) => {
  if (!bytes) return 'N/A'
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const formatKey = (key) => {
  return key
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .trim()
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Erro ao copiar:', err)
  }
}

const downloadTorrent = () => {
  if (item.value?.magnet) {
    window.location.href = item.value.magnet
  }
}

const getVideoThumbnailUrl = (thumbnailUrl) => {
  if (!thumbnailUrl) return null

  // Sempre usar proxy para URLs http/https (tanto no navegador quanto no .exe)
  if (thumbnailUrl.startsWith('http')) {
    const baseUrl = getApiBaseUrl()
    const finalUrl = `${baseUrl}/api/proxy/image?url=${encodeURIComponent(thumbnailUrl)}`
    console.log('[ItemDetails] Thumbnail de vídeo via proxy de imagem:', {
      original: thumbnailUrl,
      proxied: finalUrl
    })
    return finalUrl
  }

  // Qualquer outra URL (local/relativa) é retornada como está
  return thumbnailUrl
}

const getScreenshotUrl = (screenshotUrl) => {
  if (!screenshotUrl) return null

  // Sempre usar proxy para URLs http/https
  if (screenshotUrl.startsWith('http')) {
    const baseUrl = getApiBaseUrl()
    return `${baseUrl}/api/proxy/image?url=${encodeURIComponent(screenshotUrl)}`
  }

  return screenshotUrl
}

const getProxyVideoUrl = (videoUrl) => {
  if (!videoUrl) return null

  // Usar URL direta para garantir melhor performance (sem engasgos) e áudio funcionando
  // O proxy estava causando problemas de buffering e codecs
  return videoUrl
}

const openVideo = async (video) => {
  if (!video) return

  console.log('[ItemDetails] openVideo chamado. Vídeo recebido:', {
    name: video?.name,
    mp4: video?.mp4,
    webm: video?.webm,
    isElectron: !!window.electronAPI
  })



  // We want to open the modal, not external player
  currentVideo.value = video
  showVideoModal.value = true
}

const currentVideoIndex = computed(() => {
  if (!item.value?.gameDetails?.movies || !currentVideo.value) return -1
  return item.value.gameDetails.movies.indexOf(currentVideo.value)
})

const hasNext = computed(() => {
  const movies = item.value?.gameDetails?.movies
  return movies && currentVideoIndex.value < movies.length - 1
})

const hasPrev = computed(() => {
  return currentVideoIndex.value > 0
})

const nextVideo = () => {
  if (hasNext.value) {
    // Apenas troca o vídeo. O :key no template forçará o reload do player.
    const nextVid = item.value.gameDetails.movies[currentVideoIndex.value + 1]
    currentVideo.value = nextVid
  }
}

const prevVideo = () => {
  if (hasPrev.value) {
    const prevVid = item.value.gameDetails.movies[currentVideoIndex.value - 1]
    currentVideo.value = prevVid
  }
}

const closeVideo = () => {
  showVideoModal.value = false
  currentVideo.value = null
  videoIframeHtml.value = null
}

const openVideoInBrowser = () => {
  if (!currentVideo.value) return
  
  // Usar URL original da Steam (sem proxy) para abrir no navegador externo
  const videoUrl = currentVideo.value.mp4 || currentVideo.value.webm
  
  if (videoUrl) {
    // Extrair URL original (remover proxy se existir)
    let originalUrl = videoUrl
    if (videoUrl.includes('/api/proxy/video?url=')) {
      const match = videoUrl.match(/url=(.+)$/)
      if (match) {
        originalUrl = decodeURIComponent(match[1])
      }
    }
    
    // Abrir em nova aba do navegador
    window.open(originalUrl, '_blank')
    console.log('[ItemDetails] Vídeo aberto em navegador:', originalUrl)
  }
}

const goBack = () => {
  router.back()
}

const scrollScreenshots = (direction) => {
  if (screenshotScrollRef.value) {
    const scrollAmount = 400
    if (direction === 'left') {
      screenshotScrollRef.value.scrollBy({ left: -scrollAmount, behavior: 'smooth' })
    } else {
      screenshotScrollRef.value.scrollBy({ left: scrollAmount, behavior: 'smooth' })
    }
  }
}

const onVideoLoadStart = () => {
  console.log('[ItemDetails] Video loadstart event disparado')
}

const onVideoCanPlay = () => {
  console.log('[ItemDetails] Video canplay event disparado - vídeo pronto para reprodução')
}

const onVideoError = (event) => {
  console.error('[ItemDetails] Video error event:', event)
  const videoEl = event.target
  if (videoEl?.error) {
    console.error('[ItemDetails] Video error code:', videoEl.error.code, videoEl.error.message)
  }
}

// ================= DOWNLOAD LOGIC =================
import SourceAnalysisModal from '../components/SourceAnalysisModal.vue'

// ... (other imports)

// Analysis State
const showAnalysisModal = ref(false)
const analysisCandidates = ref([])
const analysisOriginalItem = ref(null)
const analysisLoading = ref(false)

// ...

// ================= DOWNLOAD LOGIC =================

const startDownloadFlow = async () => {
  if (!item.value) return
  
  // 1. Pre-Job Analysis (Optional/Intelligent Layer)
  analysisOriginalItem.value = item.value
  analysisCandidates.value = []
  analysisLoading.value = true
  showAnalysisModal.value = true // Open immediately
  
  try {
    const resp = await api.post('/api/analysis/pre-job', { item: item.value })
    if (resp.data && resp.data.candidates && resp.data.candidates.length > 0) {
      // Found alternatives -> Show Modal Content
      analysisCandidates.value = resp.data.candidates
      
      const enrichedOriginal = { ...item.value }
      if (resp.data.original_health) {
         enrichedOriginal.health = resp.data.original_health
         if (resp.data.original_health.seeders !== undefined) {
             enrichedOriginal.seeders = resp.data.original_health.seeders
             enrichedOriginal.leechers = resp.data.original_health.leechers
         }
      }
      
      analysisOriginalItem.value = enrichedOriginal
      analysisLoading.value = false
      return
    }
  } catch (e) {
    console.warn('[ItemDetails] Analysis failed, proceeding to direct download:', e)
  } finally {
     // analysisLoading handled inside
  }

  // 2. Direct Download (if no alternatives or analysis failed)
  // Close the loading modal
  showAnalysisModal.value = false
  analysisLoading.value = false
  openDownloadConfigurationModal()
}

const onAnalysisConfirm = (selectedItem) => {
  // Update the item to be downloaded with the selected one (might be original or swap)
  item.value = selectedItem
  showAnalysisModal.value = false
  
  // Proceed to configuration
  openDownloadConfigurationModal()
}

const openDownloadConfigurationModal = () => {
  console.log('[ItemDetails] Abrindo modal de download')
  if (!item.value) return

  downloadDestination.value = 'downloads'
  modalInfo.value = { size: null, accept_range: false, eta: null, checking: true }
  
  // Tentar obter info extra de tamanho
  if (item.value.url) {
    const url = encodeURIComponent(item.value.url)
    api.get(`/api/supports_range?url=${url}`).then(({ data }) => {
      modalInfo.value.size = data.size || null
      modalInfo.value.accept_range = !!data.accept_ranges
      if (data.size && modalInfo.value.accept_range) {
        const baseline = 1024 * 1024 // 1MB/s estimate
        modalInfo.value.eta = Math.round((data.size / baseline))
      }
    }).catch(err => {
      console.warn('supports_range failed', err)
    }).finally(() => {
      modalInfo.value.checking = false
    })
  } else {
    modalInfo.value.checking = false
  }

  showDownloadDialog.value = true
}

const browsePath = async () => {
  browseLoading.value = true
  try {
    if (window.electronAPI?.selectFolder) {
      const folder = await window.electronAPI.selectFolder()
      if (folder) downloadDestination.value = folder
      browseLoading.value = false
      return
    }
    const resp = await api.post('/api/dialog/select_folder')
    if (resp.data && resp.data.path) {
      downloadDestination.value = resp.data.path
      return
    }
    // canceled or no path -> open manual modal
    manualFolderPath.value = downloadDestination.value || ''
    showManualFolderModal.value = true
  } catch (e) {
    console.warn('Folder picker failed:', e)
    manualFolderPath.value = downloadDestination.value || ''
    showManualFolderModal.value = true
  } finally {
    browseLoading.value = false
  }
}

const confirmDownload = async () => {
  if (!item.value) return
  
  try {
    let destCandidate = (downloadDestination.value || 'downloads').toString()
    // Validacao basica
    const destLower = destCandidate.toLowerCase()
    if (destLower.startsWith('http') || destLower.startsWith('magnet:')) {
       destCandidate = 'downloads'
    }

    // Default verify_ssl true se nao houver config
    const sourceId = item.value.source_id
    const verifySsl = (downloadVerifySsl.value[sourceId] !== false) ?? true

    const jobData = {
      url: item.value.url,
      name: item.value.name,
      destination: destCandidate,
      verify_ssl: verifySsl,
      size: item.value.size || null
    }

    const result = await downloadStore.createJob(jobData)
    if (result && result.job_id) {
       showDownloadDialog.value = false
       try { const ts = useToastStore(); ts.push('Download Iniciado', `O download de "${item.value.name}" começou!`) } catch (e) {}
    }
  } catch (e) {
    console.error('Erro ao iniciar download:', e)
    try { const ts = useToastStore(); ts.push('Erro', `Falha ao iniciar: ${e.message}`) } catch (ee) { alert(e.message) }
  }
}
</script>

<style scoped>
/* Animações customizadas */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.animate-in) {
  animation: slideIn 0.3s ease-out;
}

/* Esconder scrollbar mas manter funcionalidade */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
