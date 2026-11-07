# 续写交接卡

**最近更新**：2026-11-07

## 已交付

- VitePress 项目骨架、跨章节统一导航、进度状态文件及自动校验工具。
- **《JMM 与 happens-before》** 可阅读首版：核心概念、生活类比、四种读写顺序对比、逐帧图示、容易混淆的边界、即时小测。
- 以前的独立 HTML 演示和旧版整本 Markdown 原稿归档，以便后续逐章迁移。

## 下次优先制作

1. **《volatile 可见性 vs 原子性》**：重点解释 `count++` 为何丢失更新；两个线程各读/改/写的交互动画；如何用 `AtomicInteger` 或锁修复。
2. **《CAS 与 ABA》**：通过具体版本号/余额案例演示 ABA，给出 `AtomicStampedReference` 使用示例。
3. **《线程池 execute() 流程》**：corePoolSize / workQueue / maximumPoolSize / 拒绝策略条件流动图。

## 当前约束与待检查

- 当前使用的是 VitePress 1.6.4 稳定版本。
- 构建首次运行需要 npm 安装依赖；若工具环境没有 npm 网络访问，用户本地执行即可。
- 交互模拟用于解释 **JMM 允许/保证的关系**，不是实时显示真实 CPU 的缓存变化。
- 每次完成一节后，必须更新这张交接卡和 `content-status.json`。

## 未来对 AI 的一句话指令

> 请先读项目里的 AGENTS.md、NEXT.md、content-status.json，沿用已有 VitePress 网站和 Vue 动画风格，按 NEXT.md 继续下一章，最后更新状态、构建检查并提交增量，不要重新生成孤立文档。
