import { defineConfig } from 'vitepress'
import { generateSidebar } from "vitepress-sidebar";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Lichenyu Blog Backup",
  description: "Backup files of Lichenyu's Blog",
  base: "/lcyblogbak/",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      // { text: 'Examples', link: '/markdown-examples' }
    ],

    sidebar: generateSidebar({
    // 侧边栏的根目录，默认为docs
    documentRootPath: "./",
    // 使用h1的标题作为侧边栏的标题
    useTitleFromFileHeading: true,
    // 使用文件夹的index.md
    useFolderTitleFromIndexFile: true,
    // 指向文件夹的链接
    useFolderLinkFromIndexFile: true,
    // 根据md文件的order进行排序
    sortMenusByFrontmatterOrder: true,
    // 排序之后将不是文件夹的放后面
    sortFolderTo: "top",
    // 菜单展开功能
    collapsed: false,
}),

    socialLinks: [
      { icon: 'github', link: 'https://github.com/chinasd1st/lcyblogbak' }
    ]
  }
})
