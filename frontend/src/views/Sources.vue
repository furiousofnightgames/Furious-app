<template>
  <div class="space-y-6">
    <!-- Header Stats with SVG Icons -->
    <!-- Header Stats with Premium Holo-Design -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Card 1: Fontes Salvas -->
      <div class="relative group overflow-hidden rounded-2xl p-0.5 bg-gradient-to-br from-amber-500/20 via-orange-500/5 to-transparent hover:from-amber-400/40 transition-all duration-500 hover:shadow-[0_0_30px_-5px_rgba(245,158,11,0.3)]">
        <div class="absolute inset-0 bg-gray-900/90 backdrop-blur-xl rounded-2xl"></div>
        <div class="relative p-6 flex items-center justify-between h-full">
          <div>
            <p class="text-amber-400/80 text-xs font-bold uppercase tracking-wider mb-1">Fontes Ativas</p>
            <h3 class="text-4xl font-black text-amber-100 drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]">{{ sources.length }}</h3>
          </div>
          <div class="w-14 h-14 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shadow-[0_0_15px_rgba(245,158,11,0.15)] group-hover:scale-110 transition-transform duration-300">
             <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-amber-400">
               <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
             </svg>
          </div>
        </div>
      </div>

      <!-- Card 2: Itens Indexados -->
      <div class="relative group overflow-hidden rounded-2xl p-0.5 bg-gradient-to-br from-cyan-500/20 via-blue-500/5 to-transparent hover:from-cyan-400/40 transition-all duration-500 hover:shadow-[0_0_30px_-5px_rgba(6,182,212,0.3)]">
        <div class="absolute inset-0 bg-gray-900/90 backdrop-blur-xl rounded-2xl"></div>
        <div class="relative p-6 flex items-center justify-between h-full">
          <div>
            <p class="text-cyan-400/80 text-xs font-bold uppercase tracking-wider mb-1">Itens Indexados</p>
            <h3 class="text-4xl font-black text-cyan-100 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]">{{ libraryStats.total_items }}</h3>
          </div>
          <div class="w-14 h-14 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.15)] group-hover:scale-110 transition-transform duration-300">
             <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-cyan-400">
               <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
             </svg>
          </div>
        </div>
      </div>

      <!-- Card 3: Categorias -->
      <div class="relative group overflow-hidden rounded-2xl p-0.5 bg-gradient-to-br from-purple-500/20 via-pink-500/5 to-transparent hover:from-purple-400/40 transition-all duration-500 hover:shadow-[0_0_30px_-5px_rgba(168,85,247,0.3)]">
        <div class="absolute inset-0 bg-gray-900/90 backdrop-blur-xl rounded-2xl"></div>
        <div class="relative p-6 flex items-center justify-between h-full">
          <div>
            <p class="text-purple-400/80 text-xs font-bold uppercase tracking-wider mb-1">Categorias</p>
            <h3 class="text-4xl font-black text-purple-100 drop-shadow-[0_0_8px_rgba(168,85,247,0.5)]">{{ libraryStats.total_groups }}</h3>
          </div>
          <div class="w-14 h-14 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.15)] group-hover:scale-110 transition-transform duration-300">
             <svg viewBox="0 0 24 24" fill="none" class="w-8 h-8 text-purple-400">
               <path d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
             </svg>
          </div>
        </div>
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

    <!-- Command Center Panel for Adding Sources -->
    <div class="relative overflow-hidden rounded-2xl bg-gray-900 border border-cyan-500/20 shadow-[0_0_40px_-10px_rgba(6,182,212,0.1)]">
      <!-- Decorative Background Grid -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:32px_32px] opacity-20 pointer-events-none"></div>
      
      <div class="relative p-6 md:p-8">
        <div class="flex items-center gap-4 mb-8">
          <div class="w-12 h-12 rounded-xl bg-cyan-950/50 border border-cyan-500/30 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.2)]">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6 text-cyan-400">
              <path d="M12 4v16m8-8H4" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-black text-white tracking-tight">ADICIONAR FONTE</h2>
            <p class="text-cyan-400/60 text-sm font-medium tracking-wide">COMMAND CENTER // NOVO ENDPOINT</p>
          </div>
        </div>

        <!-- Error Alert with Glitch Effect -->
        <div v-if="addError" class="mb-6 bg-red-500/10 border-l-4 border-red-500 p-4 rounded-r-lg relative overflow-hidden group">
          <div class="flex items-start gap-3 relative z-10">
            <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <div>
              <h4 class="text-red-400 font-bold text-sm">ERRO DE EXECUÇÃO</h4>
              <p class="text-red-300/80 text-sm">{{ addError }}</p>
            </div>
          </div>
        </div>

        <form @submit.prevent="handleAddSource" class="space-y-6" :class="{ 'opacity-50 pointer-events-none': isAddingSource }">
          <!-- Main Input Field -->
          <div class="relative group">
            <div class="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
            <div class="relative bg-gray-900 rounded-xl p-1 flex items-center">
              <div class="pl-4 pr-2 text-cyan-500">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                </svg>
              </div>
              <input 
                v-model="newSourceUrl" 
                placeholder="https://exemplo.com/fontes/lista.json"
                type="url"
                class="w-full bg-transparent border-none text-white placeholder-gray-600 focus:ring-0 h-12 font-mono text-sm"
                :disabled="isAddingSource"
              />
            </div>
          </div>

          <div class="flex flex-col md:flex-row gap-4">
            <!-- Add Button -->
            <button 
              type="submit" 
              class="flex-1 h-14 relative overflow-hidden rounded-xl bg-cyan-600 group outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-gray-900 transition-all"
              :disabled="isAddingSource"
            >
              <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>
              <div class="relative flex items-center justify-center gap-3 text-white font-bold tracking-wider">
                <span v-if="isAddingSource" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span v-else>
                    <svg class="w-5 h-5 inline-block mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    INICIALIZAR FONTE
                </span>
              </div>
            </button>

            <!-- Json Toggle Button -->
            <button 
              @click="showJsonPaste = !showJsonPaste" 
              type="button"
              class="px-8 h-14 rounded-xl border border-gray-700 bg-gray-800/50 text-gray-300 font-bold hover:bg-gray-800 hover:border-gray-500 hover:text-white transition-all flex items-center justify-center gap-2"
              :disabled="isAddingSource"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
              </svg>
              {{ showJsonPaste ? 'FECHAR EDITOR' : 'EDITOR RAW' }}
            </button>
          </div>
          
          <!-- JSON Editor Panel -->
          <div v-show="showJsonPaste" class="mt-4 overflow-hidden transition-all duration-300">
            <div class="rounded-xl border border-purple-500/30 bg-gray-900 relative">
               <div class="absolute top-0 left-0 right-0 h-8 bg-gray-800/80 border-b border-gray-700/50 flex items-center px-4 gap-2">
                 <div class="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                 <div class="w-3 h-3 rounded-full bg-amber-500/20 border border-amber-500/50"></div>
                 <div class="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                 <span class="ml-2 text-xs text-gray-500 font-mono">json_payload.json</span>
               </div>
               <textarea 
                  v-model="jsonPasteContent"
                  placeholder='// Cole seu JSON aqui...'
                  class="w-full h-48 bg-gray-900/50 p-4 pt-12 text-gray-300 font-mono text-xs resize-none outline-none border-none focus:ring-0"
                  :disabled="isAddingSource"
                />
               <div class="p-3 border-t border-gray-700/50 bg-gray-800/30 flex justify-end">
                  <button 
                    @click="handleAddRawJson" 
                    type="button"
                    class="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider shadow-lg shadow-purple-900/20 transition-all"
                    :disabled="isAddingSource"
                  >
                    Processar Payload
                  </button>
               </div>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Suas Fontes - DATA CHIPS GRID -->
    <div v-if="sources.length > 0" class="space-y-6">
      <div class="flex items-center gap-4">
          <div class="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-900 to-transparent"></div>
          <h2 class="text-xl font-bold text-cyan-400 tracking-wider uppercase">📡 Fontes de Dados Ativas</h2>
          <div class="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-900 to-transparent"></div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"> <!-- 4 cards per row -->
        <div
          v-for="source in sources"
          :key="source.id"
          class="group relative bg-gray-900 rounded-xl border border-gray-800 hover:border-cyan-500/50 transition-all duration-300 hover:shadow-[0_0_20px_-5px_rgba(6,182,212,0.15)] flex flex-col overflow-hidden"
        >
          <!-- Hover Glow Effect -->
          <div class="absolute -inset-px bg-gradient-to-b from-cyan-500/10 to-transparent opacity-0 group-hover:opacity-100 transition duration-500 pointer-events-none"></div>

          <!-- Card Header Area -->
          <div class="p-4 flex-1 relative z-10"> <!-- Compact Padding -->
            <!-- Top Row: Delete Menu (Now just the button to the right, or we can make title full width) -->
            <div class="flex justify-end mb-1">
               <button 
                @click.stop="deleteSource(source.id)"
                class="w-6 h-6 rounded flex items-center justify-center text-gray-500 hover:bg-red-500/20 hover:text-red-400 transition-colors"
                title="Deletar Fonte"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            <!-- Title with Inline Status -->
            <div class="flex items-center gap-2 mb-3">
              <h3 class="text-[26px] font-bold text-gray-100 truncate group-hover:text-cyan-300 transition-colors leading-tight">
                  {{ getSourceName(source.url) }}
              </h3>
              <span :class="[
                  'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border whitespace-nowrap',
                  source.url.includes('json-raw') 
                    ? 'bg-purple-900/30 text-purple-300 border-purple-500/30'
                    : 'bg-blue-900/30 text-blue-300 border-blue-500/30'
                ]">
                  {{ source.url.includes('json-raw') ? 'DADOS LOCAIS' : 'URL REMOTA' }}
              </span>
            </div>
            
            <!-- Metadata Grid (Compacted) -->
            <div class="grid grid-cols-2 gap-2">
               <div class="bg-gray-950/50 p-2 rounded border border-gray-800 group-hover:border-cyan-500/20 transition-colors">
                  <p class="text-[9px] text-gray-500 uppercase font-bold mb-0.5">Itens</p>
                  <p class="text-lg font-mono text-white leading-none">{{ getSourceItemCount(source.id) }}</p>
               </div>
               <div class="bg-gray-950/50 p-2 rounded border border-gray-800 group-hover:border-purple-500/20 transition-colors">
                  <p class="text-[9px] text-gray-500 uppercase font-bold mb-0.5">Status</p>
                  <div class="flex items-center gap-1.5 mt-0.5">
                     <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                     <span class="text-[10px] text-green-400 font-bold">ONLINE</span>
                  </div>
               </div>
            </div>
          </div>

          <!-- Footer Actions (Compacted) -->
          <div class="px-4 py-3 border-t border-gray-800 bg-gray-900/50 flex items-center justify-between relative z-10">
             <!-- SSL Toggle Custom (Green/Red) -->
             <div class="flex items-center gap-2">
               <div 
                  @click="downloadVerifySsl[source.id] = !(downloadVerifySsl[source.id] ?? true)" 
                  class="cursor-pointer flex items-center gap-2 group/ssl"
               >
                 <div class="w-8 h-4 rounded-full relative transition-colors duration-300" 
                      :class="(downloadVerifySsl[source.id] ?? true) ? 'bg-green-900/60' : 'bg-red-900/60'">
                    <div class="absolute top-0.5 left-0.5 w-3 h-3 rounded-full transition-all duration-300 shadow-sm"
                         :class="(downloadVerifySsl[source.id] ?? true) 
                           ? 'translate-x-[16px] bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)]' 
                           : 'bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.8)]'"></div>
                 </div>
                 <span class="text-[10px] font-bold text-gray-400 group-hover/ssl:text-cyan-400 transition-colors">Verificação SSL</span>
               </div>
             </div>

             <router-link to="/library" class="flex items-center gap-1 text-[10px] font-bold text-cyan-500 hover:text-cyan-300 transition-colors uppercase tracking-wide">
                ABRIR
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                </svg>
             </router-link>
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
