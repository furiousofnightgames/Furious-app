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
    return formatDistanceToNow(date, { addSuffix: true, locale: ptBR })
  } catch (e) {
    return ''
  }
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    return format(new Date(dateStr), 'dd/MM/yyyy', { locale: ptBR })
  } catch (e) {
    return ''
  }
}
