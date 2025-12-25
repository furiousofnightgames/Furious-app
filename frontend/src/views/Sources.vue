<template>
  <div class="space-y-6">
    <!-- Header Stats with SVG Icons -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="p-4 bg-gradient-to-br from-amber-900/30 to-orange-900/10 rounded-lg border border-amber-500/20 hover:border-amber-500/50 transition">
        <div class="flex items-center justify-center gap-3 mb-2">
          <div class="w-10 h-10 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
              <defs>
                <linearGradient id="booksGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #f59e0b" />
                  <stop offset="100%" style="stop-color: #d97706" />
                </linearGradient>
              </defs>
              <!-- Livros empilhados com animação escada -->
              <rect x="3" y="5" width="6" height="14" fill="url(#booksGrad)" opacity="0.5" stroke="url(#booksGrad)" stroke-width="1" rx="0.5" class="animate-bounce" style="animation-delay: 0s"/>
              <rect x="10" y="7" width="6" height="12" fill="url(#booksGrad)" opacity="0.6" stroke="url(#booksGrad)" stroke-width="1" rx="0.5" class="animate-bounce" style="animation-delay: 0.1s"/>
              <rect x="17" y="9" width="6" height="10" fill="url(#booksGrad)" opacity="0.7" stroke="url(#booksGrad)" stroke-width="1" rx="0.5" class="animate-bounce" style="animation-delay: 0.2s"/>
            </svg>
          </div>
          <h3 class="text-sm font-semibold text-amber-400">Fontes Salvas</h3>
        </div>
        <p class="text-2xl font-bold text-amber-300 text-center">{{ sources.length }}</p>
      </div>

      <div class="p-4 bg-gradient-to-br from-cyan-900/30 to-blue-900/10 rounded-lg border border-cyan-500/20 hover:border-cyan-500/50 transition">
        <div class="flex items-center justify-center gap-3 mb-2">
          <div class="w-10 h-10 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
              <defs>
                <linearGradient id="itemsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #06b6d4" />
                  <stop offset="100%" style="stop-color: #0284c7" />
                </linearGradient>
              </defs>
              <!-- Caixas/pacotes -->
              <rect x="2" y="5" width="8" height="8" fill="url(#itemsGrad)" opacity="0.5" stroke="url(#itemsGrad)" stroke-width="1.5" class="animate-bounce"/>
              <rect x="12" y="5" width="8" height="8" fill="url(#itemsGrad)" opacity="0.6" stroke="url(#itemsGrad)" stroke-width="1.5" class="animate-bounce" style="animation-delay: 0.2s"/>
              <rect x="2" y="14" width="8" height="8" fill="url(#itemsGrad)" opacity="0.6" stroke="url(#itemsGrad)" stroke-width="1.5" class="animate-bounce" style="animation-delay: 0.1s"/>
              <rect x="12" y="14" width="8" height="8" fill="url(#itemsGrad)" opacity="0.5" stroke="url(#itemsGrad)" stroke-width="1.5" class="animate-bounce" style="animation-delay: 0.3s"/>
            </svg>
          </div>
          <h3 class="text-sm font-semibold text-cyan-400">Itens Totais</h3>
        </div>
        <p class="text-2xl font-bold text-cyan-300 text-center">{{ filteredItems.length }}</p>
      </div>

      <div class="p-4 bg-gradient-to-br from-purple-900/30 to-pink-900/10 rounded-lg border border-purple-500/20 hover:border-purple-500/50 transition">
        <div class="flex items-center justify-center gap-3 mb-2">
          <div class="w-10 h-10 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
              <defs>
                <linearGradient id="tagsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color: #a855f7" />
                  <stop offset="100%" style="stop-color: #ec4899" />
                </linearGradient>
              </defs>
              <!-- Tags/etiquetas com animação rotativa -->
              <g class="animate-spin" style="animation-duration: 4s; transform-origin: 12px 12px">
                <rect x="3" y="4" width="8" height="6" fill="none" stroke="url(#tagsGrad)" stroke-width="1.5" rx="1"/>
                <circle cx="9" cy="7" r="1" fill="url(#tagsGrad)" opacity="0.8"/>
              </g>
              <g class="animate-spin" style="animation-duration: 4s; animation-direction: reverse; transform-origin: 12px 12px">
                <rect x="13" y="14" width="8" height="6" fill="none" stroke="url(#tagsGrad)" stroke-width="1.5" rx="1"/>
                <circle cx="19" cy="17" r="1" fill="url(#tagsGrad)" opacity="0.8"/>
              </g>
            </svg>
          </div>
          <h3 class="text-sm font-semibold text-purple-400">Categorias</h3>
        </div>
        <p class="text-2xl font-bold text-purple-300 text-center">{{ getCategories.size }}</p>
      </div>
    </div>

    <!-- Add Source Form -->
    <Card>
      <div class="flex items-center gap-3 mb-4">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6">
          <!-- Círculo externo -->
          <circle cx="12" cy="12" r="9" fill="none" stroke="#06b6d4" stroke-width="2"/>
          <!-- Linha horizontal do + -->
          <line x1="7" y1="12" x2="17" y2="12" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/>
          <!-- Linha vertical do + -->
          <line x1="12" y1="7" x2="12" y2="17" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <h2 class="text-xl font-bold text-cyan-400">Adicionar Nova Fonte JSON</h2>
      </div>
      
      <!-- Mensagem de erro -->
      <div v-if="addError" class="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-300 text-sm">
        {{ addError }}
      </div>

      <form @submit.prevent="handleAddSource" class="space-y-3" :class="{ 'opacity-50 pointer-events-none': isAddingSource }">
        <Input 
          v-model="newSourceUrl" 
          placeholder="https://exemplo.com/fontes/lista.json"
          type="url"
          :disabled="isAddingSource"
        />
        <div class="flex gap-3">
          <button 
            type="submit" 
            class="flex-1 px-4 py-3 rounded-lg font-semibold bg-gradient-to-r from-cyan-600 to-teal-600 text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
            :disabled="isAddingSource"
          >
            <svg v-if="!isAddingSource" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
              <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
            <span v-if="isAddingSource">⏳ Carregando...</span>
            <span v-else>Adicionar</span>
          </button>
          <button 
            @click="showJsonPaste = !showJsonPaste" 
            type="button"
            class="flex-1 px-4 py-3 rounded-lg font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
            :disabled="isAddingSource"
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
              <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 3H15V9H9V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M9 13H15M9 17H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>{{ showJsonPaste ? 'Ocultar' : 'Colar JSON' }}</span>
          </button>
        </div>
        
        <div v-if="showJsonPaste" class="mt-4 p-4 bg-purple-900/30 rounded border border-purple-500/30">
          <textarea 
            v-model="jsonPasteContent"
            placeholder='{"items": [...]}'
            class="w-full h-32 bg-gray-900 border border-cyan-500/30 rounded p-2 text-gray-100"
            :disabled="isAddingSource"
          />
          <button 
            @click="handleAddRawJson" 
            type="button"
            class="mt-3 w-full px-4 py-3 rounded-lg font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
            :disabled="isAddingSource"
          >
            <svg v-if="!isAddingSource" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
              <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 3H15V9H9V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M9 13H15M9 17H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span v-if="isAddingSource">⏳ Carregando...</span>
            <span v-else>✓ Adicionar JSON</span>
          </button>
        </div>
      </form>
    </Card>

    <!-- Suas Fontes -->
    <div v-if="sources.length > 0" class="space-y-4">
      <h2 class="text-xl font-bold text-cyan-400">📚 Suas Fontes Salvas</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="source in sources"
          :key="source.id"
          @click="selectSource(source)"
          :class="[
            'p-4 rounded-lg border cursor-pointer transition-all hover:shadow-lg',
            selectedSourceId === source.id
              ? 'bg-gradient-to-br from-cyan-500/20 to-blue-500/10 border-cyan-500 shadow-lg shadow-cyan-500/30'
              : 'bg-gradient-to-br from-gray-900/50 to-gray-800/30 border-gray-700 hover:border-cyan-500/50'
          ]"
        >
          <!-- Header com título e botão delete -->
          <div class="flex justify-between items-start gap-3 mb-3">
            <div class="flex-1 min-w-0 overflow-hidden">
              <div class="flex items-center gap-2 mb-1">
                <div class="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold">
                  {{ source.id }}
                </div>
                <h3 class="font-bold text-lg text-cyan-300 truncate">{{ getSourceName(source.url) }}</h3>
              </div>
              <div class="flex items-center gap-2 mt-2">
                <span :class="[
                  'px-2 py-1 rounded-full text-xs font-bold',
                  source.url.includes('json-raw') 
                    ? 'bg-purple-500/30 text-purple-300 border border-purple-500/50'
                    : 'bg-blue-500/30 text-blue-300 border border-blue-500/50'
                ]">
                  {{ source.url.includes('json-raw') ? '📋 Dados Locais' : '🌐 URL Remota' }}
                </span>
              </div>
            </div>
            <button 
              @click.stop="deleteSource(source.id)"
              class="px-2 py-1 rounded text-sm font-bold bg-red-600/80 hover:bg-red-600 text-white transform hover:scale-110 transition-all flex-shrink-0"
            >
              ✕
            </button>
          </div>

          <!-- Info Grid -->
          <div class="grid grid-cols-2 gap-2 mb-3 text-sm">
            <div class="p-2 bg-cyan-500/10 rounded border border-cyan-500/20">
              <p class="text-gray-400 text-xs">Items</p>
              <p class="font-bold text-cyan-300">{{ getSourceItemCount(source.id) }}</p>
            </div>
            <div class="p-2 bg-purple-500/10 rounded border border-purple-500/20">
              <p class="text-gray-400 text-xs">Tipo</p>
              <p class="font-bold text-purple-300">{{ source.url.includes('json-raw') ? 'Raw JSON' : 'URL' }}</p>
            </div>
          </div>

          <!-- SSL Toggle -->
          <div class="flex items-center gap-2">
            <Toggle :modelValue="downloadVerifySsl[source.id] ?? true" @update:modelValue="downloadVerifySsl[source.id] = $event">
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Verificação SSL
              </span>
            </Toggle>
          </div>

          <!-- Selected Indicator -->
          <div v-if="selectedSourceId === source.id" class="flex items-center justify-center gap-1 text-cyan-400 text-sm font-semibold">
            <span>✓ Selecionada</span>
          </div>
        </div>
      </div>

      <!-- Search Bar e Filtros -->
      <div v-if="selectedSourceId" ref="searchTopRef">
        <Card class="relative">
        <!-- Mensagem de erro ao carregar items -->
        <div v-if="itemLoadError" class="mb-4 p-3 bg-red-500/20 border border-red-500 rounded text-red-300 text-sm">
          {{ itemLoadError }}
        </div>

        <!-- Loading spinner -->
        <div v-if="isLoadingItems" class="mb-4 p-4 bg-blue-500/20 border border-blue-500 rounded text-blue-300 text-sm flex items-center gap-2">
          <span class="animate-spin">⏳</span>
          Carregando items da fonte...
        </div>

        <div class="flex gap-3">
          <div class="flex-1 relative">
            <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-cyan-400 pointer-events-none">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <input 
              v-model="searchQuery"
              placeholder="Buscar item..."
              type="text"
              class="w-full bg-gradient-to-r from-gray-900 to-gray-800 border-2 border-cyan-500/30 hover:border-cyan-500/50 focus:border-cyan-500 rounded-lg pl-10 pr-4 py-2.5 text-gray-100 outline-none transition-all duration-200 placeholder-gray-500"
              :disabled="isLoadingItems"
            />
          </div>
          <button v-if="searchQuery" @click="searchQuery = ''" type="button" class="px-4 py-2 rounded-lg text-sm font-semibold bg-red-600/80 hover:bg-red-600 text-white transform hover:scale-105 active:scale-95 transition-all duration-200" :disabled="isLoadingItems">
            ✕ Limpar
          </button>
        </div>

        <div v-if="getCategories.size > 0" class="mt-4">
          <p class="text-xs font-bold text-purple-400 mb-2">Categorias:</p>
          <div class="flex flex-wrap gap-2 overflow-visible relative z-0">
            <button
              @click="selectedCategory = null"
              :class="[
                'px-3 py-1 rounded text-sm transition-all flex items-center gap-2',
                !selectedCategory 
                  ? 'bg-cyan-500 text-black font-bold' 
                  : 'bg-gray-800 text-gray-300'
              ]"
            >
              Todas
              <span class="text-xs bg-black/30 px-2 py-0.5 rounded text-white font-semibold">
                {{ getCategoryItemCount(null) }}
              </span>
            </button>
            <div
              v-for="category in Array.from(getCategories)"
              :key="category"
              class="flex items-center gap-1 relative"
            >
              <button
                @click="selectedCategory = category"
                :class="[
                  'px-3 py-1 text-sm transition-all flex items-center gap-2 rounded',
                  selectedCategory === category 
                    ? 'bg-cyan-500 text-black font-bold' 
                    : 'bg-gray-700 text-gray-300 hover:text-white hover:bg-gray-600'
                ]"
              >
                {{ category }}
                <span class="text-xs bg-black/30 px-2 py-0.5 rounded text-white font-semibold">
                  {{ getCategoryItemCount(category) }}
                </span>
              </button>
              <button
                @click.stop="toggleCategoryMenu(category)"
                :class="[
                  'px-2 py-1 text-gray-400 hover:text-cyan-300 transition-colors btn-translucent',
                  activeCategoryMenu === category ? 'text-cyan-300' : ''
                ]"
                title="Menu da categoria"
              >
                ⋮
              </button>
              
              <!-- Dropdown Menu - Posicionado fora -->
              <div 
                v-if="activeCategoryMenu === category"
                class="absolute top-full right-0 mt-1 bg-gray-900 border border-cyan-500/50 rounded shadow-lg shadow-cyan-500/20 z-[9999] min-w-max max-w-md pointer-events-auto"
                @click.stop
              >
                <button
                  @click="showCategoryDetails(category)"
                  class="block w-full text-left px-4 py-2 text-sm font-semibold text-cyan-300 hover:bg-cyan-500/20 hover:text-cyan-200 hover:border-l-2 hover:border-cyan-400 transition-all duration-200 whitespace-nowrap relative z-50 bg-gray-900"
                >
                  Detalhes
                </button>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Items List -->
      <div v-if="selectedSourceId && filteredItems.length > 0" class="space-y-3">
        <p class="text-sm text-gray-400">{{ filteredItems.length }} item(ns) • Página {{ currentPage }}/{{ totalPages }}</p>
        
        <!-- Items Paginados (GRID VIEW) -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="item in paginatedItems" :key="item.id" class="h-full">
            <SteamGameCard :item="item" @download="openDownloadDialog" />
          </div>
        </div>

        <!-- Controles de Paginação -->
        <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-6">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-2 rounded-lg font-semibold text-sm bg-gray-800 text-gray-300 border border-gray-700 hover:border-cyan-500 hover:text-cyan-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            ← Anterior
          </button>
          
          <!-- Primeira página (se não visível) -->
          <button
            v-if="visiblePages[0] > 1"
            @click="currentPage = 1"
            class="px-3 py-2 rounded-lg font-semibold text-sm bg-gray-800 text-gray-300 border border-gray-700 hover:border-cyan-500"
          >
            1
          </button>
          
          <!-- Reticências (se houver gap) -->
          <span v-if="visiblePages[0] > 2" class="px-2 text-gray-500">...</span>
          
          <!-- Páginas visíveis -->
          <div class="flex gap-1">
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="currentPage = page"
              :class="[
                'px-3 py-2 rounded-lg font-semibold text-sm transition-all',
                currentPage === page
                  ? 'bg-cyan-500 text-black'
                  : 'bg-gray-800 text-gray-300 border border-gray-700 hover:border-cyan-500'
              ]"
            >
              {{ page }}
            </button>
          </div>
          
          <!-- Reticências (se houver gap) -->
          <span v-if="visiblePages[visiblePages.length - 1] < totalPages - 1" class="px-2 text-gray-500">...</span>
          
          <!-- Última página (se não visível) -->
          <button
            v-if="visiblePages[visiblePages.length - 1] < totalPages"
            @click="currentPage = totalPages"
            class="px-3 py-2 rounded-lg font-semibold text-sm bg-gray-800 text-gray-300 border border-gray-700 hover:border-cyan-500"
          >
            {{ totalPages }}
          </button>

          <button 
            @click="currentPage = Math.min(totalPages, currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 rounded-lg font-semibold text-sm bg-gray-800 text-gray-300 border border-gray-700 hover:border-cyan-500 hover:text-cyan-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            Próxima →
          </button>
        </div>
      </div>

      <Card v-else-if="selectedSourceId && filteredItems.length === 0" class="text-center py-8">
        <p class="text-gray-400">Nenhum item encontrado.</p>
      </Card>
    </div>

    <Card v-else class="text-center py-8">
      <p class="text-gray-400">Nenhuma fonte adicionada.</p>
    </Card>
  </div>

  <!-- Modal de Confirmação - Deletar Fonte -->
  <Modal v-if="showDeleteModal && sourceToDelete" @close="showDeleteModal = false">
      <div>
        <h3 class="text-lg font-bold text-red-400 mb-4">⚠️ Deletar Fonte</h3>
        <p class="text-gray-300 mb-4">
          Tem certeza que deseja deletar a fonte <span class="font-semibold text-cyan-300">"{{ sourceToDelete.title || sourceToDelete.url }}"</span>?
        </p>
        <p class="text-sm text-gray-400 mb-6">
          Todos os items desta fonte serão removidos e não poderão ser recuperados.
        </p>
        
        <div class="flex gap-2 pt-4 border-t border-gray-700">
          <button 
            type="button"
            @click="showDeleteModal = false"
            class="flex-1 border-gray-600/50 text-gray-300 hover:bg-gray-600/10 hover:border-gray-600 transition-all flex items-center justify-center gap-2 btn-translucent"
          >
            Cancelar
          </button>
          <button 
            type="button"
            @click="confirmDeleteSource"
            class="flex-1 px-4 py-2 rounded-lg font-semibold bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transform hover:scale-105 active:scale-95 transition-all duration-300 flex items-center justify-center gap-2"
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
              <path d="M9 3H15V5H9V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M5 5H19V7H18L17 20C17 21.1046 16.1046 22 15 22H9C7.89543 22 7 21.1046 7 20L6 7H5V5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <line x1="10" y1="10" x2="10" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="14" y1="10" x2="14" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Deletar
          </button>
        </div>
      </div>
    </Modal>

    <!-- Download Dialog -->
    <Modal v-if="showDownloadDialog" @close="showDownloadDialog = false">
      <div>
        <h3 class="text-lg font-bold text-cyan-400 mb-4">⬇️ Baixar Item</h3>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-400">Item:</p>
            <p class="text-cyan-300 font-semibold">{{ selectedItem?.name }}</p>
          </div>
          
          <div>
            <p class="text-sm text-gray-400">Tamanho:</p>
            <p class="text-cyan-300">
              <span v-if="modalInfo.checking">Verificando...</span>
              <span v-else-if="modalInfo.size">{{ formatBytes(modalInfo.size) }} <span class="text-xs text-gray-400">(ETA ~{{ modalInfo.eta }}s)</span></span>
              <span v-else>{{ formatBytes(selectedItem?.size) }}</span>
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
                class="border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 btn-translucent"
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
              class="flex-1 border-cyan-500/50 text-cyan-300 hover:bg-cyan-500/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 btn-translucent"
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
          <Button variant="outline" class="flex-1 btn-translucent" @click="showManualFolderModal = false">
            Cancelar
          </Button>
          <Button variant="success" class="flex-1" @click="() => { downloadDestination.value = manualFolderPath.value || downloadDestination.value; showManualFolderModal = false }">
            Usar esta pasta
          </Button>
        </div>
      </div>
    </Modal>

    <!-- Modal de Detalhes da Categoria -->
    <Modal v-if="showCategoryDetailsModal && categoryDetailsData" @close="showCategoryDetailsModal = false" title="Detalhes da Categoria" :showDefaultButtons="false">
      <div class="space-y-4 max-h-96 overflow-y-auto">
        <div class="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 p-4 rounded-lg border border-cyan-500/30">
          <h3 class="text-lg font-bold text-cyan-300 mb-2">{{ categoryDetailsData.categoryName }}</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-gray-400">Total de Itens</p>
              <p class="text-2xl font-bold text-cyan-300">{{ categoryDetailsData.totalItems }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-400">Tamanho Total</p>
              <p class="text-2xl font-bold text-emerald-300">{{ categoryDetailsData.totalSize }}</p>
            </div>
          </div>
        </div>

        <div v-if="categoryDetailsData.subcategories.length > 0" class="space-y-2">
          <p class="text-sm font-semibold text-purple-400 mb-3">Subcategorias:</p>
          <div v-for="(subcat, idx) in categoryDetailsData.subcategories" :key="idx" class="bg-gray-800/50 p-3 rounded border border-gray-700 hover:border-cyan-500/50 transition-colors">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <p class="text-sm font-semibold text-gray-200">📁 {{ subcat.name }}</p>
                <p class="text-xs text-gray-400">{{ subcat.count }} itens</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-bold text-emerald-300">{{ subcat.size }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-2 pt-4">
          <Button 
            @click="showCategoryDetailsModal = false"
            variant="outline"
            size="md"
            class="flex-1 flex items-center justify-center gap-1 whitespace-nowrap btn-translucent"
          >
            Fechar
          </Button>
        </div>
      </div>
    </Modal>
    <!-- Source Analysis Modal -->
    <SourceAnalysisModal
      :open="showAnalysisModal"
      :candidates="analysisCandidates"
      :original-item="analysisOriginalItem"
      :original-health="analysisOriginalItem?.health"
      :is-loading="analysisLoading"
      @close="showAnalysisModal = false"
      @confirm="handleSafeSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useDownloadStore } from '../stores/download'
import api from '../services/api'
import Card from '../components/Card.vue'
import SteamGameCard from '../components/SteamGameCard.vue'
import Button from '../components/Button.vue'
import Input from '../components/Input.vue'
import StatCard from '../components/StatCard.vue'
import Modal from '../components/Modal.vue'
import Toggle from '../components/Toggle.vue'
import SourceAnalysisModal from '../components/SourceAnalysisModal.vue'
import { useToastStore } from '../stores/toast'
import { formatBytes } from '../utils/format'

const downloadStore = useDownloadStore()
const searchTopRef = ref(null)
const sources = ref([])
const selectedSourceId = ref(null)
// ... (keep existing refs)
const searchQuery = ref('')
const searchQueryDebounced = ref('')
const selectedCategory = ref(null)
const showJsonPaste = ref(false)
const newSourceUrl = ref('')
const jsonPasteContent = ref('')
const showDownloadDialog = ref(false)
const selectedItem = ref(null)
const downloadDestination = ref('downloads')
const downloadVerifySsl = ref({}) 
const showManualFolderModal = ref(false)
const manualFolderPath = ref('')
const browseLoading = ref(false)
const isAddingSource = ref(false)
const addError = ref('')
const isLoadingItems = ref(false)
const itemLoadError = ref('')
const modalInfo = ref({ size: null, accept_range: false, eta: null, checking: false })
const activeCategoryMenu = ref(null)
const showCategoryDetailsModal = ref(false)
const categoryDetailsData = ref(null)

// Analysis State
const showAnalysisModal = ref(false)
const analysisCandidates = ref([])
const analysisOriginalItem = ref(null)
const analysisLoading = ref(false)

// ... (keep existing methods)

// Wrapper to handle safe download after analysis
const handleSafeSelect = (selectedCandidate) => {
  showAnalysisModal.value = false
  // Map candidate back to item format if needed, or just use it
  const finalItem = selectedCandidate.item || selectedCandidate
  // Ensure source_id is preserved if available, or we need to find it?
  // Actually, our download logic needs source_id for SSL settings etc.
  // The candidate item should have source_id.
  openDownloadConfigurationDialog(finalItem)
}

const handleSafeKeepOriginal = () => {
  showAnalysisModal.value = false
  if (analysisOriginalItem.value) {
    openDownloadConfigurationDialog(analysisOriginalItem.value)
  }
}

// Renamed original openDownloadDialog to openDownloadConfigurationDialog
function openDownloadConfigurationDialog(item) {
  console.log(`🔥 [Sources] Opening config dialog for:`, item.name)
  selectedItem.value = item
  downloadDestination.value = 'downloads'
  
  // Reset modal info
  modalInfo.value = { size: null, accept_range: false, eta: null, checking: true, browseLoading: false }
  
  try {
    const url = encodeURIComponent(item.url)
    api.get(`/api/supports_range?url=${url}`).then(({ data }) => {
      modalInfo.value.size = data.size || null
      modalInfo.value.accept_range = !!data.accept_ranges
      if (data.size && modalInfo.value.accept_range) {
        const baseline = 1024 * 1024
        modalInfo.value.eta = Math.round((data.size / baseline))
      }
    }).catch(err => {
      console.warn('supports_range failed', err)
    }).finally(() => {
      modalInfo.value.checking = false
    })
  } catch (e) {
    modalInfo.value.checking = false
  }

  showDownloadDialog.value = true
}

// New entry point triggered by @download
// New entry point triggered by @download
async function openDownloadDialog(item) {
  console.log(`🔍 [Sources] Starting analysis for:`, item.name)
  
  // 1. Trigger Analysis UI Immediately
  analysisOriginalItem.value = item // Show basic info during load
  analysisCandidates.value = []     // Clear previous
  analysisLoading.value = true
  showAnalysisModal.value = true    // Open modal in loading state
  
  try {
    const resp = await api.post('/api/analysis/pre-job', { item: item })
    
    // 2. Check results
    if (resp.data && resp.data.candidates && resp.data.candidates.length > 0) {
       console.log(`✨ Suggested ${resp.data.candidates.length} sources`)
       
       analysisCandidates.value = resp.data.candidates
       // Keep analysisOriginalItem as set, but enrich health
       
       // Sincronizar dados da fonte original para o modal
       const currentSource = sources.value.find(s => s.id === item.source_id)
       const sourceName = currentSource?.title || getSourceName(currentSource?.url)
       
       const enrichedOriginal = {
         ...item,
         source: sourceName,
         source_title: sourceName
       }
       
       // Se o backend retornou saúde enriquecida, usar!
       if (resp.data.original_health) {
          enrichedOriginal.health = resp.data.original_health
          // Se tiver seeders direto no health, atualizar root
          if (resp.data.original_health.seeders !== undefined) {
             enrichedOriginal.seeders = resp.data.original_health.seeders
             enrichedOriginal.leechers = resp.data.original_health.leechers
          }
       }
       
       analysisOriginalItem.value = enrichedOriginal
       
       // showAnalysisModal.value = true // Already open
       analysisLoading.value = false   // Switch to content view
       return
    }
  } catch (e) {
    console.warn(`Analysis failed or skipped:`, e)
  } finally {
    // analysisLoading.value = false // Handled inside success or below
  }
  
  // 3. Fallback to normal flow (No candidates or Error)
  // Close modal (it was in loading state)
  showAnalysisModal.value = false
  analysisLoading.value = false
  
  // Proceed to normal confirmation
  openDownloadConfigurationDialog(item)
}


// Modal de confirmação para deletar
const showDeleteModal = ref(false)
const sourceToDelete = ref(null)

// Paginação para performance com muitos items
// Paginação para performance com muitos items
const itemsPerPage = 24
const currentPage = ref(1)

watch(currentPage, async () => {
  await nextTick()
  if (searchTopRef.value?.scrollIntoView) {
    searchTopRef.value.scrollIntoView({ behavior: 'smooth' })
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
})

// Debounce para search - aumentado para 300ms para evitar engasgos
let searchDebounceTimer = null
watch(searchQuery, (newVal) => {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    searchQueryDebounced.value = newVal
    currentPage.value = 1  // Reset para primeira página ao filtrar
  }, 300)
})

