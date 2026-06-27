import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/extract', name: 'Extract', component: () => import('../views/ExtractView.vue') },
  { path: '/editor', name: 'Editor', component: () => import('../views/EditorView.vue') },
  { path: '/export', name: 'Export', component: () => import('../views/ExportView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
