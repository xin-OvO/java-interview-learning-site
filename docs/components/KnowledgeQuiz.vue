<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ questions: { type:Array, required:true } })
const index = ref(0)
const selected = ref(-1)
const current = computed(() => props.questions[index.value])
function choose(i) { selected.value = i }
function next() { index.value = (index.value+1) % props.questions.length; selected.value = -1 }
</script>

<template>
  <section class="knowledge-quiz" aria-label="章节理解测试">
    <div class="knowledge-quiz-header"><strong>理解测试</strong><span>第 {{ index+1 }} / {{ questions.length }} 题</span></div>
    <p class="knowledge-quiz-question">{{ current.question }}</p>
    <div class="knowledge-quiz-choices">
      <button v-for="(choice,i) in current.choices" :key="i" type="button"
        :class="{ chosen: selected===i, correct: selected>=0 && current.correct===i }"
        :aria-pressed="selected===i" @click="choose(i)">{{ 'ABCD'[i] }}. {{ choice }}</button>
    </div>
    <div v-if="selected>=0" class="knowledge-quiz-answer" aria-live="polite">
      <strong>{{ selected===current.correct ? '✓ 答对了' : '答案：' + 'ABCD'[current.correct] }}</strong>
      <p>{{ current.explanation }}</p>
      <button type="button" @click="next">{{ index===questions.length-1 ? '再测一次 ↺' : '下一题 →' }}</button>
    </div>
  </section>
</template>
