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
          <h3 class="text-sm font-semibold text-cyan-400">Itens Indexados</h3>
        </div>
        <p class="text-2xl font-bold text-cyan-300 text-center">{{ libraryStats.total_items }}</p>
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
          <h3 class="text-sm font-semibold text-purple-400">Jogos/Entradas</h3>
        </div>
        <p class="text-2xl font-bold text-purple-300 text-center">{{ libraryStats.total_groups }}</p>
      </div>
    </div>

    <Card class="bg-gradient-to-br from-gray-900/40 to-gray-900/20 border border-cyan-500/20">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div class="text-sm text-gray-400">
          A biblioteca carrega automaticamente os itens de todas as fontes.
        </div>
        <router-link to="/library">
          <Button variant="primary" class="px-4 py-2">
            Abrir Biblioteca
          </Button>
        </router-link>
      </div>
    </Card>

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
          :class="[
            'p-4 rounded-lg border cursor-pointer transition-all hover:shadow-lg',
            'bg-gradient-to-br from-gray-900/50 to-gray-800/30 border-gray-700 hover:border-cyan-500/50'
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

          <div class="flex items-center justify-center gap-1 text-cyan-400 text-sm font-semibold">
            <router-link to="/library" class="hover:text-cyan-200">Ver na Biblioteca</router-link>
          </div>
        </div>
      </div>
    </div>

    <Card v-else class="text-center py-8">
      <p class="text-gray-400">Nenhuma fonte adicionada.</p>
    </Card>

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
            Deletar
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDownloadStore } from '../stores/download'
import api from '../services/api'
import Card from '../components/Card.vue'
import Button from '../components/Button.vue'
import Input from '../components/Input.vue'
import Modal from '../components/Modal.vue'
import Toggle from '../components/Toggle.vue'
import { useToastStore } from '../stores/toast'

const downloadStore = useDownloadStore()
const sources = ref([])
const showJsonPaste = ref(false)
const newSourceUrl = ref('')
const jsonPasteContent = ref('')
const downloadVerifySsl = ref({}) 
const isAddingSource = ref(false)
const addError = ref('')

const libraryStats = ref({ total_items: 0, total_groups: 0 })
const librarySourceCounts = ref({})

const showDeleteModal = ref(false)
const sourceToDelete = ref(null)

onMounted(async () => {
  await downloadStore.fetchSources()
  sources.value = downloadStore.sources
  await refreshLibraryInfo(false)
})

const getSourceItemCount = (sourceId) => {
  const v = librarySourceCounts.value?.[sourceId]
  return typeof v === 'number' ? v : 0
}

async function refreshLibraryInfo(refresh) {
  try {
    const resp = await api.get('/api/library' + (refresh ? '?refresh=true' : ''))
    const data = resp.data || {}
    const groups = Array.isArray(data.groups) ? data.groups : []
    libraryStats.value = {
      total_items: data.total_items || 0,
      total_groups: groups.length
    }

    const counts = {}
    for (const g of groups) {
      const versions = Array.isArray(g?.versions) ? g.versions : []
      for (const it of versions) {
        const sid = it?.source_id
        if (sid == null) continue
        counts[sid] = (counts[sid] || 0) + 1
      }
    }
    librarySourceCounts.value = counts
  } catch (e) {
    // ignore; keep last known stats
  }
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
    await refreshLibraryInfo(true)
    
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
    await refreshLibraryInfo(true)
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
    await refreshLibraryInfo(true)
    
    console.log(`✅ [Sources] Fonte #${sourceId} deletada com sucesso`)
    try { const ts = useToastStore(); ts.push('Fonte deletada', 'A fonte foi removida com sucesso') } catch (e) {}
  } catch (e) {
    console.error(`❌ [Sources] Erro ao deletar fonte #${sourceId}:`, e)
    try { const ts = useToastStore(); ts.push('Erro', `Erro ao deletar fonte: ${e.message}`) } catch (ee) {}
  }
}
</script>
