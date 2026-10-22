// Krav: K29 och K35 i docs/02-KRAV.md, ADR-0050 och ADR-0056.
// Test: tests/test_malkort.py och tests/test_fokusomraden.py.
// Visar bara de mål i tidslinjen och bland korten som valts med en knapp,
// och döljer ett slags rubrik i tidslinjen när inget av dess mål visas.
// Öppnar historiken på kortet för ett mål som väljs i tidslinjen, också
// när samma mål väljs igen. Ett kommunmåls kort visas när ett av dess
// fokusområden visas.
// Utan skriptet står allt och historiken är hopfälld.
(function () {
  var urval = document.querySelector(".urval");
  var knappar = urval.querySelectorAll("button");

  function passar(mal, val) {
    if (val === "alla") return true;
    if (val === "aktiv" || val === "bytt") return mal.dataset[val] === "ja";
    return mal.dataset.slag.split(" ").indexOf(val) >= 0;
  }

  function valj(val) {
    knappar.forEach(function (knapp) {
      knapp.setAttribute("aria-pressed", knapp.dataset.urval === val);
    });
    document.querySelectorAll("[data-mal]").forEach(function (mal) {
      mal.hidden = !passar(mal, val);
    });
    document.querySelectorAll(".fokusomraden [data-mal]:not([hidden])").forEach(function (fokus) {
      fokus.parentNode.closest("article").hidden = false;
    });
    document.querySelectorAll("tr.slag").forEach(function (rubrik) {
      rubrik.hidden = !rubrik.parentNode.querySelector("[data-mal]:not([hidden])");
    });
  }

  function oppna() {
    var kort = document.getElementById(location.hash.slice(1));
    if (kort && kort.tagName === "ARTICLE") kort.querySelector(":scope > details").open = true;
  }

  knappar.forEach(function (knapp) {
    knapp.addEventListener("click", function () {
      valj(knapp.dataset.urval);
    });
  });
  window.addEventListener("hashchange", oppna);
  document.querySelectorAll("tr[data-mal] a").forEach(function (lank) {
    lank.addEventListener("click", function () {
      setTimeout(oppna);
    });
  });
  urval.hidden = false;
  valj("alla");
  oppna();
})();
