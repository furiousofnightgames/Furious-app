<template>
  <div class="space-y-12 pb-8 px-1 lg:px-0">
    <!-- Header Section: Advanced Responsive Layout -->
    <div class="flex flex-col gap-10">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
        <div class="space-y-2">
          <h1 class="text-4xl sm:text-6xl font-black tracking-tight uppercase italic text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-400 to-blue-500 drop-shadow-[0_4px_12px_rgba(34,211,238,0.3)] pr-4">
            Biblioteca
          </h1>
          <div class="flex items-center gap-6 text-[10px] sm:text-xs font-black uppercase tracking-[0.2em] text-slate-500/80">
            <div v-if="formattedBuiltAt" class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-500/40 animate-pulse"></span>
              Sincronização: <span class="text-slate-400">{{ formattedBuiltAt }}</span>
            </div>
          </div>
        </div>

        <div class="w-full lg:w-auto flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <Input 
            v-model="searchQuery" 
            placeholder="PROCURAR..." 
            class="flex-1 sm:flex-none h-14"
            clearable
            showSearch
            inputClass="h-14 bg-slate-900/90 border-white/10 text-white font-black tracking-[0.15em] placeholder:text-slate-700 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 rounded-xl px-6 shadow-2xl transition-all text-sm" 
          />
          
          <div class="flex items-center gap-3 h-14">
            <router-link to="/sources" class="h-full">
              <button class="h-full px-6 bg-slate-900 shadow-xl hover:bg-slate-800 border border-white/10 rounded-xl text-white text-[11px] font-black uppercase tracking-widest transition-all active:scale-95 flex items-center justify-center">
                Fontes
              </button>
            </router-link>
            
            <button 
              :disabled="loading" 
              @click="clearImageCache"
              class="h-full px-6 bg-slate-900 shadow-xl hover:bg-slate-800 border border-white/10 rounded-xl text-white text-[11px] font-black uppercase tracking-widest transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center"
            >
              Limpar Cache
            </button>
            
            <button 
              v-if="!isEnriching && enrichmentQueue.length > 0"
              @click="libraryStore.startBackgroundEnrichment(isTurbo ? 5 : 1)"
              class="h-full px-6 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 rounded-xl text-emerald-400 text-[11px] font-black uppercase tracking-widest transition-all active:scale-95 flex items-center justify-center gap-2 group"
            >
              <svg class="w-4 h-4 group-hover:scale-125 transition-transform" fill="currentColor" viewBox="0 0 24 24">
                <path d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Turbinar
            </button>

            <button 
              @click="refreshLibrary"
              :disabled="loading" 
              class="flex-1 sm:flex-none h-full px-8 bg-gradient-to-br from-cyan-500 to-blue-700 hover:from-cyan-400 hover:to-blue-600 text-white border border-cyan-400/30 rounded-xl text-[11px] font-black uppercase tracking-widest shadow-[0_8px_25px_-5px_rgba(6,182,212,0.5)] transition-all active:scale-95 flex items-center justify-center"
            >
              <span v-if="loading" class="flex items-center gap-2">
                <svg class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Sync
              </span>
              <span v-else>Atualizar</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Stats Dashboard: High-Contrast Premium Widgets -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Sources Stat -->
        <div class="relative group overflow-hidden bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 transition-all duration-500 hover:border-amber-500/40 shadow-2xl hover:bg-slate-900">
          <div class="absolute -right-6 -bottom-6 w-32 h-32 bg-amber-500/10 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
          <div class="flex items-center gap-6 relative z-10">
            <div class="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center shrink-0 shadow-[0_0_20px_-5px_rgba(251,191,36,0.3)] group-hover:scale-110 transition-transform duration-500">
              <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-amber-400 drop-shadow-[0_0_12px_rgba(251,191,36,0.5)]" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 19V6a2 2 0 012-2h12a2 2 0 012 2v13" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M6 18h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-black text-amber-200/40 uppercase tracking-[0.3em] mb-1">Canais</div>
              <div class="text-4xl font-black text-white tracking-tighter leading-none">{{ stats.total_sources }}</div>
            </div>
          </div>
        </div>

        <!-- Items Stat -->
        <div class="relative group overflow-hidden bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 transition-all duration-500 hover:border-cyan-500/40 shadow-2xl hover:bg-slate-900">
          <div class="absolute -right-6 -bottom-6 w-32 h-32 bg-cyan-500/10 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
          <div class="flex items-center gap-6 relative z-10">
            <div class="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0 shadow-[0_0_20px_-5px_rgba(34,211,238,0.3)] group-hover:scale-110 transition-transform duration-500">
              <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-cyan-400 drop-shadow-[0_0_12px_rgba(34,211,238,0.5)]" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-black text-cyan-200/40 uppercase tracking-[0.3em] mb-1">Indexados</div>
              <div class="text-4xl font-black text-white tracking-tighter leading-none">{{ stats.total_items }}</div>
            </div>
          </div>
        </div>

        <!-- Optimized Stat: Interactive -->
        <div 
          @click="libraryStore.startBackgroundEnrichment(isTurbo ? 5 : 1)"
          class="relative group overflow-hidden bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 transition-all duration-500 hover:border-emerald-500/40 shadow-2xl hover:bg-slate-900 cursor-pointer active:scale-95"
          :title="isEnriching ? 'Otimização em andamento...' : 'Retomar Otimização da Biblioteca'"
        >
          <div class="absolute -right-6 -bottom-6 w-32 h-32 bg-emerald-500/10 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
          <div class="flex items-center gap-6 relative z-10">
            <div :class="['w-16 h-16 rounded-2xl border flex items-center justify-center shrink-0 transition-all duration-500', isEnriching ? 'bg-emerald-500/20 border-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.4)]' : 'bg-emerald-500/10 border-emerald-500/30']">
              <svg viewBox="0 0 24 24" fill="none" :class="['w-8 h-8 text-emerald-400 drop-shadow-[0_0_12px_rgba(16,185,129,0.5)]', isEnriching ? 'animate-pulse scale-110' : 'group-hover:scale-110']" xmlns="http://www.w3.org/2000/svg">
                <path v-if="!isEnriching" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path v-else d="M13 10V3L4 14h7v7l9-11h-7z" fill="currentColor" class="animate-bounce" />
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-black text-emerald-200/40 uppercase tracking-[0.3em] mb-1">Jogos Otimizados</div>
              <div class="text-4xl font-black text-emerald-400 tracking-tighter leading-none">{{ totalOptimizedCount }}</div>
            </div>
          </div>
          <div v-if="isEnriching" class="absolute bottom-0 left-0 h-1 bg-emerald-500/30 animate-pulse" :style="{ width: '100%' }"></div>
        </div>

        <!-- Groups Stat -->
        <div class="relative group overflow-hidden bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 transition-all duration-500 hover:border-purple-500/40 shadow-2xl hover:bg-slate-900">
          <div class="absolute -right-6 -bottom-6 w-32 h-32 bg-purple-500/10 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
          <div class="flex items-center gap-6 relative z-10">
            <div class="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center shrink-0 shadow-[0_0_20px_-5px_rgba(168,85,247,0.3)] group-hover:scale-110 transition-transform duration-500">
              <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-purple-400 drop-shadow-[0_0_12px_rgba(168,85,247,0.5)]" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 7h12M8 12h12M8 17h12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M4 7h.01M4 12h.01M4 17h.01" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-black text-purple-200/40 uppercase tracking-[0.3em] mb-1">Títulos Únicos</div>
              <div class="text-4xl font-black text-white tracking-tighter leading-none">{{ filteredGroups.length }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Enrichment Tracker (Sticky in bottom right) -->
      <div 
        v-if="isEnriching"
        class="fixed bottom-10 right-8 z-[100] animate-in slide-in-from-right-10 fade-in duration-700"
      >
        <!-- Expanded View -->
        <div v-if="!isTrackerMinimized" class="px-6 py-4 rounded-2xl border border-white/10 bg-[#0a0f1d]/90 backdrop-blur-3xl shadow-[0_20px_50px_rgba(0,0,0,0.8)] flex items-center gap-6 ring-1 ring-cyan-500/30 group">
          <div class="relative w-12 h-12">
            <div class="absolute inset-0 bg-cyan-500 blur-xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <svg class="w-full h-full text-cyan-500/20" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="none" stroke="currentColor" stroke-width="3" />
            </svg>
            <svg :class="['absolute inset-0 w-full h-full -rotate-90', isCoolingDown ? 'text-rose-500 animate-pulse' : (isTurbo ? 'text-amber-500' : 'text-cyan-500')]" viewBox="0 0 36 36">
              <circle 
                cx="18" 
                cy="18" 
                r="16" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="3" 
                stroke-dasharray="100" 
                :stroke-dashoffset="isCoolingDown ? 0 : (100 - Math.min(100, Math.floor((totalOptimizedCount / groups.length) * 100)))"
                stroke-linecap="round" 
                class="transition-all duration-1000 ease-out"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg :class="['w-5 h-5 transition-all', isCoolingDown ? 'text-rose-400 scale-110' : (isTurbo ? 'text-amber-400 scale-125 animate-bounce' : 'text-cyan-400 animate-pulse')]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="isCoolingDown" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path v-else-if="!isTurbo" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z M17 10V3L8 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          
          <div class="flex flex-col min-w-[120px]">
            <span :class="['text-[10px] font-black uppercase tracking-[0.2em] leading-none mb-1', isCoolingDown ? 'text-rose-500 animate-pulse' : (isTurbo ? 'text-amber-500' : 'text-cyan-500/80')]">
              {{ isCoolingDown ? 'Resfriando (90s)' : (isTurbo ? 'Turbo Ativado' : 'Otimização') }}
            </span>
            <div class="flex items-baseline gap-2">
              <span class="text-xl font-black text-white tabular-nums">{{ enrichmentQueue.length }}</span>
              <span class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Restantes</span>
            </div>
          </div>

          <!-- Controls -->
          <div class="flex items-center gap-2 border-l border-white/10 pl-4 ml-2">
            <button 
              @click="toggleTurbo" 
              :title="isTurbo ? 'Desativar Turbo' : 'Ativar Turbo (5x mais rápido)'"
              :class="['p-2 rounded-lg border transition-all active:scale-90', isTurbo ? 'bg-amber-500 border-amber-400 text-white shadow-lg shadow-amber-500/30' : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </button>
            <button 
              @click="isTrackerMinimized = true" 
              title="Minimizar"
              class="p-2 rounded-lg border border-white/10 bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-all active:scale-90"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Minimized View (Premium Sticky Bot Icon) -->
        <button 
          v-else
          @click="isTrackerMinimized = false"
          title="Ver Progresso de Otimização"
          :class="[
            'group relative w-16 h-16 rounded-[2rem] border-2 flex items-center justify-center shadow-[0_20px_50px_rgba(0,0,0,0.5)] transition-all duration-500 hover:scale-110 active:scale-95 backdrop-blur-3xl overflow-visible', 
            isCoolingDown ? 'bg-rose-500/10 border-rose-500/30' : (isTurbo ? 'bg-amber-500/10 border-amber-500/30' : 'bg-cyan-500/10 border-cyan-500/30')
          ]"
        >
          <!-- Background Glow -->
          <div :class="['absolute inset-2 blur-2xl opacity-40 transition-colors duration-700', isCoolingDown ? 'bg-rose-500' : (isTurbo ? 'bg-amber-500' : 'bg-cyan-500')]"></div>
          
          <!-- Bot Icon -->
          <svg :class="['w-8 h-8 relative z-10 transition-all duration-500', isCoolingDown ? 'text-rose-400' : (isTurbo ? 'text-amber-400 animate-bounce' : 'text-cyan-400 animate-pulse')]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="isCoolingDown" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>

          <!-- TOP CENTERED Premium Counter Badge -->
          <div :class="[
            'absolute -top-3 left-1/2 -translate-x-1/2 z-20 px-2.5 py-0.5 rounded-full text-[10px] font-black shadow-xl ring-2 ring-[#0a0f1d] transition-all duration-500',
            isCoolingDown ? 'bg-gradient-to-r from-rose-500 to-rose-700 text-white' : (isTurbo ? 'bg-gradient-to-r from-amber-400 to-orange-600 text-slate-950' : 'bg-gradient-to-r from-cyan-400 to-blue-600 text-slate-950')
          ]">
            {{ enrichmentQueue.length }}
          </div>

          <!-- Bottom Pulse Ring (Only when active) -->
          <div v-if="!isCoolingDown" :class="['absolute inset-0 rounded-[2rem] border-2 opacity-0 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700 pointer-events-none', isTurbo ? 'border-amber-500/50' : 'border-cyan-500/50']"></div>
        </button>
      </div>
    </div>

    <!-- UI - Advanced Filter Bar: Persistent Metadata -->
    <div class="flex flex-col lg:flex-row items-center justify-between gap-6 bg-slate-900/40 backdrop-blur-3xl border border-white/10 p-5 rounded-3xl shadow-2xl">
      <div class="flex flex-wrap items-center gap-6 w-full lg:w-auto">
        <!-- Genre Filter Button -->
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 shadow-inner">
            <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </div>
          <div class="flex flex-col min-w-[140px] cursor-pointer group/btn" @click="showGenreModal = true">
            <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-500 leading-none mb-1.5 group-hover/btn:text-cyan-500 transition-colors">Estilo / Gênero</span>
            <div class="flex items-center gap-2">
               <span class="text-[11px] font-black uppercase tracking-wider text-white group-hover/btn:text-cyan-400 transition-all">
                 {{ selectedGenres.length === 0 ? 'TODOS GÊNEROS' : (selectedGenres.length === 1 ? translateGenre(selectedGenres[0]) : selectedGenres.length + ' SELECIONADOS') }}
               </span>
               <svg class="w-3 h-3 text-slate-600 group-hover/btn:text-cyan-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-width="3" stroke-linecap="round"/></svg>
            </div>
          </div>
        </div>

        <!-- Dev Filter Button -->
        <div class="flex items-center gap-3 border-l border-white/5 pl-6">
          <div class="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 shadow-inner">
            <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div class="flex flex-col min-w-[140px] cursor-pointer group/btn" @click="showDevModal = true">
            <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-500 leading-none mb-1.5 group-hover/btn:text-purple-500 transition-colors">Desenvolvedora</span>
            <div class="flex items-center gap-2">
               <span class="text-[11px] font-black uppercase tracking-wider text-white group-hover/btn:text-purple-400 transition-all">
                 {{ selectedDevelopers.length === 0 ? 'TODAS DEVS' : (selectedDevelopers.length === 1 ? selectedDevelopers[0] : selectedDevelopers.length + ' SELECIONADAS') }}
               </span>
               <svg class="w-3 h-3 text-slate-600 group-hover/btn:text-purple-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-width="3" stroke-linecap="round"/></svg>
            </div>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-6 w-full lg:w-auto">
        <!-- Sort Control -->
        <div class="flex items-center gap-3 ml-auto">
          <!-- Botão Limpar Cache de Imagens (Minimalista) -->
          <button 
            @click="clearImageCacheOnly"
            class="p-2.5 rounded-xl bg-slate-800/50 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-700 hover:border-rose-500/30 transition-all active:scale-95 group relative"
            title="Limpar apenas cache de imagens (mantém nomes/metadados)"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <!-- Pequeno ícone de 'x' ou refresh sobreposto -->
            <div class="absolute -top-1 -right-1 bg-rose-500 rounded-full p-0.5 border border-slate-900">
               <svg class="w-2 h-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M6 18L18 6M6 6l12 12"></path></svg>
            </div>
          </button>

          <div class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 shadow-inner">
            <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
          </div>
          <div class="flex flex-col min-w-[140px]">
            <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-500 leading-none mb-1.5">Ordenar por</span>
            <select 
              v-model="sortBy"
              class="bg-transparent text-[11px] font-black uppercase tracking-wider text-white focus:outline-none cursor-pointer hover:text-amber-400 transition-all appearance-none"
            >
              <option value="upload" class="bg-slate-950 text-white">DATA DE UPLOAD</option>
              <option value="name" class="bg-slate-950 text-white">NOME (A-Z)</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="p-6 border border-rose-500/20 bg-slate-950 rounded-2xl flex items-center gap-5 animate-in fade-in slide-in-from-left-6 duration-700 shadow-2xl">
      <div class="w-12 h-12 rounded-xl bg-rose-500/10 flex items-center justify-center shrink-0 border border-rose-500/20 shadow-lg">
        <svg class="w-6 h-6 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div class="text-[11px] font-black text-rose-100 uppercase tracking-widest leading-relaxed">{{ error }}</div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-8">
      <div class="p-8 rounded-3xl border border-white/5 bg-gradient-to-br from-slate-900/50 via-[#0a0f1d]/80 to-transparent backdrop-blur-2xl">
        <div class="flex items-center gap-6">
          <div class="relative w-14 h-14 shrink-0">
            <div class="absolute inset-0 bg-cyan-500 blur-xl opacity-20 animate-pulse"></div>
            <div class="w-full h-full rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-cyan-400 animate-spin" viewBox="0 0 24 24" fill="none">
                <path d="M12 2a10 10 0 1010 10" stroke="currentColor" stroke-width="3" stroke-linecap="round" opacity="0.9"/>
              </svg>
            </div>
          </div>

          <div class="min-w-0 flex-1">
            <div class="text-lg font-black text-white uppercase tracking-wider mb-2">Escaneando Fontes...</div>
            <div class="text-xs text-slate-500 font-medium uppercase tracking-widest">
              Sincronizando bancos de dados e metadados visuais.
            </div>

            <div class="mt-5 h-2 rounded-full bg-white/5 border border-white/5 overflow-hidden relative">
              <div
                class="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 transition-[width] duration-300 ease-out shadow-[0_0_15px_rgba(6,182,212,0.4)]"
                :style="{ width: `${loadingProgress}%` }"
              />
              <div class="absolute inset-0 bg-white/10 opacity-20 animate-pulse" :style="{ width: `${loadingProgress}%` }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Skeleton Slicks -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div v-for="n in 6" :key="n" class="h-full rounded-2xl border border-white/5 bg-white/[0.02] overflow-hidden animate-pulse">
          <div class="w-full aspect-[460/215] bg-white/[0.03]" />
          <div class="p-6 space-y-4">
            <div class="h-5 w-3/4 rounded bg-white/[0.05]" />
            <div class="h-3 w-1/2 rounded bg-white/[0.03]" />
            <div class="flex gap-3 pt-4">
              <div class="h-10 flex-1 rounded-xl bg-white/[0.04]" />
              <div class="h-10 flex-1 rounded-xl bg-white/[0.04]" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Library State -->
    <div v-else>
      <div ref="itemsTopRef" class="h-2" />
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-6 gap-y-10">
        <div v-for="group in paginatedGroups" :key="group.key + ':' + (group.best?.genres?.length || 0)" class="h-full">
          <SteamGameCard
            :item="toCardItem(group)"
            variant="library"
            :versionsCount="getVersionsCount(group)"
            :showFavorite="getVersionsCount(group) <= 1"
            :autoResolveImage="true"
            @details="() => openItemDetails(group)"
            @versions="() => openVersions(group)"
            @download="(item) => onDownloadClick(group, item)"
            @resolved="(data) => handleManualResolution(group.name, data)"
          />
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="!loading && filteredGroups.length > pageSize" class="flex flex-wrap items-center justify-center gap-3 pt-8 pb-8">
      <!-- Previous Button -->
      <button 
        @click="goPrevPage" 
        :disabled="page <= 1"
        class="w-12 h-12 flex items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-white/[0.06] disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-90"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Page Numbers Loop -->
      <template v-for="(p, index) in visiblePages" :key="index">
        <span v-if="p === '...'" class="w-12 h-12 flex items-center justify-center text-slate-600 font-black">•••</span>
        
        <button 
          v-else
          @click="libraryStore.setPage(p); scrollToItemsTop()"
          :class="[
            'min-w-[48px] h-12 px-2 rounded-xl font-black text-xs transition-all border active:scale-95',
            page === p 
              ? 'bg-gradient-to-br from-cyan-500 to-blue-600 text-white border-cyan-400/30 shadow-[0_0_20px_-5px_rgba(6,182,212,0.4)]' 
              : 'bg-white/[0.03] text-slate-500 border-white/10 hover:text-white hover:border-white/20 hover:bg-white/[0.06]'
          ]"
        >
          {{ p }}
        </button>
      </template>

      <!-- Next Button -->
      <button 
        @click="goNextPage" 
        :disabled="page >= totalPages"
        class="w-12 h-12 flex items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 hover:bg-white/[0.06] disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-90"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>


    <!-- MODAL DE VERSÕES PREMIUM -->
    <PremiumVersionsModal
      :is-open="showVersionsModal"
      :group-name="activeGroup?.name"
      :versions-count="activeGroup?.versions_count"
      :versions="activeGroup?.versions"
      @close="closeVersions"
      @select="selectVersion"
    />

    <!-- MODAL DE DOWNLOAD PREMIUM -->
    <PremiumDownloadModal
      :is-open="showDownloadDialog"
      :item="selectedItem"
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

    <Modal v-if="showManualFolderModal" @close="showManualFolderModal = false" title="Escolher pasta manualmente" :showDefaultButtons="false">
      <div style="pointer-events: auto;">
        <label class="block text-sm font-semibold text-gray-300 mb-2">Caminho da pasta</label>
        <Input v-model="manualFolderPath" placeholder="C:\\Users\\seu usuario\\Downloads" />
        <div class="flex gap-2 pt-4" style="pointer-events: auto;">
          <Button variant="outline" class="flex-1 btn-translucent" @click="showManualFolderModal = false">Cancelar</Button>
          <Button variant="success" class="flex-1" @click="() => { downloadDestination.value = manualFolderPath.value || downloadDestination.value; showManualFolderModal = false }">Usar esta pasta</Button>
        </div>
      </div>
    </Modal>

    <SourceAnalysisModal
      :open="showAnalysisModal"
      :original-item="analysisOriginalItem"
      :candidates="analysisCandidates"
      :original-health="analysisOriginalItem?.health"
      :is-loading="analysisLoading"
      @close="showAnalysisModal = false"
      @confirm="onAnalysisConfirm"
    />

    <!-- MODAL DE CONFIRMAÇÃO: LIMPAR CACHE -->
    <Modal 
      v-if="showClearCacheModal" 
      @close="showClearCacheModal = false" 
      title="Limpar Todo o Cache?" 
      :showDefaultButtons="false"
    >
      <div class="space-y-6">
        <div class="flex items-center gap-4 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20">
          <div class="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center shrink-0">
            <svg class="w-6 h-6 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="text-xs font-bold text-rose-200 uppercase tracking-widest leading-relaxed">
            Esta ação é irreversível e afetará toda a sua biblioteca.
          </div>
        </div>

        <div class="space-y-3 text-sm text-slate-400">
          <p>Ao confirmar, todos os dados abaixo serão <span class="text-white font-bold">APAGADOS</span>:</p>
          <ul class="list-disc list-inside space-y-1.5 ml-2">
            <li>Identificações de Jogos (AppIDs)</li>
            <li>Gêneros e Desenvolvedoras extraídos</li>
            <li>Capas e imagens em alta resolução</li>
            <li>Progresso de Auto-Otimização</li>
          </ul>
          <p class="pt-2 italic">O robô terá que re-escandear todos os <span class="text-cyan-400 font-bold">7.800+ títulos</span> do zero.</p>
        </div>

        <div class="flex gap-3 pt-2">
          <Button variant="outline" class="flex-1 btn-translucent" @click="showClearCacheModal = false">Cancelar</Button>
          <Button variant="danger" class="flex-1 shadow-lg shadow-rose-500/20" @click="confirmClearCache">Limpar Agora</Button>
        </div>
      </div>
    </Modal>

    <!-- Modal de Restauração de Imagens (SAFE - NÃO APAGA PROGRESSO) -->
    <Modal
      v-if="showImageResetModal" 
      @close="showImageResetModal = false"
      title="Restaurar APENAS Imagens"
    >
      <div class="space-y-4">
        <div class="flex items-start gap-4 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
          <div class="p-2 bg-emerald-500/20 rounded-full text-emerald-500 shrink-0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-emerald-200">Reset de Visual (Seguro)</h3>
            <p class="text-emerald-200/70 text-sm mt-1">
              Isso vai apenas apagar as fotos para baixar novas (ex: se a capa estiver errada).
            </p>
            <p class="text-emerald-200 font-bold text-xs mt-2 uppercase tracking-tight">
              ✅ SEU PROGRESSO E IDENTIFICAÇÕES SÃO MANTIDOS.
            </p>
          </div>
        </div>
        
        <div class="flex gap-3 justify-end pt-2">
          <Button variant="outline" @click="showImageResetModal = false">Cancelar</Button>
          <Button variant="danger" @click="confirmClearImageCache">
            Confirmar Reset de Fotos
          </Button>
        </div>
      </div>
    </Modal>
    <!-- MODAIS DE FILTRO MULTI-SELEÇÃO -->
    <FilterSelectionModal
      :is-open="showGenreModal"
      title="Gêneros"
      label="Preferências de Estilo"
      variant="cyan"
      :options="allGenres"
      :selected="selectedGenres"
      :translate="translateGenre"
      @close="showGenreModal = false"
      @confirm="(list) => { libraryStore.setGenres(list); showGenreModal = false }"
    />

    <FilterSelectionModal
      :is-open="showDevModal"
      title="Devs"
      label="Equipes de Criação"
      variant="purple"
      :options="allDevelopers"
      :selected="selectedDevelopers"
      @close="showDevModal = false"
      @confirm="(list) => { libraryStore.setDevelopers(list); showDevModal = false }"
    />
  </div>
