/* Skrypty serwisu.
 *
 * Wcześniej wszystko to siedziało w czterech blokach <script> wklejonych
 * bezpośrednio w szablony. Wyniesione tutaj, bo dzięki temu:
 *  - kod jest jeden, a nie powielony na każdej stronie od nowa,
 *  - WhiteNoise nadaje mu hash w nazwie i cache na rok zamiast wysyłać
 *    go w treści każdej podstrony,
 *  - da się z CSP zdjąć 'unsafe-inline' dla script-src, bo w HTML nie ma
 *    już ani jednego wykonywalnego skryptu ani atrybutu onclick.
 *
 * Każdy fragment sprawdza, czy jego elementy w ogóle są na stronie, więc
 * ten sam plik obsługuje wszystkie szablony.
 *
 * Identyfikator Google Analytics przychodzi przez data-ga-id na <body>,
 * bo plik statyczny nie przechodzi przez silnik szablonów.
 */

(function () {
  'use strict';

  // ── Zgoda na cookies i Google Analytics ──────────────────────────

  function idAnalityki() {
    return document.body.getAttribute('data-ga-id') || '';
  }

  function wczytajGA() {
    var id = idAnalityki();
    if (!id) return;

    var skrypt = document.createElement('script');
    skrypt.async = true;
    skrypt.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(skrypt);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id, { anonymize_ip: true });

    document.querySelectorAll('a[href^="tel:"]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.gtag('event', 'phone_click', {
          event_category: 'engagement',
          event_label: this.getAttribute('href')
        });
      });
    });
  }

  function zapisanaZgoda() {
    try {
      return JSON.parse(localStorage.getItem('cookie_preferences')) || null;
    } catch (e) {
      return null;
    }
  }

  function tokenCsrf() {
    var ciasteczka = document.cookie.split(';');
    for (var i = 0; i < ciasteczka.length; i++) {
      var c = ciasteczka[i].trim();
      if (c.indexOf('csrftoken=') === 0) return c.substring('csrftoken='.length);
    }
    return '';
  }

  function zapiszZgode(preferencje) {
    try {
      localStorage.setItem('cookie_preferences', JSON.stringify(preferencje));
    } catch (e) { /* tryb prywatny albo zablokowane dane witryny */ }

    // Rejestr po stronie serwera jest ścieżką audytową, więc jego awaria
    // nie może przeszkodzić w zapisaniu wyboru w przeglądarce.
    try {
      fetch('/api/log-cookie-consent/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': tokenCsrf() },
        body: JSON.stringify({ analytics: preferencje.analytics || false })
      }).catch(function () { });
    } catch (e) { /* bez fetch nic nie zapiszemy, wybór i tak działa */ }
  }

  function usunCiasteczkaGA() {
    document.cookie.split(';').forEach(function (wpis) {
      var nazwa = wpis.split('=')[0].trim();
      if (nazwa.indexOf('_ga') === 0 || nazwa.indexOf('_gid') === 0) {
        document.cookie = nazwa + '=; Max-Age=0; path=/';
        document.cookie = nazwa + '=; Max-Age=0; path=/; domain=.' + location.hostname;
      }
    });
  }

  function obsluzCookies() {
    var banner = document.getElementById('cookie-banner');
    var okno = document.getElementById('cookie-preferences');
    var przelacznik = document.getElementById('analytics-cookies');
    if (!banner || !okno || !przelacznik) return;

    var zgodaPrzyWczytaniu = zapisanaZgoda();

    if (!zgodaPrzyWczytaniu) {
      banner.style.display = 'block';
    } else if (zgodaPrzyWczytaniu.analytics) {
      wczytajGA();
    }

    function otworzOkno(zdarzenie) {
      if (zdarzenie) zdarzenie.preventDefault();
      var zapisana = zapisanaZgoda();
      przelacznik.checked = !!(zapisana && zapisana.analytics);
      okno.style.display = 'block';
    }

    function zamknijOkno() {
      okno.style.display = 'none';
    }

    document.getElementById('accept-cookies').addEventListener('click', function () {
      zapiszZgode({ necessary: true, analytics: true });
      banner.style.display = 'none';
      wczytajGA();
    });

    document.getElementById('decline-cookies').addEventListener('click', function () {
      zapiszZgode({ necessary: true, analytics: false });
      banner.style.display = 'none';
    });

    document.getElementById('cookie-settings').addEventListener('click', otworzOkno);
    document.getElementById('close-preferences').addEventListener('click', zamknijOkno);

    // Stałe wejście do ustawień z każdej podstrony. Bez niego zgody nie dało się
    // wycofać po zamknięciu bannera, a art. 7 ust. 3 RODO wymaga, żeby wycofanie
    // było tak samo łatwe jak udzielenie.
    document.querySelectorAll('[data-akcja="ustawienia-cookies"]').forEach(function (el) {
      el.addEventListener('click', otworzOkno);
    });

    document.getElementById('save-preferences').addEventListener('click', function () {
      var wlaczona = przelacznik.checked;
      var bylaWlaczona = !!(zgodaPrzyWczytaniu && zgodaPrzyWczytaniu.analytics);

      zapiszZgode({ necessary: true, analytics: wlaczona });
      banner.style.display = 'none';
      zamknijOkno();

      if (wlaczona) {
        wczytajGA();
      } else if (bylaWlaczona) {
        // Skrypt GA jest już w pamięci strony, więc samo cofnięcie zgody by go
        // nie zatrzymało. Kasujemy ciasteczka i przeładowujemy stronę.
        usunCiasteczkaGA();
        location.reload();
      }
    });

    okno.addEventListener('click', function (zdarzenie) {
      if (zdarzenie.target === okno) zamknijOkno();
    });
  }

  // ── Menu na telefonie ────────────────────────────────────────────

  function obsluzMenu() {
    var przycisk = document.querySelector('.mobile-menu-toggle');
    var menu = document.querySelector('.navbar-menu');
    var tlo = document.querySelector('.mobile-menu-overlay');
    if (!przycisk || !menu || !tlo) return;

    function zamknij() {
      menu.classList.remove('active');
      tlo.classList.remove('active');
    }

    przycisk.addEventListener('click', function () {
      menu.classList.toggle('active');
      tlo.classList.toggle('active');
    });
    tlo.addEventListener('click', zamknij);
    menu.querySelectorAll('.nav-link').forEach(function (link) {
      link.addEventListener('click', zamknij);
    });
  }

  // ── Formularz rezerwacji ─────────────────────────────────────────

  function obsluzFormularzRezerwacji() {
    var pokaz = document.getElementById('show-form-btn');
    var ukryj = document.getElementById('hide-form-btn');
    var ramka = document.getElementById('booking-form-wrapper');
    if (!ramka) return;

    if (pokaz) {
      pokaz.addEventListener('click', function () {
        ramka.style.display = 'block';
        ramka.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    }
    if (ukryj) {
      ukryj.addEventListener('click', function () {
        ramka.style.display = 'none';
      });
    }
  }

  // ── Rozwijane pytania ────────────────────────────────────────────

  function obsluzFaq() {
    // Jeden delegowany listener na listę zamiast atrybutu przy każdym pytaniu.
    document.querySelectorAll('.faq-list').forEach(function (lista) {
      lista.addEventListener('click', function (zdarzenie) {
        var przycisk = zdarzenie.target.closest('.faq-question');
        if (!przycisk) return;
        var otwarte = przycisk.parentElement.classList.toggle('active');
        przycisk.setAttribute('aria-expanded', otwarte ? 'true' : 'false');
      });
    });
  }

  // ── Kopiowanie odnośnika do artykułu ─────────────────────────────

  function obsluzKopiowanie() {
    document.querySelectorAll('[data-kopiuj]').forEach(function (przycisk) {
      przycisk.addEventListener('click', function () {
        var adres = przycisk.getAttribute('data-kopiuj');
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(adres).then(function () {
          var pierwotny = przycisk.getAttribute('aria-label') || przycisk.textContent;
          przycisk.setAttribute('aria-label', 'Skopiowano odnośnik');
          przycisk.classList.add('skopiowano');
          setTimeout(function () {
            przycisk.setAttribute('aria-label', pierwotny);
            przycisk.classList.remove('skopiowano');
          }, 2000);
        });
      });
    });
  }

  // ── Płynne przewijanie do kotwic ─────────────────────────────────

  function obsluzKotwice() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(function (link) {
      link.addEventListener('click', function (zdarzenie) {
        var cel = document.getElementById(link.getAttribute('href').slice(1));
        if (!cel) return;
        zdarzenie.preventDefault();
        cel.scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  function start() {
    obsluzCookies();
    obsluzMenu();
    obsluzFormularzRezerwacji();
    obsluzFaq();
    obsluzKopiowanie();
    obsluzKotwice();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
