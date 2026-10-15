"""Verify the captured Allbirds example, not a mock or a network-dependent test."""
import json
from pathlib import Path
import struct
import sys

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def main():
    W = Path(sys.argv[1]).resolve()
    manifest = json.loads((W / 'renders/render-manifest.json').read_text())
    metadata = json.loads((W / 'fetch.json').read_text())
    assert metadata['status_code'] == 200 and not metadata['blocked']
    assert metadata['final_url'].startswith('https://www.allbirds.com')
    source_text = BeautifulSoup((W / 'page.html').read_text(), 'lxml').get_text(' ', strip=True)
    for quote in ['Wildly Comfortable. Super Natural.', 'ALL NEW DASHER NZ COLLECTION',
                  'Easy-to-wear styles made for daily routines, weekend plans, travel, and everything in between.',
                  'Free ground shipping on orders over $100',
                  'Due to increased demand, orders may take up to 30 days to ship.']:
        assert quote.casefold() in source_text.casefold(), quote
    assert len(manifest['renders']) == 4 and len(manifest['comparisons']) == 2
    for label, width, height in [('mobile',390,844),('desktop',1440,900)]:
        live = W / f'hero-{label}.png'
        assert struct.unpack('>II',live.read_bytes()[16:24]) == (width,height)
        evidence = json.loads((W / f'hero-{label}-evidence.json').read_text())
        assert evidence['actions'], 'Overlay actions must be disclosed'
    for item in manifest['renders']:
        png = Path(item['png'])
        width, height = struct.unpack('>II', png.read_bytes()[16:24])
        assert width == item['viewport']['width']
        assert height >= item['viewport']['height']
        assert item['content_width'] == width
        if item['variant'] == 'after':
            for control in item['controls']:
                assert control['width'] >= 44 and control['height'] >= 44, control
            primary = [c for c in item['controls'] if c['primary'] and c['top'] < item['viewport']['height']]
            assert len(primary) == 1
            assert primary[0]['top'] + primary[0]['height'] <= item['viewport']['height']
    for item in manifest['comparisons']:
        text = Path(item['html']).read_text()
        assert text.count('src="data:image/png;base64,') == 2
        assert 'WF-1' in text and 'WF-2' in text and 'Evidence:' in text
        assert Path(item['png']).stat().st_size > 10000


    def contrast(a, b):
        def luminance(color):
            values = [int(color[i:i+2],16)/255 for i in (0,2,4)]
            linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
            return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))
        values = sorted([luminance(a),luminance(b)])
        return (values[1]+.05)/(values[0]+.05)


    ratios = {}
    for foreground, background in [('222222','ffffff'),('555555','ffffff'),('174ea6','ffffff'),
                                  ('b42318','ffffff'),('444444','e4e4e4')]:
        value = contrast(foreground,background)
        assert value >= 4.5
        ratios[f'{foreground}/{background}'] = round(value,2)
    assert contrast('888888','ffffff') >= 3
    assert contrast('eeeeee','ffffff') < 3, 'Contrast negative control must fail'
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height in [(390,844),(1440,900)]:
            page=browser.new_page(viewport={'width':width,'height':height}, java_script_enabled=False)
            page.goto((W/'after.html').as_uri())
            heading=page.locator('h1').bounding_box()
            assert heading['y'] + heading['height'] <= height
            assert page.locator('.wf-menu').is_visible() == (width == 390)
            page.close()
        browser.close()
    assert 'Self-review' in (W / 'DESIGN-NOTES.md').read_text()
    (W / 'contrast-results.json').write_text(json.dumps(ratios,indent=2)+'\n')
    print('ALLBIRDS PASS', json.dumps(ratios, sort_keys=True))


if __name__ == "__main__":
    main()