</template>

<script>
export default {
  name: 'Library'
}
</script>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'

import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import api from '../services/api'
import { useDownloadStore } from '../stores/download'
import { useLibraryStore } from '../stores/library'
import Card from '../components/Card.vue'
import SteamGameCard from '../components/SteamGameCard.vue'
import Modal from '../components/Modal.vue'
import PremiumDownloadModal from '../components/PremiumDownloadModal.vue'
import PremiumVersionsModal from '../components/PremiumVersionsModal.vue'
import Button from '../components/Button.vue'
import Input from '../components/Input.vue'
import FavoriteToggleButton from '../components/FavoriteToggleButton.vue'
import SourceAnalysisModal from '../components/SourceAnalysisModal.vue'
import FilterSelectionModal from '../components/FilterSelectionModal.vue'
import { formatBytes, formatRelativeDate, translateGenre } from '../utils/format'
import { useToastStore } from '../stores/toast'



const downloadStore = useDownloadStore()
const libraryStore = useLibraryStore()
const { groups, stats, loading, error, page, searchQuery, selectedGenres, selectedDevelopers, sortBy, isEnriching, isCoolingDown, enrichmentQueue, isTurbo } = storeToRefs(libraryStore)
const router = useRouter()

const totalOptimizedCount = computed(() => {
  return groups.value.filter(g => g.metadata_resolved).length
})

