# AI 续写规则（必须先读）

本仓库是用户长期维护的 **一部完整 Java 后端面试互动教材**，而非学习计划/面试题罗列。

## 开始前

1. 读取 `README.md`、`NEXT.md`、`content-status.json`、`CHANGELOG.md`。
2. 仅读取将修改的章节、复用的 Vue 组件；不要在上下文中粘贴整书。
3. 使用现有目录、主题、组件和章节格式；禁止覆盖已有章节内容。
4. `sources/旧版知识手册原稿.md` 是旧资料，未经逐章核对不能直接标为 ready。

## 每一知识点的写作约定

- 从初学者视角讲清“为什么有这个问题”再给名词，避免上来定义堆砌。
- 用短句、生活类比、逐步推导、Java 8 或 Java 17 可运行代码。
- 依次包含：①30 秒速懂 ②一个反例 ③交互动画 ④准确原理 ⑤边界与常见误解 ⑥面试答案 ⑦检测题。
- 区分**代码文本顺序**、**线程执行交错**、**可见性**、**重排序**、**happens-before**，不把 JMM 抽象规则描述成真实 CPU 缓存工作流程。
- 标注依赖具体 JDK、MySQL、Kafka、ES 版本的细节。绝不编造实验输出、性能数据或严格内存保证。
- 页面尽量用可访问的 Vue CSS/SVG 动画；动画须有“下一步”“上一步/重置”以及同步文字解释；不能只有颜色或依赖自动播放。
- 每页需有一个能帮助读者检测理解的问题和答案解析。

## 修改步骤

1. 在目标 `.md` 原处新增/修订内容；新增动画组件到 `docs/components/`，避免复制多个相似组件。
2. 检查 `content-status.json` 状态与路径；只在确有可阅读正文时标为 `ready`。
3. `npm run status` 更新生成的进度页；`npm run build` 验证整个网站（没有网络依赖时可以至少运行 `npm run check`）。
4. 更新 `CHANGELOG.md` 与 `NEXT.md`，写清“这次新增、未完、下一步、已验证”。
5. 使用 Git 保留旧版本，不删除章节、不把不同批次独立导出为互不关联的 HTML。

## 未来用户要求“继续写”的默认流程

- 先读取 `NEXT.md` 确认下一篇，再检查 `content-status.json`。
- 完成一个或少数几个连续知识点；保持站点统一；交付**整个仓库变更（或可提交到用户授权的 GitHub 仓库）**，不是仅交付一个新 HTML。
- 若新对话无法访问最新文件，明确要求用户提供最新仓库/ZIP；不要假装已经读取过。

## v0.3.0 可复用交互组件（续写优先）

- `docs/components/StepLab.vue`：从 `*-lab.json` 读取 `modes`、`scenarios` 和逐帧卡片，不要复制新的一份动画播放器。
- `docs/components/KnowledgeQuiz.vue`：从 `*-quiz.json` 读取三道或更多题目；答案和解析必须属于同一份 JSON。
- 章节 Markdown 直接 `import Xxx from '../../components/xxx-lab.json'`，用 `<StepLab :lab="Xxx" />` 调用。
- 每次更新执行 `npm run status && npm run check && npm run offline`。离线预览生成需要 Python `markdown-it-py`，用户直接双击现成的 `PREVIEW.html` 不需要安装依赖。
- 已完成六节：JMM、volatile、CAS/ABA、AQS、线程池、ThreadLocal/CompletableFuture；下一阶段以 JVM 为主。
