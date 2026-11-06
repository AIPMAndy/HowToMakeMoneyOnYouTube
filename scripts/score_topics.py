#!/usr/bin/env python3
"""Rank ideas from a CSV with five manually assessed 1-5 dimensions.
No invented analytics or guaranteed-virality scores.
"""
import argparse,csv,sys
W={'demand':35,'proof':25,'money':20,'effort':10,'edge':10}
p=argparse.ArgumentParser()
p.add_argument('file',help='CSV with columns title,demand,proof,money,effort,edge')
a=p.parse_args();rows=[]
with open(a.file,encoding='utf-8-sig',newline='') as f:
 for index,row in enumerate(csv.DictReader(f),start=2):
  try:
   if not row['title'].strip():raise ValueError('empty title')
   values={k:int(row[k]) for k in W}
   if any(not 1<=v<=5 for v in values.values()):raise ValueError('must score 1–5')
   score=sum(values[k]*W[k]/5 for k in W)
  except (KeyError,ValueError,TypeError) as e:sys.exit(f'Invalid line {index}: {e}')
  rows.append((round(score),row['title'].strip()))
for rank,(score,title) in enumerate(sorted(rows,reverse=True),1):print(f'{rank:02d}. {score:3d}/100  {title}')
