<template>
  <div class="card" :class="{ expanded: isOpen }" @click="isOpen = !isOpen">
    <div class="card-header">
      <div class="rank-badge">#{{ index + 1 }}</div>
      <div class="main-info">
        <div class="title-row">
          <span class="title">{{ item.title }}</span>
        </div>
        <div class="meta-row">
          <span class="source" :class="sourceClass">{{ sourceLabel }}</span>
          <span v-if="item.score" class="score">🔥 {{ item.score }}</span>
          <span v-if="item.comments" class="comments">💬 {{ item.comments }}</span>
          <Tag v-for="cat in item.categories" :key="cat" :type="cat" />
        </div>
      </div>
      <div class="expand-icon">{{ isOpen ? '▾' : '▸' }}</div>
    </div>

    <Transition name="fade">
      <div v-if="isOpen" class="card-body">
        <!-- 摘要 -->
        <div v-if="item.summary" class="summary-section">
          <div class="section-label">摘要</div>
          <p class="summary-text">{{ item.summary }}</p>
        </div>

        <!-- 原因 -->
        <div class="reason-section" :class="{ 'no-summary': !item.summary }">
          <div class="section-label">值得关注的原因</div>
          <p class="reason-text">{{ item.reason }}</p>
        </div>

        <!-- 链接 -->
        <div class="links">
          <a :href="item.url" target="_blank" class="link-btn external" @click.stop>
            <span>📄</span> 阅读原文
          </a>
          <a v-if="item.hn_url" :href="item.hn_url" target="_blank" class="link-btn" @click.stop>
            <span>💬</span> HN 讨论
          </a>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  index: { type: Number, default: 0 },
})

const isOpen = ref(false)

const sourceLabel = computed(() => {
  const map = { 'Hacker News': 'HN', 'GitHub Trending': 'GitHub', 'ArXiv': 'ArXiv' }
  return map[props.item.source] || props.item.source
})

const sourceClass = computed(() => {
  const map = { 'Hacker News': 'hn', 'GitHub Trending': 'github', 'ArXiv': 'arxiv' }
  return map[props.item.source] || ''
})
</script>

<script>
import { h } from 'vue'

const Tag = {
  props: { type: String },
  setup(props) {
    const labelMap = { ai_coding: 'AI Coding', embodied_ai: '具身智能', general_ai: '通用 AI' }
    const colorMap = {
      ai_coding: { bg: '#1a3a5c', text: '#60a5fa' },
      embodied_ai: { bg: '#2d1b4e', text: '#a78bfa' },
      general_ai: { bg: '#1a3a2e', text: '#34d399' },
    }
    return () => {
      const c = colorMap[props.type] || colorMap.general_ai
      return h('span', { class: 'tag', style: { background: c.bg, color: c.text } },
        labelMap[props.type] || props.type)
    }
  }
}
</script>

<style scoped>
.card {
  background: #1a1a2e;
  border-radius: 14px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #2a2a3e;
}
.card:hover {
  border-color: #3a3a5e;
  box-shadow: 0 4px 20px rgba(96, 165, 250, 0.06);
}
.card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.rank-badge {
  min-width: 32px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a3e;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #888;
}
.main-info { flex: 1; min-width: 0; }
.title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  color: #e8e8f0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}
.source {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}
.source.hn { background: #1a3a2e; color: #34d399; }
.source.github { background: #2a2a3e; color: #e0e0e0; }
.source.arxiv { background: #2d1b4e; color: #a78bfa; }
.score { font-size: 12px; color: #f59e0b; }
.comments { font-size: 12px; color: #888; }
.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.expand-icon { font-size: 18px; color: #555; margin-top: 2px; }
.card-body { margin-top: 14px; padding-top: 14px; border-top: 1px solid #2a2a3e; }
.summary-section {
  background: #12122a;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 10px;
}
.reason-section {
  background: #12122a;
  border-radius: 10px;
  padding: 14px;
}
.section-label {
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 6px;
}
.summary-section .section-label { color: #f59e0b; }
.reason-section .section-label { color: #60a5fa; }
.summary-text {
  font-size: 13px;
  line-height: 1.6;
  color: #b0b0c0;
}
.reason-text {
  font-size: 13px;
  line-height: 1.6;
  color: #b0b0c0;
}
.links {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
.link-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  background: #2a2a3e;
  border-radius: 8px;
  font-size: 12px;
  color: #b0b0c0;
  text-decoration: none;
  transition: all 0.15s;
}
.link-btn:hover { background: #3a3a5e; color: #e8e8f0; }
.link-btn.external { background: #1a2a4e; color: #60a5fa; }
.link-btn.external:hover { background: #1a3a6e; }
.fade-enter-active { transition: all 0.25s ease; }
.fade-leave-active { transition: all 0.15s ease; }
.fade-enter-from { opacity: 0; transform: translateY(-8px); }
.fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
