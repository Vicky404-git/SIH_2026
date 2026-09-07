(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("settings");
    if (!user) return;
    document.getElementById("set-name").value = user.name;
    document.getElementById("set-user").value = user.username;
    document.getElementById("set-role").value = user.role;
    document.getElementById("theme").value = localStorage.getItem("sovereign_theme") || "dark";
    document.getElementById("motion").checked = localStorage.getItem("sovereign_reduced_motion") === "1";
    document.getElementById("theme").addEventListener("change", function () {
      localStorage.setItem("sovereign_theme", this.value);
      App.applyAppearance();
    });
    document.getElementById("motion").addEventListener("change", function () {
      localStorage.setItem("sovereign_reduced_motion", this.checked ? "1" : "0");
      App.applyAppearance();
    });
    document.getElementById("save-set").addEventListener("click", function () {
      App.toast("Settings saved on this workstation.", "ok");
    });
    var del = document.getElementById("set-del");
    if (del) del.addEventListener("click", App.confirmDeleteSession);
  });
})();