function toggleTurbo() {
  libraryStore.toggleTurbo()
  
  if (isTurbo.value) {
    const ts = useToastStore()
    ts.push('MODO TURBO', 'Aceleração ativada. Otimizando 5 jogos simultaneamente.')
  }
}

const itemsTopRef = ref(null)

const showClearCacheModal = ref(false)
const showGenreModal = ref(false)
const showDevModal = ref(false)
const isTrackerMinimized = ref(true)

const lastPageWithoutFilter = ref(1)

// groups, stats, loading, error managed by store

const cacheBust = ref(0)

const loadingProgress = ref(0)
let loadingProgressTimer = null

function startLoadingProgress() {
  try {
    if (loadingProgressTimer) {
      clearInterval(loadingProgressTimer)
      loadingProgressTimer = null
    }
    loadingProgress.value = 0
    loadingProgressTimer = setInterval(() => {
      // Ramp up quickly at first, then slow down; never reach 100% until finished.
      const p = loadingProgress.value
      const cap = 90
      if (p >= cap) return
      const step = p < 30 ? 6 : (p < 60 ? 3 : 1)
      loadingProgress.value = Math.min(cap, p + step)
    }, 180)
  } catch (e) {}
}

function finishLoadingProgress() {
  try {
    if (loadingProgressTimer) {
      clearInterval(loadingProgressTimer)
      loadingProgressTimer = null
    }
    loadingProgress.value = 100
    setTimeout(() => {
      loadingProgress.value = 0
    }, 350)
  } catch (e) {}
}

