(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("agents");
    if (!user) return;
    SovereignAPI.getAgents().then(function (rows) {
      document.getElementById("agent-grid").innerHTML = rows
        .map(function (a) {
          return (
            '<article class="card agent-card"><div class="agent-top"><h3>' +
            App.escapeHtml(a.name) +
            '</h3><span class="badge badge-ok"><span class="dot ok"></span> ' +
            App.escapeHtml(a.status) +
            "</span></div><p>" +
            App.escapeHtml(a.description) +
            '</p><div class="metric-sub">Last activity ' +
            App.escapeHtml(a.lastActivity) +
            " · Permissions " +
            App.escapeHtml(a.permissions) +
            "</div></article>"
          );
        })
        .join("");
    });
  });
})();
