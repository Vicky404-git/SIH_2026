(function (global) {
  "use strict";

  var ROLE_NAV = {
    Admin: [
      "dashboard",
      "workbench",
      "documents",
      "knowledge-bases",
      "agents",
      "reports",
      "audit-logs",
      "security",
      "settings",
    ],
    "AI/ML Engineer": [
      "dashboard",
      "workbench",
      "documents",
      "knowledge-bases",
      "agents",
      "reports",
      "audit-logs",
      "settings",
    ],
    Operator: ["dashboard", "workbench", "documents", "reports", "settings"],
    Viewer: ["dashboard", "workbench", "reports", "settings"],
  };

  var ROLE_ACTIONS = {
    Admin: { upload: true, delete: true, agents: true, security: true, sessionDelete: true },
    "AI/ML Engineer": { upload: true, delete: true, agents: true, security: false, sessionDelete: true },
    Operator: { upload: true, delete: false, agents: false, security: false, sessionDelete: true },
    Viewer: { upload: false, delete: false, agents: false, security: false, sessionDelete: false },
  };

  function readAuth() {
    var token = sessionStorage.getItem("sovereign_auth") || localStorage.getItem("sovereign_auth");
    var raw = sessionStorage.getItem("sovereign_user") || localStorage.getItem("sovereign_user");
    var user = null;
    try {
      user = raw ? JSON.parse(raw) : null;
    } catch (e) {
      user = null;
    }
    return { authenticated: token === "1" && !!user, user: user };
  }

  function requireAuth() {
    var state = readAuth();
    if (!state.authenticated) {
      var next = encodeURIComponent(location.pathname.split("/").pop() || "dashboard.html");
      location.replace("login.html?next=" + next);
      return null;
    }
    return state.user;
  }

  function canAccess(pageId, role) {
    var allowed = ROLE_NAV[role] || ROLE_NAV.Viewer;
    return allowed.indexOf(pageId) !== -1;
  }

  function can(action, role) {
    var map = ROLE_ACTIONS[role] || ROLE_ACTIONS.Viewer;
    return !!map[action];
  }

  function logoutAndRedirect() {
    return SovereignAPI.logout().then(function () {
      if (global.SovereignSession) SovereignSession.clearLocal();
      location.replace("login.html");
    });
  }

  global.Auth = {
    readAuth: readAuth,
    requireAuth: requireAuth,
    canAccess: canAccess,
    can: can,
    logoutAndRedirect: logoutAndRedirect,
    ROLE_NAV: ROLE_NAV,
  };

  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("login-form");
    if (!form) return;
    if (readAuth().authenticated) {
      location.replace("dashboard.html");
      return;
    }
    var userEl = document.getElementById("username");
    var passEl = document.getElementById("password");
    var errEl = document.getElementById("login-error");
    var submit = document.getElementById("login-submit");
    var toggle = document.getElementById("pw-toggle");
    var remembered = localStorage.getItem("sovereign_remember_user");
    if (remembered) {
      userEl.value = remembered;
      document.getElementById("remember").checked = true;
    }
    toggle.addEventListener("click", function () {
      var show = passEl.type === "password";
      passEl.type = show ? "text" : "password";
      toggle.setAttribute("aria-label", show ? "Hide password" : "Show password");
      toggle.textContent = show ? "Hide" : "Show";
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      errEl.classList.remove("show");
      errEl.textContent = "";
      if (!userEl.value.trim() || !passEl.value) {
        errEl.textContent = "Enter your username and password.";
        errEl.classList.add("show");
        return;
      }
      submit.disabled = true;
      submit.textContent = "Signing in…";
      var remember = document.getElementById("remember").checked;
      SovereignAPI.login(userEl.value, passEl.value, remember)
        .then(function () {
          if (remember) localStorage.setItem("sovereign_remember_user", userEl.value.trim());
          else localStorage.removeItem("sovereign_remember_user");
          var params = new URLSearchParams(location.search);
          var next = params.get("next") || "dashboard.html";
          if (!/^[a-z0-9.-]+\.html$/i.test(next)) next = "dashboard.html";
          location.replace(next);
        })
        .catch(function () {
          errEl.textContent = "Invalid credentials. Check username and password.";
          errEl.classList.add("show");
          submit.disabled = false;
          submit.textContent = "SIGN IN";
        });
    });
  });
})(window);
