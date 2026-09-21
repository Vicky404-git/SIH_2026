(function (global) {
  "use strict";

  var STATES = {
    waiting: { label: "Waiting", icon: "○" },
    running: { label: "Running", icon: "●" },
    success: { label: "Completed", icon: "✓" },
    failed: { label: "Failed", icon: "✕" },
  };

  function render(container, steps) {
    if (!container) return;
    container.innerHTML = (steps || [])
      .map(function (s) {
        var st = STATES[s.status] || STATES.waiting;
        return (
          '<div class="trace-step" data-status="' +
          App.escapeHtml(s.status || "waiting") +
          '">' +
          '<span aria-hidden="true">' +
          st.icon +
          "</span>" +
          "<div><div class=\"t-action\">Step " +
          App.escapeHtml(s.step) +
          ": " +
          App.escapeHtml(s.action) +
          '</div><div class="t-status">' +
          st.label +
          (s.status === "success" ? " — OK" : "") +
          "</div></div></div>"
        );
      })
      .join("");
  }

  /**
   * Simulated streaming trace. Replace play() internals with SSE/WebSocket/polling.
   */
  function play(container, plan, onUpdate, interval) {
    var steps = (plan || []).map(function (s) {
      return { step: s.step, action: s.action, status: "waiting" };
    });
    render(container, steps);
    var i = 0;
    return new Promise(function (resolve) {
      function tick() {
        if (i > 0) steps[i - 1].status = "success";
        if (i < steps.length) {
          steps[i].status = "running";
          render(container, steps);
          if (onUpdate) onUpdate(steps[i], steps);
          i += 1;
          setTimeout(tick, interval || 520);
        } else {
          render(container, steps);
          resolve(steps);
        }
      }
      tick();
    });
  }

  function applyFinal(container, trace) {
    render(
      container,
      (trace || []).map(function (s) {
        var status = s.status;
        if (status === "ok" || status === "completed") status = "success";
        return { step: s.step, action: s.action, status: status };
      })
    );
  }

  global.Trace = { render: render, play: play, applyFinal: applyFinal, STATES: STATES };
})(window);
