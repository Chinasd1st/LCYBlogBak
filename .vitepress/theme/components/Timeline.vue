<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  posts: { type: Array, required: true },
  limit: { type: Number, default: 0 },
  showMore: { type: Boolean, default: false }
})

const expanded = ref(false)

const sortedPosts = computed(() => {
  return [...props.posts].sort((a, b) => b.ts - a.ts)
})

const visiblePosts = computed(() => {
  if (props.limit > 0 && !expanded.value) {
    return sortedPosts.value.slice(0, props.limit)
  }
  return expanded.value ? sortedPosts.value : sortedPosts.value.slice(0, 30)
})

const totalCount = computed(() => sortedPosts.value.length)

function formatTime(ts) {
  const d = new Date(ts * 1000)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function formatDate(ts) {
  const d = new Date(ts * 1000)
  const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
  return `${months[d.getMonth()]}月${d.getDate()}日`
}

function getYearMonth(ts) {
  const d = new Date(ts * 1000)
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  return `${d.getFullYear()}年${months[d.getMonth()]}`
}

function getDayOfWeek(ts) {
  const d = new Date(ts * 1000)
  const days = ['日', '一', '二', '三', '四', '五', '六']
  return '周' + days[d.getDay()]
}

const groupedPosts = computed(() => {
  const groups = []
  let currentKey = null
  let currentGroup = null

  for (const post of visiblePosts.value) {
    const key = getYearMonth(post.ts)
    if (key !== currentKey) {
      currentGroup = { label: key, posts: [] }
      groups.push(currentGroup)
      currentKey = key
    }
    currentGroup.posts.push(post)
  }
  return groups
})
</script>

<template>
  <div class="tl">
    <div class="tl-header">
      <span class="tl-count">{{ totalCount }}</span>
      <span class="tl-label">条说说</span>
    </div>

    <div class="tl-content">
      <div v-for="group in groupedPosts" :key="group.label" class="tl-group">
        <div class="tl-month">{{ group.label }}</div>

        <div v-for="post in group.posts" :key="post.tid" class="tl-node">
          <div class="tl-time-badge">{{ formatTime(post.ts) }}</div>

          <div class="tl-card">
            <div class="tl-card-meta">
              <span class="tl-weekday">{{ getDayOfWeek(post.ts) }}</span>
              <span class="tl-date">{{ formatDate(post.ts) }}</span>
              <span v-if="post.source" class="tl-source">{{ post.source }}</span>
            </div>

            <div class="tl-card-body" v-html="post.content || '<em style=&quot;opacity:0.3&quot;>...</em>'" />

            <div v-if="post.images && post.images.length" class="tl-gallery">
              <div
                v-for="(img, i) in post.images"
                :key="i"
                class="tl-thumb"
              >
                <img
                  :src="'/LCYBlogBak/downloaded/' + img"
                  :alt="'图片 ' + (i + 1)"
                  loading="lazy"
                />
              </div>
            </div>

            <a v-if="post.link" :href="'/LCYBlogBak' + post.link" class="tl-link">查看原文 →</a>
          </div>
        </div>
      </div>

      <div v-if="showMore" class="tl-more">
        <a href="/LCYBlogBak/timeline">查看更多 →</a>
      </div>
      <div v-else-if="!expanded && totalCount > 30" class="tl-more" @click="expanded = true">
        展开全部 {{ totalCount }} 条
      </div>
    </div>
  </div>
</template>

<style scoped>
.tl {
  max-width: 700px;
  margin: -1rem auto 0;
}

.tl-header {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  margin-bottom: 2rem;
}

.tl-count {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--vp-c-brand-1);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.tl-label {
  font-size: 0.85rem;
  color: var(--vp-c-text-3);
}

.tl-content {
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 0.5rem;
}

.tl-group {
  margin-bottom: 0;
}

.tl-month {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--vp-c-text-3);
  padding: 1rem 0 0.5rem;
  border-bottom: 1px solid var(--vp-c-divider);
  margin-bottom: 0.75rem;
  position: sticky;
  top: 55px;
  background: var(--vp-c-bg);
  z-index: 10;
}

.tl-node {
  display: flex;
  gap: 0.75rem;
  padding: 0.625rem 0;
  border-bottom: 1px solid var(--vp-c-divider-light);
  transition: background 0.15s;
}

.tl-node:last-child {
  border-bottom: none;
}

.tl-node:hover {
  background: var(--vp-c-bg-soft);
  margin: 0 -0.75rem;
  padding-left: 0.75rem;
  padding-right: 0.75rem;
  border-radius: 6px;
}

.tl-time-badge {
  flex-shrink: 0;
  width: 48px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--vp-c-brand-1);
  font-variant-numeric: tabular-nums;
  padding-top: 0.15rem;
  text-align: right;
}

.tl-card {
  flex: 1;
  min-width: 0;
}

.tl-card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.tl-weekday {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  padding: 0.05rem 0.4rem;
  border-radius: 3px;
}

.tl-date {
  font-size: 0.75rem;
  color: var(--vp-c-text-2);
}

.tl-source {
  font-size: 0.65rem;
  color: var(--vp-c-text-3);
  margin-left: auto;
}

.tl-card-body {
  font-size: 0.9rem;
  line-height: 1.65;
  color: var(--vp-c-text-1);
  word-break: break-word;
  text-wrap: pretty;
  overflow-wrap: break-word;
  white-space: pre-line;
}

.tl-gallery {
  display: flex;
  gap: 4px;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  font-size: 0;
}

.tl-gallery:only-child {
  max-width: 320px;
}

.tl-thumb {
  flex: 1 1 0;
  min-width: 80px;
  max-width: 160px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
}

.tl-gallery:only-child .tl-thumb {
  flex: 0 0 auto;
  max-width: 100%;
}

.tl-thumb img {
  width: 100%;
  height: auto;
  display: block;
  vertical-align: top;
}

.tl-more {
  text-align: center;
  padding: 0.875rem;
  margin-top: 0.75rem;
  cursor: pointer;
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  transition: all 0.2s;
}

.tl-more:hover {
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}

:deep(.tl-card-body em) {
  color: var(--vp-c-text-3);
}

.tl-link {
  display: inline-block;
  margin-top: 0.4rem;
  font-size: 0.75rem;
  color: var(--vp-c-brand-1);
  text-decoration: none;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.tl-link:hover {
  opacity: 1;
}
</style>
