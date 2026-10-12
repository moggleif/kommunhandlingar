// Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.
// Visar en månad i taget med början på innevarande, döljer det som varit i
// listan och de organ som valts bort. Utan skriptet står allt på sidan.
(function () {
  var nu = new Date();
  var tva = function (n) { return (n < 10 ? "0" : "") + n; };
  var manad = nu.getFullYear() + "-" + tva(nu.getMonth() + 1);
  var idag = manad + "-" + tva(nu.getDate());
  var manader = Array.prototype.slice.call(document.querySelectorAll(".manad"));
  var valda = {};
  var visad = 0;
  manader.forEach(function (m, i) { if (m.dataset.manad <= manad) { visad = i; } });

  function visaManad() {
    manader.forEach(function (m, i) { m.hidden = i !== visad; });
    document.querySelector('[data-steg="-1"]').disabled = visad === 0;
    document.querySelector('[data-steg="1"]').disabled = visad === manader.length - 1;
  }

  function visaUrval() {
    document.querySelectorAll(".manad [data-organ]").forEach(function (r) {
      r.hidden = !valda[r.dataset.organ];
    });
    document.querySelectorAll(".listmanad").forEach(function (m) {
      var synliga = 0;
      m.querySelectorAll("tr[data-organ]").forEach(function (r) {
        r.hidden = !valda[r.dataset.organ] || r.dataset.datum < idag;
        synliga += r.hidden ? 0 : 1;
      });
      m.hidden = synliga === 0;
    });
  }

  document.querySelectorAll(".urval input").forEach(function (ruta) {
    valda[ruta.dataset.organ] = ruta.checked;
    ruta.addEventListener("change", function () {
      valda[ruta.dataset.organ] = ruta.checked;
      visaUrval();
    });
  });
  document.querySelectorAll("[data-steg]").forEach(function (knapp) {
    knapp.addEventListener("click", function () {
      visad += Number(knapp.dataset.steg);
      visaManad();
    });
  });
  document.querySelector(".blad").hidden = false;
  visaManad();
  visaUrval();
})();
