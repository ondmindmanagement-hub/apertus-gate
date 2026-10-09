#!/usr/bin/env python3
import json, os, re, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API_URL = os.getenv("APERTUS_API_URL", "https://api.publicai.co/v1/chat/completions")
MODEL = os.getenv("APERTUS_MODEL", "swiss-ai/apertus-v1.5-8b")
API_KEY = os.getenv("APERTUS_API_KEY", "")
USER_AGENT = "ApertusGate/1.0 (Hack Apertus 2026)"

SYSTEM_PROMPT = """You are Apertus Gate, a review layer for AI actions.
Return ONLY valid JSON with this exact schema:
{
  "risk_level":"low|medium|high",
  "decision":"allow|human_review|required_block",
  "reasons":["short reason"],
  "missing_information":["short item"],
  "safe_next_step":"one concrete safe next step"
}
Assess reversibility, external side effects, financial/legal/security impact, data sensitivity,
and whether a human should approve before execution. Never claim an action was executed."""

def extract_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise ValueError("Model did not return JSON")
        return json.loads(m.group(0))

def normalize(payload):
    risk = payload.get("risk_level")
    decision = payload.get("decision")
    if risk not in {"low","medium","high"}:
        risk = "high"
    if decision not in {"allow","human_review","required_block"}:
        decision = "human_review"
    reasons = payload.get("reasons") if isinstance(payload.get("reasons"), list) else ["Unstructured model response"]
    missing = payload.get("missing_information") if isinstance(payload.get("missing_information"), list) else []
    safe = str(payload.get("safe_next_step") or "Ask a human reviewer before execution.")
    return {
        "risk_level": risk,
        "decision": decision,
        "reasons": [str(x)[:300] for x in reasons][:6],
        "missing_information": [str(x)[:300] for x in missing][:6],
        "safe_next_step": safe[:600],
        "model": MODEL,
    }

def demo_review(action, context):
    s = (action + " " + context).lower()
    high_terms = ["send money","wire transfer","delete","production","credential","password","legal","contract","publish private","medical"]
    med_terms = ["email","external","deploy","upload","customer","personal data"]
    if any(x in s for x in high_terms):
        risk, decision = "high", "human_review"
    elif any(x in s for x in med_terms):
        risk, decision = "medium", "human_review"
    else:
        risk, decision = "low", "allow"
    return {
        "risk_level": risk,
        "decision": decision,
        "reasons": ["Deterministic demo-mode policy; no model call was made."],
        "missing_information": [],
        "safe_next_step": "Configure APERTUS_API_KEY to run the same review through Apertus 1.5.",
        "model": "demo-policy",
    }

def call_apertus(action, context):
    if not API_KEY:
        return demo_review(action, context)
    prompt = f"Proposed action:\n{action}\n\nContext:\n{context or '(none provided)'}"
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 420
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "Content-Type":"application/json",
        "Authorization":f"Bearer {API_KEY}",
        "User-Agent":USER_AGENT,
    }, method="POST")
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.load(resp)
    content = data["choices"][0]["message"]["content"]
    result = normalize(extract_json(content))
    result["raw_model_output"] = content[:4000]
    return result

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path.startswith("/static/"):
            rel = "static/index.html" if path == "/" else path.lstrip("/")
            return str(ROOT / rel)
        return super().translate_path(path)

    def do_POST(self):
        if self.path != "/api/review":
            self.send_error(404); return
        try:
            # Reject oversized/unknown request bodies before reading any bytes.
            # This demo must not accept arbitrarily large requests on a local port.
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                self.send_error(411, "Content-Length required"); return
            try:
                n = int(raw_length)
            except ValueError:
                self.send_error(400, "Invalid Content-Length"); return
            if n < 1 or n > 12_288:
                self.send_error(413, "Request must be 1-12288 bytes"); return
            req = json.loads(self.rfile.read(n))
            if not isinstance(req, dict) or not isinstance(req.get("action"), str) or not isinstance(req.get("context", ""), str):
                raise ValueError("Expected an object with a string action and context")
            action = req["action"].strip()
            context = req.get("context", "").strip()
            if not action or len(action) > 4000 or len(context) > 6000:
                raise ValueError("Action/context length invalid")
            result = call_apertus(action, context)
            out = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(out)))
            self.end_headers()
            self.wfile.write(out)
        except urllib.error.HTTPError as e:
            # Upstream error bodies can contain user data, diagnostics or tokens.
            self.send_error(502, f"Inference provider HTTP {e.code}; details withheld")
        except (ValueError, json.JSONDecodeError):
            self.send_error(400, "Invalid review request or model response")
        except Exception:
            self.send_error(502, "Review unavailable; no decision authorized")

if __name__ == "__main__":
    os.chdir(ROOT)
    port = int(os.getenv("PORT","8787"))
    print(f"Apertus Gate on http://127.0.0.1:{port}")
    print("Mode:", "Apertus API" if API_KEY else "demo-policy (set APERTUS_API_KEY for real inference)")
    # Bind loopback by default. Docker/remote deployment must opt in to exposure.
    host = os.getenv("HOST","127.0.0.1")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
