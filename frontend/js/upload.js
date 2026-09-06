(function (global) {
  "use strict";

  var ACCEPT = ".pdf,.doc,.docx,.png,.jpg,.jpeg";

  function bindDropzone(el, onFiles) {
    if (!el) return;
    el.addEventListener("dragover", function (e) {
      e.preventDefault();
      el.classList.add("is-over");
    });
    el.addEventListener("dragleave", function () {
      el.classList.remove("is-over");
    });
    el.addEventListener("drop", function (e) {
      e.preventDefault();
      el.classList.remove("is-over");
      if (e.dataTransfer.files && e.dataTransfer.files.length) {
        onFiles(Array.prototype.slice.call(e.dataTransfer.files));
      }
    });
  }

  function pick(onFiles) {
    var input = document.createElement("input");
    input.type = "file";
    input.accept = ACCEPT;
    input.multiple = true;
    input.addEventListener("change", function () {
      onFiles(Array.prototype.slice.call(input.files || []));
    });
    input.click();
  }

  function toMeta(file) {
    return {
      name: file.name,
      size: file.size,
      type: file.type,
      ext: (file.name.split(".").pop() || "").toLowerCase(),
      isImage: /^image\//.test(file.type) || /\.(png|jpe?g)$/i.test(file.name),
      file: file,
    };
  }

  function uploadWithFormData(file, onProgress) {
    /* Ready for: fetch(API + '/documents', { method: 'POST', body: fd }) */
    var fd = new FormData();
    fd.append("file", file);
    fd.append("session_id", SovereignSession.getSessionId());
    return SovereignAPI.uploadDocument(file, onProgress).then(function (res) {
      res._formDataPrepared = true;
      return res;
    });
  }

  global.Upload = {
    ACCEPT: ACCEPT,
    bindDropzone: bindDropzone,
    pick: pick,
    toMeta: toMeta,
    uploadWithFormData: uploadWithFormData,
  };
})(window);
