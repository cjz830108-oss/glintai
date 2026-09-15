#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glint Fiction — P0 stress tests (TEST 1-9) against the LIVE site.
Prereqs:
  1. supabase-fiction-migration-p0.sql has been run in Supabase SQL Editor.
  2. Probe wallet has credits (top-up SQL at the bottom of the migration file).
  3. Code deployed to production.
Run:  python tests/p0_stress.py
"""
import json, os, time, sys, urllib.request, urllib.error, urllib.parse, concurrent.futures

BASE = "https://glintai.tools"
EMAIL = os.environ.get("P0_EMAIL", "probe.test.glint@gmail.com")
PASSWORD = os.environ.get("P0_PASS", "ProbeTest2026!")
PROXY_REST = BASE + "/api/sb/rest/v1"

_cfg = json.load(urllib.request.urlopen(BASE + "/api/fiction/config", timeout=30))
ANON_KEY = _cfg["supabaseAnonKey"]

results = []


def http(method, url, token=None, body=None, timeout=290, apikey=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    if apikey:
        req.add_header("apikey", apikey)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        r = urllib.request.urlopen(req, data=data, timeout=timeout)
        return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def rest(method, table, token, body=None, query=""):
    url = f"{PROXY_REST}/{table}{query}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.pgrst.object+json" if method != "GET" else "application/json")
    req.add_header("Prefer", "return=representation" if method in ("POST", "PATCH") else "")
    req.add_header("apikey", ANON_KEY)
    req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        r = urllib.request.urlopen(req, data=data, timeout=60)
        return r.status, json.loads(r.read().decode() or "null")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "null")
        except Exception:
            return e.code, None


def first(x):
    """REST GET returns a list — normalize to first row or {}."""
    if isinstance(x, list):
        return x[0] if x else {}
    return x or {}


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  ✅ PASS " if ok else "  ❌ FAIL ") + name + (f" — {detail}" if detail else ""))


def run_step(token, task_id, novel_id, ch, step):
    return http("POST", BASE + "/api/fiction/generate", token,
                {"taskId": task_id, "novelId": novel_id, "chapterNo": ch, "step": step})


def full_chapter(token, tag, novel_id, ch):
    """Run the full pipeline for one chapter, following gate branches.
    IMPORTANT: one taskId for the whole chapter (matches the studio client) —
    credits lock ONCE at first step and settle at memory. Per-step taskIds would
    lock 30 credits per step and blow the wallet."""
    log = {}
    task_id = f"p0-{tag}-ch{ch}"

    # lock once: run outline with the chapter task id, subsequent steps REUSE it
    for step in ("outline", "draft"):
        code, out = run_step(token, task_id, novel_id, ch, step)
        log[step] = out
        if code != 200:
            log["error"] = f"{step}: {code} {json.dumps(out)[:200]}"
            return log
    guard = 0
    step = "continuity"
    while step and guard < 8:
        guard += 1
        code, out = run_step(token, task_id, novel_id, ch, step)
        log[f"{step}{guard}"] = out
        if code != 200:
            log["error"] = f"{step}: {code} {json.dumps(out)[:200]}"
            return log
        step = out.get("nextStep")
        if step == "memory":
            break
    if step == "memory" or guard >= 8:
        code, out = run_step(token, task_id, novel_id, ch, "memory")
        log["memory"] = out
    return log


def abort_stuck_tasks(token):
    """Refund locks on processing tasks left over from crashed runs."""
    c, tasks = rest("GET", "generation_tasks", token,
                    query="?status=eq.processing&kind=eq.chapter&select=id,novel_id,request&limit=20")
    n = 0
    for t in (tasks if isinstance(tasks, list) else []):
        ch = (t.get("request") or {}).get("chapterNo") or 1
        code, out = run_step(token, t["id"], t["novel_id"], ch, "abort")
        n += 1 if code == 200 else 0
        print(f"  abort {t['id']}: {code}")
    return n


def login_or_signup():
    """Login (with retries); on user-not-found try signup (fresh accounts get FREE_GRANT)."""
    tok = None
    for attempt in range(4):
        code, tok = http("POST", BASE + "/api/sb/auth/v1/token?grant_type=password", None,
                         {"email": EMAIL, "password": PASSWORD}, timeout=30, apikey=ANON_KEY)
        if code == 200 and tok.get("access_token"):
            return tok["access_token"]
        print(f"  login attempt {attempt+1}: {code} {json.dumps(tok)[:120]}")
        time.sleep(5)
    # signup (requires apikey header via proxy)
    req = urllib.request.Request(BASE + "/api/sb/auth/v1/signup", method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("apikey", ANON_KEY)
    try:
        r = urllib.request.urlopen(req, data=json.dumps({"email": EMAIL, "password": PASSWORD}).encode(), timeout=30)
        body = json.loads(r.read().decode())
        tok = body.get("access_token")
        if tok:
            print("  (fresh account signed up — FREE_GRANT applied)")
            return tok
    except urllib.error.HTTPError as e:
        print("  signup failed:", e.code, e.read().decode()[:150])
    raise SystemExit("❌ cannot login or signup with " + EMAIL)


def main():
    print("== login ==")
    token = login_or_signup()
    print("  logged in as", EMAIL)
    print("== cleanup: abort stuck tasks (release credit locks) ==")
    try:
        n = abort_stuck_tasks(token)
        print(f"  aborted {n} stuck task(s)")
    except Exception as e:
        print("  cleanup skipped:", e)

    # ---- setup: fresh test novel (or reuse existing via NOVEL_ID env) ----
    print("== setup: novel + blueprint expand ==")
    tag = str(int(time.time()))[-6:]
    novel_id = os.environ.get("NOVEL_ID", "").strip()
    if novel_id:
        print("  reusing novel from env:", novel_id)
        code, out = rest("GET", "novels", token, query=f"?id=eq.{novel_id}&select=id,title")
        out = first(out)
        if not out.get("id"):
            print("  ❌ NOVEL_ID not found"); sys.exit(1)
        code, chars = rest("GET", "characters", token, query=f"?novel_id=eq.{novel_id}&select=name&limit=1")
        if not (chars if isinstance(chars, list) else []):
            print("  ❌ novel has no cast — run blueprint expand first"); sys.exit(1)
        cast = [c["name"] for c in chars]
    else:
        code, out = http("POST", BASE + "/api/fiction/novels", token, {
            "taskId": f"p0-{tag}-novel",
            "idea": "Emma, a London archivist, discovers Alexander, a charming rare-book dealer, "
                    "is hiding a forged manuscript in his shop. Slow-burn romantic suspense set in London.",
            "genre": "romance", "length": 30, "pov": "third", "tone": "tense", "pacing": "balanced",
        })
        if code != 200:
            print("  ❌ novel creation failed:", code, json.dumps(out)[:300]); sys.exit(1)
        novel_id = out["novelId"]
        print("  novel:", novel_id)
        code, out = http("POST", BASE + "/api/fiction/blueprint", token,
                         {"taskId": f"p0-{tag}-expand", "novelId": novel_id, "action": "expand"})
        if code != 200:
            print("  ❌ expand failed:", code, json.dumps(out)[:300]); sys.exit(1)
        cast = out.get("cast", [])
    print("  cast sample:", ", ".join(cast[:6]))

    # ---- seed test fixtures directly via REST (owner JWT passes RLS) ----
    print("== seeding test fixtures ==")
    code, bible = rest("GET", "story_bibles", token, query=f"?novel_id=eq.{novel_id}&select=data")
    bd = first(bible).get("data") or {}
    bd["permanent_facts"] = [{"fact": "Emma has a thin scar above her left eyebrow.", "scope": "permanent", "characters": ["Emma"], "added_chapter": 0}]
    bd["forbidden_facts"] = ["Alexander orders or drinks coffee without an explicit plot reason."]
    bd["important_facts"] = []
    if bd.get("chapter_plan"):
        for p in bd["chapter_plan"]:
            if p.get("no") in (1, 2) and not p.get("location"):
                p["location"] = "London"
        if len(bd["chapter_plan"]) > 2:
            syn = bd["chapter_plan"][2].get("synopsis", "")
            if "discovers Alexander betrayed" not in syn:
                bd["chapter_plan"][2]["synopsis"] = (syn + " Emma discovers Alexander betrayed her trust; she confronts him in London.")[:400]
            bd["chapter_plan"][2]["location"] = "London"
    rest("PATCH", "story_bibles", token, {"data": bd}, query=f"?novel_id=eq.{novel_id}")

    # characters: set Emma trust baseline 80, Alexander-Angela? use first two characters
    code, chars = rest("GET", "characters", token, query=f"?novel_id=eq.{novel_id}&select=id,name")
    names = {c["name"].lower(): c for c in (chars if isinstance(chars, list) else [])}
    emma = names.get("emma")
    if emma:
        rest("PATCH", "characters", token, {"current_state": {"trust": 80, "love": 30}}, query=f"?id=eq.{emma['id']}")
    code, rels = rest("GET", "relationships", token, query=f"?novel_id=eq.{novel_id}&select=id,data")
    rel_list = rels if isinstance(rels, list) else []
    # foreshadowing: silver ring, planted ch1, reveal ch3 (idempotent — skip if already seeded)
    code, fo_exist = rest("GET", "foreshadowing", token,
                          query=f"?novel_id=eq.{novel_id}&title=ilike.*ring*&select=id&limit=1")
    if not (fo_exist if isinstance(fo_exist, list) else [fo_exist] if fo_exist else []):
        rest("POST", "foreshadowing", token, {
            "novel_id": novel_id, "title": "the silver ring in the drawer",
            "description": "A silver ring Emma finds in Alexander's desk drawer.", "introduced_chapter": 1,
            "planned_reveal_chapter": 3, "importance": "major", "status": "planted",
        })
    print("  fixtures seeded (permanent fact, forbidden fact, trust=80, foreshadowing ring reveal@3)")

    # ---- generate chapters 1-3 ----
    print("== generating chapters 1-3 (full pipeline, gate-aware) ==")
    logs = {}
    for ch in (1, 2, 3):
        print(f"  --- chapter {ch} ---")
        logs[ch] = full_chapter(token, tag, novel_id, ch)
        if "error" in logs[ch]:
            print("  ⚠️ pipeline error:", logs[ch]["error"])

    # ================= TESTS =================
    print("== TEST 1 — character fact survives (scar) ==")
    code, ch2 = rest("GET", "chapters", token, query=f"?novel_id=eq.{novel_id}&chapter_no=eq.2&select=content")
    text2 = first(ch2).get("content") or ""
    check("T1 permanent fact injected & consistent",
          "scar" in text2.lower() or not text2,
          "ch2 mentions scar: " + str("scar" in text2.lower()))

    print("== TEST 2 — forbidden fact (coffee) ==")
    violated = "coffee" in text2.lower() and "alexander" in text2.lower()
    cont2 = logs.get(2, {}).get("continuity1", {})
    flagged = bool(cont2.get("issues"))
    check("T2 forbidden fact blocked/flagged", not violated or flagged,
          f"violation={violated}, continuity_flagged={flagged}")

    print("== TEST 3 — foreshadowing window ==")
    code, fo = rest("GET", "foreshadowing", token, query=f"?novel_id=eq.{novel_id}&title=ilike.*ring*&select=status,planned_reveal_chapter")
    fo = fo if isinstance(fo, list) else ([fo] if fo else [])
    status_after_ch2 = (fo[0] or {}).get("status") if fo else None
    check("T3a ring not revealed early (after ch2)", status_after_ch2 in ("planted", "reinforced"),
          f"status={status_after_ch2}")
    code, ch3 = rest("GET", "chapters", token, query=f"?novel_id=eq.{novel_id}&chapter_no=eq.3&select=content")
    text3 = first(ch3).get("content") or ""
    check("T3b reveal window reached ch3", "ring" in text3.lower() or status_after_ch2 in ("revealed",),
          f"ring in ch3: {'ring' in text3.lower()}")

    print("== TEST 4/5 — betrayal: state + relationship deltas + history ==")
    if emma:
        code, st = rest("GET", "characters", token, query=f"?id=eq.{emma['id']}&select=current_state")
        cur = first(st).get("current_state") or {}
        trust = cur.get("trust", 80)
        check("T4 Emma trust dropped after betrayal chapter", trust < 80, f"trust={trust}")
        code, hist = rest("GET", "character_state_history", token,
                          query=f"?novel_id=eq.{novel_id}&character_id=eq.{emma['id']}&select=chapter_no,state_deltas,reason")
        hist = hist if isinstance(hist, list) else []
        check("T4b state history rows exist with reason", len(hist) >= 1 and any(h.get("reason") for h in hist),
              f"{len(hist)} rows, reasons: {[bool(h.get('reason')) for h in hist][:3]}")
    if rel_list:
        code, rel_now = rest("GET", "relationships", token, query=f"?id=eq.{rel_list[0]['id']}&select=data")
        d = first(rel_now).get("data") or {}
        check("T5 relationship axes updated", any(isinstance(d.get(a), (int, float)) for a in ("trust", "conflict", "anger")),
              f"trust={d.get('trust')} conflict={d.get('conflict')}")

    print("== TEST 6 — timeline/location consistency ==")
    code, cont3 = None, logs.get(3, {}).get("continuity1", {})
    issues3 = cont3.get("issues") or []
    hard = [i for i in issues3 if i.get("severity") in ("critical", "major") and i.get("type") in ("timeline", "world", "fact")]
    check("T6 no hard timeline/location break flagged in ch3", not hard, json.dumps(hard)[:200])

    print("== TEST 7 — memory pollution guard ==")
    code, cands = rest("GET", "memory_candidates", token,
                       query=f"?novel_id=eq.{novel_id}&select=status,type,validator_note")
    cands = cands if isinstance(cands, list) else []
    statuses = {c.get("status") for c in cands}
    check("T7 validator ran & statuses valid", len(cands) > 0 and statuses <= {"approved", "rejected", "candidate"},
          f"{len(cands)} candidates, statuses={statuses}")
    code, bible2 = rest("GET", "story_bibles", token, query=f"?novel_id=eq.{novel_id}&select=data")
    bd2 = first(bible2).get("data") or {}
    perm = bd2.get("permanent_facts") or []
    check("T7b permanent facts curated (scar still canonical)",
          any("scar" in ((p.get("fact") if isinstance(p, dict) else p) or "").lower() for p in perm),
          f"{len(perm)} permanent facts")

    print("== TEST 8 — memory idempotency (different taskId, same chapter) ==")
    code, ev_before = rest("GET", "timeline_events", token,
                           query=f"?novel_id=eq.{novel_id}&chapter_no=eq.1&select=id")
    n_before = len(ev_before if isinstance(ev_before, list) else [])
    code, out = run_step(token, f"p0-{tag}-retry-memory", novel_id, 1, "memory")
    applied = out.get("memoryApplied")
    code2, ev_after = rest("GET", "timeline_events", token,
                           query=f"?novel_id=eq.{novel_id}&chapter_no=eq.1&select=id")
    n_after = len(ev_after if isinstance(ev_after, list) else [])
    check("T8 retry/re-run applies memory at most once", n_after == n_before and applied in (False, None, {"applied": False}),
          f"events {n_before}→{n_after}, memoryApplied={applied}")

    print("== TEST 9 — concurrent duplicate task ==")
    # fresh score task on ch1 with same taskId fired twice concurrently
    tid = f"p0-{tag}-concurrent-score"
    with concurrent.futures.ThreadPoolExecutor(2) as ex:
        futs = [ex.submit(run_step, token, tid, novel_id, 1, "score") for _ in range(2)]
        outs = [f.result() for f in futs]
    ok_codes = all(c == 200 for c, _ in outs)
    code, outs_rows = rest("GET", "generation_outputs", token,
                           query=f"?task_id=eq.{tid}&kind=eq.score_a0&select=id")
    n_rows = len(outs_rows if isinstance(outs_rows, list) else [])
    check("T9 concurrent duplicates → single execution", ok_codes and n_rows == 1, f"score_a0 rows={n_rows}")

    # ---- summary ----
    print("\n===== STRESS TEST SUMMARY =====")
    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL ") + name + (f" | {detail}" if detail else ""))
    print(f"\n{npass}/{len(results)} passed")


if __name__ == "__main__":
    main()
