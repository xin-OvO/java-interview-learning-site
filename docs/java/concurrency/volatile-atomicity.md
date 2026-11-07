---
title: volatile 可见性与原子性 · count++ 为什么丢数据
outline: deep
---

<script setup>
import CounterRaceLab from '../../components/CounterRaceLab.vue'
import AtomicityQuiz from '../../components/AtomicityQuiz.vue'
</script>

# volatile 可见性与原子性：为什么两个线程各加一，结果却是 1？

<p class="lead">上一节我们知道：A 先写 <code>data</code> 再发布 <code>volatile ready</code>，B 先获取 <code>ready</code> 再读 <code>data</code>，就能建立可见性保证。可是有人问：<strong>既然 volatile 能让其他线程看到最新值，为什么两个线程做 <code>count++</code> 还是可能少加一次？</strong></p>

::: tip 30 秒速懂

把 `count++` 想成两个人在一张纸上登记人数。两个人都想让人数加一：

1. A 看纸：当前 `0`；B 也看纸：当前 `0`。
2. A 心算 `0 + 1 = 1`；B 也心算 `0 + 1 = 1`。
3. A 写回 `1`；B 再写回 `1`。

两个人都认真执行了“加一”，**结果却只有 `1`，丢失了一次更新**。

`volatile` 让读写共享变量遵守特定的可见性与顺序规则，**但不会把“读 → 加 → 写”包成一个别人不能插队的整体**。要保证这一整个操作不被并发破坏，可使用 `AtomicInteger.incrementAndGet()` 或同一把锁保护的 `synchronized`。
:::

## 1. 反例：volatile 已经加了，为什么还是有错？

```java
class Counter {
    volatile int count = 0;

    void addOne() {
        count++;  // 看着只有一行，其实不是一次不可分割的更新
    }
}

// 线程 A：counter.addOne();
// 线程 B：counter.addOne();
```

直觉是：初始为 `0`，A 加 `1`，B 再加 `1`，最后 `2`。

但在并发场景里，**A 和 B 不一定“一个完整做完，再轮到另一个完整做”**。`count++` 从逻辑上至少有三个步骤：

```java
int oldValue = count;   // 第一步：读共享值
int newValue = oldValue + 1; // 第二步：在自己的计算中加一
count = newValue;       // 第三步：写回共享值
```

::: info 先看清“原子性”是什么意思
**原子操作**：在我们讨论的并发意义下，这个操作作为一个不可分割的整体完成；别人不能在中间插入一次竞争性的更新，导致这次操作的效果丢失。

`volatile int count` 的**单次读、单次写**有相应的原子性与可见性保证。但 `count++` 是一个复合的“读—改—写”，**单步安全不代表组合起来安全**。
:::

## 2. 动手看动画：两次 ++ 是怎么变成一次的？

先选择 **「volatile count++」**，连续点“下一步”，尤其注意：**A 读到 0 后、写回之前，B 也可以读到 0**。接着切换到 **AtomicInteger** 和 **synchronized**，观察为什么最终都能得到 2。

<CounterRaceLab />

### 2.1 把第一条动画翻译成时间线

```text
共享变量 count = 0

时间↓       线程 A                       线程 B
----------------------------------------------------
  ①        读取 count → 0
  ②                                     读取 count → 0
  ③        计算 0 + 1 → 1
  ④                                     计算 0 + 1 → 1
  ⑤        写回 count = 1
  ⑥                                     写回 count = 1
----------------------------------------------------
最终：count = 1（预期是 2）
```

这里没有任何“读到了不该读的旧值”的问题：**B 读的时候 A 还没写回 1，B 正常读取到 0**。

同样也**不需要发生指令重排**。即使每个线程内部都严格按照“读、加、写”的源码顺序执行，只要两个线程在这三步之间交错，就会丢失更新。

### 2.2 为什么 A 写了 1 后，B 不会自动重新算一遍？

因为 B 早就把 `0` 取出来放进了本次计算的临时值，已经算出了 `1`。后面 A 对共享变量的写入，**不会追溯修改 B 已经完成的计算**。

`volatile` 没有规定“只要别人写了新值，我之前读出来的本地变量就必须自动重新计算”。这不是 volatile 的职责。

## 3. 精确定义：可见性、原子性、有序性分别负责什么？

| 概念 | 通俗说法 | `volatile` 对 `count++` 能做什么？ |
|---|---|---|
| **可见性** | 写了一个新值，别的线程后续怎样可靠地看到它？ | 对 volatile 本身的读写提供规范定义的可见性保证。|
| **原子性** | 整套读—改—写是否不可被竞争更新打断？ | **不能**。两个线程仍可先后读取同一个 0，再都写回 1。|
| **有序性** | 哪些指令优化不能破坏规定的观察结果？ | 为 volatile 读写建立发布/获取相关的顺序约束，但不禁止全部重排。|

前一章 [JMM 与 happens-before](/java/concurrency/jmm-happens-before) 讲的是**A 的先前写入如何对 B 后续读取可见**。

