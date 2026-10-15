"""message_test.py drives MiroFish's API end to end; tested against a fake API, no network."""
import importlib.util
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("message_test", os.path.join(HERE, "..", "skills", "cro", "scripts", "message_test.py"))
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)


class Fake(BaseHTTPRequestHandler):
    calls = []
    polls = {}
    fail_sim = False

    def log_message(self, *a):
        pass

    def _ok(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _poll(self, key, final, mid):
        n = Fake.polls.get(key, 0) + 1
        Fake.polls[key] = n
        return final if n >= 2 else mid

    def do_GET(self):
        Fake.calls.append(("GET", self.path))
        p = self.path
        if p == "/health":
            return self._ok({"status": "ok"})
        if p == "/v1/stats":
            n = len(Fake.calls)
            return self._ok({"model": "claude-haiku-5-5", "input_tokens": 1000 * n, "output_tokens": 100 * n})
        if p.startswith("/api/graph/task/"):
            return self._ok({"success": True, "data": self._poll("g", {"status": "completed"}, {"status": "processing", "progress": 50})})
        if p.startswith("/api/graph/project/"):
            return self._ok({"success": True, "data": {"graph_id": "g1"}})
        if p.endswith("/run-status"):
            if Fake.fail_sim:
                return self._ok({"success": True, "data": {"runner_status": "failed"}})
            return self._ok({"success": True, "data": self._poll("s", {"runner_status": "completed"}, {"runner_status": "running"})})
        if p.startswith("/api/report/"):
            return self._ok({"success": True, "data": {"markdown_content": "## Findings\nMonthly option drew fewer objections."}})
        self._ok({"success": False, "error": "unknown"}, 404)

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        Fake.calls.append(("POST", self.path, raw))
        p = self.path
        if p == "/api/graph/ontology/generate":
            assert b'name="simulation_requirement"' in raw and b'filename="brief.md"' in raw
            return self._ok({"success": True, "data": {"project_id": "p1"}})
        if p == "/api/graph/build":
            return self._ok({"success": True, "data": {"task_id": "t1"}})
        if p == "/api/simulation/create":
            return self._ok({"success": True, "data": {"simulation_id": "s1"}})
        if p == "/api/simulation/prepare":
            return self._ok({"success": True, "data": {"task_id": "t2"}})
        if p == "/api/simulation/prepare/status":
            return self._ok({"success": True, "data": self._poll("p", {"status": "ready"}, {"status": "processing"})})
        if p == "/api/simulation/start":
            assert json.loads(raw)["max_rounds"] == 3
            return self._ok({"success": True, "data": {}})
        if p == "/api/report/generate":
            return self._ok({"success": True, "data": {"report_id": "r1", "task_id": "t3", "status": "generating"}})
        if p == "/api/report/generate/status":
            return self._ok({"success": True, "data": self._poll("r", {"status": "completed"}, {"status": "processing"})})
        self._ok({"success": False, "error": "unknown"}, 404)


class MessageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Fake)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        Fake.calls, Fake.polls, Fake.fail_sim = [], {}, False
        self.tmp = tempfile.mkdtemp()
        self.brief = os.path.join(self.tmp, "brief.md")
        with open(self.brief, "w") as fh:
            fh.write("# Offer\nDay rate from GBP 1,200.")

    def args(self, **kw):
        a = dict(brief=self.brief, question="Day rate or monthly?", out=os.path.join(self.tmp, "out"), name="t",
                 rounds=3, platform="reddit", timeout=60)
        a.update(kw)
        return type("A", (), a)

    def client(self):
        return mt.Client(self.base, self.base, poll=0, sleep=lambda s: None)

    def test_full_run_writes_report_with_caveat_and_cost(self):
        path = mt.run(self.args(), self.client(), log=lambda *a: None)
        text = open(path).read()
        self.assertIn("Simulated opinion", text)
        self.assertIn("Monthly option drew fewer objections", text)
        self.assertIn("**Cost:**", text)
        self.assertIn("claude-haiku-5-5", text)
        ids = json.load(open(os.path.join(self.tmp, "out", "run.json")))
        self.assertEqual((ids["project_id"], ids["simulation_id"], ids["report_id"]), ("p1", "s1", "r1"))
        order = [c[1].split("/")[-1] for c in Fake.calls if c[0] == "POST"]
        self.assertEqual(order[:4], ["generate", "build", "create", "prepare"])

    def test_failed_simulation_raises(self):
        Fake.fail_sim = True
        with self.assertRaises(mt.MiroFishError):
            mt.run(self.args(), self.client(), log=lambda *a: None)

    def test_check_reports_model(self):
        out = []
        mt.check(self.args(), self.client(), log=out.append)
        self.assertEqual(out, ["MIROFISH UP haiku"])

    def test_unreachable_api_is_a_clear_error(self):
        c = mt.Client("http://127.0.0.1:9", None, poll=0, sleep=lambda s: None)
        with self.assertRaisesRegex(mt.MiroFishError, "start it with"):
            mt.check(self.args(), c, log=lambda *a: None)


if __name__ == "__main__":
    unittest.main()