const showImageResetModal = ref(false)

function clearImageCacheOnly() {
  console.log('[Library] Opening Image Reset Modal')
  showImageResetModal.value = true
}

async function confirmClearImageCache() {
  try {
    const ts = useToastStore()
    ts.push('Limpando...', 'Solicitando limpeza ao sistema...')
    
    // 1. Limpar backend (Remove metadados de imagem do DB)
    await api.post('/api/library/images/clear')
    
    // 2. Limpar frontend (Remove cache local)
    localStorage.removeItem('imageCache')
    
    showImageResetModal.value = false
    ts.push('Sucesso', 'Cache esvaziado! Recarregando em 2s...')
    
    setTimeout(() => {
      window.location.reload()
    }, 2000)
  } catch (e) {
    console.error(e)
    alert('Erro ao limpar cache: ' + e.message)
  }
}

function formatRelativeCompact(dateStr) {
  if (!dateStr) return ''
  try {
    const dt = new Date(dateStr)
    const t = dt.getTime()
    if (isNaN(t)) {
      // fallback to original formatter if it's not an ISO date
      return formatRelativeDate(dateStr) || String(dateStr)
    }
    const now = Date.now()
    const diffSec = Math.max(0, Math.floor((now - t) / 1000))

    const minute = 60
    const hour = 60 * minute
    const day = 24 * hour
    const week = 7 * day
    const month = 30 * day
    const year = 365 * day

    if (diffSec < minute) return `há ${diffSec}s`
    if (diffSec < hour) return `há ${Math.floor(diffSec / minute)}m`
    if (diffSec < day) return `há ${Math.floor(diffSec / hour)}h`
    if (diffSec < week) return `há ${Math.floor(diffSec / day)}d`
    if (diffSec < month) return `há ${Math.floor(diffSec / week)}sem`
    if (diffSec < year) {
      const n = Math.floor(diffSec / month)
      return `há ${n} ${n === 1 ? 'mês' : 'meses'}`
    }
    const y = Math.floor(diffSec / year)
    return `há ${y} ${y === 1 ? 'ano' : 'anos'}`
  } catch (e) {
    return formatRelativeDate(dateStr) || String(dateStr)
  }
}