// Reset página quando categoria muda
watch(selectedCategory, () => {
  currentPage.value = 1
})

onMounted(async () => {
  await downloadStore.fetchSources()
  sources.value = downloadStore.sources
  await downloadStore.fetchAllItems()
})

const getSourceItemCount = (sourceId) => {
  return downloadStore.items.filter(i => i.source_id === sourceId).length
}

// Extrai nome amigável da URL da fonte
const getSourceName = (url) => {
  if (!url) return 'Fonte Desconhecida'
  
  // Para fontes locais (JSON colado)
  if (url.includes('json-raw')) {
    return 'JSON Local'
  }
  
  try {
    // Extrai o nome do arquivo da URL
    const urlObj = new URL(url)
    const pathname = urlObj.pathname
    const filename = pathname.split('/').pop()
    
    // Remove extensão .json
    let name = filename.replace(/\.json$/i, '')
    
    // Capitaliza primeira letra
    name = name.charAt(0).toUpperCase() + name.slice(1)
    
    return name || 'Fonte Remota'
  } catch (e) {
    // Se não conseguir fazer parse da URL, tenta extrair do final
    const parts = url.split('/')
    const lastPart = parts[parts.length - 1]
    const name = lastPart.replace(/\.json$/i, '')
    return name.charAt(0).toUpperCase() + name.slice(1) || 'Fonte Remota'
  }
}

