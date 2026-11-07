---
title: CAS 与 ABA · 比较后才更新，为什么还可能出错
outline: deep
---

<script setup>
import StepLab from '../../components/StepLab.vue'
import KnowledgeQuiz from '../../components/KnowledgeQuiz.vue'
import casLab from '../../components/cas-aba-lab.json'
import casQuiz from '../../components/cas-aba-quiz.json'
</script>

# CAS 与 ABA：明明检查了旧值，怎么还会改错？

<p class="lead">上一节我们发现：两个线程都读取 <code>count=0</code>，再各自写回 <code>1</code>，会丢失一次递增。现在换一种思路：<strong>写入之前先问一句“它还是我刚才看见的那个值吗？”</strong>这就是 CAS 的出发点。</p>

::: tip 30 秒速懂

CAS = **Compare-And-Set（比较并设置）**。可以理解成售票员处理库存：

- 我刚才看到余票是 **5 张**，准备改成 **4 张**。
- 提交时重新核对：**当前仍是 5 吗？** 是，才允许这次更新；不是，就报告失败。
- 别人先把 5 改为 4，我再用旧的 5 去写，就不能悄悄覆盖别人的结果。

**但是：**如果库存经历了 **5 → 3 → 5**，只看“现在还是 5”会发现不了期间曾被修改，这就是 **ABA 问题**。
:::

## 1. 反例：不核对旧值，更新就会丢

```java
// 共享值当前为 0
int oldA = count;  // A 读到 0
int oldB = count;  // B 也读到 0
count = oldA + 1;  // A 写 1
count = oldB + 1;  // B 还是写 1：覆盖了 A 的成果
```

上面是**概念性的交错步骤**，不是可以直接复制运行的完整并发程序。核心问题是：B 从未检查它读取以后，`count` 有没有被其他线程改变。

使用 `AtomicInteger.compareAndSet(expected, update)` 时，比较与更新在并发意义上是**同一次原子操作**：

```java
AtomicInteger atom = new AtomicInteger(0);
boolean ok = atom.compareAndSet(0, 1);
// 只有当前值仍是 0，才尝试改成 1；返回是否成功
```

它不是 Java 的 `if (atom.get()==0) atom.set(1)` 的简单缩写。后面这种写法的判断和写入之间可以被其他线程插入。

## 2. 动画：成功 → 失败 → ABA → 带版本号的修复

先看第一个模式，看 B 为什么**不能直接覆盖 A**；再切到 ABA，看“值绕一圈回到原样”的危险；最后看加上版本号后的效果。

<StepLab :lab="casLab" />

### 2.1 一次 compareAndSet 失败，是否自动重试？

**不会。** `compareAndSet()` 单次调用只告诉你成功或失败；要不要再次读取、重新计算并尝试，需要业务代码决定。

```java
import java.util.concurrent.atomic.AtomicInteger;

public class CasLoopDemo {
    public static void main(String[] args) {
        AtomicInteger count = new AtomicInteger(0);

        // 这一段手写重试循环在 Java 8 / 17 都能运行
        for (;;) {
            int old = count.get();
            int updated = old + 1;
            if (count.compareAndSet(old, updated)) {
                break; // 成功，退出
            }
            // 失败说明尝试时已经不匹配；重新读取和计算
        }
        System.out.println(count.get()); // 1
    }
}
```

注意 `AtomicInteger.incrementAndGet()` 本身保证原子递增，实际 JVM/JDK 可能采用原子加指令或其他实现；**不要认为它在所有平台上都恰好执行上面这段 Java 循环**。

## 3. ABA 究竟是什么？

假设某个状态最初为 `A`：

```text
时间向下：
线程 A                         线程 B
读到状态 A，准备改 C           —
暂时停住                       将 A 改为 B
                               又将 B 改回 A
CAS(预期 A, 新值 C) 成功        —
```

A 的 CAS 在原子性上**没有出错**：提交时当前值确实等于 `A`。但假设业务要求「从我检查起，这个对象从未被别人修改过」，单纯的值比较就不够了。

::: warning ABA 不是所有业务场景里的漏洞

如果你关心的只有**当前计数值**，而不关心中间改动的历史，那么 `A → B → A` 可能完全没问题。

危险场景通常是：**业务正确性依赖“期间没有变更”**，例如需要识别状态版本是否更新过、某个节点或资源是否经历过释放再复用。不能看到 ABA 三个字就断言所有 CAS 都不安全。
:::

## 4. 为什么版本号能发现变化？

让状态从单独的 `A` 变成一对数据 **`(A, stamp=0)`**：

```text
A 首次读取       (A, 0)
B 修改第一次     (B, 1)
B 修改第二次     (A, 2)
A 想提交时对比   预期 (A,0) ≠ 当前 (A,2)
结果             CAS 失败
```

