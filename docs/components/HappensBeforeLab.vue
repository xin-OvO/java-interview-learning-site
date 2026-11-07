<script setup>
import { ref, computed } from 'vue'
const step = ref(0)
const steps = [
  { title:'初始状态', content:'data 从 0 开始，ready 从 false 开始。线程 A 与线程 B 尚未读写。' },
  { title:'A 先修改数据', content:'线程 A 执行 data = 42。这是普通写入，单靠这一步，线程 B 还没有跨线程可见性保证。' },
  { title:'A 再发布信号', content:'线程 A 执行 volatile ready = true。A 在它之前对 data 的写入，不能被移到这次 volatile 发布的后面，从而破坏发布语义。' },
  { title:'B 获取信号', content:'线程 B 读取 ready，观察到 true。此例的写/读建立 volatile 的同步关系，B 后续读取能看到 A 在发布前的修改。' },
  { title:'B 读取数据', content:'线程 B 再读取 data，得到 42。条件：没有其他线程再次修改 data。注意，这里靠的是 happens-before，不是因为 B 恰好晚几毫秒运行。' }
]
const s = computed(()=>steps[step.value])
</script>

<template>
  <section class="hb-lab" aria-label="happens-before 五步交互演示">
    <header class="hb-head"><strong>动手演示：先写数据 → 发布 → 获取 → 读数据</strong><span>第 {{ step + 1 }} / 5 步</span></header>
    <div class="hb-columns">
      <div class="hb-track">
        <div class="hb-track-head">线程 A · 负责写</div>
        <div class="hb-node" :class="{active: step===1, done:step>1}">
          <span class="hb-number">①</span>
          <code>data = 42</code>
          <small>{{ step >= 1 ? '已执行普通写入' : '等待执行' }}</small>
        </div>
        <div class="hb-arrow">↓ 程序顺序</div>
        <div class="hb-node" :class="{active: step===2, done:step>2}">
          <span class="hb-number">②</span>
          <code>ready = true</code>
          <small>{{ step >= 2 ? '已执行 volatile 写' : '等待发布' }}</small>
        </div>
      </div>
      <div class="hb-track">
        <div class="hb-track-head">线程 B · 负责读</div>
        <div class="hb-node" :class="{active:step===3, done:step>3}">
          <span class="hb-number">③</span>
          <code>if (ready)</code>
          <small>{{ step >= 3 ? '已读到 true' : '等待读取' }}</small>
        </div>
        <div class="hb-arrow">↓ 程序顺序</div>
        <div class="hb-node" :class="{active:step===4}">
          <span class="hb-number">④</span>
          <code>read(data)</code>
          <small>{{ step >= 4 ? '得到 42' : '等待读取' }}</small>
        </div>
      </div>
    </div>
    <div class="hb-bridge" :class="{established:step>=3}" aria-live="polite">
      <span>② volatile 写</span> <span class="hb-bridge-line">→</span> <span>③ volatile 读</span>
      <b>{{ step>=3 ? 'happens-before 已建立' : '尚未建立跨线程获取关系' }}</b>
    </div>
    <div class="hb-feedback" aria-live="polite"><div class="hb-step-title">{{ s.title }}</div><p>{{ s.content }}</p></div>
    <div class="hb-controls">
      <button type="button" @click="step=0" :disabled="step===0">↺ 重置</button>
      <div><button type="button" @click="step--" :disabled="step===0">上一步</button><button type="button" class="primary" @click="step = step < 4 ? step + 1 : 0">{{ step===4 ? '再看一次' : '下一步 →' }}</button></div>
    </div>
  </section>
</template>

<style scoped>
.hb-lab{border:1px solid var(--vp-c-divider);border-radius:16px;padding:20px;margin:22px 0;background:var(--vp-c-bg-soft)}
.hb-head,.hb-controls,.hb-controls>div{display:flex;align-items:center;justify-content:space-between;gap:10px}
.hb-head strong{font-size:15px}.hb-head span{font-size:12px;color:var(--vp-c-text-2);white-space:nowrap}
.hb-columns{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}
.hb-track{border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);padding:12px;border-radius:12px;min-width:0}
.hb-track-head{font-weight:700;font-size:13px;text-align:center;margin-bottom:10px}
.hb-node{display:flex;flex-direction:column;align-items:center;gap:2px;border:1px solid var(--vp-c-divider);border-radius:9px;padding:12px 6px;background:var(--vp-c-bg-soft);transition:.2s ease}
.hb-node.active{border-color:var(--vp-c-brand-1);box-shadow:0 0 0 3px var(--vp-c-brand-soft);transform:translateY(-1px)}
.hb-node.done{background:var(--vp-c-brand-soft);border-color:var(--vp-c-brand-2)}
.hb-number{font-size:12px;color:var(--vp-c-text-3)}
.hb-node code{font-weight:700;font-size:13px;white-space:nowrap}.hb-node small{font-size:11px;color:var(--vp-c-text-2);text-align:center}
.hb-arrow{height:33px;text-align:center;color:var(--vp-c-text-3);font-size:11px;line-height:33px}
.hb-bridge{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;border:1px dashed var(--vp-c-divider);border-radius:10px;padding:10px;margin-top:12px;font-size:12px}
.hb-bridge.established{border-color:var(--vp-c-brand-1);background:var(--vp-c-brand-soft)}
.hb-bridge-line{font-weight:700;color:var(--vp-c-brand-1)}.hb-bridge b{display:block;width:100%;text-align:center;font-size:11px;color:var(--vp-c-text-2)}
.hb-feedback{margin-top:14px;min-height:102px;border:1px solid var(--vp-c-divider);padding:13px 15px;background:var(--vp-c-bg);border-radius:10px}.hb-step-title{font-size:14px;font-weight:700;color:var(--vp-c-brand-1)}.hb-feedback p{font-size:13px;line-height:1.8;margin:5px 0 0}
.hb-controls{margin-top:14px}.hb-controls button{border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);border-radius:8px;padding:8px 12px;font-size:13px;cursor:pointer;min-height:36px}.hb-controls button.primary{background:var(--vp-c-brand-1);color:#fff;border-color:var(--vp-c-brand-1)}.hb-controls button:disabled{opacity:.4;cursor:not-allowed}
@media(max-width:600px){.hb-lab{padding:13px}.hb-columns{gap:8px}.hb-track{padding:7px}.hb-node code{font-size:11px}.hb-node{padding:8px 2px}}
</style>
