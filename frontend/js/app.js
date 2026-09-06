(function (global) {
  "use strict";

  var NAV = [
    { id: "dashboard", href: "dashboard.html", label: "Dashboard", icon: "grid" },
    { id: "workbench", href: "workbench.html", label: "AI Workbench", icon: "work" },
    { id: "documents", href: "documents.html", label: "Documents", icon: "doc" },
    { id: "knowledge-bases", href: "knowledge-bases.html", label: "Knowledge Bases", icon: "kb" },
    { id: "agents", href: "agents.html", label: "Agents", icon: "agent" },
    { id: "reports", href: "reports.html", label: "Reports", icon: "report" },
    { id: "audit-logs", href: "audit-logs.html", label: "Audit Logs", icon: "log" },
    { id: "security", href: "security.html", label: "Security Center", icon: "shield" },
    { id: "settings", href: "settings.html", label: "Settings", icon: "gear" },
  ];

  function icon(name) {
    var map = {
      grid: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
      work: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4z"/><path d="M8 10h8M8 14h5"/></svg>',
      doc: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h8l5 5v13H7z"/><path d="M15 3v5h5"/></svg>',
      kb: '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="7" rx="7" ry="3"/><path d="M5 7v5c0 1.7 3.1 3 7 3s7-1.3 7-3V7"/><path d="M5 12v5c0 1.7 3.1 3 7 3s7-1.3 7-3v-5"/></svg>',
      agent: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3"/><path d="M5 19c1.5-3 4-4.5 7-4.5S17.5 16 19 19"/></svg>',
      report: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h9l5 5v13H6z"/><path d="M9 13h8M9 17h6"/></svg>',
      log: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5h14v14H5z"/><path d="M8 9h8M8 12h8M8 15h5"/></svg>',
      shield: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l8 3v6c0 5-3.4 8.2-8 9-4.6-.8-8-4-8-9V6z"/></svg>',
      gear: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/></svg>',
    };
    return map[name] || "";
  }

  function applyAppearance() {
    var theme = localStorage.getItem("sovereign_theme") || "dark";
    var reduced = localStorage.getItem("sovereign_reduced_motion") === "1";
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.classList.toggle("reduced-motion", reduced);
  }

  function openModal(html) {
    closeModal();
    var overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.id = "app-modal";
    overlay.innerHTML = '<div class="modal" role="dialog" aria-modal="true">' + html + "</div>";
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) closeModal();
    });
    document.body.appendChild(overlay);
    var focusable = overlay.querySelector("button, [href], input, select, textarea");
    if (focusable) focusable.focus();
  }

  function closeModal() {
    var el = document.getElementById("app-modal");
    if (el) el.remove();
  }

  function toast(message, type) {
    var host = document.getElementById("toast-host");
    if (!host) {
      host = document.createElement("div");
      host.id = "toast-host";
      host.className = "toast-host";
      document.body.appendChild(host);
    }
    var t = document.createElement("div");
    t.className = "toast" + (type ? " toast-" + type : "");
    t.setAttribute("role", "status");
    t.textContent = message;
    host.appendChild(t);
    setTimeout(function () {
      t.classList.add("out");
      setTimeout(function () {
        t.remove();
      }, 280);
    }, 3200);
  }

  function confirmDeleteSession() {
    openModal(
      '<h2 id="del-title">Delete this session?</h2>' +
        "<p>This will permanently delete:</p>" +
        "<ul class=\"check-list\">" +
        "<li>Conversation messages</li>" +
        "<li>Uploaded session files</li>" +
        "<li>Generated reports</li>" +
        "<li>Agent run data</li>" +
        "<li>Temporary session data</li>" +
        "</ul>" +
        "<p class=\"warn-text\">This action cannot be undone.</p>" +
        '<div class="modal-actions">' +
        '<button type="button" class="btn btn-ghost" id="cancel-del">Cancel</button>' +
        '<button type="button" class="btn btn-danger" id="confirm-del">Delete Everything</button>' +
        "</div>"
    );
    document.getElementById("cancel-del").addEventListener("click", closeModal);
    document.getElementById("confirm-del").addEventListener("click", function () {
      var btn = document.getElementById("confirm-del");
      btn.disabled = true;
      btn.textContent = "Deleting…";
      SovereignSession.deleteEverything()
        .then(function (res) {
          closeModal();
          toast(res.message || "Session deleted successfully.", "ok");
          if (location.pathname.indexOf("workbench") !== -1) {
            setTimeout(function () {
              location.reload();
            }, 600);
          }
        })
        .catch(function (err) {
          btn.disabled = false;
          btn.textContent = "Delete Everything";
          toast(err.message || "Delete was not confirmed. Session was not cleared.", "err");
        });
    });
  }

  function renderShell(user, pageId) {
    applyAppearance();
    var role = user.role || "Viewer";
    var links = NAV.filter(function (n) {
      return Auth.canAccess(n.id, role);
    })
      .map(function (n) {
        var active = n.id === pageId ? ' aria-current="page" class="nav-link is-active"' : ' class="nav-link"';
        return (
          "<a href=\"" +
          n.href +
          '"' +
          active +
          ">" +
          icon(n.icon) +
          "<span>" +
          n.label +
          "</span></a>"
        );
      })
      .join("");

    var showDelete = Auth.can("sessionDelete", role);

    return (
      '<div class="app-shell">' +
      '<header class="topbar">' +
      '<button type="button" class="icon-btn sidebar-toggle" id="sidebar-toggle" aria-label="Toggle navigation">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>' +
      "</button>" +
      '<a class="brand" href="dashboard.html">' +
      '<span class="brand-mark" aria-hidden="true"></span>' +
      "<span><strong>SOVEREIGN AI</strong><small>On-Premise Workbench</small></span>" +
      "</a>" +
      '<div class="workspace-chip" title="Current workspace">' +
      '<span class="dot ok"></span>' +
      "<span>" +
      escapeHtml(user.workspace || "MRPL Workspace") +
      "</span>" +
      "</div>" +
      '<div class="topbar-right">' +
      '<div class="sec-pill" title="Security status"><span class="dot ok"></span> AIR-GAPPED</div>' +
      '<div class="user-block">' +
      '<span class="avatar" aria-hidden="true">' +
      initials(user.name) +
      "</span>" +
      "<span><strong>" +
      escapeHtml(user.name) +
      '</strong><span class="role-badge">' +
      escapeHtml(role) +
      "</span></span>" +
      "</div>" +
      "</div>" +
      "</header>" +
      '<aside class="sidebar" id="sidebar">' +
      "<nav class=\"side-nav\" aria-label=\"Primary\">" +
      links +
      "</nav>" +
      '<div class="side-footer">' +
      (showDelete
        ? '<button type="button" class="btn btn-ghost btn-block" id="delete-session-btn">Delete Everything From This Session</button>'
        : "") +
      '<button type="button" class="btn btn-quiet btn-block" id="logout-btn">Logout</button>' +
      "</div>" +
      "</aside>" +
      '<div class="sidebar-backdrop" id="sidebar-backdrop" hidden></div>' +
      "</div>"
    );
  }

  function initials(name) {
    return String(name || "U")
      .split(" ")
      .map(function (p) {
        return p.charAt(0);
      })
      .join("")
      .slice(0, 2)
      .toUpperCase();
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function mountLayout(pageId) {
    applyAppearance();
    var user = Auth.requireAuth();
    if (!user) return null;
    if (!Auth.canAccess(pageId, user.role)) {
      location.replace("dashboard.html");
      return null;
    }

    var root = document.getElementById("app-root");
    if (!root) return user;

    var existing = document.querySelector(".app-shell");
    if (!existing) {
      var wrap = document.createElement("div");
      wrap.innerHTML = renderShell(user, pageId);
      while (wrap.firstChild) {
        document.body.insertBefore(wrap.firstChild, root);
      }
    }

    document.getElementById("logout-btn").addEventListener("click", function () {
      Auth.logoutAndRedirect();
    });
    var del = document.getElementById("delete-session-btn");
    if (del) del.addEventListener("click", confirmDeleteSession);

    var toggle = document.getElementById("sidebar-toggle");
    var sidebar = document.getElementById("sidebar");
    var backdrop = document.getElementById("sidebar-backdrop");
    function closeSide() {
      document.body.classList.remove("sidebar-open");
      if (backdrop) backdrop.hidden = true;
    }
    if (toggle) {
      toggle.addEventListener("click", function () {
        document.body.classList.toggle("sidebar-open");
        if (backdrop) backdrop.hidden = !document.body.classList.contains("sidebar-open");
      });
    }
    if (backdrop) backdrop.addEventListener("click", closeSide);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        closeModal();
        closeSide();
      }
    });

    SovereignSession.getSessionId();
    return user;
  }

  function formatBytes(n) {
    if (n < 1024) return n + " B";
    if (n < 1048576) return (n / 1024).toFixed(1) + " KB";
    return (n / 1048576).toFixed(1) + " MB";
  }

  function confidenceMeta(value) {
    var v = String(value || "").toLowerCase();
    if (v === "high") return { level: "high", label: "HIGH CONFIDENCE", icon: "●" };
    if (v === "medium") return { level: "medium", label: "MEDIUM CONFIDENCE", icon: "▲" };
    return { level: "low", label: "LOW CONFIDENCE", icon: "!" };
  }

  function isDocxResult(result) {
    return typeof result === "string" && /\.docx\s*$/i.test(result.trim());
  }

  global.App = {
    mountLayout: mountLayout,
    openModal: openModal,
    closeModal: closeModal,
    toast: toast,
    escapeHtml: escapeHtml,
    formatBytes: formatBytes,
    confidenceMeta: confidenceMeta,
    isDocxResult: isDocxResult,
    applyAppearance: applyAppearance,
    confirmDeleteSession: confirmDeleteSession,
  };

  applyAppearance();
})(window);
