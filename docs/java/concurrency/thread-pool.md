---
title: ThreadPoolExecutor · execute() 任务去向全流程
outline: deep
---

<script setup>
import StepLab from '../../components/StepLab.vue'
import KnowledgeQuiz from '../../components/KnowledgeQuiz.vue'
import poolLab from '../../components/thread-pool-lab.json'
import poolQuiz from '../../components/thread-pool-quiz.json'
</script>

# 线程池 execute()：为什么有时排队，有时创建线程，有时拒绝？

<p class="lead">想象一家餐厅：固定有一位厨师（核心线程），门口只有一个等候位（有界队列），生意太忙还能临时请一位厨师（扩展线程）。当厨师和等候位都满了，新来的订单会怎样？这就是 <code>ThreadPoolExecutor.execute()</code> 处理任务的核心问题。</p>

::: tip 30 秒速懂

`ThreadPoolExecutor` 的典型 `execute(task)` 路线：

1. **工作线程数少于 corePoolSize**：先尝试创建核心工作线程执行任务。
2. **否则**：线程池还在运行时，尝试把任务放入工作队列。
3. **队列放不进去**：尝试在 `maximumPoolSize` 上限内创建更多线程。
4. **已经无法接收**：执行拒绝策略。

所以：**不是“任务一来就先扩容到 maximumPoolSize”**；通常先达到核心线程数，再排队，队列满了才考虑扩容。
:::

## 1. 反例：明明 max=100，为什么只有 2 个线程忙？

```java
ExecutorService pool = new ThreadPoolExecutor(
        2, 100, 30, TimeUnit.SECONDS,
        new LinkedBlockingQueue<Runnable>());
```

不少人以为这个线程池在 2 个线程忙不过来时会自动创建 100 个线程。**通常不会**：这里无参 `LinkedBlockingQueue` 的容量是 `Integer.MAX_VALUE`，任务优先排队，`offer()` 一般不会因为业务积压而失败。除非出现极端条件，线程池很难走到“队列满，扩容到 max”那条分支。

后果是：**队列可能越来越长，占用内存，而不是自动扩容把积压消化掉。** 这也是生产系统常见的线程池误配置。

## 2. 交互流程：分别模拟有界、无界和关闭

点“有界队列”中的四个提交步骤，看 T1、T2、T3、T4 分别去了哪里。然后切换“无界队列”，观察 `max` 为什么长期发挥不了作用。

<StepLab :lab="poolLab" />

## 3. execute() 到底按什么条件判断？

下面是用中文缩写的**控制流程**，不是对特定 JDK 源码逐字复制：

```text
                       execute(task)
                             │
                  workerCount < core ?
                      ┌──────┴───────┐
                     是              否
                      ↓              ↓
             addWorker(task)   pool 运行中 && queue.offer(task) ?
                   │                 ├─ 是 → 二次检查池状态 / worker 数
                   └─ 成功返回       │        ├─ 已 shutdown 且能移除任务 → reject
                                     │        └─ 无 worker → 尝试启动 worker
                                     └─ 否 → addWorker(task, 非核心上限 max)
                                                   ├─ 成功 → 执行任务
                                                   └─ 失败 → reject
```

为什么**入队成功以后还要重新检查线程池状态**？因为入队的一瞬间池可能从 RUNNING 变成 SHUTDOWN。`execute()` 并不能只依据入队前看到的状态，决定这个任务一定已被合法接收。

还有一种细节：任务排队成功但工作线程数量为 `0` 时，要尝试启动一个没有首任务的 worker 去消费队列；否则任务可能一直没人取。

### 3.1 这五个参数分别负责什么？

| 参数 | 通俗理解 | 容易答错的地方 |
|---|---|---|
| `corePoolSize` | 核心工作线程数量阈值 | 默认不一定在创建线程池时就立刻建好。|
| `maximumPoolSize` | 线程数的总上限 | **包括核心线程**，不是“额外线程数量”。|
| `workQueue` | 放不下当前直接执行的任务先排队 | 队列容量直接改变扩容与拒绝路径。|
| `keepAliveTime` | 非核心空闲线程等待任务的超时时间 | 默认主要约束超出核心数的空闲线程；可设置允许核心超时。|
| `RejectedExecutionHandler` | 接不下新任务时如何处理 | 拒绝不一定会抛异常，取决于策略。|

### 3.2 四种标准拒绝策略

| 策略 | 行为 | 风险 |
|---|---|---|
| `AbortPolicy` | 抛 `RejectedExecutionException` | 调用方没处理可能导致请求失败。|
| `CallerRunsPolicy` | **在未关闭等条件满足时**，由提交线程直接运行任务 | 能形成背压，但阻塞提交线程，甚至拖慢 HTTP 请求线程。|
| `DiscardPolicy` | 静默丢弃被拒绝的任务 | 无感知丢任务，业务风险高。|
| `DiscardOldestPolicy` | 尝试丢弃队头任务，再提交当前任务 | 可能丢旧任务；关闭、持续满载等情况须额外考虑。|

::: warning 特别注意：CallerRunsPolicy 不是绝对不丢任务

标准 `CallerRunsPolicy` 在执行器**未关闭**时，才由调用线程运行任务。如果执行器已经关闭，它不会帮你执行这个任务。所以绝不能把它写成“所有拒绝任务都能被主线程兜底执行”。
:::

## 4. 一段可以稳定看到「入队 → 扩容 → 拒绝」的 Java 代码

下面为 **Java 8 / Java 17** 可运行示例。两个执行中的任务故意等待门闩，因此输出的**拒绝结果是稳定可复现的**（普通日志打印先后不依赖固定线程调度）。

