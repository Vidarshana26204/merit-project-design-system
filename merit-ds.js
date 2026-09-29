/* ============================================================
   MERIT DS — interactions (vanilla)
   copy buttons · code tabs · scroll-spy · live widgets
   ============================================================ */
(function () {
  'use strict';

  /* ---------- copy-to-clipboard (code blocks) ---------- */
  function wireCopy() {
    document.querySelectorAll('.copyBtn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrap = btn.closest('.codeBody');
        var visible = wrap.querySelector('pre:not([hidden]) code');
        var text = visible ? visible.innerText : '';
        navigator.clipboard.writeText(text).then(function () {
          var prev = btn.querySelector('.lbl').textContent;
          btn.classList.add('done');
          btn.querySelector('.lbl').textContent = 'Copied!';
          setTimeout(function () {
            btn.classList.remove('done');
            btn.querySelector('.lbl').textContent = prev;
          }, 1300);
        });
      });
    });
  }

  /* ---------- code tabs (CSS / Flutter / HTML) ---------- */
  function wireTabs() {
    document.querySelectorAll('.codeWrap').forEach(function (wrap) {
      var tabs = wrap.querySelectorAll('.codeTabs button');
      var panes = wrap.querySelectorAll('.codeBody pre');
      tabs.forEach(function (tab, i) {
        tab.addEventListener('click', function () {
          tabs.forEach(function (t) { t.classList.remove('active'); });
          panes.forEach(function (p) { p.hidden = true; });
          tab.classList.add('active');
          if (panes[i]) panes[i].hidden = false;
        });
      });
    });
  }

  /* ---------- copy hex on swatch click ---------- */
  function wireSwatches() {
    document.querySelectorAll('.sw').forEach(function (sw) {
      sw.addEventListener('click', function () {
        var hex = sw.getAttribute('data-hex');
        if (!hex) return;
        navigator.clipboard.writeText(hex);
        var tag = sw.querySelector('.copytag');
        if (tag) {
          var prev = tag.textContent;
          tag.textContent = 'COPIED';
          setTimeout(function () { tag.textContent = prev; }, 1100);
        }
      });
    });
  }

  /* ---------- live toggles / checkboxes ---------- */
  function wireToggles() {
    document.querySelectorAll('.toggle').forEach(function (t) {
      t.addEventListener('click', function () { t.classList.toggle('on'); });
    });
    document.querySelectorAll('.check:not(.done)').forEach(function (c) {
      c.addEventListener('click', function () {
        c.classList.toggle('on');
        c.textContent = c.classList.contains('on') ? '✓' : '';
      });
    });
  }

  /* ---------- demo progress: animate on first view ---------- */
  function wireProgress() {
    var bars = document.querySelectorAll('.progress > i[data-w]');
    if (!('IntersectionObserver' in window)) {
      bars.forEach(function (b) { b.style.width = b.getAttribute('data-w'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.style.width = e.target.getAttribute('data-w');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.5 });
    bars.forEach(function (b) { b.style.width = '0%'; io.observe(b); });
  }

  /* ---------- scroll-spy nav ---------- */
  function wireScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll('nav.toc a'));
    var map = {};
    links.forEach(function (l) {
      var id = l.getAttribute('href').slice(1);
      var sec = document.getElementById(id);
      if (sec) map[id] = l;
    });
    var ids = Object.keys(map);
    if (!ids.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (l) { l.classList.remove('active'); });
          if (map[e.target.id]) map[e.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px', threshold: 0 });
    ids.forEach(function (id) { io.observe(document.getElementById(id)); });

    links.forEach(function (l) {
      l.addEventListener('click', function () {
        links.forEach(function (x) { x.classList.remove('active'); });
        l.classList.add('active');
      });
    });
  }

  /* ---------- token reference table (§24) ----------
     Reads live computed values off build/css/merit-tokens.css — never a
     hand-copied hex. The NAME list below must be kept in sync with
     tokens/semantic.*.tokens.json keys (rare: only on add/remove); the
     VALUES always reflect whatever is actually shipped. */
  var SEMANTIC_TOKENS = [
    'bg-app', 'bg-brand', 'surface-default', 'surface-sunken', 'surface-inverse',
    'surface-selected', 'text-primary', 'text-secondary', 'text-tertiary',
    'text-link', 'border-default', 'border-subtle', 'action-primary',
    'action-primary-pressed', 'action-accent', 'feedback-success',
    'feedback-warning', 'feedback-error', 'focus-ring'
  ];

  function buildTokenTable() {
    var host = document.getElementById('tokenRefTable');
    if (!host) return;
    var root = getComputedStyle(document.documentElement);
    var darkEl = document.createElement('div');
    darkEl.className = 'dark';
    darkEl.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none';
    document.body.appendChild(darkEl);
    var dark = getComputedStyle(darkEl);

    var rows = SEMANTIC_TOKENS.map(function (name) {
      var varName = '--merit-' + name;
      var light = (root.getPropertyValue(varName) || '').trim();
      var d = (dark.getPropertyValue(varName) || '').trim();
      if (!light) return '';
      return '<tr>' +
        '<td><code>' + name + '</code></td>' +
        '<td><span style="display:inline-flex;align-items:center;gap:6px">' +
          '<span style="width:14px;height:14px;border-radius:4px;border:1.5px solid var(--line);background:' + light + ';display:inline-block"></span>' +
          '<code>' + light + '</code></span></td>' +
        '<td><span style="display:inline-flex;align-items:center;gap:6px">' +
          '<span style="width:14px;height:14px;border-radius:4px;border:1.5px solid var(--line);background:' + d + ';display:inline-block"></span>' +
          '<code>' + d + '</code></span></td>' +
        '<td class="mono">var(' + varName + ')</td>' +
        '</tr>';
    }).join('');

    document.body.removeChild(darkEl);
    host.innerHTML = '<table class="spec">' +
      '<thead><tr><th>Token</th><th>Light</th><th>Dark</th><th>CSS</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>';
  }

  function init() {
    wireCopy(); wireTabs(); wireSwatches(); wireToggles();
    wireProgress(); wireScrollSpy(); buildTokenTable();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
