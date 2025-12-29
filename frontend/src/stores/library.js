import { defineStore } from 'pinia'
import api from '../services/api'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    groups: [],
    stats: {
      total_sources: 0,
      total_items: 0,
      built_at: null
    },
    page: 1,
    searchQuery: '',
    scrollPosition: 0,
    isLoaded: false,
    loading: false,
    error: null
  }),

  actions: {
    async fetchLibrary(refresh = false) {
      console.log(`[LibraryStore] fetchLibrary called. refresh=${refresh}, isLoaded=${this.isLoaded}, loading=${this.loading}, groups=${this.groups.length}`)

      if (this.isLoaded && !refresh) {
        console.log('[LibraryStore] Cache hit. Returning early.')
        return
      }

      console.log('[LibraryStore] Starting fetch...')
      this.loading = true
      this.error = null

      try {
        const resp = await api.get('/api/library' + (refresh ? '?refresh=true' : ''))
        const data = resp.data || {}

        this.groups = data.groups || []
        this.stats = {
          total_sources: data.total_sources || 0,
          total_items: data.total_items || 0,
          built_at: data.built_at || null
        }

        this.isLoaded = true
        console.log(`[LibraryStore] Fetch complete. Loaded ${this.groups.length} groups. isLoaded set to TRUE.`)
      } catch (e) {
        this.error = e.message || 'Erro ao carregar biblioteca'
        console.error('[LibraryStore] Error:', e)
      } finally {
        this.loading = false
      }
    },

    clearCache() {
      this.groups = []
      this.stats = { total_sources: 0, total_items: 0, built_at: null }
      this.page = 1
      this.searchQuery = ''
      this.scrollPosition = 0
      this.isLoaded = false
      this.error = null
    },

    setPage(p) {
      this.page = p
    },

    setSearchQuery(q) {
      this.searchQuery = q
      this.page = 1 // Reset page on new search
      this.scrollPosition = 0
    },

    setScrollPosition(pos) {
      this.scrollPosition = pos
    }
  }
})
