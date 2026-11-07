---
title: Java 后端互动知识手册
---

# Java 后端 · 交互式知识手册

<div class="intro-hero">
  <div class="eyebrow">不是死记八股 · 而是一步步把原理看明白</div>
  <h2>看得懂、能动手、会回答</h2>
  <p>每篇从具体问题开始，用通俗语言解释；然后逐帧展示线程行为；最后补上准确原理、Java 代码、常见误区和面试回答。每次继续写，整本书只会增长，不会另起文档。</p>
</div>

## 当前可阅读的 6 节 · 多线程专题

| 节次 | 知识点 | 动手能看到什么 |
|---|---|---|
| 第一节 | [JMM 与 happens-before](/java/concurrency/jmm-happens-before) | 两个线程对 `data`、`ready` 的观察顺序，volatile 发布/获取。 |
| 第二节 | [volatile 的可见性与原子性](/java/concurrency/volatile-atomicity) | 两次 `count++` 为什么丢一次更新；原子类和锁如何解决。 |
| 第三节 | [CAS 与 ABA](/java/concurrency/cas-aba) | CAS 成功、失败与重试；A→B→A 为什么骗过旧值比较。 |
| 第四节 | [AQS 与 ReentrantLock](/java/concurrency/aqs) | 抢锁失败怎么排队；唤醒≠持锁；重入次数与公平性。 |
| 第五节 | [线程池 execute() 流程](/java/concurrency/thread-pool) | 核心线程→队列→扩容→拒绝；无界队列与 shutdown。 |
| 第六节 | [ThreadLocal 与 CompletableFuture](/java/concurrency/thread-local) | 池线程数据污染、`finally remove()`、异步传参。 |

::: tip 每节都是“真正的教材正文”，不是目录清单

每节都包含：**30 秒速懂 → 反例 → 互动动画 → 原理 → Java 代码 → 边界与误解 → 面试答案 → 答题检测**。

每个按钮都能自己点击、重放、切换场景；动画是选定的合法/教学过程，不是 CPU 缓存或 JVM 实况。
:::

## 还没有完成的部分

全书规划 **13 个模块、53 个专题**，目前首版可读 **6 节**。后面将继续覆盖 JVM、Spring、B+ 树、Kafka、Redis、ES、分布式与 AI Agent。**未写好的章节不会伪装成已经完成。**

[查看每个专题的真实完成度](/progress)

## 让它持续增长而不是重写

```text
同一个 Git 仓库 / 同一个 VitePress 网站
├── docs/java/concurrency/      已完成 6 节
├── docs/java/jvm/              下一步：内存、GC、OOM
├── docs/components/            复用的动画和测验播放器
├── content-status.json         所有专题的状态
├── AGENTS.md                    每一节必须遵守的讲解标准
└── NEXT.md                      下一次从哪里继续
```

**离线阅读**：下载项目 ZIP 后直接双击根目录的 `PREVIEW.html`，即可在六章之间切换。正式运行方式见 `README.md`。
