#!/usr/bin/env python3
"""Create a private local episode brief from templates. Does not call YouTube APIs."""
import argparse, json, pathlib, re, sys
P = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description='Create an episode workspace with a human fact-check gate')
p.add_argument('--slug',required=True,help='lowercase letters, digits, hyphens')
p.add_argument('--title',required=True)
p.add_argument('--output',default='episodes')
a=p.parse_args()
if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a.slug):
    sys.exit('Invalid slug. Use lowercase letters/digits/hyphens.')
if not a.title.strip():sys.exit('Title required')
base=P/a.output/a.slug
if base.exists():sys.exit(f'Already exists: {base}; no overwrite')
base.mkdir(parents=True)
(base/'brief.md').write_text(f'''# {a.title}\n\n观众是谁：\n他遇到的问题：\n看完视频能做成的事：\n真实演示素材（自己的文件/屏录）：\n三条原始来源与核验日期：\n\n## 0–30 秒开场\n\n结果镜头：\n问题和承诺：\n\n## 完整操作分镜\n\n| 时间 | 画面 | 旁白 | 原始证据 |\n| --- | --- | --- | --- |\n| 00:00 | 实拍结果 | | |\n| 00:30 | 步骤 1 | | |\n\n## 发布前（必须由人确认）\n\n- [ ] 每个数字和案例有原始来源\n- [ ] 没有虚构收益/伪造截图/使用泄密账号\n- [ ] 第三方素材许可核查\n- [ ] 写实 AI 生成内容已核对披露规则\n- [ ] 测试标题/封面和实际视频对应\n- [ ] 描述与免费资源入口可打开\n- [ ] 无人观看也能给用户具体帮助\n''',encoding='utf-8')
(base/'metrics.csv').write_text('video_url,checked_at,hours_since_publish,impressions,ctr_pct,views,avg_view_duration_sec,retention_30s_pct,source,link_clicks,qualified_leads,paid_orders,notes\n',encoding='utf-8')
(base/'sources.json').write_text(json.dumps({'title':a.title,'claims':[],'verified_at':None},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(base/'script.md').write_text(f'# {a.title}\n\n## 00:00 真实结果\n\n## 00:10 观众问题\n\n## 00:30 操作第一步\n\n## 验证与边界\n',encoding='utf8')
(base/'description.md').write_text(f'# {a.title}\n\n完整版教学：\n免费资源：\n演示日期与版本：\n',encoding='utf8')
manifest={'title':a.title,'viewer_result':'请填入观众完成的实际结果',
          'owned_source_video':'source.mp4','script':'script.md','thumbnail':'thumbnail.png',
          'description':'description.md','source_claims':[],
          'review':{k:False for k in ('rights_checked','screen_privacy_checked','claims_reviewed',
          'audio_reviewed','thumbnail_true','links_tested','ai_disclosure_reviewed','paid_promotion_reviewed')}}
(base/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Created:',base)
print('NEXT: Add your owned source.mp4, thumbnail.png and verified claims; check human approval fields in manifest.json, then run scripts/check_episode.py')
