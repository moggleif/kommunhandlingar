// Krav: K50 i docs/02-KRAV.md, ADR-0073. Test: tests/test_malar.py prövar att
// skriptet och väljarna står på sidan; hur det beter sig prövas för hand.
// Står på målsidan. Visar ett perspektiv i taget, och i Ett år i taget ett
// år, efter adressen: ?vy=tidslinje, ?vy=ar&ar=2025 eller ?vy=kort. Utan val
// är det tidslinjen och det senaste valda året, först det senaste året, och
// en adress till ett kort (#mal-3) visar korten. Varje val läggs i
// webbläsarens historik. Ett mål som väljs visar korten redan i
// klickhanteraren, så att webbläsaren kan gå till kortet. Utan skriptet står
// alla perspektiv.
(function () {
  var perspektiv = document.querySelector(".perspektiv");
  var arval = document.querySelector(".arval");
  var valt = null;
  var aren = Array.prototype.map.call(arval.querySelectorAll("button"), function (knapp) {
    return knapp.dataset.ar;
  });

  // Adressen kan vara skriven för hand; ett okänt val ger förvalet.
  function lage() {
    var fraga = new URLSearchParams(location.search);
    var vy = /^#mal-/.test(location.hash) ? "kort" : fraga.get("vy");
    if (!perspektiv.querySelector('[data-vy="' + vy + '"]')) vy = "tidslinje";
    var onskat = fraga.get("ar") || valt;
    var ar = aren.indexOf(onskat) >= 0 ? onskat : aren[aren.length - 1];
    return { vy: vy, ar: ar };
  }

  function markera(grupp, falt, varde) {
    grupp.querySelectorAll("button").forEach(function (knapp) {
      knapp.setAttribute("aria-pressed", knapp.dataset[falt] === varde);
    });
  }

  function visaVy(vy) {
    document.querySelectorAll("section[data-vy]").forEach(function (sektion) {
      sektion.hidden = sektion.dataset.vy !== vy;
    });
    markera(perspektiv, "vy", vy);
  }

  function visa() {
    var nu = lage();
    valt = nu.ar;
    visaVy(nu.vy);
    document.querySelectorAll("section.aret").forEach(function (sektion) {
      sektion.hidden = sektion.dataset.ar !== nu.ar;
    });
    markera(arval, "ar", nu.ar);
  }

  function ga(vy, ar) {
    history.pushState(null, "", "?vy=" + vy + (vy === "ar" ? "&ar=" + ar : ""));
    visa();
  }

  perspektiv.querySelectorAll("button").forEach(function (knapp) {
    knapp.addEventListener("click", function () {
      ga(knapp.dataset.vy, lage().ar);
    });
  });
  arval.querySelectorAll("button").forEach(function (knapp) {
    knapp.addEventListener("click", function () {
      ga("ar", knapp.dataset.ar);
    });
  });
  window.addEventListener("popstate", visa);
  document.querySelectorAll("a[href^='#mal-']").forEach(function (lank) {
    lank.addEventListener("click", function () {
      visaVy("kort");
      setTimeout(function () {
        history.replaceState(null, "", "?vy=kort" + location.hash);
        visa();
      });
    });
  });
  perspektiv.hidden = false;
  arval.hidden = false;
  visa();
})();
