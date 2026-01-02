import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useFavoritesStore = defineStore('favorites', () => {
  const items = ref([])
  const drawerOpen = ref(false)
  const loading = ref(false)
  const error = ref(null)

  function normalizeFavoriteName(name) {
    const raw = String(name || '').trim()
    if (!raw) return ''

    let s = raw.replace(/\s*[\(\[\{].*?[\)\]\}]\s*/g, ' ')
    s = s.replace(/\s+/g, ' ').trim()

    const seps = [' – ', ' — ', ' - ']
    for (const sep of seps) {
      const idx = s.indexOf(sep)
      if (idx > 0) {
        const head = s.slice(0, idx).trim()
        const tail = s.slice(idx + sep.length).trim()
        const tailLower = tail.toLowerCase()
        if (
          /^v?\d/.test(tailLower) ||
          tailLower.startsWith('v') ||
          tailLower.includes('dlc') ||
          tailLower.includes('bonus') ||
          tailLower.includes('repack') ||
          tailLower.includes('update') ||
          tailLower.includes('build') ||
          tailLower.includes('emulator') ||
          tail.includes('+')
        ) {
          s = head
          break
        }
      }
    }

    // Aggressive cleanup patterns
    s = s.replace(/\s*[\(\[].*?(dlc|update|repack|multi|build|v\d|patch|fix|hotfix|language|soundtrack|artbook|goat|goty|edition|remaster).*?[\)\]]/gi, '')
    s = s.replace(/\s+(v|ver|version)\.?\s*\d[\w.]*/gi, '')
    s = s.replace(/\s+build\s*\d+/gi, '')
    s = s.replace(/\s+update\s*\d*/gi, '')
    s = s.replace(/,\s*v\d.*/gi, '')
    s = s.replace(/\s+\+\s*.*$/i, '') // Remove anything after " + "

    // Hydra-style specific cleanups
    s = s.replace(/\s+goty$/i, '')
    s = s.replace(/\s+edition$/i, '')
    s = s.replace(/\s+deluxe(\s+edition)?$/i, '')
    s = s.replace(/\s+remastered$/i, '')

    return s.trim()
  }

  function openDrawer() {
    drawerOpen.value = true
  }

  function closeDrawer() {
    drawerOpen.value = false
  }

  function toggleDrawer() {
    drawerOpen.value = !drawerOpen.value
  }

  function isFavorited(sourceId, itemId) {
    return items.value.some(f => f.source_id === sourceId && f.item_id === itemId)
  }

  async function fetchFavorites() {
    try {
      loading.value = true
      const resp = await api.get('/api/favorites')
      items.value = Array.isArray(resp.data) ? resp.data : []
      error.value = null
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function addFavorite(payload) {
    const resp = await api.post('/api/favorites', payload)
    const fav = resp.data
    if (fav && fav.id) {
      const idx = items.value.findIndex(i => i.id === fav.id)
      if (idx === -1) {
        items.value.unshift(fav)
      } else {
        items.value.splice(idx, 1)
        items.value.unshift(fav)
      }
    } else {
      await fetchFavorites()
    }
  }

  async function removeFavoriteByItem(sourceId, itemId) {
    await api.delete('/api/favorites/by_item', { params: { source_id: sourceId, item_id: itemId } })
    items.value = items.value.filter(f => !(f.source_id === sourceId && f.item_id === itemId))
  }

  async function toggleFavoriteFromItem(item) {
    const sourceId = item?.source_id
    const itemId = item?.id

    if (sourceId == null || itemId == null) return

    if (isFavorited(sourceId, itemId)) {
      await removeFavoriteByItem(sourceId, itemId)
      return
    }

    await addFavorite({
      source_id: sourceId,
      item_id: itemId,
      name: normalizeFavoriteName(item?.name || ''),
      url: item?.url || '',
      image: item?.icon || item?.capsule || item?.image || item?.poster || ''
    })
  }

  return {
    items,
    drawerOpen,
    loading,
    error,
    openDrawer,
    closeDrawer,
    toggleDrawer,
    isFavorited,
    fetchFavorites,
    addFavorite,
    removeFavoriteByItem,
    toggleFavoriteFromItem,
    normalizeFavoriteName
  }
})
