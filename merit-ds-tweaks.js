/* ============================================================
   MERIT DS — Tweaks panel (vanilla, no React/Babel)
   Hidden by default. Opens only when a host editor posts
   __activate_edit_mode; keeps the same host protocol as the old
   tweaks-panel.jsx (__edit_mode_available / __edit_mode_set_keys /
   __edit_mode_dismissed), so EDITMODE-BEGIN/END persistence still works.

   Usage: define window.MERIT_TWEAKS = {defaults, controls} before this
   script. controls: [{section}] | [{key,label,type:'radio',options}] |
   [{key,label,type:'toggle'}]. `apply(values)` is called on every change.
   ============================================================ */
(function () {
  'use strict';
  var cfg = window.MERIT_TWEAKS;
  if (!cfg) return;

  var values = Object.assign({}, cfg.defaults);
  var panel = null;

  function post(msg) {
    if (window.parent && window.parent !== window) window.parent.postMessage(msg, '*');
  }

  function set(key, val) {
    values[key] = val;
    cfg.apply(values);
    var edits = {}; edits[key] = val;
    post({ type: '__edit_mode_set_keys', edits: edits });
    render();
  }

  var CSS =
    '.twk{position:fixed;right:16px;bottom:16px;z-index:2147483646;width:260px;' +
    'background:var(--cream);color:var(--ink);border:2px solid var(--line);border-radius:16px;' +
    'box-shadow:5px 5px 0 var(--line);font:600 12px/1.4 var(--font-body);overflow:hidden}' +
    '.twk-hd{display:flex;align-items:center;justify-content:space-between;padding:10px 10px 10px 14px;' +
    'background:var(--ink);color:var(--cream);cursor:move;user-select:none;font-family:var(--font-display);font-weight:700;font-size:13px}' +
    '.twk-x{border:1.5px solid var(--cream);background:transparent;color:var(--cream);border-radius:8px;' +
    'width:26px;height:26px;cursor:pointer;font:700 12px/1 var(--font-body)}' +
    '.twk-bd{padding:12px 14px 14px;display:flex;flex-direction:column;gap:10px}' +
    '.twk-sect{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--text-mute)}' +
    '.twk-row{display:flex;flex-direction:column;gap:6px}' +
    '.twk-row.h{flex-direction:row;align-items:center;justify-content:space-between}' +
    '.twk-seg{display:flex;gap:4px}' +
    '.twk-seg button{flex:1;border:2px solid var(--line);border-radius:99px;background:#fff;color:var(--ink);' +
    'padding:6px 4px;font:700 11px/1 var(--font-body);cursor:pointer}' +
    '.twk-seg button[aria-checked="true"]{background:var(--purple);color:#fff}' +
    '.twk button:focus-visible{outline:3px solid var(--purple);outline-offset:2px}';

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'on') Object.keys(attrs.on).forEach(function (ev) { n.addEventListener(ev, attrs.on[ev]); });
      else if (k === 'text') n.textContent = attrs.text;
      else n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }

  function control(c) {
    if (c.section) return el('div', { class: 'twk-sect', text: c.section });
    if (c.type === 'radio') {
      return el('div', { class: 'twk-row' }, [
        el('span', { text: c.label }),
        el('div', { class: 'twk-seg', role: 'radiogroup', 'aria-label': c.label },
          c.options.map(function (o) {
            return el('button', {
              type: 'button', role: 'radio', 'aria-checked': String(values[c.key] === o), text: o,
              on: { click: function () { set(c.key, o); } }
            });
          }))
      ]);
    }
    if (c.type === 'toggle') {
      var sw = el('span', {
        class: 'toggle' + (values[c.key] ? ' on' : ''), role: 'switch', tabindex: '0',
        'aria-checked': String(!!values[c.key]), 'aria-label': c.label
      });
      // Created after merit-ds.js wires page toggles, so only this handler runs.
      sw.addEventListener('click', function () { set(c.key, !values[c.key]); });
      sw.addEventListener('keydown', function (e) {
        if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); set(c.key, !values[c.key]); }
      });
      return el('div', { class: 'twk-row h' }, [el('span', { text: c.label }), sw]);
    }
    return null;
  }

  function dragFrom(e) {
    if (e.target.closest('.twk-x')) return;
    var r = panel.getBoundingClientRect(), sx = e.clientX, sy = e.clientY;
    var right0 = window.innerWidth - r.right, bottom0 = window.innerHeight - r.bottom;
    function move(ev) {
      var maxR = window.innerWidth - panel.offsetWidth - 16, maxB = window.innerHeight - panel.offsetHeight - 16;
      panel.style.right = Math.min(maxR, Math.max(16, right0 - (ev.clientX - sx))) + 'px';
      panel.style.bottom = Math.min(maxB, Math.max(16, bottom0 - (ev.clientY - sy))) + 'px';
    }
    function up() { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up); }
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
  }

  function render() {
    if (!panel) return;
    var body = panel.querySelector('.twk-bd');
    body.textContent = '';
    cfg.controls.forEach(function (c) { var n = control(c); if (n) body.appendChild(n); });
  }

  function open() {
    if (panel) return;
    panel = el('div', { class: 'twk', role: 'dialog', 'aria-label': 'Tweaks' }, [
      el('div', { class: 'twk-hd', on: { pointerdown: dragFrom } }, [
        el('span', { text: cfg.title || 'Tweaks' }),
        el('button', { class: 'twk-x', type: 'button', 'aria-label': 'Close tweaks', text: '✕', on: { click: dismiss } })
      ]),
      el('div', { class: 'twk-bd' })
    ]);
    document.body.appendChild(panel);
    render();
  }

  function close() { if (panel) { panel.remove(); panel = null; } }
  function dismiss() { close(); post({ type: '__edit_mode_dismissed' }); }

  document.head.appendChild(el('style', { text: CSS }));
  cfg.apply(values);
  window.addEventListener('message', function (e) {
    var t = e && e.data && e.data.type;
    if (t === '__activate_edit_mode') open();
    else if (t === '__deactivate_edit_mode') close();
  });
  post({ type: '__edit_mode_available' });
})();
