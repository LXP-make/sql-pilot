import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import SqlOptimize from '../views/SqlOptimize.vue'
import NaturalToSql from '../views/NaturalToSql.vue'
import History from '../views/History.vue'
import Feedback from '../views/Feedback.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/optimize',
    name: 'SqlOptimize',
    component: SqlOptimize
  },
  {
    path: '/natural-to-sql',
    name: 'NaturalToSql',
    component: NaturalToSql
  },
  {
    path: '/history',
    name: 'History',
    component: History
  },
  {
    path: '/feedback',
    name: 'Feedback',
    component: Feedback
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