const getCategories = computed(() => {
  const categories = new Set()
  downloadStore.items
    .filter(i => i.source_id === selectedSourceId.value)
    .forEach(i => {
      if (i.category) categories.add(i.category)
    })
  return categories
})

// Função de busca fuzzy otimizada - rápida E precisa
function fuzzyScore(text, query) {
  const t = text.toLowerCase()
  const q = query.toLowerCase()
  
  // Pontuação perfeita se for match exato
  if (t === q) return 1000
  
  // Se contém exatamente como substring
  const idx = t.indexOf(q)
  if (idx !== -1) {
    // Bonus se for no inicio
    if (idx === 0) return 950
    // Bonus se for após espaço ou caractere especial
    if (idx > 0 && /[\s\-_\.]/.test(t[idx - 1])) return 920
    return 850
  }
  
  // Busca por primeira letra de cada palavra
  const words = t.split(/[\s\-_\.]+/).filter(w => w.length > 0)
  const initials = words.map(w => w[0]).join('')
  
  if (initials.includes(q)) return 800
  
  // Busca fuzzy precisa: cada letra do query deve aparecer em ordem no text
  let textIdx = 0
  let matchCount = 0
  let lastDistance = 0
  
  for (let i = 0; i < q.length; i++) {
    const found = t.indexOf(q[i], textIdx)
    if (found === -1) return 0 // Uma letra não encontrada = sem match
    
    // Penaliza se as letras estão muito separadas
    const distance = found - textIdx
    if (distance > 5) {
      lastDistance = 0
      break
    }
    
    matchCount++
    textIdx = found + 1
    lastDistance = distance
  }
  
  // Se todas as letras foram encontradas em sequência
  if (matchCount === q.length) {
    return 200 + Math.max(0, 100 - lastDistance * 10)
  }
  
  return 0
}

