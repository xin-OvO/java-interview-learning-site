import { defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'
const state = JSON.parse(readFileSync(new URL('../../content-status.json', import.meta.url), 'utf8'))
const sidebar = [
  { text: '开始阅读', items: [{text:'这本书怎么用',link:'/'},{text:'全书进度',link:'/progress'}] },
  ...state.modules.map(m=>({
    text: `${m.priority} · ${m.title}`,
    collapsed: m.priority !== 'P0',
    items: m.chapters.filter(c=>c.status!=='planned').map(c=>({
      text: `${c.title}${c.status==='draft'?'（初稿）':''}`,
      link: `/${c.path}`
    }))
  })).filter(m=>m.items.length)
]
export default defineConfig({
  lang:'zh-CN',
  title:'Java 后端 · 互动知识手册',
  description:'从零理解原理，边看图边点动画的 Java 后端面试教材',
  cleanUrls:true,
  themeConfig: {
    siteTitle:'☕ Java 后端 · 互动知识手册',
    nav:[{text:'开始阅读',link:'/'},{text:'全书进度',link:'/progress'}],
    sidebar,
    outline:{label:'本页目录',level:[2,3]},
    docFooter:{prev:'上一节',next:'下一节'},
    search:{provider:'local'},
    returnToTopLabel:'回到顶部',
    sidebarMenuLabel:'目录',
    darkModeSwitchLabel:'切换主题',
    footer:{message:'渐进式构建 · Markdown 正文 + Vue 动画 · Git 版本管理',copyright:'用于个人学习与面试复习'}
  },
  head:[['meta',{name:'theme-color',content:'#0b9a86'}]]
})
