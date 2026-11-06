#!/usr/bin/env python3
"""Read an episode manifest and enforce the human approval checklist, without uploads.

Does not verify the truth of the claims or licenses; it checks evidence references exist.
"""
import argparse,json,pathlib,re

def check(path):
    obj=json.loads(path.read_text(encoding='utf8'))
    blockers=[]
    for k in ('title','viewer_result','owned_source_video','script','thumbnail','description','source_claims'):
        if not obj.get(k):blockers.append(f'missing: {k}')
    for k in ('owned_source_video','script','thumbnail','description'):
        v=obj.get(k)
        if not v:continue
        base=(path.parent/v).resolve()
        if not base.is_relative_to(path.parent.resolve()):blockers.append(f'outside episode folder: {k}')
        elif not base.is_file():blockers.append(f'file not found: {k}: {v}')
    for i,c in enumerate(obj.get('source_claims',[]),1):
        if not all(c.get(k) for k in ('claim','source','checked_at')):
            blockers.append(f'claim {i}: claim/source/checked_at required')
        elif not (c['source'].startswith('https://') or (path.parent/c['source']).is_file()):
            blockers.append(f'claim {i}: source must be https URL or local file')
    for gate in ('rights_checked','screen_privacy_checked','claims_reviewed','audio_reviewed','thumbnail_true','links_tested','ai_disclosure_reviewed','paid_promotion_reviewed'):
        if obj.get('review',{}).get(gate) is not True:blockers.append(f'human approval missing: {gate}')
    return blockers

def main():
    p=argparse.ArgumentParser(description='Local evidence-based release gate')
    p.add_argument('manifest');args=p.parse_args();path=pathlib.Path(args.manifest)
    problems=check(path)
    if problems:
        print('BLOCKED — release checklist not passed:')
        for x in problems:print(' - '+x)
        raise SystemExit(1)
    print('PASS — manifest references and human approvals present. Facts/licenses still require actual human verification.')
if __name__=='__main__':main()
