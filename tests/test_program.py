"""Regression tests for program.py experiment statistics."""

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "program", Path(__file__).resolve().parents[1] / "skills" / "cro" / "scripts" / "program.py")
program = importlib.util.module_from_spec(spec)
spec.loader.exec_module(program)


class Analyse(unittest.TestCase):
    def test_clear_win(self):
        r = program.analyse(70000, 1750, 70500, 1960, planned_per_variant=64000)
        self.assertEqual(r["verdict"], "WIN")
        self.assertLess(r["p_value"], 0.01)
        self.assertGreater(r["ci95"][0], 0)

    def test_not_finished_is_never_called(self):
        r = program.analyse(20000, 500, 20000, 600, planned_per_variant=64000)
        self.assertTrue(r["verdict"].startswith("NOT FINISHED"))

    def test_srm_overrides_everything(self):
        r = program.analyse(70000, 1750, 60000, 1600, planned_per_variant=50000)
        self.assertTrue(r["verdict"].startswith("INVALID"))

    def test_flat(self):
        r = program.analyse(50000, 1250, 50000, 1262, planned_per_variant=50000)
        self.assertTrue(r["verdict"].startswith("FLAT"))

    def test_loss(self):
        r = program.analyse(60000, 1800, 60000, 1560, planned_per_variant=50000)
        self.assertEqual(r["verdict"], "LOSS")

    def test_p_value_reference(self):
        # 500/10000 vs 600/10000: classic two-proportion z ~ 3.06, p ~ 0.0022
        r = program.analyse(10000, 500, 10000, 600)
        self.assertAlmostEqual(r["p_value"], 0.0022, places=3)


if __name__ == "__main__":
    unittest.main()
