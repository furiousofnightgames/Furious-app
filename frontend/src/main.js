import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useDownloadStore } from './stores/download'
import './styles/globals.css'
import './styles/cyberpunk.css'
import './styles/tailwind.css'

const pinia = createPinia()

console.log('App initialized. Version: LibraryCacheFix')

// Prevent multiple initializations during hot reload
if (!window.__appInitialized) {
  window.__appInitialized = true

  const app = createApp(App)

  app.use(pinia)
  app.use(router)

  // call aria2 status check and connect websocket after app boot
  setTimeout(() => {
    try {
      const store = useDownloadStore()
      if (store) {
        if (typeof store.checkAria2Status === 'function') {
          store.checkAria2Status().catch(() => { })
        }
        if (typeof store.connectWebSocket === 'function') {
          store.connectWebSocket()
        }
      }
    } catch (e) {
      // ignore
    }
  }, 500)

  app.mount('#app')
}

// mount toast root component dynamically
import Toast from './components/Toast.vue'
const toastRoot = document.createElement('div')
document.body.appendChild(toastRoot)
createApp(Toast).use(pinia).mount(toastRoot)
