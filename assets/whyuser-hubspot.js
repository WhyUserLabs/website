/* ═══════════════════════════════════════════════════════════════════════
   WhyUser · HubSpot form helper                                2026-09-29
   ───────────────────────────────────────────────────────────────────────
   Sends the site's own forms (benchmark report, category nomination) to
   the one HubSpot form, and remembers the visitor's UTM tags for the
   session so a form on a later page still records where they came from.

   Which CTA a lead used goes in the hidden field conversion_cta:
     design_partner_request  index.html#access
     benchmark_nominate      benchmarks/index.html
     benchmark_report        benchmarks/<category>/index.html

   HubSpot needs, on this form:
     · CAPTCHA off (HubSpot refuses API submissions while it is on)
     · a hidden field for the contact property conversion_cta
   ═══════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var CFG = {
    portal: '246967803',
    form: '1d7a87db-9b37-4d76-9089-4c748aa0e2f9',
    consent: {
      subscriptionTypeId: 3350680830,
      legalBasis: 'LEGITIMATE_INTEREST_PQL',
      text: "We'll store and process this information to provide you our products and services. You may opt out of this at any time."
    }
  };
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid'];
  var STORE = 'wu_utm';

  function fromQuery() {
    var o = {}, any = false;
    try {
      var q = new URLSearchParams(window.location.search);
      KEYS.forEach(function (k) { var v = q.get(k); if (v) { o[k] = v.slice(0, 250); any = true; } });
    } catch (e) {}
    return any ? o : null;
  }

  /* Tags on this URL win; otherwise use the ones saved earlier this session. */
  function utms() {
    var q = fromQuery();
    if (q) return q;
    try { return JSON.parse(window.sessionStorage.getItem(STORE) || 'null') || {}; } catch (e) { return {}; }
  }

  (function remember() {
    var q = fromQuery();
    if (!q) return;
    try { window.sessionStorage.setItem(STORE, JSON.stringify(q)); } catch (e) {}
  })();

  function cookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]+)'));
    return m ? m[1] : '';
  }

  /* opts: { cta, email, firstname, lastname, notes, extra: [{ name, value }] }. Resolves on success,
     rejects with an Error on any failure (HubSpot's reason goes to the console). */
  function submit(opts) {
    var pageUrl = window.location.href.split('#')[0].split('?')[0];
    var fields = [
      { objectTypeId: '0-1', name: 'firstname', value: opts.firstname },
      { objectTypeId: '0-1', name: 'lastname', value: opts.lastname },
      { objectTypeId: '0-1', name: 'email', value: opts.email },
      { objectTypeId: '0-1', name: 'conversion_cta', value: opts.cta },
      { objectTypeId: '0-1', name: 'form_url', value: pageUrl }
    ];
    if (opts.notes) fields.push({ objectTypeId: '0-1', name: 'contact_us_notes', value: opts.notes });
    (opts.extra || []).forEach(function (f) { if (f.value) fields.push({ objectTypeId: '0-1', name: f.name, value: f.value }); });
    var u = utms();
    KEYS.forEach(function (k) { if (u[k]) fields.push({ objectTypeId: '0-1', name: k, value: u[k] }); });

    var context = { pageUri: pageUrl, pageName: document.title };
    var hutk = cookie('hubspotutk');
    if (hutk) context.hutk = hutk;

    return fetch('https://api.hsforms.com/submissions/v3/integration/submit/' + CFG.portal + '/' + CFG.form, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fields: fields,
        context: context,
        legalConsentOptions: { legitimateInterest: {
          value: true, subscriptionTypeId: CFG.consent.subscriptionTypeId,
          legalBasis: CFG.consent.legalBasis, text: CFG.consent.text } }
      })
    }).then(function (r) {
      if (r.ok) return true;
      return r.text().then(function (t) {
        if (window.console) console.warn('HubSpot form error', r.status, t);
        throw new Error('hubspot_' + r.status);
      });
    });
  }

  window.WhyUserHS = { submit: submit, utms: utms };
})();
