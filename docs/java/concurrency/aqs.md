---
title: AQS 与 ReentrantLock · 抢锁、排队、唤醒、重入
outline: deep
---

<script setup>
import StepLab from '../../components/StepLab.vue'
import KnowledgeQuiz from '../../components/KnowledgeQuiz.vue'
import aqsLab from '../../components/aqs-lab.json'
import aqsQuiz from '../../components/aqs-quiz.json'
</script>

# AQS 与锁：抢不到锁，线程去哪儿了？

<p class="lead">你已经知道：用同一把锁保护 <code>count++</code> 能避免丢失更新。接下来问一个更底层的问题：线程 A 正在持锁，线程 B 也想进来时，B 是一直站着疯狂检查，还是会排队等通知？<strong>AQS 的价值是提供获取、等待、唤醒等同步基础机制，供锁等同步器复用。</strong></p>

::: tip 30 秒速懂

把 `ReentrantLock` 想成一个**只有一把钥匙的房间**：

1. A 先取得钥匙，进入房间。
2. B 来了拿不到，就登记到等待队列，条件合适时阻塞等待。
3. A 离开并放回钥匙，系统通知后面等待的人。
4. B 被唤醒后**还需要重新尝试拿钥匙**；被叫醒 ≠ 已拿到钥匙。

**AQS**（`AbstractQueuedSynchronizer`）可以把状态记录、等待队列和唤醒机制封装起来。`ReentrantLock` 的同步实现使用了 AQS，但它自身还有公平/非公平策略、持锁者、可重入等语义。
:::

## 1. 反例：不同的锁锁不住同一个共享变量

```java
private static int count = 0;
private static final Object LOCK_A = new Object();
private static final Object LOCK_B = new Object();

// 线程 A
synchronized (LOCK_A) { count++; }

// 线程 B
synchronized (LOCK_B) { count++; }
```

**错误原因：** 两边虽然都写了 `synchronized`，但互斥的单位是**同一个监视器对象**。A 用 `LOCK_A`，B 用 `LOCK_B`，它们可以同时进入各自的临界区。

`ReentrantLock` 也一样：所有竞争线程必须使用**同一个锁实例**来保护同一份共享数据。

## 2. 动画：等待队列、重入计数和非公平插队

先选择「锁竞争」模式，跟着 A 持锁、B 入队、A 解锁、B 重新获取；再尝试「可重入」和「非公平插队」。

<StepLab :lab="aqsLab" />

## 3. AQS 管理哪些东西？

可以先记住三件事，不必马上硬背全部节点字段：

| 组成 | 直观理解 | 与 ReentrantLock 的关系 |
|---|---|---|
| `state` | 一个整型同步状态 | 独占锁中常表示持有/重入次数，`0` 通常为空闲。|
| 等待队列 | 抢不到资源的人登记排队 | 获取失败的线程可能入队、阻塞，等待后续唤醒。|
| 获取/释放模板 | 不同同步器共用排队唤醒机制 | 由具体同步器规定 `tryAcquire` / `tryRelease` 等尝试逻辑。|

AQS 的核心不是一个“谁先排队谁一定先拿到锁”的万能队列。它通过状态检查、原子更新、队列和 `park/unpark` 等机制协调竞争者。

### 3.1 一个简化的独占获取过程

```text
线程 B 想 lock()
  ↓
尝试获取锁（tryAcquire）
  ├─ 成功 → 进入临界区
  └─ 失败 → 进入 AQS 等待队列
               ↓
           根据条件等待 / park
               ↓
        被通知或其他原因返回
               ↓
        再次检查获取条件
               ├─ 成功 → 进入临界区
               └─ 失败 → 继续等待 / 重试
```

这里的 `park` 可能被唤醒，也可能出现允许的**无理由返回**，所以等待方需要**循环检查条件**。不能把 `unpark` 简化成“精准地把锁所有权交给 B”。

### 3.2 为什么叫“可重入”？

```java
ReentrantLock lock = new ReentrantLock();
lock.lock(); // 第一次：当前线程获得锁，计数 1
lock.lock(); // 第二次：同一线程再次获得，计数 2
try {
    // 只有当前线程能进入的工作区
} finally {
    lock.unlock(); // 计数减为 1
    lock.unlock(); // 计数减为 0，完全释放
}
```

**同一个线程**重复获取自己的锁不会因为自己的锁而阻塞；但每次成功 `lock()` 都必须有对应的 `unlock()`，否则锁可能永远不释放。

实际业务不要手工到处配对两次，尽量把每次获取与释放放到清楚的 `try/finally` 生命周期内。

## 4. 公平锁和非公平锁到底差在哪？

```java
ReentrantLock nonfair = new ReentrantLock();     // 默认非公平
ReentrantLock fair = new ReentrantLock(true);    // 选择公平策略
```

- **非公平**：可能允许新到的线程趁锁刚释放时先拿到锁，即使已有等待者；这叫 barging（插队）。
- **公平**：通常会优先考虑等待时间更久的竞争者；但不保证操作系统按理想顺序调度，更不能声称任何 API 调用都绝对 FIFO。
- 例如无超时的 `tryLock()` 在公平锁上也可以立即获取可用锁，而不严格遵循公平等待顺序——这是 API 的明确语义。

