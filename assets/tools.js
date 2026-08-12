// Glint AI — shared tool logic for standalone tool landing pages.
// Functions are copied verbatim from index.html so each tool page works independently.

function copyOut(id) {
  const el = document.getElementById(id);
  const txt = el.innerText || el.textContent;
  if (!txt || txt === 'Output appears here.' || txt === 'Click Generate.') return;
  navigator.clipboard.writeText(txt).then(() => {
    const o = el.textContent;
    el.textContent = '✓ Copied!';
    setTimeout(() => { el.textContent = o; }, 900);
  });
}

// --- Summarizer (extractive) ---
function runSummarize() {
  const txt = document.getElementById('sumIn').value.trim();
  const out = document.getElementById('sumOut');
  if (!txt) { out.textContent = 'Paste some text first.'; return; }
  const ratio = +document.getElementById('sumRatio').value / 100;
  document.getElementById('sumRatioLbl').textContent = '~' + Math.round(ratio * 100) + '% of original';
  const sentences = txt.replace(/\s+/g, ' ').match(/[^.!?]+[.!?]+/g) || [txt];
  if (sentences.length < 2) { out.textContent = txt; return; }
  const words = txt.toLowerCase().match(/\b[a-z0-9']+\b/g) || [];
  const freq = {}; words.forEach(w => freq[w] = (freq[w] || 0) + 1);
  const scored = sentences.map(s => {
    const sw = (s.toLowerCase().match(/\b[a-z0-9']+\b/g) || []);
    const score = sw.reduce((a, w) => a + (freq[w] || 0), 0) / (sw.length || 1);
    return { s, score };
  });
  const n = Math.max(1, Math.round(sentences.length * ratio));
  scored.sort((a, b) => b.score - a.score);
  const top = scored.slice(0, n).sort((a, b) => sentences.indexOf(a.s) - sentences.indexOf(b.s)).map(x => x.s.trim());
  out.textContent = top.join(' ');
}

// --- Readability ---
function runRead() {
  const txt = document.getElementById('readIn').value;
  const words = (txt.match(/\b[^\s]+\b/g) || []).length;
  const chars = txt.length;
  const sents = (txt.match(/[.!?]+/g) || []).length || (words ? 1 : 0);
  const syll = (txt.toLowerCase().match(/[aeiouy]+/g) || []).length || 1;
  const wps = sents ? words / sents : 0;
  const spw = words ? syll / words : 0;
  const score = words && sents ? Math.max(0, Math.min(100, 206.835 - 1.015 * wps - 84.6 * spw)) : 0;
  document.getElementById('sWords').textContent = words;
  document.getElementById('sChars').textContent = chars;
  document.getElementById('sSent').textContent = sents;
  document.getElementById('sRead').textContent = (words / 200).toFixed(1) + ' min';
  document.getElementById('sScore').textContent = words ? Math.round(score) : '–';
  let lbl = 'Very easy';
  if (score < 30) lbl = 'Difficult / academic';
  else if (score < 50) lbl = 'Fairly difficult';
  else if (score < 70) lbl = 'Standard';
  else if (score < 90) lbl = 'Easy';
  document.getElementById('readHint').textContent = words
    ? ('Reading ease: ' + lbl + ' (higher = easier).')
    : 'Start typing to see live stats.';
}

// --- Markdown -> HTML (basic) ---
function escapeHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function mdToHtml() {
  let md = document.getElementById('mdIn').value;
  let h = escapeHtml(md);
  h = h.replace(/^###### (.*)$/gm, '<h6>$1</h6>')
       .replace(/^##### (.*)$/gm, '<h5>$1</h5>')
       .replace(/^#### (.*)$/gm, '<h4>$1</h4>')
       .replace(/^### (.*)$/gm, '<h3>$1</h3>')
       .replace(/^## (.*)$/gm, '<h2>$1</h2>')
       .replace(/^# (.*)$/gm, '<h1>$1</h1>')
       .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
       .replace(/\*(.*?)\*/g, '<em>$1</em>')
       .replace(/!\[(.*?)\]\((.*?)\)/g, '<img alt="$1" src="$2">')
       .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
       .replace(/^\s*[-*] (.*)$/gm, '<li>$1</li>');
  h = h.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  document.getElementById('mdOut').innerHTML = h || 'Output appears here.';
  document.getElementById('mdOut').classList.add('html');
}
function htmlToMd() {
  let h = document.getElementById('mdIn').value;
  let md = h.replace(/<h1>(.*?)<\/h1>/g, '# $1\n')
           .replace(/<h2>(.*?)<\/h2>/g, '## $1\n')
           .replace(/<h3>(.*?)<\/h3>/g, '### $1\n')
           .replace(/<strong>(.*?)<\/strong>/g, '**$1**')
           .replace(/<em>(.*?)<\/em>/g, '*$1*')
           .replace(/<a href="(.*?)">(.*?)<\/a>/g, '[$2]($1)')
           .replace(/<li>(.*?)<\/li>/g, '- $1\n')
           .replace(/<[^>]+>/g, '');
  document.getElementById('mdOut').textContent = md.trim() || 'Output appears here.';
  document.getElementById('mdOut').classList.remove('html');
}

// --- JSON ---
function jsonFmt() {
  const out = document.getElementById('jsonOut');
  try {
    out.textContent = JSON.stringify(JSON.parse(document.getElementById('jsonIn').value), null, 2);
    out.style.color = 'var(--text)';
  } catch (e) {
    out.style.color = 'var(--warn)';
    out.textContent = 'Invalid JSON: ' + e.message;
  }
}
function jsonMin() {
  const out = document.getElementById('jsonOut');
  try {
    out.textContent = JSON.stringify(JSON.parse(document.getElementById('jsonIn').value));
    out.style.color = 'var(--text)';
  } catch (e) {
    out.style.color = 'var(--warn)';
    out.textContent = 'Invalid JSON: ' + e.message;
  }
}

// --- Password ---
function genPw() {
  const len = +document.getElementById('pwLen').value;
  const sets = [];
  if (document.getElementById('pwUpper').checked) sets.push('ABCDEFGHIJKLMNOPQRSTUVWXYZ');
  if (document.getElementById('pwLower').checked) sets.push('abcdefghijklmnopqrstuvwxyz');
  if (document.getElementById('pwNum').checked) sets.push('0123456789');
  if (document.getElementById('pwSym').checked) sets.push('!@#$%^&*()-_=+[]{};:,.?');
  if (!sets.length) { document.getElementById('pwOut').textContent = 'Select at least one option.'; return; }
  const all = sets.join('');
  let pw = '';
  sets.forEach(s => pw += s[Math.floor(Math.random() * s.length)]);
  for (let i = pw.length; i < len; i++) pw += all[Math.floor(Math.random() * all.length)];
  pw = pw.split('').sort(() => Math.random() - 0.5).join('');
  document.getElementById('pwOut').textContent = pw;
}

// --- YouTube Title & Hook Generator ---
function genYt() {
  const topicRaw = (document.getElementById('ytTopic').value || '').trim();
  const topic = topicRaw || 'your topic';
  const kw = (document.getElementById('ytKw').value || '').split(',').map(s => s.trim()).filter(Boolean);
  const t = topic.replace(/^(how to|how do i|ways to|tips for)\s+/i, '').replace(/\.$/, '');
  const T = t.charAt(0).toUpperCase() + t.slice(1);
  const titles = [
    `How to ${t} (Step by Step)`,
    `${T}: 7 Tips That Actually Work`,
    `I Tried ${t} for 30 Days — Here's What Happened`,
    `The ${T} Mistake Everyone Makes`,
    `${T} Explained in 5 Minutes`,
    `Stop Doing ${t} Wrong — Do This Instead`,
    `Beginner's Guide to ${t} (2026)`,
    `${T} | The Only Tutorial You Need`
  ];
  if (kw.length) titles.push(`${T} — ${kw[0]} Edition`, `Best ${kw[0]} for ${t}`);
  const hooks = [
    `Imagine if you could ${t} without the usual headache.`,
    `Most people get ${t} wrong — here's the fix.`,
    `I wish I knew this about ${t} sooner.`,
    `If you only watch one video about ${t}, make it this one.`,
    `You don't need fancy tools to ${t}. Here's proof.`
  ];
  document.getElementById('ytOut').textContent =
    'Titles:\n• ' + titles.join('\n• ') + '\n\nHooks:\n• ' + hooks.join('\n• ');
}

// --- Hashtag Generator ---
function genHash() {
  const topicRaw = (document.getElementById('hashTopic').value || '').trim() || 'yourniche';
  const base = topicRaw.toLowerCase().replace(/[^a-z0-9]+/g, '');
  const mods = ['tips', 'daily', 'life', '2026', 'hacks', 'guide', 'community', 'love', 'gram', 'tok', 'creator', 'growth', 'reels', 'shorts'];
  const tags = new Set();
  tags.add('#' + base);
  mods.forEach(m => tags.add('#' + base + m));
  tags.add('#' + base + 'tips'); tags.add('#' + base + 'daily');
  const arr = [...tags].slice(0, 24);
  const ig = arr.slice(0, 15).join(' ');
  const tt = arr.slice(0, 12).join(' ');
  const yt = arr.slice(0, 8).join(' ');
  const x = arr.slice(0, 6).join(' ');
  document.getElementById('hashOut').textContent =
    'Instagram:\n' + ig + '\n\nTikTok:\n' + tt + '\n\nYouTube:\n' + yt + '\n\nX / Twitter:\n' + x;
}

// --- SERP / Meta Preview ---
function serpPreview() {
  const title = document.getElementById('serpTitle').value || 'Page title preview';
  const url = document.getElementById('serpUrl').value || 'yoursite.com/page';
  const desc = document.getElementById('serpDesc').value || 'Meta description preview text appears here.';
  document.getElementById('serpTitlePrev').textContent = title;
  document.getElementById('serpDescPrev').textContent = desc;
  const clean = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
  document.getElementById('serpUrlPrev').textContent = clean.includes('/') ? clean : clean + ' › page';
  const hints = [];
  hints.push('Title ' + title.length + ' chars ' + (title.length <= 60 ? '✓' : '✗ >60'));
  hints.push('Desc ' + desc.length + ' chars ' + (desc.length <= 155 ? '✓' : '✗ >155'));
  document.getElementById('serpHint').textContent = hints.join('   ');
}

// --- Word & Character Counter ---
function wcCount() {
  const txt = document.getElementById('wcIn').value;
  const words = (txt.match(/\b[^\s]+\b/g) || []).length;
  const chars = txt.length;
  const charsNo = txt.replace(/\s/g, '').length;
  const sents = (txt.match(/[.!?]+/g) || []).length || (words ? 1 : 0);
  const paras = txt.split(/\n\s*\n/).filter(p => p.trim()).length || (words ? 1 : 0);
  document.getElementById('wcWords').textContent = words;
  document.getElementById('wcChars').textContent = chars;
  document.getElementById('wcCharsNo').textContent = charsNo;
  document.getElementById('wcSent').textContent = sents;
  document.getElementById('wcPara').textContent = paras;
  document.getElementById('wcRead').textContent = (words / 200).toFixed(1) + 'm';
  const over = [];
  if (chars > 280) over.push('X >280');
  if (chars > 2200) over.push('IG >2200');
  if (chars > 5000) over.push('YT >5000');
  document.getElementById('wcHint').textContent = words
    ? ('Read time ~' + (words / 200).toFixed(1) + ' min. ' + (over.length ? over.join('; ') + '.' : 'Within X/IG/YT limits.'))
    : 'Start typing to see live counts.';
}

// Init live-counting tools on load
window.addEventListener('DOMContentLoaded', () => {
  const r = document.getElementById('readIn'); if (r) runRead();
  const w = document.getElementById('wcIn'); if (w) wcCount();
});

// ===================== NEW TOOLS (humanizer, detector, paraphraser, pdf, grammar, bio, bg) =====================
// --- AI Humanizer ---
const AI_PHRASES = {
  "in today's world":"these days","it is important to note that":"note that",
  "furthermore":"also","moreover":"plus","delve":"look","leverage":"use",
  "utilize":"use","robust":"solid","a myriad of":"many","in order to":"to",
  "underscore":"show","showcase":"show","foster":"build","crucial":"key",
  "pivotal":"key","navigate":"handle","landscape":"field","realm":"area",
  "underscored":"shown","embark":"start","unlock":"open","elevate":"raise",
  "tailored":"custom","seamless":"smooth","cutting-edge":"modern","holistic":"full",
  "game-changer":"big win","testament to":"proof of","it's worth noting":"note that",
  "plays a vital role":"matters","at the end of the day":"in the end"
};
function humanizeLocal() {
  const el = document.getElementById('humIn');
  let t = el.value.trim();
  const out = document.getElementById('humOut');
  if (!t) { out.textContent = 'Paste some text first.'; return; }
  for (const [k,v] of Object.entries(AI_PHRASES)) {
    const re = new RegExp('\\b'+k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\b','gi');
    t = t.replace(re, v);
  }
  t = t.replace(/([,;])\s+(And|But|Yet|So|Now|Then|Later|Also|Plus)\b/g, '. $2');
  out.textContent = t.trim();
}
function copyHumanPrompt() {
  const t = document.getElementById('humIn').value.trim();
  if (!t) { document.getElementById('humOut').textContent = 'Paste some text first.'; return; }
  const prompt = "Rewrite the following text so it reads like natural, human writing. Vary sentence length, cut filler words (e.g. 'delve', 'leverage', 'it is important to note'), add a little imperfection, and keep the exact meaning. Do not add new facts.\n\nTEXT:\n" + t;
  navigator.clipboard.writeText(prompt).then(()=>{ const o=document.getElementById('humOut'); const prev=o.textContent; o.textContent='✓ Prompt copied — paste into ChatGPT / Claude.'; setTimeout(()=>o.textContent=prev,1200); });
}

// --- AI Detector (heuristic) ---
const AI_TELLS = ["furthermore","moreover","delve","leverage","utilize","robust","myriad","underscore","pivotal","navigate","landscape","realm","seamless","holistic","cutting-edge","tailored","crucial","in today's world","it is important to note","plays a vital role","at the end of the day","game-changer","testament to"];
function detectAi() {
  const txt = document.getElementById('detIn').value.trim();
  const out = document.getElementById('detOut');
  if (!txt) { out.textContent = 'Paste some text to scan.'; return; }
  const words = txt.match(/\b[a-z0-9']+\b/gi) || [];
  const sents = txt.split(/[.!?]+\s*/).filter(s=>s.trim().length);
  const n = words.length || 1;
  const avgLen = words.reduce((a,w)=>a+w.length,0)/n;
  const sentLens = sents.map(s=>(s.match(/\b[a-z0-9']+\b/gi)||[]).length);
  const mean = sentLens.reduce((a,b)=>a+b,0)/(sentLens.length||1);
  const variance = sentLens.reduce((a,b)=>a+Math.pow(b-mean,2),0)/(sentLens.length||1);
  const burst = Math.sqrt(variance);
  const uniq = new Set(words.map(w=>w.toLowerCase())).size;
  const ttr = uniq/n;
  const tells = AI_TELLS.filter(p=>new RegExp('\\b'+p.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\b','i').test(txt)).length;
  const tellDensity = tells / (sents.length||1);
  const pronouns = (txt.match(/\b(I|we|you|my|our|your)\b/gi)||[]).length / n;
  let score = 0;
  score += tellDensity>0.4 ? 35 : tellDensity*90;
  score += burst<4 ? 25 : (burst<8 ? 12 : 0);
  score += avgLen>5.6 ? 12 : 0;
  score += ttr<0.45 ? 15 : (ttr<0.55 ? 7 : 0);
  score += pronouns<0.02 ? 12 : 0;
  score = Math.max(0, Math.min(100, Math.round(score)));
  const verdict = score>=70 ? 'Likely AI-written' : score>=40 ? 'Uncertain / mixed' : score>=20 ? 'Likely human' : 'Looks human';
  out.innerHTML = '<div style="font-size:34px;font-weight:800;margin-bottom:6px;">' + score + '<span style="font-size:16px;font-weight:500;">/100 AI-likelihood</span></div>'
    + '<div style="margin-bottom:10px;font-weight:600;">' + verdict + '</div>'
    + '<div class="hint">Burstiness (sentence-length variation): ' + burst.toFixed(1) + ' — ' + (burst<4?'low (AI-typical)':'healthy') + '</div>'
    + '<div class="hint">Avg word length: ' + avgLen.toFixed(2) + ' chars</div>'
    + '<div class="hint">Vocab diversity (TTR): ' + (ttr*100).toFixed(1) + '%</div>'
    + '<div class="hint">AI-tell phrases found: ' + tells + '</div>'
    + '<div class="hint" style="margin-top:8px;">Heuristic only — use a paid detector for decisions that matter.</div>';
}

// --- Paraphraser (local synonym engine) ---
const SYN = { "good":["great","solid","nice","decent"],"bad":["poor","weak","rough"],"big":["large","huge","major"],"small":["tiny","little","minor"],"fast":["quick","rapid","speedy"],"slow":["sluggish","gradual"],"easy":["simple","straightforward"],"hard":["tough","difficult"],"important":["key","vital","major"],"use":["use","apply","employ"],"make":["make","build","create"],"get":["get","obtain","gain"],"show":["show","reveal","display"],"help":["help","assist","aid"],"think":["think","believe","reckon"],"very":["very","really","quite"],"many":["many","numerous","lots of"],"thing":["thing","item","matter"],"people":["people","folks","users"],"need":["need","require","want"],"find":["find","discover","locate"],"change":["change","alter","tweak"],"improve":["improve","boost","enhance"],"reduce":["reduce","cut","lower"],"increase":["increase","raise","grow"],"create":["create","build","craft"],"start":["start","begin","kick off"],"end":["end","finish","wrap up"],"idea":["idea","concept","notion"],"problem":["problem","issue","snag"],"solution":["solution","fix","answer"],"result":["result","outcome","effect"],"reason":["reason","cause","why"],"example":["example","case","instance"],"difference":["difference","gap","contrast"],"benefit":["benefit","plus","perk"],"risk":["risk","hazard","downside"],"way":["way","method","approach"],"time":["time","moment","while"],"work":["work","function","operate"],"money":["money","cash","budget"],"business":["business","brand","company"],"customer":["customer","client","buyer"],"content":["content","copy","material"],"video":["video","clip","footage"],"post":["post","update","publish"],"grow":["grow","scale","expand"],"learn":["learn","pick up","grasp"],"build":["build","make","set up"],"write":["write","draft","pen"],"read":["read","scan","go through"],"watch":["watch","view","check"],"happy":["happy","glad","pleased"],"free":["free","no-cost","gratis"] };
function paraphrase() {
  let t = document.getElementById('paraIn').value.trim();
  const out = document.getElementById('paraOut');
  const mode = document.getElementById('paraMode').value;
  if (!t) { out.textContent = 'Paste a paragraph first.'; return; }
  const swapRate = mode==='simple' ? 0.55 : mode==='formal' ? 0.4 : 0.32;
  t = t.replace(/\b([A-Za-z][a-z]+)\b/g, (w) => {
    const low = w.toLowerCase();
    if (SYN[low] && Math.random() < swapRate) {
      const opts = SYN[low];
      let pick = opts[Math.floor(Math.random()*opts.length)];
      if (/^[A-Z]/.test(w)) pick = pick.charAt(0).toUpperCase()+pick.slice(1);
      return pick;
    }
    return w;
  });
  if (mode==='simple') {
    t = t.replace(/\b(do not|does not|did not)\b/gi,"don't").replace(/\b(cannot)\b/gi,"can't");
    t = t.replace(/([,;])\s+(and|but|so|now|then|also)\b/gi,'. $2');
  }
  out.textContent = t.trim();
}

// --- PDF Summarizer (client-side pdf.js + extractive) ---
let _pdfReady = false;
async function ensurePdf() {
  if (window.pdfjsLib) return true;
  return await new Promise((res) => {
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
    s.onload = () => {
      try { window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'; } catch(e){}
      _pdfReady = true; res(true);
    };
    s.onerror = () => res(false);
    document.head.appendChild(s);
  });
}
async function summarizePdf() {
  const file = document.getElementById('pdfFile').files[0];
  const out = document.getElementById('pdfOut');
  const hint = document.getElementById('pdfHint');
  if (!file) { hint.textContent = 'Choose a PDF file first.'; return; }
  hint.textContent = 'Loading PDF engine…';
  const ok = await ensurePdf();
  if (!ok) { hint.textContent = 'Could not load the PDF engine (offline?). Paste text into the Summarizer tool instead.'; return; }
  hint.textContent = 'Extracting text…';
  try {
    const buf = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buf }).promise;
    let text = '';
    for (let p = 1; p <= pdf.numPages; p++) {
      const page = await pdf.getPage(p);
      const tc = await page.getTextContent();
      text += tc.items.map(i => i.str).join(' ') + ' ';
    }
    text = text.replace(/\s+/g,' ').trim();
    if (!text) { hint.textContent = 'No extractable text found (scanned PDF?).'; return; }
    const ratio = +document.getElementById('pdfRatio').value/100;
    document.getElementById('pdfRatioLbl').textContent = '~'+Math.round(ratio*100)+'% of original';
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    const words = text.toLowerCase().match(/\b[a-z0-9']+\b/g) || [];
    const freq = {}; words.forEach(w => freq[w]=(freq[w]||0)+1);
    const scored = sentences.map(s => {
      const sw = s.toLowerCase().match(/\b[a-z0-9']+\b/g) || [];
      return { s, score: sw.reduce((a,w)=>a+(freq[w]||0),0)/(sw.length||1) };
    });
    const nt = Math.max(1, Math.round(sentences.length*ratio));
    scored.sort((a,b)=>b.score-a.score);
    const top = scored.slice(0,nt).sort((a,b)=>sentences.indexOf(a.s)-sentences.indexOf(b.s)).map(x=>x.s.trim());
    out.textContent = top.join(' ');
    hint.textContent = '✓ ' + pdf.numPages + ' page(s), ' + words.length + ' words → ' + top.length + '-sentence summary.';
  } catch(e) {
    hint.textContent = 'Failed to read PDF: ' + e.message;
  }
}

// --- Grammar Checker ---
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

// --- Bio & Resume Generator ---
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

// --- Background Remover (on-device WASM model) ---
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
