# Java 后端面试 · 交互式知识手册

> 一个**持续增长的同一本书**，不是每次生成一份孤立文档。

- **内容**：Markdown (`docs/**/*.md`)；按知识点渐进追加，保留之前所有章节。
- **动画**：Vue (`docs/components/*.vue`)；插入到 Markdown 中，支持点击、步骤切换、可视化讲解。
- **目录与进度**：`content-status.json` 是唯一事实来源；导航和进度统计基于它生成。
- **跨对话续写**：先读 `AGENTS.md`、`NEXT.md`、`content-status.json`；每次更新后提交到 Git。若希望 ChatGPT 在新对话继续，给它 GitHub 仓库地址并授权可用连接，或重新上传最新项目 ZIP。

## 快速运行

安装 Node.js 20 或更高版本，进入项目目录：

```bash
npm install
npm run dev
```

浏览器打开终端打印的地址，通常是 `http://127.0.0.1:5173`。

```bash
npm run start:chapter -- java/concurrency/volatile-atomicity # 安全建立下一节（不会覆盖旧文件）
npm run status  # 根据 content-status.json 重新生成学习进度页
npm run check   # 检查计划/正文文件、禁用的误报状态等
npm run build   # 构建整个文档站
npm run preview # 预览构建结果
```

> 开发版只需安装一次依赖，以后新增章节直接刷新页面；无需重新制作整份 Word/HTML。

## 如何新增一节

1. 推荐先执行 `npm run start:chapter -- java/concurrency/volatile-atomicity` 自动创建初稿并更新状态；或者手动在 `docs/...` 下新增如 `docs/java/concurrency/cas.md` 的 Markdown。
2. 在 `content-status.json` 中将该章的 `status` 从 `planned` 改为 `ready`，并填入 `path`。或标记 `draft`（初稿）。
3. 需要动画时，在 `docs/components/` 中新建 Vue 组件，在 `.md` 文件中通过 `<script setup> import ... </script>` 引用。
4. 执行 `npm run status && npm run build`，修改 `CHANGELOG.md` 和 `NEXT.md`。
5. 用 Git 提交。**不要覆盖整个项目。**

## 关键文件

| 文件 | 作用 |
|---|---|
| `AGENTS.md` | 后续 AI 继续写作的固定规则和风格标准 |
| `NEXT.md` | 已写到哪里、下一步写哪章、当前问题 |
| `content-status.json` | 13 个模块、各章节状态、可完成度统计 |
| `docs/java/concurrency/jmm-happens-before.md` | JMM 与 happens-before 示例第一章 |
| `docs/components/*.vue` | 可复用交互动画 |
| `sources/旧版知识手册原稿.md` | 上一版 33 页文字知识手册原稿，留作待扩写素材 |
| `docs/public/legacy/jmm-original.html` | 之前独立的 JMM 动画 HTML 归档 |

## 状态说明

- `planned`：计划中，不算已完成，正文文件可不存在。
- `draft`：已有初稿，需要人工核查事实、讲解和互动效果。
- `ready`：可以阅读的首版，仍可持续完善；不代表永远不需修订。

构建后的页面可以部署到 GitHub Pages / 任意静态站点。项目本身不依赖数据库、账号系统或后端服务。

## 本项目的限制

- `npm install` 首次需要下载依赖，离线环境无法首次安装。
- VitePress 不会“自动写知识点”；需要逐章补写，但所有成果都在同一目录和同一网站里。
- 如果不把项目文件放在 GitHub 或重新提供给新的聊天，新对话**不保证能读取本地项目的最新版本**。`NEXT.md` 和 `content-status.json` 可以减少上下文丢失。
