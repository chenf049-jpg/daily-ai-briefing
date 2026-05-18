<template>
  <div class="app">
    <header class="header">
      <h1>每日 AI 日报</h1>
      <p class="subtitle" v-if="data.date">{{ data.date }} · AI Coding & 具身智能</p>
      <p class="subtitle" v-else>加载中...</p>
    </header>

    <main class="main">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>数据加载失败</p>
        <p class="error-detail">{{ error }}</p>
      </div>

      <div v-else-if="data.total === 0" class="empty">
        <p>暂无数据，请等待下次更新</p>
      </div>

      <div v-else class="news-list">
        <NewsCard
          v-for="(item, index) in data.items"
          :key="index"
          :item="item"
          :index="index"
        />
      </div>
    </main>

    <footer class="footer">
      <p>数据来源: Hacker News & GitHub Trending · 每日自动更新</p>
      <p class="update-time">更新时间: {{ data.update_time || '-' }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NewsCard from './components/NewsCard.vue'

const data = ref({ items: [] })
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const resp = await fetch('/briefing.json?t=' + Date.now())
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    data.value = await resp.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
  background: #0f0f1a;
  color: #e0e0e0;
  min-height: 100vh;
}

.app {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px 16px;
}

.header {
  text-align: center;
  padding: 32px 0 24px;
}

.header h1 {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: #666;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: #666;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #2a2a3e;
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error {
  text-align: center;
  padding: 40px 0;
  color: #f87171;
}

.error-detail {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}

.empty {
  text-align: center;
  padding: 60px 0;
  color: #666;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer {
  text-align: center;
  padding: 32px 0 24px;
  font-size: 12px;
  color: #444;
}

.update-time {
  margin-top: 4px;
  font-size: 11px;
}
</style>
