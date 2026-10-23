/* ============================================================
   MERIT DS v3 — reference-site interactions (vanilla, no deps)
   Everything colour-related reads live CSS custom properties from
   build/css/merit-tokens.css, so the site can never drift from what ships.
   ============================================================ */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var cssVar = function (name, el) { return getComputedStyle(el || document.documentElement).getPropertyValue(name).trim(); };

  /* Resolve any CSS colour (incl. var()) to #RRGGBB via a probe element. */
  function hexOf(value) {
    var probe = document.createElement('i');
    probe.style.color = value;
    document.body.appendChild(probe);
    var m = getComputedStyle(probe).color.match(/[\d.]+/g).map(Number);
    probe.remove();
    return '#' + m.slice(0, 3).map(function (n) { return Math.round(n).toString(16).padStart(2, '0'); }).join('').toUpperCase();
  }
  function luminance(hex) {
    var c = [1, 3, 5].map(function (i) { return parseInt(hex.slice(i, i + 2), 16) / 255; })
      .map(function (v) { return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  function contrast(a, b) {
    var x = luminance(a), y = luminance(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  }

  /* ---------- General Sans: local first, Fontshare CDN fallback ---------- */
  function ensureDisplayFont() {
    if (!document.fonts || !document.fonts.load) return;
    document.fonts.load('600 16px "General Sans"').then(function (faces) {
      if (faces.length) return;
      var l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = 'https://api.fontshare.com/v2/css?f[]=general-sans@500,600,700,500i,600i,700i&display=swap';
      document.head.appendChild(l);
    }).catch(function () {});
  }

  /* ---------- theme ---------- */
  function wireTheme() {
    var btn = $('#themeBtn');
    var root = document.documentElement;
    var saved = null;
    try { saved = localStorage.getItem('merit-ds-theme'); } catch (e) {}
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    apply(saved || (prefersDark ? 'dark' : 'light'));
    btn.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(next);
      try { localStorage.setItem('merit-ds-theme', next); } catch (e) {}
    });
    function apply(theme) {
      root.dataset.theme = theme;
      var dark = theme === 'dark';
      btn.setAttribute('aria-pressed', String(dark));
      btn.querySelector('i').className = dark ? 'ph ph-sun' : 'ph ph-moon';
      btn.querySelector('span').textContent = dark ? 'Light' : 'Dark';
      renderSwatches();
    }
  }

  /* ---------- mobile nav ---------- */
  function wireMenu() {
    var btn = $('#menuBtn'), side = $('#side');
    btn.addEventListener('click', function () {
      var open = side.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
    $$('.toc a').forEach(function (a) {
      a.addEventListener('click', function () { side.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); });
    });
  }

  /* ---------- swatches (data-swatches="token:role token:role") ---------- */
  function renderSwatches() {
    $$('[data-swatches]').forEach(function (host) {
      var items = host.getAttribute('data-swatches').split(/\s(?=[a-z]+-?\d*:)/);
      host.innerHTML = items.map(function (item) {
        var i = item.indexOf(':');
        var tok = item.slice(0, i), role = item.slice(i + 1);
        var hex = hexOf('var(--merit-' + tok + ')');
        var fg = contrast(hex, '#1E1B2E') >= contrast(hex, '#FFFFFF') ? '#1E1B2E' : '#FFFFFF';
        return '<button class="sw" data-hex="' + hex + '" aria-label="Copy ' + hex + '">' +
          '<span class="swc" style="background:' + hex + ';color:' + fg + '"><span>' + hex + '</span><span class="copytag">COPY</span></span>' +
          '<span class="meta"><b>' + tok + '</b>' + role + '</span></button>';
      }).join('');
    });
  }
  function wireSwatchCopy() {
    document.addEventListener('click', function (e) {
      var sw = e.target.closest('.sw');
      if (!sw || !navigator.clipboard) return;
      navigator.clipboard.writeText(sw.dataset.hex).then(function () {
        var tag = sw.querySelector('.copytag');
        tag.textContent = 'COPIED';
        setTimeout(function () { tag.textContent = 'COPY'; }, 1100);
      });
    });
  }

  /* ---------- code blocks ---------- */
  function wireCode() {
    $$('.codeWrap').forEach(function (wrap) {
      var tabs = $$('.codeTabs button', wrap), panes = $$('.codeBody pre', wrap);
      tabs.forEach(function (tab, i) {
        tab.addEventListener('click', function () {
          tabs.forEach(function (t) { t.classList.remove('active'); });
          panes.forEach(function (p) { p.hidden = true; });
          tab.classList.add('active');
          panes[i].hidden = false;
        });
      });
      var copy = $('.copyBtn', wrap);
      copy.addEventListener('click', function () {
        var code = $('pre:not([hidden]) code', wrap);
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(code.innerText).then(function () {
          copy.classList.add('done'); $('.lbl', copy).textContent = 'Copied';
          setTimeout(function () { copy.classList.remove('done'); $('.lbl', copy).textContent = 'Copy'; }, 1300);
        });
      });
    });
  }

  /* ---------- live controls ---------- */
  function wireControls() {
    $$('.toggle').forEach(function (t) {
      t.addEventListener('click', function () { t.setAttribute('aria-pressed', String(t.classList.toggle('on'))); });
    });
    $$('button.check').forEach(function (c) {
      c.addEventListener('click', function () { var on = c.classList.toggle('on'); c.textContent = on ? '✓' : ''; });
    });
    $$('.chips, .seg').forEach(function (group) {
      var single = group.classList.contains('seg');
      $$('button', group).forEach(function (b) {
        b.addEventListener('click', function () {
          if (single) $$('button', group).forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
          b.setAttribute('aria-pressed', single ? 'true' : String(b.getAttribute('aria-pressed') !== 'true'));
        });
      });
    });
    $$('.qcard button.opt').forEach(function (o) {
      o.addEventListener('click', function () {
        $$('button.opt', o.closest('.qcard')).forEach(function (x) { x.classList.remove('sel'); x.removeAttribute('aria-pressed'); });
        o.classList.add('sel'); o.setAttribute('aria-pressed', 'true');
      });
    });
    var flash = $('#flashCard');
    if (flash) flash.addEventListener('click', function () { flash.classList.toggle('flipped'); });
  }

  /* ---------- progress bars animate on first view ---------- */
  function wireProgress() {
    var bars = $$('.progress > i[data-w]');
    var fill = function (b) { b.style.width = b.getAttribute('data-w'); };
    if (!('IntersectionObserver' in window)) { bars.forEach(fill); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { fill(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.4 });
    bars.forEach(function (b) { io.observe(b); });
  }

  /* ---------- scroll-spy ---------- */
  function wireScrollSpy() {
    var links = $$('nav.toc a'), map = {};
    links.forEach(function (l) { map[l.getAttribute('href').slice(1)] = l; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting || !map[e.target.id]) return;
        links.forEach(function (l) { l.classList.remove('active'); l.removeAttribute('aria-current'); });
        map[e.target.id].classList.add('active');
        map[e.target.id].setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    $$('section.sec').forEach(function (s) { io.observe(s); });
  }

  /* ---------- generated specimens ---------- */
  var TYPE_STYLES = ['display-xl', 'display-lg', 'display-md', 'title-lg', 'title-md', 'title-sm', 'emphasis-lg', 'emphasis-md',
    'body-lg', 'body-md', 'body-sm', 'label-md', 'label-sm', 'eyebrow', 'numeric-xl', 'numeric-lg', 'numeric-md'];
  function renderType() {
    var host = $('#typeTable'); if (!host) return;
    host.innerHTML = TYPE_STYLES.map(function (s) {
      var p = '--merit-type-' + s + '-';
      var size = cssVar(p + 'size'), w = cssVar(p + 'weight'), lh = cssVar(p + 'line-height'), tr = cssVar(p + 'tracking');
      var fam = cssVar(p + 'family').split(',')[0].replace(/['"]/g, '');
      var style = 'font-family:var(' + p + 'family);font-size:min(' + size + ',9vw);font-weight:' + w + ';line-height:' + lh + ';letter-spacing:' + tr +
        ';text-transform:' + (cssVar(p + 'transform') || 'none') + ';font-style:' + (cssVar(p + 'style') || 'normal') + ';font-variant-numeric:' + (cssVar(p + 'numeric') || 'normal');
      var sample = /^numeric/.test(s) ? '04:59 · 1,240' : /^(label|eyebrow)/.test(s) ? 'Past papers' : /^emphasis/.test(s) ? 'Keep your streak alive' : 'Hit your weak spots first';
      return '<tr><td><code>type.' + s.replace('-', '.') + '</code></td><td><span style="' + style + '">' + sample + '</span></td>' +
        '<td class="muted">' + fam + ' · ' + size + ' / ' + lh + ' · ' + w + (tr && tr !== '0em' ? ' · ' + tr : '') + '</td></tr>';
    }).join('');
  }
  function renderRadius() {
    var host = $('#radiusTable'); if (!host) return;
    var uses = { xs: 'Tiny chips', sm: 'Icon & letter chips', md: 'Inputs, quiz options', lg: 'Small cards, tiles', xl: 'Cards', '2xl': 'Sheets, bands', pill: 'Buttons, chips, search' };
    host.innerHTML = Object.keys(uses).map(function (k) {
      var v = cssVar('--merit-radius-' + k);
      return '<tr><td><code>' + k + '</code></td><td><span class="dot" style="width:22px;height:22px;border-radius:' + (k === 'pill' ? '11px' : 'min(' + v + ',11px)') + ';background:var(--merit-surface-selected)"></span>' + v + '</td><td>' + uses[k] + '</td></tr>';
    }).join('');
  }
  function renderSpace() {
    var host = $('#spaceScale'); if (!host) return;
    host.innerHTML = ['1', '2', '3', '4', '5', '6', '8', '10', '12', '16'].map(function (k) {
      var v = cssVar('--merit-space-' + k);
      return '<div class="row"><code style="width:72px">space.' + k + '</code><span style="display:inline-block;height:14px;width:' + v + ';border-radius:4px;background:var(--merit-action-primary)"></span><span class="muted">' + v + '</span></div>';
    }).join('');
  }
  var PATTERNS = ['dots', 'halftone', 'stripes', 'checks', 'hatch', 'waves', 'zigzag', 'chevron', 'triangles', 'grid', 'plus', 'arcs', 'diamonds', 'scales', 'bricks', 'dashes'];
  var SUBJECTS = [['biology', 'Biology', 1], ['physics', 'Physics', 2], ['chemistry', 'Chemistry', 3], ['maths', 'Combined Maths', 4], ['ict', 'ICT', 5], ['languages', 'Languages', 6]];
  function renderSubjects() {
    var b = $('#subjBadges');
    if (b) b.innerHTML = SUBJECTS.map(function (s) {
      return '<span class="subj" style="background:var(--merit-category-' + s[2] + ')"><img src="assets/v3/patchwork-demo/' + s[0] + '-mono.svg" alt="" />' + s[1] + '</span>';
    }).join('');
    var t = $('#tiles');
    if (t) t.innerHTML = SUBJECTS.map(function (s) {
      return '<div class="card" style="padding:14px;text-align:center"><img src="assets/v3/patchwork-demo/' + s[0] + '-tile.svg" alt="" style="width:100%;max-width:120px" /><h4 style="margin-top:8px">' + s[1] + '</h4></div>';
    }).join('');
    var pw = $('#pwPatterns');
    if (pw) pw.innerHTML = PATTERNS.map(function (n) {
      return '<figure><img src="assets/v3/patchwork-demo/pattern-' + n + '.svg" alt="" /><figcaption>' + n + '</figcaption></figure>';
    }).join('');
  }
  function renderGrades() {
    var g = $('#grades'); if (!g) return;
    g.innerHTML = 'abcdef'.split('').map(function (l) {
      return '<span class="grade" style="width:44px;height:44px;font-size:20px;border-radius:14px;background:var(--merit-grade-' + l + '-bg);color:var(--merit-grade-' + l + '-fg)">' + l.toUpperCase() + '</span>';
    }).join('');
  }
  var ICONS = [['house', 'fill'], ['books', ''], ['exam', ''], ['trophy', ''], ['user', ''], ['flame', 'fill'], ['coins', 'fill'], ['crown', 'fill'], ['timer', ''], ['flag', ''],
    ['bookmark-simple', ''], ['lightbulb', ''], ['check-circle', 'fill'], ['x-circle', 'fill'], ['lock-simple', ''], ['magnifying-glass', ''], ['dna', 'duotone'], ['atom', 'duotone'], ['flask', 'duotone'], ['function', 'duotone'], ['cpu', 'duotone'], ['translate', 'duotone']];
  function renderIcons() {
    var g = $('#iconGrid'); if (!g) return;
    g.innerHTML = ICONS.map(function (i) {
      var cls = i[1] ? 'ph-' + i[1] : 'ph';
      var color = i[0] === 'flame' ? ';color:var(--merit-reward-streak)' : i[1] === 'duotone' ? ';color:var(--merit-text-link)' : '';
      return '<div><i class="' + cls + ' ph-' + i[0] + '" style="' + color.slice(1) + '"></i>' + i[0] + '<br><span style="opacity:.7">' + (i[1] || 'regular') + '</span></div>';
    }).join('');
  }
  function renderCharts() {
    var bars = $('#bars'), legend = $('#legend');
    if (bars) {
      var data = [['Biology', 82], ['Chemistry', 64], ['Physics', 71], ['Maths', 48], ['ICT', 90]];
      bars.innerHTML = data.map(function (d, i) {
        return '<div class="b" role="img" aria-label="' + d[0] + ' ' + d[1] + '%" title="' + d[0] + ': ' + d[1] + '%" style="height:' + d[1] + '%;background:var(--merit-chart-' + (i + 1) + ')"></div>';
      }).join('');
      legend.innerHTML = data.map(function (d, i) { return '<span><span class="dot" style="background:var(--merit-chart-' + (i + 1) + ')"></span>' + d[0] + ' ' + d[1] + '%</span>'; }).join('');
    }
    var heat = $('#heat');
    if (heat) {
      var cells = '';
      for (var i = 0; i < 105; i++) { var v = (i * 37 + (i % 7) * 11) % 9; cells += '<i class="' + (v > 6 ? 'h3' : v > 4 ? 'h2' : v > 2 ? 'h1' : '') + '"></i>'; }
      heat.innerHTML = cells;
    }
  }
  function renderDarkCompare() {
    var host = $('#darkCompare'); if (!host) return;
    var mk = function (theme) {
      return '<div data-theme="' + theme + '" class="panel" style="background:var(--merit-bg-app)">' +
        '<span class="label">' + theme + '</span>' +
        '<div class="card"><div class="row" style="justify-content:space-between"><h4 style="color:var(--merit-text-primary)">Enzymes</h4><span class="badge violet">Pro</span></div>' +
        '<p class="muted" style="margin:4px 0 10px">Biology · 64% complete</p><div class="progress"><i style="width:64%"></i></div>' +
        '<div class="row" style="margin-top:14px"><button class="btn primary sm">Continue</button><a href="#dark">Details</a></div></div></div>';
    };
    host.innerHTML = mk('light') + mk('dark');
  }

  /* ---------- token reference (§30) ----------
     NAMES must match tokens/semantic.*.tokens.json (only on add/remove);
     VALUES are always read live from the shipped CSS. */
  var SEMANTIC_TOKENS = [
    'bg-app', 'bg-brand', 'surface-default', 'surface-sunken', 'surface-inverse', 'surface-selected', 'surface-feature',
    'text-primary', 'text-secondary', 'text-tertiary', 'text-link', 'text-eyebrow',
    'text-on-primary', 'text-on-primary-strong', 'text-on-accent', 'text-on-feature', 'text-on-inverse', 'text-on-success', 'text-on-warning', 'text-on-error',
    'border-default', 'border-strong', 'border-subtle',
    'action-primary', 'action-primary-pressed', 'action-primary-strong', 'action-accent', 'action-accent-pressed',
    'feedback-success', 'feedback-success-subtle', 'feedback-success-text', 'feedback-warning', 'feedback-error', 'feedback-error-subtle',
    'focus-ring', 'decor-sparkle', 'decor-sparkle-warm', 'decor-underline', 'decor-connector'
  ];
  function buildTokenTable() {
    var host = $('#tokenRefTable'); if (!host) return;
    var probe = function (theme) {
      var el = document.createElement('div');
      el.setAttribute('data-theme', theme);
      el.style.cssText = 'position:absolute;visibility:hidden';
      document.body.appendChild(el);
      return el;
    };
    var lt = probe('light'), dk = probe('dark');
    var cell = function (v) { return '<td><span class="dot" style="background:' + v + '"></span><code>' + v + '</code></td>'; };
    var rows = SEMANTIC_TOKENS.map(function (n) {
      var v = '--merit-' + n;
      return '<tr><td><code>' + n + '</code></td>' + cell(cssVar(v, lt)) + cell(cssVar(v, dk)) + '<td class="mono">var(' + v + ')</td></tr>';
    });
    ['e1', 'e2', 'e3'].forEach(function (e) {
      rows.push('<tr><td><code>elevation-' + e + '</code></td><td colspan="2"><span class="dot" style="background:var(--merit-surface-default);box-shadow:var(--merit-elevation-' + e + ')"></span><span class="muted">soft, themed</span></td><td class="mono">var(--merit-elevation-' + e + ')</td></tr>');
    });
    lt.remove(); dk.remove();
    host.innerHTML = '<table class="spec"><thead><tr><th>Token</th><th>Light</th><th>Dark</th><th>CSS</th></tr></thead><tbody>' + rows.join('') + '</tbody></table>';
  }

  function init() {
    ensureDisplayFont();
    renderType(); renderRadius(); renderSpace(); renderSubjects(); renderGrades(); renderIcons(); renderCharts(); renderDarkCompare();
    wireTheme(); wireMenu(); wireSwatchCopy(); wireCode(); wireControls(); wireProgress(); wireScrollSpy(); buildTokenTable();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
