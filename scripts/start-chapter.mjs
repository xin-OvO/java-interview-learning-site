import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
const root=resolve(import.meta.dirname,'..');
const key=process.argv[2];
if (!key) { console.error('用法：npm run start:chapter -- java/concurrency/volatile-atomicity'); process.exit(1) }
const file=join(root,'content-status.json');
const state=JSON.parse(readFileSync(file,'utf8'));
const chapter=state.modules.flatMap(m=>m.chapters).find(c=>c.path===key);
if (!chapter) { console.error(`进度文件中没有路径：${key}`); process.exit(1) }
const dest=join(root,'docs',key+'.md');
if (existsSync(dest)) { console.error(`文件已经存在，拒绝覆盖：${dest}`); process.exit(1) }
mkdirSync(dirname(dest),{recursive:true});
const title=chapter.title;
const template=`---\ntitle: ${title}\n---\n\n# ${title}\n\n> 初稿：请按 AGENTS.md 的标准逐节完善。没有足够讲解之前，保持 draft 状态。\n\n## 30 秒先懂\n\n用容易理解的话说明：这个知识点到底要解决什么问题？\n\n## 一个真实问题\n\n给出能复现或推演的 Java 8/17 示例。\n\n## 动手演示\n\n在 docs/components/ 中添加可复用 Vue 动画，按步骤解释每次读/写变化。\n\n## 严格原理\n\n从 Java 规范和源码机制严谨解释，区分不同版本。\n\n## 常见误区\n\n指出最容易记错、最容易混淆的结论。\n\n## 面试回答\n\n给出可以口述的完整回答和可能追问。\n\n## 自测\n\n提供至少一道需要真正理解才答得对的题目。\n`;
writeFileSync(dest,template,'utf8');
chapter.status='draft';
state.updated=new Date().toISOString().slice(0,10);
writeFileSync(file,JSON.stringify(state,null,2)+'\n','utf8');
execFileSync(process.execPath,[join(root,'scripts/sync-progress.mjs')],{stdio:'inherit'});
console.log('已建立章节草稿',dest);
