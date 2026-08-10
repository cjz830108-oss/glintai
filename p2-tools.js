const GRAM_HOMOPHONES = [
  [/\b(its|it is)\b/gi, 'its (possessive) vs it is (contraction)'],
  [/\b(your|you are)\b/gi, 'your (possessive) vs you are (contraction)'],
  [/\b(their|there|they are)\b/gi, 'their / there / they are - pick the right one'],
  [/\b(then|than)\b/gi, 'then vs than - then = time or order, than = comparison'],
  [/\b(affect|effect)\b/gi, 'affect vs effect - affect = verb, effect = noun'],
  [/\b(loose|lose)\b/gi, 'loose vs lose - loose = not tight, lose = misplace'],
  [/\b(to|too|two)\b/gi, 'to / too / two - check each is correct'],
  [/\b(accept|except)\b/gi, 'accept vs except - accept = receive, except = exclude'],
  [/\b(who|whom)\b/gi, 'who vs whom - who = subject, whom = object'],
  [/\b(complement|compliment)\b/gi, 'complement vs compliment - complement completes, compliment praises'],
];
function checkGrammar() {
  const el = document.getElementById('gramIn');
  const out = document.getElementById('gramOut');
  const txt = el.value;
  if (!txt.trim()) { out.textContent = 'Paste some text first.'; return; }
  const issues = [];
  const dw = txt.match(/\b([a-zA-Z]+)\s+\1\b/gi);
  if (dw) dw.slice(0, 10).forEach(function (w) { issues.push('Repeated word: ' + w); });
  if (txt.indexOf('  ') !== -1) issues.push('Double spaces detected - trim to one.');
  const lowStart = txt.match(/(?:^|[.!?]\s+)([a-z])/g);
  if (lowStart && lowStart.length) issues.push(lowStart.length + ' sentence(s) may start with a lowercase letter.');
  GRAM_HOMOPHONES.forEach(function (pair) {
    if (pair[0].test(txt)) issues.push('Possible confusion: ' + pair[1]);
  });
  const filler = ['in todays', 'important to note', 'moreover', 'furthermore', 'delve', 'leverage', 'navigate the', 'ever-evolving', 'robust', 'unlock', 'seamless'];
  const found = filler.filter(function (f) { return txt.toLowerCase().indexOf(f) !== -1; });
  if (found.length) issues.push('AI-sounding phrases found: ' + found.join(', ') + ' - consider simpler wording.');
  if (issues.length === 0) {
    out.textContent = 'No obvious issues found. (Light local check - for deep editing use the ChatGPT prompt.)';
  } else {
    out.textContent = issues.map(function (i, k) { return (k + 1) + '. ' + i; }).join('\n');
  }
}
function copyGramPrompt() {
  const txt = document.getElementById('gramIn').value;
  if (!txt.trim()) { alert('Paste text first.'); return; }
  const prompt = 'You are a professional editor. Fix all grammar, spelling, and punctuation errors in the text below. Keep the meaning and tone. Return only the corrected text.\n\n' + txt;
  navigator.clipboard.writeText(prompt).then(function () {
    document.getElementById('gramOut').textContent = 'ChatGPT prompt copied! Paste it into ChatGPT for a fully corrected version.';
  });
}
function generateBio() {
  const name = (document.getElementById('bioName').value || 'Your Name').trim();
  const role = (document.getElementById('bioRole').value || 'professional').trim();
  const yr = (document.getElementById('bioYr').value || 'several').trim();
  const skills = (document.getElementById('bioSkills').value || 'relevant skills').trim();
  const goal = (document.getElementById('bioGoal').value || 'grow in my field').trim();
  const sk = skills.split(',').map(function (s) { return s.trim(); }).filter(Boolean);
  const skList = sk.length ? sk.join(', ') : skills;
  const cap = goal.charAt(0).toUpperCase() + goal.slice(1);
  const linkedin = name + ' - ' + role + ' with ' + yr + ' years of experience.\n\nI help teams with ' + skList + '. ' + cap + '. Open to new connections and collaborations.';
  const twitter = role + ' - ' + yr + 'y exp - ' + (sk.slice(0, 3).join(' - ') || skills) + '\n🎯 ' + cap;
  const resume = name + ' - ' + role + ' (' + yr + '+ yrs) skilled in ' + skList + '. ' + cap + '.';
  document.getElementById('bioOut').textContent = '— LinkedIn Summary —\n' + linkedin + '\n\n— Twitter / X Bio —\n' + twitter + '\n\n— One-line Resume Pitch —\n' + resume;
}
let _bgLibLoading = null;
function loadBgLib() {
  if (window.removeBackground) return Promise.resolve();
  if (_bgLibLoading) return _bgLibLoading;
  _bgLibLoading = new Promise(function (resolve, reject) {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1/dist/index.umd.js';
    s.onload = function () { window.removeBackground ? resolve() : reject(new Error('Model loader missing.')); };
    s.onerror = function () { reject(new Error('Failed to load model loader.')); };
    document.head.appendChild(s);
  });
  return _bgLibLoading;
}
async function removeBg() {
  const fileEl = document.getElementById('bgFile');
  const hint = document.getElementById('bgHint');
  const out = document.getElementById('bgOut');
  const dl = document.getElementById('bgDl');
  const file = fileEl.files && fileEl.files[0];
  if (!file) { hint.textContent = 'Choose an image first.'; return; }
  hint.textContent = 'Loading on-device AI model... (first run downloads ~40MB, then cached)';
  dl.style.display = 'none';
  out.innerHTML = '';
  try {
    await loadBgLib();
    hint.textContent = 'Removing background...';
    const blob = await window.removeBackground(file);
    const url = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = url;
    img.style.maxWidth = '100%';
    img.style.borderRadius = '10px';
    img.style.marginTop = '8px';
    out.appendChild(img);
    dl.href = url;
    dl.style.display = 'inline-block';
    hint.textContent = 'Done - your image never left the browser.';
  } catch (e) {
    hint.textContent = 'Error: ' + (e && e.message ? e.message : e);
  }
}
