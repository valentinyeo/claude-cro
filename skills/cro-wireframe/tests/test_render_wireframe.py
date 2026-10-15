"""Run with the CRO Python environment; all generated files stay in scratch."""

import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills/cro/scripts/render_wireframe.py"
SCRATCH = Path(os.environ.get("CRO_WIREFRAME_SCRATCH", str(Path(tempfile.gettempdir()) / "cro-wireframe-tests")))
spec = importlib.util.spec_from_file_location("render_wireframe", SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def png_size(path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


class WireframeTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.w = Path(self.temp.name)
        self.source = self.w / "before.html"
        self.after = self.w / "after.html"
        self.annotations = self.w / "annotations.json"
        self.source.write_text('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;min-height:1300px} a{display:inline-flex;padding:12px;min-height:44px;min-width:44px;box-sizing:border-box}</style><h1>Daily walking shoes</h1><a href="#shoes">Shop men</a></html>')
        self.after.write_text(self.source.read_text().replace('Daily walking shoes', '<span data-annotation="1">1</span>Comfort for daily walks').replace('href="#shoes"', 'class="wf-cta" href="#shoes"'))
        self.annotations.write_text(json.dumps([{"number": 1, "finding_id": "H-1 <script>", "change": "Move benefit & CTA above image", "evidence": "mobile.png: headline below image"}]))

    def render(self, **kwargs):
        return renderer.render_wireframes(self.source, self.w / "renders", **kwargs)

    def test_single_full_page_both_widths(self):
        manifest = self.render()
        self.assertEqual(len(manifest["renders"]), 2)
        for item in manifest["renders"]:
            width, height = png_size(Path(item["png"]))
            self.assertEqual(width, item["viewport"]["width"])
            self.assertGreater(height, item["viewport"]["height"])
            self.assertEqual(item["content_width"], width)
        self.assertEqual(manifest["comparisons"], [])
        self.assertEqual(json.loads((self.w / "renders/render-manifest.json").read_text()), manifest)

    def test_pair_composites_and_determinism(self):
        manifest = self.render(after=self.after, annotations_path=self.annotations)
        self.assertEqual(len(manifest["renders"]), 4)
        self.assertEqual(len(manifest["comparisons"]), 2)
        hashes = {}
        for item in manifest["renders"]:
            path = Path(item["png"])
            hashes[path] = hashlib.sha256(path.read_bytes()).digest()
            self.assertEqual(png_size(path)[0], item["viewport"]["width"])
        for item in manifest["comparisons"]:
            page = Path(item["html"]).read_text()
            self.assertIn("H-1 &lt;script&gt;", page)
            self.assertIn("mobile.png: headline below image", page)
            self.assertIn("Move benefit &amp; CTA", page)
            self.assertEqual(page.count('src="data:image/png;base64,'), 2)
            embedded = page.split('src="data:image/png;base64,')[1].split('"')[0]
            self.assertTrue(base64.b64decode(embedded).startswith(b"\x89PNG"))
            self.assertTrue(Path(item["png"]).is_file())
            self.assertGreater(png_size(Path(item["png"]))[0], 2 * (390 if item["device"] == "mobile" else 1440))
        self.render(after=self.after, annotations_path=self.annotations)
        for path, digest in hashes.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), digest)

    def test_no_meta_viewport_still_exact_width(self):
        self.source.write_text('<html><body style="margin:0">Shoes</body></html>')
        manifest = self.render()
        self.assertEqual(png_size(Path(manifest["renders"][0]["png"]))[0], 390)

    def test_overflow_is_reported_without_widening_png(self):
        self.source.write_text('<body style="margin:0"><div style="width:1800px;height:1400px">Overflowing original layout</div></body>')
        manifest = self.render()
        mobile = manifest["renders"][0]
        self.assertEqual(mobile["content_width"], 1800)
        self.assertEqual(png_size(Path(mobile["png"])), (390, 1400))

    def test_javascript_cannot_change_content(self):
        self.source.write_text('<body><h1>Keep me</h1><script>document.body.innerHTML="changed";fetch("https://example.com")</script></body>')
        self.source.write_text(self.source.read_text() + '<a href="#">Keep me</a>')
        manifest = self.render()
        self.assertEqual(manifest["renders"][0]["controls"][0]["text"], "Keep me")

    def test_local_stylesheet_supported(self):
        (self.w / "assets").mkdir()
        (self.w / "assets/kit.css").write_text('a{height:60px;width:180px;display:block}')
        self.source.write_text('<link rel="stylesheet" href="assets/kit.css"><a href="#">Shop shoes</a>')
        self.assertEqual(self.render()["renders"][0]["controls"][0]["height"], 60)

    def test_remote_resource_is_blocked(self):
        self.source.write_text('<img src="https://example.com/shoe.png">')
        with self.assertRaisesRegex(ValueError, "disallowed resources"):
            self.render()

    def test_parent_file_resource_is_blocked(self):
        self.source.write_text('<link rel="stylesheet" href="../outside.css">')
        with self.assertRaisesRegex(ValueError, "disallowed resources"):
            self.render()

    def test_missing_local_resource_fails(self):
        self.source.write_text('<img src="missing.png">')
        with self.assertRaises(ValueError):
            self.render()

    def test_broken_data_image_fails(self):
        self.source.write_text('<img src="data:image/png;base64,bm90LXBuZw==">')
        with self.assertRaises(ValueError):
            self.render()

    def test_annotations_required_with_after(self):
        with self.assertRaisesRegex(ValueError, "supplied together"):
            self.render(after=self.after)
        with self.assertRaisesRegex(ValueError, "supplied together"):
            self.render(annotations_path=self.annotations)

    def test_marker_mismatch_fails(self):
        self.after.write_text('<span data-annotation="2">2</span>')
        with self.assertRaisesRegex(ValueError, "match annotation"):
            self.render(after=self.after, annotations_path=self.annotations)

    def test_duplicate_marker_fails(self):
        self.after.write_text('<span data-annotation="1">1</span>' * 2)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.render(after=self.after, annotations_path=self.annotations)

    def test_bad_marker_fails(self):
        self.source.write_text('<span data-annotation="zero">0</span>')
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.render()

    def test_invalid_annotation_contract(self):
        for value in [{}, [], [None], [{"number": True}], [{"number": -1}], [{"number": 1}],
                      [{"number": 1, "finding_id": "H-1", "change": "Move CTA", "evidence": ""}]]:
            with self.subTest(value=value):
                self.annotations.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    renderer.read_annotations(self.annotations)

    def test_duplicate_annotation_number_fails(self):
        entries = json.loads(self.annotations.read_text()) * 2
        self.annotations.write_text(json.dumps(entries))
        with self.assertRaisesRegex(ValueError, "unique"):
            renderer.read_annotations(self.annotations)

    def test_missing_source_and_invalid_json_exit_nonzero(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.w / 'missing.html')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.annotations.write_text('not json')
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), '--after', str(self.after), '--annotations', str(self.annotations)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
