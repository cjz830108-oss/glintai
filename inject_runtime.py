# -*- coding: utf-8 -*-
"""Inject Glint runtime (auth + usage + ads + analytics) into all pages.

Idempotent: each snippet is only added if its marker is absent, so re-running
is safe. Tool pages get the full stack (supabase proxy, auth modal, usage, ads,
analytics); content pages get usage + ads + analytics (they already ship the
auth modal via make_pages, and blog pages need no login).
"""
import os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))

AUTH_MODAL = (
'  <!-- AUTH MODAL (reused from index.html) -->\n'
'  <div id="authModal" style="display:none;position:fixed;inset:0;background:rgba(10,10,30,.5);z-index:100;align-items:center;justify-content:center;padding:20px;">\n'
'    <div style="background:#fff;border-radius:18px;max-width:380px;width:100%;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,.25);">\n'
'      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;">\n'
'        <h3 style="margin:0;font-size:20px;color:#14142a;">Glint AI account</h3>\n'
'        <button onclick="closeModal()" style="border:none;background:none;font-size:22px;cursor:pointer;color:#5b5b6b;">×</button>\n'
'      </div>\n'
'      <form id="authForm" style="display:flex;flex-direction:column;gap:12px;">\n'
'        <input type="email" id="authEmail" placeholder="you@email.com" required style="padding:12px 14px;border:1px solid #d8d8e8;border-radius:12px;font-size:15px;font-family:inherit;" />\n'
'        <input type="password" id="authPass" placeholder="Password (or use magic link)" style="padding:12px 14px;border:1px solid #d8d8e8;border-radius:12px;font-size:15px;font-family:inherit;" />\n'
'        <button type="submit" class="btn btn-primary" id="authSubmit">Log in</button>\n'
'        <button type="button" class="btn btn-ghost google-btn" onclick="googleLogin()">Continue with Google</button>\n'
'        <button type="button" class="btn btn-ghost" onclick="magicLink(event)">Email me a magic link</button>\n'
'        <button type="button" class="btn btn-ghost" id="toggleAuth" onclick="toggleMode()">Need an account? Sign up</button>\n'
'      </form>\n'
'      <p id="authMsg" style="margin:14px 0 0;font-size:13.5px;color:#5b5b6b;min-height:18px;"></p>\n'
'    </div>\n'
'  </div>\n'
)

SUPABASE_SCRIPT = ('  <script src="/vendor/supabase.min.js" '
  'onerror="this.onerror=null;this.src=\'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js\'"></script>\n')
AUTH_SCRIPT = '  <script src="/supabase-auth.js"></script>\n'
ANALYTICS_SCRIPT = '  <script defer src="/analytics.js"></script>\n'
USAGE_SCRIPT = '  <script src="/usage.js"></script>\n'
ADS_SCRIPT = '  <script src="/ads.js"></script>\n'
GEO_SCRIPT = '  <script src="/geo.js"></script>\n'

# ordered (marker, snippet) — appended in this order before </body>
TOOL_ITEMS = [
    ('/vendor/supabase.min.js', SUPABASE_SCRIPT),
    ('/supabase-auth.js', AUTH_SCRIPT),
    ('id="authModal"', AUTH_MODAL),
    ('/analytics.js', ANALYTICS_SCRIPT),
    ('/usage.js', USAGE_SCRIPT),
    ('/ads.js', ADS_SCRIPT),
    ('/geo.js', GEO_SCRIPT),
]
CONTENT_ITEMS = [
    ('/analytics.js', ANALYTICS_SCRIPT),
    ('/usage.js', USAGE_SCRIPT),
    ('/ads.js', ADS_SCRIPT),
    ('/geo.js', GEO_SCRIPT),
]

tool_files = ['index.html', 'tools/index.html'] + sorted(glob.glob(os.path.join(ROOT, 'tools', '*.html')))
content_files = []
for d in ['extension', 'resources', 'ai-tools', 'privacy', 'terms', 'dashboard']:
    p = os.path.join(ROOT, d, 'index.html')
    if os.path.exists(p): content_files.append(p)
for p in ['404.html']:
    if os.path.exists(os.path.join(ROOT, p)): content_files.append(os.path.join(ROOT, p))
content_files += sorted(glob.glob(os.path.join(ROOT, 'blog', '*.html')))

def inject(path, items):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    missing = [snip for (mk, snip) in items if mk not in html]
    if not missing:
        return False
    block = ''.join(missing)
    if '</body>' not in html:
        html = html + '\n' + block
    else:
        html = html.replace('</body>', block + '</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

print('--- tool pages ---')
for p in tool_files:
    if inject(p, TOOL_ITEMS):
        print('  + injected:', os.path.relpath(p, ROOT))
    else:
        print('  = present :', os.path.relpath(p, ROOT))

print('--- content pages ---')
for p in content_files:
    if inject(p, CONTENT_ITEMS):
        print('  + injected:', os.path.relpath(p, ROOT))
    else:
        print('  = present :', os.path.relpath(p, ROOT))
print('done')
