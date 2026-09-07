(function () {
  document.addEventListener("DOMContentLoaded", function () {
    if (!App.mountLayout("security")) return;
    SovereignAPI.getSecurityStatus().then(function (s) {
      document.getElementById("egress").textContent = s.networkEgress + " External Calls";
      document.getElementById("feed").innerHTML = s.events
        .map(function (e) {
          return "<li><time>" + App.escapeHtml(e.time) + "</time>" + App.escapeHtml(e.text) + "</li>";
        })
        .join("");
    });
  });
})();
