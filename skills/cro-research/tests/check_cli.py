"""Run the offline regression suite with an unambiguous acceptance marker."""
from pathlib import Path
import sys
import unittest

suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    sys.exit(1)
print("CLI CHECK PASSED")