这一章讲的是另外一个问题：**即使读写都可见，两个线程同时修改同一个值，是否会覆盖彼此的成果？**

### 3.1 两个关键区别

- `volatile count = 1`：这是**一次写操作**，没有“先读再算再写”的复合步骤。
- `volatile count++`：这是**一次复合操作**，要先知道旧值才能计算新值，会出现并发竞争窗口。

因此不要把“`volatile` 保证可见性”背成“`volatile` 保证并发安全”。

::: warning 为什么不能简单说“volatile 保证最新值”？
准确的说法是：volatile 读写遵循 Java 内存模型定义的同步顺序和可见性规则。它**不会预知未来的写入**，更不能阻止两个线程在任何写回发生之前都读到 `0`。
:::

## 4. 用 Java 代码稳定复现丢失更新

很多示例让两个线程循环一百万次，然后说“你应该看到少于两百万”。这种写法只能说**可能**发生竞争，不保证每次运行都会出现特定数字。

为了第一次学习更直观，我们用两个 `CountDownLatch` 把执行顺序固定成：**A、B 都先读完 0，然后再一起开始写回**。

下面代码可直接保存为 `VolatileLostUpdateDemo.java`，在 **Java 8 / Java 17** 下编译运行：

```java
import java.util.concurrent.CountDownLatch;

public class VolatileLostUpdateDemo {
    private static volatile int count = 0;

    public static void main(String[] args) throws InterruptedException {
        CountDownLatch bothRead = new CountDownLatch(2);
        CountDownLatch canWrite = new CountDownLatch(1);

        Runnable task = () -> {
            int oldValue = count; // A、B 都会先读到 0
            bothRead.countDown();
            try {
                canWrite.await(); // 等另一位线程也读完
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
            count = oldValue + 1; // 两人都会把 1 写回
        };

        Thread a = new Thread(task, "A");
        Thread b = new Thread(task, "B");
        a.start();
        b.start();

        bothRead.await();     // 确认两人都拿到旧值
        canWrite.countDown(); // 允许两人写回
        a.join();
        b.join();

        System.out.println(count); // 1
    }
}
```

这段示例为什么能稳定得到 `1`？

- 两个线程都在 `count` 更新前，先完成一次读取，因此都会拿到 `0`。
- 主线程等两人读取结束才释放 `canWrite`；两人之后都执行 `count = 0 + 1`。
- 两次写回的都是 `1`，所以最终还是 `1`。

**注意：** 这里故意把 `count++` 拆开来控制交错，用于**稳定证明复合操作会丢失更新**；不是声称真实业务中的单行 `count++` 每次都执行成这个固定顺序。

## 5. 修复方案一：AtomicInteger 原子递增

```java
import java.util.concurrent.atomic.AtomicInteger;

public class AtomicCounterDemo {
    private static final AtomicInteger count = new AtomicInteger(0);

    public static void main(String[] args) throws InterruptedException {
        Runnable task = () -> count.incrementAndGet();
        Thread a = new Thread(task, "A");
        Thread b = new Thread(task, "B");
        a.start();
        b.start();
        a.join();
        b.join();

        System.out.println(count.get()); // 2
    }
}
```

`AtomicInteger.incrementAndGet()` 的承诺是：**整个递增作为原子更新完成**。当 A 和 B 都成功执行一次时，结果一定包含两次递增。

### 5.1 CAS 是什么？先理解“尝试，不允许乱覆盖”

CAS = **Compare And Set**，可以先记成“拿旧值核对一下，没变才写入”。

在上面的交互动画里，使用了一个 CAS 风格的概念过程：

1. A 想把 `0 → 1`，成功。
2. B 也想把 `0 → 1`，但现在真实值已是 `1`，所以这次尝试失败。
3. B 重新基于 `1` 计算，尝试 `1 → 2`，成功。

它确保 B 不会像普通 `count++` 那样，**把 A 的更新无条件覆盖掉**。

::: info 关于“源码级”和“概念级”的区别
这是用 CAS 解释原子更新的一条**概念执行路径**。`AtomicInteger.incrementAndGet()` 的具体底层实现会因 JDK 版本、JVM 和 CPU 而不同；现代 JDK 可能使用原子 get-and-add 等机制，不能把动画逐帧当成它真实执行的 Java 源码或机器指令。下一章会专门讲 `compareAndSet()`、CAS 循环和 ABA。
:::

### 5.2 一个极容易写错的代码

```java
AtomicInteger count = new AtomicInteger(0);

// 错误：两次操作分别是原子的，拼在一起不是！
count.set(count.get() + 1);

// 正确：整个递增具有原子性
count.incrementAndGet();
```

`AtomicInteger` 不是魔法容器；**要选对它提供的原子操作**。同理，`get()`、计算、`set()` 分开写，仍然可能丢失更新。

## 6. 修复方案二：synchronized 把整套步骤锁起来

