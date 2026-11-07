---
title: JMM 与 happens-before · 从零理解
outline: deep
---

<script setup>
import HappensBeforeLab from '../../components/HappensBeforeLab.vue'
import OrderCompare from '../../components/OrderCompare.vue'
import MemoryQuiz from '../../components/MemoryQuiz.vue'
</script>

# JMM 与 happens-before：为什么看到 ready=true 后，就能看到 data=42？

<p class="lead">读这一章不需要先记住“内存屏障”“缓存一致性协议”。我们先问一个简单问题：<strong>一个线程写完东西，另一个线程怎么知道它真的写完了？</strong></p>

<div class="lesson-lens">
<strong>30 秒先懂</strong>

把线程 A 想成做饭的人，线程 B 想成取餐的人：

- A **先做好饭**（`data = 42`），再**亮起“已出餐”的灯**（`ready = true`）。
- B **先看到灯亮**（读到 `ready = true`），再去**取饭**（读取 `data`）。
- 只要这个“灯”用的是 `volatile`，就能在 Java 内存模型中建立对应的“发布 → 获取”保证。

**这不是让线程排队执行，而是给两个线程建立一条可靠的通信规则。**
</div>

## 1. 最初的问题：代码不是已经有先后顺序了吗？

下面两个变量由线程 A 和 B 共享：

```java
int data = 0;
boolean ready = false;

// 线程 A
// ①
 data = 42;
// ②
 ready = true;

// 线程 B
// ③
if (ready) {
    // ④
    int result = data;
    System.out.println(result);
}
```

你可能想：**A 明明是先写 data，再写 ready；B 看到了 ready=true，那肯定也能看到 data=42。**

问题是：A 内部的“先写后写”，不自动等于 B 能观察到这两个写入的同样顺序。Java 编译器、运行时和 CPU 可以在满足规则的前提下优化执行过程；不同线程读写共享数据还可能出现可见性差异。

没有同步保证时，B 在 `ready=true` 的分支里**可能读到旧的 `data=0`**。这句话不意味着每次都会出现 0，而是**语言规范没有承诺一定是 42**。

::: warning 先区分两个不同问题
**线程交错**：B 很可能在 A 写 data 以前就执行了读取，这是完全正常的时间安排。

**内存可见性 / 顺序**：即便从源码看 A 的 data 写在 ready 写之前，也不代表 B 必定观察到相同顺序。volatile 解决的是后一个问题中的同步保证，不是强制 A、B 按我们指定的时间运行。
:::

## 2. JMM 到底是什么？不要把它想成硬件结构图

**JMM 是 Java Memory Model（Java 内存模型）**，是一套规定多线程读写共享变量时，哪些结果允许出现、哪些结果必须保证的**语言规则**。

它**不是**：

- JVM 运行时的“堆、虚拟机栈、方法区”结构图。
- 某个 CPU 的 L1/L2/L3 缓存线路图。
- “每次写 volatile 都把所有东西立即复制到物理内存”的逐条硬件流程。

它**关心的是**：

| 关键词 | 生活中的说法 | 真正要解决的事 |
|---|---|---|
| 可见性 | “我改完了，你能看到吗？” | A 对共享数据的修改，何时能保证 B 看见 |
| 有序性 | “先做好饭，再亮灯” | 某些操作不能被优化成破坏同步语义的顺序 |
| 原子性 | “一套动作不能被别人插到中间” | `count++` 包含读、加、写，不是一个不可分割的动作 |
| happens-before | “这次改动对那次读取有保证” | 用一条规范上的关系，推导前面写入对后面读取可见 |

::: tip 术语翻译
`happens-before` 可以暂时记成 **“先行发生关系”**。但不要把它理解成普通钟表上的“早一分钟”。它首先是 **Java 规定的可见性和顺序保证关系**。
:::

## 3. 改成 volatile：不神奇，但有明确规则

只需要修改一个字段：

```java
int data = 0;
volatile boolean ready = false;

// 线程 A
 data = 42;       // ① 普通写
 ready = true;    // ② volatile 写：发布

// 线程 B
if (ready) {      // ③ volatile 读：获取；假设读到 true
    int x = data; // ④ 普通读
    System.out.println(x);
}
```

这里的保证是**有条件的**：如果 B 的 `ready` 读确实看到这次 A 发布的 `true`，而且没有其他线程再改 `data`，那么 B 接着读 `data` 就能看到 `42`。B 也可能先读到 `false`，那就不会执行 `if` 中的代码。

### 3.1 点按钮，看线程之间的关系如何出现

<HappensBeforeLab />

上面动画演示的是**一条被选择的、符合规则的执行路径**，不是 CPU 缓存的实时截图。

### 3.2 真正保证“42”的不是一句 volatile，而是三段关系

```text
线程 A                                     线程 B

① data = 42
     │ 同一线程内：程序顺序
     ▼
② ready = true  ── volatile 同步 ──▶  ③ 读到 ready = true
                                           │ 同一线程内：程序顺序
                                           ▼
                                       ④ 读取 data
```

分三段来理解：

1. **① → ②**：同一线程，程序顺序规则。A 的 data 写对这次 volatile 发布来说位于前面。
2. **② → ③**：对**同一个 volatile 变量**的写，与同步顺序中的后续读取之间建立 happens-before 关系。在此示例里，B 读到了 A 写的 `true`。
3. **③ → ④**：同一线程，程序顺序规则。B 在读 ready 后，再读取 data。

**happens-before 具有传递性**，所以可以连起来：

```text
①  ──▶  ②  ──▶  ③  ──▶  ④

因此：① data=42 happens-before ④ 读取 data
```

这才是 B 能保证看到 `42` 的原因。

