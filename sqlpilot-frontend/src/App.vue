<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-text">SQL Pilot</router-link>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">首页</router-link>
          <router-link to="/optimize" class="nav-item" :class="{ active: $route.path === '/optimize' }">SQL优化</router-link>
          <router-link to="/natural-to-sql" class="nav-item" :class="{ active: $route.path === '/natural-to-sql' }">自然语言转SQL</router-link>
          <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">历史记录</router-link>
          <router-link to="/feedback" class="nav-item" :class="{ active: $route.path === '/feedback' }">反馈</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="app-footer">
      <p>SQL Pilot &mdash; SQL性能优化助手</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--gray-800);
  color: white;
  padding: 0 var(--space-4);
  height: var(--header-height);
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--gray-700);
}

.header-content {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--space-8);
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.logo-text {
  font-size: var(--text-xl);
  font-weight: 700;
  letter-spacing: 0.5px;
  color: white;
  text-decoration: none;
}
.logo-text:hover {
  color: white;
}

.nav-menu {
  display: flex;
  gap: var(--space-1);
}

.nav-item {
  color: var(--gray-400);
  text-decoration: none;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}
.nav-item:hover {
  color: white;
  background: var(--gray-700);
}
.nav-item.active {
  color: white;
  background: var(--color-primary);
}

.app-main {
  flex: 1;
  max-width: var(--content-max-width);
  margin: 0 auto;
  width: 100%;
  padding: var(--space-6) var(--space-8);
}

.app-footer {
  text-align: center;
  padding: var(--space-4);
  color: var(--gray-400);
  font-size: var(--text-xs);
  border-top: 1px solid var(--gray-200);
}

/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 640px) {
  .header-content {
    padding: 0 var(--space-4);
  }
  .nav-item {
    padding: var(--space-2);
    font-size: var(--text-xs);
  }
}
</style>
