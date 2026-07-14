<script setup>
import { ref, onMounted, computed } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { useRoute } from 'vitepress'
import Lightbox from './components/Lightbox.vue'
import Timeline from './components/Timeline.vue'
import DeployTime from './components/DeployTime.vue'

const { Layout: DefaultLayout } = DefaultTheme
const route = useRoute()
const posts = ref([])

const isHome = computed(() => route.path === '/LCYBlogBak/' || route.path === '/LCYBlogBak/index.html')

onMounted(async () => {
  try {
    const res = await fetch('/LCYBlogBak/timeline.json')
    posts.value = await res.json()
  } catch (e) {
    console.error('Failed to load timeline:', e)
  }
})
</script>

<template>
  <DefaultLayout>
    <template #layout-top>
      <Lightbox />
    </template>
    <template #home-features-after>
      <DeployTime />
      <div class="home-timeline">
        <Timeline :posts="posts" :limit="10" :show-more="true" />
      </div>
    </template>
  </DefaultLayout>
</template>

<style>
.home-timeline {
  max-width: 1152px;
  margin: 3rem auto 0;
  padding: 0 24px;
}
</style>
