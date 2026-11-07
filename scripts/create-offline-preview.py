"""从同一本书的 Markdown/JSON 自动产生无依赖浏览器预览。

知识正文唯一来源为 docs/**/*.md，动画步骤/题目唯一来源为 docs/components/*.json。
生成的 PREVIEW.html 不能当成另一份课程源码进行手工维护。
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
state = json.loads((ROOT / 'content-status.json').read_text('utf8'))
chapters = [(module, chapter) for module in state['modules'] for chapter in module['chapters'] if chapter['status'] == 'ready']
all_ready = {ch['path'] for _, ch in chapters}
markdown = MarkdownIt('default', {'html': True, 'linkify': False}).enable('table')


def encoded_json(value):
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def render_body(chapter):
    path = chapter['path']
    if path == 'java/concurrency/jmm-happens-before':
        return ('<div class="legacy-note">第一章在离线版使用原有互动演示；VitePress 正式版以本项目中的 JMM Markdown 与 Vue 组件为准。</div>'
                '<iframe class="legacy-frame" loading="lazy" title="JMM happens-before 动态示范" '
                'src="docs/public/legacy/jmm-original.html"></iframe>')
    source = (DOCS / f'{path}.md').read_text('utf8')
    source = re.sub(r'\A---\n.*?\n---\s*\n', '', source, count=1, flags=re.S)
    # Vue setup 部分只是正式站点引用，离线版根据同名变量找动画 JSON。
    m = re.search(r'<script setup>(.*?)</script>', source, flags=re.S)
    imported = dict(re.findall(r"import\s+(\w+)\s+from\s+['\"]\.\./\.\./components/([^'\"]+\.json)['\"]", m.group(1) if m else ''))
    source = re.sub(r'<script setup>.*?</script>\s*', '', source, count=1, flags=re.S)

    def step_placeholder(m):
        var = m.group(1)
        filename = imported.get(var)
        if not filename or not (DOCS/'components'/filename).is_file():
            raise RuntimeError(f'{path}: StepLab 数据引用无效: {var}')
        key = filename.removesuffix('.json')
        labs[key] = json.loads((DOCS/'components'/filename).read_text('utf8'))
        return f'\n<div class="generic-lab" data-lab="{html.escape(key)}"></div>\n'

    def quiz_placeholder(m):
        var = m.group(1)
        filename = imported.get(var)
        if not filename or not (DOCS/'components'/filename).is_file():
            raise RuntimeError(f'{path}: KnowledgeQuiz 数据引用无效: {var}')
        key = filename.removesuffix('.json')
        quizzes[key] = json.loads((DOCS/'components'/filename).read_text('utf8'))
        return f'\n<div class="generic-quiz" data-quiz="{html.escape(key)}"></div>\n'

    source = re.sub(r'<StepLab\s+:lab="(\w+)"\s*/>', step_placeholder, source)
    source = re.sub(r'<KnowledgeQuiz\s+:questions="(\w+)"\s*/>', quiz_placeholder, source)
    if '<CounterRaceLab />' in source:
        labs['legacy-counter'] = json.loads((DOCS/'components/counter-scenarios.json').read_text('utf8'))
        source = source.replace('<CounterRaceLab />', '\n<div class="old-counter-lab"></div>\n')
    if '<AtomicityQuiz />' in source:
        quizzes['legacy-atomicity'] = json.loads((DOCS/'components/atomicity-questions.json').read_text('utf8'))
        source = source.replace('<AtomicityQuiz />', '\n<div class="generic-quiz" data-quiz="legacy-atomicity"></div>\n')

    # Markdown 扩展 ::: tip/warning/info => 离线提示框（与 VitePress 语义一致）。
    blocks = {}
    def replace_block(match):
        kind, title, content = match.group(1), match.group(2).strip(), match.group(3)
        token = f'OFFLINEBLOCKTOKEN{len(blocks)}'
        blocks[token] = f'<aside class="admon admon-{kind}"><strong>{html.escape(title or kind.upper())}</strong>{markdown.render(content)}</aside>'
        return f'\n\n{token}\n\n'
    source = re.sub(r'^::: (tip|info|warning|danger|details)([^\n]*)\n(.*?)^:::\s*$', replace_block, source, flags=re.M|re.S)

    def localize_link(match):
        slug = match.group(1)
        return f'](#{slug})' if slug in all_ready else f'](#not-ready)'
    source = re.sub(r'\]\(/([^\)]+)\)', localize_link, source)
    rendered = markdown.render(source)
    for token, block in blocks.items():
        rendered = rendered.replace(f'<p>{token}</p>', block).replace(token, block)
    return rendered

labs, quizzes = {}, {}
pages = []
for module, chapter in chapters:
    path = chapter['path']
    pages.append((path, module, chapter, render_body(chapter)))

# 同一导航拥有 6 章。导航名和顺序来自内容状态，不写死额外课程。
nav_html = ''.join(
    f'<div class="sidebar-group"><strong>{html.escape(m["priority"])} · {html.escape(m["title"])}</strong>' +
    ''.join(f'<button data-open="{html.escape(ch["path"])}">{html.escape(ch["title"])}</button>'
            for mm,ch in chapters if mm is m) + '</div>'
    for m in state['modules'] if any(mm is m for mm,_ in chapters)
)
ready = len(chapters)
total = sum(len(x['chapters']) for x in state['modules'])
initial = pages[-1][0]
sections = '\n'.join(
    f'<section id="{html.escape(path)}" class="chapter" data-title="{html.escape(ch["title"])}">'
    f'<div class="chapter-kicker">{html.escape(mod["title"])} · 第 {i+1} 节</div>{body}</section>'
    for i,(path,mod,ch,body) in enumerate(pages)
)

TEMPLATE = (ROOT/'scripts/offline-preview-template.html').read_text('utf8')
page = (TEMPLATE.replace('@@NAV@@', nav_html)
        .replace('@@SECTIONS@@', sections)
        .replace('@@READY@@', str(ready))
        .replace('@@TOTAL@@', str(total))
        .replace('@@INITIAL@@', encoded_json(initial))
        .replace('@@LABS@@', encoded_json(labs))
        .replace('@@QUIZZES@@', encoded_json(quizzes)))
(ROOT/'PREVIEW.html').write_text(page,encoding='utf8')
print(f"✓ PREVIEW.html：{ready} 章，{len(labs)} 组动画，{len(quizzes)} 组测验，{len(page)} 字符")
