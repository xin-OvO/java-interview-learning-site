<script setup>
import { computed, ref } from 'vue'

// 每一帧是人为挑选的合法执行交错，不是 CPU 缓存/字节码实时执行器。
import labData from './counter-scenarios.json'
const { modes, scenarios } = labData
const mode = ref('volatile')
const index = ref(0)
const frames = computed(() => scenarios[mode.value])
const frame = computed(() => frames.value[index.value])
const selection = computed(() => modes.find(item => item.id === mode.value))
const isFinished = computed(() => index.value === frames.value.length - 1)
function setMode(next) { mode.value = next; index.value = 0 }
function back() { index.value = Math.max(0, index.value - 1) }
function next() { index.value = isFinished.value ? 0 : index.value + 1 }
</script>

<template>
  <section class="counter-lab" aria-label="两个线程分别执行加一，逐步比较 volatile AtomicInteger synchronized">
    <div class="lab-top">
      <div><strong>双线程加一实验室</strong><p>手动一步一步执行，看共享计数器发生了什么</p></div>
      <span class="step-count">{{ index + 1 }} / {{ frames.length }} 帧</span>
    </div>
    <div class="mode-list" role="group" aria-label="选择并发实现方式">
      <button v-for="item in modes" :key="item.id" type="button" :class="{ chosen: mode === item.id }" :aria-pressed="mode === item.id" @click="setMode(item.id)">{{ item.name }}</button>
    </div>
    <div class="mode-caption">{{ selection.subtitle }}</div>
    <div class="board">
      <div class="worker" :class="{ spotlight: frame.actor === 'A' }">
        <div class="worker-name"><span class="worker-tag">A</span>线程 A <span v-if="frame.actor==='A'" class="playing">▶ 本步执行</span></div>
        <div class="worker-val"><small>{{ mode === 'atomic' ? '本次尝试 / 结果' : '自己的临时值' }}</small><strong>{{ frame.a }}</strong></div>
        <div class="worker-state">{{ frame.aState }}</div>
        <code class="worker-code" :class="{ visible: !!frame.codeA }">{{ frame.codeA || '等待下一步…' }}</code>
      </div>
      <div class="shared" :class="{ changed: index>0 && frame.value!==frames[index-1].value }">
        <small>共享计数器 count</small>
        <div class="count-number" aria-live="polite">{{ frame.value }}</div>
        <span v-if="mode==='volatile'">volatile int</span>
        <span v-else-if="mode==='atomic'">AtomicInteger</span>
        <span v-else>普通 int + 同一把锁</span>
        <div v-if="mode==='lock'" class="lock-state" :class="{ held:frame.lock!=='空闲' }">🔒 {{ frame.lock }}</div>
      </div>
      <div class="worker" :class="{ spotlight: frame.actor === 'B' }">
        <div class="worker-name"><span class="worker-tag b">B</span>线程 B <span v-if="frame.actor==='B'" class="playing">▶ 本步执行</span></div>
        <div class="worker-val"><small>{{ mode === 'atomic' ? '本次尝试 / 结果' : '自己的临时值' }}</small><strong>{{ frame.b }}</strong></div>
        <div class="worker-state">{{ frame.bState }}</div>
        <code class="worker-code" :class="{ visible: !!frame.codeB }">{{ frame.codeB || '等待下一步…' }}</code>
      </div>
    </div>
    <div class="frame-details" aria-live="polite">
      <div class="frame-title"><b>第 {{ index + 1 }} 步：{{ frame.actor ? `线程 ${frame.actor} · ` : '' }}{{ frame.action }}</b><span :class="{warning: mode==='volatile' && isFinished, success:mode!=='volatile'&&isFinished}">{{ isFinished ? `最终 count = ${frame.value}` : `当前 count = ${frame.value}` }}</span></div>
      <p>{{ frame.note }}</p>
    </div>
    <div class="timeline" role="group" aria-label="演示步骤进度">
      <button v-for="(_, i) in frames" :key="i" type="button" :class="{ done:i<index, now:i===index }" :aria-label="`跳到第 ${i+1} 步`" :aria-current="i===index ? 'step' : undefined" @click="index=i"><span class="sr-only">第 {{i+1}} 步</span></button>
    </div>
    <div class="lab-controls">
      <button type="button" @click="index=0" :disabled="index===0">↺ 重置</button>
      <div class="ctrl-right"><button type="button" @click="back" :disabled="index===0">← 上一步</button><button type="button" class="primary" @click="next">{{isFinished ? '重新演示 ↺' : '下一步 →'}}</button></div>
    </div>
    <p class="disclaimer">这是一条<strong>人为选定的合法线程交错路径</strong>，帮助理解“丢失更新”和修复机制；不是运行时监控，不代表 CPU 缓存变化，也不表示每次运行一定按此顺序执行。CAS 动画是概念模型，不等于 <code>incrementAndGet()</code> 在所有 JDK/CPU 上的逐条指令。</p>
  </section>
</template>

