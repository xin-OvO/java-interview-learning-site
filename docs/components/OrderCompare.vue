<script setup>
import { ref, computed } from 'vue'
const selected = ref(0)
const cases = [
 {a:['data = 42','ready = true'],b:['读取 ready','读取 data'],good:true,desc:'这是唯一能完整串起来的情况。假设 B 的 volatile 读观察到 true，且没有其他线程修改 data，就能保证 B 再读到 42。'},
 {a:['data = 42','ready = true'],b:['读取 data','读取 ready'],good:false,desc:'B 在获取 volatile 信号以前，就已经先读过 data。后面的 volatile 读无法“倒着”修复前面那次读取。data 可能是 0，也可能是 42。'},
 {a:['ready = true','data = 42'],b:['读取 ready','读取 data'],good:false,desc:'data 写在发布之后。B 即使已经看到 ready=true，也可能抢在线程 A 改 data 之前读取它。'},
 {a:['ready = true','data = 42'],b:['读取 data','读取 ready'],good:false,desc:'发布位置和读取位置都不合适。B 先读的 data 与 A 的后续修改之间没有需要的 happens-before 关系。'}
]
const c = computed(()=>cases[selected.value])
</script>
<template>
 <section class="order-lab" aria-label="四种代码读写顺序对比">
   <strong>点选顺序：四种写法，哪一种可以保证结果？</strong>
   <div class="order-tabs" role="group" aria-label="选择代码顺序">
     <button v-for="(x,i) in cases" :key="i" type="button" :class="{selected:selected===i}" @click="selected=i">情况 {{ i+1 }}{{ i===0?' ✓':'' }}</button>
   </div>
   <div class="order-columns">
     <div><h4>线程 A · 两次写入</h4><code v-for="(line,i) in c.a" :key="i" :class="{signal:line.includes('ready')}">{{i+1}}. {{line}}</code></div>
     <div><h4>线程 B · 两次读取</h4><code v-for="(line,i) in c.b" :key="i" :class="{signal:line.includes('ready')}">{{i+1}}. {{line}}</code></div>
   </div>
   <div class="order-feedback" :class="{pass:c.good}" aria-live="polite">
     <b>{{c.good?'✅ 能保证 data = 42':'⚠️ 不能保证 data = 42'}}</b>
     <p>{{c.desc}}</p>
   </div>
   <small class="order-note">统一前提：ready 是 volatile；B 所读取的 ready = true 来自 A 的这次写入；没有其他线程对 data 写入。若 B 读到 ready=false，不能套用“获取成功”的推理。</small>
 </section>
</template>
<style scoped>
.order-lab{border:1px solid var(--vp-c-divider);background:var(--vp-c-bg-soft);border-radius:16px;padding:20px;margin:24px 0}.order-lab>strong{font-size:15px}.order-tabs{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.order-tabs button{border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);padding:7px 11px;border-radius:8px;cursor:pointer;font-size:13px}.order-tabs button.selected{border-color:var(--vp-c-brand-1);background:var(--vp-c-brand-soft);color:var(--vp-c-brand-1);font-weight:700}.order-columns{display:grid;grid-template-columns:1fr 1fr;gap:12px}.order-columns>div{background:var(--vp-c-bg);border:1px solid var(--vp-c-divider);padding:12px;border-radius:10px;min-width:0}.order-columns h4{margin:0 0 10px;font-size:13px}.order-columns code{display:block;padding:9px;margin:6px 0;background:var(--vp-c-bg-soft);border-radius:6px;font-size:12px;white-space:normal;word-break:break-word}.order-columns code.signal{background:var(--vp-c-brand-soft);color:var(--vp-c-brand-1)}.order-feedback{border:1px solid var(--vp-c-divider);padding:12px;border-radius:10px;margin:14px 0;background:var(--vp-c-bg)}.order-feedback.pass{border-color:var(--vp-c-brand-2)}.order-feedback b{font-size:14px}.order-feedback p{font-size:13px;line-height:1.8;margin:8px 0 0}.order-note{font-size:12px;color:var(--vp-c-text-2);line-height:1.8;display:block}@media(max-width:570px){.order-lab{padding:13px}.order-columns{gap:8px}.order-columns>div{padding:8px}.order-columns code{font-size:11px}}
</style>
