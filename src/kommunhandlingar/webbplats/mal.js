// Krav: K29, K35 och K50 i docs/02-KRAV.md, ADR-0050, ADR-0056 och ADR-0073.
// Test: tests/test_malkort.py, tests/test_malar.py och tests/test_fokusomraden.py.
// Visar ett perspektiv i taget, och i Ett år i taget ett år, efter adressen:
// ?vy=tidslinje, ?vy=ar&ar=2025 eller ?vy=kort. Utan val är det tidslinjen
// och det senaste året, och en adress till ett kort (#mal-3) visar korten.
// Varje val läggs i webbläsarens historik.
// Visar bara de mål som valts med urvalet, i alla perspektiv, och döljer ett
// slags rubrik i tidslinjen när inget av dess mål visas. Ett kommunmåls kort
// visas när ett av dess fokusområden visas.
// Ett mål som väljs i tidslinjen visar korten och öppnar kortets historik,
// också när samma mål väljs igen.
// Utan skriptet står allt och historiken är hopfälld.
(function () {
  var urval = document.querySelector(".urval");
  var knappar = urval.querySelectorAll("button");
  var perspektiv = document.querySelector(".perspektiv");
  var arval = document.querySelector(".arval");
  var aren = Array.prototype.map.call(arval.querySelectorAll("button"), function (knapp) {
    return knapp.dataset.ar;
  });

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

  // Adressen kan vara skriven för hand; ett okänt val ger förvalet.
  function lage() {
    var fraga = new URLSearchParams(location.search);
    var vy = fraga.get("vy");
    if (/^#mal-/.test(location.hash)) vy = "kort";
    if (!perspektiv.querySelector('[data-vy="' + vy + '"]')) vy = "tidslinje";
    var ar = aren.indexOf(fraga.get("ar")) >= 0 ? fraga.get("ar") : aren[aren.length - 1];
    return { vy: vy, ar: ar };
  }

  function visaVy(vy) {
    document.querySelectorAll("section[data-vy]").forEach(function (sektion) {
      sektion.hidden = sektion.dataset.vy !== vy;
    });
    perspektiv.querySelectorAll("button").forEach(function (knapp) {
      knapp.setAttribute("aria-pressed", knapp.dataset.vy === vy);
    });
  }

  function visa() {
    var nu = lage();
    visaVy(nu.vy);
    document.querySelectorAll("section.aret").forEach(function (sektion) {
      sektion.hidden = sektion.dataset.ar !== nu.ar;
    });
    arval.querySelectorAll("button").forEach(function (knapp) {
      knapp.setAttribute("aria-pressed", knapp.dataset.ar === nu.ar);
    });
  }

  function ga(vy, ar) {
    history.pushState(null, "", "?vy=" + vy + (vy === "ar" ? "&ar=" + ar : ""));
    visa();
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
  window.addEventListener("popstate", function () {
    visa();
    oppna();
  });
  // Korten visas före klicket, så att webbläsaren kan gå till kortet.
  document.querySelectorAll("a[href^='#mal-']").forEach(function (lank) {
    lank.addEventListener("click", function () {
      visaVy("kort");
      setTimeout(function () {
        history.replaceState(null, "", "?vy=kort" + location.hash);
        visa();
        oppna();
      });
    });
  });
  urval.hidden = false;
  perspektiv.hidden = false;
  arval.hidden = false;
  valj("alla");
  visa();
  oppna();
})();
