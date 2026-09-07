(function () {
  var rows = [];
  function openDetail(r) {
    var existing = document.getElementById("drawer");
    if (existing) existing.remove();
    var back = document.createElement("div");
    back.className = "drawer-backdrop";
    back.id = "drawer-back";
    var d = document.createElement("aside");
    d.className = "drawer";
    d.id = "drawer";
    d.innerHTML =
      "<h2>Audit event</h2><p><strong>" +
      App.escapeHtml(r.action) +
      "</strong></p><p>" +
      App.escapeHtml(r.displayTime) +
      "</p><p>User: " +
      App.escapeHtml(r.user) +
      "<br>Agent: " +
      App.escapeHtml(r.agent) +
      "<br>Resource: " +
      App.escapeHtml(r.resource) +
      "<br>Status: " +
      App.escapeHtml(r.status) +
      '</p><button type="button" class="btn" id="close-d">Close</button>';
    document.body.appendChild(back);
    document.body.appendChild(d);
    function close() {
      d.remove();
      back.remove();
    }
    back.onclick = close;
    document.getElementById("close-d").onclick = close;
  }
  function render(list) {
    document.getElementById("audit-body").innerHTML = list
      .map(function (r) {
        var badge = r.status === "SUCCESS" ? "badge-ok" : r.status === "BLOCKED" ? "badge-err" : "badge-warn";
        return (
          "<tr><td>" +
          App.escapeHtml(r.displayTime) +
          "</td><td>" +
          App.escapeHtml(r.user) +
          "</td><td>" +
          App.escapeHtml(r.action) +
          "</td><td>" +
          App.escapeHtml(r.agent) +
          "</td><td>" +
          App.escapeHtml(r.resource) +
          '</td><td><span class="badge ' +
          badge +
          '">' +
          App.escapeHtml(r.status) +
          '</span></td><td><button type="button" class="btn btn-sm" data-id="' +
          r.id +
          '">Detail</button></td></tr>'
        );
      })
      .join("");
    document.querySelectorAll("[data-id]").forEach(function (b) {
      b.addEventListener("click", function () {
        var r = rows.find(function (x) {
          return x.id === b.getAttribute("data-id");
        });
        if (r) openDetail(r);
      });
    });
  }
  function load() {
    SovereignAPI.getAuditLogs({
      query: document.getElementById("audit-q").value,
      status: document.getElementById("audit-st").value,
    }).then(function (list) {
      rows = list;
      render(list);
    });
  }
  document.addEventListener("DOMContentLoaded", function () {
    if (!App.mountLayout("audit-logs")) return;
    document.getElementById("audit-q").addEventListener("input", load);
    document.getElementById("audit-st").addEventListener("change", load);
    load();
  });
})();
