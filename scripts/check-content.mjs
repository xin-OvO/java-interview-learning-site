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
