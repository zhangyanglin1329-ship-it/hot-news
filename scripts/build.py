#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
import json, html, re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
BASELINE = ROOT / 'template' / 'baseline.html'
ARCHIVE = ROOT / 'archive'
SECTORS = DATA / 'sectors.json'

def esc(s):
    return html.escape(str(s), quote=True)

def load_editions():
    out = {}
    for p in sorted(DATA.glob('20??-??-??.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        out[d['date']] = d
    return out

def source_body(story):
    body = story['body'].rstrip()
    src = story.get('source', '').strip()
    return body + (f'（来源：{src}）' if src else '')

def render_step(step):
    tone = step.get('tone', 'neutral')
    cls = ['step']
    if tone == 'up': cls.append('direction-up')
    elif tone == 'down': cls.append('direction-down')
    elif tone == 'key': cls.append('key-change')
    txt = step.get('text', '')
    ann = step.get('annotation')
    if ann and ann in txt:
        before, after = txt.split(ann, 1)
        inner = esc(before) + f'<span class="key-annotation">{esc(ann)}</span>' + esc(after)
    else:
        inner = esc(txt)
    return f'<span class="{" ".join(cls)}">{inner}</span>'

def render_story(story, first=False):
    time = esc(story.get('time',''))
    category = esc(story.get('category',''))
    status = story.get('status')
    left = [f'<span>{time}</span>', '<span class="meta-sep">·</span>', f'<span class="meta-type">{category}</span>']
    if status:
        left += ['<span class="meta-sep">·</span>', f'<span class="event-status">{esc(status)}</span>']
    imp = story['impact']
    rclass = 'good' if imp.get('direction') == 'good' else 'bad'
    result = f'{esc(imp.get("label",""))} · {esc(imp.get("sector",""))}'
    body = source_body(story)
    title = story.get('title','')
    label = story.get('commentary_label') or ('会员限免 · 投研拆解' if first else '投研拆解')
    chain = ''.join(render_step(s) for s in story.get('chain',[]))
    note = story.get('research_note')
    note_html = ''
    if note:
        note_html = (f'<div class="chain-research-note"><span class="chain-note-label">{esc(note.get("label",""))}</span>'
                     f'<span class="chain-note-text">{esc(note.get("text",""))}</span></div>')
    return (
      '<article class="story">'
      f'<div class="meta"><div class="meta-left">{"".join(left)}</div><div class="meta-result {rclass}">{result}</div></div>'
      f'<div class="quick-news" data-body="{esc(body)}" data-title="{esc(title)}">'
      f'<div class="quick-news-full"><span class="quick-news-title">【{esc(title)}】</span><span>{esc(body)}</span></div>'
      '<div class="quick-news-preview"><div class="quick-news-row quick-news-row1"></div><div class="quick-news-row quick-news-row2"></div>'
      '<div class="quick-news-row quick-news-row3"><div class="quick-news-row3-text"></div><button class="quick-news-more" type="button">查看更多</button></div></div>'
      '<button class="quick-news-collapse" type="button">收起</button></div>'
      '<section class="commentary">'
      f'<div class="commentary-label benefit-inline"><span class="benefit-v">V</span><span>{esc(label)}</span></div>'
      '<div class="chain-wrap">'
      f'<div class="chain-full">{chain}</div>'
      '<div class="chain-preview"><div class="chain-row chain-row1"></div><div class="chain-row chain-row2"><div class="chain-row2-text"></div><button class="chain-more" type="button">查看完整</button></div></div>'
      f'{note_html}<button class="chain-collapse" type="button">收起</button></div></section></article>'
    )

def render_main(edition):
    return '\n'.join(render_story(s, i == 0) for i,s in enumerate(edition['stories'])) + '\n<div aria-hidden="true" class="feed-tail"></div>'

def last7(latest):
    dt = datetime.strptime(latest, '%Y-%m-%d')
    return [(dt - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

def label_for_date(d):
    dt = datetime.strptime(d, '%Y-%m-%d')
    return f'{dt.month}月{dt.day}日'

def render_head(current, latest, editions):
    ed = editions[current]
    buttons = []
    for d in last7(latest):
        available = d in editions
        classes = 'edition-history-item' + (' is-current' if d == current else '')
        attrs = f' class="{classes}" data-date="{d}" type="button"'
        if not available:
            attrs += ' disabled aria-disabled="true"'
        mark = '<span class="edition-history-current">今日</span>' if d == latest else ''
        buttons.append(f'<button{attrs}><span>{esc(label_for_date(d))}</span>{mark}</button>')
    return (
      '<div class="edition-head"><div class="edition-left"><div class="edition-title">今日重点</div>'
      f'<div class="edition-meta"><button aria-expanded="false" aria-haspopup="true" class="edition-date-trigger" type="button">{esc(ed.get("label") or label_for_date(current))}</button>'
      f'<span class="edition-count"> · 精选 {len(ed["stories"])} 个近期重要事件</span></div></div>'
      f'<div class="edition-intro"><span class="edition-intro-label">本期导读</span><span class="edition-intro-text">{esc(ed.get("intro",""))}</span></div>'
      '<div aria-label="最近7天往期" class="edition-history-panel"><div class="edition-history-label">最近7天</div>'
      + ''.join(buttons) + '</div></div>'
    )

def render_templates(editions):
    return '\n'.join(f'<template id="edition-template-{d}">\n{render_main(ed)}\n</template>' for d,ed in sorted(editions.items(), reverse=True))

def edition_meta_js(editions):
    meta = {d:{'label':ed.get('label') or label_for_date(d),'count':f'· 精选 {len(ed["stories"])} 个近期重要事件','intro':ed.get('intro','')} for d,ed in editions.items()}
    return json.dumps(meta, ensure_ascii=False, separators=(',',':'))

def build_page(current, latest, editions, baseline):
    head_start = baseline.index('<div class="edition-head">')
    main_start = baseline.index('<main>', head_start)
    main_close = baseline.index('</main>', main_start) + len('</main>')
    script_start = baseline.index('<script>', main_close)
    prefix = baseline[:head_start]
    suffix = baseline[script_start:]
    # Keep all frozen CSS/JS from the baseline; update only edition data/date literal.
    suffix = re.sub(r"const EDITION_META=\{.*?\n\};", f'const EDITION_META={edition_meta_js(editions)};', suffix, count=1, flags=re.S)
    suffix = re.sub(r"if\(date==='\d{4}-\d{2}-\d{2}' && current\)", f"if(date==='{latest}' && current)", suffix, count=1)
    return (prefix + render_head(current, latest, editions) + '\n<main>\n' + render_main(editions[current]) + '\n</main>\n' +
            render_templates(editions) + '\n\n</div>\n' + suffix)

def main():
    editions = load_editions()
    latest = json.loads((DATA/'latest.json').read_text(encoding='utf-8'))['latest']
    if latest not in editions:
        raise SystemExit('latest edition missing')
    baseline = BASELINE.read_text(encoding='utf-8')
    sectors = set(json.loads(SECTORS.read_text(encoding='utf-8')))
    latest_stories = editions[latest]['stories']
    if not (5 <= len(latest_stories) <= 15):
        raise SystemExit(f'latest edition must contain 5-15 stories, got {len(latest_stories)}')
    invalid = [s['impact']['sector'] for s in latest_stories if s['impact']['sector'] not in sectors]
    if invalid:
        raise SystemExit(f'latest edition has non-whitelist sectors: {invalid}')
    ARCHIVE.mkdir(exist_ok=True)
    (ROOT/'index.html').write_text(build_page(latest, latest, editions, baseline), encoding='utf-8')
    for d in editions:
        (ARCHIVE/f'{d}.html').write_text(build_page(d, latest, editions, baseline), encoding='utf-8')
    print(f'built {len(editions)} editions; latest={latest}')

if __name__ == '__main__':
    main()
