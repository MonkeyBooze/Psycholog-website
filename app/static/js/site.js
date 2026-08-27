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

  function analyticsId() {
    return document.body.getAttribute('data-ga-id') || '';
  }

  function loadAnalytics() {
    var id = analyticsId();
    if (!id) return;

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id);

    document.querySelectorAll('a[href^="tel:"]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.gtag('event', 'phone_click', {
          event_category: 'engagement',
          event_label: this.getAttribute('href')
        });
      });
    });
  }

  function storedConsent() {
    try {
      return JSON.parse(localStorage.getItem('cookie_preferences')) || null;
    } catch (e) {
      return null;
    }
  }

  function csrfToken() {
    var cookieList = document.cookie.split(';');
    for (var i = 0; i < cookieList.length; i++) {
      var c = cookieList[i].trim();
      if (c.indexOf('csrftoken=') === 0) return c.substring('csrftoken='.length);
    }
    return '';
  }

  function saveConsent(preferences) {
    try {
      localStorage.setItem('cookie_preferences', JSON.stringify(preferences));
    } catch (e) { /* tryb prywatny albo zablokowane dane witryny */ }

    // Rejestr po stronie serwera jest ścieżką audytową, więc jego awaria
    // nie może przeszkodzić w zapisaniu wyboru w przeglądarce.
    try {
      fetch('/api/log-cookie-consent/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
        body: JSON.stringify({ analytics: preferences.analytics || false })
      }).catch(function () { });
    } catch (e) { /* bez fetch nic nie zapiszemy, wybór i tak działa */ }
  }

  function clearAnalyticsCookies() {
    document.cookie.split(';').forEach(function (entry) {
      var cookieName = entry.split('=')[0].trim();
      if (cookieName.indexOf('_ga') === 0 || cookieName.indexOf('_gid') === 0) {
        document.cookie = cookieName + '=; Max-Age=0; path=/';
        document.cookie = cookieName + '=; Max-Age=0; path=/; domain=.' + location.hostname;
      }
    });
  }

  function setupCookieConsent() {
    var banner = document.getElementById('cookie-banner');
    var dialog = document.getElementById('cookie-preferences');
    var toggle = document.getElementById('analytics-cookies');
    if (!banner || !dialog || !toggle) return;

    var consentOnLoad = storedConsent();

    if (!consentOnLoad) {
      banner.style.display = 'block';
    } else if (consentOnLoad.analytics) {
      loadAnalytics();
    }

    function openDialog(event) {
      if (event) event.preventDefault();
      var stored = storedConsent();
      toggle.checked = !!(stored && stored.analytics);
      dialog.style.display = 'block';
    }

    function closeDialog() {
      dialog.style.display = 'none';
    }

    document.getElementById('accept-cookies').addEventListener('click', function () {
      saveConsent({ necessary: true, analytics: true });
      banner.style.display = 'none';
      loadAnalytics();
    });

    document.getElementById('decline-cookies').addEventListener('click', function () {
      saveConsent({ necessary: true, analytics: false });
      banner.style.display = 'none';
    });

    document.getElementById('cookie-settings').addEventListener('click', openDialog);
    document.getElementById('close-preferences').addEventListener('click', closeDialog);

    // Stałe wejście do ustawień z każdej podstrony. Bez niego zgody nie dało się
    // wycofać po zamknięciu bannera, a art. 7 ust. 3 RODO wymaga, żeby wycofanie
    // było tak samo łatwe jak udzielenie.
    document.querySelectorAll('[data-action="cookie-settings"]').forEach(function (el) {
      el.addEventListener('click', openDialog);
    });

    document.getElementById('save-preferences').addEventListener('click', function () {
      var enabled = toggle.checked;
      var wasEnabled = !!(consentOnLoad && consentOnLoad.analytics);

      saveConsent({ necessary: true, analytics: enabled });
      banner.style.display = 'none';
      closeDialog();

      if (enabled) {
        loadAnalytics();
      } else if (wasEnabled) {
        // Skrypt GA jest już w pamięci strony, więc samo cofnięcie zgody by go
        // nie zatrzymało. Kasujemy ciasteczka i przeładowujemy stronę.
        clearAnalyticsCookies();
        location.reload();
      }
    });

    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) closeDialog();
    });
  }

  // ── Menu na telefonie ────────────────────────────────────────────

  function setupMobileMenu() {
    var button = document.querySelector('.mobile-menu-toggle');
    var menu = document.querySelector('.navbar-menu');
    var overlay = document.querySelector('.mobile-menu-overlay');
    if (!button || !menu || !overlay) return;

    function close() {
      menu.classList.remove('active');
      overlay.classList.remove('active');
    }

    button.addEventListener('click', function () {
      menu.classList.toggle('active');
      overlay.classList.toggle('active');
    });
    overlay.addEventListener('click', close);
    menu.querySelectorAll('.nav-link').forEach(function (link) {
      link.addEventListener('click', close);
    });
  }

  // ── Formularz rezerwacji ─────────────────────────────────────────

  function setupBookingForm() {
    var showButton = document.getElementById('show-form-btn');
    var hideButton = document.getElementById('hide-form-btn');
    var wrapper = document.getElementById('booking-form-wrapper');
    if (!wrapper) return;

    if (showButton) {
      showButton.addEventListener('click', function () {
        wrapper.style.display = 'block';
        wrapper.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    }
    if (hideButton) {
      hideButton.addEventListener('click', function () {
        wrapper.style.display = 'none';
      });
    }
  }

  // ── Rozwijane pytania ────────────────────────────────────────────

  function setupFaq() {
    // Jeden delegowany listener na listę zamiast atrybutu przy każdym pytaniu.
    document.querySelectorAll('.faq-list').forEach(function (list) {
      list.addEventListener('click', function (event) {
        var button = event.target.closest('.faq-question');
        if (!button) return;
        var isOpen = button.parentElement.classList.toggle('active');
        button.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    });
  }

  // ── Kopiowanie odnośnika do artykułu ─────────────────────────────

  function setupCopyLink() {
    document.querySelectorAll('[data-copy]').forEach(function (button) {
      button.addEventListener('click', function () {
        var url = button.getAttribute('data-copy');
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(url).then(function () {
          var original = button.getAttribute('aria-label') || button.textContent;
          button.setAttribute('aria-label', 'Skopiowano odnośnik');
          button.classList.add('copied');
          setTimeout(function () {
            button.setAttribute('aria-label', original);
            button.classList.remove('copied');
          }, 2000);
        });
      });
    });
  }

  // ── Płynne przewijanie do kotwic ─────────────────────────────────

  function setupSmoothScroll() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(function (link) {
      link.addEventListener('click', function (event) {
        var target = document.getElementById(link.getAttribute('href').slice(1));
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  function start() {
    setupCookieConsent();
    setupMobileMenu();
    setupBookingForm();
    setupFaq();
    setupCopyLink();
    setupSmoothScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
