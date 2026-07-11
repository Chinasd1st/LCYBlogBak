import DefaultTheme from 'vitepress/theme'
import Timeline from './components/Timeline.vue'
import Lightbox from './components/Lightbox.vue'
import Layout from './Layout.vue'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component('Timeline', Timeline)
  }
}
