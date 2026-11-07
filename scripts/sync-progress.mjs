import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
const root = resolve(import.meta.dirname,'..');
const obj = JSON.parse(readFileSync(join(root, 'content-status.json'),'utf8'));
const all = obj.modules.flatMap(x=>x.chapters);
const count = s=>all.filter(c=>c.status===s).length;
const lines = [
'<!-- 由 npm run status 根据 content-status.json 生成，请勿手动修改 -->',
'# 全书编写进度','',
'> 这是**同一本**不断扩充的交互式知识手册：只有“首版可阅读”才展示为正文，未写的不假装完成。','',
`**共 ${obj.modules.length} 个模块 / ${all.length} 个专题，首版可读 ${count('ready')}，初稿 ${count('draft')}，计划中 ${count('planned')}。**`,'',
`最后更新：${obj.updated}`,'',
'| 优先级 | 模块 | 章节 | 状态 |','|---|---|---|---|'
];
for (const m of obj.modules) {
 for (const c of m.chapters) {
  const chapter = c.status==='planned'?c.title:`[${c.title}](/${c.path})`;
  lines.push(`| ${m.priority} | ${m.title} | ${chapter} | ${obj.statusGuide[c.status]} |`);
 }
}
lines.push('', '## 下一步', '', '详细续写任务请参考项目根目录的 `NEXT.md`。需要下一次对话继续时，先给 AI 提供最新仓库或压缩包，并让它读取 `AGENTS.md`。', '');
writeFileSync(join(root,'docs','progress.md'),lines.join('\n'),'utf8');
console.log(`进度页已更新：首版 ${count('ready')}/${all.length}；初稿 ${count('draft')}；计划中 ${count('planned')}`);
