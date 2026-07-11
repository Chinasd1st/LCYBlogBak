<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const active = ref(null)

function open(src) {
  active.value = src
  document.body.style.overflow = 'hidden'
}

function close() {
  active.value = null
  document.body.style.overflow = ''
}

function handleClick(e) {
  if (active.value) return
  const img = e.target.closest('.vp-doc img, .tl-thumb img')
  if (img && img.src) {
    open(img.src)
  }
}

function handleKey(e) {
  if (e.key === 'Escape' && active.value) close()
}

onMounted(() => {
  document.addEventListener('click', handleClick)
  document.addEventListener('keydown', handleKey)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClick)
  document.removeEventListener('keydown', handleKey)
})
</script>

<template>
  <Teleport to="body">
    <div v-if="active" class="lb-overlay" @click="close">
      <img :src="active" @click.stop />
      <button class="lb-close" @click="close">&times;</button>
    </div>
  </Teleport>
</template>

<style>
.lb-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  cursor: zoom-out;
  backdrop-filter: blur(8px);
}

.lb-overlay img {
  max-width: 90vw;
  max-height: 85vh;
  border-radius: 6px;
  object-fit: contain;
  cursor: default;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
}

.lb-close {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.lb-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.vp-doc img {
  cursor: zoom-in;
  border-radius: 6px;
  transition: opacity 0.15s;
}

.vp-doc img:hover {
  opacity: 0.9;
}
</style>