// Função para calcular score total do item - otimizada
function itemScore(item, query) {
  if (!query) return 0
  
  const nameScore = fuzzyScore(item.name, query)
  if (nameScore > 0) return nameScore
  
  return item.category ? fuzzyScore(item.category, query) * 0.5 : 0
}

// Função para extrair primeira palavra
function getFirstWord(text) {
  return text.split(/[\s:\-_\.\(\)]/)[0].toLowerCase()
}

// Função para buscar por primeiro termo ou primeira letra de cada palavra
function matchStartsWith(text, query) {
  const t = text.toLowerCase()
  const q = query.toLowerCase()
  const words = t.split(/[\s:\-_\.\(\)]+/).filter(w => w.length > 0)
  
  // Verificar se começa com a query
  if (t.startsWith(q)) return 950
  
  // Verificar se alguma palavra começa com a query
  for (const word of words) {
    if (word.startsWith(q)) return 900
  }
  
  // Verificar se as primeiras letras de cada palavra formam a query
  const initials = words.map(w => w[0]).join('').toLowerCase()
  if (initials.includes(q)) return 850
  
  // Verificar match de primeira letra de cada palavra individualmente
  let matches = 0
  for (let i = 0; i < q.length && i < words.length; i++) {
    if (words[i].startsWith(q[i])) matches++
  }
  if (matches > 0 && matches === q.length) return 800
  
  return 0
}

