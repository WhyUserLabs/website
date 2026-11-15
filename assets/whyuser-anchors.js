/* ═══════════════════════════════════════════════════════════════════
   whyuser-anchors.js — make every #anchor link land, even inside a tab.

   Every section on the site has an id, so /page.html#some-section works.
   The browser handles that alone when the section is visible. This file
   covers the case it cannot: the target sits inside a closed <details>
   or an inactive tab panel (the homepage story tabs, the sample-report
   tabs). It opens what hides the target, then scrolls to it.

   It runs on load and whenever the hash changes. It changes nothing on
   a page whose hash is empty or points nowhere.
   ═══════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function target() {
    var h = (location.hash || '').slice(1);
    if (!h) return null;
    try { h = decodeURIComponent(h); } catch (e) { /* keep raw */ }
    return document.getElementById(h);
  }

  function isHidden(el) {
    if (el.hidden || el.getAttribute('aria-hidden') === 'true') return true;
    return window.getComputedStyle(el).display === 'none';
  }

  /* The control that shows a hidden panel: a tab whose aria-controls
     names it, or (sample reports) a tab whose data-tab-key matches the
     panel's data-panel. */
  function controllerFor(panel) {
    var c = null;
    if (panel.id) c = document.querySelector('[aria-controls="' + panel.id + '"]');
    if (!c && panel.getAttribute('data-panel')) {
      c = document.querySelector('[data-tab-key="' + panel.getAttribute('data-panel') + '"]');
    }
    return c;
  }

  /* Open everything between the target and <body>. Returns true if
     anything had to be opened. */
  function reveal(el) {
    var opened = false;
    for (var n = el; n && n !== document.body; n = n.parentElement) {
      if (n.tagName === 'DETAILS' && !n.open) { n.open = true; opened = true; }
      else if (isHidden(n)) {
        var c = controllerFor(n);
        if (c) { c.click(); opened = true; }
      }
    }
    return opened;
  }

  function offset() {
    var v = parseFloat(window.getComputedStyle(document.documentElement).scrollPaddingTop);
    return isNaN(v) ? 0 : v;
  }

  function go(instant, force) {
    var el = target();
    if (!el) return;
    var opened = reveal(el);
    var off = Math.abs(el.getBoundingClientRect().top - offset());
    if (force || opened || off > 40) {
      try { el.scrollIntoView({ block: 'start', behavior: instant ? 'instant' : 'smooth' }); }
      catch (e) { el.scrollIntoView(true); }
    }
  }

  /* After the page's own tab scripts have set their first tab. Jump
     straight there: the site's smooth scrolling would otherwise crawl
     down a long page on arrival. */
  function onReady() { setTimeout(function () { go(true, true); }, 0); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', onReady);
  else onReady();

  /* Images and fonts can push the target down after the first scroll.
     Skip the correction if the reader has started scrolling. */
  var moved = false;
  ['wheel', 'touchstart', 'keydown'].forEach(function (t) {
    window.addEventListener(t, function () { moved = true; }, { once: true, passive: true });
  });
  window.addEventListener('load', function () { if (!moved) go(true); });
  window.addEventListener('hashchange', function () { go(false); });
})();
