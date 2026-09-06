/**
 * Isolated mock API layer for the SIH prototype.
 * Replace function bodies with Fetch calls when the Python backend is ready.
 */
(function (global) {
  "use strict";

  var API_BASE = global.SOVEREIGN_API_BASE || "http://localhost:8000";
  var USE_MOCK = false;
  var LATENCY = 420;

  function delay(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms == null ? LATENCY : ms);
    });
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  var users = {
    admin: {
      id: "usr_admin",
      username: "admin",
      email: "admin@mrpl.local",
      name: "Admin User",
      role: "Admin",
      password: "admin123",
      workspace: "MRPL Refinery — Unit C-204",
    },
    engineer: {
      id: "usr_eng",
      username: "engineer",
      email: "engineer@mrpl.local",
      name: "Priya Nair",
      role: "AI/ML Engineer",
      password: "eng123",
      workspace: "MRPL Refinery — Unit C-204",
    },
  };

  var dashboardData = {
    greetingName: "Admin",
    systemStatus: "OPERATIONAL",
    activeAgents: 8,
    documentsIndexed: 124,
    knowledgeBases: 6,
    reportsGenerated: 32,
    security: { mode: "AIR-GAPPED", networkEgress: 0 },
    conversations: [
      {
        id: "c1",
        title: "Compressor bearing condition vs. C-204 guidelines",
        preview: "Bearing temperature 82°C exceeds 75°C threshold…",
        time: "10:42 AM",
      },
      {
        id: "c2",
        title: "Inspection image analysis — C-204",
        preview: "Surface discoloration consistent with lubrication film breakdown.",
        time: "Yesterday",
      },
      {
        id: "c3",
        title: "Safety procedure retrieval — rotating equipment",
        preview: "LOTO sequence and PPE requirements retrieved from SP-RE-04.",
        time: "Yesterday",
      },
    ],
    agentActivity: [
      { agent: "Retrieval Agent", event: "completed", time: "10:41 AM" },
      { agent: "Vision Agent", event: "completed", time: "10:41 AM" },
      { agent: "Analysis Agent", event: "completed", time: "10:42 AM" },
      { agent: "Report Agent", event: "completed", time: "09:18 AM" },
    ],
    health: [
      { name: "AI Runtime", status: "Operational" },
      { name: "Knowledge Base", status: "Operational" },
      { name: "Agent Orchestrator", status: "Operational" },
      { name: "Document Processing", status: "Operational" },
      { name: "Security Layer", status: "Operational" },
    ],
  };

  var documents = [
    {
      id: "doc_1",
      name: "Maintenance Manual — Compressor Unit C-204",
      type: "PDF",
      status: "Indexed",
      uploaded: "2026-08-12",
      size: "4.2 MB",
      kb: "Maintenance Manuals",
    },
    {
      id: "doc_2",
      name: "Inspection Report — C-204 — August 2026",
      type: "DOCX",
      status: "Indexed",
      uploaded: "2026-08-28",
      size: "812 KB",
      kb: "Equipment Specifications",
    },
    {
      id: "doc_3",
      name: "Inspection Image — Compressor Bearing",
      type: "JPG",
      status: "Indexed",
      uploaded: "2026-09-04",
      size: "2.1 MB",
      kb: "Equipment Specifications",
    },
    {
      id: "doc_4",
      name: "Safety Procedure — Rotating Equipment",
      type: "PDF",
      status: "Indexed",
      uploaded: "2026-07-03",
      size: "1.4 MB",
      kb: "Safety Procedures",
    },
    {
      id: "doc_5",
      name: "Equipment Specification — C-204",
      type: "PDF",
      status: "Indexed",
      uploaded: "2026-06-18",
      size: "3.0 MB",
      kb: "Equipment Specifications",
    },
    {
      id: "doc_6",
      name: "Vibration Log — Train 2",
      type: "PDF",
      status: "Processing",
      uploaded: "2026-09-05",
      size: "640 KB",
      kb: "Maintenance Manuals",
    },
    {
      id: "doc_7",
      name: "Scan — Nameplate C-204 (low contrast)",
      type: "PNG",
      status: "Failed",
      uploaded: "2026-09-02",
      size: "380 KB",
      kb: "Equipment Specifications",
    },
  ];

  var knowledgeBases = [
    { id: "kb_1", name: "Maintenance Manuals", documents: 124, status: "Indexed", quality: 94 },
    { id: "kb_2", name: "Equipment Specifications", documents: 58, status: "Indexed", quality: 91 },
    { id: "kb_3", name: "Safety Procedures", documents: 36, status: "Indexed", quality: 97 },
    { id: "kb_4", name: "Inspection Archives", documents: 42, status: "Indexed", quality: 88 },
    { id: "kb_5", name: "OEM Bulletins", documents: 19, status: "Indexed", quality: 86 },
    { id: "kb_6", name: "Work Order History", documents: 71, status: "Re-indexing", quality: 79 },
  ];

  var agents = [
    {
      id: "ag_doc",
      name: "Document Agent",
      status: "Ready",
      description: "Parses, chunks and indexes technical PDFs, DOCX files and scanned procedures.",
      lastActivity: "10:38 AM",
      permissions: "Read / Index",
    },
    {
      id: "ag_vis",
      name: "Vision Agent",
      status: "Ready",
      description: "Analyzes technical images and scanned documents for equipment condition.",
      lastActivity: "10:41 AM",
      permissions: "Read / Analyze",
    },
    {
      id: "ag_ret",
      name: "Retrieval Agent",
      status: "Ready",
      description: "Searches private knowledge bases and returns cited source passages.",
      lastActivity: "10:41 AM",
      permissions: "Read / Retrieve",
    },
    {
      id: "ag_an",
      name: "Analysis Agent",
      status: "Ready",
      description: "Compares measurements against thresholds, manuals and prior inspections.",
      lastActivity: "10:42 AM",
      permissions: "Read / Analyze",
    },
    {
      id: "ag_res",
      name: "Research Agent",
      status: "Ready",
      description: "Cross-references multiple sources to assemble an evidence-backed brief.",
      lastActivity: "09:12 AM",
      permissions: "Read",
    },
    {
      id: "ag_rep",
      name: "Report Agent",
      status: "Ready",
      description: "Generates structured DOCX technical reports from completed analyses.",
      lastActivity: "09:18 AM",
      permissions: "Read / Write",
    },
    {
      id: "ag_val",
      name: "Validation Agent",
      status: "Ready",
      description: "Checks completeness, citation coverage and policy constraints before release.",
      lastActivity: "10:42 AM",
      permissions: "Read / Validate",
    },
    {
      id: "ag_sec",
      name: "Security / Policy Agent",
      status: "Ready",
      description: "Screens prompts, files and retrievals against on-premise security policy.",
      lastActivity: "10:40 AM",
      permissions: "Policy / Block",
    },
  ];

  var reports = [
    {
      id: "rep_1",
      name: "Maintenance Analysis Report",
      file: "Maintenance_Analysis_Report.docx",
      type: "DOCX",
      generated: "Today",
      status: "Ready",
    },
    {
      id: "rep_2",
      name: "C-204 Inspection Summary",
      file: "C204_Inspection_Summary.docx",
      type: "DOCX",
      generated: "Yesterday",
      status: "Ready",
    },
    {
      id: "rep_3",
      name: "Rotating Equipment Safety Brief",
      file: "RE_Safety_Brief.docx",
      type: "DOCX",
      generated: "2 Sep 2026",
      status: "Ready",
    },
  ];

  var auditLogs = [
    {
      id: "aud_1",
      timestamp: "2026-09-05T10:42:00",
      displayTime: "10:42 AM",
      user: "Admin",
      action: "AI analysis completed",
      agent: "Analysis Agent",
      resource: "Compressor Unit C-204",
      status: "SUCCESS",
    },
    {
      id: "aud_2",
      timestamp: "2026-09-05T10:41:00",
      displayTime: "10:41 AM",
      user: "Admin",
      action: "Knowledge Base Search",
      agent: "Retrieval Agent",
      resource: "Maintenance Manual",
      status: "SUCCESS",
    },
    {
      id: "aud_3",
      timestamp: "2026-09-05T10:41:12",
      displayTime: "10:41 AM",
      user: "Admin",
      action: "Image analysis",
      agent: "Vision Agent",
      resource: "Inspection Image — Compressor Bearing",
      status: "SUCCESS",
    },
    {
      id: "aud_4",
      timestamp: "2026-09-05T10:40:00",
      displayTime: "10:40 AM",
      user: "Admin",
      action: "Document accessed",
      agent: "Document Agent",
      resource: "Maintenance Manual — Compressor Unit C-204",
      status: "SUCCESS",
    },
    {
      id: "aud_5",
      timestamp: "2026-09-05T09:18:00",
      displayTime: "09:18 AM",
      user: "Admin",
      action: "Report generated",
      agent: "Report Agent",
      resource: "Maintenance_Analysis_Report.docx",
      status: "SUCCESS",
    },
    {
      id: "aud_6",
      timestamp: "2026-09-04T16:22:00",
      displayTime: "Yesterday 4:22 PM",
      user: "Admin",
      action: "Unauthorized retrieval attempt blocked",
      agent: "Security / Policy Agent",
      resource: "External corpus request",
      status: "BLOCKED",
    },
    {
      id: "aud_7",
      timestamp: "2026-09-04T11:05:00",
      displayTime: "Yesterday 11:05 AM",
      user: "Admin",
      action: "Session permission scope verified",
      agent: "Security / Policy Agent",
      resource: "Current User",
      status: "SUCCESS",
    },
  ];

  var securityStatus = {
    onPremise: true,
    airGapped: true,
    rbac: "ACTIVE",
    promptInjection: "ACTIVE",
    auditLogging: "ACTIVE",
    sandboxed: "ACTIVE",
    networkEgress: 0,
    permissionScope: "Current User",
    events: [
      { time: "10:40 AM", text: "Security screening completed. No threats detected." },
      { time: "Yesterday", text: "Unauthorized retrieval attempt blocked." },
      { time: "Yesterday", text: "Session permission scope verified." },
      { time: "2 Sep", text: "Network egress check: 0 external calls." },
    ],
  };

  var analysisResult = {
    result:
      "The compressor bearing on Unit C-204 is operating above the maintenance guideline.\n\n" +
      "Bearing temperature is 82°C against a documented threshold of 75°C (previous inspection: 68°C). " +
      "The uploaded inspection image shows surface discoloration consistent with lubrication film breakdown on the outer race.\n\n" +
      "Recommended actions:\n" +
      "- Schedule lubrication check and oil sample within 24 hours\n" +
      "- Increase vibration monitoring interval to 4 hours until temperature returns below threshold\n" +
      "- Do not extend the current run cycle; follow rotating-equipment LOTO before any intrusive inspection\n\n" +
      "Comparison against Maintenance Manual — Compressor Unit C-204 (p. 42) and Inspection Procedure (p. 17).",
    reasoning:
      "The answer was generated by retrieving relevant maintenance documentation and cross-checking the uploaded inspection image against equipment specifications for Unit C-204. Temperature, prior readings and visual condition were compared to published thresholds. No hidden chain-of-thought is shown; this is the user-facing explanation summary.",
    confidence: "high",
    status: "completed",
    industrialTable: {
      caption: "C-204 compressor bearing — parameter comparison",
      columns: ["Parameter", "Current", "Threshold", "Previous", "Status"],
      rows: [
        ["Bearing Temperature", "82°C", "75°C", "68°C", "Above Threshold"],
        ["Radial Vibration", "4.8 mm/s", "7.1 mm/s", "3.9 mm/s", "Within Limit"],
        ["Oil Level", "Low-normal", "Min mark", "Normal", "Watch"],
      ],
    },
    sources: [
      { id: "src_1", title: "Maintenance Manual", page: "Page 42", excerpt: "Alarm threshold for journal bearing metal temperature is 75°C. Investigate lubrication and load if exceeded." },
      { id: "src_2", title: "Inspection Procedure", page: "Page 17", excerpt: "Discoloration of the outer race indicates inadequate oil film. Capture image and compare with prior inspection." },
      { id: "src_3", title: "Safety Standard", page: "Section 4.2", excerpt: "Rotating equipment intrusive work requires LOTO and designated PPE before cover removal." },
    ],
    trace: [
      { step: 1, action: "Security screening", status: "success" },
      { step: 2, action: "Document retrieval", status: "success" },
      { step: 3, action: "Searching knowledge base", status: "success" },
      { step: 4, action: "Analyzing uploaded image", status: "success" },
      { step: 5, action: "Cross-referencing maintenance manual", status: "success" },
      { step: 6, action: "Generating technical response", status: "success" },
    ],
  };

  var reportResult = {
    result: "Maintenance_Analysis_Report.docx",
    reasoning:
      "The report agent compiled the completed analysis, cited sources and recommended actions into a structured technical maintenance report. Only the generated file is returned; the raw filesystem path is not displayed.",
    confidence: "high",
    status: "completed",
    sources: [
      { id: "src_1", title: "Maintenance Manual", page: "Page 42", excerpt: "Threshold and lubrication guidance included in Section 6.4." },
      { id: "src_2", title: "Inspection Procedure", page: "Page 17", excerpt: "Image comparison checklist attached as Appendix B." },
    ],
    trace: [
      { step: 1, action: "Security screening", status: "success" },
      { step: 2, action: "Assembling analysis context", status: "success" },
      { step: 3, action: "Validating citations", status: "success" },
      { step: 4, action: "Generating DOCX report", status: "success" },
    ],
  };

  function currentUserFromStore() {
    try {
      var raw = sessionStorage.getItem("sovereign_user") || localStorage.getItem("sovereign_user");
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  var api = {
    endpoints: {
      login: "POST /auth/login",
      logout: "POST /auth/logout",
      me: "GET /users/me",
      documents: "POST /documents",
      listDocuments: "GET /documents",
      deleteDocument: "DELETE /documents/{id}",
      chat: "POST /chat",
      conversations: "GET /conversations",
      conversation: "GET /conversations/{id}",
      agents: "GET /agents",
      agentRun: "GET /agents/runs/{id}",
      reports: "POST /reports",
      listReports: "GET /reports",
      downloadReport: "GET /reports/{id}/download",
      auditLogs: "GET /audit-logs",
      security: "GET /security/status",
      deleteSession: "DELETE /session/{session_id}",
    },

    login: function (username, password, remember) {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: username, password: password, remember: remember }),
        }).then(function (r) {
          return r.json();
        });
      }
      return delay(650).then(function () {
        var key = String(username || "").trim().toLowerCase();
        var user = users[key];
        if (!user || user.password !== password) {
          var err = new Error("Invalid credentials");
          err.code = "INVALID_CREDENTIALS";
          throw err;
        }
        var safe = {
          id: user.id,
          username: user.username,
          email: user.email,
          name: user.name,
          role: user.role,
          workspace: user.workspace,
        };
        var store = remember ? localStorage : sessionStorage;
        var other = remember ? sessionStorage : localStorage;
        store.setItem("sovereign_auth", "1");
        store.setItem("sovereign_user", JSON.stringify(safe));
        other.removeItem("sovereign_auth");
        other.removeItem("sovereign_user");
        return { ok: true, user: safe };
      });
    },

    logout: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/auth/logout", { method: "POST" }).then(function (r) {
          return r.json();
        });
      }
      return delay(200).then(function () {
        sessionStorage.removeItem("sovereign_auth");
        sessionStorage.removeItem("sovereign_user");
        localStorage.removeItem("sovereign_auth");
        localStorage.removeItem("sovereign_user");
        return { ok: true };
      });
    },

    getCurrentUser: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/users/me").then(function (r) {
          return r.json();
        });
      }
      return delay(80).then(function () {
        var user = currentUserFromStore();
        if (!user) {
          var err = new Error("Unauthenticated");
          err.code = "UNAUTHENTICATED";
          throw err;
        }
        return user;
      });
    },

    getDashboardData: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/dashboard").then(function (r) {
          return r.json();
        });
      }
      return delay().then(function () {
        return clone(dashboardData);
      });
    },

    uploadDocument: function (file, onProgress) {
      if (!USE_MOCK) {
        var fd = new FormData();
        fd.append("file", file);
        return fetch(API_BASE + "/documents", { method: "POST", body: fd }).then(function (r) {
          return r.json();
        });
      }
      return new Promise(function (resolve, reject) {
        if (!file) {
          reject(Object.assign(new Error("Upload failed."), { code: "UPLOAD_FAILED" }));
          return;
        }
        var allowed = ["pdf", "doc", "docx", "png", "jpg", "jpeg"];
        var ext = (file.name.split(".").pop() || "").toLowerCase();
        if (allowed.indexOf(ext) === -1) {
          reject(Object.assign(new Error("Upload failed. Please check the file format and try again."), { code: "UPLOAD_FAILED" }));
          return;
        }
        var pct = 0;
        var timer = setInterval(function () {
          pct += 18;
          if (pct > 100) pct = 100;
          if (onProgress) onProgress({ phase: "uploading", percent: pct });
          if (pct >= 100) {
            clearInterval(timer);
            setTimeout(function () {
              if (onProgress) onProgress({ phase: "processing", percent: 100 });
            }, 280);
            setTimeout(function () {
              if (onProgress) onProgress({ phase: "extracting", percent: 100 });
            }, 620);
            setTimeout(function () {
              if (onProgress) onProgress({ phase: "indexing", percent: 100 });
            }, 980);
            setTimeout(function () {
              var rec = {
                id: "doc_" + Date.now(),
                name: file.name,
                type: ext.toUpperCase(),
                status: "Indexed",
                uploaded: "Today",
                size: (file.size / 1024).toFixed(0) + " KB",
                kb: "Session uploads",
              };
              documents.unshift(rec);
              resolve(rec);
            }, 1280);
          }
        }, 160);
      });
    },

    sendChatMessage: function (payload) {
      if (!USE_MOCK) {
        var fd = new FormData();
        // The Python backend expects the text to be named "prompt"
        fd.append("prompt", payload.message || "");
        
        // If the user uploaded an image in the UI, attach it
        var sessionFiles = SovereignSession.loadFiles();
        if (sessionFiles && sessionFiles.length > 0 && sessionFiles[0].rawFile) {
            fd.append("image", sessionFiles[0].rawFile);
        }

        return fetch(API_BASE + "/run-agent", {
          method: "POST",
          body: fd, // Do NOT set Content-Type header; fetch does it automatically for FormData
        }).then(function (r) {
          if (!r.ok) {
             throw new Error("Backend error: " + r.status);
          }
          return r.json();
        }).then(function(backendData) {
            // Map the Python backend response to exactly what Mahek's UI expects
            return {
                result: backendData.result,
                reasoning: backendData.reasoning || "Reasoning unavailable.",
                confidence: backendData.confidence || "high",
                status: backendData.status || "completed",
                trace: backendData.trace || [],
                sources: [] 
            };
        });
      }
      
      return delay(200).then(function () {
        var text = (payload && payload.message ? payload.message : "").toLowerCase();
        if (/exfiltrat|external api|send this data offsite/.test(text)) {
          return {
            result: "",
            reasoning: "",
            confidence: "low",
            status: "security_blocked",
            trace: [{ step: 1, action: "Security screening", status: "failed" }],
            sources: [],
          };
        }
        if (/stop early|incomplete demo/.test(text)) {
          return {
            result: "Partial notes only: security screening and retrieval finished. Vision analysis did not complete.",
            reasoning: "The agent reached its execution limit before completing the requested task.",
            confidence: "low",
            status: "incomplete",
            trace: [
              { step: 1, action: "Security screening", status: "success" },
              { step: 2, action: "Searching knowledge base", status: "success" },
              { step: 3, action: "Analyzing uploaded image", status: "failed" },
            ],
            sources: [],
          };
        }
        if (/fail retrieval|retrieval fail/.test(text)) {
          return {
            result: "",
            reasoning: "",
            confidence: "low",
            status: "retrieval_failed",
            trace: [
              { step: 1, action: "Security screening", status: "success" },
              { step: 2, action: "Searching knowledge base", status: "failed" },
            ],
            sources: [],
          };
        }
        if (/generate (a )?technical( maintenance)? report|docx|download report/.test(text)) {
          return clone(reportResult);
        }
        return clone(analysisResult);
      });
    },

    getAgentTrace: function (runId) {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/agents/runs/" + encodeURIComponent(runId)).then(function (r) {
          return r.json();
        });
      }
      return delay(120).then(function () {
        return clone(analysisResult.trace);
      });
    },

    getSources: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/chat/sources").then(function (r) {
          return r.json();
        });
      }
      return delay(120).then(function () {
        return clone(analysisResult.sources);
      });
    },

    generateReport: function (payload) {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/reports", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload || {}),
        }).then(function (r) {
          return r.json();
        });
      }
      return delay(800).then(function () {
        return clone(reportResult);
      });
    },

    downloadReport: function (reportId, filename) {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/reports/" + encodeURIComponent(reportId) + "/download").then(function (r) {
          return r.blob();
        });
      }
      return delay(300).then(function () {
        var name = filename || "Maintenance_Analysis_Report.docx";
        var blob = new Blob(
          ["Sovereign AI mock DOCX placeholder for " + name + "\nSIH PS 26117 — MRPL\n"],
          { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }
        );
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

    deleteSession: function (sessionId) {
      var id = sessionId || sessionStorage.getItem("sovereign_session_id") || "session_local";
      if (!USE_MOCK) {
        return fetch(API_BASE + "/session/" + encodeURIComponent(id), { method: "DELETE" }).then(function (r) {
          if (!r.ok) throw new Error("Session delete failed");
          return r.json();
        });
      }
      return delay(500).then(function () {
        return { ok: true, message: "Session deleted successfully." };
      });
    },

    getDocuments: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/documents").then(function (r) {
          return r.json();
        });
      }
      return delay().then(function () {
        return clone(documents);
      });
    },

    deleteDocument: function (id) {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/documents/" + encodeURIComponent(id), { method: "DELETE" }).then(function (r) {
          return r.json();
        });
      }
      return delay(280).then(function () {
        documents = documents.filter(function (d) {
          return d.id !== id;
        });
        return { ok: true };
      });
    },

    getKnowledgeBases: function () {
      return delay().then(function () {
        return clone(knowledgeBases);
      });
    },

    getAgents: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/agents").then(function (r) {
          return r.json();
        });
      }
      return delay().then(function () {
        return clone(agents);
      });
    },

    getReports: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/reports").then(function (r) {
          return r.json();
        });
      }
      return delay().then(function () {
        return clone(reports);
      });
    },

    getAuditLogs: function (filters) {
      if (!USE_MOCK) {
        var q = filters ? "?" + new URLSearchParams(filters).toString() : "";
        return fetch(API_BASE + "/audit-logs" + q).then(function (r) {
          return r.json();
        });
      }
      return delay().then(function () {
        var rows = clone(auditLogs);
        if (filters && filters.query) {
          var q = filters.query.toLowerCase();
          rows = rows.filter(function (r) {
            return (r.action + r.resource + r.user + r.agent).toLowerCase().indexOf(q) !== -1;
          });
        }
        if (filters && filters.status && filters.status !== "all") {
          rows = rows.filter(function (r) {
            return r.status === filters.status;
          });
        }
        return rows;
      });
    },

    getSecurityStatus: function () {
      if (!USE_MOCK) {
        return fetch(API_BASE + "/security/status").then(function (r) {
          return r.json();
        });
      }
      return delay().then(function () {
        return clone(securityStatus);
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
        { step: 4, action: "Analyzing uploaded image", status: "waiting" },
        { step: 5, action: "Cross-referencing documents", status: "waiting" },
        { step: 6, action: "Generating answer", status: "waiting" },
      ];
    },
  };

  global.MockAPI = api;
  global.SovereignAPI = api;
})(window);
