(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("knowledge-bases");
    if (!user) return;
    SovereignAPI.getKnowledgeBases().then(function (rows) {
      document.getElementById("kb-grid").innerHTML = rows
        .map(function (k) {
          return (
            '<article class="card"><h3>' +
            App.escapeHtml(k.name) +
            '</h3><div class="metric">' +
            k.documents +
            '</div><div class="metric-sub">Documents</div><p class="badge badge-ok">' +
            App.escapeHtml(k.status) +
            '</p><div class="quality" aria-label="Retrieval quality ' +
            k.quality +
            '%"><span style="width:' +
            k.quality +
            '%"></span></div><div class="metric-sub">Retrieval quality ' +
            k.quality +
            '%</div><div class="card-actions"><button type="button" class="btn btn-sm">Rename</button><button type="button" class="btn btn-sm">Assign Documents</button><button type="button" class="btn btn-sm">Re-index</button><button type="button" class="btn btn-sm">Delete</button></div></article>'
          );
        })
        .join("");
      document.querySelectorAll("#kb-grid .btn").forEach(function (b) {
        b.addEventListener("click", function () {
          App.toast(b.textContent + " queued for this knowledge base (prototype).", "ok");
        });
      });
    });
    document.getElementById("kb-create").addEventListener("click", function () {
      App.toast("Create Knowledge Base — ready for POST when backend is connected.", "ok");
    });
  });
})();
