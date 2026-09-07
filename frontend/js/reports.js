(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("reports");
    if (!user) return;
    SovereignAPI.getReports().then(function (rows) {
      document.getElementById("report-list").innerHTML = rows
        .map(function (r) {
          return (
            '<article class="report-item"><div><h3 style="margin:0 0 4px">' +
            App.escapeHtml(r.name) +
            '</h3><div class="metric-sub">' +
            App.escapeHtml(r.type) +
            " · Generated: " +
            App.escapeHtml(r.generated) +
            " · " +
            App.escapeHtml(r.file) +
            '</div></div><div class="quick-actions"><button type="button" class="btn" data-view="' +
            r.id +
            '">View</button><button type="button" class="btn btn-primary" data-dl="' +
            App.escapeHtml(r.file) +
            '">Download</button></div></article>'
          );
        })
        .join("");
      document.querySelectorAll("[data-dl]").forEach(function (b) {
        b.addEventListener("click", function () {
          SovereignAPI.downloadReport("rep_1", b.getAttribute("data-dl"));
        });
      });
      document.querySelectorAll("[data-view]").forEach(function (b) {
        b.addEventListener("click", function () {
          App.openModal(
            "<h2>Report preview</h2><p>Technical maintenance report generated on-premise. Binary preview will use GET /reports/{id}.</p><div class=\"modal-actions\"><button type=\"button\" class=\"btn\" id=\"c\">Close</button></div>"
          );
          document.getElementById("c").onclick = App.closeModal;
        });
      });
    });
  });
})();
