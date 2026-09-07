(function () {
  function greeting() {
    var h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  }
  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("dashboard");
    if (!user) return;
    document.getElementById("greet").textContent = greeting() + ", " + (user.name.split(" ")[0] || "Admin");
    SovereignAPI.getDashboardData().then(function (d) {
      document.getElementById("stat-status").innerHTML =
        '<span class="ops-flag"><span class="dot ok"></span> ' + App.escapeHtml(d.systemStatus) + "</span>";
      document.getElementById("stat-agents").textContent = d.activeAgents;
      document.getElementById("stat-docs").textContent = d.documentsIndexed;
      document.getElementById("stat-kb").textContent = d.knowledgeBases;
      document.getElementById("stat-reports").textContent = d.reportsGenerated;
      document.getElementById("stat-sec").innerHTML =
        d.security.mode + '<div class="metric-sub">Network Egress: ' + d.security.networkEgress + "</div>";
      document.getElementById("conv-list").innerHTML = d.conversations
        .map(function (c) {
          return (
            "<li><div><strong>" +
            App.escapeHtml(c.title) +
            '</strong><div class="metric-sub">' +
            App.escapeHtml(c.preview) +
            "</div></div><span class=\"metric-sub\">" +
            App.escapeHtml(c.time) +
            "</span></li>"
          );
        })
        .join("");
      document.getElementById("act-list").innerHTML = d.agentActivity
        .map(function (a) {
          return (
            "<li><span>" +
            App.escapeHtml(a.agent) +
            " " +
            App.escapeHtml(a.event) +
            '</span><span class="metric-sub">' +
            App.escapeHtml(a.time) +
            "</span></li>"
          );
        })
        .join("");
      document.getElementById("health-list").innerHTML = d.health
        .map(function (h) {
          return (
            '<div class="health-row"><span>' +
            App.escapeHtml(h.name) +
            '</span><span class="status-ok">● ' +
            App.escapeHtml(h.status) +
            "</span></div>"
          );
        })
        .join("");
    });
  });
})();
