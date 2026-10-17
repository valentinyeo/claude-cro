"""Cloud sessions: no local DNS behind a proxy, and a preinstalled Chromium that may not match Playwright's build."""
import os
import socket
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "cro", "scripts"))
import fetch_page  # noqa: E402
import netenv  # noqa: E402


def no_dns(*a, **k):
    raise socket.gaierror(-2, "Name or service not known")


class NetEnvTest(unittest.TestCase):
    def test_dns_failure_blocks_without_proxy(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("socket.getaddrinfo", no_dns):
            with self.assertRaises(ValueError):
                fetch_page.resolve_and_check("example.com")

    def test_dns_failure_allowed_behind_proxy(self):
        with mock.patch.dict(os.environ, {"HTTPS_PROXY": "http://user:pw@proxy.local:3128"}, clear=True), \
             mock.patch("socket.getaddrinfo", no_dns):
            self.assertEqual(fetch_page.resolve_and_check("example.com"), "example.com")
            with self.assertRaises(ValueError):
                fetch_page.resolve_and_check("localhost")
            self.assertEqual(netenv.browser_proxy(), {"server": "http://proxy.local:3128", "username": "user", "password": "pw"})

    def test_private_ip_still_blocked_behind_proxy(self):
        with mock.patch.dict(os.environ, {"HTTPS_PROXY": "http://proxy.local:3128"}, clear=True):
            with self.assertRaises(ValueError):
                fetch_page.resolve_and_check("127.0.0.1")

    def test_launch_falls_back_to_installed_chromium(self):
        calls = []

        class Chromium:
            def launch(self, **kw):
                calls.append(kw)
                if "executable_path" not in kw:
                    raise RuntimeError("Executable doesn't exist at /opt/pw-browsers/chromium-1248/chrome")
                return "browser"

        pw = mock.Mock(chromium=Chromium())
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(netenv, "_installed_chromes", return_value=["/opt/pw-browsers/chromium-1194/chrome-linux/chrome"]):
            self.assertEqual(netenv.launch_chromium(pw), "browser")
        self.assertEqual(calls[-1]["executable_path"], "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")


if __name__ == "__main__":
    unittest.main()
