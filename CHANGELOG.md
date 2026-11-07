# 更新记录

## 2026-11-08 — 0.3.0

- **在同一个 VitePress 项目新增 4 个完整章节**：《CAS 与 ABA》《AQS 与锁》《线程池 execute()》《ThreadLocal 与 CompletableFuture》，保留旧的 JMM 和 volatile 内容。
- 新增共享 `StepLab.vue` 与 `KnowledgeQuiz.vue`，共 4 套动画数据、4 套题目数据：**12 个可切换动画模式、12 道有解析测试题**；避免为每个知识点重复造一份组件。
- 四章均包含：30 秒速懂、反例、分步可视化、准确原理、代码、边界/误解、面试参考答案、自测。
- 免安装 `PREVIEW.html` 重构成**自动从内容状态生成六章统一导航**，已用 Chromium 验证章节切换、动画步骤、模式切换、答题交互、移动端宽度与无 JS 运行异常。
- 使用 `javac --release 8` 编译运行新四章 5 个 Java 程序，得到正确输出；`npm run status` 和 `npm run check` 通过。
- 不足：本次 `npm install` 遇到 DNS `EAI_AGAIN`，环境内仍未具备 VitePress npm 依赖，无法进行 `npm run build` 全站打包验证；由用户在可联网机器复验。

## 2026-11-08 — 0.2.0

- **在原有网站中新增第二节《volatile 可见性 vs 原子性》**：初学者比喻、真实竞争原因、保证与非保证的边界。
- 新增可点击三模式逐帧动画 `CounterRaceLab.vue`：`volatile count++` 丢失更新、`AtomicInteger` 竞争重试的概念模型、`synchronized` 同锁互斥。
- 新增交互答题 `AtomicityQuiz.vue`（3 道题，回答后立即解析）。
- 补充 Java 8/17 可运行示例：CountDownLatch 稳定复现丢失更新、AtomicInteger 和 synchronized 两种修复。
- 更新首页、全书进度、状态 JSON、续写交接卡，保持现有 JMM 课程及旧资料不变。
- 新增共用动画数据 JSON，使免安装的 `PREVIEW.html` 可以直接展示本章逐帧动画和检测题；正式站与离线预览共享同一份内容数据。
- 已验证：`npm run status`、`npm run check` 通过；3 个 Java 程序以 `javac --release 8` 编译并运行，输出分别为 `1`、`2`、`2`；互动脚本通过 Node 语法检查。
- 未验证：`npm run build`。`npm install` 时访问 `registry.npmjs.org` 返回 DNS `EAI_AGAIN`，需在本地联网环境进行正式构建。

## 2026-11-07 — 0.1.0

- 建立可增量更新的 Markdown + Vue + VitePress 单站点项目。
- 加入 JMM 与 happens-before 首版互动课程，含动态逐帧时间线、四种顺序对比和理解测验。
- 引入进度状态 JSON、自动生成进度页、静态检查和 AI 接续指南。
- 保留旧版知识手册原稿与旧 JMM HTML 演示。
