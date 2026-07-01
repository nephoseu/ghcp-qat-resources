document.addEventListener("DOMContentLoaded", function () {
  var content = document.querySelector(".md-content");
  if (!content) return;

  content.addEventListener("copy", function (e) {
    e.preventDefault();
  });
  content.addEventListener("cut", function (e) {
    e.preventDefault();
  });
  content.addEventListener("contextmenu", function (e) {
    e.preventDefault();
  });
  content.addEventListener("keydown", function (e) {
    var key = e.key ? e.key.toLowerCase() : "";
    if ((e.ctrlKey || e.metaKey) && (key === "c" || key === "x")) {
      e.preventDefault();
    }
  });
});
