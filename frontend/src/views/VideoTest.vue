<template>
  <div class="min-h-screen bg-slate-950 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold text-white mb-6">🎬 Teste de Vídeos</h1>

      <!-- Info do Ambiente -->
      <div class="bg-slate-800 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-bold text-cyan-300 mb-4">Ambiente</h2>
        <div class="space-y-2 text-sm font-mono">
          <p>URL: <span class="text-green-400">{{ window.location.href }}</span></p>
          <p>UserAgent: <span class="text-green-400">{{ navigator.userAgent.substring(0, 80) }}</span></p>
          <p>isExe: <span :class="isExe ? 'text-red-400' : 'text-yellow-400'">{{ isExe }}</span></p>
        </div>
      </div>

      <!-- Teste 1: Vídeo Direto da Steam -->
      <div class="bg-slate-800 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-bold text-cyan-300 mb-4">Teste 1: Vídeo Direto (sem proxy)</h2>
        <p class="text-slate-300 mb-4 text-sm">URL: https://cdn.akamai.steamstatic.com/steam/apps/256704889/movie.mp4</p>
        <video
          class="w-full max-h-64 bg-black rounded mb-4"
          controls
          crossorigin="anonymous"
        >
          <source src="https://cdn.akamai.steamstatic.com/steam/apps/256704889/movie.mp4" type="video/mp4" />
          Seu navegador não suporta vídeo.
        </video>
        <p class="text-xs text-slate-400">Se o vídeo aparecer acima, o problema NÃO é a tag &lt;video&gt;</p>
      </div>

      <!-- Teste 2: Vídeo via Proxy -->
      <div class="bg-slate-800 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-bold text-cyan-300 mb-4">Teste 2: Vídeo via Proxy</h2>
        <p class="text-slate-300 mb-4 text-sm">URL: {{ proxyUrl }}</p>
        <button 
          @click="loadProxyVideo"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded mb-4"
        >
          Carregar Vídeo via Proxy
        </button>
        <video
          v-if="proxyVideoUrl"
          class="w-full max-h-64 bg-black rounded mb-4"
          controls
          crossorigin="anonymous"
        >
          <source :src="proxyVideoUrl" type="video/mp4" />
          Seu navegador não suporta vídeo.
        </video>
        <p v-else class="text-slate-400 text-sm">Clique no botão acima para carregar</p>
        <p class="text-xs text-slate-400 mt-2">Se o vídeo aparecer acima, o proxy está funcionando</p>
      </div>

      <!-- Teste 3: Vídeo da API -->
      <div class="bg-slate-800 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-bold text-cyan-300 mb-4">Teste 3: Vídeo da API (Dota 2)</h2>
        <button 
          @click="loadApiVideo"
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded mb-4"
        >
          Carregar Vídeo da API
        </button>
        <div v-if="apiVideo" class="bg-slate-900 p-4 rounded">
          <h3 class="text-white font-bold mb-3">{{ apiVideo.name }}</h3>
          <video
            class="w-full max-h-64 bg-black rounded mb-4"
            controls
            crossorigin="anonymous"
          >
            <source :src="apiVideo.mp4" type="video/mp4" />
            Seu navegador não suporta vídeo.
          </video>
          <div class="text-xs text-slate-400 space-y-1">
            <p><span class="text-slate-300">MP4:</span> {{ apiVideo.mp4?.substring(0, 100) }}...</p>
            <p><span class="text-slate-300">WebM:</span> {{ apiVideo.webm?.substring(0, 100) }}...</p>
          </div>
        </div>
        <p v-else class="text-slate-400 text-sm">Clique no botão acima para carregar</p>
      </div>

      <!-- Logs -->
      <div class="bg-slate-800 rounded-lg p-6">
        <h2 class="text-xl font-bold text-cyan-300 mb-4">Logs</h2>
        <div class="bg-slate-900 p-3 rounded text-xs text-slate-300 max-h-48 overflow-y-auto font-mono">
          <div v-for="(log, idx) in logs" :key="idx" class="mb-1">
            <span class="text-slate-500">[{{ log.time }}]</span>
            <span :class="log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-green-400' : 'text-slate-300'">
              {{ log.message }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const isExe = ref(false)
const proxyUrl = ref('')
const proxyVideoUrl = ref('')
const apiVideo = ref(null)
const logs = ref([])

const addLog = (message, type = 'info') => {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ time, message, type })
  if (logs.value.length > 50) logs.value.pop()
  console.log(`[${type.toUpperCase()}] ${message}`)
}

onMounted(() => {
  const ua = navigator.userAgent || ''
  isExe.value = ua.includes('PyQt') || ua.includes('QtWebEngine') || 
                (window.location.hostname === '127.0.0.1' && window.location.protocol === 'http:')
  
  addLog(`Ambiente: ${isExe.value ? '.exe (PyQt5)' : 'Navegador'}`)
  addLog(`Base URL: ${api.defaults.baseURL}`)
})

const loadProxyVideo = async () => {
  try {
    const videoUrl = 'https://cdn.akamai.steamstatic.com/steam/apps/256704889/movie.mp4'
    const baseUrl = api.defaults.baseURL || 'http://127.0.0.1:8001'
    proxyUrl.value = `${baseUrl}/api/proxy/video?url=${encodeURIComponent(videoUrl)}`
    
    addLog(`Testando proxy: ${proxyUrl.value.substring(0, 80)}...`)
    
    // Testar se o proxy responde
    const response = await fetch(proxyUrl.value, { method: 'HEAD' })
    if (response.ok) {
      addLog(`✓ Proxy respondeu com status ${response.status}`, 'success')
      proxyVideoUrl.value = proxyUrl.value
    } else {
      addLog(`✗ Proxy retornou ${response.status}`, 'error')
    }
  } catch (e) {
    addLog(`✗ Erro no proxy: ${e.message}`, 'error')
  }
}

const loadApiVideo = async () => {
  try {
    addLog('Carregando detalhes de Dota 2...')
    const res = await api.get('/api/game-details/570')
    
    if (res.data?.movies && res.data.movies.length > 0) {
      const video = res.data.movies[0]
      addLog(`✓ Vídeo carregado: ${video.name}`, 'success')
      
      // Aplicar proxy se necessário
      const baseUrl = api.defaults.baseURL || 'http://127.0.0.1:8001'
      const videoToUse = { ...video }
      
      if (videoToUse.mp4?.startsWith('http')) {
        videoToUse.mp4 = `${baseUrl}/api/proxy/video?url=${encodeURIComponent(videoToUse.mp4)}`
        addLog(`Aplicando proxy para MP4`)
      }
      
      apiVideo.value = videoToUse
    } else {
      addLog('✗ Nenhum vídeo encontrado', 'error')
    }
  } catch (e) {
    addLog(`✗ Erro: ${e.message}`, 'error')
  }
}
</script>
