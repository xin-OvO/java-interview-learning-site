<script setup>
import { computed, ref } from 'vue'
import questions from './atomicity-questions.json'
const idx = ref(0)
const selected = ref(-1)
const current = computed(() => questions[idx.value])
const answered = computed(() => selected.value >= 0)
function advance() { if (idx.value === questions.length - 1) idx.value = 0; else idx.value++; selected.value = -1 }
</script>

<template>
  <section class="atomic-quiz" aria-label="volatile 与原子性理解测试">
    <div class="aq-heading"><strong>检验理解：3 道小题</strong><span>第 {{idx + 1}} / {{questions.length}} 题</span></div>
    <p class="aq-question">{{ current.question }}</p>
    <button v-for="(option, i) in current.choices" :key="idx + '-' + i" type="button" class="aq-option" :class="{ picked:selected===i, correct:answered&&i===current.correct }" :aria-pressed="selected===i" @click="selected = i"><b>{{ String.fromCharCode(65 + i) }}.</b> {{ option }}</button>
    <div v-if="answered" class="aq-feedback" role="status"><strong>{{selected===current.correct ? '✓ 回答正确' : '再对照动画看看，正确答案是 ' + String.fromCharCode(65 + current.correct) }}</strong><p>{{current.explanation}}</p><button type="button" @click="advance">{{idx===questions.length - 1 ? '重新做一轮 ↺' : '下一题 →'}}</button></div>
  </section>
</template>

<style scoped>
.atomic-quiz{border:1px solid var(--vp-c-divider);border-radius:14px;background:var(--vp-c-bg-soft);padding:20px;margin:18px 0}
.aq-heading{display:flex;justify-content:space-between;gap:10px;align-items:center}.aq-heading strong{font-size:15px}.aq-heading span{font-size:12px;color:var(--vp-c-text-2)}
.aq-question{font-size:14px;font-weight:700;margin:14px 0 12px;line-height:1.75}.aq-option{display:block;width:100%;text-align:left;margin:8px 0;padding:11px 12px;border:1px solid var(--vp-c-divider);border-radius:9px;background:var(--vp-c-bg);font-size:13px;line-height:1.7;cursor:pointer}.aq-option b{color:var(--vp-c-brand-1)}.aq-option.picked{border-color:var(--vp-c-brand-1);background:var(--vp-c-brand-soft)}.aq-option.correct{border-left:4px solid var(--vp-c-brand-1)}
.aq-feedback{border-radius:9px;border:1px solid var(--vp-c-divider);background:var(--vp-c-bg);padding:12px;margin-top:12px}.aq-feedback strong{font-size:14px;color:var(--vp-c-brand-1)}.aq-feedback p{font-size:13px;line-height:1.85;margin:6px 0 12px}.aq-feedback button{background:var(--vp-c-brand-1);color:var(--vp-c-bg);border:0;border-radius:8px;padding:8px 12px;font-size:12px;font-weight:700;cursor:pointer}@media(max-width:560px){.atomic-quiz{padding:12px}}
</style>
