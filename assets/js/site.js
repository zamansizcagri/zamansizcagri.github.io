/* Zamansız Çağrı — küçük etkileşimler: tıklayınca yüklenen YouTube oynatıcısı,
   tek açık klip satırı, adres çubuğundan doğrudan klip açma. */
(function () {
  'use strict';
  var doc = document;

  /* Üst bandın alt çizgisi: sayfa kayınca görünür */
  var ust = doc.querySelector('.ust');
  function kaydir() {
    if (ust) ust.classList.toggle('kaydi', window.scrollY > 8);
  }
  kaydir();
  window.addEventListener('scroll', kaydir, { passive: true });

  /* Kapak görseli: YouTube büyük kapağı yoksa (120 px yer tutucu döner) orta boya geç */
  function kapakYedek(img) {
    if (img.dataset.yedek) return;
    var kutu = img.closest('.oynatici');
    if (!kutu) return;
    img.dataset.yedek = '1';
    img.removeAttribute('srcset');
    img.src = 'https://i.ytimg.com/vi/' + kutu.dataset.yt + '/hqdefault.jpg';
  }
  [].forEach.call(doc.querySelectorAll('.oynatici__kapak img'), function (img) {
    function kontrol() {
      if (img.naturalWidth && img.naturalWidth < 200) kapakYedek(img);
    }
    if (img.complete) kontrol();
    else img.addEventListener('load', kontrol);
    img.addEventListener('error', function () { kapakYedek(img); });
  });

  /* Oynatıcı: kapak tıklanınca youtube-nocookie gömmesi yüklenir */
  function durdur(kutu) {
    if (kutu && kutu.dataset.kapak && kutu.querySelector('iframe')) {
      kutu.innerHTML = kutu.dataset.kapak;
    }
  }
  function oynat(kutu) {
    if (!kutu || kutu.querySelector('iframe')) return;
    [].forEach.call(doc.querySelectorAll('.oynatici'), function (diger) {
      if (diger !== kutu) durdur(diger);
    });
    var f = doc.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(kutu.dataset.yt) +
      '?autoplay=1&rel=0&playsinline=1';
    f.title = (kutu.dataset.baslik || 'Zamansız Çağrı') + ' (YouTube videosu)';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen';
    f.setAttribute('allowfullscreen', '');
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    kutu.dataset.kapak = kutu.innerHTML;
    kutu.innerHTML = '';
    kutu.appendChild(f);
    f.focus();
  }
  doc.addEventListener('click', function (e) {
    var kapak = e.target.closest && e.target.closest('.oynatici__kapak');
    if (!kapak) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    e.preventDefault();
    oynat(kapak.closest('.oynatici'));
  });

  /* Klip listesi: aynı anda tek satır açık, adres çubuğu satırı gösterir */
  var parcalar = [].slice.call(doc.querySelectorAll('details.parca'));
  parcalar.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (d.open) {
        parcalar.forEach(function (o) { if (o !== d && o.open) o.open = false; });
        if (window.history && history.replaceState) history.replaceState(null, '', '#' + d.id);
      } else {
        durdur(d.querySelector('.oynatici'));
        if (location.hash === '#' + d.id && window.history && history.replaceState) {
          history.replaceState(null, '', location.pathname + location.search);
        }
      }
    });
  });

  /* zamansizcagri.com/#kardes-ol gibi bir adresle gelinirse o klibi aç */
  function adrestenAc() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var d = doc.getElementById(id);
    if (d && d.tagName === 'DETAILS') {
      d.open = true;
      d.scrollIntoView({ block: 'start' });
    }
  }
  adrestenAc();
  window.addEventListener('hashchange', adrestenAc);
})();
