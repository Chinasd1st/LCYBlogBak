import { defineConfig } from 'vitepress'
import { generateSidebar } from "vitepress-sidebar";

const zhSidebar = generateSidebar({
  documentRootPath: "./",
  useTitleFromFileHeading: true,
  useFolderTitleFromIndexFile: true,
  useFolderLinkFromIndexFile: true,
  sortMenusByFrontmatterOrder: true,
  sortFolderTo: "top",
  collapsed: false,
});

const enSidebar = generateSidebar({
  documentRootPath: "./en",
  useTitleFromFileHeading: true,
  useFolderTitleFromIndexFile: true,
  useFolderLinkFromIndexFile: true,
  sortMenusByFrontmatterOrder: true,
  sortFolderTo: "top",
  collapsed: false,
});

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "李晨煜 QQ空间说说备份",
  description: "李晨煜 QQ空间说说完整备份 · 2025.04 — 2026.06",
  base: "/LCYBlogBak/",
  lastUpdated: true,
  sitemap: {
    hostname: "https://chinasd1st.github.io/LCYBlogBak",
  },
  head: [
    ["meta", { name: "author", content: "李晨煜" }],
    ["meta", { property: "og:title", content: "李晨煜 QQ空间说说备份" }],
    ["meta", { property: "og:description", content: "150 条说说完整备份 · 2025.04 — 2026.06" }],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:locale", content: "zh_CN" }],
    ["meta", { property: "og:locale:alternate", content: "en_US" }],
    ["meta", { property: "og:image", content: "/LCYBlogBak/og-image.png" }],
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
    ["meta", { name: "twitter:image", content: "/LCYBlogBak/og-image.png" }],
  ],

  locales: {
    root: {
      label: "中文",
      lang: "zh-CN",
      themeConfig: {
        nav: [
          { text: "首页", link: "/" },
          { text: "项目介绍", link: "/intro" },
          { text: "技术细节", link: "/tech" },
        ],
        sidebar: zhSidebar,
        search: {
          provider: "local",
          options: {
            detailedView: true,
            translations: {
              button: { buttonText: "搜索", buttonAriaLabel: "搜索" },
              modal: {
                displayDetails: "显示详细列表",
                resetButtonTitle: "重置搜索",
                backButtonTitle: "关闭搜索",
                noResultsText: "没有结果",
                footer: {
                  selectText: "选择",
                  selectKeyAriaLabel: "输入",
                  navigateText: "导航",
                  navigateUpKeyAriaLabel: "上箭头",
                  navigateDownKeyAriaLabel: "下箭头",
                  closeText: "关闭",
                  closeKeyAriaLabel: "Esc",
                },
              },
            },
          },
        },
        lastUpdated: { text: "最后更新" },
        docFooter: { prev: "上一篇", next: "下一篇" },
        outline: { label: "页面导航" },
        returnToTopLabel: "回到顶部",
        sidebarMenuLabel: "菜单",
        darkModeSwitchLabel: "主题",
        lightModeSwitchTitle: "切换到浅色模式",
        darkModeSwitchTitle: "切换到深色模式",
      },
    },
    en: {
      label: "English",
      lang: "en-US",
      title: "Lichenyu Qzone Backup",
      description: "Complete backup of Lichenyu's Qzone posts · 2025.04 — 2026.06",
      themeConfig: {
        nav: [
          { text: "Home", link: "/en/" },
          { text: "About", link: "/en/intro" },
          { text: "Tech", link: "/en/tech" },
        ],
        sidebar: enSidebar,
        search: {
          provider: "local",
          options: {
            detailedView: true,
          },
        },
        lastUpdated: { text: "Last updated" },
        docFooter: { prev: "Previous", next: "Next" },
        outline: { label: "On this page" },
        returnToTopLabel: "Return to top",
        sidebarMenuLabel: "Menu",
        darkModeSwitchLabel: "Appearance",
        lightModeSwitchTitle: "Switch to light mode",
        darkModeSwitchTitle: "Switch to dark mode",
      },
    },
  },

  themeConfig: {
    socialLinks: [
      { icon: "github", link: "https://github.com/chinasd1st/lcyblogbak" },
    ],
  },
});
