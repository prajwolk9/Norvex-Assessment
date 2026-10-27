(function () {
  "use strict";
  var csrf = document.querySelector('meta[name=csrf]').content;
  // admin song preview (streams through the same protected endpoint)
  document.querySelectorAll('.preview').forEach(function (b) {
    var au = new Audio();
    b.addEventListener('click', function () {
      if (!au.paused) { au.pause(); b.textContent = '▶ Preview'; return; }
      fetch('/admin/audio/' + b.dataset.id + '/preview', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRF': csrf } })
        .then(function (r) { return r.json(); })
        .then(function (j) { au.src = j.url; au.play(); b.textContent = '❚❚ Stop'; });
    });
    au.addEventListener('ended', function () { b.textContent = '▶ Preview'; });
  });
  document.querySelectorAll('form[data-confirm]').forEach(function (f) {
    f.addEventListener('submit', function (e) { if (!confirm(f.dataset.confirm)) e.preventDefault(); });
  });
})();
