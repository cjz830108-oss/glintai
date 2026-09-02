/* =========================================================================
 * Glint AI — privacy-friendly analytics  (/analytics.js)
 * -------------------------------------------------------------------------
 * Cookie-free, GDPR-friendly analytics via Plausible (no personal data,
 * no cookies, no consent banner required in most jurisdictions).
 *
 * Activate by setting the domain before this script loads, e.g. in your
 * page <head>:  <script>window.GLINT_PLAUSIBLE_DOMAIN='glintai.tools';</script>
 *
 * Until configured, this file is a complete no-op (no network requests).
 *
 * Usage events are emitted by /usage.js via GlintAnalytics.event(name, props)
 * e.g. GlintAnalytics.event('tool_used', { tool: 'summarizer' }).
 * ========================================================================= */
(function () {
  'use strict';

  var DOMAIN = (typeof window.GLINT_PLAUSIBLE_DOMAIN !== 'undefined') ? window.GLINT_PLAUSIBLE_DOMAIN : 'glintai.tools';

  function load() {
    if (!DOMAIN) return;
    var s = document.createElement('script');
    s.defer = true;
    s.setAttribute('data-domain', DOMAIN);
    s.src = 'https://plausible.io/js/script.js';
    document.head.appendChild(s);
  }

  function event(name, props) {
    if (typeof window.plausible === 'function') {
      try { window.plausible(name, { props: props || {} }); } catch (e) {}
    }
  }

  window.GlintAnalytics = { event: event };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