在 Java 8 / 17 中，`AtomicStampedReference<V>` 支持同时比较**引用与版本戳**：

```java
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.AtomicStampedReference;

public class AbaDemo {
    enum State { A, B, C }

    public static void main(String[] args) {
        // 场景 1：只比较引用，无法识别从 A → B → A 的历史
        AtomicReference<State> normal = new AtomicReference<>(State.A);
        State old = normal.get();              // A 先观察到 A
        normal.set(State.B);                   // 模拟 B 修改
        normal.set(State.A);                   // 模拟 B 又改回来
        System.out.println(normal.compareAndSet(old, State.C)); // true

        // 场景 2：除了引用，还检查版本号
        AtomicStampedReference<State> tagged =
                new AtomicStampedReference<>(State.A, 0);
        int[] holder = new int[1];
        State oldRef = tagged.get(holder);     // 原子地取得引用+stamp
        int oldStamp = holder[0];              // 0

        tagged.compareAndSet(State.A, State.B, 0, 1);
        tagged.compareAndSet(State.B, State.A, 1, 2);
        System.out.println(tagged.compareAndSet(
                oldRef, State.C, oldStamp, oldStamp + 1)); // false
    }
}
```

**运行输出固定为：**

```text
true
false
```

这段程序用串行操作**固定模拟**了 A 暂停、B 改动、A 继续的交错，方便稳定说明原理。真正的并发程序仍需要处理重试、冲突和线程退出等问题。

### 4.1 一个源码级细节：比较的是引用，不是 equals

`AtomicStampedReference` 的引用比较使用 `==`（是否为**同一个对象引用**），不是对象的 `equals()`。所以如果业务状态是“内容相同但不同实例”的对象，不能直接用 `equals` 的心智模型解释它。上面使用 `enum State`，正好避免了“值相同但对象身份不同”的干扰。

### 4.2 版本号并非万能

- `stamp` 是整数。如果版本策略设计不当、发生回绕或被业务代码错误复用，仍可能失去辨别能力。
- 只能保护**这一对引用与版本**的原子更新；并不自动保护数据库另一行、外部支付服务或多个独立对象组成的事务。
- 发生 CAS 失败时，**业务应重新验证前提**，不能无脑循环到成功，尤其是退款、扣款等有副作用的流程。

## 5. CAS 有什么代价？

| 问题 | 怎么理解 |
|---|---|
| 高竞争下重复失败 | 很多线程同时提交同一个旧值，失败方可能花时间重复计算与尝试。|
| ABA | 只有当前值的比较，无法记录“中途被改过”的历史。|
| 多变量一致性 | 单个 CAS 不能天然把两个独立账户的金额更新成一个原子事务。|
| 自旋 ≠ 一定无阻塞 | CAS 是原子原语，外层重试循环可能一直竞争；整体算法是否 lock-free 还取决于算法性质。|

单个热点计数器可考虑 `AtomicInteger`；高并发统计还可了解 `LongAdder`（它的汇总语义和单次原子快照并不相同）。涉及一组需要同时一致的字段时，锁或事务往往更好解释与维护。

## 6. 面试怎么回答？

**面试官：CAS 是什么，解决什么问题？**

> CAS 是 Compare-And-Set：比较期望旧值与当前值，匹配才原子写入新值，不匹配就失败。它能避免简单读—改—写在竞争时悄悄覆盖别人的成功更新。单次 CAS 失败不会自动重试，通常由上层决定重试逻辑。

**追问：ABA 是什么？**

> A 线程先读到状态 A，B 线程把状态改为 B 又改回 A。A 再 CAS 时只看当前还是 A，可能成功，却没有识别期间变化。如果业务必须检测修改历史，可引入版本号，如 AtomicStampedReference 同时对比引用和 stamp。

**追问：AtomicStampedReference 彻底解决所有并发问题吗？**

> 不能。它只原子管理单个引用和版本戳，不是数据库事务。版本还要正确维护；CAS 失败要按业务重新校验。

## 7. 自测：CAS 看的是“现在”还是“历史”？

<KnowledgeQuiz :questions="casQuiz" />

### 这一章应当能独立说明

- [ ] 画出 CAS 成功、失败、重新尝试的完整过程。
- [ ] 解释 `compareAndSet()` 与 `get()+set()` 的根本区别。
- [ ] 举出一个业务上在乎“期间被修改过”的 ABA 场景。
- [ ] 解释为什么 `AtomicStampedReference` 要同时检查引用和 stamp。
- [ ] 不把 `compareAndSet()` 的单次调用说成“自动无限重试”。

**上一节：** [volatile 可见性与原子性](/java/concurrency/volatile-atomicity)  
**下一节：** [AQS 与锁](/java/concurrency/aqs)

### 规范参考

- [JDK 17 AtomicInteger API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html)
- [JDK 17 AtomicStampedReference API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/AtomicStampedReference.html)
