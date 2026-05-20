<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-text">SQL Pilot</span>
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
      <router-view />
    </main>
    <footer class="app-footer">
      <p>SQL Pilot &mdash; SQL性能优化助手</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f6f8;
  color: #1e293b;
  -webkit-font-smoothing: antialiased;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #1e293b;
  color: white;
  padding: 0 1rem;
  height: 56px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #334155;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.nav-menu {
  display: flex;
  gap: 0.25rem;
}

.nav-item {
  color: #94a3b8;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.15s ease;
}

.nav-item:hover {
  color: white;
  background: #334155;
}

.nav-item.active {
  color: white;
  background: #2563eb;
}

.app-main {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 1.5rem 2rem;
}

.app-footer {
  text-align: center;
  padding: 1rem;
  color: #94a3b8;
  font-size: 0.8rem;
  border-top: 1px solid #e2e8f0;
}
</style>
