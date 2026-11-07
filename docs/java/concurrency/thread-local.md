---
title: ThreadLocal 与 CompletableFuture · 线程复用和异步传参
outline: deep
---

<script setup>
import StepLab from '../../components/StepLab.vue'
import KnowledgeQuiz from '../../components/KnowledgeQuiz.vue'
import localLab from '../../components/threadlocal-future-lab.json'
import localQuiz from '../../components/threadlocal-future-quiz.json'
</script>

# ThreadLocal 与 CompletableFuture：为什么异步线程拿不到我的用户信息？

<p class="lead">做 Java 后端时，你可能把当前用户、traceId 等上下文放入 <code>ThreadLocal</code>，并在一个请求里随时读取。问题来了：<strong>线程池会复用工作线程，而 CompletableFuture 又可能把任务切到另一个线程。</strong>你放进去的值到底跟着“请求”走，还是跟着“线程”走？</p>

::: tip 30 秒速懂

- **ThreadLocal**：像每个工作人员自己的储物柜。线程 A 存的东西，线程 B 不会自动拿到；柜子属于**线程**，不属于一次请求。
- **线程池复用**：同一个工作人员可能连续处理两个用户。如果上一次忘记清理储物柜，下一次可能读到旧用户的数据。
- **CompletableFuture**：像把工作单交给别人去做。工作单可以携带**明确参数**，但不会自动搬走你自己柜子里的所有物品。

核心原则：**ThreadLocal 要 set / try / finally remove；异步业务上下文优先显式传参。**
:::

## 1. 反例：一个线程先处理 A，再处理 B

```java
static final ThreadLocal<String> USER = new ThreadLocal<>();

// 同一个线程池 worker 先执行任务 1
USER.set("用户 A");
// ...任务结束，却没有 remove()

// 同一个 worker 又执行任务 2
System.out.println(USER.get()); // 如果任务 2 没有先 set，可能读到「用户 A」
```

ThreadLocal **不是**“任务隔离变量”。它是“线程隔离变量”。只要线程池复用同一个工作线程，旧的 ThreadLocal 条目可能继续保留，造成**跨请求污染**，严重时会把 A 用户的上下文带入 B 的处理流程。

## 2. 动画：错误复用 → finally 清理 → 异步切线程

第一种场景看同一 worker 复用导致的错误；第二种看为什么 `remove()` 有用；第三种看主线程的 `ThreadLocal` 为什么不会自动传进 `CompletableFuture` 的异步线程。

<StepLab :lab="localLab" />

## 3. ThreadLocal 的数据到底存在哪里？

你可以先用下图建立**概念模型**：

```text
Thread-1 ──> ThreadLocalMap-1
                   └── (ThreadLocal USER) → "A"

Thread-2 ──> ThreadLocalMap-2
                   └── (ThreadLocal USER) → "B"
```

两个线程访问的**是同一个 `ThreadLocal` 对象**，但通过当前线程找到的映射不同。ThreadLocal 本身并不是装着一个共享的 `String` 字段，供线程去抢读写。

### 3.1 为什么可能出现内存泄漏？

在经典的 `ThreadLocalMap` 实现中，条目的 **key 持有 ThreadLocal 的弱引用**，而 **value 是强引用**：

```text
线程活着 ─→ ThreadLocalMap ─→ Entry
                              ├─ key: 弱引用 → ThreadLocal
                              └─ value: 强引用 → 大对象 / 用户上下文
```

假如业务丢掉了对 ThreadLocal 对象的其他强引用：

1. GC 可能清除弱引用的 key，让它变成 `null`。
2. **value 不会因此必然立刻释放**，因为它仍被 `ThreadLocalMap.Entry` 强引用。
3. 后续在 ThreadLocalMap 上的相关操作可能清理这些陈旧条目，但**不能依赖某个固定时间点自动清理**。
4. 在线程池里，线程生命周期长，因此滞留对象或旧上下文的危害更加明显。