const formattedBuiltAt = computed(() => {
  const v = stats.value?.built_at
  if (!v) return ''
  try {
    const dt = new Date(v)
    if (!isNaN(dt.getTime())) {
      return dt.toLocaleString()
    }
  } catch (e) {}
  return String(v)
})
// searchQuery is in store

const showVersionsModal = ref(false)
const activeGroup = ref(null)

const showAnalysisModal = ref(false)
const analysisCandidates = ref([])
const analysisOriginalItem = ref(null)
const analysisLoading = ref(false)
const analysisPendingItem = ref(null)

const showDownloadDialog = ref(false)
const selectedItem = ref(null)
const downloadDestination = ref('downloads')
const downloadVerifySsl = ref({})
const showManualFolderModal = ref(false)

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
const manualFolderPath = ref('')
const browseLoading = ref(false)
const modalInfo = ref({ size: null, accept_range: false, eta: null, checking: false })
const freeSpaceInfo = ref(null)

const isRepackDetected = computed(() => {
  return selectedItem.value?.name?.toLowerCase().includes('repack') || 
         selectedItem.value?.source_title?.toLowerCase().includes('fitgirl') ||
         selectedItem.value?.source_title?.toLowerCase().includes('dodi')
})

const estimatedRequiredSpace = computed(() => {
  const size = selectedItem.value?.size || modalInfo.value.size || 0
  if (!size) return 0
  // FIX: Reduzido para 1.25x conforme pedido do usuário (para evitar bloqueios falsos).
  return isRepackDetected.value ? size * 1.25 : size * 1.1
})

