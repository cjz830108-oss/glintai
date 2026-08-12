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
