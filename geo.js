/* Glint AI — GEO breadcrumb injector.
 * Derives a BreadcrumbList from the current URL path and injects schema.org
 * JSON-LD. Self-maintaining: works for any current or future page without
 * template changes. Degrades silently. Run after DOM is ready. */
(function () {
  try {
    var path = location.pathname || '/';
    if (path === '/' || path === '' || path === '/index.html') return;

    var BASE = 'https://glintai.tools/';
    var parts = path.split('/').filter(Boolean); // ['tools','ai-humanizer.html']

    var labelMap = {
      'tools': 'Tools', 'blog': 'Blog', 'resources': 'Resources',
      'ai-tools': 'AI Tool Reviews', 'extension': 'Extension', 'about': 'About',
      'privacy': 'Privacy', 'terms': 'Terms', 'dashboard': 'Dashboard'
    };
    function pretty(file) {
      if (!file) return '';
      return file.replace(/\.html$/, '')
        .replace(/-/g, ' ')
        .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    }

    var crumbs = [{ name: 'Home', url: BASE }];
    var acc = BASE;
    for (var i = 0; i < parts.length; i++) {
      acc += parts[i] + (i < parts.length - 1 ? '/' : '');
      var nm = labelMap[parts[i]] || pretty(parts[i]);
      crumbs.push({ name: nm, url: acc });
    }

    var itemList = crumbs.map(function (c, idx) {
      return {
        '@type': 'ListItem',
        'position': idx + 1,
        'name': c.name,
        'item': c.url
      };
    });

    var ld = {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      'itemListElement': itemList
    };
    var s = document.createElement('script');
    s.type = 'application/ld+json';
    s.textContent = JSON.stringify(ld);
    document.head.appendChild(s);
  } catch (e) { /* no-op */ }
})();