const isPlaceholderSize = computed(() => {
  const size = selectedItem.value?.size || modalInfo.value.size || 0
  if (!size) return false
  
  // Quase certeza que é só metadata se for minúsculo
  if (size < 10 * 1024 * 1024) return true
  
  // Apenas para casos extremas de "Coleções" que fingem ter poucos GBs
  const suspiciousKeywords = ['collection', 'all games']
  const isSuspiciousName = suspiciousKeywords.some(k => selectedItem.value?.name?.toLowerCase().includes(k))
  
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
    console.error('[Library] Erro ao checar espaço:', e)
  }
}

watch(downloadDestination, () => {
  checkDiskSpace()
})

const pageSize = 21

// page and searchQuery are now in the store (mapped above)

async function fetchLibrary(refresh = false) {
  if (refresh || !libraryStore.isLoaded) {
    startLoadingProgress()
  } else {
    // Debug log to verify cache usage
    console.log('Library cache hit! Not reloading.')
  }
  
  await libraryStore.fetchLibrary(refresh)
  
  if (refresh) {
    libraryStore.setPage(1)
  }
  
  finishLoadingProgress()
}

function refreshLibrary() {
  return fetchLibrary(true)
}

async function clearImageCache() {
  showClearCacheModal.value = true
}

async function confirmClearCache() {
  try {
    showClearCacheModal.value = false
    const ts = useToastStore()
    
    // 1. Clear LocalStorage (Resolved images in browser)
    localStorage.removeItem('imageCache')
    
    // 2. Clear Backend (Database + API Caches)
    await api.post('/api/cache/clear')
    
    // 3. Reset Store Enrichment state
    libraryStore.isEnriching = false
    libraryStore.enrichmentQueue = []
    
    // 4. Visual Feedback
    cacheBust.value = (cacheBust.value || 0) + 1
    ts.push('Reset Completo', 'Todo o cache foi limpo (Banco + Imagens). Reiniciando otimização...')
    
    // 5. Force Library Reload and restart Background Enrichment
    await fetchLibrary(true)
  } catch (e) {
    console.error('[Library] Erro ao limpar cache total:', e)
  }
}

const SOURCE_BLACKLIST = ['FITGIRL', 'DODI', 'ONLINEFIX', 'HYDRA', 'KAOS', 'ELAMIGOS', 'GOG']

/**
 * Computes all unique genres available across the loaded library items.
 * Robust precision: excludes source names and cleans metadata.
 */
