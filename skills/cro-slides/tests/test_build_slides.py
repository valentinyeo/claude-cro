#!/usr/bin/env python3
"""Run with the CRO Python environment; writes artifacts only below /tmp."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'skills/cro/scripts/build_slides.py'
spec = importlib.util.spec_from_file_location('build_slides', SCRIPT)
slides = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slides)
SCRATCH = Path(os.environ.get('SLIDES_TEST_OUTPUT', str(Path(tempfile.gettempdir()) / 'cro-slides-tests')))


def fixture():
    return {
        'site': 'Example store', 'consultant': {'name': 'A Consultant', 'site': 'https://example.org', 'contact': 'hello@example.org'},
        'logo': 'image.png', 'slides': [
            {'type': 'bottom-line', 'title': 'Make shopping easier', 'sentences': ['Customers have to dismiss a popup.', 'That can interrupt product discovery.', 'Start by checking the timing with customers.']},
            {'type': 'title', 'title': 'An evidence-led plan', 'subtitle': 'Audit of the first visit', 'image': 'image.png'},
            {'type': 'score', 'title': 'A useful starting point', 'overall': 65, 'evidence': 'FULL-AUDIT.md: score table', 'categories': [{'name': 'UX', 'score': 60, 'weight': 50}, {'name': 'Copy', 'score': 70, 'weight': 50}]},
            {'type': 'test-readiness', 'title': 'Learn before comparing versions', 'verdict': 'NOT_TESTABLE', 'status': 'ASSUMED', 'baseline': '80 orders/month at 2% conversion, an illustration only', 'evidence': 'readiness.txt: NOT_TESTABLE'},
            {'type': 'finding', 'title': 'Let people see the product', 'image': 'image.png', 'problem': 'A popup covers the product.', 'evidence': 'desktop.png: centered signup popup', 'why': 'This may interrupt customers before they see the product.', 'fix': 'Delay the prompt until after product exploration.', 'callouts': [{'x': 10, 'y': 20, 'w': 70, 'h': 50, 'label': 'Signup popup'}]},
            {'type': 'before-after', 'title': 'A direction to explore', 'before': 'image.png', 'after': 'image.png', 'before_label': 'Current page', 'after_label': 'Illustration only, not a shipped change', 'evidence': 'Same test image in both panels; layout fixture only'},
            {'type': 'strengths', 'title': 'Keep what works', 'items': ['Clear product image (desktop.png).', 'Visible close control (desktop.png).']},
            {'type': 'roadmap', 'title': 'The first 90 days', 'phases': [{'label': 'Days 1-30', 'items': ['Check tracking and observe five shoppers.']}, {'label': 'Days 31-60', 'items': ['Ship and review the first fixes.']}, {'label': 'Days 61-90', 'items': ['Repeat customer research and compare the baseline.']}], 'measurement': 'Compare four weeks before and after; record campaigns and seasonality. This is directional, not causal proof.'},
            {'type': 'offer', 'title': 'One focused engagement', 'packages': [{'name': 'Research and fixes', 'price': '$4,000 / month (sample only)', 'timeline': '90 days', 'deliverables': ['Audit fixes', 'Customer research', 'Baseline report']}], 'proof': 'Share shipped work, research observations and measured orders. No guaranteed lift.'},
            {'type': 'tracking', 'title': 'Nothing measures visits or leads today', 'found': ['No analytics or pixel fires on any page.', 'No record of form submissions per month.'], 'access': ['Cloudflare analytics read access.', 'Search Console restricted user.', 'Lead count for the last 3 months.']},
            {'type': 'next-steps', 'title': 'Agree on the first priority', 'items': ['Confirm traffic and orders.', 'Choose the first research round.'], 'url': 'https://example.org/call', 'label': 'Book a call'},
            {'type': 'appendix', 'title': 'Sources and limits', 'items': ['FULL-AUDIT.md', 'ACTION-PLAN.md', 'readiness.txt', 'No access to checkout or analytics.']},
        ]}


class SlidesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        cls.folder = Path(tempfile.mkdtemp(prefix='run-', dir=SCRATCH))
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 960, 'height': 600})
            page.set_content('<body style="margin:0;background:#f5f3ea;font-family:Arial"><div style="background:#24594c;color:white;padding:70px"><h1>Comfort for everyday life</h1><p>Shop natural materials.</p></div><h2 style="padding:40px">Explore the collection</h2></body>')
            page.screenshot(path=str(cls.folder / 'image.png'))
            page.set_viewport_size({'width': 375, 'height': 812})
            page.screenshot(path=str(cls.folder / 'phone.png'))
            browser.close()

    def build(self, data=None, name='deck', embed=True):
        dest = self.folder / f'{name}.html'
        slides.build(data or fixture(), self.folder, dest, embed)
        return dest

    def test_all_types_responsive_and_tiers(self):
        data = fixture()
        self.assertEqual({s['type'] for s in data['slides']}, slides.TYPES)
        deck = self.build(data, 'all-types')
        for width, height in [(1440, 900), (1280, 720), (768, 1024), (375, 812), (320, 740)]:
            self.assertEqual(slides.inspect_deck(deck, self.folder / f'render-{width}', True, width, height), len(data['slides']))
        offer = next(s for s in data['slides'] if s['type'] == 'offer')
        offer['packages'] *= 3
        deck = self.build(data, 'three-tiers')
        slides.inspect_deck(deck, check=True)
        slides.inspect_deck(deck, check=True, width=375, height=812)
        data['slides'][4]['image'] = 'phone.png'
        deck = self.build(data, 'phone-image')
        slides.inspect_deck(deck, check=True)

    def test_client_and_readiness(self):
        data = fixture()
        data['mode'] = 'CLIENT'
        with self.assertRaisesRegex(ValueError, 'CLIENT'):
            self.build(data)
        data['slides'] = [s for s in data['slides'] if s['type'] != 'offer']
        data['slides'][-2].pop('url')
        data['slides'][-2]['title'] = 'Approve the roadmap'
        deck = self.build(data, 'client')
        slides.inspect_deck(deck, check=True)
        content = deck.read_text()
        self.assertNotIn('Book a call', content)
        self.assertIn('Audit &amp; roadmap', content)
        readiness = next(s for s in data['slides'] if s['type'] == 'test-readiness')
        for verdict in slides.MEANINGS:
            readiness['verdict'] = verdict
            self.assertIn(slides.MEANINGS[verdict], self.build(data).read_text())

    def test_validation_and_escaping(self):
        data = fixture()
        data['slides'][0]['title'] = '<script>alert("bad")</script>'
        data['consultant']['name'] = '<b>Not HTML</b>'
        content = self.build(data, 'escaped').read_text()
        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<script>alert(', content)
        self.assertNotIn('<b>Not HTML</b>', content)
        cases = [lambda d: d.update(brand='red; background:url(https://example.com)'),
                 lambda d: d.update(mode='OTHER'),
                 lambda d: d.update(mode=[]),
                 lambda d: d.update(brand=None),
                 lambda d: d.update(logo=17),
                 lambda d: d['slides'][1].update(image=17),
                 lambda d: d['slides'][2].update(overall=100),
                 lambda d: d['slides'][2]['categories'][0].update(weight=20),
                 lambda d: d['slides'][4]['callouts'][0].update(x=90),
                 lambda d: d['slides'][4]['callouts'][0].update(w=0),
                 lambda d: d['slides'][4].pop('evidence'),
                 lambda d: d['slides'][-2].update(url='javascript:alert(1)'),
                 lambda d: d['slides'][3].update(status='UNKNOWN'),
                 lambda d: d['slides'][2].update(overall=float('nan'))]
        for change in cases:
            bad = fixture()
            change(bad)
            with self.assertRaises(ValueError):
                self.build(bad)

    def test_portable_images(self):
        deck = self.build(name='embedded')
        self.assertIn('data:image/png;base64,', deck.read_text())
        self.assertNotIn('src="http', deck.read_text())
        copied = self.build(name='copied', embed=False)
        self.assertTrue((self.folder / 'copied-assets').is_dir())
        moved = self.folder / 'moved'
        import shutil
        moved.mkdir(exist_ok=True)
        shutil.copyfile(copied, moved / copied.name)
        shutil.copytree(self.folder / 'copied-assets', moved / 'copied-assets', dirs_exist_ok=True)
        slides.inspect_deck(moved / copied.name, check=True)
        data = fixture()
        data['slides'][4]['image'] = 'missing.png'
        with self.assertRaisesRegex(ValueError, 'missing image'):
            self.build(data)

    def test_checker_rejects_overflow_and_missing_images(self):
        data = fixture()
        data['slides'][4]['fix'] = 'Extremely long content ' * 500
        bad = self.build(data, 'overflow')
        with self.assertRaisesRegex(ValueError, 'overflow'):
            slides.inspect_deck(bad, check=True)
        data = fixture()
        data['consultant']['name'] = 'An excessively long consultant name ' * 150
        data['slides'][0]['source'] = 'FULL-AUDIT.md: Bottom line'
        with self.assertRaisesRegex(ValueError, 'Source overlaps footer'):
            slides.inspect_deck(self.build(data, 'footer-collision'), check=True)
        good = self.build(name='missing-rendered')
        good.write_text(re.sub(r'src="data:[^"]+"', 'src="absent.png"', good.read_text()))
        with self.assertRaisesRegex(ValueError, 'Missing image'):
            slides.inspect_deck(good, check=True)
        corrupt = self.folder / 'corrupt.png'
        corrupt.write_bytes(b'not an image')
        data = fixture()
        data['slides'][4]['image'] = corrupt.name
        with self.assertRaisesRegex(ValueError, 'Missing image'):
            slides.inspect_deck(self.build(data, 'corrupt'), check=True)

    def test_navigation_callouts_and_print(self):
        from playwright.sync_api import sync_playwright
        data = fixture()
        deck = self.build(data, 'navigation')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            page.goto(deck.as_uri())
            self.assertEqual(page.locator('#counter').inner_text(), '1 / 12')
            page.keyboard.press('ArrowRight')
            self.assertEqual(page.locator('#counter').inner_text(), '2 / 12')
            page.locator('#next').click()
            self.assertEqual(page.locator('#counter').inner_text(), '3 / 12')
            page.keyboard.press('ArrowRight')
            self.assertEqual(page.locator('#counter').inner_text(), '4 / 12')
            page.keyboard.press('ArrowLeft')
            self.assertEqual(page.locator('#counter').inner_text(), '3 / 12')
            page.locator('.slide.active h1').click(position={'x': 5, 'y': 5})
            self.assertEqual(page.locator('#counter').inner_text(), '2 / 12')
            page.locator('body').click(position={'x': 1, 'y': 1})
            page.keyboard.press('End')
            self.assertEqual(page.locator('#counter').inner_text(), '12 / 12')
            page.keyboard.press('Home')
            self.assertEqual(page.locator('#counter').inner_text(), '1 / 12')
            page.evaluate('showSlide(4)')
            shot = page.locator('.slide.active .shot').bounding_box()
            img = page.locator('.slide.active .shot img').bounding_box()
            box = page.locator('.slide.active .callout').bounding_box()
            self.assertAlmostEqual(shot['width'], img['width'], delta=1)
            self.assertAlmostEqual(shot['height'], img['height'], delta=1)
            self.assertAlmostEqual((box['x']-img['x'])/img['width'], .10, delta=.01)
            self.assertAlmostEqual((box['y']-img['y'])/img['height'], .20, delta=.01)
            page.emulate_media(media='print')
            self.assertEqual(page.locator('.slide:visible').count(), len(data['slides']))
            pdf = page.pdf(path=str(self.folder / 'deck.pdf'), prefer_css_page_size=True, print_background=True)
            self.assertEqual(len(re.findall(rb'/Type /Page\b', pdf)), len(data['slides']))
            box = re.search(rb'/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]', pdf)
            self.assertIsNotNone(box)
            self.assertAlmostEqual(float(box[1]) / float(box[2]), 16/9, delta=.001)
            self.assertAlmostEqual(float(box[2]), 540, delta=1)
            for i in range(len(data['slides'])):
                page.evaluate('(i)=>showSlide(i)', i)
                self.assertEqual(page.evaluate(slides.ISSUES_JS), [])
            browser.close()

    def test_cli(self):
        source = self.folder / 'slides.json'
        source.write_text(json.dumps(fixture()))
        result = subprocess.run([sys.executable, str(SCRIPT), str(source), '-o', str(self.folder / 'cli.html'), '--embed', '--check', '--render', str(self.folder / 'cli-render')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)
        self.assertEqual(len(list((self.folder / 'cli-render').glob('slide-*.png'))), 12)
        self.assertEqual(len(list((self.folder / 'cli-render/phone').glob('slide-*.png'))), 12)
        source.write_text('{bad json')
        result = subprocess.run([sys.executable, str(SCRIPT), str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Error:', result.stderr)


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print('SLIDES TESTS PASSED')
        print(f'Artifacts: {SlidesTests.folder}')
    sys.exit(not result.result.wasSuccessful())
