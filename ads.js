/* =========================================================================
 * Glint AI — ad placeholder system  (/ads.js)
 * -------------------------------------------------------------------------
 * - Renders [data-ad] slots. Until you configure an AdSense publisher id,
 *   each slot shows a clearly-labeled placeholder so you can see exactly
 *   where ads will appear.
 * - AdSense-ready: set window.GLINT_ADS_CLIENT = 'ca-pub-xxxx' (e.g. in
 *   an inline <script> before this file) and real ads load automatically.
 * - On tool pages it auto-injects one content slot after the first tool
 *   card, so ad inventory exists site-wide without hand-editing every page.
 * Privacy: no cookies, no personal data. AdSense is the only 3rd party.
 * ========================================================================= */
(function () {
  'use strict';

  var PUBLISHER = (typeof window.GLINT_ADS_CLIENT !== 'undefined') ? window.GLINT_ADS_CLIENT : null;

  function injectStyles() {
    var css =
      '.glint-ad{display:block;text-align:center;padding:18px;margin:18px 0;border:1px dashed var(--line,rgba(120,120,200,.3));border-radius:12px;background:rgba(255,255,255,.02);color:var(--text-soft,#9aa0c0);}' +
      '.glint-ad .ga-label{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.7;margin-bottom:6px;}' +
      '.glint-ad .ga-note{font-size:12px;}' +
      '.glint-ad ins.adsbygoogle{display:block;}';
    var s = document.createElement('style');
    s.textContent = css;
    document.head.appendChild(s);
  }

  function placeholder(slot) {
    var d = document.createElement('div');
    d.className = 'glint-ad';
    d.setAttribute('data-ad', slot);
    d.innerHTML = '<span class="ga-label">Advertisement</span>' +
      '<span class="ga-note">Ad slot — set GLINT_ADS_CLIENT in /ads.js to activate Google AdSense.</span>';
    return d;
  }

  function loadAdsense() {
    if (!PUBLISHER) return;
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + encodeURIComponent(PUBLISHER);
    document.head.appendChild(s);
  }

  function mount() {
    injectStyles();
    if (PUBLISHER) loadAdsense();

    var slots = document.querySelectorAll('[data-ad]');
    slots.forEach(function (el) {
      if (el.dataset.filled) return;
      el.dataset.filled = '1';
      if (PUBLISHER) {
        el.classList.add('glint-ad');
        var ins = document.createElement('ins');
        ins.className = 'adsbygoogle';
        ins.style.display = 'block';
        ins.setAttribute('data-ad-client', PUBLISHER);
        ins.setAttribute('data-ad-slot', el.getAttribute('data-slot') || '');
        ins.setAttribute('data-ad-format', 'auto');
        ins.setAttribute('data-full-width-responsive', 'true');
        el.appendChild(ins);
        try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
      } else {
        var p = placeholder(el.getAttribute('data-ad') || 'content');
        if (el.parentNode) el.parentNode.replaceChild(p, el);
      }
    });

    // auto-inject a content slot on tool surfaces when no explicit slot exists
    if (!PUBLISHER && document.querySelector('.tool-card') && !document.querySelector('.glint-ad')) {
      var card = document.querySelector('.tool-card');
      var ad = placeholder('content');
      if (card.parentNode) card.parentNode.insertBefore(ad, card.nextSibling);
    }
  }

  window.GlintAds = { mount: mount };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
