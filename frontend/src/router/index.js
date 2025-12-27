import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Downloads from '../views/Downloads.vue'
import Sources from '../views/Sources.vue'
import NewDownload from '../views/NewDownload.vue'
import ItemDetails from '../views/ItemDetails.vue'
import Library from '../views/Library.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/downloads',
    name: 'Downloads',
    component: Downloads
  },
  {
    path: '/sources',
    name: 'Sources',
    component: Sources
  },
  {
    path: '/library',
    name: 'Library',
    component: Library
  },
  {
    path: '/new',
    name: 'NewDownload',
    component: NewDownload
  },
  {
    path: '/new-download',
    name: 'NewDownloadAlt',
    component: NewDownload
  },
  {
    path: '/item/:id',
    name: 'ItemDetails',
    component: ItemDetails
  }
]

const router = createRouter({
  history: createWebHashHistory(), // Changed from createWebHistory for Electron compatibility
  routes
})

export default router
