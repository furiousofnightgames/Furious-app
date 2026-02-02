<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 relative overflow-hidden">
    <!-- Animated background particles -->
    <div class="absolute inset-0 opacity-30 pointer-events-none">
      <div class="absolute top-20 left-20 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-[128px] animate-blob"></div>
      <div class="absolute top-40 right-20 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-[128px] animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-20 left-40 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-[128px] animate-blob animation-delay-4000"></div>
    </div>
    
    <!-- Header com gradiente premium -->
    <div class="relative overflow-hidden pb-0">
      <!-- Gradiente overlay superior -->
      <div class="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-transparent pointer-events-none z-[5]"></div>
      
      <!-- Botão voltar premium -->
      <div class="absolute top-6 left-6 z-20">
        <button 
          @click="goBack"
          class="group flex items-center gap-2 px-5 py-2.5 bg-slate-900/60 hover:bg-slate-800/80 backdrop-blur-xl rounded-xl transition-all duration-300 text-cyan-400 hover:text-cyan-300 border border-slate-700/50 hover:border-cyan-500/30 shadow-lg hover:shadow-cyan-500/20"
        >
          <svg class="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          <span class="font-medium">Voltar</span>
        </button>
      </div>

      <!-- Imagem principal premium com efeitos -->
      <div v-if="headerImageUrl" class="pt-20 px-4 md:px-8 flex justify-center relative">
        <!-- Glow effect atrás da imagem -->
        <div class="absolute inset-0 flex justify-center items-center">
          <div class="w-full max-w-5xl h-96 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 blur-3xl"></div>
        </div>
        <img
          :src="headerImageUrl"
          alt="Header do jogo"
          class="relative w-full max-w-6xl max-h-[500px] rounded-3xl shadow-2xl shadow-black/50 border border-slate-700/50 object-contain object-center transition-transform hover:scale-[1.02] duration-500"
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
        <!-- Card principal premium -->
        <div class="bg-gradient-to-br from-slate-800/95 to-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 mb-8 shadow-[0_20px_70px_-10px_rgba(0,0,0,0.7)] hover:shadow-[0_30px_90px_-10px_rgba(6,182,212,0.3)] transition-all duration-500 animate-fade-in-up">
          <!-- Título e informações básicas -->
          <div class="mb-8">
            <!-- Alerta de Fonte Alternativa (SteamGridDB) -->
            <div v-if="item?.gameDetails?.source === 'steamgriddb' && !item?.gameDetails?.not_found_on_store" class="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-start gap-4 animate-in">
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

            <!-- Alerta de Jogo Não Encontrado (Placeholder) -->
            <div v-if="item?.gameDetails?.not_found_on_store" class="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-start gap-4 animate-in">
              <div class="p-2 bg-rose-500/20 rounded-full text-rose-500 shrink-0">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-rose-200">Dados Não Encontrados</h3>
                <p class="text-rose-200/70 text-sm mt-1">
                  Não foram encontrados dados técnicos ou artes para este jogo na Steam ou no acervo da comunidade. Usando um identificador genérico para organização.
                </p>
              </div>
            </div>

            <div class="flex items-start justify-between gap-4 mb-4">
              <h1 class="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-cyan-50 to-purple-100 bg-clip-text text-transparent drop-shadow-lg leading-tight">{{ item?.name }}</h1>
              <div class="flex-shrink-0">
                <FavoriteToggleButton v-if="item" :item="item" />
              </div>
            </div>
            
            <!-- Badges de informação -->
            <div class="flex flex-wrap gap-3 mb-6">
              <span v-if="item?.category" class="px-4 py-2 bg-gradient-to-r from-cyan-500/30 to-blue-500/30 border border-cyan-400/50 rounded-xl text-cyan-200 text-sm font-semibold shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transition-all hover:scale-105">
                {{ item.category }}
              </span>
              <span v-if="item?.uploadDate" class="px-4 py-2 bg-gradient-to-r from-purple-500/30 to-pink-500/30 border border-purple-400/50 rounded-xl text-purple-200 text-sm font-semibold shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 transition-all hover:scale-105">
                {{ formatDate(item.uploadDate) }}
              </span>
              <span v-if="item?.size" class="px-4 py-2 bg-gradient-to-r from-amber-500/30 to-orange-500/30 border border-amber-400/50 rounded-xl text-amber-200 text-sm font-semibold shadow-lg shadow-amber-500/20 hover:shadow-amber-500/40 transition-all hover:scale-105">
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
              <!-- Source removed as per user request (redundant) -->

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

        <!-- Vídeos da Steam - Carousel Horizontal -->
        <div v-if="item?.gameDetails?.movies && item.gameDetails.movies.length > 0" class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-6">Vídeos ({{ item.gameDetails.movies.length }})</h2>
          <div class="relative">
            <!-- Seta esquerda -->
            <button 
              @click="scrollVideos('left')"
              class="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 hover:bg-black/80 text-white p-2 rounded-full transition"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <!-- Container do carousel -->
            <div ref="videoScrollRef" class="overflow-x-auto pb-4 scrollbar-hide">
              <div class="flex gap-6 min-w-max px-12">
                <div
                  v-for="(video, idx) in item.gameDetails.movies"
                  :key="idx"
                  class="group cursor-pointer flex-shrink-0"
                  @click="openVideo(video)"
                >
                  <!-- Debug: mostrar dados do vídeo -->
                  <div style="display: none;">
                    {{ console.log(`[Template] Renderizando vídeo ${idx}:`, video) }}
                  </div>
                  <div class="relative overflow-hidden rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 w-80 h-48 mb-3">
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
                  <p class="text-white font-semibold text-sm w-80 truncate">{{ video.name }}</p>
                </div>
              </div>
            </div>

            <!-- Seta direita -->
            <button 
              @click="scrollVideos('right')"
              class="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-black/50 hover:bg-black/80 text-white p-2 rounded-full transition"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
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
                      @click="openScreenshot(idx)"
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

        <!-- Sobre o Jogo (Rich HTML Description) -->
        <div v-if="item?.gameDetails?.about_the_game" class="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <svg class="w-7 h-7 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Sobre o Jogo
          </h2>
          <div 
            class="prose prose-invert prose-slate max-w-none text-slate-300 leading-relaxed about-game-content"
            v-html="processedAboutTheGame"
          ></div>
        </div>


        <!-- Card Unificado: Especificações Técnicas Premium -->
        <div v-if="item?.gameDetails?.found" class="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-md border border-slate-700/50 rounded-2xl p-8 mb-8 shadow-2xl shadow-black/30">
          <h2 class="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent mb-8 flex items-center gap-3">
            <div class="p-2 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl border border-amber-500/30">
              <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            Especificações Técnicas
          </h2>

          <!-- Grid Principal: 2 Colunas -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            <!-- Coluna Esquerda: Requisitos -->
            <div v-if="item?.gameDetails?.pc_requirements && (item.gameDetails.pc_requirements.minimum || item.gameDetails.pc_requirements.recommended)" class="space-y-5">
              <h3 class="text-lg font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 flex items-center gap-2">
                <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Requisitos de Sistema
              </h3>
              
              <!-- Mínimo -->
              <div v-if="item.gameDetails.pc_requirements.minimum" class="group bg-gradient-to-br from-slate-900/60 to-slate-950/60 backdrop-blur-sm border border-slate-700/50 hover:border-cyan-500/30 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10">
                <h4 class="text-sm font-bold text-cyan-400 mb-3 flex items-center gap-2">
                  <span class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>
                  Mínimo
                </h4>
                <div class="prose prose-xs prose-invert prose-slate max-w-none text-slate-300 text-xs leading-relaxed" v-html="item.gameDetails.pc_requirements.minimum"></div>
              </div>

              <!-- Recomendado -->
              <div v-if="item.gameDetails.pc_requirements.recommended" class="group bg-gradient-to-br from-slate-900/60 to-slate-950/60 backdrop-blur-sm border border-slate-700/50 hover:border-emerald-500/30 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10">
                <h4 class="text-sm font-bold text-emerald-400 mb-3 flex items-center gap-2">
                  <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                  Recomendado
                </h4>
                <div class="prose prose-xs prose-invert prose-slate max-w-none text-slate-300 text-xs leading-relaxed" v-html="item.gameDetails.pc_requirements.recommended"></div>
              </div>
            </div>

            <!-- Coluna Direita: Idiomas + Info Técnica -->
            <div class="space-y-5">
              
              <!-- Idiomas -->
              <div v-if="dubbedLanguages.length > 0 || subtitledLanguages.length > 0">
                <h3 class="text-lg font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent mb-4 flex items-center gap-2">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                  </svg>
                  Idiomas
                </h3>

                <!-- Dublados -->
                <div v-if="dubbedLanguages.length > 0" class="mb-4">
                  <p class="text-xs text-cyan-400 font-semibold mb-2 flex items-center gap-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
                    </svg>
                    Áudio Completo (Dublagem)
                  </p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="(lang, idx) in dubbedLanguages" :key="idx" class="px-3 py-1.5 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-400/40 rounded-lg text-xs text-cyan-300 font-medium shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20 transition-shadow">
                      {{ lang }}
                    </span>
                  </div>
                </div>

                <!-- Apenas Legendas -->
                <div v-if="subtitledLanguages.length > 0">
                  <p class="text-xs text-slate-400 font-semibold mb-2 flex items-center gap-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                    </svg>
                    Interface / Legendas
                  </p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="(lang, idx) in subtitledLanguages" :key="idx" class="px-3 py-1.5 bg-slate-800/60 border border-slate-600/40 rounded-lg text-xs text-slate-400 hover:text-slate-300 hover:border-slate-500/50 transition-colors">
                      {{ lang }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Informações Técnicas Compactas Premium -->
              <div class="bg-gradient-to-br from-slate-900/60 to-slate-950/60 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 space-y-3 shadow-lg">
                <div v-if="item.gameDetails.controller_support && item.gameDetails.controller_support !== 'none'" class="flex items-center justify-between text-sm group hover:bg-slate-800/30 p-2 rounded-lg transition-colors">
                  <span class="text-slate-400 flex items-center gap-2">
                    <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    </svg>
                    Controle
                  </span>
                  <span class="text-white font-semibold">{{ item.gameDetails.controller_support === 'full' ? 'Suporte Completo' : 'Parcial' }}</span>
                </div>
                <div v-if="item.gameDetails.developers && item.gameDetails.developers.length > 0" class="flex items-center justify-between text-sm group hover:bg-slate-800/30 p-2 rounded-lg transition-colors">
                  <span class="text-slate-400">Desenvolvedora</span>
                  <span class="text-white font-semibold truncate ml-2" :title="item.gameDetails.developers.join(', ')">{{ item.gameDetails.developers.join(', ') }}</span>
                </div>
                <div v-if="item.gameDetails.publishers && item.gameDetails.publishers.length > 0" class="flex items-center justify-between text-sm group hover:bg-slate-800/30 p-2 rounded-lg transition-colors">
                  <span class="text-slate-400">Publicadora</span>
                  <span class="text-white font-semibold truncate ml-2" :title="item.gameDetails.publishers.join(', ')">{{ item.gameDetails.publishers.join(', ') }}</span>
                </div>
                <div v-if="item.gameDetails.release_date" class="flex items-center justify-between text-sm group hover:bg-slate-800/30 p-2 rounded-lg transition-colors">
                  <span class="text-slate-400">Lançamento</span>
                  <span class="text-white font-semibold">{{ item.gameDetails.release_date }}</span>
                </div>
                <div v-if="item.gameDetails.metacritic_score" class="flex items-center justify-between text-sm group hover:bg-slate-800/30 p-2 rounded-lg transition-colors">
                  <span class="text-slate-400 flex items-center gap-2">
                    <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    Metacritic
                  </span>
                  <span class="text-xl font-bold" :style="{ color: getMetacriticColor(item.gameDetails.metacritic_score) }">{{ item.gameDetails.metacritic_score }}</span>
                </div>
              </div>
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

          <div 
            class="relative w-full max-w-4xl mx-4 aspect-video bg-black rounded-xl overflow-hidden transition-all duration-300"
            style="box-shadow: 0 0 60px rgba(6, 182, 212, 0.6), 0 0 30px rgba(6, 182, 212, 0.4), 0 25px 50px -12px rgba(0, 0, 0, 0.9); border: 2px solid rgba(6, 182, 212, 0.5);"
          >
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
            <div :key="currentVideo.name" v-if="currentVideo.hls || currentVideo.mp4 || currentVideo.webm" class="w-full h-full flex items-center justify-center bg-black">
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
                <!-- Priorizar HLS (formato moderno com áudio) -->
                <source v-if="currentVideo.hls" :src="getProxyVideoUrl(currentVideo.hls)" type="application/x-mpegURL" />
                <!-- Fallback para formatos legados -->
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

        <!-- Modal de Galeria de Screenshots (Preview Premium) -->
        <div v-if="showScreenshotModal && item?.gameDetails?.screenshots" class="fixed inset-0 z-50 flex items-center justify-center bg-black/95" @click.self="closeScreenshot">
          
          <!-- Botão Anterior (Overlay) -->
          <button 
            v-if="currentScreenshotIdx > 0"
            @click.stop="prevScreenshot"
            class="absolute left-4 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition backdrop-blur-md group"
          >
            <svg class="w-8 h-8 opacity-70 group-hover:opacity-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div 
            class="relative w-full max-w-4xl mx-4 overflow-hidden rounded-xl bg-black transition-all duration-300 flex items-center justify-center group/img"
            style="box-shadow: 0 0 60px rgba(6, 182, 212, 0.6), 0 0 30px rgba(6, 182, 212, 0.4), 0 25px 50px -12px rgba(0, 0, 0, 0.9); border: 2px solid rgba(6, 182, 212, 0.5);"
          >
            <!-- Botão Fechar (X) -->
            <button
              class="absolute top-4 right-4 text-white/70 hover:text-white z-20 bg-black/50 hover:bg-black/80 rounded-full p-2 transition backdrop-blur-sm shadow-xl"
              @click="closeScreenshot"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <!-- Imagem -->
            <img 
              :key="currentScreenshotIdx"
              :src="getScreenshotUrl(item.gameDetails.screenshots[currentScreenshotIdx])"
              class="w-full h-auto max-h-[85vh] object-contain select-none animate-fade-in"
              style="will-change: opacity;"
            />
            
            <!-- Info Overlay (Sutil ao passar o mouse) -->
            <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent pointer-events-none opacity-0 group-hover/img:opacity-100 transition-opacity">
              <p class="text-white/60 text-xs text-center font-medium">Screenshot {{ currentScreenshotIdx + 1 }} de {{ item.gameDetails.screenshots.length }}</p>
            </div>
          </div>

          <!-- Botão Próximo (Overlay) -->
          <button 
            v-if="currentScreenshotIdx < item.gameDetails.screenshots.length - 1"
            @click.stop="nextScreenshot"
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

  <!-- MODAL DE DOWNLOAD PREMIUM -->
  <PremiumDownloadModal
    :is-open="showDownloadDialog"
    :item="item"
    :image-url="headerImageUrl"
    :destination="downloadDestination"
    :browse-loading="browseLoading"
    :loading="downloadStore.loading"
    :free-space-info="freeSpaceInfo"
    :estimated-required-space="estimatedRequiredSpace"
    :is-repack-detected="isRepackDetected"
    :is-placeholder-size="isPlaceholderSize"
    :has-enough-space="hasEnoughSpace"
    :modal-info="modalInfo"
    :preflight-loading="preflightLoading"
    :preflight-error="preflightError"
    :preflight-result="preflightResult"
    :preflight-aria2="preflightAria2"
    :preflight-health="preflightHealth"
    @close="showDownloadDialog = false"
    @confirm="confirmDownload"
    @browse="browsePath"
    @refresh-preflight="runPreflightForce"
  />

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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import { useDownloadStore } from '../stores/download'
import { useToastStore } from '../stores/toast'
import { formatBytes } from '../utils/format'
import Modal from '../components/Modal.vue'
import PremiumDownloadModal from '../components/PremiumDownloadModal.vue'
import Input from '../components/Input.vue'
import Button from '../components/Button.vue'
import FavoriteToggleButton from '../components/FavoriteToggleButton.vue'
import Hls from 'hls.js'

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
const videoScrollRef = ref(null)
const showVideoModal = ref(false)
const currentVideo = ref(null)
const headerImageUrl = ref(null)

// Screenshot Gallery Refs
const showScreenshotModal = ref(false)
const currentScreenshotIdx = ref(0)

const openScreenshot = (idx) => {
  currentScreenshotIdx.value = idx
  showScreenshotModal.value = true
  document.addEventListener('keydown', handleScreenshotKeys)
}

const closeScreenshot = () => {
  showScreenshotModal.value = false
  document.removeEventListener('keydown', handleScreenshotKeys)
}

const nextScreenshot = () => {
  if (currentScreenshotIdx.value < item.value.gameDetails.screenshots.length - 1) {
    currentScreenshotIdx.value++
  }
}

const prevScreenshot = () => {
  if (currentScreenshotIdx.value > 0) {
    currentScreenshotIdx.value--
  }
}

const handleScreenshotKeys = (e) => {
  if (e.key === 'ArrowRight') nextScreenshot()
  if (e.key === 'ArrowLeft') prevScreenshot()
  if (e.key === 'Escape') closeScreenshot()
}

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
const freeSpaceInfo = ref(null)

const isRepackDetected = computed(() => {
  return item.value?.name?.toLowerCase().includes('repack') || 
         item.value?.source?.toLowerCase().includes('fitgirl') ||
         item.value?.source?.toLowerCase().includes('dodi')
})

const estimatedRequiredSpace = computed(() => {
  const size = item.value?.size || modalInfo.value.size || 0
  if (!size) return 0
  // FIX: Reduced from 2.5 to 1.25 to avoid blocking users with tight but sufficient space.
  // Although installation needs more, the download itself should be allowed.
  return isRepackDetected.value ? size * 1.25 : size * 1.1
})

const isPlaceholderSize = computed(() => {
  const size = item.value?.size || modalInfo.value.size || 0
  if (!size) return false
  if (size < 10 * 1024 * 1024) return true
  const suspiciousKeywords = ['collection', 'all games']
  const isSuspiciousName = suspiciousKeywords.some(k => item.value?.name?.toLowerCase().includes(k))
  if (isSuspiciousName && size < 1024 * 1024 * 1024 * 30) { 
    return true
  }
  return false
})

const hasEnoughSpace = computed(() => {
  if (!freeSpaceInfo.value || !estimatedRequiredSpace.value) return true
  return freeSpaceInfo.value.free > estimatedRequiredSpace.value
})

async function checkDiskSpace() {
  try {
    const path = downloadDestination.value || 'downloads'
    const info = await downloadStore.getDiskSpace(path)
    if (info && info.status === 'success') {
      freeSpaceInfo.value = info
    }
  } catch (e) {
    console.error('[ItemDetails] Erro ao checar espaço:', e)
  }
}

watch(downloadDestination, () => {
  checkDiskSpace()
})

const preflightLoading = ref(false)
const preflightResult = ref(null)
const preflightError = ref(null)
const preflightAria2 = ref(null)
const preflightHealth = ref(null)
const preflightHealthLabel = computed(() => {
  const h = preflightHealth.value
  if (!h) return ''
  const s = Number(h.seeders ?? 0)
  if (Number.isFinite(s)) {
    if (s >= 20) return 'Saudável'
    if (s >= 5) return 'Ok'
    if (s >= 1) return 'Baixa'
    return 'Crítica'
  }
  return 'Desconhecida'
})


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
const processedAboutTheGame = computed(() => {
  if (!item.value?.gameDetails?.about_the_game) return ''
  
  let html = item.value.gameDetails.about_the_game
  
  // Usar DOMParser para manipular o HTML de forma segura
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  
  // Processar todas as imagens
  const images = doc.querySelectorAll('img')
  const baseUrl = getApiBaseUrl()
  
  images.forEach(img => {
    const src = img.getAttribute('src')
    if (src && src.startsWith('http')) {
      // Usar proxy para evitar problemas de CORS e erros de carregamento
      // Codificar a URL corretamente
      const proxyUrl = `${baseUrl}/api/proxy/image?url=${encodeURIComponent(src)}`
      img.setAttribute('src', proxyUrl)
      
      // Também corrigir data-src se existir (comum em lazy loading)
      const dataSrc = img.getAttribute('data-src')
      if (dataSrc && dataSrc.startsWith('http')) {
         img.setAttribute('data-src', `${baseUrl}/api/proxy/image?url=${encodeURIComponent(dataSrc)}`)
      }
    }
  })
  
  // Retornar o HTML processado
  return doc.body.innerHTML
})

// ================= VIDEO PLAYER LOGIC =================
const openVideo = async (video) => {
  if (!video) return

  console.log('[ItemDetails] openVideo chamado. Vídeo recebido:', {
    name: video?.name,
    hls: video?.hls,
    mp4: video?.mp4,
    webm: video?.webm,
    isElectron: !!window.electronAPI
  })

  // Abrir modal
  currentVideo.value = video
  showVideoModal.value = true
}

// Variável para armazenar instância do HLS
let hlsInstance = null

// Watch para inicializar HLS quando o vídeo mudar
watch([showVideoModal, currentVideo], async ([isOpen, video]) => {
  // Limpar instância anterior
  if (hlsInstance) {
    hlsInstance.destroy()
    hlsInstance = null
  }

  if (!isOpen || !video) return

  // Aguardar próximo tick para garantir que o elemento de vídeo foi renderizado
  await nextTick()

  const videoElement = document.querySelector('.w-full.h-full.object-contain')
  if (!videoElement) {
    console.warn('[ItemDetails] Elemento de vídeo não encontrado')
    return
  }

  // Se o vídeo for HLS, usar hls.js
  if (video.hls) {
    const hlsUrl = getProxyVideoUrl(video.hls)
    console.log('[ItemDetails] Inicializando HLS player para:', hlsUrl)

    if (Hls.isSupported()) {
      hlsInstance = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        // Otimizações para fluidez (Smoothness)
        maxBufferLength: 30, // Aumentar buffer para 30s
        maxMaxBufferLength: 60,
        capLevelToPlayerSize: true, // Limitar qualidade ao tamanho do player para economizar recursos
        startLevel: -1, // Auto start level
        abrEwmaDefaultEstimate: 5000000, // Estimativa inicial de banda (5mbps)
      })

      hlsInstance.loadSource(hlsUrl)
      hlsInstance.attachMedia(videoElement)

      hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log('[ItemDetails] HLS manifest carregado, iniciando reprodução')
        videoElement.play().catch(e => console.warn('[ItemDetails] Autoplay bloqueado:', e))
      })

      hlsInstance.on(Hls.Events.ERROR, (event, data) => {
        console.error('[ItemDetails] HLS Error:', data)
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.error('[ItemDetails] Fatal network error, tentando recuperar...')
              hlsInstance.startLoad()
              break
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.error('[ItemDetails] Fatal media error, tentando recuperar...')
              hlsInstance.recoverMediaError()
              break
            default:
              console.error('[ItemDetails] Erro fatal irrecuperável')
              hlsInstance.destroy()
              break
          }
        }
      })
    } else if (videoElement.canPlayType('application/vnd.apple.mpegurl')) {
      // Safari nativo suporta HLS
      videoElement.src = hlsUrl
      videoElement.addEventListener('loadedmetadata', () => {
        videoElement.play().catch(e => console.warn('[ItemDetails] Autoplay bloqueado:', e))
      })
    } else {
      console.error('[ItemDetails] HLS não suportado neste navegador')
    }
  }
}, { immediate: true })


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
  
  // Priorizar HLS (formato moderno com áudio) sobre MP4/WebM legados
  const videoUrl = currentVideo.value.hls || currentVideo.value.mp4 || currentVideo.value.webm
  
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