<style scoped>
.counter-lab{border:1px solid var(--vp-c-divider);border-radius:18px;background:var(--vp-c-bg-soft);padding:20px;margin:24px 0}
.lab-top,.lab-controls,.ctrl-right,.frame-title{display:flex;align-items:center;justify-content:space-between;gap:10px}
.lab-top strong{font-size:17px}.lab-top p{font-size:12px;color:var(--vp-c-text-2);line-height:1.7;margin:3px 0 0}
.step-count{font-size:12px;color:var(--vp-c-text-2);white-space:nowrap}
.mode-list{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 8px}
.mode-list button{padding:8px 11px;border-radius:9px;font-size:12px;border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);cursor:pointer;transition:.15s}
.mode-list button.chosen{background:var(--vp-c-brand-soft);border-color:var(--vp-c-brand-1);color:var(--vp-c-brand-1);font-weight:700}
.mode-caption{font-size:12px;color:var(--vp-c-text-2);margin-bottom:14px}
.board{display:grid;grid-template-columns:minmax(0,1fr) 142px minmax(0,1fr);gap:11px;align-items:stretch}
.worker,.shared{border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);border-radius:12px;padding:13px;min-width:0;transition:border-color .2s,background .2s,transform .2s}
.worker.spotlight{border-color:var(--vp-c-brand-1);background:var(--vp-c-brand-soft);transform:translateY(-2px)}
.worker-name{font-size:13px;font-weight:700;display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.worker-tag{background:#e0f2fe;color:#0b72af;border-radius:6px;padding:2px 6px;font-weight:800}.worker-tag.b{background:#ffedd5;color:#b45309}
.playing{font-size:10px;color:var(--vp-c-brand-1);font-weight:600}
.worker-val{margin:15px 0 7px;display:flex;flex-direction:column;gap:3px}.worker-val small,.shared small{font-size:11px;color:var(--vp-c-text-2)}.worker-val strong{font-size:21px;font-variant-numeric:tabular-nums}
.worker-state{font-size:12px;color:var(--vp-c-text-2);min-height:36px;line-height:1.5}
.worker-code{display:block;margin-top:9px;border-radius:6px;padding:8px 5px;min-height:40px;font-size:11px;word-break:break-word;white-space:normal;background:var(--vp-c-bg-soft);color:var(--vp-c-text-3);line-height:1.6}
.worker-code.visible{background:var(--vp-c-brand-soft);color:var(--vp-c-text-1)}
.shared{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:8px;background:linear-gradient(145deg,var(--vp-c-bg),var(--vp-c-brand-soft))}
.shared.changed{border-color:var(--vp-c-brand-1);box-shadow:0 0 0 2px var(--vp-c-brand-soft)}
.shared span{font-size:11px;color:var(--vp-c-text-2)}.count-number{font-size:52px;font-weight:800;line-height:1.05;color:var(--vp-c-brand-1);font-variant-numeric:tabular-nums}
.lock-state{border:1px solid var(--vp-c-divider);border-radius:20px;font-size:11px;padding:4px 8px}.lock-state.held{border-color:var(--vp-c-brand-1);color:var(--vp-c-brand-1)}
.frame-details{border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);margin-top:14px;padding:13px;border-radius:11px;min-height:123px}
.frame-title{align-items:flex-start}.frame-title b{font-size:14px}.frame-title span{font-size:12px;color:var(--vp-c-text-2);white-space:nowrap}.frame-title .warning{color:#b45309;font-weight:700}.frame-title .success{color:var(--vp-c-brand-1);font-weight:700}
.frame-details p{font-size:13px;line-height:1.85;margin:8px 0 0}
.timeline{display:flex;gap:5px;margin:15px 0}.timeline button{flex:1;height:10px;border-radius:99px;background:var(--vp-c-divider);border:0;cursor:pointer;min-width:3px;transition:.2s}.timeline button.done{background:var(--vp-c-brand-2);opacity:.45}.timeline button.now{background:var(--vp-c-brand-1)}
.lab-controls button{padding:8px 12px;border-radius:8px;border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);cursor:pointer;font-size:12px}.lab-controls button.primary{color:var(--vp-c-bg);background:var(--vp-c-brand-1);border-color:var(--vp-c-brand-1);font-weight:700}.lab-controls button:disabled{opacity:.4;cursor:not-allowed}
.disclaimer{font-size:11px !important;color:var(--vp-c-text-2);line-height:1.7 !important;margin:14px 0 0 !important}
@media(max-width:640px){.counter-lab{padding:12px}.board{grid-template-columns:1fr 1fr;gap:8px}.shared{grid-column:1/-1;grid-row:1;padding:10px}.shared .count-number{font-size:32px}.worker{padding:10px}.worker-val strong{font-size:18px}.worker-code{font-size:10px}.frame-title{flex-wrap:wrap}.lab-controls button{padding:8px}.lab-top strong{font-size:14px}}
@media(prefers-reduced-motion:reduce){.worker,.shared,.timeline button{transition:none}.worker.spotlight{transform:none}}
</style>
