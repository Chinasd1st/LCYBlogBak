---
title: 时间线
description: 李晨煜 QQ空间说说时间线
---

<script setup>
import { ref, onMounted } from 'vue'
import Timeline from '/.vitepress/theme/components/Timeline.vue'

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch('/LCYBlogBak/timeline.json')
    posts.value = await res.json()
  } catch (e) {
    console.error('Failed to load timeline:', e)
  } finally {
    loading.value = false
  }
})
</script>

<div v-if="loading" style="text-align:center;padding:4rem;color:var(--vp-c-text-3);">加载中...</div>
<Timeline v-else :posts="posts" />