```java
import java.util.concurrent.*;

public class PoolRouteDemo {
    public static void main(String[] args) throws InterruptedException {
        CountDownLatch release = new CountDownLatch(1);
        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                1, 2, 60, TimeUnit.SECONDS,
                new ArrayBlockingQueue<Runnable>(1),
                new ThreadPoolExecutor.AbortPolicy());

        Runnable blocker = () -> {
            try {
                release.await(); // T1、T3 一直忙，直到主线程放行
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        try {
            pool.execute(blocker);            // T1：创建核心 worker
            pool.execute(() -> {});            // T2：进队列
            pool.execute(blocker);             // T3：队列满，扩容 worker
            try {
                pool.execute(() -> {});        // T4：队列满、线程达到 max
                System.out.println("T4 accepted");
            } catch (RejectedExecutionException e) {
                System.out.println("T4 rejected"); // 稳定打印
            }
        } finally {
            release.countDown();
            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) {
                pool.shutdownNow();
            }
        }
    }
}
```

**输出关键行：** `T4 rejected`。

> 为什么 T2 不会抢先执行导致不同结果？T1 被门闩阻塞、单个核心 worker 在忙；T2 必须先占据容量 1 的队列；T3 再触发创建第二个 worker 并在门闩处等待。提交 T4 时队列和工作线程名额均已占满。

## 5. 线上如何选择线程池参数？

先看任务类型，再看阻塞时长、目标吞吐、延迟、下游承载能力、内存预算，而不是背一个固定的“CPU 核心数 × 2”。

- **CPU 密集型**：过多线程会增加上下文切换，通常从接近可用 CPU 数量的规模开始压测。
- **IO 等待明显**：线程数可能大于 CPU 数量，但必须同时考虑数据库连接池、HTTP 连接、Kafka Consumer 对象及下游限流能力。
- **短任务高流量**：队列必须有明确容量与饱和处理方式；排队时间也是延迟的一部分。
- **任务可能永久阻塞**：线程和队列容量再大也不能从根本上解决，需要超时、隔离、取消和监控。

需要持续监控 `getActiveCount()`、`getPoolSize()`、`getQueue().size()`、`getCompletedTaskCount()`、拒绝次数，以及任务排队时间。监控读数是**运行时快照**，不保证多个指标来自同一瞬间。

## 6. shutdown、shutdownNow、submit 与 execute

**`shutdown()`**：拒绝新任务，已经提交的任务仍有机会执行完成；不会等待它们结束。`awaitTermination()` 可以用于等待。

**`shutdownNow()`**：尝试中断正在运行的任务，返回尚未开始执行的排队任务列表；**不保证**能强制停止忽略中断的任务。

**`execute(Runnable)`**：提交一个没有结果的任务。饱和时 `AbortPolicy` 的拒绝异常从调用点抛出。任务自身抛异常会交给工作线程的异常处理机制。

**`submit(...)`**：返回 `Future`，可获得结果和异常；任务运行异常通常通过 `Future.get()` 的 `ExecutionException` 表现，不能以为“没看到工作线程日志 = 成功”。

## 7. 边界和误解

- **“线程池总是先创建 max 个线程”**：错。队列策略优先级很关键。
- **“无界队列不会 OOM”**：错。大量排队任务占用堆内存。
- **“maximumPoolSize 就是最大额外线程数”**：错，是工作线程总数上限。
- **“线程池已关闭还能加任务，只要队列有空间”**：错，会拒绝新提交。
- **“线程越多吞吐一定越大”**：错。下游连接数、CPU、锁竞争可能先成为瓶颈。
- **“任务超时就可以强制杀死线程”**：错。Java 中断是协作式机制，不保证任务立即退出。

## 8. 面试怎么回答？

**面试官：ThreadPoolExecutor.execute() 的流程？**

> 先看工作线程数是否小于 corePoolSize，是就尝试新增核心 worker；否则在线程池仍运行时尝试入队。入队成功需要二次检查池状态并确保至少有 worker 消费队列。入队失败再尝试在 maximumPoolSize 内扩容。扩容失败或不能接收时走拒绝策略。所以队列类型直接影响扩容路径。

**追问：设置 core=10、max=100，为什么线程数一直只有 10？**

> 如果使用默认容量很大的 LinkedBlockingQueue，超过核心数的任务通常直接排队，队列不满就不会触发新建非核心 worker 的分支。风险是积压和内存消耗，并非配置错了 max 数值本身。

**追问：你们生产为什么要使用有界队列？**

> 主要是为排队和内存设置上界，并在系统过载时让拒绝/背压策略及时暴露问题。具体容量、线程数要通过任务等待时间、目标吞吐和下游能力压测，而不是拍脑袋。

## 9. 自测：第四个任务为什么进不去？

<KnowledgeQuiz :questions="poolQuiz" />

### 本章检查点

- [ ] 能画出 core → queue → max → reject 的流程。
- [ ] 能解释为什么入队后仍要二次检查线程池状态。
- [ ] 能说出四种拒绝策略以及 `CallerRunsPolicy` 的边界。
- [ ] 会写有界队列和关闭线程池的代码。
- [ ] 能结合自己的业务解释队列积压、内存、连接数之间的关系。

**上一节：** [AQS 与锁](/java/concurrency/aqs)  
**下一节：** [ThreadLocal 与 CompletableFuture](/java/concurrency/thread-local)

### 规范参考

- [JDK 17 ThreadPoolExecutor API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)
- [JDK 17 ExecutorService API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/ExecutorService.html)
