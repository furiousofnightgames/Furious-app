import axios from 'axios'

// Detectar ambiente (Electron vs Navegador)
const isElectron = window.electronAPI !== undefined
console.log('[API] Ambiente detectado:', isElectron ? 'Electron' : 'Navegador')

// Detectar porta dinamicamente
let baseURL = window.location.origin

// Debug: Log da detecção
console.log('[API] Detecção de baseURL:', {
  isElectron,
  hostname: window.location.hostname,
  port: window.location.port,
  protocol: window.location.protocol,
  origin: window.location.origin,
  href: window.location.href
})

// Se estiver no Electron ou origin estiver vazio, usar fallback
if (isElectron || !baseURL || baseURL === 'null' || baseURL === '') {
  baseURL = 'http://127.0.0.1:8001' // Changed from 8000 to match backend
  console.log('[API] Usando fallback para backend:', baseURL)
} else {
  console.log('[API] Usando baseURL do origin:', baseURL)
}

const api = axios.create({
  baseURL: baseURL,
  timeout: 60000,  // 1 minutes - Increased from 30s for large library loads
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  response => response,
  error => {
    // Extrair mensagem de erro adequadamente
    const errorData = error.response?.data || {}
    let errorMessage = error.message

    if (errorData.detail) {
      errorMessage = errorData.detail
    } else if (errorData.error) {
      errorMessage = errorData.error
    } else if (errorData.message) {
      errorMessage = errorData.message
    } else if (error.response?.statusText) {
      errorMessage = error.response.statusText
    }

    // Log para debugging
    console.error('[API Error]', error.response?.status, errorMessage)

    // Rejeitar com informação estruturada
    const err = new Error(errorMessage)
    err.response = error.response
    err.status = error.response?.status
    throw err
  }
)

export default api
