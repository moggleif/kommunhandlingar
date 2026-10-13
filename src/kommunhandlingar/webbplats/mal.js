// Krav: K26 i docs/02-KRAV.md, ADR-0044. Test: tests/test_mal.py.
// Döljer de slag som valts bort, och visar bara ett mål, och åren det står
// med, när dess rubrik i översikten väljs, tills knappen visar alla igen.
// Utan skriptet står allt.
(function () {
  var valda = {};
  var spar = null;
  var alla = document.getElementById("alla");

  function visa() {
    document.querySelectorAll("[data-spar]").forEach(function (rad) {
      rad.hidden = !valda[rad.dataset.slag] || (spar !== null && rad.dataset.spar !== spar);
    });
    document.querySelectorAll("section[id^=ar-]").forEach(function (ar) {
      ar.hidden = spar !== null && !ar.querySelector("article:not([hidden])");
    });
    alla.hidden = spar === null;
  }

  function kopplaUrval(ruta) {
    valda[ruta.dataset.slag] = ruta.checked;
    ruta.addEventListener("change", function () {
      valda[ruta.dataset.slag] = ruta.checked;
      visa();
    });
  }

  function kopplaSpar(knapp) {
    knapp.addEventListener("click", function () {
      spar = knapp.closest("tr").dataset.spar;
      visa();
    });
  }

  document.querySelectorAll(".urval input").forEach(kopplaUrval);
  document.querySelectorAll("button.spar").forEach(kopplaSpar);
  alla.addEventListener("click", function () {
    spar = null;
    visa();
  });
  visa();
})();
