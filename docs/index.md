---
title: Java 后端互动知识手册
---

# Java 后端 · 交互式知识手册

<div class="intro-hero">
  <div class="eyebrow">不是背八股 · 而是把原理真正看明白</div>
  <h2>看得懂、能动手、会回答</h2>
  <p>从一个真实问题开始，用通俗语言解释；用可点的图一步步演示；最后再说出严格的技术结论。每次只完善少量专题，整本书持续增长。</p>
</div>

## 现在可以阅读

**[第一节：JMM 和 happens-before，为什么 volatile 能让另一线程看到 data=42？](/java/concurrency/jmm-happens-before)**

这个专题包含：

- `data=42` 与 `ready=true` 的真实问题。
- 为什么“代码先写了”不等于“其他线程一定看到”。
- 可点击的 happens-before 分步演示。
- 四种读写顺序的比较图。
- `volatile` 究竟保证什么、不保证什么。
- 常见面试问答和点击选择题。

## 这本书怎么持续变长？

```text
同一网站
  ├── P0 Java 集合 → HashMap、红黑树……
  ├── P0 多线程 → JMM（可读）、volatile、CAS、AQS……
  ├── P0 JVM → GC、OOM……
  ├── P0 Spring → IOC、事务……
  ├── P0 数据库 → B+树、MVCC……
  ├── P1 Kafka / Redis / ES……
  └── P2 算法 / AI Agent……
```

新增章节后，它就出现在**本网站侧边目录中**，不是另做一个分散的 HTML 文件。

**[查看全书实际完成度 →](/progress)**

::: tip 适合第一次接触多线程底层知识的人
不理解 JMM、主内存、可见性这些术语很正常。课程优先用普通语言解释，再给严格的术语。动画只是帮助理解，不代表真实 CPU 正在按图示移动数据。
:::
