import { readFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
const root = resolve(import.meta.dirname, '..');
const config = JSON.parse(readFileSync(join(root, 'content-status.json'), 'utf8'));
const valid = new Set(['planned', 'draft', 'ready']);
const used = new Set();
const errors = [];
for (const module of config.modules) {
  for (const c of module.chapters) {
    if (!valid.has(c.status)) errors.push(`${module.id}/${c.path}: 未知状态 ${c.status}`);
    if (used.has(c.path)) errors.push(`${c.path}: 重复路径`);
    used.add(c.path);
    const filename = join(root, 'docs', `${c.path}.md`);
    if (c.status !== 'planned' && !existsSync(filename)) errors.push(`已开始章节缺失: ${filename}`);
    if (c.status === 'ready' && existsSync(filename)) {
      const txt = readFileSync(filename, 'utf8');
      if (txt.length < 1000) errors.push(`已完成内容过短: ${c.path}`);
      if (!/^##\s+(?:\d+\.\s*)?面试/m.test(txt)) errors.push(`章节缺少面试问答: ${c.path}`);
      if (!/^##\s+(?:\d+\.\s*)?自测/m.test(txt)) errors.push(`章节缺少自测: ${c.path}`);
      // 数据驱动动画：确认 Markdown 引用的每份 JSON 存在且具有有效场景与答案。
      const imports = [...txt.matchAll(/import\s+\w+\s+from\s+['"]\.\.\/\.\.\/components\/([^'"]+\.json)['"]/g)];
      for (const match of imports) {
        const file = join(root, 'docs/components', match[1]);
        if (!existsSync(file)) { errors.push(`${c.path}: 互动数据缺失 ${match[1]}`); continue; }
        try {
          const value = JSON.parse(readFileSync(file, 'utf8'));
          if (match[1].endsWith('-lab.json')) {
            if (!Array.isArray(value.modes) || !value.modes.length) throw Error('modes 不能为空');
            for (const mode of value.modes) {
              const frames = value.scenarios?.[mode.id];
              if (!Array.isArray(frames) || frames.length < 3) throw Error(`模式 ${mode.id} 少于 3 帧`);
              for (const f of frames) {
                if (!f.headline || !f.note || !Array.isArray(f.cards) || !f.cards.length)
                  throw Error(`模式 ${mode.id} 存在无解释的帧`);
              }
            }
          }
          if (match[1].endsWith('-quiz.json')) {
            if (!Array.isArray(value) || value.length < 1) throw Error('没有问题');
            for (const q of value) {
              if (!q.question || !q.explanation || !Array.isArray(q.choices) || q.choices.length < 2 ||
                  !Number.isInteger(q.correct) || q.correct < 0 || q.correct >= q.choices.length)
                throw Error('题目、选项或答案索引无效');
            }
          }
        } catch(e) { errors.push(`${c.path}: ${match[1]} 数据错误 ${e.message}`); }
      }
    }
  }
}
const total = [...used].length;
const ready = config.modules.flatMap(m => m.chapters).filter(c => c.status === 'ready').length;
if (errors.length) {
  errors.forEach(x => console.error('✗', x));
  process.exit(1);
}
console.log(`✓ ${config.modules.length} 模块 / ${total} 章节；${ready} 个可阅读首版；内容状态与文件一致`);
