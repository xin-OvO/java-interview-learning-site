# Java 后端面试 · 交互式知识手册

> 一个**持续增长的同一本书**，不是每次生成一份孤立文档。

- **内容**：Markdown (`docs/**/*.md`)；按知识点渐进追加，保留之前所有章节。
- **动画**：Vue (`docs/components/*.vue`)；插入到 Markdown 中，支持点击、步骤切换、可视化讲解。
- **目录与进度**：`content-status.json` 是唯一事实来源；导航和进度统计基于它生成。
- **跨对话续写**：先读 `AGENTS.md`、`NEXT.md`、`content-status.json`；每次更新后提交到 Git。若希望 ChatGPT 在新对话继续，给它 GitHub 仓库地址并授权可用连接，或重新上传最新项目 ZIP。

## 快速运行

**不安装任何依赖：** 解压后双击根目录的 `PREVIEW.html`，可以在**6 个可阅读章节**之间切换。包含 JMM（旧版离线动画）、volatile、CAS/ABA、AQS、线程池 execute()、ThreadLocal/CompletableFuture。新增的四章有 **12 种逐帧演示模式**与即时答题。预览从教材 Markdown 和 JSON 自动生成，**不是独立维护的第二本教材**。

如果要使用正式的统一章节导航、搜索和 VitePress 样式，安装 Node.js 20 或更高版本，进入项目目录：

```bash
npm install
npm run dev
```

浏览器打开终端打印的地址，通常是 `http://127.0.0.1:5173`。

```bash
npm run start:chapter -- java/jvm/memory # 安全建立下一节（不会覆盖旧文件）
npm run status  # 根据 content-status.json 重新生成学习进度页
npm run check   # 检查计划/正文文件、禁用的误报状态等
npm run build   # 构建整个文档站
npm run preview # 预览构建结果
```

> 开发版只需安装一次依赖，以后新增章节直接刷新页面；无需重新制作整份 Word/HTML。

## 如何新增一节

1. 推荐先执行 `npm run start:chapter -- java/jvm/memory` 自动创建初稿并更新状态；或者在 `docs/...` 下新增 Markdown。
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
| `docs/java/concurrency/jmm-happens-before.md` | 第一章：JMM 与 happens-before |
| `docs/java/concurrency/volatile-atomicity.md` | 第二章：volatile 可见性 vs 原子性 |
| `docs/components/CounterRaceLab.vue` | 第二章：volatile / AtomicInteger / synchronized 三模式逐帧动画 |
| `docs/components/counter-scenarios.json` | 三模式动画共享数据；正式网站和离线预览都从这里读取 |
| `docs/components/atomicity-questions.json` | 本章理解测试共享数据 |
| `docs/components/StepLab.vue` | 多章共用的动画播放器，步骤来自 `*-lab.json` |
| `docs/components/KnowledgeQuiz.vue` | 多章共用的即时理解测试，题目来自 `*-quiz.json` |
| `docs/java/concurrency/cas-aba.md` | CAS / ABA / 版本戳（第三节） |
| `docs/java/concurrency/aqs.md` | AQS / ReentrantLock（第四节） |
| `docs/java/concurrency/thread-pool.md` | execute 全流程（第五节） |
| `docs/java/concurrency/thread-local.md` | ThreadLocal / CompletableFuture（第六节） |
| `PREVIEW.html` | 全站免安装预览（自动生成，不要手工改正文） |
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
- `npm run offline` 或 `python3 scripts/create-offline-preview.py` 可以重建全书免安装预览，需要 Python 安装 `markdown-it-py`：`python3 -m pip install markdown-it-py`。项目自带已生成的 `PREVIEW.html`，直接阅读无需安装 Python 包。正式 VitePress 网站不依赖此 Python 包。
- 当前交付环境未能获取 npm 依赖，**不能保证已完成 VitePress 正式构建验证**；`npm run status`、`npm run check`、Java 样例及离线预览浏览器交互已独立验证。请在可联网开发机执行 `npm install && npm run build`。
