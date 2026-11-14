// Krav: K51 i docs/02-KRAV.md, ADR-0074. Test: tests/test_tema.py.
// Står i sidans <head>: sätter det tema som besökaren sparat innan sidan
// ritas, och visar sedan knappen som byter och sparar temat. Utan sparat
// tema gäller läsarens inställning.
(function () {
  var rot = document.documentElement;
  var minne = lagring();

  // En webbläsare som spärrat lagringen kastar ett fel vid åtkomsten; då
  // gäller valet bara på sidan.
  function lagring() {
    try {
      return window.localStorage;
    } catch (e) {
      return null;
    }
  }

  function morkt() {
    if (rot.dataset.tema) return rot.dataset.tema === "morkt";
    return matchMedia("(prefers-color-scheme: dark)").matches;
  }

  rot.dataset.tema = (minne && minne.getItem("tema")) || "";
  document.addEventListener("DOMContentLoaded", function () {
    var knapp = document.querySelector(".tema");
    knapp.setAttribute("aria-pressed", morkt());
    knapp.addEventListener("click", function () {
      rot.dataset.tema = morkt() ? "ljust" : "morkt";
      knapp.setAttribute("aria-pressed", morkt());
      if (minne) minne.setItem("tema", rot.dataset.tema);
    });
    knapp.hidden = false;
  });
})();
