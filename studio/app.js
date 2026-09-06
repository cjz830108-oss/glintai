/* Glint Fiction Studio — shared app runtime (auth, api, toasts) */
const App = (() => {
  let sb = null;
  let session = null;
  let cfg = null;

  async function boot() {
    cfg = await fetch('/api/fiction/config').then((r) => r.json());
    if (!cfg.supabaseUrl) throw new Error(cfg.error?.message || 'Studio not configured');
    sb = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
    const { data } = await sb.auth.getSession();
    session = data?.session || null;
    sb.auth.onAuthStateChange((_e, s) => { session = s; });
    return session;
  }

  function requireLogin(loginEl, mainEl) {
    if (session) { loginEl.style.display = 'none'; mainEl.style.display = ''; return true; }
    loginEl.style.display = ''; mainEl.style.display = 'none';
    return false;
  }

  async function signIn(email, password) {
    const { error } = await sb.auth.signInWithPassword({ email, password });
    if (error) throw error;
    const { data } = await sb.auth.getSession();
    session = data?.session || null;
  }

  async function magicLink(email) {
    const { error } = await sb.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: location.origin + '/studio/index.html' },
    });
    if (error) throw error;
  }

  async function signUp(email, password) {
    const { error } = await sb.auth.signUp({ email, password });
    if (error) throw error;
  }

  async function api(path, opts = {}) {
    if (!session) throw new Error('Not signed in');
    const res = await fetch(path, {
      method: opts.method || (opts.body ? 'POST' : 'GET'),
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.access_token}` },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error?.message || `API ${res.status}`);
    return data;
  }

  const uid = () => (crypto.randomUUID ? crypto.randomUUID() : `t-${Date.now()}-${Math.random().toString(36).slice(2)}`);

  function toast(msg, isErr = false) {
    let el = document.querySelector('.toast');
    if (!el) { el = document.createElement('div'); el.className = 'toast'; document.body.appendChild(el); }
    el.textContent = msg;
    el.classList.toggle('err', isErr);
    el.style.display = 'block';
    clearTimeout(el._t);
    el._t = setTimeout(() => (el.style.display = 'none'), isErr ? 7000 : 3500);
  }

  function fmtDate(s) { return s ? new Date(s).toLocaleDateString() : ''; }

  return { boot, requireLogin, signIn, signUp, magicLink, signOut: () => sb?.auth.signOut(), api, uid, toast, getSession: () => session, fmtDate };
})();
window.App = App;
