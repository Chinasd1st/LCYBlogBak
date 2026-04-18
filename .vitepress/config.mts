import { defineConfig } from 'vitepress'
import { generateSidebar } from "vitepress-sidebar";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Lichenyu Blog Backup",
  description: "Backup files of Lichenyu's Blog",
  base: "/LCYBlogBak/",
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

    search: {
      provider: 'local',
      options: {
        detailedView: true,
        locales: {
          root: { // 如果你想翻译默认语言，请将此处设为 `root`
            translations: {
              button: {
                buttonText: '搜索',
                buttonAriaLabel: '搜索'
              },
              modal: {
                displayDetails: '显示详细列表',
                resetButtonTitle: '重置搜索',
                backButtonTitle: '关闭搜索',
                noResultsText: '没有结果',
                footer: {
                  selectText: '选择',
                  selectKeyAriaLabel: '输入',
                  navigateText: '导航',
                  navigateUpKeyAriaLabel: '上箭头',
                  navigateDownKeyAriaLabel: '下箭头',
                  closeText: '关闭',
                  closeKeyAriaLabel: 'Esc'
                }
              }
            }
          }
        }
      }

    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/chinasd1st/lcyblogbak' }
    ]
  }
})
