"""Static acceptance checks for the public skill and complete component kit."""
from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1]
text = (SKILL / 'SKILL.md').read_text()
css = (SKILL / 'assets/wireframe.css').read_text()
reference = (SKILL / 'references/components.md').read_text()


def check_prose(value):
    assert '\u2014' not in value, 'Use plain punctuation, not em dashes'


for value in [text, reference, css]:
    check_prose(value)
try:
    check_prose('known bad \u2014 prose')
except AssertionError:
    pass
else:
    raise AssertionError('Negative control did not fail')
assert text.startswith('---\nname: cro-wireframe\n')
assert len(text.splitlines()) < 250
for field in ['description:', 'argument-hint:', 'disable-model-invocation: true', 'allowed-tools:']:
    assert field in text, field
assert '/cro wireframe' in text
for expected in ['scoring.md', 'business-types.md', 'test-readiness.md', 'proven-tests-',
                 'before.html', 'after.html', 'annotations.json', 'DESIGN-NOTES.md',
                 'render_wireframe.py', 'cro-py', 'cro-slides', 'before-after',
                 '390 x 844', '44 x 44', '4.5:1', '3:1', 'industry-reported',
                 're-render', 'all four page PNGs', 'both comparison PNGs']:
    assert expected in text, expected
for component in ['Header / nav', 'Hero:', 'Trust bar / logos', 'Reviews / stars',
                  'Product gallery', 'Price block', 'Sticky add-to-cart',
                  'Form with visible labels', 'Pricing table', 'FAQ accordion',
                  'Guarantee badge', 'Footer', 'Annotations:']:
    assert component in reference, component
for class_list in re.findall(r'class="([^"]+)"', reference):
    for name in class_list.split():
        if name.startswith('wf-'):
            assert f'.{name}' in css, name
assert 'data-annotation="1"' in reference
assert all(f'"{field}"' in reference for field in ['number', 'finding_id', 'change', 'evidence'])
print('CONTRACT PASS')
