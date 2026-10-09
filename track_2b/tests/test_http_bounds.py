import json, os, subprocess, sys, time, unittest, urllib.request, urllib.error, socket
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class HTTPBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s=socket.socket()
        s.bind(("127.0.0.1",0))
        cls.port=s.getsockname()[1]
        s.close()
        env={**os.environ,"PORT":str(cls.port),"HOST":"127.0.0.1","APERTUS_API_KEY":""}
        cls.proc=subprocess.Popen([sys.executable,str(ROOT/"src/server.py")],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.port}/",timeout=1) as r:
                    if r.status==200: return
            except Exception:
                time.sleep(.05)
        raise RuntimeError("HTTP test server not running")
    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:cls.proc.wait(timeout=3)
        except subprocess.TimeoutExpired: cls.proc.kill()
    def request(self,payload):
        req=urllib.request.Request(f"http://127.0.0.1:{self.port}/api/review",data=payload,headers={"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=5) as r:return r.status,r.read().decode()
        except urllib.error.HTTPError as e:return e.code,e.read().decode()
    def test_valid_request_demo_only(self):
        code,body=self.request(b'{"action":"Summarize public notes","context":""}')
        self.assertEqual(code,200)
        self.assertEqual(json.loads(body)["model"],"demo-policy")
    def test_oversized_post_denied(self):
        code,_=self.request(b"x"*12289)
        self.assertEqual(code,413)
    def test_missing_or_invalid_action(self):
        for body in [b'[]',b'{"action":7}',b'{"action":""}',b'not json']:
            with self.subTest(body=body):
                code,_=self.request(body)
                self.assertEqual(code,400)
    def test_long_action_denied_instead_of_truncation(self):
        code,_=self.request(json.dumps({"action":"X"*4001,"context":""}).encode())
        self.assertEqual(code,400)
    def test_context_too_long_denied(self):
        code,_=self.request(json.dumps({"action":"a","context":"x"*6001}).encode())
        self.assertEqual(code,400)
if __name__=="__main__":unittest.main()
