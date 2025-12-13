<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/50">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
        <h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-400">Download Direto</h1>
      </div>
      <p class="text-gray-400 ml-1">Insira uma URL para baixar arquivos diretamente</p>
    </div>

    <!-- Form Card -->
    <Card class="bg-gradient-to-br from-gray-900/50 to-gray-900/20 border border-cyan-500/20 hover:border-cyan-500/40 transition-all">
      <form @submit.prevent="handleDownload" class="space-y-5">
        <!-- URL Input -->
        <div>
          <label class="block text-sm font-bold text-cyan-300 mb-3 flex items-center gap-2">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.658 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            URL do Download
          </label>
          <Input 
            v-model="downloadForm.url"
            placeholder="https://exemplo.com/arquivo.zip"
            type="url"
            class="bg-gray-900/70 border-cyan-500/30 focus:border-cyan-500/70"
            required
          />
        </div>

        <!-- Name Input -->
        <div>
          <label class="block text-sm font-bold text-cyan-300 mb-3 flex items-center gap-2">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Nome do Arquivo
          </label>
          <Input 
            v-model="downloadForm.name"
            placeholder="Deixe em branco para auto-detectar"
            class="bg-gray-900/70 border-cyan-500/30 focus:border-cyan-500/70"
          />
        </div>

        <!-- Destination -->
        <div>
          <label class="block text-sm font-bold text-cyan-300 mb-3 flex items-center gap-2">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            Pasta de Destino
          </label>
          <div class="flex gap-2">
            <div class="flex-1 p-3 bg-gray-900/70 border border-cyan-500/20 rounded-lg hover:border-cyan-500/40 transition-all">
              <p class="text-sm text-cyan-300 truncate font-mono">
                {{ downloadForm.destination || 'downloads' }}
              </p>
            </div>
            <Button type="button" @click="browseFolder" variant="outline" size="md" :disabled="browseLoading" class="flex items-center gap-1 whitespace-nowrap btn-translucent">
              <svg v-if="!browseLoading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Procurar</span>
            </Button>
          </div>
        </div>

        <!-- Settings -->
        <div class="p-4 bg-gradient-to-r from-cyan-900/20 to-blue-900/20 rounded-lg border border-cyan-500/20 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm font-bold text-cyan-300 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Configurações
            </span>
          </div>
          <Toggle v-model="downloadForm.verify_ssl">
            <span class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Certificado SSL
            </span>
          </Toggle>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 pt-4 border-t border-cyan-500/20">
          <Button type="submit" variant="primary" size="md" class="flex-1" :disabled="downloadStore.loading">
            <span v-if="downloadStore.loading" class="flex items-center gap-2 justify-center">
              <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Aguarde...
            </span>
            <span v-else class="flex items-center gap-2 justify-center">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Iniciar Download
            </span>
          </Button>
          <router-link to="/sources" class="flex-1">
            <Button type="button" variant="outline" size="md" class="w-full flex items-center justify-center gap-1 btn-translucent">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Escolher de Fonte</span>
            </Button>
          </router-link>
        </div>
      </form>
    </Card>

    <!-- Info Card -->
    <Card class="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 hover:border-cyan-500/50 transition-all">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h3 class="font-bold text-cyan-300 mb-1">Dica</h3>
          <p class="text-sm text-gray-400">Use a aba <span class="text-cyan-300 font-semibold">"Fontes JSON"</span> para carregar uma fonte e escolher itens para baixar. Esta aba é para downloads diretos de URLs.</p>
        </div>
      </div>
    </Card>

    <!-- Manual folder input modal -->
    <Modal v-if="showManualFolderModal" @close="showManualFolderModal = false" title="Escolher pasta manualmente" :showDefaultButtons="false">
      <div class="space-y-4">
        <p class="text-sm text-gray-400 flex items-start gap-2">
          <svg class="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <span>Digite o caminho completo da pasta onde deseja salvar o arquivo:</span>
        </p>
        <Input 
          v-model="manualFolderPath" 
          placeholder="C:\\Users\\seu-usuario\\Downloads"
          class="bg-gray-900/70 border-cyan-500/30 focus:border-cyan-500/70 font-mono text-sm"
        />
        <div class="flex gap-2 pt-2">
          <Button 
            type="button" 
            @click="showManualFolderModal = false" 
            variant="outline"
            size="md"
            class="flex-1"
          >
            Cancelar
          </Button>
          <Button 
            type="button" 
            @click="applyManualFolder" 
            variant="primary"
            size="md"
            class="flex-1"
          >
            Usar esta pasta
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDownloadStore } from '../stores/download'
import { useToastStore } from '../stores/toast'
import api from '../services/api'
import Card from '../components/Card.vue'
import Button from '../components/Button.vue'
import Input from '../components/Input.vue'
import Modal from '../components/Modal.vue'
import Toggle from '../components/Toggle.vue'

const router = useRouter()
const downloadStore = useDownloadStore()

const downloadForm = ref({
  url: '',
  name: '',
  destination: 'downloads',
  verify_ssl: true
})
const showManualFolderModal = ref(false)
const manualFolderPath = ref('')
const browseLoading = ref(false)

async function browseFolder() {
  // Try backend native picker first, then fallback to manual modal
  browseLoading.value = true
  try {
    if (window.electronAPI?.selectFolder) {
      const folder = await window.electronAPI.selectFolder()
      if (folder) downloadForm.value.destination = folder
      browseLoading.value = false
      return
    }
    const resp = await api.post('/api/dialog/select_folder')
    if (resp.data && resp.data.path) {
      downloadForm.value.destination = resp.data.path
      return
    }

    // canceled or no path -> open manual modal
    manualFolderPath.value = downloadForm.value.destination || ''
    showManualFolderModal.value = true
  } catch (e) {
    manualFolderPath.value = downloadForm.value.destination || ''
    showManualFolderModal.value = true
  } finally {
    browseLoading.value = false
  }
}

function applyManualFolder() {
  downloadForm.value.destination = manualFolderPath.value || downloadForm.value.destination
  showManualFolderModal.value = false
}

async function handleDownload() {
  if (!downloadForm.value.url) {
    try { const ts = useToastStore(); ts.push('Erro', 'Por favor, insira uma URL') } catch (e) {}
    return
  }

  try {
    // Parse URL para validação básica
    try {
      new URL(downloadForm.value.url)
    } catch (e) {
      throw new Error('URL inválida - use http:// ou https://')
    }

    const config = {
      url: downloadForm.value.url.trim(),
      name: downloadForm.value.name || downloadForm.value.url.split('/').pop(),
      destination: downloadForm.value.destination || 'downloads',
      verify_ssl: downloadForm.value.verify_ssl !== false
    }

    const result = await downloadStore.createJob(config)
    if (!result || !result.job_id) {
      throw new Error('Resposta inválida do servidor')
    }
    
    // Verifica se já há downloads rodando
    const hasRunning = downloadStore.jobs.some(j => j.status === 'running')
    const toastMsg = hasRunning ? `Download #${result.job_id} colocado na fila` : `Download #${result.job_id} iniciado`
    try { const ts = useToastStore(); ts.push('Download', toastMsg) } catch (e) {}
    router.push('/downloads')
  } catch (e) {
    const errMsg = e.response?.data?.detail || e.message || 'Erro ao criar job'
    try { const ts = useToastStore(); ts.push('Erro', errMsg) } catch (ee) { alert(`Erro: ${errMsg}`) }
  }
}
</script>
