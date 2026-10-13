// Krav: K29 i docs/02-KRAV.md, ADR-0050. Test: tests/test_malkort.py.
// Visar bara de mål i tidslinjen och bland korten som valts med en knapp,
// och öppnar historiken på kortet för ett mål som väljs i tidslinjen.
// Utan skriptet står allt och historiken är hopfälld.
(function () {
  var urval = document.querySelector(".urval");
  var knappar = urval.querySelectorAll("button");

  function passar(mal, val) {
    if (val === "alla") return true;
    if (val === "aktiv" || val === "bytt") return mal.dataset[val] === "ja";
    return mal.dataset.slag === val;
  }

  function valj(val) {
    knappar.forEach(function (knapp) {
      knapp.setAttribute("aria-pressed", knapp.dataset.urval === val);
    });
    document.querySelectorAll("[data-mal]").forEach(function (mal) {
      mal.hidden = !passar(mal, val);
    });
  }

  function oppna() {
    var kort = document.getElementById(location.hash.slice(1));
    if (kort && kort.tagName === "ARTICLE") kort.querySelector("details").open = true;
  }

  knappar.forEach(function (knapp) {
    knapp.addEventListener("click", function () {
      valj(knapp.dataset.urval);
    });
  });
  window.addEventListener("hashchange", oppna);
  urval.hidden = false;
  valj("alla");
  oppna();
})();
