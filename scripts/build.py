#!/usr/bin/env python3
"""Build standalone guide pages + browser data from the reviewed JSON source of truth.
Only Python stdlib is required. No external requests or secrets.
"""
from __future__ import annotations
import html, json, os, pathlib, re
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'
DEFAULT_URL = 'https://aipmandy.github.io/HowToMakeMoneyOnYouTube/'
SITE_URL = os.getenv('SITE_URL', DEFAULT_URL).rstrip('/') + '/'

def load(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

def safe(x):
    return html.escape(str(x), quote=True)

def link(slug):
    return f'{SITE_URL}guides/{quote(slug)}/'

def guide_html(g):
    steps = '\n'.join(f'<li><label><input type="checkbox"> <span>{safe(step)}</span></label></li>' for step in g['steps'])
    schema = {'@context':'https://schema.org','@type':'HowTo', 'name':g['title'], 'description':g['overview'],
              'inLanguage':'zh-CN','step':[{'@type':'HowToStep','text':s} for s in g['steps']]}
    jsonld = json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')
    example = f'''<section class="article-panel"><h2>完整示例：本章怎样落地</h2><p>{safe(g.get('worked_example','请按本章步骤完成独立演示。'))}</p><h2>最容易失败的地方</h2><p>{safe(g.get('common_failure','缺少对观众结果的验证。'))}</p><h2>验收门槛</h2><p>{safe(g.get('verification','保留完成本章的原始证据。'))}</p></section>'''
    path = f'../../assets/style.css'
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe(g['title'])} · YouTube 不露脸赚钱教程</title>
<meta name="description" content="{safe(g['overview'][:140])}">
<link rel="canonical" href="{safe(link(g['id']))}"><link rel="stylesheet" href="{path}"><link rel="stylesheet" href="../../assets/youtube-theme.css">
<meta property="og:type" content="article"><meta property="og:title" content="{safe(g['title'])}"><meta property="og:description" content="{safe(g['overview'][:140])}">
<script type="application/ld+json">{jsonld}</script></head><body class="article-body">
<header class="site-header"><a class="brand" href="../../index.html"><span class="brand-mark">▶</span><strong>AI 酋长 Andy</strong><span class="brand-dot">/</span> YouTube 开源教程</a><a class="back" href="../../index.html#guides">返回全部指南 ↗</a></header>
<main class="article-shell"><p class="eyebrow">{safe(g['stage'])} · GUIDE {g['index']+1:02d}</p><h1>{safe(g['title'])}</h1><p class="article-lead">{safe(g['overview'])}</p>
<section class="article-panel"><h2>跟着做：逐步完成</h2><ol class="article-checks">{steps}</ol><p class="hint">这些勾选仅在当前页面有效；完整进度请在主页勾选并导出备份。</p></section>
{example}
<section class="article-panel"><h2>本章交付物</h2><p>{safe(g['deliverable'])}</p><h2>关键判断</h2><p>{safe(g['insight'])}</p></section>
<section class="article-panel"><h2>下一步</h2><p>回到主站打开 90 天任务表，完成本章后记录证据，而不是只做阅读打卡。</p><a class="button-primary" href="../../index.html#plan">继续执行 90 天计划 ↗</a></section>
<section class="article-panel article-contact"><h2>联系 AI 酋长 Andy</h2><p>个人微信：<strong>AIPMAndy</strong>（在微信搜索添加，备注「YouTube 教程」）</p><p>个人官网：<a href="https://metaver.vip/" target="_blank" rel="noopener noreferrer">metaver.vip ↗</a></p></section><footer class="article-foot">免费开源 · AI 酋长 Andy · <a href="https://github.com/AIPMAndy">GitHub</a> · <a href="https://metaver.vip/">个人官网</a> · 个人微信 AIPMAndy</footer></main></body></html>'''

def build():
    guides=load('guides.json'); cases=load('cases.json'); ideas=load('ideas.json'); plan=load('plan90.json'); sources=load('sources.json')
    payload={'guides':guides,'cases':cases,'ideas':ideas,'plan':plan,'sources':sources,'generated_at':load('meta.json')['content_updated_at'],'site_url':SITE_URL}
    js='/* Auto-generated from data/*.json; edit data, then run python scripts/build.py. */\nwindow.YT_DATA = '+json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')+';\n'
    (SITE/'assets'/'data.js').write_text(js,encoding='utf-8')
    for g in guides:
        d=SITE/'guides'/g['id']; d.mkdir(parents=True,exist_ok=True)
        (d/'index.html').write_text(guide_html(g),encoding='utf-8')
    stamp = load('meta.json')['content_updated_at']
    urls=[(SITE_URL,stamp,'weekly')]+[(link(g['id']),stamp,'monthly') for g in guides]
    x=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    x.extend(f'<url><loc>{safe(url)}</loc><lastmod>{stamp}</lastmod><changefreq>{freq}</changefreq></url>' for url,stamp,freq in urls)
    x.append('</urlset>')
    (SITE/'sitemap.xml').write_text('\n'.join(x)+'\n',encoding='utf-8')
    (SITE/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n',encoding='utf-8')
    (SITE/'llms.txt').write_text(f'# HowToMakeMoneyOnYouTube\n\nFree Chinese faceless YouTube tutorial by AI 酋长 Andy.\nHome: {SITE_URL}\nSource: https://github.com/AIPMAndy/HowToMakeMoneyOnYouTube\nPersonal website: https://metaver.vip/\nPersonal WeChat: AIPMAndy\n\nGuides:\n'+'\n'.join(f'- {g["title"]}: {link(g["id"])}' for g in guides)+'\n\nAll revenue claims require primary sources; no guaranteed earnings.\n',encoding='utf-8')
    print(f'Generated {len(guides)} searchable guides, {len(plan)} plan days, {len(urls)} URLs')

if __name__=='__main__': build()
