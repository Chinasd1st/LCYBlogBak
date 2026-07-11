<script setup>
import DefaultTheme from 'vitepress/theme'
import Lightbox from './components/Lightbox.vue'

const { Layout: DefaultLayout } = DefaultTheme
</script>

<template>
  <DefaultLayout>
    <template #layout-top>
      <Lightbox />
    </template>
  </DefaultLayout>
</template>
