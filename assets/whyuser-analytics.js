/* ═══════════════════════════════════════════════════════════════════════
   WhyUser · GA4 event layer                                    2026-08-29
   ───────────────────────────────────────────────────────────────────────
   Loaded on every page, after the gtag.js snippet in <head>.

   WHY THIS EXISTS
   Pageviews alone tell you traffic, not intent. On this site the things
   worth counting are: who asked for access, who opened a real report, who
   looked at pricing, and who read a glossary term. Those are the signals
   that separate a bounce from a buyer.

   HOW IT REPORTS
   Every event is sent twice on purpose:
     · gtag(...)           → straight to GA4 (G-2JWLP7NZVG)
     · dataLayer.push(...) → visible to GTM (GTM-T6Q5V2WZ), so you can
                             build triggers there later without touching
                             this file again.
   If either tag is absent the calls no-op safely.

   NO CONFIG NEEDED
   Everything is inferred from the DOM. No data-attributes to add to
   markup, no per-page edits. Delegated listeners on document, so links
   injected later still fire.
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var HOST = 'whyuser.com';

  function send(name, params) {
    params = params || {};
    try { if (typeof window.gtag === 'function') window.gtag('event', name, params); } catch (e) {}
    try {
      window.dataLayer = window.dataLayer || [];
      var d = { event: name };
      for (var k in params) { if (Object.prototype.hasOwnProperty.call(params, k)) d[k] = params[k]; }
      window.dataLayer.push(d);
    } catch (e) {}
  }

  function text(el) {
    return (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 90);
  }

  function isInternal(url) {
    try {
      var u = new URL(url, window.location.href);
      if (u.protocol !== 'http:' && u.protocol !== 'https:') return true;
      return u.hostname === window.location.hostname || u.hostname.indexOf(HOST) !== -1;
    } catch (e) { return true; }
  }

  /* ── page classification ───────────────────────────────────────────── */
  var path = window.location.pathname;
  var file = (path.split('/').pop() || 'index.html').toLowerCase();
  var section =
      path.indexOf('/reports/') !== -1  ? 'sample_report' :
      path.indexOf('/compare/') !== -1  ? 'compare'       :
      path.indexOf('/glossary') !== -1  ? 'glossary'      :
      file === 'pricing.html'           ? 'pricing'       :
      file === 'accuracy.html'          ? 'proof'         :
      file === 'developers.html'        ? 'technical'     :
      file === 'success.html'           ? 'conversion'    : 'marketing';

  send('page_context', { page_section: section, page_file: file });

  /* ── 1. a real report export was opened ────────────────────────────
     These are the highest-intent non-form pageviews on the site. They
     were untracked entirely until now, because the four report pages
     carried no Google tag at all. */
  if (section === 'sample_report') {
    send('view_sample_report', {
      report_file: file,
      report_type:
        file.indexOf('committee') !== -1 ? 'committee_simulation' :
        file.indexOf('ad-')       !== -1 ? 'ad_campaign'          :
        file.indexOf('email')     !== -1 ? 'email_campaign'       :
        file.indexOf('audience')  !== -1 ? 'audience_discovery'   : 'other'
    });
  }

  /* ── 2. the thank-you page is the conversion ───────────────────────
     GA4's recommended event name for a lead is generate_lead. Fired here
     rather than on the submit click, so a failed submit is not counted. */
  if (section === 'conversion') {
    send('generate_lead', { value: 0, currency: 'USD', lead_source: 'request_access_form' });
  }

  /* ── 3. pricing viewed ─────────────────────────────────────────────── */
  if (section === 'pricing') { send('view_item_list', { item_list_name: 'plans' }); }

  /* ── delegated click handling ──────────────────────────────────────── */
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (!href) return;
    var label = text(a);

    /* 4. request-access intent. Every CTA that leads to the access form,
          wherever it sits: nav button, hero, closing CTA, footer. */
    if (href.indexOf('#access') !== -1) {
      send('request_access_click', {
        cta_text: label,
        cta_location: a.closest('nav') ? 'nav'
                    : a.closest('footer') ? 'footer'
                    : a.closest('.page-cta, .cta-section') ? 'closing_cta' : 'body',
        page_section: section
      });
      return;
    }

    /* 5. glossary term jumps. Which vocabulary people actually care about
          is a content-strategy signal you cannot get any other way now
          that the nine term pages are one page. */
    if (href.charAt(0) === '#' && section === 'glossary') {
      send('select_content', {
        content_type: 'glossary_term',
        item_id: href.slice(1),
        link_text: label
      });
      return;
    }

    /* 6. outbound links */
    if (!isInternal(href)) {
      send('click', { link_url: href, link_text: label, outbound: true });
      return;
    }

    /* 7. mailto */
    if (href.indexOf('mailto:') === 0) {
      send('contact_email_click', { email: href.replace('mailto:', ''), page_section: section });
    }
  }, true);

  /* ── 8. scroll depth, capped at one event per threshold ────────────── */
  (function () {
    var hits = {}, marks = [25, 50, 75, 90];
    function onScroll() {
      var doc = document.documentElement;
      var h = Math.max(doc.scrollHeight, document.body.scrollHeight) - window.innerHeight;
      if (h <= 0) return;
      var pct = Math.round((window.pageYOffset / h) * 100);
      for (var i = 0; i < marks.length; i++) {
        var m = marks[i];
        if (pct >= m && !hits[m]) {
          hits[m] = 1;
          send('scroll', { percent_scrolled: m, page_section: section });
        }
      }
    }
    var t = null;
    window.addEventListener('scroll', function () {
      if (t) return;
      t = setTimeout(function () { t = null; onScroll(); }, 250);
    }, { passive: true });
  })();
})();
