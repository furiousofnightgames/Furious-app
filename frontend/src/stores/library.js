import { defineStore } from 'pinia'
import api from '../services/api'

const GENRE_PRIORITY = {
  "Ação": 1, "Action": 1, "Tiro": 1, "Shooter": 1, "FPS": 1,
  "Corrida": 2, "Racing": 2, "Esportes": 2, "Sports": 2,
  "Luta": 3, "Fighting": 3,
  "RPG": 5, "Estratégia": 6, "Strategy": 6,
  "Aventura": 7, "Adventure": 7,
  "Sobrevivência": 8, "Survival": 8,
  "Terror": 9, "Horror": 9, "Terror Psicológico": 9, "Psychological Horror": 9,
  "Simulação": 15, "Simulation": 15,
  "Plataforma": 16, "Platformer": 16,
  "Quebra-cabeça": 17, "Puzzle": 17,
  "Sandbox": 18, "Mundo Aberto": 19, "Open World": 19,
  "Indie": 100, "Casual": 105, "Multijogador": 110, "Multiplayer": 110, "Massively Multiplayer": 110,
  "Acesso Antecipado": 200, "Early Access": 200, "Gratuito para Jogar": 205, "Free to Play": 205,
  "Utilitários": 210, "Utilities": 210
};

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
    selectedGenres: [],
    selectedDevelopers: [],
    sortBy: 'upload', // 'recent' removed, defaulting to date
    scrollPosition: 0,
    isLoaded: false,
    loading: false,
    error: null,

    // Background Enrichment
    isEnriching: false,
    isCoolingDown: false,
    enrichmentQueue: [],
    _activeWorkers: 0,
    _maxConcurrency: 1,
    _lastRequestAt: 0, // Para escalonamento entre bots
    isTurbo: false
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

        // HYDRATION PASS: Pre-populate imageCache from DB items to avoid reactive delays
        // This ensures SteamGameCard finds the image in localStorage AT THE MOMENT of creation.
        try {
          const rawCache = localStorage.getItem('imageCache')
          const cache = rawCache ? JSON.parse(rawCache) : {}
          let changed = false

          this.groups.forEach(g => {
            const best = g.best || {}
            const img = best.image || best.header_image || best.thumbnail
            const appId = g.appId || best.appId || best.steam_appid

            if (img && img.startsWith('http')) {
              const key = appId ? `img_v2_app_${appId}` : `img_v2_${g.name}`
              if (!cache[key]) {
                cache[key] = img
                changed = true
              }
            }
          })

          if (changed) {
            localStorage.setItem('imageCache', JSON.stringify(cache))
            console.log('[LibraryStore] Eager Image Hydration complete.')
          }
        } catch (e) {
          console.warn('[LibraryStore] Hydration failed:', e)
        }

        // HYDRATION PASS: Pre-populate imageCache from DB items to avoid reactive delays
        // This ensures SteamGameCard finds the image in localStorage AT THE MOMENT of creation.
        try {
          const rawCache = localStorage.getItem('imageCache')
          const cache = rawCache ? JSON.parse(rawCache) : {}
          let changed = false

          this.groups.forEach(g => {
            const best = g.best || {}
            const img = best.image || best.header_image || best.thumbnail
            const appId = g.appId || best.appId || best.steam_appid

            if (img && img.startsWith('http')) {
              const key = appId ? `img_v2_app_${appId}` : `img_v2_${g.name}`
              if (!cache[key]) {
                cache[key] = img
                changed = true
              }
            }
          })

          if (changed) {
            localStorage.setItem('imageCache', JSON.stringify(cache))
            console.log('[LibraryStore] Eager Image Hydration complete.')
          }
        } catch (e) {
          console.warn('[LibraryStore] Hydration failed:', e)
        }
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
      this.selectedGenres = []
      this.selectedDevelopers = []
      this.sortBy = 'upload' // Changed from 'recent' to 'upload' as default
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

    setGenres(gList) {
      this.selectedGenres = Array.isArray(gList) ? gList : []
      this.page = 1
      this.scrollPosition = 0
    },

    setDevelopers(dList) {
      this.selectedDevelopers = Array.isArray(dList) ? dList : []
      this.page = 1
      this.scrollPosition = 0
    },

    setSortBy(s) {
      this.sortBy = s
      this.page = 1
      this.scrollPosition = 0
    },

    setScrollPosition(pos) {
      this.scrollPosition = pos
    },

    // =========================================================================
    // BACKGROUND ENRICHMENT: Silent Metadata/Image Scraper
    // =========================================================================

    async startBackgroundEnrichment(concurrency = null) {
      if (concurrency !== null) {
        this._maxConcurrency = concurrency
      } else {
        this._maxConcurrency = this.isTurbo ? 5 : 1
      }

      if (this.isEnriching) {
        return
      }
      if (!this.groups.length) return

      // Identify candidates: Not already resolved AND (No genres OR no images)
      const candidates = this.groups.filter(g => {
        if (g.metadata_resolved) return false
        const item = g.best || {}
        const hasGenres = Array.isArray(item.genres) && item.genres.length > 0
        const hasImage = !!(item.image || item.header_image || item.thumbnail)
        return !hasGenres || !hasImage
      })

      if (candidates.length === 0) {
        console.log('[Enricher] Library already fully enriched.')
        return
      }

      console.log(`[Enricher] Starting background sync for ${candidates.length} items. Concurrency: ${this._maxConcurrency}`)
      this.enrichmentQueue = candidates.map(c => ({ name: c.name, appId: c.appId }))
      this.isEnriching = true
      this._activeWorkers = 0

      // Start initial batch of workers
      for (let i = 0; i < this._maxConcurrency; i++) {
        this.enrichNextItem()
      }
    },

    async enrichNextItem() {
      if (!this.isEnriching || this.isCoolingDown || this.enrichmentQueue.length === 0) {
        if (this._activeWorkers <= 1 && !this.isCoolingDown) {
          this.isEnriching = false
          console.log('[Enricher] Sync complete.')
        }
        return
      }

      // Check if we already have too many workers
      if (this._activeWorkers >= this._maxConcurrency) return

      const next = this.enrichmentQueue.shift()
      if (!next) return

      // INTERLEAVING LOGIC: Garantir 600ms de distância de QUALQUER pedido anterior (vários bots)
      const now = Date.now()
      const timeSinceLast = now - this._lastRequestAt
      const minGap = 600 // 600ms para um Turbo extremo, conforme pedido do usuário

      if (timeSinceLast < minGap) {
        // Se o espaço é muito curto, devolve o item para a fila e espera o tempo restante + um jitter
        this.enrichmentQueue.unshift(next)
        const waitMore = (minGap - timeSinceLast) + Math.floor(Math.random() * 500)
        setTimeout(() => this.enrichNextItem(), waitMore)
        return
      }

      this._lastRequestAt = Date.now()
      this._activeWorkers++

      try {
        // Reuse the resolver which already persists metadata to GameMetadata
        const resp = await api.post(`/api/resolver?game_name=${encodeURIComponent(next.name)}`)
        const data = resp.data || {}

        if (data.found) {
          this.applyMetadata(next.name, data)
        } else if (data.rate_limited) {
          // INTERNACIONALIZADO: Detectar Rate Limit da Steam e pausar Bots
          console.warn(`🚨 [Enricher] STEAM RATE LIMIT detectado! Pausando bots por 90s.`)
          this.isCoolingDown = true

          // Devolver item para a fila para não perder o progresso
          this.enrichmentQueue.unshift(next)

          // Agendar retomada automática em 90s
          setTimeout(() => {
            console.log(`✅ [Enricher] Cooldown finalizado. Retomando bots...`)
            this.isCoolingDown = false
            if (this.isEnriching) {
              for (let i = 0; i < this._maxConcurrency; i++) {
                this.enrichNextItem()
              }
            }
          }, 93000) // 93s por segurança
          return
        }
      } catch (e) {
        // Silently fail and continue
      } finally {
        this._activeWorkers--
      }

      // Schedule next item
      // Turbo mode (concurrency > 1) uses shorter delays
      const isTurbo = this._maxConcurrency > 1
      const delay = isTurbo
        ? Math.floor(Math.random() * 500) + 500   // 0.5s - 1s in turbo
        : Math.floor(Math.random() * 2000) + 3000 // 3s - 5s in gentle mode

      setTimeout(() => {
        this.enrichNextItem()

        // If we are under-capacity (just started or turbo toggled), spin up more workers
        while (this.isEnriching && this._activeWorkers < this._maxConcurrency && this.enrichmentQueue.length > 0) {
          this.enrichNextItem()
        }
      }, delay)
    },

    removeFromQueue(name) {
      this.enrichmentQueue = this.enrichmentQueue.filter(q => q.name !== name)
    },

    applyMetadata(name, data) {
      const groupIdx = this.groups.findIndex(g => g.name === name)
      if (groupIdx !== -1) {
        const g = this.groups[groupIdx]
        if (g.best) {
          // Force reactivity by creating a fresh object structure
          const updated = { ...g, best: { ...g.best } }
          const best = updated.best

          if (data.appId) best.appId = data.appId
          if (data.header) best.header_image = data.header
          if (data.capsule) best.image = data.capsule

          // Apply metadata as fresh array copies
          if (data.genres) best.genres = [...data.genres]
          if (data.developers && data.developers.length > 0) best.developer = data.developers[0]

          if (best.genres && best.genres.length > 0) {
            // Pick best category based on priority
            const sorted = [...best.genres].sort((a, b) => {
              const pA = GENRE_PRIORITY[a] || 999
              const pB = GENRE_PRIORITY[b] || 999
              return pA - pB
            })
            best.category = sorted[0]
          }

          // Mark as fully resolved to prevent future queuing
          updated.metadata_resolved = true

          // Use splice for absolute guaranteed reactivity in Vue 3 filters
          this.groups.splice(groupIdx, 1, updated)

          console.log(`[Enricher] Metadata applied & resolved marked for: ${name}`)
        }
      }
    },

    toggleTurbo() {
      this.isTurbo = !this.isTurbo
      this._maxConcurrency = this.isTurbo ? 5 : 1

      // If already enriching, this._maxConcurrency update above is enough.
      // If not, we start it.
      if (!this.isEnriching && this.groups.length > 0) {
        this.startBackgroundEnrichment()
      }
    }
  }
})
