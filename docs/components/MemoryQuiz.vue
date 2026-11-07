<script setup>
import { ref, computed } from 'vue'
const selected=ref(-1)
const options=[
  '只要 ready 是 volatile，data 在前还是在后都没区别',
  'A 先写 data 再写 ready；B 先读到 ready=true 再读 data，才形成所需的保证',
  'volatile 能让 count++ 变成一个不可分割的操作'
]
const result=computed(()=>selected.value===1)
</script>
<template>
<section class="quiz" aria-label="happens-before 理解测试">
 <div class="quiz-title">小测：下面哪句话正确？</div>
 <button v-for="(x,i) in options" :key="i" type="button" :class="{picked:selected===i}" @click="selected=i"><span>{{'ABC'[i]}}.</span>{{x}}</button>
 <div v-if="selected>=0" class="quiz-answer" aria-live="polite"><strong>{{result?'✅ 回答正确':'❌ 还差一点，正确选 B'}}</strong><p>要建立完整的 happens-before：普通写 data → volatile 写 ready → volatile 读 ready → 普通读 data。`volatile` 不能把 `count++` 自动变成原子操作。</p></div>
</section>
</template>
<style scoped>
.quiz{border:1px solid var(--vp-c-divider);border-radius:14px;padding:18px;margin:20px 0;background:var(--vp-c-bg-soft)}.quiz-title{font-size:16px;font-weight:700;margin-bottom:14px}.quiz>button{display:flex;gap:10px;align-items:flex-start;text-align:left;width:100%;padding:12px;margin:8px 0;background:var(--vp-c-bg);border:1px solid var(--vp-c-divider);border-radius:10px;font-size:13px;cursor:pointer;line-height:1.7}.quiz>button.picked{border-color:var(--vp-c-brand-1);background:var(--vp-c-brand-soft)}.quiz>button span{font-weight:700;color:var(--vp-c-brand-1)}.quiz-answer{padding:12px;background:var(--vp-c-bg);border-radius:9px;border:1px solid var(--vp-c-divider);margin-top:10px}.quiz-answer strong{font-size:14px}.quiz-answer p{font-size:13px;line-height:1.8;margin:7px 0 0}
</style>