const allGenres = computed(() => {
  const set = new Set()
  groups.value.forEach(g => {
    const processGenre = (raw) => {
      if (!raw || typeof raw !== 'string') return
      const clean = raw.trim()
      const upper = clean.toUpperCase()
      if (!SOURCE_BLACKLIST.includes(upper) && clean.length > 1) {
        set.add(clean)
      }
    }

    const item = g.best || {}
    // ONLY use the primary category (which is already calculated by priority in backend/store)
    if (item.category) {
      processGenre(item.category)
    } else if (Array.isArray(item.genres) && item.genres.length > 0) {
      processGenre(item.genres[0])
    }
  })
  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

const allDevelopers = computed(() => {
  const set = new Set()
  groups.value.forEach(g => {
    const dev = g.best?.developer
    if (dev && typeof dev === 'string') set.add(dev.trim())
  })
  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

const filteredGroups = computed(() => {
  let list = [...groups.value]

  // 1. Precise Text Search
  const q = (searchQuery.value || '').trim().toLowerCase()
  if (q) {
    list = list.filter(g => (g.name || '').toLowerCase().includes(q))
  }

  // 2. High-Precision Single-Genre Filtering (Filtered by the card's category)
  if (selectedGenres.value.length > 0) {
    list = list.filter(g => {
      const category = g.best?.category || (Array.isArray(g.best?.genres) && g.best.genres[0])
      return category && selectedGenres.value.includes(category)
    })
  }

  // 3. Multi-Developer Filtering (OR logic within devs)
  if (selectedDevelopers.value.length > 0) {
    list = list.filter(g => {
      const dev = g.best?.developer
      return dev && selectedDevelopers.value.includes(dev)
    })
  }

  // 4. Advanced Sorting
  const sort = sortBy.value
  list.sort((a, b) => {
    if (sort === 'name') {
      const clean = (s) => (s || '').replace(/^[^a-zA-Z0-9]+/, '').toLowerCase()
      return clean(a.name).localeCompare(clean(b.name))
    }
    if (sort === 'upload') {
      const dateA = new Date(a.best?.uploadDate || 0).getTime()
      const dateB = new Date(b.best?.uploadDate || 0).getTime()
      return dateB - dateA
    }
    // Default: 'recent' (sync timestamp or implicit order)
    const tsA = Number(a.recent_ts || 0)
    const tsB = Number(b.recent_ts || 0)
    return tsB - tsA
  })

  return list
})

const totalPages = computed(() => {
  const total = filteredGroups.value.length
  return Math.max(1, Math.ceil(total / pageSize))
})

const paginatedGroups = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredGroups.value.slice(start, start + pageSize)
})

const visiblePages = computed(() => {
  const current = page.value
  const total = totalPages.value
  const delta = 2 // Numbers to show on each side of current
  const range = []
  const rangeWithDots = []
  let l

  range.push(1)

  if (total <= 1) return [1]

  for (let i = current - delta; i <= current + delta; i++) {
    if (i < total && i > 1) {
      range.push(i)
    }
  }

  range.push(total)

  for (const i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1)
      } else if (i - l !== 1) {
        rangeWithDots.push('...')
      }
    }
    rangeWithDots.push(i)
    l = i
  }

  return rangeWithDots
})

function scrollToItemsTop() {
  try {
    nextTick(() => {
      const el = itemsTopRef.value
      if (el && typeof el.scrollIntoView === 'function') {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        return
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })
  } catch (e) {}
}

function goPrevPage() {
  if (page.value > 1) {
    libraryStore.setPage(page.value - 1)
    scrollToItemsTop()
  }
}

function goNextPage() {
  if (page.value < totalPages.value) {
    libraryStore.setPage(page.value + 1)
    scrollToItemsTop()
  }
}

// Update store when search query changes (handled by v-model on input which should map to store)
// However, since we used storeToRefs, searchQuery is a ref.
// But to trigger side effects like page reset, we should watch it or use the action.
// Better: use a writable computed for the input.
// For now, let's watch the ref and ensure page is reset if it wasn't done by the setter.

watch(searchQuery, (newVal, oldVal) => {
  // Se o componente foi destruído/recriado sem keep-alive o newVal pode vir populado
  // mas aqui o keep-alive deve manter o estado.
  
  // Caso 1: Começou a digitar (limpo -> pesquisando)
  if (!oldVal && newVal) {
    lastPageWithoutFilter.value = page.value
    console.log('[Library] Salvando página anterior:', lastPageWithoutFilter.value)
  }

  // Caso 2: Limpou a pesquisa (pesquisando -> limpo)
  if (!newVal && oldVal) {
    console.log('[Library] Restaurando página anterior:', lastPageWithoutFilter.value)
    libraryStore.setPage(lastPageWithoutFilter.value)
    // Não scrollamos para o topo ao limpar, conforme regra atual
  } 
  // Caso 3: Mudou a pesquisa ou começou nova pesquisa
  else if (newVal) {
    if (page.value !== 1) {
      libraryStore.setPage(1)
    }
    scrollToItemsTop()
  }
})

watch(selectedGenres, () => {
  if (page.value !== 1) {
    libraryStore.setPage(1)
  }
  scrollToItemsTop()
}, { deep: true })

watch(selectedDevelopers, () => {
  if (page.value !== 1) {
    libraryStore.setPage(1)
  }
  scrollToItemsTop()
}, { deep: true })

watch(sortBy, () => {
  if (page.value !== 1) {
    libraryStore.setPage(1)
  }
  scrollToItemsTop()
})

function handleManualResolution(name, data) {
  // Prune the queue if this item was resolved manually (paginating)
  libraryStore.removeFromQueue(name)
  // Ensure the local store state is also updated for filters
  libraryStore.applyMetadata(name, data)
}

function toCardItem(group) {
  const best = group?.best || {}
  return {
    ...best,
    name: group?.name || best?.name || 'Item',
    size: best?.size,
    category: best?.category,
    uploadDate: best?.uploadDate,
    source: best?.source_title || best?.source,
    // Provide the same image fields Sources cards rely on.
    // SteamGameCard prefers: image -> header_image -> thumbnail, and caches by item.name.
    image: best?.image || best?.header_image || best?.thumbnail,
    header_image: best?.header_image || best?.image || best?.thumbnail,
    thumbnail: best?.thumbnail || best?.image || best?.header_image,
    icon: best?.icon,
    // Preserve any detected Steam appId so SteamGameCard can use the cheap header.jpg fallback.
    appId: best?.appId || best?.appid || best?.steam_appid
  }
}

function getVersionsCount(group) {
  const vc = group?.versions_count
  if (typeof vc === 'number' && !Number.isNaN(vc)) return vc
  const asNum = Number(vc)
  if (!Number.isNaN(asNum) && isFinite(asNum)) return asNum
  const v = group?.versions
  return Array.isArray(v) ? v.length : 0
}

function openVersions(group) {
  activeGroup.value = group
  showVersionsModal.value = true
}

function openItemDetails(group) {
  const item = toCardItem(group)
  try {
    sessionStorage.setItem('itemDetails', JSON.stringify(item))
  } catch (e) {
    // ignore
  }
  router.push({ name: 'ItemDetails', params: { id: item.id || item.name } })
}

function closeVersions() {
  showVersionsModal.value = false
  activeGroup.value = null
}

function selectVersion(v) {
  closeVersions()
  startDownloadFlow(v)
}

function onDownloadClick(group, emittedItem) {
  if (!group) return
  const vc = getVersionsCount(group)
  if (vc > 1) {
    openVersions(group)
    return
  }

  const item = emittedItem || group.best
  startDownloadFlow(item)
}

async function startDownloadFlow(item) {
  if (!item) return

  analysisPendingItem.value = item
  analysisOriginalItem.value = item
  analysisCandidates.value = []
  analysisLoading.value = true
  showAnalysisModal.value = true

  try {
    const resp = await api.post('/api/analysis/pre-job/with-recommendations', { item })
    if (resp.data && resp.data.candidates && resp.data.candidates.length > 0) {
      analysisCandidates.value = resp.data.candidates

      const enrichedOriginal = { ...item }
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
    // fallback to direct download
  }

  showAnalysisModal.value = false
  analysisLoading.value = false
  openDownloadConfigurationDialog(item)
}

function onAnalysisConfirm(selectedItem) {
  const item = selectedItem || analysisPendingItem.value
  showAnalysisModal.value = false
  analysisLoading.value = false
  analysisPendingItem.value = null
  openDownloadConfigurationDialog(item)
}

function openDownloadConfigurationDialog(item) {
  if (!item) return

  selectedItem.value = item
  downloadDestination.value = 'downloads'

  preflightError.value = null
  preflightResult.value = null
  preflightAria2.value = null
  preflightHealth.value = null

  const sourceId = item.source_id
  if (!(sourceId in downloadVerifySsl.value)) {
    Object.assign(downloadVerifySsl.value, { [sourceId]: true })
  }

  modalInfo.value = { size: null, accept_range: false, eta: null, checking: true }

  const urlRaw = (item.url || '').toString().trim()
  if (urlRaw.startsWith('magnet:')) {
    // Magnet: always run pre-flight with real probe, even if coming from pre-job flow.
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
        preflightHealth.value = { seeders: item?.seeders ?? null, leechers: item?.leechers ?? null }
      }

      preflightResult.value = { accept_ranges: false, size: null, status_code: null, note: 'Magnet links use aria2' }
      preflightError.value = null
      preflightLoading.value = false
    })().catch(() => {
      preflightLoading.value = false
    })
  } else {
    // HTTP/HTTPS: keep existing behavior for size/range.
    try {
      const url = encodeURIComponent(urlRaw)
      api.get(`/api/supports_range?url=${url}`).then(({ data }) => {
        modalInfo.value.size = data.size || null
        modalInfo.value.accept_range = !!data.accept_ranges
        if (data.size && modalInfo.value.accept_range) {
          const baseline = 1024 * 1024
          modalInfo.value.eta = Math.round((data.size / baseline))
        }
        checkDiskSpace()
      }).catch(() => {}).finally(() => {
        modalInfo.value.checking = false
      })
    } catch (e) {
      modalInfo.value.checking = false
    }
  }

  checkDiskSpace()
  showDownloadDialog.value = true
}

