<script setup>
import { computed, ref } from 'vue'

// 教学动画只展示明确选定的概念路径，不模拟真实调度、CPU 缓存或线程状态采样。
const props = defineProps({ lab: { type: Object, required: true } })
const mode = ref(props.lab.modes[0]?.id || '')
const index = ref(0)
const currentMode = computed(() => props.lab.modes.find(m => m.id === mode.value))
const frames = computed(() => props.lab.scenarios[mode.value] || [])
const frame = computed(() => frames.value[index.value] || { cards: [] })
function select(id) { mode.value = id; index.value = 0 }
function reset() { index.value = 0 }
function previous() { index.value = Math.max(0, index.value - 1) }
function next() { index.value = index.value + 1 >= frames.value.length ? 0 : index.value + 1 }
</script>

<template>
  <section class="step-lab" :aria-label="lab.title">
    <header class="step-lab-head">
      <div><strong>{{ lab.title }}</strong><p>{{ lab.intro }}</p></div>
      <span aria-live="polite">{{ index + 1 }} / {{ frames.length }} 步</span>
    </header>
    <div class="step-lab-tabs" role="group" aria-label="切换实验场景">
      <button v-for="m in lab.modes" :key="m.id" type="button" :aria-pressed="mode === m.id"
        :class="{ active:mode===m.id }" @click="select(m.id)">{{ m.name }}</button>
    </div>
    <p class="step-lab-subtitle">{{ currentMode?.subtitle }}</p>
    <div class="step-lab-tiles" :key="mode + '-' + index">
      <article v-for="(card, i) in frame.cards" :key="i" :class="['step-lab-tile', { focus: i === frame.focus }]">
        <span class="step-lab-tile-label">{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <span class="step-lab-tile-detail">{{ card.detail }}</span>
      </article>
    </div>
    <div class="step-lab-timeline" aria-hidden="true">
      <span v-for="(_,i) in frames" :key="i" :class="{done:i<index,active:i===index}" />
    </div>
    <div class="step-lab-explain" aria-live="polite">
      <strong>{{ frame.headline }}</strong>
      <p>{{ frame.note }}</p>
      <pre v-if="frame.code"><code>{{ frame.code }}</code></pre>
    </div>
    <footer class="step-lab-controls">
      <button type="button" :disabled="index===0" @click="reset">↺ 重置</button>
      <div>
        <button type="button" :disabled="index===0" @click="previous">← 上一步</button>
        <button type="button" class="primary" @click="next">{{ index === frames.length-1 ? '重新演示 ↺' : '下一步 →' }}</button>
      </div>
    </footer>
    <p class="step-lab-footnote">{{ lab.footnote || '概念演示：展示一种合法过程，不是 CPU、JVM 或操作系统的实时监控。' }}</p>
  </section>
</template>
