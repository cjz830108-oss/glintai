#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0 post-migration diagnostics — one-shot probe."""
import json, urllib.request, urllib.error, sys

BASE = "https://glintai.tools"
EMAIL = "probe.test.glint@gmail.com"
PASSWORD = "ProbeTest2026!"


def http(method, url, token=None, body=None, timeout=60, apikey=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    if apikey: req.add_header("apikey", apikey)
    if token: req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        r = urllib.request.urlopen(req, data=data, timeout=timeout)
        return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]
    except Exception as e:
        return 0, str(e)


cfg = json.load(urllib.request.urlopen(BASE + "/api/fiction/config", timeout=30))
KEY = cfg["supabaseAnonKey"]
REST = BASE + "/api/sb/rest/v1"

print("== 1. migration objects (anon) ==")
c, b = http("GET", REST + "/memory_candidates?select=id&limit=1", apikey=KEY)
print(f"  memory_candidates: {c} {b[:120]}")
c, b = http("GET", REST + "/character_state_history?select=id&limit=1", apikey=KEY)
print(f"  character_state_history: {c} {b[:120]}")

print("== 2. login probe ==")
c, b = http("POST", BASE + "/api/sb/auth/v1/token?grant_type=password", body={"email": EMAIL, "password": PASSWORD}, apikey=KEY)
try:
    TOKEN = json.loads(b).get("access_token")
except Exception:
    TOKEN = None
print(f"  login: {c} token={'OK' if TOKEN else b[:120]}")
if not TOKEN:
    sys.exit(1)

print("== 3. probe user's novels (test runs evidence) ==")
c, b = http("GET", REST + "/novels?select=id,title,status,chapter_count,created_at&order=created_at.desc&limit=8", token=TOKEN, apikey=KEY)
print(b)

print("== 4. recent generation_tasks (deploy fingerprint: reader/chapter tasks) ==")
c, b = http("GET", REST + "/generation_tasks?select=id,kind,step,status,created_at&order=created_at.desc&limit=8", token=TOKEN, apikey=KEY)
print(b)

print("== 5. memory_candidates rows (did validator run?) ==")
c, b = http("GET", REST + "/memory_candidates?select=novel_id,chapter_no,status,type,created_at&order=created_at.desc&limit=6", token=TOKEN, apikey=KEY)
print(b)

print("== 6. deploy fingerprint: new-code error shape ==")
c, b = http("POST", BASE + "/api/fiction/generate", token=TOKEN, body={"taskId": "probe-fp-1", "novelId": "00000000-0000-0000-0000-000000000000", "chapterNo": 1, "step": "nope"})
print(f"  status={c} body={b[:200]}")
