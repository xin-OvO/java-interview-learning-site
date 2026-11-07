"""只生成免安装预览壳；正式内容维护在 docs/ Markdown + Vue。"""
import json, html
from pathlib import Path
root=Path(__file__).resolve().parent.parent
st=json.loads((root/'content-status.json').read_text())
total=sum(len(m['chapters']) for m in st['modules'])
ready=sum(c['status']=='ready' for m in st['modules'] for c in m['chapters'])
items=[]
for m in st['modules']:
  n=sum(c['status']=='ready' for c in m['chapters'])
  items.append(f'<div class="module"><span class="priority">{m["priority"]}</span><span>{html.escape(m["title"])}</span><small>{n}/{len(m["chapters"])}</small></div>')
modules='\n'.join(items)
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>互动教材：项目结构预览</title><style>
:root{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;color:#162b42;background:#f4f7fb}*{box-sizing:border-box}body{margin:0}.head{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#10253a;color:white;padding:17px 26px}.head strong{font-size:16px}.head span{font-size:12px;color:#a1e8dd}.layout{display:grid;grid-template-columns:260px 1fr;min-height:calc(100vh - 58px)}aside{background:#fff;border-right:1px solid #dbe5ee;padding:22px 15px}.kicker{font-size:11px;font-weight:800;letter-spacing:.08em;color:#7790a8;margin:0 10px 10px}.module{display:flex;align-items:center;gap:8px;padding:10px 11px;border-radius:9px;font-size:13px;color:#43576a}.module small{margin-left:auto;color:#7895a5}.module:nth-of-type(2){background:#e7f7f3;color:#057e68;font-weight:800}.priority{background:#eef2f6;padding:3px 5px;border-radius:5px;font-size:10px;color:#677d8d}main{min-width:0;padding:22px;max-width:1400px;width:100%;margin:0 auto}.notice{background:#ecfaf6;border:1px solid #b9e6da;border-radius:12px;padding:17px 19px;font-size:14px;line-height:1.8}.notice strong{color:#087d6c}.notice p{margin:6px 0 0;color:#426179}.header{margin:18px 0;display:flex;align-items:center;justify-content:space-between;gap:12px}.header h1{font-size:22px;margin:0}.stats{font-size:12px;color:#648092}.frame{border:1px solid #dce5ed;border-radius:14px;overflow:hidden;background:white;box-shadow:0 10px 35px rgba(22,41,64,.08)}iframe{border:0;width:100%;height:970px;display:block}.footer{font-size:12px;color:#7790a8;margin:14px 0 18px}@media(max-width:900px){.layout{grid-template-columns:1fr}aside{display:none}.head{padding:15px}main{padding:12px}iframe{height:900px}.header h1{font-size:18px}}
</style></head><body><div class="head"><strong>☕ Java 后端 · 互动知识手册</strong><span>单一项目 · 渐进更新</span></div><div class="layout"><aside><div class="kicker">全书目录 · 可阅读章节</div>MODULES</aside><main><div class="notice"><strong>免安装结构预览</strong><p>下方嵌入此前已完成的 JMM 独立动画，演示统一网站的课程入口。正式课程正文位于 <code>docs/java/concurrency/jmm-happens-before.md</code>，动画已改为可复用的 Vue 组件；打开正式 VitePress 网站才是以后逐章扩展的完整样式。此页仅供不安装 npm 时快速查看，不是第二套需要维护的教材。</p></div><div class="header"><h1>第一课 · JMM 与 happens-before</h1><span class="stats">已可读 READY / TOTAL · 其余继续补充</span></div><div class="frame"><iframe loading="eager" title="JMM 交互动画旧版归档" src="docs/public/legacy/jmm-original.html"></iframe></div><div class="footer">正式项目：运行 npm install && npm run dev；导航会按 content-status.json 自动加入新章节。</div></main></div></body></html>'''
page=page.replace('MODULES',modules).replace('READY',str(ready)).replace('TOTAL',str(total))
(root/'PREVIEW.html').write_text(page,encoding='utf-8')
print(root/'PREVIEW.html')