::: details 再严谨一点：happens-before 不等于物理时间的箭头
规则保证的是 Java 程序可以观察到的行为。编译器和处理器仍可以进行**不破坏这条保证**的优化。不要由“存在 happens-before”推出“实际机器指令严格一行一行照源码执行”。
:::

## 4. volatile 会阻止所有指令重排吗？

**不会。** 它只限制会破坏对应发布/获取语义的重排。

- 对于 A：`data = 42` 写在 `volatile ready = true` **之前**，这次普通写不能被移到发布之后，让 B 看到 ready 却拿不到原本发布的数据。
- 对于 B：`int x = data` 写在读 `ready` **之后**，不能在内存模型里被当成发布前的读取，从而破坏获取后的可见性保证。
- 不相关的操作依然可能被编译器/CPU 优化。volatile 不是“所有线程完全串行运行”的开关。

你也会看到两个词：

**Release（发布/释放）**：A 发出 ready=true 时，把此前的数据修改纳入这次发布所保障的范围。

**Acquire（获取）**：B 读到对应发布信号后，后面读取的数据享有这次发布带来的可见性保证。

不需要记住“必须刷新哪个 CPU 缓存”，只记住 **“先写数据，再发布；先获取，再读数据”**。

## 5. 四种顺序，为什么只有一种能保证？

在下面互动区，你可以切换**线程 A 的写顺序**和**线程 B 的读顺序**。

<OrderCompare />

### 5.1 中间插入别的代码也可以

你之前问“两个 ready 必须连续吗？”——**不需要紧挨着**，而是需要关系能串起来。

```java
// 线程 A
 data = 42;
 String note = "已处理";
 ready = true;   // volatile 发布

// 线程 B
if (ready) {    // volatile 获取到 true
    int local = 123;
    System.out.println(data); // 保证看到 42
}
```

`note`、`local` 插在中间都不影响正确的 happens-before 链。真正要对齐的是**发布之前的写**与**获取之后的读**。

### 5.2 如果 B 先读 data，再读 volatile ready 呢？

```java
// A：先 data 后 ready
 data = 42;
 ready = true;    // volatile

// B：先读取 data
int before = data;
boolean flag = ready;
System.out.println(before + ", " + flag);
```

**即使 B 最终读到了 `flag=true`，也不能反过来保证前面那次 `before` 是 42。**

原因很简单：B 已经读完 `data`，**后面**获得的保证不会倒流回**前面**已经发生的读取。

## 6. 易错边界：volatile 不是万能药

### 误区一：“volatile 写永远在 volatile 读之前”

错误。B 完全可能先运行，看到 `ready=false`。正确表述是：**在 volatile 的同步顺序里，写入与后续读取之间有相应 happens-before 规则**；不是说写线程一定先得到 CPU 时间。

### 误区二：“data 本身没加 volatile，所以永远不能可靠读取”

错误。在这个发布/获取例子中，`data` 可以是普通变量，借助 `ready` 的同步关系确保这次写入对后续读取可见。

### 误区三：“ready=true 放在 data=42 前面也一样”

错误。B 看到 ready=true 时，A 可能还没执行 data=42。发布只能保证**发布之前**的相关写入，不能提前保证未来的写入。

### 误区四：“volatile 保证可见性，所以 count++ 安全”

错误。`count++` 实际至少包含**读旧值、加一、写回**三个逻辑步骤。两个线程可能同时读到 0，各自加一，最后都写回 1，导致丢失一次更新。

```java
volatile int count = 0;

// A、B 都执行一次：
count++;    // 两个线程执行结束，结果仍可能是 1，而不是 2
```

要修复，需要 `synchronized`、`AtomicInteger.incrementAndGet()` 等可以保证原子性的方案。下一章会用逐帧动画专门解释这一点。

## 7. 面试怎么回答？

**面试官：JMM 和 happens-before 是什么？volatile 为什么能保证可见性？**

> JMM 是 Java 定义线程之间如何读写共享变量的一套内存模型规则，并不是 JVM 堆栈布局。happens-before 规定两个操作间的可见性和顺序保证，具有传递性。
>
> 如果线程 A 先写普通变量 data，再写 volatile ready；线程 B 先读到这次发布的 ready=true，再读 data，那么通过程序顺序规则、volatile 规则和 happens-before 传递性，A 对 data 的写入就对 B 后续读取可见。
>
> volatile 不保证所有操作严格按源码执行，更不能保证 count++ 这样的复合操作是原子的。

**再追问：ready 写和读必须紧挨着 data 吗？**

不需要。只要 A 的目标写位于发布之前、B 的目标读位于获取之后，且建立了对应的同步关系，就能利用 happens-before 传递性。

**再追问：为什么不能简单说 volatile “把数据刷到主内存”？**

因为 JMM 定义的是可观察到的可见性和顺序约束，不是某一种 CPU 的具体缓存刷写路径。不同 JVM 与硬件可以采用不同的正确实现。

## 8. 自测：能否真的分清“发布前”和“获取后”？

<MemoryQuiz />

### 检查清单

- [ ] 能说清 JMM 与 JVM 运行时内存区域的区别。
- [ ] 知道“在 A 线程代码里写在前面”为什么不自动等于“B 一定看到”。
- [ ] 能画出 `data写 → ready写 → ready读 → data读` 的完整链条。
- [ ] 明白 volatile 不禁止所有重排序、不保证 B 一定先读到 true。
- [ ] 能解释为什么先读 data 后读 ready 不能追溯保证前面的读取。
- [ ] 能说出为什么 volatile 不保证 `count++` 原子性。

---

**旧版独立演示（只作对照）：** [打开此前制作的 JMM 单页 HTML](/legacy/jmm-original.html)。现在起新内容都写进这一个网站里的章节，旧文件只保留作参考。