const filteredItems = computed(() => {
  let items = downloadStore.items.filter(i => i.source_id === selectedSourceId.value)
  
  // Aplicar filtro de categoria primeiro (mais rápido)
  if (selectedCategory.value) {
    items = items.filter(i => i.category === selectedCategory.value)
  }
  
  // Aplicar busca por texto
  if (searchQueryDebounced.value) {
    const query = searchQueryDebounced.value.trim().toLowerCase()
    
    if (query.length > 0) {
      // Calcular score para cada item - otimizado
      const scored = items.map(item => {
        const nameScore = fuzzyScore(item.name, query)
        const categoryScore = item.category ? fuzzyScore(item.category, query) : 0
        
        // Priorizar match no name
        const finalScore = nameScore > 0 ? nameScore : categoryScore * 0.6
        
        return { item, score: finalScore }
      })
      
      // Filtrar items com score > 0 e ordenar por score
      items = scored
        .filter(s => s.score > 0)
        .sort((a, b) => b.score - a.score)
        .map(s => s.item)
    }
  }
  
  // Ordenar por data de upload (mais recentes primeiro)
  // Items sem data vão para o final
  items.sort((a, b) => {
    const dateA = a.uploadDate ? new Date(a.uploadDate).getTime() : 0
    const dateB = b.uploadDate ? new Date(b.uploadDate).getTime() : 0
    return dateB - dateA // Ordem decrescente (mais recente primeiro)
  })
  
  return items
})

