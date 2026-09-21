(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("documents");
    if (!user) return;
    var all = [];
    function render(rows) {
      var body = document.getElementById("doc-body");
      body.innerHTML = rows
        .map(function (d) {
          var badge =
            d.status === "Indexed"
              ? "badge-ok"
              : d.status === "Processing"
              ? "badge-info"
              : "badge-err";
          var del = Auth.can("delete", user.role)
            ? '<button type="button" class="btn btn-sm" data-del="' + d.id + '">Delete</button>'
            : "";
          return (
            "<tr><td>" +
            App.escapeHtml(d.name) +
            "</td><td>" +
            App.escapeHtml(d.type) +
            '</td><td><span class="badge ' +
            badge +
            '">' +
            App.escapeHtml(d.status) +
            "</span></td><td>" +
            App.escapeHtml(d.uploaded) +
            '</td><td><button type="button" class="btn btn-sm" data-prev="' +
            d.id +
            '">Preview</button> ' +
            del +
            "</td></tr>"
          );
        })
        .join("");
      body.querySelectorAll("[data-prev]").forEach(function (b) {
        b.addEventListener("click", function () {
          var doc = all.find(function (x) {
            return x.id === b.getAttribute("data-prev");
          });
          App.openModal(
            "<h2>Document preview</h2><p>" +
              App.escapeHtml(doc.name) +
              "</p><p class=\"metric-sub\">Indexed excerpt from private knowledge base. Full binary preview will attach to GET /documents/{id}.</p><div class=\"modal-actions\"><button type=\"button\" class=\"btn\" id=\"c\">Close</button></div>"
          );
          document.getElementById("c").onclick = App.closeModal;
        });
      });
      body.querySelectorAll("[data-del]").forEach(function (b) {
        b.addEventListener("click", function () {
          SovereignAPI.deleteDocument(b.getAttribute("data-del")).then(load);
        });
      });
    }
    function apply() {
      var q = document.getElementById("doc-search").value.toLowerCase();
      var st = document.getElementById("doc-filter").value;
      render(
        all.filter(function (d) {
          return (!q || d.name.toLowerCase().indexOf(q) !== -1) && (st === "all" || d.status === st);
        })
      );
    }
    function load() {
      SovereignAPI.getDocuments().then(function (rows) {
        all = rows;
        apply();
      });
    }
    Upload.bindDropzone(document.getElementById("doc-drop"), function (files) {
      files.forEach(function (f) {
        Upload.uploadWithFormData(f).then(load).catch(function (e) {
          App.toast(e.message || "Upload failed.", "err");
        });
      });
    });
    document.getElementById("doc-upload").addEventListener("click", function () {
      Upload.pick(function (files) {
        files.forEach(function (f) {
          Upload.uploadWithFormData(f).then(load).catch(function (e) {
            App.toast(e.message || "Upload failed.", "err");
          });
        });
      });
    });
    document.getElementById("doc-search").addEventListener("input", apply);
    document.getElementById("doc-filter").addEventListener("change", apply);
    load();
  });
})();
