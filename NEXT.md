# 续写交接卡

**最近更新**：2026-11-08 · **项目版本 v0.3.0**

## 当前成果（已有六章可阅读，53 章总规划）

1. `docs/java/concurrency/jmm-happens-before.md` — JMM 与 happens-before；保留原有动画。
2. `docs/java/concurrency/volatile-atomicity.md` — volatile 与 count++；保留原有动画。
3. `docs/java/concurrency/cas-aba.md` — **本次新增**，CAS 成功/失败/重试、ABA、版本戳，三模式动画、代码、三题。
4. `docs/java/concurrency/aqs.md` — **本次新增**，获取失败入队、唤醒、可重入、非公平插队，三模式动画、代码、三题。
5. `docs/java/concurrency/thread-pool.md` — **本次新增**，core / workQueue / max / reject、shutdown，三模式动画、代码、三题。
6. `docs/java/concurrency/thread-local.md` — **本次新增**，ThreadLocalMap、污染/清理、CompletableFuture 显式传参，三模式动画、代码、三题。

### 统一项目的新机制

- 新增共享 `StepLab.vue`（数据驱动逐帧动画）、`KnowledgeQuiz.vue`（即时答题）。每章分别有 `*-lab.json` 和 `*-quiz.json` 数据；这些数据被正式 Vue 站点和离线预览共同读取。
- `scripts/create-offline-preview.py` 改成自动遍历 `content-status.json` 中所有 `ready` 章节，不再只渲染第二章。根目录 `PREVIEW.html` 可以切换六节、操作动画/答题，**不另建孤立 HTML**。
- `content-status.json` 已更新到 **6 ready / 0 draft / 47 planned**；状态、进度页与导航保持一致。

## 下次按顺序制作（优先）

1. **《JVM 堆栈与对象生命周期》**：栈帧、局部变量引用、对象堆上分配、GC Roots 逐帧示意；区分 JMM 与 JVM 内存区域。
2. **《GC 与垃圾回收器》**：可达性分析、Minor/Major/Full GC 的术语边界、G1 场景图、日志样本。
3. **《OOM 排查实战》**：Java heap space vs GC overhead vs Direct buffer memory vs 容器 OOMKilled；排查步骤与命令，不能混为一谈。
4. **《类加载与双亲委派》**：加载、链接、初始化、双亲委派与破坏边界。

## 验证和风险

- `npm run status`、`npm run check` 通过；新四章共 5 个可运行 Java 程序，通过 `javac --release 8` 编译与实际运行：`true/false`、`1`、`2`、`T4 rejected`、`A/null/null/hello, main-user`。
- Playwright Chromium 使用内存加载生成的 `PREVIEW.html`，测试了六章导航、模式切换、下一步、答题反馈、移动端宽度及页面无脚本异常。由于沙盒环境限制，不能直接打开本地 file:// / loopback 链接，**不宣称已测试实际用户双击打开行为**。
- 正式 VitePress 依赖安装尝试返回 npm registry DNS `EAI_AGAIN`，因此没有完成安装，故 `npm run build` 尚未验证；用户在本地联网环境运行 `npm install && npm run build`。
- 教学动画只演示选定的概念路径，不是 JVM/CPU 真实执行采样；避免将实现细节写成语言规范保证。

## 下一次对话的一句话

> 用最新版本 ZIP 或可读的 GitHub 仓库打开本项目，先读 `AGENTS.md`、`NEXT.md`、`content-status.json`；从 JVM 章节开始渐进续写，复用 StepLab 和 KnowledgeQuiz，完成后更新状态/进度/预览/CHANGELOG，运行检查并提交 Git。不要重新创建独立文档，也不要覆盖已完成章节。