即使 `ThreadLocal` 本身被声明为 `static final`，不会轻易丢失 key，**不 remove 也仍然可能导致跨任务数据污染、持有不再需要的对象**。所以清理不仅仅是防止“key 变 null”这一种问题。

## 4. 正确写法：try / finally / remove

```java
private static final ThreadLocal<String> USER = new ThreadLocal<>();

void handle(String userId) {
    USER.set(userId);
    try {
        doBusiness(); // 同一线程内可以 USER.get()
    } finally {
        USER.remove(); // 不论成功、失败，都执行清理
    }
}
```

注意这是**作用域约束**：所有进入这个上下文的入口都必须保证清理；而不是“创建了 ThreadLocal 就全局线程安全”。如果 `doBusiness` 内部切换到其他线程，那个线程不会自动继承这里的 USER 值。

## 5. CompletableFuture 为什么可能切换线程？

`CompletableFuture<T>` 可以表示一个将来完成的值，并用链式方法编排后续处理：

```java
CompletableFuture.supplyAsync(() -> queryUser(id), executor)
        .thenApply(user -> user.getName())
        .exceptionally(ex -> "fallback");
```

要分清楚几个常见方法：

| API | 作用 | 线程语义 |
|---|---|---|
| `supplyAsync(supplier, executor)` | 异步执行、有返回值 | 使用传入的 executor。|
| `runAsync(runnable, executor)` | 异步执行、无返回值 | 使用传入的 executor。|
| `thenApply(fn)` | 转换上一步结果 | 非 Async：可能由完成上一阶段的线程或其他调用线程执行，不要假定固定线程。|
| `thenApplyAsync(fn, executor)` | 用指定执行器安排转换 | 由 executor 执行；不保证每次创建新线程。|
| `thenCompose(fn)` | 把“返回 Future 的函数”展开成单层链 | 和 thenApply 的返回结构不同。|
| `thenCombine(other, fn)` | 合并两个 Future 的结果 | 通常等待二者都正常完成再执行合并函数。|
| `exceptionally(fn)` | 失败后的降级处理 | 处理异常完成结果；异常链路仍要考虑执行阶段。|
| `join()` / `get()` | 获取最终结果 | 都可能等待；异常包装与受检异常声明不同。|

没有显式传 `executor` 的 `*Async` 方法通常使用默认异步执行设施，常见是 `ForkJoinPool.commonPool()`；**不要依赖它一定在某个固定线程执行**，也不能当成“每提交一次就开一个新线程”。

### 5.1 为什么 ThreadLocal 不会自动跟着 CompletableFuture 跑？

```java
USER.set("张三"); // main 线程
CompletableFuture.supplyAsync(() -> USER.get(), executor);
```

异步任务可能在工作线程 W 上执行，W 查的是**自己的 ThreadLocalMap**。如果 W 没有对应值，`get()` 默认可能返回 `null`；如果 W 曾经残留旧值，可能读到**错误的旧值**。无论哪种，都不能假设它等于 main 线程刚设置的“张三”。

**推荐显式传递不可变业务参数：**

```java
String userId = USER.get(); // 在提交任务之前读取上下文
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> queryUser(userId), executor);
```

这样异步任务依赖什么数据，在参数里一目了然。如果确实要用上下文传播框架，也需要明确传播、恢复和清理规则，并注意线程池复用。

## 6. Java 8 / Java 17 可运行演示：线程池残留与异步传参

下面只用**一个固定工作线程**，确保它会复用，输出不会依赖线程池碰巧选择哪一个 worker。

```java
import java.util.concurrent.*;

public class ThreadLocalFutureDemo {
    private static final ThreadLocal<String> USER = new ThreadLocal<>();

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newSingleThreadExecutor();
        try {
            // 任务 A 留下线程上下文（错误示范）
            pool.submit(() -> USER.set("A")).get();
            System.out.println(pool.submit(() -> USER.get()).get()); // A

            // 清理同一个 worker 的映射
            pool.submit(() -> USER.remove()).get();
            System.out.println(pool.submit(() -> USER.get()).get()); // null

            // main 设置 USER，工作线程不会自动得到 main 的值
            USER.set("main-user");
            try {
                System.out.println(pool.submit(() -> USER.get()).get()); // null
                String userId = USER.get(); // 明确从 main 取参数
                CompletableFuture<String> future = CompletableFuture.supplyAsync(
                        () -> "hello, " + userId, pool);
                System.out.println(future.join()); // hello, main-user
            } finally {
                USER.remove();
            }
        } finally {
            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) pool.shutdownNow();
        }
    }
}
```

