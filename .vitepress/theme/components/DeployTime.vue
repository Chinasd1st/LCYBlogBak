<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const elapsed = ref({ days: 0, hours: 0, minutes: 0, seconds: 0 })
const buildTime = ref(null)
let timer = null

function update() {
  if (!buildTime.value) return
  const diff = Math.floor((Date.now() - buildTime.value) / 1000)
  elapsed.value = {
    days: Math.floor(diff / 86400),
    hours: Math.floor((diff % 86400) / 3600),
    minutes: Math.floor((diff % 3600) / 60),
    seconds: diff % 60,
  }
}

onMounted(async () => {
  try {
    const res = await fetch('/LCYBlogBak/deploy-time.json')
    const data = await res.json()
    buildTime.value = data.time
    update()
    timer = setInterval(update, 1000)
  } catch (e) {
    console.error('Failed to load deploy time:', e)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function pad(n) {
  return String(n).padStart(2, '0')
}
</script>

<template>
  <div class="deploy-time" v-if="buildTime">
    上次部署至今 <span class="dt-num">{{ elapsed.days }}</span> 天
    <span class="dt-num">{{ pad(elapsed.hours) }}</span> :
    <span class="dt-num">{{ pad(elapsed.minutes) }}</span> :
    <span class="dt-num">{{ pad(elapsed.seconds) }}</span>
  </div>
</template>

<style>
.deploy-time {
  text-align: center;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  margin-top: 1.5rem;
  font-variant-numeric: tabular-nums;
}
.dt-num {
  font-weight: 600;
  color: var(--vp-c-text-1);
}
</style>