const scrollVideos = (direction) => {
  if (videoScrollRef.value) {
    const scrollAmount = 400
    if (direction === 'left') {
      videoScrollRef.value.scrollBy({ left: -scrollAmount, behavior: 'smooth' })
    } else {
      videoScrollRef.value.scrollBy({ left: scrollAmount, behavior: 'smooth' })
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

  preflightError.value = null
  preflightResult.value = null
  preflightAria2.value = null
  preflightHealth.value = null
  
  // Tentar obter info extra de tamanho
  const urlRaw = (item.value.url || '').toString().trim()
  if (urlRaw && urlRaw.startsWith('magnet:')) {
    // Magnet: size/ETA via HTTP range does not apply. Run pre-flight automatically.
    modalInfo.value.checking = false
    preflightLoading.value = true
    ;(async () => {
      try {
        const aria2Resp = await api.get('/api/aria2/status')
        preflightAria2.value = aria2Resp.data || null
      } catch (e) {
        preflightAria2.value = null
      }

      try {
        const healthResp = await api.post('/api/magnet/health', { url: urlRaw })
        preflightHealth.value = healthResp.data || null
      } catch (e) {
        preflightHealth.value = { seeders: item.value?.seeders ?? null, leechers: item.value?.leechers ?? null }
      }

      preflightResult.value = { accept_ranges: false, size: null, status_code: null, note: 'Magnet links use aria2' }
      preflightError.value = null
      preflightLoading.value = false
    })().catch(() => {
      preflightLoading.value = false
    })
  } else if (urlRaw) {
    // HTTP/HTTPS
    const url = encodeURIComponent(urlRaw)
    api.get(`/api/supports_range?url=${url}`).then(({ data }) => {
      modalInfo.value.size = data.size || null
      modalInfo.value.accept_range = !!data.accept_ranges
      preflightResult.value = data || null
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
  checkDiskSpace() // Check space immediately on open
}

const runPreflightForce = async () => {
  preflightError.value = null
  preflightResult.value = null
  preflightAria2.value = null
  preflightHealth.value = null

  const urlRaw = (item.value?.url || '').toString().trim()
  if (!urlRaw) {
    preflightError.value = 'URL inválida para análise.'
    return
  }

  preflightLoading.value = true
  try {
    if (urlRaw.startsWith('magnet:')) {
      const aria2Resp = await api.get('/api/aria2/status')
      preflightAria2.value = aria2Resp.data || null

      const healthResp = await api.post('/api/magnet/health', { url: urlRaw, force_refresh: true })
      console.log('[ITEMDETAILS] Resposta force_refresh:', healthResp.data)
      preflightHealth.value = healthResp.data || null
      preflightResult.value = { accept_ranges: false, size: null, status_code: null, note: 'Magnet links use aria2' }
    } else {
      const resp = await api.get('/api/supports_range', { params: { url: urlRaw } })
      preflightResult.value = resp.data || null
    }
  } catch (e) {
    preflightError.value = e?.message || 'Falha ao analisar URL'
  } finally {
    preflightLoading.value = false
  }
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
       
       console.log('[ItemDetails] Job criado com sucesso, redirecionando para /downloads')
       await nextTick()
       router.push('/downloads')
    }
  } catch (e) {
    console.error('Erro ao iniciar download:', e)
    try { const ts = useToastStore(); ts.push('Erro', `Falha ao iniciar: ${e.message}`) } catch (ee) { alert(e.message) }
  }
}

// Helper function para cor dinâmica do Metacritic
const getMetacriticColor = (score) => {
  if (score >= 75) return '#66cc33' // Verde (bom)
  if (score >= 50) return '#ffcc33' // Amarelo (médio)
  return '#ff6666' // Vermelho (ruim)
}

// Computed property para parsear idiomas do HTML
const parsedLanguages = computed(() => {
  const langs = item.value?.gameDetails?.supported_languages
  if (!langs) return []
  
  // Remover tags HTML mas preservar asteriscos que indicam áudio completo
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = langs
  const text = tempDiv.textContent || tempDiv.innerText || ''
  
  // Dividir por vírgulas e processar cada idioma
  return text
    .split(',')
    .map(lang => {
      const trimmed = lang.trim()
      // Verificar se tem asterisco (áudio completo/dublagem)
      const hasFullAudio = trimmed.includes('*')
      const cleanName = trimmed.replace(/\*/g, '').trim()
      
      // Ignorar linhas de rodapé explicativas
      if (cleanName.toLowerCase().includes('idiomas com suporte') || 
          cleanName.toLowerCase().includes('languages with full') ||
          cleanName.length === 0) {
        return null
      }
      
      return {
        name: cleanName,
        hasFullAudio: hasFullAudio
      }
    })
    .filter(lang => lang !== null)
    .slice(0, 30) // Limitar a 30 idiomas
})

// Idiomas com dublagem completa
const dubbedLanguages = computed(() => {
  return parsedLanguages.value
    .filter(lang => lang.hasFullAudio)
    .map(lang => lang.name)
})

// Idiomas apenas com legendas/interface
const subtitledLanguages = computed(() => {
  return parsedLanguages.value
    .filter(lang => !lang.hasFullAudio)
    .map(lang => lang.name)
})
</script>

<style scoped>
/* Animações Premium */
@keyframes blob {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animate-fade-in-up {
  animation: fade-in-up 0.8s ease-out forwards;
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

/* Centralizar imagens e vídeos na seção "Sobre o Jogo" */
.about-game-content :deep(img),
.about-game-content :deep(video),
.about-game-content :deep(.bb_img_ctn) {
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
  text-align: center; /* Para spans */
}

/* Aplicar estilo visual APENAS nas mídias, NÃO nos containers */
.about-game-content :deep(img),
.about-game-content :deep(video) {
  max-width: 95% !important; /* Limitar largura */
  max-height: 600px !important; /* Limitar altura máxima */
  width: auto !important; /* Manter proporção */
  height: auto !important; /* Manter proporção */
  object-fit: contain !important; /* Garantir que caiba */
  
  /* Moldura Premium - Apenas na midia real */
  border-radius: 12px;
  border: 1px solid rgba(167, 243, 208, 0.2); 
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.5), 
    0 0 15px rgba(6, 182, 212, 0.15); 
  
  transition: all 0.3s ease;
}

/* Remover qualquer estilo visual do container para não ficar um quadrado feio */
.about-game-content :deep(.bb_img_ctn) {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.about-game-content :deep(img):hover,
.about-game-content :deep(video):hover {
  transform: scale(1.01);
  box-shadow: 
    0 10px 20px -5px rgba(0, 0, 0, 0.6), 
    0 0 30px rgba(6, 182, 212, 0.5); /* Glow mais forte no hover */
  border-color: rgba(34, 211, 238, 0.8);
}


/* Tentar centralizar containers que possam ter sobrado */
.about-game-content :deep(p) {
  text-align: left; /* Manter texto alinhado a esquerda */
}

/* Mas se o P tiver apenas imagem/video, centralizar (se suportado) */
.about-game-content :deep(p:has(img)),
.about-game-content :deep(p:has(video)) {
  text-align: center;
}
</style>
