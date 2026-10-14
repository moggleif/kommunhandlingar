// Krav: K22 och K32 i docs/02-KRAV.md, ADR-0032 och ADR-0053.
// Test: tests/test_kalender.py.
// Visar en månad i taget med början på innevarande, döljer det som varit i
// listan tills knappen trycks och de organ som valts bort, och fäller ut kvaliteten när en länk
// till de osäkra datumen följs. Utan skriptet står allt på sidan.
(function () {
  var nu = new Date();
  var manad = nu.getFullYear() + "-" + tvasiffrigt(nu.getMonth() + 1);
  var idag = manad + "-" + tvasiffrigt(nu.getDate());
  var manader = Array.prototype.slice.call(document.querySelectorAll(".manad"));
  var valda = {};
  var visad = 0;
  var tidigare = false;

  function tvasiffrigt(n) {
    return (n < 10 ? "0" : "") + n;
  }

  function visaManad() {
    manader.forEach(function (m, i) { m.hidden = i !== visad; });
    document.querySelector('[data-steg="-1"]').disabled = visad === 0;
    document.querySelector('[data-steg="1"]').disabled = visad === manader.length - 1;
  }

  function visaRad(rad) {
    rad.hidden = !valda[rad.dataset.organ] || (!tidigare && rad.dataset.datum < idag);
    return !rad.hidden;
  }

  function visaUrval() {
    document.querySelectorAll(".manad [data-organ]").forEach(function (ruta) {
      ruta.hidden = !valda[ruta.dataset.organ];
    });
    document.querySelectorAll(".listmanad").forEach(function (m) {
      var rader = Array.prototype.slice.call(m.querySelectorAll("tr[data-organ]"));
      m.hidden = rader.map(visaRad).indexOf(true) === -1;
    });
  }

  function kopplaUrval(ruta) {
    valda[ruta.dataset.organ] = ruta.checked;
    ruta.addEventListener("change", function () {
      valda[ruta.dataset.organ] = ruta.checked;
      visaUrval();
    });
  }

  function oppnaKvalitet() {
    document.getElementById("kvalitet").open = true;
  }

  function kopplaSteg(knapp) {
    knapp.addEventListener("click", function () {
      visad += Number(knapp.dataset.steg);
      visaManad();
    });
  }

  function kopplaTidigare(knapp) {
    knapp.addEventListener("click", function () {
      tidigare = !tidigare;
      knapp.textContent = (tidigare ? "Dölj" : "Visa") + " tidigare sammanträden";
      visaUrval();
    });
  }

  if (!manader.length) { return; }
  manader.forEach(function (m, i) { if (m.dataset.manad <= manad) { visad = i; } });
  document.querySelectorAll(".urval input").forEach(kopplaUrval);
  document.querySelectorAll("[data-steg]").forEach(kopplaSteg);
  document.querySelectorAll('a[href="#osakra"]').forEach(function (lank) {
    lank.addEventListener("click", oppnaKvalitet);
  });
  kopplaTidigare(document.querySelector(".tidigare button"));
  document.querySelector(".tidigare").hidden = false;
  document.querySelector(".blad").hidden = false;
  visaManad();
  visaUrval();
})();
