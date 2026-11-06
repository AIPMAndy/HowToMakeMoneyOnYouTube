import json, pathlib, re, sys, unittest, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT/'data'
SITE = ROOT/'docs'

def load(n):
    return json.loads((DATA/n).read_text(encoding='utf-8'))

class RepositoryDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guides=load('guides.json'); cls.cases=load('cases.json')
        cls.ideas=load('ideas.json');cls.plan=load('plan90.json');cls.sources=load('sources.json')

    def test_guide_count_and_ids(self):
        self.assertGreaterEqual(len(self.guides),36)
        ids=[x['id'] for x in self.guides]
        self.assertEqual(len(ids),len(set(ids)))
        for i,g in enumerate(self.guides):
            self.assertEqual(g['index'],i)
            self.assertRegex(g['id'],r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
            self.assertGreater(len(g['overview']),70)
            self.assertGreaterEqual(len(g['steps']),4)
            self.assertTrue(g['deliverable'] and g['insight'])
            self.assertGreater(len(g['worked_example']),20)
            self.assertGreater(len(g['common_failure']),10)
            self.assertGreater(len(g['verification']),20)

    def test_90_day_plan_complete(self):
        self.assertEqual(len(self.plan),90)
        self.assertEqual([x['day'] for x in self.plan],list(range(1,91)))
        for p in self.plan:
            self.assertIn(p['phase'],['启动','放大','变现验证'])
            self.assertGreater(len(p['task']),7)
            self.assertGreater(len(p['done_criteria']),15)
            self.assertIn('evidence_type',p)

    def test_cases_are_cited_and_scoped(self):
        self.assertGreaterEqual(len(self.cases),4)
        for c in self.cases:
            for key in ['name','url','primary_source','observed','reusable','limits','claim_type','checked_at']:
                self.assertTrue(c.get(key),f'{c.get("name")}: missing {key}')
            self.assertTrue(c['url'].startswith('https://'))
            self.assertTrue(c['primary_source'].startswith('https://'))
            self.assertRegex(c['checked_at'],r'^2026-11-\d\d$')

    def test_original_ideas_have_proof(self):
        self.assertGreaterEqual(len(self.ideas),36)
        for x in self.ideas:
            for field in ['title','asset','proof','viewer','cta']:
                self.assertTrue(x.get(field))

    def test_sources_are_real_https_and_timestamped(self):
        self.assertGreaterEqual(len(self.sources),19)
        links=[s['url'] for s in self.sources]
        self.assertEqual(len(links),len(set(links)))
        for s in self.sources:
            self.assertTrue(s['url'].startswith('https://'))
            self.assertRegex(s['checked_at'],r'^\d{4}-\d{2}-\d{2}$')

    def test_generated_single_guide_pages(self):
        for guide in self.guides:
            f=SITE/'guides'/guide['id']/'index.html'
            self.assertTrue(f.is_file(),guide['id'])
            text=f.read_text(encoding='utf-8')
            self.assertIn(guide['title'],text)
            self.assertIn('application/ld+json',text)
            for step in guide['steps']:self.assertIn(step.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'),text)

    def test_main_site_links_and_local_processing(self):
        html=(SITE/'index.html').read_text(encoding='utf-8')
        js=(SITE/'assets'/'app.js').read_text(encoding='utf-8')
        for k in ['guideSearch','guideCards','totalScore','dailyPlan','caseCards','ideaRows','exportProgress','importProgress','clinicForm','economyForm','econEquation']:
            self.assertIn(f'id="{k}"',html)
        for k in ['localStorage','createObjectURL','URL.revokeObjectURL','renderPlan','renderGuides','initEconomy','initClinic']:
            self.assertIn(k,js)
        for risk in ['eval(','innerHTML','= Function(','document.write(']:
            self.assertNotIn(risk,js)

    def test_public_author_contact_across_site(self):
        home=(SITE/'index.html').read_text(encoding='utf-8')
        script=(SITE/'assets'/'app.js').read_text(encoding='utf-8')
        builder=(ROOT/'scripts'/'build.py').read_text(encoding='utf-8')
        for value in ['https://metaver.vip/', 'AIPMAndy', 'id="contact"', 'data-copy-wechat="AIPMAndy"']:
            self.assertIn(value, home)
        self.assertIn('initContact()', script)
        self.assertIn('AIPMAndy', builder)
        for guide in self.guides:
            page=(SITE/'guides'/guide['id']/'index.html').read_text(encoding='utf-8')
            self.assertIn('AIPMAndy', page, guide['id'])
            self.assertIn('https://metaver.vip/', page, guide['id'])

    def test_sitemap_urls_and_count(self):
        xml=ET.parse(SITE/'sitemap.xml')
        ns={'m':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls=[x.text for x in xml.findall('.//m:loc',ns)]
        self.assertEqual(len(urls),len(self.guides)+1)
        self.assertEqual(len(set(urls)),len(urls))
        self.assertTrue(all(x.startswith('https://aipmandy.github.io/HowToMakeMoneyOnYouTube/') for x in urls))
        self.assertIn('Sitemap:',(SITE/'robots.txt').read_text())
        self.assertIn('HowToMakeMoneyOnYouTube',(SITE/'llms.txt').read_text())

    def test_no_false_live_revenue_claims_in_data(self):
        text=(DATA/'cases.json').read_text(encoding='utf-8')
        for phrase in ['已证实月入百万','保证涨粉','所有人都能赚钱']:
            self.assertNotIn(phrase,text)

if __name__=='__main__':unittest.main()
