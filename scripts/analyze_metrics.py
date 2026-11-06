#!/usr/bin/env python3
"""Inspect normalized, manually entered YouTube results. No network calls or fake benchmarks.

Input template: templates/METRICS_INPUT.csv . All quantitative results require actual data.
"""
from __future__ import annotations
import argparse, csv, pathlib, statistics, sys

FIELDS = ('video_id','format','views','impressions','ctr_pct','video_duration_sec',
          'avg_view_duration_sec','retention_30s_pct','resource_clicks','qualified_leads',
          'paid_orders','net_revenue_cny','production_hours','traffic_source','time_window')
NUMBER_FIELDS = FIELDS[2:13]


def optional_number(row, key, line):
    s = row.get(key, '').strip()
    if s == '':
        return None
    try: v = float(s)
    except ValueError: raise ValueError(f'第 {line} 行 {key} 不是数字: {s!r}')
    if not 0 <= v < 1e15: raise ValueError(f'第 {line} 行 {key} 超出范围')
    if key.endswith('_pct') and v > 100: raise ValueError(f'第 {line} 行 {key} 应在 0..100')
    return v


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or set(FIELDS) - set(reader.fieldnames):
            raise ValueError('缺少字段: ' + ', '.join(sorted(set(FIELDS) - set(reader.fieldnames or []))))
        data = []
        for ln, row in enumerate(reader, 2):
            if not row['video_id'].strip(): raise ValueError(f'第 {ln} 行缺少 video_id')
            if row['format'] not in ('long', 'short'): raise ValueError(f'第 {ln} 行 format 只能 long/short')
            if row['time_window'] not in ('first7d','first30d','lifetime'): raise ValueError(f'第 {ln} 行 time_window 只能 first7d/first30d/lifetime')
            parsed = {k: optional_number(row, k, ln) for k in NUMBER_FIELDS}
            parsed.update(video_id=row['video_id'].strip(), format=row['format'],
                          traffic_source=(row['traffic_source'] or 'unknown').strip() or 'unknown',
                          time_window=row['time_window'])
            if parsed['avg_view_duration_sec'] is not None and parsed['video_duration_sec'] is not None:
                # Rewatch can exceed actual length; alert, don't claim invalid.
                pass
            data.append(parsed)
        if len({r['video_id'] for r in data}) != len(data):
            raise ValueError('一行代表一个视频及固定窗口；video_id 不得重复。请合并后再分析。')
        return data


def fmt(x, suffix='', digits=1): return '缺失' if x is None else f'{x:,.{digits}f}{suffix}'


def diagnose(row, cohort):
    issues = []
    impr, ctr = row['impressions'], row['ctr_pct']
    same = [x for x in cohort if x['format'] == row['format']
            and x['traffic_source'] == row['traffic_source']
            and x['time_window'] == row['time_window'] and x['video_id'] != row['video_id']]
    if row['format'] == 'long':
        if impr is None: issues.append('未填展示量：无法判断包装问题。')
        elif impr < 500: issues.append('展示少于 500，先继续采样或核对观众需求；不要推断被限流。')
        elif ctr is None: issues.append('有展示但缺 CTR：回 Studio 补充。')
        else:
            baseline = [x['ctr_pct'] for x in same if x['ctr_pct'] is not None and (x['impressions'] or 0) >= 500]
            if len(baseline) >= 3:
                med=statistics.median(baseline)
                if ctr < med * .7: issues.append(f'CTR 比同格式同来源样本中位数 {fmt(med,"%",2)} 明显偏低：可测试标题/封面，避免推定因果。')
            else: issues.append('相同格式/来源样本不足 3 条：不设全网通用 CTR 合格线。')
    else:
        issues.append('Shorts 采用其自身观看与留存指标，不与长视频展示 CTR 比较。')
    r30=row['retention_30s_pct']
    if r30 is None: issues.append('缺少前 30 秒留存：如该视频可用，请从 Studio 补充。')
    else:
        values=[x['retention_30s_pct'] for x in same if x['retention_30s_pct'] is not None]
        if len(values)>=3 and r30 < statistics.median(values)*.75:
            issues.append('30 秒留存弱于同组：回看标题承诺与开头是否匹配。')
    clicks,leads=row['resource_clicks'],row['qualified_leads']
    if clicks is not None and clicks >= 20 and leads == 0:
        issues.append('资源已有点击但无有效咨询：核对受众/资源承诺/服务适配，先访谈而不是降价。')
    if leads is not None and leads>0 and row['paid_orders']==0:
        issues.append('已有有效咨询暂无订单：复查目标匹配和具体交付，不归咎单一价格。')
    return issues or ['当前无明确异常信号；建议保持发布与记录，继续形成可比样本。']


def report(rows):
    out=['# YouTube 视频数据诊断（按实际录入数据）','',
         '> 本工具只做数据整理和启发式排查，不直接抓取 Studio、不判断“平台限流”，不预测推荐算法。',
         '> 同一 CSV 行 = 同一时间窗口内的一条视频；跨日期/格式不可随意排名。',
         f'视频数：**{len(rows)}**；长视频 {sum(x["format"]=="long" for x in rows)} 条；Shorts {sum(x["format"]=="short" for x in rows)} 条。','']
    for r in rows:
        out.extend([f'## {r["video_id"]} ({r["format"]}, 来源：{r["traffic_source"]}, 窗口：{r["time_window"]})',
                    f'- 观看：{fmt(r["views"],digits=0)}；展示：{fmt(r["impressions"],digits=0)}；CTR：{fmt(r["ctr_pct"],"%",2)}',
                    f'- 平均观看秒数：{fmt(r["avg_view_duration_sec"],digits=0)}；前 30 秒留存：{fmt(r["retention_30s_pct"],"%",1)}',
                    f'- 资源点击：{fmt(r["resource_clicks"],digits=0)}；有效咨询：{fmt(r["qualified_leads"],digits=0)}；订单：{fmt(r["paid_orders"],digits=0)}',
                    f'- 净收款（用户录入）：{fmt(r["net_revenue_cny"],digits=2)} 元；制作工时：{fmt(r["production_hours"],digits=1)}',
                    '- 下一步观察：' ])
        out.extend('  - '+s for s in diagnose(r,rows));out.append('')
    paid=[r['net_revenue_cny'] for r in rows if r['net_revenue_cny'] is not None]
    out.extend(['## 完整性',f'- 实际填写净收款：{len(paid)}/{len(rows)} 条；空白不等于零。',
                '- 强烈建议在 `templates/EXPERIMENT_LOG.md` 写明下一轮只改变的一个因素。',''])
    return '\n'.join(out)


def main(argv=None):
    p=argparse.ArgumentParser(description='Diagnose normalized YouTube video CSV without network access')
    p.add_argument('file',help='CSV copied from templates/METRICS_INPUT.csv')
    p.add_argument('--output',help='write Markdown report to given path')
    args=p.parse_args(argv)
    try:
        rows=read_rows(args.file);out=report(rows)
        if args.output:
            path=pathlib.Path(args.output)
            if path.exists(): raise ValueError('输出文件已存在，不覆盖历史复盘')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(out+'\n',encoding='utf-8');print(path)
        else: print(out)
    except (OSError,ValueError) as exc:p.error(str(exc))

if __name__=='__main__':main()
