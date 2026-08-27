/* =========================================================================
 * Glint AI — unified usage engine  (/usage.js)
 * -------------------------------------------------------------------------
 * - Wraps the global tool functions (runSummarize, humanizeLocal, ...)
 *   AFTER they are defined, so we never touch the tool source code.
 * - Anonymous: counted in localStorage, NEVER hard-blocked (honors the
 *   "No signup required" trust point). After a few uses we show a soft,
 *   dismissible nudge to create a free account.
 * - Logged-in Free: capped at plan AI credits / PDF pages per month. When
 *   the allowance is exhausted the tool renders an INLINE PAYWALL (not a
 *   blocking error) pointing at Upgrade / Log in.
 * - Pro / Team: unlimited.
 * - Persists usage to Supabase `profiles` for logged-in users (RLS allows
 *   updating own row).
 * Degrades gracefully when Supabase / auth modal are absent.
 * ========================================================================= */
(function () {
  'use strict';

  var LS_KEY = 'glint_usage_v1';

  // slug -> tool definition.  out = id of the element the tool writes to.
  var TOOLS = {
    summarizer:  { fn: 'runSummarize',   out: 'sumOut',   kind: 'ai',   label: 'AI Text Summarizer' },
    humanizer:   { fn: 'humanizeLocal',  out: 'humOut',   kind: 'ai',   label: 'AI Humanizer' },
    detector:    { fn: 'detectAi',       out: 'detOut',   kind: 'ai',   label: 'AI Content Detector' },
    paraphraser: { fn: 'paraphrase',     out: 'paraOut',  kind: 'ai',   label: 'Paraphraser' },
    pdf:         { fn: 'summarizePdf',   out: 'pdfOut',   kind: 'pdf',  label: 'PDF Summarizer' },
    youtube:     { fn: 'genYt',          out: 'ytOut',    kind: 'ai',   label: 'YouTube Title Generator' },
    hashtag:     { fn: 'genHash',        out: 'hashOut',  kind: 'ai',   label: 'Hashtag Generator' },
    bio:         { fn: 'generateBio',    out: 'bioOut',   kind: 'ai',   label: 'Bio & Resume Generator' },
    grammar:     { fn: 'checkGrammar',   out: 'gramOut',  kind: 'ai',   label: 'Grammar Checker' },
    readability: { fn: 'runRead',        out: 'readStats',kind: 'free', label: 'Readability Analyzer' },
    markdown:    { fn: 'mdToHtml',       out: 'mdOut',    kind: 'free', label: 'Markdown Converter' },
    json:        { fn: 'jsonFmt',        out: 'jsonOut',  kind: 'free', label: 'JSON Formatter' },
    password:    { fn: 'genPw',          out: 'pwOut',    kind: 'free', label: 'Password Generator' },
    serp:        { fn: 'serpPreview',    out: 'serpOut',  kind: 'free', label: 'SERP Preview' },
    counter:     { fn: 'wcCount',        out: 'wcStats',  kind: 'free', label: 'Word Counter' },
    background:  { fn: 'removeBg',       out: 'bgOut',    kind: 'free', label: 'Background Remover' }
  };

  var state = {
    tier: 'anon',          // 'anon' | 'free' | 'pro'
    plan: 'free',
    aiUsed: 0, aiLimit: 50,
    pdfUsed: 0, pdfLimit: 20,
    profile: null,
    ready: false
  };

  function monthKey(d) { d = d || new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1); }

  function loadLocal() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (raw) {
        var o = JSON.parse(raw);
        if (o.period === monthKey()) return o;
      }
    } catch (e) {}
    return { period: monthKey(), ai: 0, pdf: 0 };
  }
  function saveLocal(o) { try { localStorage.setItem(LS_KEY, JSON.stringify(o)); } catch (e) {} }
  var local = loadLocal();

  function supabaseClient() {
    try { return (typeof client !== 'undefined') ? client : null; } catch (e) { return null; }
  }

  function refreshFromProfile(p) {
    if (!p) return;
    state.profile = p;
    state.plan = p.plan || 'free';
    state.tier = (state.plan === 'pro' || state.plan === 'team') ? 'pro' : 'free';
    state.aiLimit  = (p.ai_credits_limit  != null) ? p.ai_credits_limit  : 50;
    state.pdfLimit = (p.pdf_pages_limit  != null) ? p.pdf_pages_limit  : 20;
    var ps = p.period_start ? new Date(p.period_start) : null;
    var now = new Date();
    var stale = !ps || ps.getMonth() !== now.getMonth() || ps.getFullYear() !== now.getFullYear();
    state.aiUsed  = stale ? 0 : (p.ai_credits_used  || 0);
    state.pdfUsed = stale ? 0 : (p.pdf_pages_used || 0);
    if (stale) patchProfile({ ai_credits_used: 0, pdf_pages_used: 0, period_start: now.toISOString() });
  }

  function patchProfile(obj) {
    var c = supabaseClient();
    if (!c || !state.profile) return;
    c.from('profiles').update(obj).eq('id', state.profile.id).then(function (res) {
      if (res && res.error) console.warn('GlintUsage profile patch failed', res.error);
    });
  }

  function initAuth() {
    var c = supabaseClient();
    if (!c || !c.auth) { state.ready = true; mountBanner(); return; }
    c.auth.getSession().then(function (r) {
      if (r.data && r.data.session && r.data.session.user) fetchProfile(r.data.session.user.id);
      else { state.ready = true; mountBanner(); }
    });
    c.auth.onAuthStateChange(function (_e, session) {
      if (session && session.user) fetchProfile(session.user.id);
      else { state.tier = 'anon'; state.plan = 'free'; state.ready = true; mountBanner(); }
    });
  }

  function fetchProfile(uid) {
    var c = supabaseClient();
    if (!c) { state.ready = true; return; }
    c.from('profiles')
      .select('plan, ai_credits_used, ai_credits_limit, pdf_pages_used, pdf_pages_limit, period_start')
      .eq('id', uid).single().then(function (r) {
        if (r.data) refreshFromProfile(r.data);
        state.ready = true;
        mountBanner();
      });
  }

  /* ---- core API ---- */
  function check(slug) {
    var t = TOOLS[slug];
    if (!t || t.kind === 'free') return { ok: true, tier: state.tier, remaining: Infinity };
    if (state.tier === 'pro')  return { ok: true, tier: 'pro', remaining: Infinity };
    if (state.tier === 'anon') return { ok: true, tier: 'anon', remaining: Infinity }; // never block anon
    // logged-in free user
    if (t.kind === 'ai') {
      var left = state.aiLimit - state.aiUsed;
      return { ok: left > 0, tier: 'free', remaining: left, reason: 'ai' };
    }
    var pl = state.pdfLimit - state.pdfUsed;
    return { ok: pl > 0, tier: 'free', remaining: pl, reason: 'pdf' };
  }

  function record(slug) {
    var t = TOOLS[slug];
    if (!t) return;
    if (t.kind === 'ai') {
      local.ai += 1; saveLocal(local);
      if (state.tier === 'free') { state.aiUsed += 1; patchProfile({ ai_credits_used: state.aiUsed }); }
    } else if (t.kind === 'pdf') {
      local.pdf += 1; saveLocal(local);
      if (state.tier === 'free') { state.pdfUsed += 1; patchProfile({ pdf_pages_used: state.pdfUsed }); }
    } else {
      return; // free tools: no count, no event
    }
    if (typeof window.GlintAnalytics !== 'undefined') window.GlintAnalytics.event('tool_used', { tool: slug, tier: state.tier });
    mountBanner();
  }

  /* ---- inline paywall (NOT a hard error) ---- */
  function showPaywall(slug) {
    var t = TOOLS[slug];
    var out = document.getElementById(t.out);
    if (!out) return;
    var kindLabel = (t.kind === 'pdf') ? 'PDF' : 'AI';
    var used = (t.kind === 'pdf') ? (state.pdfUsed + '/' + state.pdfLimit) : (state.aiUsed + '/' + state.aiLimit);
    out.innerHTML =
      '<div class="glint-paywall">' +
        '<div class="gp-badge">⚡ Pro</div>' +
        '<h3>You\'ve used your free ' + kindLabel + ' allowance</h3>' +
        '<p>Your free plan includes <b>' + used + ' ' + kindLabel + ' uses this month</b>. ' +
        'Upgrade to Pro for unlimited AI tools, GPT-level summaries, and the prompt library.</p>' +
        '<div class="gp-actions">' +
          '<a class="btn btn-primary" href="/#pricing">Upgrade to Pro — $9/mo</a>' +
          '<button class="btn btn-ghost" type="button" onclick="window.GlintUsage.authOrGo()">Log in / Sign up free</button>' +
        '</div>' +
        '<p class="gp-fine">Cancel anytime. No credit card needed to start.</p>' +
      '</div>';
  }

  function authOrGo() {
    if (typeof window.openModal === 'function') window.openModal();
    else location.href = '/#pricing';
  }

  function mountBanner() {
    var el = document.getElementById('glint-usage-banner');
    if (!el) return;
    if (state.tier === 'pro' || state.tier === 'anon') { el.style.display = 'none'; return; }
    var left = Math.max(0, state.aiLimit - state.aiUsed);
    el.style.display = '';
    el.innerHTML = 'Free plan: <b>' + left + '</b> AI uses left this month · <a href="/#pricing">Upgrade to Pro</a>';
  }

  function maybeAnonNudge() {
    if (state.tier !== 'anon') return;
    if (sessionStorage.getItem('glint_nudge')) return;
    if ((local.ai + local.pdf) < 5) return;
    sessionStorage.setItem('glint_nudge', '1');
    var pill = document.createElement('div');
    pill.className = 'glint-nudge';
    pill.innerHTML = 'Loving Glint AI? ' +
      '<button type="button" class="gn-link" onclick="window.GlintUsage.authOrGo()">Create a free account</button> ' +
      'to sync your tools across devices. ' +
      '<button type="button" class="gn-x" onclick="this.parentNode.remove()">×</button>';
    document.body.appendChild(pill);
  }

  /* ---- wrap global tool functions (after they exist) ---- */
  function wrapAll() {
    Object.keys(TOOLS).forEach(function (slug) {
      var t = TOOLS[slug];
      var orig = window[t.fn];
      if (typeof orig !== 'function') return;
      if (orig.__glintWrapped) return;
      var wrapped = function () {
        var verdict = check(slug);
        if (!verdict.ok) { showPaywall(slug); return; }
        var out = document.getElementById(t.out);
        if (out && out.querySelector && out.querySelector('.glint-paywall')) out.innerHTML = '';
        var r = orig.apply(this, arguments);
        record(slug);
        if (verdict.tier === 'anon') maybeAnonNudge();
        return r;
      };
      wrapped.__glintWrapped = true;
      window[t.fn] = wrapped;
    });
  }

  function injectStyles() {
    var css =
      '.glint-paywall{border:1px solid var(--brand,#00f0ff);border-radius:14px;padding:18px 20px;margin:10px 0;background:linear-gradient(180deg,rgba(0,240,255,.08),rgba(255,46,151,.06));}' +
      '.glint-paywall h3{margin:6px 0 8px;font-size:17px;color:var(--text,#e8e8f5);}' +
      '.glint-paywall p{margin:0 0 12px;color:var(--text-soft,#9aa0c0);font-size:14px;}' +
      '.glint-paywall .gp-badge{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.04em;color:#07070d;background:var(--brand,#00f0ff);padding:2px 8px;border-radius:999px;}' +
      '.glint-paywall .gp-actions{display:flex;gap:10px;flex-wrap:wrap;}' +
      '.glint-paywall .gp-fine{margin:12px 0 0;font-size:12px;color:var(--text-soft,#9aa0c0);}' +
      '.glint-nudge{position:fixed;left:16px;bottom:16px;z-index:90;max-width:340px;background:#0d0d18;border:1px solid var(--line,rgba(120,120,200,.2));border-radius:12px;padding:12px 32px 12px 14px;font-size:13px;color:var(--text,#e8e8f5);box-shadow:0 10px 30px rgba(0,0,0,.4);}' +
      '.glint-nudge .gn-link{background:none;border:none;color:var(--brand,#00f0ff);font-weight:700;cursor:pointer;font-size:13px;padding:0;}' +
      '.glint-nudge .gn-x{position:absolute;top:4px;right:8px;background:none;border:none;color:var(--text-soft,#9aa0c0);font-size:18px;cursor:pointer;}' +
      '#glint-usage-banner{display:none;background:var(--bg-soft,#0d0d18);border:1px solid var(--line,rgba(120,120,200,.2));border-radius:10px;padding:8px 12px;font-size:13px;color:var(--text,#e8e8f5);margin:10px 0;}' +
      '#glint-usage-banner a{color:var(--brand,#00f0ff);font-weight:700;}' +
      '#authModal input{border:1px solid #d8d8e8 !important;}' +
      '#authModal .btn{padding:11px 14px;border-radius:12px;font-size:15px;cursor:pointer;font-family:inherit;border:1px solid #d8d8e8;background:#f3f3f8;color:#14142a;}' +
      '#authModal .btn-primary{background:var(--brand,#00f0ff);color:#07070d;border-color:var(--brand,#00f0ff);font-weight:700;}' +
      '#authModal .btn-ghost{background:#fff;color:#14142a;}';
    var s = document.createElement('style');
    s.textContent = css;
    document.head.appendChild(s);
  }

  function boot() {
    injectStyles();
    wrapAll();
    initAuth();
  }

  window.GlintUsage = {
    check: check, record: record, showPaywall: showPaywall,
    authOrGo: authOrGo, mountBanner: mountBanner, state: state, TOOLS: TOOLS
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  // also re-wrap once everything (incl. late scripts) has loaded
  window.addEventListener('load', wrapAll);
})();
