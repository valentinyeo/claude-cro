import importlib.util
import os
import re
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "cro" / "scripts"


class Inputs(unittest.TestCase):
    def test_connection_uses_checked_address(self):
        spec = importlib.util.spec_from_file_location("fetch_page", SCRIPTS / "fetch_page.py")
        fp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fp)
        received = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                received.set()
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        real_getaddrinfo = socket.getaddrinfo
        lookups = []

        def getaddrinfo(host, port, *args, **kwargs):
            if host != "pinned.test":
                return real_getaddrinfo(host, port, *args, **kwargs)
            lookups.append(host)
            address = "93.184.216.34" if len(lookups) == 1 else "127.0.0.1"
            return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (address, port or 0))]

        thread.start()
        try:
            with mock.patch.dict(os.environ, {}, clear=True), \
                 mock.patch("socket.getaddrinfo", side_effect=getaddrinfo):
                try:
                    fp.fetch_page(f"http://pinned.test:{server.server_port}/", timeout=1)
                except (RuntimeError, ValueError):
                    pass
            self.assertGreaterEqual(len(lookups), 2)
            self.assertFalse(received.is_set(), "The local server received a request")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_unspecified_address_is_blocked(self):
        for name in ("fetch_page", "capture_screenshot", "analyze_funnel"):
            with self.subTest(module=name):
                spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.assertTrue(module.is_private_ip("::"))
                self.assertFalse(module.is_private_ip("93.184.216.34"))
                self.assertFalse(module.is_private_ip("2606:4700::1111"))

    def test_trust_bundle_floor(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        bounds = re.findall(r"^\s*certifi\s*>=\s*(\d+(?:\.\d+)+)", requirements, re.M | re.I)
        self.assertTrue(bounds, "requirements.txt needs an explicit certifi lower bound")
        for bound in bounds:
            self.assertGreaterEqual(tuple(map(int, bound.split("."))), (2026, 10, 19))

    def test_skill_commands_keep_urls_out_of_shell(self):
        for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            in_bash = False
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip() == "```bash":
                    in_bash = True
                elif line.strip().startswith("```"):
                    in_bash = False
                elif in_bash:
                    with self.subTest(path=str(path.relative_to(ROOT)), line=number):
                        self.assertNotIn("<page-url>", line)
        self.assertIn("Keep data out of shell syntax", (ROOT / "skills" / "cro" / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