// Items paginados para renderizar
const paginatedItems = computed(() => {
  const total = filteredItems.value.length
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredItems.value.slice(start, end)
})

// Total de páginas
const totalPages = computed(() => {
  return Math.ceil(filteredItems.value.length / itemsPerPage)
})

// Intervalo de páginas visíveis (estilo Steam)
const maxVisiblePages = 5
const visiblePages = computed(() => {
  if (totalPages.value <= maxVisiblePages) {
    // Se tem 5 ou menos páginas, mostrar todas
    return Array.from({ length: totalPages.value }, (_, i) => i + 1)
  }
  
  // Calcular range de páginas centrado na página atual
  let start = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
  let end = Math.min(totalPages.value, start + maxVisiblePages - 1)
  
  // Ajustar se chegou no final
  if (end - start + 1 < maxVisiblePages) {
    start = Math.max(1, end - maxVisiblePages + 1)
  }
  
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

async function selectSource(source) {
  console.log(`\n🔄 [Sources] selectSource(${source.id}) - Carregando items sob demanda`)
  selectedSourceId.value = source.id
  searchQuery.value = ''
  selectedCategory.value = null
  
  // Garantir que o objeto de SSL seja reativo - inicializar apenas se não existir
  if (!(source.id in downloadVerifySsl.value)) {
    // Usar Object.assign para garantir reatividade
    Object.assign(downloadVerifySsl.value, { [source.id]: true })
  }
  // Se já existe, manter o valor anterior (não sobrescrever)
  
  // Limpar items anteriores
  downloadStore.items = []
  
  // Carregar items da fonte (releitura do JSON)
  try {
    isLoadingItems.value = true
    itemLoadError.value = ''
    console.log(`⏳ Aguardando items de "${source.title}"...`)
    await downloadStore.fetchSourceItems(source.id)
    console.log(`✓ Items carregados com sucesso`)
  } catch (e) {
    console.error(`❌ Erro ao carregar items:`, e.message)
    itemLoadError.value = `Erro ao carregar items: ${e.message}`
  } finally {
    isLoadingItems.value = false
  }
}

async function handleAddSource() {
  if (!newSourceUrl.value) {
    try { const ts = useToastStore(); ts.push('Erro', 'Por favor, insira uma URL') } catch (e) {}
    return
  }
  addError.value = ''
  isAddingSource.value = true
  
  try {
    // Validar URL
    new URL(newSourceUrl.value)

    const result = await downloadStore.loadJsonFromUrl(newSourceUrl.value)
    sources.value = downloadStore.sources
    await downloadStore.fetchAllItems()
    
    // Selecionar última fonte adicionada
    if (sources.value.length > 0) {
      selectedSourceId.value = sources.value[sources.value.length - 1].id
    }
    
    newSourceUrl.value = ''
    
    // Mostrar aviso se for duplicata
    if (result.duplicate) {
      try { const ts = useToastStore(); ts.push('Aviso', 'Fonte já existe') } catch (e) {}
    } else {
      try { const ts = useToastStore(); ts.push('Fonte', 'Fonte JSON adicionada com sucesso') } catch (e) {}
    }
  } catch (e) {
    const errMsg = e.message || 'Erro ao adicionar fonte'
    addError.value = errMsg
  } finally {
    isAddingSource.value = false
  }
}

async function handleAddRawJson() {
  if (!jsonPasteContent.value) return
  addError.value = ''
  isAddingSource.value = true
  
  try {
    const data = JSON.parse(jsonPasteContent.value)
    const result = await downloadStore.loadJsonRaw(data)
    sources.value = downloadStore.sources
    await downloadStore.fetchAllItems()
    selectedSourceId.value = sources.value[sources.value.length - 1].id
    jsonPasteContent.value = ''
    showJsonPaste.value = false
    
    // Mostrar aviso se for duplicata
    if (result.duplicate) {
      try { const ts = useToastStore(); ts.push('Aviso', 'Fonte já existe') } catch (e) {}
    } else {
      try { const ts = useToastStore(); ts.push('Fonte', 'Fonte JSON adicionada com sucesso') } catch (e) {}
    }
  } catch (e) {
    addError.value = e.message || 'Erro ao adicionar JSON'
    console.error('Erro:', e)
  } finally {
    isAddingSource.value = false
  }
}

async function deleteSource(sourceId) {
  console.log(`🗑️ [Sources] Abrindo modal de confirmação para deletar fonte #${sourceId}`)
  sourceToDelete.value = sources.value.find(s => s.id === sourceId)
  showDeleteModal.value = true
}

async function confirmDeleteSource() {
  const sourceId = sourceToDelete.value?.id
  if (!sourceId) return

  console.log(`🗑️ [Sources] Iniciando deleção da fonte #${sourceId}`)
  showDeleteModal.value = false
  
  try {
    console.log(`📤 [Sources] Chamando API para deletar fonte #${sourceId}`)
    await downloadStore.deleteSource(sourceId)
    console.log(`✓ [Sources] API respondeu com sucesso`)
    
    console.log(`📝 [Sources] Removendo fonte #${sourceId} do array local`)
    sources.value = sources.value.filter(s => s.id !== sourceId)
    console.log(`✓ [Sources] Fonte removida do array - Total: ${sources.value.length}`)
    
    console.log(`📝 [Sources] Removendo items da fonte #${sourceId} do store`)
    const itemsAntes = downloadStore.items.length
    downloadStore.items = downloadStore.items.filter(i => i.source_id !== sourceId)
    console.log(`✓ [Sources] Items removidos: ${itemsAntes - downloadStore.items.length} items deletados`)
    
    if (selectedSourceId.value === sourceId) {
      console.log(`✓ [Sources] Limpando seleção (fonte deletada estava selecionada)`)
      selectedSourceId.value = null
      searchQuery.value = ''
      selectedCategory.value = null
    }
    
    console.log(`✅ [Sources] Fonte #${sourceId} deletada com sucesso`)
    try { const ts = useToastStore(); ts.push('Fonte deletada', 'A fonte foi removida com sucesso') } catch (e) {}
  } catch (e) {
    console.error(`❌ [Sources] Erro ao deletar fonte #${sourceId}:`, e)
    try { const ts = useToastStore(); ts.push('Erro', `Erro ao deletar fonte: ${e.message}`) } catch (ee) {}
  }
}



async function browsePath() {
  // Try backend native picker first, then fallback to manual modal
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

async function confirmDownload() {
  console.log(`📥 [confirmDownload] Iniciado`)
  
  if (!selectedItem.value) {
    const msg = 'Nenhum item selecionado'
    console.error(`❌ ${msg}`)
    try { const ts = useToastStore(); ts.push('Erro', msg) } catch (e) { alert(msg) }
    return
  }
  
  try {
    // Validar destination
    let destCandidate = (downloadDestination.value || 'downloads').toString()
    const destLower = destCandidate.toLowerCase()
    const suspicious = destLower.startsWith('http') || destLower.startsWith('magnet:') || destCandidate.includes('%25') || destCandidate.includes('announce')
    if (suspicious) {
      console.warn(`⚠️  Destino suspeito detectado, usando padrão`)
      destCandidate = 'downloads'
    }

    console.log(`📋 Preparando job com:`, {
      url: selectedItem.value.url,
      name: selectedItem.value.name,
      destination: destCandidate,
      verify_ssl: (downloadVerifySsl.value[selectedItem.value.source_id] !== false) ?? true,
      size: selectedItem.value.size || null
    })
    
    // DEBUG: Log adicional bem visível
    console.log(`🔒 SSL STATUS: source=${selectedItem.value.source_id}, value=${downloadVerifySsl.value[selectedItem.value.source_id]}, send=${(downloadVerifySsl.value[selectedItem.value.source_id] !== false) ?? true}`)

    const jobData = {
      url: selectedItem.value.url,
      name: selectedItem.value.name,
      destination: destCandidate,
      verify_ssl: (downloadVerifySsl.value[selectedItem.value.source_id] !== false) ?? true,
      size: selectedItem.value.size || null
    }
    
    console.log(`🚀 Chamando createJob com:`, jobData)
    const result = await downloadStore.createJob(jobData)
    
    if (!result) {
      throw new Error('Resposta nula do servidor')
    }
    
    if (!result.job_id) {
      throw new Error(`Resposta inválida do servidor: ${JSON.stringify(result)}`)
    }

    console.log(`✅ Job criado com sucesso: #${result.job_id}`)
    
    // Verifica se já há downloads rodando
    const hasRunning = downloadStore.jobs.some(j => j.status === 'running')
    const toastMsg = hasRunning ? `Download #${result.job_id} colocado na fila` : `Download #${result.job_id} iniciado`
    try { const ts = useToastStore(); ts.push('Download', toastMsg) } catch (e) { alert(toastMsg) }
    
    showDownloadDialog.value = false
    selectedItem.value = null
  } catch (e) {
    const errMsg = e.response?.data?.detail || e.message || 'Erro ao criar job'
    console.error(`❌ Erro em confirmDownload:`, e, `\nMensagem: ${errMsg}`)
    try { const ts = useToastStore(); ts.push('Erro', errMsg) } catch (ee) { alert(`Erro: ${errMsg}`) }
  }
}

// Funções para menu hamburger da categoria
const getCategoryItemCount = (category) => {
  if (category === null) {
    return downloadStore.items.filter(i => i.source_id === selectedSourceId.value).length
  }
  return downloadStore.items.filter(i => i.source_id === selectedSourceId.value && i.category === category).length
}

const toggleCategoryMenu = (category) => {
  activeCategoryMenu.value = activeCategoryMenu.value === category ? null : category
}

const showCategoryDetails = (category) => {
  const items = downloadStore.items.filter(
    i => i.source_id === selectedSourceId.value && i.category === category
  )
  
  if (items.length === 0) {
    alert('Nenhum item nesta categoria')
    return
  }
  
  // Agrupar itens por tipo/subcategoria
  const grouped = {}
  items.forEach(item => {
    const subcat = item.type || 'Sem tipo'
    if (!grouped[subcat]) grouped[subcat] = { count: 0, size: 0 }
    grouped[subcat].count++
    grouped[subcat].size += item.size || 0
  })
  
  // Montar dados para o modal
  const totalSize = Object.values(grouped).reduce((sum, g) => sum + g.size, 0)
  const subcategories = Object.entries(grouped)
    .map(([name, data]) => ({
      name,
      count: data.count,
      size: formatBytes(data.size)
    }))
    .sort((a, b) => b.count - a.count)
  
  categoryDetailsData.value = {
    categoryName: category,
    totalItems: items.length,
    totalSize: formatBytes(totalSize),
    subcategories
  }
  
  showCategoryDetailsModal.value = true
  activeCategoryMenu.value = null
}

// Funções antigas removidas
const downloadAllFromCategory = (category) => {
  alert('Opção desabilitada')
  activeCategoryMenu.value = null
}

const copyCategoryItems = (category) => {
  alert('Opção desabilitada')
  activeCategoryMenu.value = null
}

const showCategoryStats = (category) => {
  alert('Opção desabilitada')
  activeCategoryMenu.value = null
}

// Funções de formatação de data
function formatRelativeDate(dateString) {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  
  if (diffMinutes < 1) return 'agora'
  if (diffMinutes < 60) return `há ${diffMinutes}min`
  if (diffHours < 24) return `há ${diffHours}h`
  if (diffDays === 0) return 'hoje'
  if (diffDays === 1) return 'ontem'
  if (diffDays < 7) return `há ${diffDays} dias`
  if (diffDays < 30) return `há ${Math.floor(diffDays / 7)} semanas`
  if (diffDays < 365) return `há ${Math.floor(diffDays / 30)} meses`
  return `há ${Math.floor(diffDays / 365)} anos`
}

function formatFullDate(dateString) {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function isRecentUpload(dateString) {
  if (!dateString) return false
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  return diffDays < 30 // Considera recente se foi adicionado nos últimos 30 dias
}
</script>
