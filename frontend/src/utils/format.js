export function formatBytes(bytes) {
  // handle null/undefined
  if (bytes === null || bytes === undefined) return '—'

  // if it's a numeric string, try to parse
  if (typeof bytes === 'string') {
    // try to parse strings like '1.6 GB', '1600000000', '1,600,000,000'
    const s = bytes.trim()
    // match number with optional decimal and optional unit
    const m = s.match(/^([0-9]+(?:[.,][0-9]+)?)\s*(b|kb|mb|gb|tb)?$/i)
    if (m) {
      let num = parseFloat(m[1].replace(',', '.'))
      const unit = (m[2] || '').toLowerCase()
      const multipliers = { 'b': 1, 'kb': 1024, 'mb': 1024 ** 2, 'gb': 1024 ** 3, 'tb': 1024 ** 4 }
      const mult = multipliers[unit] || 1
      bytes = Math.round(num * mult)
    } else {
      // fallback: extract digits only (handles strings like '1600000000')
      const cleaned = s.replace(/[^0-9]/g, '')
      if (cleaned === '') return bytes || '—'
      bytes = parseInt(cleaned, 10)
    }
  }

  if (typeof bytes !== 'number' || !isFinite(bytes)) return '—'
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

export function formatSpeed(bytesPerSecond) {
  if (!bytesPerSecond) return '0 B/s'
  return formatBytes(bytesPerSecond) + '/s'
}

export function formatMbps(bytesPerSecond) {
  if (!bytesPerSecond) return '0 Mbps'
  const mbps = (bytesPerSecond * 8) / 1000000
  const value = mbps >= 100 ? mbps.toFixed(0) : mbps.toFixed(1)
  return value + ' Mbps'
}

export function formatTime(seconds) {
  if (!seconds || seconds <= 0) return '∞'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) return `${hours}h ${minutes}m`
  if (minutes > 0) return `${minutes}m ${secs}s`
  return `${secs}s`
}

export function calculateETA(downloaded, total, speed) {
  if (!speed || speed === 0) return null
  const remaining = total - downloaded
  return formatTime(remaining / speed)
}

export function calculateSpeedMultiplier(speed) {
  // Assume base speed of 1 MB/s for single connection
  // Taxa = speed / 1MB/s
  if (!speed || speed === 0) return '—'
  const speedMBs = speed / 1024 / 1024
  const multiplier = speedMBs / 1  // 1 MB/s is base
  return multiplier.toFixed(1) + 'x'
}

export function getStatusColor(status) {
  const colors = {
    queued: '#fbbf24',
    running: '#10b981',
    paused: '#8b5cf6',
    completed: '#34d399',
    failed: '#ef4444',
    canceled: '#6b7280'
  }
  return colors[status] || '#9ca3af'
}

export function getStatusLabel(status) {
  const labels = {
    queued: 'Fila',
    running: 'Baixando',
    paused: 'Pausado',
    completed: 'Concluído',
    failed: 'Erro',
    canceled: 'Cancelado'
  }
  return labels[status] || status
}

import { formatDistanceToNow, format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export function formatRelativeDate(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    if (isNaN(date)) return ''

    // Custom compact formatter
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)

    if (diffInSeconds < 60) return 'Agora'

    const minutes = Math.floor(diffInSeconds / 60)
    if (minutes < 60) return `${minutes}m`

    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h`

    const days = Math.floor(hours / 24)
    if (days < 7) return `${days}d`

    const weeks = Math.floor(days / 7)
    // Fix: Show weeks up to 29 days to avoid "0 months"
    if (days < 30) return `${weeks} sem`

    const months = Math.floor(days / 30)
    // Fix: Proper portuguese pluralization
    if (months < 12) return `${months} ${months > 1 ? 'meses' : 'mês'}`

    const years = Math.floor(days / 365)
    return `${years} ${years > 1 ? 'anos' : 'ano'}`
  } catch (e) {
    return ''
  }
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    if (isNaN(date)) return ''
    return format(date, 'dd/MM/yyyy HH:mm', { locale: ptBR })
  } catch (e) {
    return ''
  }
}

/**
 * Traduz gêneros da Steam para Português Brasileiro.
 * Centraliza o mapeamento para evitar duplicidade.
 */
export function translateGenre(genre) {
  if (!genre) return 'Geral'

  const mapping = {
    'Action': 'Ação',
    'Adventure': 'Aventura',
    'Casual': 'Casual',
    'Indie': 'Indie',
    'Massively Multiplayer': 'MMO / Multijogador',
    'Racing': 'Corrida',
    'RPG': 'RPG',
    'Simulation': 'Simulação',
    'Sports': 'Esportes',
    'Strategy': 'Estratégia',
    'Violent': 'Violento',
    'Gore': 'Gore',
    'Sexual Content': 'Conteúdo Sexual',
    'Nudity': 'Nudez',
    'Early Access': 'Acesso Antecipado',
    'Free to Play': 'Gratuito para Jogar',
    'Short': 'Curto',
    'Design & Illustration': 'Design e Ilustração',
    'Education': 'Educação',
    'Software Training': 'Treinamento de Software',
    'Utilities': 'Utilitários',
    'Video Production': 'Produção de Vídeo',
    'Web Publishing': 'Publicação Web',
    'Game Development': 'Desenvolvimento de Jogos',
    'Audio Production': 'Produção de Áudio',
    'Photo Editing': 'Edição de Fotos',
    'Accounting': 'Contabilidade',
    'Animation & Modeling': 'Animação e Modelagem',
    'Action-Adventure': 'Ação e Aventura',
    'Classic': 'Clássico',
    'Tactical': 'Tático',
    'Survival': 'Sobrevivência',
    'Open World': 'Mundo Aberto',
    'Sandbox': 'Sandbox',
    'Shooter': 'Tiro',
    'Platformer': 'Plataforma',
    'Puzzle': 'Quebra-cabeça',
    'Stealth': 'Furtividade',
    'Horror': 'Terror',
    'Psychological Horror': 'Terror Psicológico',
    'Story Rich': 'Rico em História',
    'Multiplayer': 'Multijogador',
    'Singleplayer': 'Um Jogador',
    'Co-op': 'Cooperativo',
    'Space': 'Espaço',
    'Driving': 'Direção',
    'Fighting': 'Luta',
    'Anime': 'Anime',
    'Metroidvania': 'Metroidvania',
    'Soulslike': 'Soulslike',
    'Cute': 'Fofo',
    'Cyberpunk': 'Cyberpunk',
    'Sci-fi': 'Ficção Científica',
    'Fantasy': 'Fantasia',
    'Zombies': 'Zumbis',
    'Aliens': 'Aliens',
    'Atmospheric': 'Atmosférico',
    'Detective': 'Detetive',
    'Gothic': 'Gótico',
    'Medieval': 'Medieval',
    'Minimalist': 'Minimalista',
    'Mystery': 'Mistério',
    'Relaxing': 'Relaxante',
    'Turn-Based': 'Em Turnos',
    'Rogue-like': 'Rogue-like',
    'Rogue-lite': 'Rogue-lite',
    'Bullet Hell': 'Bullet Hell',
    'Custom Games': 'Jogos Customizados'
  }

  // Se o gênero estiver no mapeamento, retorna a tradução
  if (mapping[genre]) return mapping[genre]

  // Se não estiver, tenta uma tradução parcial ou retorna o original capitalizado
  return genre
}
