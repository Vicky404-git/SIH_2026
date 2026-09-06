(function (global) {
  "use strict";

  var KEYS = {
    sessionId: "sovereign_session_id",
    messages: "sovereign_messages",
    files: "sovereign_session_files",
    state: "sovereign_run_state",
  };

  function getSessionId() {
    var id = sessionStorage.getItem(KEYS.sessionId);
    if (!id) {
      id = "ses_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 8);
      sessionStorage.setItem(KEYS.sessionId, id);
    }
    return id;
  }

  function loadMessages() {
    try {
      return JSON.parse(sessionStorage.getItem(KEYS.messages) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveMessages(list) {
    sessionStorage.setItem(KEYS.messages, JSON.stringify(list));
  }

  function loadFiles() {
    try {
      return JSON.parse(sessionStorage.getItem(KEYS.files) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveFiles(list) {
    sessionStorage.setItem(KEYS.files, JSON.stringify(list));
  }

  function setRunState(state) {
    sessionStorage.setItem(KEYS.state, state);
  }

  function getRunState() {
    return sessionStorage.getItem(KEYS.state) || "IDLE";
  }

  function clearLocal() {
    sessionStorage.removeItem(KEYS.sessionId);
    sessionStorage.removeItem(KEYS.messages);
    sessionStorage.removeItem(KEYS.files);
    sessionStorage.removeItem(KEYS.state);
  }

  function deleteEverything() {
    var id = getSessionId();
    return SovereignAPI.deleteSession(id).then(function (res) {
      if (!res || !res.ok) {
        throw new Error("Session delete was not confirmed by the server.");
      }
      clearLocal();
      return res;
    });
  }

  global.SovereignSession = {
    getSessionId: getSessionId,
    loadMessages: loadMessages,
    saveMessages: saveMessages,
    loadFiles: loadFiles,
    saveFiles: saveFiles,
    setRunState: setRunState,
    getRunState: getRunState,
    clearLocal: clearLocal,
    deleteEverything: deleteEverything,
    KEYS: KEYS,
  };
})(window);