预期输出：

```text
A
null
null
hello, main-user
```

### 6.1 用 CompletableFuture 处理异常

```java
CompletableFuture<String> result = CompletableFuture
        .supplyAsync(() -> {
            throw new IllegalStateException("remote failed");
        }, pool)
        .thenApply(value -> "结果=" + value)
        .exceptionally(ex -> "降级结果");

System.out.println(result.join()); // 降级结果
```

要关注：`join()` 抛出的未处理异常通常是 `CompletionException` 之类的包装，`get()` 则使用 `ExecutionException` 等受检异常机制；不要误以为 `join()` 没有可能失败。

## 7. 常见误解与生产边界

- **“ThreadLocal 的值属于一次 HTTP 请求”**：错。它属于线程，不会自动按请求清理。
- **“线程池 worker 执行完任务就被销毁”**：错。通常会复用。
- **“ThreadLocal 的弱引用 key 使 value 必然被自动立即回收”**：错。value 仍可能被 Entry 强引用。
- **“CompletableFuture 会自动传播父线程的 ThreadLocal”**：错。普通 ThreadLocal 没这个保证。
- **“InheritableThreadLocal 能完美解决线程池传播”**：错。它主要发生在线程创建的继承阶段，线程池重用时容易出现陈旧上下文。
- **“thenApply 一定在主线程，thenApplyAsync 一定新建线程”**：都错。要区分阶段完成时机与执行器。
- **“异常只影响当前 Future，不需要监控”**：错。异步链上的异常若没有观察/处理，业务可能默默未完成预期流程。

## 8. 面试怎么回答？

**面试官：ThreadLocal 为什么在线程池里容易出问题？**

> ThreadLocal 的数据放在每个线程关联的 ThreadLocalMap 中。线程池会复用工作线程，一个任务的值不会随任务结束自动清理；后续任务如果忘了覆盖或清理，可能读到旧值。长期持有大对象还可能增加内存滞留。一般用 set / try / finally remove 确保任务范围结束就清理。

**追问：ThreadLocal 为什么可能造成内存泄漏？**

> 经典 ThreadLocalMap 的 Entry key 是弱引用，value 是强引用。key 可能被回收而 value 仍被 Entry 持有，直到相关清理操作发生。如果对应线程长期存活，就可能有较长时间的内存滞留；所以不能依赖 GC 代替 remove。

**追问：CompletableFuture 的 thenApply 和 thenApplyAsync 区别？**

> thenApply 不要求一定异步调度，可能由完成阶段的线程执行；thenApplyAsync 使用异步执行策略，可显式传 Executor 控制线程池。两者都不能自动保证普通 ThreadLocal 在跨线程时传播，业务参数最好显式传递。

## 9. 自测：上下文跟着谁走？

<KnowledgeQuiz :questions="localQuiz" />

### 本章检查点

- [ ] 解释 ThreadLocalMap 为什么是“每个线程自己的映射”。
- [ ] 能说出 value 为什么可能滞留及 `remove()` 的意义。
- [ ] 在单线程池写出残留值的稳定复现程序。
- [ ] 分清 `thenApply`、`thenApplyAsync`、`thenCompose`。
- [ ] 知道异步业务上下文应优先显式传参，而非假设 ThreadLocal 自动传播。

**上一节：** [线程池 execute() 全流程](/java/concurrency/thread-pool)  
**下一节（计划中）：** [JVM 堆栈与对象生命周期](/java/jvm/memory)

### 规范参考

- [JDK 17 ThreadLocal API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/ThreadLocal.html)
- [JDK 17 CompletableFuture API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/CompletableFuture.html)
