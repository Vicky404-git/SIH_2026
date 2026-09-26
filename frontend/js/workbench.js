(function () {
  "use strict";

  var thinkingCopy = [
    "Thinking…",
    "Searching knowledge base…",
    "Analyzing image…",
    "Comparing against reference data…",
    "Generating report…",
  ];

  var pendingFiles = [];
  var busy = false;

  function $(id) {
    return document.getElementById(id);
  }

  function setState(s) {
    SovereignSession.setRunState(s);
    $("run-state").textContent = s;
  }

  function renderAttachments() {
    var host = $("attach-row");
    if (!pendingFiles.length) {
      host.innerHTML = "";
      return;
    }
    host.innerHTML = pendingFiles
      .map(function (f, i) {
        var img = f.isImage && f.preview
          ? '<img src="' + f.preview + '" alt="">'
          : "<span aria-hidden=\"true\">📄</span>";
        return (
          '<div class="file-chip">' +
          img +
          "<span>" +
          App.escapeHtml(f.name) +
          " · " +
          App.formatBytes(f.size) +
          "</span>" +
          (f.isImage
            ? '<button type="button" class="btn btn-sm" data-zoom="' + i + '">Zoom</button>'
            : "") +
          '<button type="button" class="btn btn-sm" data-remove="' +
          i +
          '">Remove</button></div>'
        );
      })
      .join("");
    host.querySelectorAll("[data-remove]").forEach(function (b) {
      b.addEventListener("click", function () {
        pendingFiles.splice(Number(b.getAttribute("data-remove")), 1);
        persistFiles();
        renderAttachments();
      });
    });
    host.querySelectorAll("[data-zoom]").forEach(function (b) {
      b.addEventListener("click", function () {
        var f = pendingFiles[Number(b.getAttribute("data-zoom"))];
        if (!f || !f.preview) return;
        App.openModal(
          "<h2>Image preview</h2><p>" +
          App.escapeHtml(f.name) +
          "</p><img src=\"" +
          f.preview +
          "\" alt=\"" +
          App.escapeHtml(f.name) +
          "\"><div class=\"modal-actions\"><button type=\"button\" class=\"btn\" id=\"close-prev\">Close</button></div>"
        );
        document.getElementById("close-prev").addEventListener("click", App.closeModal);
      });
    });
  }

  function persistFiles() {
    SovereignSession.saveFiles(
      pendingFiles.map(function (f) {
        return { name: f.name, size: f.size, type: f.type, isImage: f.isImage };
      })
    );
  }

  function addFiles(files) {
    files.forEach(function (file) {
      var meta = Upload.toMeta(file);
      if (meta.isImage) {
        meta.preview = URL.createObjectURL(file);
      }
      pendingFiles.push(meta);
    });
    persistFiles();
    renderAttachments();
  }

  function formatAnswer(text) {
    var parts = String(text || "").split(/\n\n+/);
    return parts
      .map(function (p) {
        var lines = p.split("\n");
        if (lines.some(function (l) { return /^[-•]/.test(l.trim()); })) {
          var items = lines
            .filter(function (l) { return l.trim(); })
            .map(function (l) {
              return "<li>" + App.escapeHtml(l.replace(/^[-•]\s*/, "")) + "</li>";
            })
            .join("");
          return "<ul>" + items + "</ul>";
        }
        return "<p>" + App.escapeHtml(p).replace(/\n/g, "<br>") + "</p>";
      })
      .join("");
  }

  function industrialTable(table) {
    if (!table) return "";
    var head = table.columns
      .map(function (c) {
        return "<th>" + App.escapeHtml(c) + "</th>";
      })
      .join("");
    var body = table.rows
      .map(function (r) {
        var flag = /above|watch/i.test(r[4] || "");
        return (
          "<tr>" +
          r
            .map(function (c, i) {
              var cls = i === 4 && flag ? ' class="flag"' : "";
              var prefix = i === 4 && flag ? "⚠ " : "";
              return "<td" + cls + ">" + prefix + App.escapeHtml(c) + "</td>";
            })
            .join("") +
          "</tr>"
        );
      })
      .join("");
    return (
      '<div class="industrial table-wrap" style="margin:12px 0"><table class="data"><caption class="sr-only">' +
      App.escapeHtml(table.caption || "Comparison") +
      "</caption><thead><tr>" +
      head +
      "</thead><tbody>" +
      body +
      "</tbody></table></div>"
    );
  }

  function reportCard(filename) {
    return (
      '<div class="report-card"><h3>📄 Technical Report Generated</h3><p>' +
      App.escapeHtml(filename) +
      '</p><button type="button" class="btn btn-primary" data-download="' +
      App.escapeHtml(filename) +
      '">Download Report</button></div>'
    );
  }

  function renderResult(result) {
    var status = result.status || "completed";
    var html = "";

    if (status === "security_blocked") {
      html +=
        '<div class="alert alert-err" role="alert"><strong>SECURITY BLOCKED</strong><p>Request blocked by security policy.</p><p>The system detected content that cannot be processed under the current security policy.</p></div>';
      return html;
    }
    if (status === "retrieval_failed") {
      html +=
        '<div class="alert alert-err" role="alert"><strong>RETRIEVAL FAILED</strong><p>The assistant couldn\'t complete this. Please retry or rephrase your request.</p><button type="button" class="btn btn-sm retry-btn">Retry</button></div>';
      return html;
    }
    if (status === "incomplete") {
      html +=
        '<div class="alert alert-warn" role="alert"><strong>⚠ RUN STOPPED BEFORE FINISHING</strong><p>The agent reached its execution limit before completing the requested task.</p><p>Partial progress is shown below. This is not a completed result.</p><button type="button" class="btn btn-sm retry-btn">Retry</button></div>';
    }
    if (status === "error" || status === "agent_step_failed") {
      html +=
        '<div class="alert alert-err" role="alert"><strong>Step failed — showing partial progress.</strong><p>The assistant couldn\'t complete this. Please retry or rephrase your request.</p><button type="button" class="btn btn-sm retry-btn">Retry</button></div>';
    }

    var conf = App.confidenceMeta(result.confidence);
    html += '<section class="answer-section" aria-labelledby="answer-title">';
    html += '<div class="answer-section-head"><h3 id="answer-title">AI Answer</h3>';
    html +=
      '<span class="conf conf-' +
      conf.level +
      '" role="img" aria-label="' +
      conf.label +
      '"><span aria-hidden="true">' +
      conf.icon +
      "</span> " +
      conf.label +
      "</span></div>";

    if (App.isDocxResult(result.result)) {
      html += reportCard(result.result.trim());
    } else if (result.result) {
      html += '<div class="answer-body">' + formatAnswer(result.result) + "</div>";
      html += industrialTable(result.industrialTable);
    } else {
      html += '<p class="metric-sub">No completed answer was returned.</p>';
    }
    html += "</section>";

    if (result.reasoning) {
      html +=
        '<details class="why why-section" open><summary>Agent Explanation</summary><div class="why-body">' +
        App.escapeHtml(result.reasoning) +
        "</div></details>";
    }
    return html;
  }

  function appendMessage(role, html, result) {
    var empty = $("empty-state");
    if (empty) empty.hidden = true;
    var wrap = document.createElement("article");
    wrap.className = "msg msg-" + role;
    wrap.innerHTML = '<div class="bubble">' + html + "</div>";
    $("chat-scroll").appendChild(wrap);
    $("chat-scroll").scrollTop = $("chat-scroll").scrollHeight;
    wrap.querySelectorAll("[data-download]").forEach(function (b) {
      b.addEventListener("click", function () {
        SovereignAPI.downloadReport("rep_1", b.getAttribute("data-download"));
      });
    });
    wrap.querySelectorAll(".retry-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        var last = SovereignSession.loadMessages().filter(function (m) {
          return m.role === "user";
        }).pop();
        if (last) send(last.text, true);
      });
    });
    var list = SovereignSession.loadMessages();
    list.push({ role: role, html: html, result: result || null, text: role === "user" ? wrap.innerText : "" });
    SovereignSession.saveMessages(list);
    return wrap;
  }

  function restore() {
    var msgs = SovereignSession.loadMessages();
    if (!msgs.length) return;
    $("empty-state").hidden = true;
    msgs.forEach(function (m) {
      var wrap = document.createElement("article");
      wrap.className = "msg msg-" + m.role;
      wrap.innerHTML = '<div class="bubble">' + m.html + "</div>";
      $("chat-scroll").appendChild(wrap);
    });
  }

  function renderSources(sources) {
    var host = $("sources-list");
    if (!sources || !sources.length) {
      host.innerHTML = "<p class=\"metric-sub\">No citations for this run.</p>";
      return;
    }
    host.innerHTML = sources
      .map(function (s) {
        return (
          '<button type="button" class="source-chip" data-src="' +
          App.escapeHtml(s.id) +
          '"><strong>' +
          App.escapeHtml(s.title) +
          "</strong><small>" +
          App.escapeHtml(s.page) +
          "</small></button>"
        );
      })
      .join("");
    host.querySelectorAll(".source-chip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var src = sources.find(function (x) {
          return x.id === btn.getAttribute("data-src");
        });
        if (!src) return;
        App.openModal(
          "<h2>" +
          App.escapeHtml(src.title) +
          "</h2><p>" +
          App.escapeHtml(src.page) +
          "</p><p>" +
          App.escapeHtml(src.excerpt) +
          '</p><div class="modal-actions"><button type="button" class="btn" id="close-src">Close</button></div>'
        );
        document.getElementById("close-src").addEventListener("click", App.closeModal);
      });
    });
  }

  function send(text, isRetry) {
    if (busy) return;
    var message = (text || $("composer-input").value || "").trim();
    if (!message && !pendingFiles.length) return;

    busy = true;
    $("send-btn").disabled = true;
    $("composer-input").disabled = true;
    if (!isRetry && message) {
      appendMessage("user", App.escapeHtml(message));
      $("composer-input").value = "";
    }

    var aiWrap = document.createElement("article");
    aiWrap.className = "msg msg-ai";
    aiWrap.innerHTML =
      '<div class="bubble"><div class="thinking"><span class="spinner" aria-hidden="true"></span><span id="think-label">Thinking…</span></div></div>';
    $("empty-state").hidden = true;
    $("chat-scroll").appendChild(aiWrap);

    var kind = /report|docx/i.test(message) ? "report" : "analysis";
    var plan = SovereignAPI.simulatedTracePlan(kind);
    var labels = thinkingCopy.slice();
    var li = 0;
    var thinkTimer = setInterval(function () {
      li = (li + 1) % labels.length;
      var el = document.getElementById("think-label");
      if (el) el.textContent = labels[li];
    }, 900);

    setState("THINKING");
    Trace.play($("trace-list"), plan, function (step) {
      var map = {
        "Security screening": "THINKING",
        "Document retrieval": "RETRIEVING",
        "Searching knowledge base": "RETRIEVING",
        "Analyzing uploaded image": "ANALYZING",
        "Analyzing image": "ANALYZING",
        "Cross-referencing documents": "VALIDATING",
        "Cross-referencing maintenance manual": "VALIDATING",
        "Generating answer": "THINKING",
        "Generating DOCX report": "THINKING",
      };
      setState(map[step.action] || "THINKING");
    }).then(function () {
      return SovereignAPI.sendChatMessage({
        message: message,
        session_id: SovereignSession.getSessionId(),
        attachments: pendingFiles.map(function (f) {
          return f.name;
        }),
      });
    }).then(function (result) {
      clearInterval(thinkTimer);
      Trace.applyFinal($("trace-list"), result.trace);
      var st = result.status;
      if (st === "completed") setState("COMPLETED");
      else if (st === "incomplete") setState("INCOMPLETE");
      else if (st === "security_blocked") setState("SECURITY_BLOCKED");
      else if (st === "retrieval_failed") setState("RETRIEVAL_FAILED");
      else setState("AGENT_STEP_FAILED");
      aiWrap.querySelector(".bubble").innerHTML = renderResult(result);
      renderSources(result.sources);
      var list = SovereignSession.loadMessages();
      list.push({ role: "ai", html: aiWrap.querySelector(".bubble").innerHTML, result: result });
      SovereignSession.saveMessages(list);
      aiWrap.querySelectorAll("[data-download]").forEach(function (b) {
        b.addEventListener("click", function () {
          SovereignAPI.downloadReport("rep_1", b.getAttribute("data-download"));
        });
      });
      aiWrap.querySelectorAll(".retry-btn").forEach(function (b) {
        b.addEventListener("click", function () {
          send(message, true);
        });
      });
    }).catch(function () {
      clearInterval(thinkTimer);
      setState("NETWORK_ERROR");
      aiWrap.querySelector(".bubble").innerHTML =
        '<div class="alert alert-err" role="alert">The assistant couldn\'t complete this. Please retry or rephrase your request.<br><button type="button" class="btn btn-sm retry-btn">Retry</button></div>';
    }).finally(function () {
      busy = false;
      $("send-btn").disabled = false;
      $("composer-input").disabled = false;
      $("chat-scroll").scrollTop = $("chat-scroll").scrollHeight;
    });
  }

  function uploadFiles(files) {
    if (!files.length) return;
    addFiles(files);
    setState("UPLOADING");
    $("upload-status").hidden = false;
    var bar = $("upload-bar");
    var label = $("upload-label");
    var queue = files.slice();
    function next() {
      if (!queue.length) {
        setState("IDLE");
        setTimeout(function () {
          $("upload-status").hidden = true;
        }, 600);
        return;
      }
      var file = queue.shift();
      Upload.uploadWithFormData(file, function (p) {
        var map = {
          uploading: "Uploading…",
          processing: "Processing document…",
          extracting: "Extracting content…",
          indexing: "Indexing…",
        };
        label.textContent = map[p.phase] || "Working…";
        bar.style.width = (p.percent || 0) + "%";
        if (p.phase === "processing") setState("PROCESSING");
      }).then(next).catch(function (err) {
        setState("UPLOAD_FAILED");
        $("upload-status").hidden = false;
        label.textContent = err.message || "Upload failed. Please check the file format and try again.";
        App.toast(err.message || "Upload failed.", "err");
      });
    }
    next();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var user = App.mountLayout("workbench");
    if (!user) return;
    restore();
    renderAttachments();
    setState(SovereignSession.getRunState());

    Upload.bindDropzone($("dropzone"), uploadFiles);
    $("attach-btn").addEventListener("click", function () {
      Upload.pick(uploadFiles);
    });
    $("send-btn").addEventListener("click", function () {
      send();
    });
    $("composer-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });
    document.querySelectorAll("[data-prompt]").forEach(function (c) {
      c.addEventListener("click", function () {
        $("composer-input").value = c.getAttribute("data-prompt");
        send();
      });
    });
    $("context-toggle").addEventListener("click", function () {
      document.body.classList.toggle("context-open");
    });
  });
})();
