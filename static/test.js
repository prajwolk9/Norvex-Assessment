(function () {
  "use strict";
  var csrf = document.querySelector('meta[name=csrf]').content;
  var saved = JSON.parse(document.getElementById('saved').textContent || '{}');
  var qs = Array.prototype.slice.call(document.querySelectorAll('.q'));
  var saveState = document.getElementById('savestate');

  function el(tag, attrs) {
    var e = document.createElement(tag);
    for (var k in (attrs || {})) { if (k === 'text') e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]); }
    for (var i = 2; i < arguments.length; i++) { if (arguments[i]) e.appendChild(arguments[i]); }
    return e;
  }
  function select(opts, blank) {
    var s = el('select');
    s.appendChild(el('option', { value: '', text: blank || '—' }));
    opts.forEach(function (o) { s.appendChild(el('option', { value: o, text: o })); });
    return s;
  }

  // ---------- render + collect per type -------------------------------------
  function render(q) {
    var type = q.dataset.type, id = q.dataset.id;
    var opts = JSON.parse(q.dataset.opts || '[]'), cfg = JSON.parse(q.dataset.cfg || '{}');
    var box = q.querySelector('.inputs'), val = saved[id];

    if (type === 'single' || type === 'multi') {
      opts.forEach(function (o) {
        var inp = el('input', { type: type === 'single' ? 'radio' : 'checkbox', name: 'q' + id, value: o });
        box.appendChild(el('label', { 'class': 'opt' }, inp, el('span', { text: ' ' + o })));
      });
      q._get = function () {
        var c = q.querySelectorAll('input:checked');
        if (type === 'single') return c.length ? c[0].value : null;
        return Array.prototype.map.call(c, function (x) { return x.value; });
      };
      q._set = function (v) {
        if (v == null) return;
        var arr = type === 'single' ? [v] : v;
        q.querySelectorAll('input').forEach(function (i) { i.checked = arr.indexOf(i.value) >= 0; });
      };
    } else if (type === 'fields') {
      cfg.fields.forEach(function (f) {
        var inp = f.kind === 'select' ? select(f.opts) : el('input', { type: 'text', placeholder: f.ph || '' });
        inp.className = 'fld';
        box.appendChild(el('label', { 'class': 'field' }, el('span', { text: f.label }), inp));
      });
      q._get = function () { return Array.prototype.map.call(q.querySelectorAll('.fld'), function (x) { return x.value; }); };
      q._set = function (v) { (v || []).forEach(function (x, i) { var f = q.querySelectorAll('.fld')[i]; if (f) f.value = x; }); };
    } else if (type === 'time_mmss') {
      box.appendChild(el('label', { 'class': 'field' }, el('span', { text: 'Minutes' }), el('input', { type: 'number', min: 0, max: 20, 'class': 'm' })));
      box.appendChild(el('label', { 'class': 'field' }, el('span', { text: 'Seconds' }), el('input', { type: 'number', min: 0, max: 59, 'class': 's' })));
      q._get = function () { var m = q.querySelector('.m').value, s = q.querySelector('.s').value; return (m === '' && s === '') ? null : [m, s]; };
      q._set = function (v) { if (v) { q.querySelector('.m').value = v[0]; q.querySelector('.s').value = v[1]; } };
    } else if (type === 'time_sec') {
      box.appendChild(el('label', { 'class': 'field' }, el('span', { text: 'Time (seconds)' }), el('input', { type: 'number', min: 0, max: 1200, 'class': 'sec' })));
      q._get = function () { var v = q.querySelector('.sec').value; return v === '' ? null : v; };
      q._set = function (v) { if (v != null) q.querySelector('.sec').value = v; };
    } else if (type === 'table') {
      var t = el('table', { 'class': 'grid' });
      t.appendChild(el('tr', {}, el('th', { text: 'Section #' }), el('th', { text: 'Start time (min : sec)' }), el('th', { text: 'Section name' })));
      for (var r = 0; r < cfg.rows; r++) {
        var tr = el('tr', { 'class': 'row' });
        tr.appendChild(el('td', { text: String(r + 1) }));
        tr.appendChild(el('td', {}, el('input', { type: 'number', min: 0, max: 20, 'class': 'm', placeholder: 'min' }), el('span', { text: ' : ' }), el('input', { type: 'number', min: 0, max: 59, 'class': 's', placeholder: 'sec' })));
        var sel = select(cfg.names); sel.className = 'n';
        tr.appendChild(el('td', {}, sel));
        t.appendChild(tr);
      }
      box.appendChild(t);
      q._get = function () {
        return Array.prototype.map.call(q.querySelectorAll('tr.row'), function (r) {
          return [r.querySelector('.m').value, r.querySelector('.s').value, r.querySelector('.n').value];
        });
      };
      q._set = function (v) {
        (v || []).forEach(function (row, i) {
          var r = q.querySelectorAll('tr.row')[i]; if (!r) return;
          r.querySelector('.m').value = row[0]; r.querySelector('.s').value = row[1]; r.querySelector('.n').value = row[2];
        });
      };
    } else if (type === 'chords') {
      var list = el('div', { 'class': 'chords' });
      var addBtn = el('button', { type: 'button', 'class': 'btn small ghost', text: '+ Add chord' });
      var roman = el('input', { type: 'text', 'class': 'roman', placeholder: 'e.g. ii, V, I' });
      function addRow(v) {
        if (list.children.length >= cfg.max) return;
        var row = el('div', { 'class': 'crow' });
        row.appendChild(el('span', { 'class': 'cn', text: String(list.children.length + 1) }));
        var root = select(cfg.roots, 'root'); root.className = 'c0';
        row.appendChild(root);
        var acc = null;
        if (cfg.acc) { acc = select(['#', 'b'], '♮'); acc.className = 'cacc'; row.appendChild(acc); }
        var ql = select(cfg.quals, 'quality'); ql.className = 'c1';
        var nm = select(cfg.nums, 'number'); nm.className = 'c2';
        row.appendChild(ql); row.appendChild(nm);
        var rm = el('button', { type: 'button', 'class': 'link', text: '✕' });
        rm.addEventListener('click', function () { row.remove(); renum(); q.dispatchEvent(new Event('change', { bubbles: true })); });
        row.appendChild(rm);
        list.appendChild(row);
        if (v) {
          var r0 = v[0] || '';
          if (acc && r0.length > 1 && (r0.slice(-1) === '#' || r0.slice(-1) === 'b')) { acc.value = r0.slice(-1); r0 = r0.slice(0, -1); }
          root.value = r0; ql.value = v[1] || ''; nm.value = v[2] || '';
        }
      }
      function renum() { Array.prototype.forEach.call(list.children, function (r, i) { r.querySelector('.cn').textContent = i + 1; }); }
      addBtn.addEventListener('click', function () { addRow(); });
      box.appendChild(list); box.appendChild(addBtn);
      box.appendChild(el('label', { 'class': 'field' }, el('span', { text: 'Roman-numeral scale degrees (if requested)' }), roman));
      q._get = function () {
        var rows = Array.prototype.map.call(list.children, function (r) {
          var a = r.querySelector('.cacc');
          return [r.querySelector('.c0').value + (a ? a.value : ''), r.querySelector('.c1').value, r.querySelector('.c2').value];
        }).filter(function (c) { return c[0] || c[1] || c[2]; });
        return { c: rows, r: roman.value };
      };
      q._set = function (v) { if (!v) return; (v.c || []).forEach(addRow); roman.value = v.r || ''; };
      if (!val) { addRow(); addRow(); addRow(); addRow(); }
    }
    if (val != null) q._set(val);
  }

  function isAnswered(q) {
    var a = q._get();
    if (a == null) return false;
    if (Array.isArray(a)) {
      if (!a.length) return false;
      return a.some(function (x) { return Array.isArray(x) ? x.some(Boolean) : (x !== '' && x != null); });
    }
    if (typeof a === 'object') return (a.c && a.c.length) || a.r;
    return a !== '';
  }
  function updateProgress() {
    var n = qs.filter(isAnswered).length;
    document.getElementById('progress').textContent = n + ' / ' + qs.length + ' answered';
  }

  // ---------- autosave -------------------------------------------------------
  var timers = {};
  function save(q) {
    saveState.textContent = 'Saving…';
    fetch('/api/answer', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRF': csrf },
      body: JSON.stringify({ q: parseInt(q.dataset.id, 10), a: q._get() })
    }).then(function (r) {
      saveState.textContent = r.ok ? 'Saved ✓' : 'Could not save — check your connection';
    }).catch(function () { saveState.textContent = 'Could not save — check your connection'; });
  }
  qs.forEach(function (q) {
    render(q);
    var h = function () { clearTimeout(timers[q.dataset.id]); timers[q.dataset.id] = setTimeout(function () { save(q); updateProgress(); }, 500); };
    q.addEventListener('change', h); q.addEventListener('input', h);
  });
  updateProgress();

  document.getElementById('testform').addEventListener('submit', function (e) {
    var unanswered = qs.length - qs.filter(isAnswered).length;
    if (!confirm((unanswered ? unanswered + ' question(s) are unanswered. ' : '') + 'Submit your assessment? You cannot change answers afterwards.')) e.preventDefault();
  });

  // ---------- audio players --------------------------------------------------
  // Audio is requested per-play from the server, which returns a short-lived, session-bound URL.
  document.addEventListener('contextmenu', function (e) { if (e.target.closest('.player')) e.preventDefault(); });
  document.querySelectorAll('.player').forEach(function (p) {
    var q = p.closest('.q'), btn = p.querySelector('.playbtn'), au = p.querySelector('audio');
    var fill = p.querySelector('.fill'), left = p.querySelector('.left'), loaded = false;
    au.controlsList = 'nodownload noplaybackrate'; au.setAttribute('disablePictureInPicture', '');
    au.addEventListener('timeupdate', function () { if (au.duration) fill.style.width = (100 * au.currentTime / au.duration) + '%'; });
    au.addEventListener('ended', function () { loaded = false; btn.textContent = '▶ Play'; au.removeAttribute('src'); au.load(); fill.style.width = '0'; });
    au.addEventListener('pause', function () { if (!au.ended) btn.textContent = '▶ Resume'; });
    au.addEventListener('playing', function () { btn.textContent = '❚❚ Pause'; });
    btn.addEventListener('click', function () {
      if (loaded) { au.paused ? au.play() : au.pause(); return; }
      btn.disabled = true;
      fetch('/api/audio/' + q.dataset.id + '/play', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRF': csrf } })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok) { left.textContent = res.j.error || 'Unavailable'; return; }
          au.src = res.j.url; loaded = true; au.play();
          left.textContent = res.j.left + ' play' + (res.j.left === 1 ? '' : 's') + ' left';
          btn.disabled = false;
        }).catch(function () { left.textContent = 'Could not load audio'; btn.disabled = false; });
    });
  });
})();
