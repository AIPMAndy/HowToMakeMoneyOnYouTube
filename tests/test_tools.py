"""Negative cases are intentional; don't silently accept unusable evidence."""
import csv, importlib.util, json, pathlib, tempfile, unittest, subprocess, sys
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]

def load_module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
analysis=load_module('analyze_metrics')
checker=load_module('check_episode')

class ToolTests(unittest.TestCase):
    def mkcsv(self,rows):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        file=pathlib.Path(t.name)/'data.csv'
        with file.open('w',newline='',encoding='utf8') as f:
            wr=csv.DictWriter(f,fieldnames=analysis.FIELDS);wr.writeheader();wr.writerows(rows)
        return file
    def valid(self, **changes):
        a={k:'' for k in analysis.FIELDS}
        a.update(video_id='case1',format='long',views='500',impressions='1000',
                 ctr_pct='5',video_duration_sec='300',avg_view_duration_sec='120',
                 retention_30s_pct='60',resource_clicks='10',qualified_leads='1',
                 paid_orders='0',net_revenue_cny='',production_hours='4',
                 traffic_source='browse',time_window='first7d')
        return dict(a,**changes)

    def test_valid_metrics(self):
        rows=analysis.read_rows(self.mkcsv([self.valid()]))
        self.assertEqual(rows[0]['views'],500.0)
        self.assertIsNone(rows[0]['net_revenue_cny'])
        self.assertIn('缺失',analysis.report(rows))

    def test_negative_metrics_rejected(self):
        with self.assertRaisesRegex(ValueError,'超出范围'):
            analysis.read_rows(self.mkcsv([self.valid(views='-1')]))

    def test_ctr_over_100_rejected(self):
        with self.assertRaisesRegex(ValueError,'0..100'):
            analysis.read_rows(self.mkcsv([self.valid(ctr_pct='102')]))

    def test_wrong_window_rejected(self):
        with self.assertRaisesRegex(ValueError,'time_window'):
            analysis.read_rows(self.mkcsv([self.valid(time_window='arbitrary')]))

    def test_duplicate_video_rejected(self):
        with self.assertRaisesRegex(ValueError,'video_id 不得重复'):
            analysis.read_rows(self.mkcsv([self.valid(),self.valid()]))

    def test_short_is_not_long_ctr_benchmark(self):
        item=analysis.read_rows(self.mkcsv([self.valid(format='short',ctr_pct='',impressions='')]))[0]
        result=analysis.diagnose(item,[item])
        self.assertTrue(any('Shorts' in i for i in result))

    def test_comparable_group_respects_time_window(self):
        rows=analysis.read_rows(self.mkcsv([self.valid(),self.valid(video_id='two',time_window='first30d')]))
        self.assertTrue(any('样本不足' in s for s in analysis.diagnose(rows[0],rows)))

    def test_missing_field_rejected(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        f=pathlib.Path(tmp.name)/'bad.csv';f.write_text('video_id,views\na,3\n')
        with self.assertRaisesRegex(ValueError,'缺少字段'):analysis.read_rows(f)

    def manifest(self,root,approved=False):
        for name in ['source.mp4','script.md','thumbnail.png','description.md']:(root/name).write_text('sample')
        d={'title':'A title','viewer_result':'One practical result','owned_source_video':'source.mp4','script':'script.md',
           'thumbnail':'thumbnail.png','description':'description.md',
           'source_claims':[{'claim':'verifiable','source':'https://github.com/AIPMAndy/FreePhoto','checked_at':'2026-11-05'}],
           'review':{k:approved for k in ('rights_checked','screen_privacy_checked','claims_reviewed','audio_reviewed',
                 'thumbnail_true','links_tested','ai_disclosure_reviewed','paid_promotion_reviewed')}}
        path=root/'manifest.json';path.write_text(json.dumps(d));return path

    def test_manifest_cannot_pass_without_human_reviews(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(len(checker.check(self.manifest(pathlib.Path(t)))),8)

    def test_manifest_passes_when_file_refs_and_reviews_present(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(checker.check(self.manifest(pathlib.Path(t),True)),[])

    def test_manifest_catches_missing_source(self):
        with tempfile.TemporaryDirectory() as t:
            path=self.manifest(pathlib.Path(t),True);(path.parent/'source.mp4').unlink()
            self.assertTrue(any('file not found' in x for x in checker.check(path)))

    def test_new_episode_scaffold_creates_release_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            result=subprocess.run([sys.executable,str(ROOT/'scripts/new_episode.py'),'--slug','case-1',
                                   '--title','example','--output',t],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            d=pathlib.Path(t)/'case-1'
            self.assertTrue((d/'manifest.json').is_file())
            self.assertTrue((d/'script.md').is_file())
            self.assertTrue((d/'description.md').is_file())
            self.assertTrue(any('human approval missing' in x for x in checker.check(d/'manifest.json')))

    def test_manifest_rejects_outside_file(self):
        with tempfile.TemporaryDirectory() as t:
            path=self.manifest(pathlib.Path(t),True)
            d=json.loads(path.read_text());d['script']='../outside.md';path.write_text(json.dumps(d))
            self.assertTrue(any('outside episode folder' in x for x in checker.check(path)))

if __name__=='__main__':unittest.main()