::: warning 常见误区：AQS 队列是 FIFO，所以 ReentrantLock 必须先来先得？

不对。等待队列有顺序，并不代表每次**锁获取**都严格按顺序成功。非公平锁允许竞争插队；即使公平策略也受具体 API 与调度影响。把“队列次序”和“拿锁顺序”区分开。
:::

## 5. Java 8 / 17 可运行例子：一把锁保护 count

```java
import java.util.concurrent.locks.ReentrantLock;

public class ReentrantLockDemo {
    private static final ReentrantLock LOCK = new ReentrantLock();
    private static int count = 0;

    static void add() {
        LOCK.lock();
        try {
            count++; // 整个读—加—写都在锁里
        } finally {
            LOCK.unlock(); // 即使发生异常，也必须释放
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Thread a = new Thread(ReentrantLockDemo::add, "A");
        Thread b = new Thread(ReentrantLockDemo::add, "B");
        a.start();
        b.start();
        a.join();
        b.join();
        System.out.println(count); // 2
    }
}
```

为什么结果是 `2`？

1. 同一个 `LOCK` 实例保护两次操作。
2. A 或 B 先拿锁都无所谓；**另一个必须等待已经持锁的线程释放**。
3. 两次受保护的递增最终都会执行一次。
4. 主线程通过 `join()` 等两者结束，再观察结果。

`lock()` 遇到竞争时的阻塞与唤醒，不需要业务自己写一个 `while(true)` 狂转。注意 `ReentrantLock` 也提供 `lockInterruptibly()`、`tryLock()`、`Condition` 等能力；不同方法的等待和中断语义有差别。

## 6. AQS 与 synchronized 有什么区别？

| 角度 | `synchronized` | `ReentrantLock` |
|---|---|---|
| 基础实现 | JVM 监视器机制 | Java 类库同步器，内部依赖 AQS 等机制 |
| 释放方式 | 退出同步块自动释放 | 通常必须在 `finally` 手动 `unlock()` |
| 可重入 | 支持 | 支持 |
| 可中断地等待锁 | 没有同样形式的直接 API | 有 `lockInterruptibly()` |
| 定时尝试锁 | 没有直接对应形式 | 有 `tryLock(timeout, unit)` |
| 公平策略选择 | 没有公开构造参数 | 可用 `new ReentrantLock(true)` |

不要把 `synchronized` 说成“永远很慢”，也不要说 `ReentrantLock` 一定更快。**性能和可控性取决于具体竞争方式、JDK 实现和业务场景。**

## 7. 边界和面试常见陷阱

- **“B 被唤醒等于 B 直接持有锁”**：错误。它仍需再次满足获取条件。
- **“state=0/1 是 AQS 在所有子类的唯一含义”**：错误。`Semaphore`、`CountDownLatch` 等同步器对 state 的解释不同。
- **“AQS 只适合独占锁”**：错误。它还支持共享获取模式，某些同步器使用共享模式。
- **“公平锁完全杜绝饥饿或严格保证 FIFO”**：过度承诺。公平锁偏向排队者，但具体 API 与系统调度仍有边界。
- **“unlock 可以少写一次”**：错误。重入次数要匹配，否则会一直持锁。
- **“用两个不同锁保护一个变量也安全”**：错误。所有修改路径要遵循同一互斥规则。

## 8. 面试怎么回答？

**面试官：AQS 是什么？**

> AQS 是 Java 并发包里构建同步器的基础框架。它维护同步状态，并提供等待队列、线程阻塞与唤醒的公共机制；具体同步器实现尝试获取或释放状态的逻辑。`ReentrantLock` 可以借助 AQS 实现独占锁及其排队等待行为。

**追问：抢不到 ReentrantLock 会发生什么？**

> 线程先尝试获取锁；失败后可能加入 AQS 等待队列，根据条件阻塞。持锁者释放时会触发相应唤醒，等待线程醒来后还要重新检查并竞争锁，不是直接被分配锁。

**追问：为什么 ReentrantLock 可重入？**

> 锁记录当前独占持有线程和同步状态。相同线程再次获取时可以增加重入计数；解锁逐次减少，直到计数归零才完全释放。

## 9. 自测：叫醒了是否等于拿到了？

<KnowledgeQuiz :questions="aqsQuiz" />

### 本章检查点

- [ ] 能解释 AQS 的 state、队列、获取/释放三个作用。
- [ ] 能画出竞争失败 → 入队 → 等待 → 唤醒 → 再竞争的过程。
- [ ] 能解释 state=2 对可重入锁的意义。
- [ ] 会写 `lock(); try { ... } finally { unlock(); }`。
- [ ] 不混淆 FIFO 等待队列和公平锁实际获取顺序。

**上一节：** [CAS 与 ABA](/java/concurrency/cas-aba)  
**下一节：** [线程池 execute() 全流程](/java/concurrency/thread-pool)

### 规范参考

- [JDK 17 AbstractQueuedSynchronizer API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/locks/AbstractQueuedSynchronizer.html)
- [JDK 17 ReentrantLock API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html)