async function runPreflightForce() {
  preflightError.value = null
  preflightResult.value = null
  preflightAria2.value = null
  preflightHealth.value = null

  const urlRaw = (selectedItem.value?.url || '').toString().trim()
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
      console.log('[LIBRARY] Resposta force_refresh:', healthResp.data)
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

async function browsePath() {
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
    manualFolderPath.value = downloadDestination.value || ''
    showManualFolderModal.value = true
  } catch (e) {
    manualFolderPath.value = downloadDestination.value || ''
    showManualFolderModal.value = true
  } finally {
    browseLoading.value = false
  }
}

async function confirmDownload() {
  if (!selectedItem.value) return
  
  if (!hasEnoughSpace.value) {
    try {
      const ts = useToastStore()
      ts.push('Bloqueado', 'Não há espaço em disco suficiente para este item.')
    } catch (e) {}
    return
  }

  try {
    let destCandidate = (downloadDestination.value || 'downloads').toString()
    const destLower = destCandidate.toLowerCase()
    const suspicious = destLower.startsWith('http') || destLower.startsWith('magnet:') || destCandidate.includes('%25') || destCandidate.includes('announce')
    if (suspicious) destCandidate = 'downloads'

    const sourceId = selectedItem.value.source_id
    const verifySsl = (downloadVerifySsl.value[sourceId] !== false) ?? true

    const jobData = {
      url: selectedItem.value.url,
      name: selectedItem.value.name,
      destination: destCandidate,
      verify_ssl: verifySsl,
      size: selectedItem.value.size || null
    }

    const result = await downloadStore.createJob(jobData)
    if (result && result.job_id) {
      showDownloadDialog.value = false
      selectedItem.value = null
      try {
        const ts = useToastStore()
        ts.push('Download', `Download #${result.job_id} iniciado`)
      } catch (e) {}
      
      console.log('[Library] Job criado com sucesso, redirecionando para /downloads')
      await nextTick()
      router.push('/downloads')
    }
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message || ''
    const ts = useToastStore()
    
    if (errorMsg.startsWith('DOWNLOAD_ALREADY_EXISTS')) {
      const status = errorMsg.split(':')[1] || 'em andamento'
      let statusLabel = 'em andamento'
      if (status === 'paused') statusLabel = 'pausado (aguardando ação)'
      
      ts.push('Já na Lista', `O item "${selectedItem.value?.name}" já está na sua lista de histórico (${statusLabel}).`)
      
      // Mesmo dando erro, vamos sugerir ir pro histórico pra resolver
      showDownloadDialog.value = false
      router.push('/downloads')
    } else {
      ts.push('Erro', errorMsg || 'Erro ao criar job')
    }
  }
}

// Save scroll position before leaving -> REMOVED
// onBeforeRouteLeave -> REMOVED

onMounted(() => {
  console.log('[Library] Montado - carregando biblioteca')
  // Fix stale sort state: If store has 'recent' (removed option), force to 'upload'
  if (sortBy.value === 'recent') {
    libraryStore.setSortBy('upload')
  }
  fetchLibrary(false)
  startLoadingProgress()
})


</script>
