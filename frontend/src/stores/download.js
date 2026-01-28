import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import { useToastStore } from './toast'

// Use window object for true global singleton that survives hot-reload
if (!window.__wsInstance) {
  window.__wsInstance = null
  window.__wsConnecting = false
}

export const useDownloadStore = defineStore('download', () => {
  const jobs = ref([])
  const sources = ref([])
  const items = ref([])
  const aria2Available = ref(false)
  const aria2Checked = ref(false)
  const loading = ref(false)
  const error = ref(null)
  const ws = ref(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  let reconnectTimeout = null
  let manuallyDisconnected = false

  // Cache de última velocidade conhecida por job para evitar piscagem
  const lastKnownSpeed = ref({})

  const activeDownloads = computed(() =>
    jobs.value.filter(j => ['running', 'queued', 'pending'].includes(j.status))
  )
  const completedDownloads = computed(() =>
    jobs.value.filter(j => ['completed', 'completed_cleaned'].includes(j.status))
  )
  const failedDownloads = computed(() =>
    jobs.value.filter(j => j.status === 'failed')
  )
  const canceledDownloads = computed(() =>
    jobs.value.filter(j => j.status === 'canceled')
  )

  const totalSpeed = computed(() =>
    activeDownloads.value.reduce((acc, j) => acc + (j.speed || 0), 0)
  )

  const totalProgress = computed(() => {
    if (activeDownloads.value.length === 0) return 0
    const total = activeDownloads.value.reduce((acc, j) => acc + (j.progress || 0), 0)
    return Math.round(total / activeDownloads.value.length)
  })

  // Helper to format progress to 1 decimal place
  function formatProgress(p) {
    if (p === null || p === undefined) return 0
    return Math.round(p * 10) / 10
  }

  // Actions
  async function fetchJobs() {
    try {
      loading.value = true
      const response = await api.get('/api/jobs')
      jobs.value = response.data
      error.value = null
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function cleanupJob(jobId) {
    try {
      const response = await api.post(`/api/jobs/${jobId}/cleanup`)
      toastSuccess('Limpeza', 'Arquivos do instalador removidos, histórico preservado')
      // Atualizar lista local
      const job = jobs.value.find(j => j.id === jobId)
      if (job) job.status = 'completed_cleaned'
      return response.data
    } catch (e) {
      const msg = e.response?.data?.detail || e.message
      toastError('Erro na limpeza', msg)
      throw e
    }
  }

  // generic helper to call backend endpoints that return JSON
  async function fetchApi(path, method = 'get', data = null) {
    try {
      const resp = method.toLowerCase() === 'post' ? await api.post(path, data) : await api.get(path)
      return resp.data
    } catch (e) {
      // Normalize error to include backend message when available
      try {
        if (e.response && e.response.data) {
          const detail = e.response.data.detail || e.response.data.error || e.response.data.message || JSON.stringify(e.response.data)
          throw new Error(detail)
        }
      } catch (_err) { }
      throw e
    }
  }

  // convenience helpers to show toasts
  function toastSuccess(title, message) {
    try {
      const ts = useToastStore()
      ts.push(title, message)
    } catch (e) { }
  }

  function toastError(title, message) {
    try {
      const ts = useToastStore()
      ts.push(title, message)
    } catch (e) { }
  }

  async function fetchSources() {
    try {
      console.log(`📚 [Store] fetchSources() - Buscando lista de fontes`)
      const response = await api.get('/api/sources')
      sources.value = response.data
      console.log(`✓ [Store] Fontes carregadas: ${sources.value.length}`)
      sources.value.forEach(s => console.log(`  • Fonte #${s.id}: ${s.url}`))
      // Check aria2 availability once when fetching sources
      if (!aria2Checked.value) {
        checkAria2Status().catch(() => { })
      }
    } catch (e) {
      console.error(`❌ [Store] Erro ao buscar fontes:`, e.message)
      error.value = e.message
    }
  }

  async function checkAria2Status() {
    try {
      aria2Checked.value = true
      const resp = await api.get('/api/aria2/status')
      aria2Available.value = !!resp.data && !!resp.data.available
      console.log('[Store] aria2 availability:', aria2Available.value, resp.data)
      return aria2Available.value
    } catch (e) {
      console.warn('[Store] aria2 status check failed:', e.message)
      aria2Available.value = false
      return false
    }
  }

  async function fetchSourceItems(sourceId) {
    try {
      console.log(`📦 [Store] fetchSourceItems(${sourceId}) - Buscando items`)
      const response = await api.get(`/api/sources/${sourceId}/items`)
      console.log(`✓ [Store] ${response.data.length} items recebidos da fonte #${sourceId}`)

      // Adicionar items da fonte, não substituir todos
      const existingIds = new Set(items.value.map(i => i.id))
      let adicionados = 0
      response.data.forEach(item => {
        if (!existingIds.has(item.id)) {
          items.value.push(item)
          adicionados++
        }
      })
      console.log(`✓ [Store] ${adicionados} items novos adicionados - Total: ${items.value.length}`)
    } catch (e) {
      console.error(`❌ [Store] Erro ao buscar items da fonte ${sourceId}:`, e.message)
      error.value = e.message
    }
  }

  async function fetchAllItems() {
    try {
      console.log(`🔄 [Store] fetchAllItems() - Carregando items de todas as fontes`)
      items.value = []
      for (const source of sources.value) {
        console.log(`  • Carregando items da fonte #${source.id}`)
        const response = await api.get(`/api/sources/${source.id}/items`)
        const count = response.data.length
        items.value.push(...response.data)
        console.log(`    ✓ ${count} items carregados`)
      }
      console.log(`✅ Total de items carregados: ${items.value.length}`)
    } catch (e) {
      console.error(`❌ [Store] Erro ao buscar items:`, e.message)
      error.value = e.message
    }
  }

  async function createJob(config) {
    try {
      loading.value = true

      // Log para debug
      console.log('[createJob] Config recebido:', config)

      // Validação básica
      if (!config.url || typeof config.url !== 'string') {
        error.value = 'URL inválida'
        throw new Error('URL_INVALID')
      }
      const urlStr = config.url.trim()

      // Allow http(s) URLs or magnet links (when aria2 is available)
      if (urlStr.startsWith('magnet:')) {
        if (!aria2Available.value) {
          error.value = 'aria2 não está disponível no servidor para magnet links'
          throw new Error('ARIA2_NOT_AVAILABLE')
        }
      } else if (!urlStr.startsWith('http')) {
        error.value = 'URL inválida'
        throw new Error('URL_INVALID_FORMAT')
      }

      if (!config.destination || typeof config.destination !== 'string') {
        console.error('[createJob] destination inválido ou ausente:', config.destination)
        error.value = 'Destino inválido'
        throw new Error('DESTINATION_INVALID')
      }

      // Adicionar defaults para k e n_conns se não estiverem especificados
      const finalConfig = {
        ...config,
        k: config.k || 4,           // Default: 4 partes
        n_conns: config.n_conns || 8  // Default: 8 workers para velocidade otimizada
      }

      console.log('[createJob] Enviando para API:', { url: finalConfig.url, name: finalConfig.name, destination: finalConfig.destination, k: finalConfig.k, n_conns: finalConfig.n_conns })
      const response = await api.post('/api/jobs', finalConfig)

      // Não bloquear a UI em fetchJobs(): em alguns cenários (SQLite lock / reload / worker atualizando DB)
      // isso pode demorar e deixar modal preso em loading.
      try {
        Promise.race([
          fetchJobs(),
          new Promise((resolve) => setTimeout(resolve, 1500))
        ]).catch(() => { })
      } catch (e) { }

      toastSuccess('Sucesso', `${finalConfig.name || 'Download'} iniciado`)
      return response.data
    } catch (e) {
      error.value = e.message
      console.error('[createJob] Erro:', e)

      // Mapear erros para mensagens amigáveis
      let errorMsg = e.message
      if (e.message === 'URL_INVALID') errorMsg = 'Insira uma URL válida'
      else if (e.message === 'URL_INVALID_FORMAT') errorMsg = 'URL deve começar com http(s)'
      else if (e.message === 'ARIA2_NOT_AVAILABLE') errorMsg = 'aria2 não disponível. Instale aria2 ou configure ARIA2C_PATH.'
      else if (e.message === 'DESTINATION_INVALID') errorMsg = 'Selecione uma pasta de destino válida'

      toastError('Erro ao criar download', errorMsg)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function pauseJob(jobId) {
    try {
      await api.post(`/api/jobs/${jobId}/pause`)
      await fetchJobs()
    } catch (e) {
      error.value = e.message
      toastError('Erro', e.message)
      throw e
    }
  }

  async function resumeJob(jobId) {
    try {
      await api.post(`/api/jobs/${jobId}/resume`)
      await fetchJobs()
    } catch (e) {
      error.value = e.message
      toastError('Erro', e.message)
      throw e
    }
  }

  async function cancelJob(jobId) {
    try {
      await api.post(`/api/jobs/${jobId}/cancel`)
      await fetchJobs()
      toastSuccess('Cancelado', 'Download removido')
    } catch (e) {
      error.value = e.message
      toastError('Erro', e.message)
      throw e
    }
  }

  async function retryJob(jobId) {
    try {
      loading.value = true
      console.log(`[retryJob] Retentando job #${jobId}`)

      // Get current job details
      const jobResponse = await api.get(`/api/jobs/${jobId}`)
      const job = jobResponse.data

      if (!job) {
        throw new Error('Job não encontrado')
      }

      console.log(`[retryJob] Status atual: ${job.status}`)

      // Se o job é paused ou failed e NÃO é erro de certificado, tentar usar resume.
      // Para erros de certificado, criar novo job com verify_ssl=false diretamente.
      const lastErr = (job.last_error || job.error || '').toLowerCase()
      const isCertError = lastErr.includes('certificate verify failed') || lastErr.includes('ssl')

      if (['paused', 'failed'].includes(job.status) && !isCertError) {
        console.log(`[retryJob] Usando resume para job em status ${job.status}`)
        try {
          await api.post(`/api/jobs/${jobId}/resume`)
          await fetchJobs()
          return { ok: true }
        } catch (resumeError) {
          console.warn(`[retryJob] Resume falhou:`, resumeError.message)
          // Se resume falhar, criar novo job
        }
      }

      // Se é canceled, sempre criar novo job (não pode resumir de cancelado)
      if (job.status === 'canceled') {
        console.log(`[retryJob] Job cancelado - criando novo job`)
      }

      // Criar novo job com os dados originais
      const retryConfig = {
        url: job.item_url || job.url,
        name: job.item_name || job.name,
        destination: job.dest || 'downloads',
        // Se detectamos erro de certificado, forçar verify_ssl=false
        verify_ssl: isCertError ? false : (job.verify_ssl !== false),
        size: job.total || null
      }

      console.log(`[retryJob] Criando novo job com config:`, retryConfig)
      const result = await createJob(retryConfig)

      // Deletar o job anterior cancelado/falho
      try {
        await api.delete(`/api/jobs/${jobId}`)
      } catch (ee) {
        console.warn(`[retryJob] Warning ao deletar job anterior:`, ee.message)
      }

      await fetchJobs()
      return result
    } catch (e) {
      error.value = e.message
      console.error(`[retryJob] Erro:`, e)
      toastError('Erro ao retentar', e.message)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function getJobDetails(jobId) {
    try {
      const response = await api.get(`/api/jobs/${jobId}`)
      return response.data
    } catch (e) {
      error.value = e.message
      toastError('Erro ao carregar detalhes', e.message)
      throw e
    }
  }

  async function deleteJobFile(jobId) {
    try {
      console.log(`[Store] deleteJobFile(${jobId}) - Iniciando`)
      const response = await api.delete(`/api/jobs/${jobId}`)
      console.log(`[Store] deleteJobFile(${jobId}) - Resposta:`, response.data)

      // Limpar cache de velocidade do job deletado
      delete lastKnownSpeed.value[jobId]

      await fetchJobs()
      return response.data
    } catch (e) {
      error.value = e.message
      console.error(`[Store] deleteJobFile(${jobId}) - Erro:`, e)
      toastError('Erro ao deletar arquivo', e.message)
      throw e
    }
  }

  async function clearCompletedJobs() {
    try {
      console.log('[Store] clearCompletedJobs - Iniciando...')
      // Coletar apenas IDs visíveis na tela (todos os que estão em jobs.value)
      const visibleCompletedIds = jobs.value.filter(j => j.status === 'completed').map(j => j.id)
      console.log('[Store] clearCompletedJobs - IDs visíveis a deletar:', visibleCompletedIds)

      const response = await api.delete('/api/jobs/completed/clear', {
        data: { job_ids: visibleCompletedIds }
      })
      console.log('[Store] clearCompletedJobs - Resposta:', response.data)

      // Remove completed jobs from memory immediately
      jobs.value = jobs.value.filter(j => j.status !== 'completed')

      // Limpar cache de velocidade dos jobs removidos
      visibleCompletedIds.forEach(id => delete lastKnownSpeed.value[id])

      console.log('[Store] clearCompletedJobs - Jobs após filtro:', jobs.value.length)

      // Fetch fresh data from backend
      await fetchJobs()
      toastSuccess('Limpeza', 'Concluídos removidos')
    } catch (e) {
      error.value = e.message
      toastError('Erro ao limpar concluídos', e.message)
      throw e
    }
  }

  async function clearFailedJobs() {
    try {
      console.log('[Store] clearFailedJobs - Iniciando...')
      // Coletar apenas IDs visíveis na tela (todos os que estão em jobs.value)
      const visibleFailedIds = jobs.value.filter(j => j.status === 'failed').map(j => j.id)
      console.log('[Store] clearFailedJobs - IDs visíveis a deletar:', visibleFailedIds)

      const response = await api.delete('/api/jobs/failed/clear', {
        data: { job_ids: visibleFailedIds }
      })
      console.log('[Store] clearFailedJobs - Resposta:', response.data)

      // Remove failed jobs from memory immediately
      jobs.value = jobs.value.filter(j => j.status !== 'failed')

      // Limpar cache de velocidade dos jobs removidos
      visibleFailedIds.forEach(id => delete lastKnownSpeed.value[id])

      console.log('[Store] clearFailedJobs - Jobs após filtro:', jobs.value.length)

      // Fetch fresh data from backend
      await fetchJobs()
      toastSuccess('Limpeza', 'Com erros removidos')
      return response.data
    } catch (e) {
      error.value = e.message
      console.error('[Store] clearFailedJobs - Erro:', e)
      toastError('Erro ao limpar erros', e.message)
      throw e
    }
  }

  async function clearCanceledJobs() {
    try {
      console.log('[Store] clearCanceledJobs - Iniciando...')
      // Coletar apenas IDs visíveis na tela (todos os que estão em jobs.value)
      const visibleCanceledIds = jobs.value.filter(j => j.status === 'canceled').map(j => j.id)
      console.log('[Store] clearCanceledJobs - IDs visíveis a deletar:', visibleCanceledIds)

      const response = await api.delete('/api/jobs/canceled/clear', {
        data: { job_ids: visibleCanceledIds }
      })
      console.log('[Store] clearCanceledJobs - Resposta:', response.data)

      // Remove canceled jobs from memory immediately
      jobs.value = jobs.value.filter(j => j.status !== 'canceled')

      // Limpar cache de velocidade dos jobs removidos
      visibleCanceledIds.forEach(id => delete lastKnownSpeed.value[id])

      console.log('[Store] clearCanceledJobs - Jobs após filtro:', jobs.value.length)

      // Fetch fresh data from backend
      await fetchJobs()
      toastSuccess('Limpeza', 'Cancelados removidos')
      return response.data
    } catch (e) {
      error.value = e.message
      console.error('[Store] clearCanceledJobs - Erro:', e)
      toastError('Erro ao limpar cancelados', e.message)
      throw e
    }
  }

  async function loadJsonFromUrl(url) {
    try {
      console.log(`\n🌐 [Store] loadJsonFromUrl() - URL: ${url}`)

      // Validar URL
      const urlObj = new URL(url)
      if (!urlObj.protocol.startsWith('http')) throw new Error('URL inválida')
      console.log(`✓ URL válida`)

      // Salvar a fonte diretamente no backend
      console.log(`💾 [Store] Salvando fonte no backend...`)
      loading.value = true
      const response = await api.post('/api/load-json', { url })
      console.log(`✓ Fonte criada - ID: ${response.data.source_id}`)

      // Verificar se é duplicata
      if (response.data.duplicate) {
        console.log(`⚠️ [Store] Fonte duplicada detectada!`)
        await fetchSources()
        // Não chamar fetchSourceItems para duplicata, pois já existe
        console.log(`⚠️ Usando fonte já existente`)
        return response.data
      }

      await fetchSources()
      await fetchSourceItems(response.data.source_id)
      console.log(`✅ Fonte adicionada com sucesso`)
      return response.data
    } catch (e) {
      console.error(`❌ [Store] loadJsonFromUrl erro:`, e.message)
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadJsonRaw(data) {
    try {
      console.log(`\n📋 [Store] loadJsonRaw() - Carregando JSON colado`)

      // Validar dados antes de salvar
      let itemsData = []

      if (Array.isArray(data)) {
        console.log(`✓ Formato detectado: array simples`)
        itemsData = data
      } else if (data && data.items && Array.isArray(data.items)) {
        console.log(`✓ Formato detectado: {items: [...]}`)
        itemsData = data.items
      } else if (data && data.downloads && Array.isArray(data.downloads)) {
        console.log(`✓ Formato detectado: {downloads: [...]} (Magnet links)`)
        itemsData = data.downloads.map(dl => ({
          name: dl.title || dl.name || 'Sem título',
          url: (dl.uris && dl.uris[0]) || dl.url || '',
          size: dl.fileSize || '?',
          category: data.name || 'Downloads'
        }))
      } else if (data && data.data && Array.isArray(data.data)) {
        console.log(`✓ Formato detectado: {data: [...]}`)
        itemsData = data.data
      } else if (data && data.results && Array.isArray(data.results)) {
        console.log(`✓ Formato detectado: {results: [...]}`)
        itemsData = data.results
      } else if (data && data.content && Array.isArray(data.content)) {
        console.log(`✓ Formato detectado: {content: [...]}`)
        itemsData = data.content
      } else if (typeof data === 'object' && data !== null) {
        // Tentar encontrar primeiro array no objeto
        for (const key in data) {
          if (Array.isArray(data[key])) {
            console.log(`✓ Formato detectado: {${key}: [...]}`)
            itemsData = data[key]
            break
          }
        }
      }

      if (itemsData.length === 0) {
        throw new Error('Nenhum array encontrado. Formatos aceitos: [], {items: []}, {downloads: []}, {data: []}, {results: []}, {content: []}')
      }

      console.log(`✓ JSON parsing - ${itemsData.length} items encontrados`)

      loading.value = true
      const response = await api.post('/api/load-json/raw', { data })
      console.log(`✓ Fonte criada - ID: ${response.data.source_id}`)

      // Verificar se é duplicata
      if (response.data.duplicate) {
        console.log(`⚠️ [Store] JSON duplicado detectado!`)
        await fetchSources()
        // Não chamar fetchSourceItems para duplicata, pois já existe
        console.log(`⚠️ Usando fonte já existente`)
        return response.data
      }

      await fetchSources()
      await fetchSourceItems(response.data.source_id)
      console.log(`✅ Fonte adicionada com sucesso`)
      return response.data
    } catch (e) {
      console.error(`❌ [Store] loadJsonRaw erro:`, e.message)
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteSource(sourceId) {
    try {
      console.log(`🗑️ [Store] deleteSource(${sourceId}) - Iniciando`)
      console.log(`📤 [Store] Enviando DELETE para /api/sources/${sourceId}`)
      const response = await api.delete(`/api/sources/${sourceId}`)
      console.log(`✓ [Store] Resposta recebida:`, response.data)

      console.log(`🔄 [Store] Atualizando lista de fontes`)
      await fetchSources()
      console.log(`✓ [Store] Fontes atualizadas - Total: ${sources.value.length}`)

      console.log(`✅ [Store] deleteSource(${sourceId}) concluído`)
    } catch (e) {
      console.error(`❌ [Store] Erro ao deletar fonte ${sourceId}:`, e.message)
      error.value = e.message
      throw e
    }
  }

  const reconnectAttempts = ref(0)
  const maxReconnectDelay = 30000 // 30 seconds

  function connectWebSocket(force = false) {
    // Forced reconnect: close any existing socket and start a new connection.
    if (force) {
      try {
        manuallyDisconnected = false
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout)
          reconnectTimeout = null
        }

        const existing = ws.value || window.__wsInstance
        if (existing && existing.readyState !== WebSocket.CLOSED) {
          try {
            // prevent old handlers from mutating state after we start a new socket
            existing.onopen = null
            existing.onmessage = null
            existing.onerror = null
            existing.onclose = null
          } catch (e) { }
          try { existing.close() } catch (e) { }
        }

        ws.value = null
        window.__wsInstance = null
        window.__wsConnecting = false
        isConnected.value = false
        isConnecting.value = false
      } catch (e) { }
    } else {
      // Prevent multiple simultaneous connection attempts
      if (isConnected.value || window.__wsConnecting) {
        console.log('[WebSocket] Already connected or connecting, skipping')
        return
      }

      // Reuse global singleton if available
      if (window.__wsInstance && window.__wsInstance.readyState === WebSocket.OPEN) {
        console.log('[WebSocket] Reusing existing global WebSocket instance')
        ws.value = window.__wsInstance
        isConnected.value = true
        reconnectAttempts.value = 0
        return
      }
    }

    window.__wsConnecting = true

    // In Electron, window.location.host doesn't work (file:// protocol)
    // Use the backend URL from api configuration instead
    let wsHost = window.location.host
    if (!wsHost || wsHost === '' || window.location.protocol === 'file:') {
      // Extract host from api.defaults.baseURL (e.g., 'http://127.0.0.1:8001' -> '127.0.0.1:8001')
      const baseURL = api.defaults.baseURL || 'http://127.0.0.1:8001'
      wsHost = baseURL.replace(/^https?:\/\//, '')
      console.log('[WebSocket] Using backend URL for WebSocket:', wsHost)
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${wsHost}/ws`

    console.log(`[WebSocket] Creating new connection to: ${wsUrl} (Attempt ${reconnectAttempts.value + 1})`)
    ws.value = new WebSocket(wsUrl)
    window.__wsInstance = ws.value

    ws.value.onopen = () => {
      isConnected.value = true
      window.__wsConnecting = false
      reconnectAttempts.value = 0 // Reset attempts on success
      console.log('[WebSocket] Connected')
    }

    ws.value.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        if (message.type === 'progress' && Array.isArray(message.jobs)) {
          message.jobs.forEach(update => {
            const job = jobs.value.find(j => j.id === update.id)
            if (job) {
              // Se velocidade vem como 0 ou undefined, usar última conhecida
              if ((update.speed === 0 || update.speed === null || update.speed === undefined) && lastKnownSpeed.value[update.id]) {
                // Manter última velocidade conhecida
                update.speed = lastKnownSpeed.value[update.id]
              } else if (update.speed > 0) {
                // Guardar nova velocidade conhecida
                lastKnownSpeed.value[update.id] = update.speed
              }

              // Atualizar apenas campos que mudaram
              Object.keys(update).forEach(key => {
                if (update[key] !== null && update[key] !== undefined) {
                  job[key] = update[key]
                }
              })
            }
          })
        }
      } catch (e) {
        console.error('[WebSocket] Error parsing message:', e)
      }
    }

    ws.value.onerror = (error) => {
      console.error('[WebSocket] Error:', error)
      isConnected.value = false
      window.__wsConnecting = false
    }

    ws.value.onclose = () => {
      isConnected.value = false
      window.__wsConnecting = false
      console.log('[WebSocket] Disconnected')

      // Only try to reconnect if not manually disconnected
      if (!manuallyDisconnected) {
        // Calculate delay with exponential backoff (1s, 2s, 4s, 8s, 16s, 30s max)
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), maxReconnectDelay)
        reconnectAttempts.value++

        console.log(`[WebSocket] Will attempt reconnection in ${delay}ms... (Attempt ${reconnectAttempts.value})`)

        // Clear any existing timeout
        if (reconnectTimeout) clearTimeout(reconnectTimeout)

        reconnectTimeout = setTimeout(() => {
          if (!isConnected.value && !manuallyDisconnected) {
            console.log('[WebSocket] Attempting reconnection...')
            connectWebSocket()
          }
        }, delay)
      }
    }
  }

  function disconnectWebSocket() {
    manuallyDisconnected = true
    reconnectAttempts.value = 0
    if (reconnectTimeout) clearTimeout(reconnectTimeout)
    if (ws.value) {
      ws.value.close()
      ws.value = null
      window.__wsInstance = null
      window.__wsConnecting = false
      isConnected.value = false
      isConnecting.value = false
    }
  }

  async function checkSetup(jobId) {
    try {
      const response = await api.get(`/api/jobs/${jobId}/setup-check`)
      return response.data
    } catch (e) {
      console.error(`[Store] checkSetup(${jobId}) - Erro:`, e)
      return { found: false, error: e.message }
    }
  }

  async function runSetup(jobId, setupPath) {
    try {
      const response = await api.post(`/api/jobs/${jobId}/setup-run`, { path: setupPath })
      toastSuccess('Instalação', 'Instalador iniciado com sucesso')
      return response.data
    } catch (e) {
      const msg = e.response?.data?.detail || e.message
      console.error(`[Store] runSetup(${jobId}) - Erro:`, msg)
      toastError('Erro ao iniciar instalador', msg)
      throw e
    }
  }

  async function getDiskSpace(path = '') {
    try {
      const response = await api.get('/api/system/disk-space', { params: { path } })
      return response.data
    } catch (e) {
      console.error('[Store] getDiskSpace erro:', e)
      return { free: 0, status: 'error' }
    }
  }

  async function markInstalled(jobId) {
    try {
      await api.post(`/api/jobs/${jobId}/mark-installed`)
      toastSuccess('Instalação', 'Item marcado como instalado manualmente')
      const job = jobs.value.find(j => j.id === jobId)
      if (job) job.setup_executed = true
    } catch (e) {
      toastError('Erro', e.message)
      throw e
    }
  }

  async function cleanupJob(jobId) {
    try {
      console.log(`[Store] cleanupJob(${jobId}) - Iniciando limpeza...`)
      const response = await api.post(`/api/jobs/${jobId}/cleanup`)

      if (response.data && response.data.status === 'success') {
        console.log(`[Store] Limpeza confirmada. Removendo job ${jobId} da lista local.`)
        // Remover job da lista local imediatamente para atualizar a UI
        jobs.value = jobs.value.filter(j => j.id !== jobId)
        toastSuccess('Limpeza', 'Arquivos removidos e download finalizado')
      }
      return response.data
    } catch (e) {
      console.error(`[Store] Erro ao limpar job ${jobId}:`, e)
      toastError('Erro na limpeza', e.message || 'Falha ao remover arquivos')
      throw e
    }
  }

  return {
    jobs,
    sources,
    items,
    loading,
    error,
    isConnected,
    activeDownloads,
    completedDownloads,
    failedDownloads,
    canceledDownloads,
    totalSpeed,
    totalProgress,
    fetchJobs,
    fetchSources,
    fetchSourceItems,
    fetchAllItems,
    createJob,
    pauseJob,
    resumeJob,
    cancelJob,
    retryJob,
    getJobDetails,
    deleteJobFile,
    clearCompletedJobs,
    clearFailedJobs,
    clearCanceledJobs,
    loadJsonFromUrl,
    loadJsonRaw,
    deleteSource,
    fetchApi,
    connectWebSocket,
    disconnectWebSocket,
    formatProgress,
    checkSetup,
    runSetup,
    markInstalled,
    getDiskSpace,
    cleanupJob
  }
})
