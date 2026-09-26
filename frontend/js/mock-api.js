/**
 * Sovereign AI Real Backend API Client.
 * All dummy and mock data has been removed.
 * Communicates directly with FastAPI backend on http://localhost:8000.
 */
(function (global) {
  "use strict";

  var API_BASE = global.SOVEREIGN_API_BASE !== undefined
    ? global.SOVEREIGN_API_BASE
    : (typeof location !== "undefined" && location.port === "8000" ? "" : "http://localhost:8000");

  function currentUserFromStore() {
    try {
      var raw = sessionStorage.getItem("sovereign_user") || localStorage.getItem("sovereign_user");
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  var api = {
    API_BASE: API_BASE,

    login: function (username, password, remember) {
      return fetch(API_BASE + "/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username, password: password, remember: remember }),
      })
        .then(function (r) {
          if (!r.ok) {
            return r.json().then(function (err) {
              var error = new Error(err.message || err.detail || "Invalid credentials");
              error.code = "INVALID_CREDENTIALS";
              throw error;
            });
          }
          return r.json();
        })
        .then(function (res) {
          if (!res.ok) {
            var err = new Error(res.message || "Invalid credentials");
            err.code = "INVALID_CREDENTIALS";
            throw err;
          }
          var store = remember ? localStorage : sessionStorage;
          var other = remember ? sessionStorage : localStorage;
          store.setItem("sovereign_auth", "1");
          store.setItem("sovereign_user", JSON.stringify(res.user));
          other.removeItem("sovereign_auth");
          other.removeItem("sovereign_user");
          return res;
        });
    },

    logout: function () {
      sessionStorage.removeItem("sovereign_auth");
      sessionStorage.removeItem("sovereign_user");
      localStorage.removeItem("sovereign_auth");
      localStorage.removeItem("sovereign_user");
      return fetch(API_BASE + "/auth/logout", { method: "POST" })
        .catch(function () { })
        .then(function () {
          return { ok: true };
        });
    },

    getCurrentUser: function () {
      return fetch(API_BASE + "/users/me")
        .then(function (r) {
          if (!r.ok) {
            var err = new Error("Unauthenticated");
            err.code = "UNAUTHENTICATED";
            throw err;
          }
          return r.json();
        })
        .catch(function () {
          var user = currentUserFromStore();
          if (user) return user;
          throw new Error("Unauthenticated");
        });
    },

    getDashboardData: function () {
      return fetch(API_BASE + "/dashboard").then(function (r) {
        if (!r.ok) throw new Error("Failed to load dashboard data");
        return r.json();
      });
    },

    uploadDocument: function (file, onProgress) {
      if (onProgress) onProgress({ phase: "uploading", percent: 30 });
      var fd = new FormData();
      fd.append("file", file);
      return fetch(API_BASE + "/documents", {
        method: "POST",
        body: fd,
      })
        .then(function (r) {
          if (!r.ok) throw new Error("Upload failed: " + r.statusText);
          if (onProgress) onProgress({ phase: "indexing", percent: 100 });
          return r.json();
        });
    },

    getDocuments: function () {
      return fetch(API_BASE + "/documents").then(function (r) {
        if (!r.ok) throw new Error("Failed to load documents");
        return r.json();
      });
    },

    deleteDocument: function (id) {
      return fetch(API_BASE + "/documents/" + encodeURIComponent(id), {
        method: "DELETE",
      }).then(function (r) {
        if (!r.ok) throw new Error("Failed to delete document");
        return r.json();
      });
    },

    getKnowledgeBases: function () {
      return fetch(API_BASE + "/knowledge-bases").then(function (r) {
        if (!r.ok) throw new Error("Failed to load knowledge bases");
        return r.json();
      });
    },

    getAgents: function () {
      return fetch(API_BASE + "/agents").then(function (r) {
        if (!r.ok) throw new Error("Failed to load agents");
        return r.json();
      });
    },

    sendChatMessage: function (payload) {
      return fetch(API_BASE + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then(function (r) {
        if (!r.ok) throw new Error("Chat request failed");
        return r.json();
      });
    },

    getSources: function () {
      return fetch(API_BASE + "/chat/sources").then(function (r) {
        if (!r.ok) throw new Error("Failed to load sources");
        return r.json();
      });
    },

    getAgentTrace: function (runId) {
      return fetch(API_BASE + "/agents/runs/" + encodeURIComponent(runId)).then(function (r) {
        if (!r.ok) throw new Error("Failed to load trace");
        return r.json();
      });
    },

    getReports: function () {
      return fetch(API_BASE + "/reports").then(function (r) {
        if (!r.ok) throw new Error("Failed to load reports");
        return r.json();
      });
    },

    generateReport: function (payload) {
      return fetch(API_BASE + "/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      }).then(function (r) {
        if (!r.ok) throw new Error("Failed to generate report");
        return r.json();
      });
    },

    downloadReport: function (reportId, filename) {
      var name = filename || (reportId + ".docx");
      var param = filename || reportId;
      return fetch(API_BASE + "/reports/" + encodeURIComponent(param) + "/download")
        .then(function (r) {
          if (!r.ok) throw new Error("Download failed");
          return r.blob();
        })
        .then(function (blob) {
          var url = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url;
          a.download = name;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          return { ok: true };
        });
    },

    getAuditLogs: function (filters) {
      var q = filters ? "?" + new URLSearchParams(filters).toString() : "";
      return fetch(API_BASE + "/audit-logs" + q).then(function (r) {
        if (!r.ok) throw new Error("Failed to load audit logs");
        return r.json();
      });
    },

    getSecurityStatus: function () {
      return fetch(API_BASE + "/security/status").then(function (r) {
        if (!r.ok) throw new Error("Failed to load security status");
        return r.json();
      });
    },

    deleteSession: function (sessionId) {
      var id = sessionId || sessionStorage.getItem("sovereign_session_id") || "workbench";
      return fetch(API_BASE + "/session/" + encodeURIComponent(id), {
        method: "DELETE",
      }).then(function (r) {
        if (!r.ok) throw new Error("Session reset failed");
        return r.json();
      });
    },

    simulatedTracePlan: function (kind) {
      if (kind === "report") {
        return [
          { step: 1, action: "Security screening", status: "waiting" },
          { step: 2, action: "Assembling analysis context", status: "waiting" },
          { step: 3, action: "Validating citations", status: "waiting" },
          { step: 4, action: "Generating DOCX report", status: "waiting" },
        ];
      }
      return [
        { step: 1, action: "Security screening", status: "waiting" },
        { step: 2, action: "Document retrieval", status: "waiting" },
        { step: 3, action: "Searching knowledge base", status: "waiting" },
        { step: 4, action: "Analyzing uploaded evidence", status: "waiting" },
        { step: 5, action: "Synthesizing answer", status: "waiting" },
      ];
    },
  };

  global.SovereignAPI = api;
  global.MockAPI = api; // alias for existing pages
})(window);