```java
public class SynchronizedCounterDemo {
    private static int count = 0;
    private static final Object LOCK = new Object();

    private static void addOne() {
        synchronized (LOCK) {
            count++; // 只有拿到同一把锁的人，才能进入这里
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Thread a = new Thread(SynchronizedCounterDemo::addOne, "A");
        Thread b = new Thread(SynchronizedCounterDemo::addOne, "B");
        a.start();
        b.start();
        a.join();
        b.join();
        System.out.println(count); // 2
    }
}
```

可以把 `synchronized` 想成一间**只有一把钥匙的操作室**：

- A 先拿到钥匙，就能在屋内读、加、写；此时 B 只能等。
- A 归还钥匙后，B 才能进入，看到 A 完成的结果，再做第二次加一。
- **必须保护的是同一份共享数据，并且竞争线程必须使用同一把锁。** A 锁 `LOCK_A`、B 锁 `LOCK_B`，对同一个 `count` 并没有形成互斥。

`synchronized` 也提供相应的可见性和 happens-before 保证：**对一个监视器的解锁 happens-before 后续对同一个监视器的加锁**。

## 7. 边界与常见误解

**误解一：“volatile 已经读最新值，B 不应该再读到 0。”**

B 读取时 A 可能还没有写回 1，所以 B 合法且正常地读到 0。随后 A 写回 1，并不会自动重做 B 已经执行的读取。

**误解二：“丢失更新是 CPU 指令重排造成的。”**

不一定。本节动画里完全不需要重排。仅仅因为两个线程的操作**交错执行**就能复现。

**误解三：“AtomicInteger 的 get() 和 set() 都是原子的，所以 get()+set() 一起也是原子的。”**

错误。每一个方法的单独原子性，不会自动扩大成整个 `get → 计算 → set`。

**误解四：“加了 synchronized，就算两边锁不一样也安全。”**

错误。A、B 必须用**同一把锁**，才能防止对共享变量的更新交错。

**误解五：“AtomicInteger 比 synchronized 在所有场景下都更好。”**

不成立。`AtomicInteger` 很适合单个数值的简单原子更新；如果要同时维护库存数、总金额等**多个共享字段之间的一致性**，同一个锁保护整个业务逻辑往往更直观。高竞争下的吞吐量也需要实际测量，不能光凭名字判断。

**误解六：“线程启动了，我在 main 线程直接打印就一定能看到最终值。”**

错误。打印前还要等待工作线程完成，例如用 `join()`；否则你可能在两个工作线程还没运行完时就打印。`join()` 负责等待和建立对应完成后的可见性，**不能替代 `count++` 本身所需的并发保护**。

## 8. 面试怎么回答？

**面试官：volatile 能保证可见性，为什么不能保证 count++ 的原子性？**

> `count++` 不是一个不可分割的操作，逻辑上包括读取旧值、加一、写回。`volatile` 保证单次读写的内存可见性与相关有序性，但不会让读—改—写整体互斥。比如两个线程都在别人写回前读到 0，分别算出 1，最后都写回 1，就会丢失一次更新。解决可以用 `AtomicInteger.incrementAndGet()` 做原子更新，也可以用同一把锁上的 `synchronized` 把整个操作保护起来。

**追问一：`volatile int count` 的单次读和写是不是原子的？**

是。这里不安全的不是一次读取或一次赋值，而是 `count++` 需要把多个步骤作为**一个整体**完成。

**追问二：`AtomicInteger` 为什么不会丢失更新？**

它提供原子的读—改—写操作，例如 `incrementAndGet()`；发生竞争时，更新不会默默覆盖掉别人已经完成的递增。CAS 重试可以帮助理解这一思想，但不能假定所有 JDK 都按动画中的 Java 代码逐步执行。

**追问三：只要 `synchronized` 包住了 `count++`，就一定安全？**

只有当所有可能并发修改这个共享 `count` 的路径都遵守同一把锁时，才能依靠这把锁保证这一更新过程的互斥。绕开锁的写入仍然会破坏约束。

## 9. 自测：是真的理解了，还是只记住一句话？

<AtomicityQuiz />

### 学完这一章，你应该会做这几件事

- [ ] 不看资料，画出 A、B 都读取 0、都写回 1 的线程时间线。
- [ ] 解释“可见性”和“原子性”为何是两个不同问题。
- [ ] 知道 `AtomicInteger.incrementAndGet()` 与 `get()+set()` 的区别。
- [ ] 能写出同一锁对象上的 `synchronized (LOCK)` 正确示例。
- [ ] 不把动画当成 CPU 缓存快照或某个 JDK 固定的汇编指令。

---

**前一节：** [JMM 与 happens-before：先发布，再获取](/java/concurrency/jmm-happens-before)  
**下一节：** [CAS、ABA 与 AtomicStampedReference](/java/concurrency/cas-aba)

### 规范参考

- [Java 语言规范 JLS §17.4：内存模型与 happens-before](https://docs.oracle.com/javase/specs/jls/se17/html/jls-17.html)
- [Oracle JDK 17 API：AtomicInteger](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html)
