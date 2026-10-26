#!/usr/bin/env python3
"""Zamansız Çağrı — site üretici.

Kullanım:  python3 _kaynak/build.py
Okur:      _kaynak/sarkilar.json  (site bilgisi + klipler, en yeni en üstte)
Yazar:     index.html, sitemap.xml  (repo kökünde)

Yeni klip eklemek için sarkilar.json'daki "sarkilar" listesinin BAŞINA bir kayıt ekleyip
bu betiği çalıştırın. İlk kayıt ana sayfadaki "en yeni klip" olur.

Arapça âyet metinleri elle yazılmaz: kanalın yayımladığı metinden alınır ve her kaydın
"kontrol" alanındaki uzunluk / kod noktası toplamı / FNV-1a değeriyle doğrulanır.
Değer tutmazsa betik durur.
"""
import html
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
VERI = json.loads((KOK / "_kaynak" / "sarkilar.json").read_text(encoding="utf-8"))
SITE = VERI["site"]
SARKILAR = VERI["sarkilar"]


def e(metin):
    return html.escape(metin or "", quote=True)


def fnv1a(kodlar):
    h = 2166136261
    for c in kodlar:
        h ^= c
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def arapca_dogrula():
    for s in SARKILAR:
        capa = s["capa"]
        if capa["dil"] != "ar":
            continue
        k = [ord(ch) for ch in capa["metin"]]
        beklenen = capa["kontrol"]
        bulunan = {"uzunluk": len(k), "toplam": sum(k), "fnv1a": fnv1a(k)}
        if bulunan != beklenen:
            sys.exit(f"HATA: {s['slug']} Arapça metni kontrol değerini tutmuyor: {bulunan} != {beklenen}")


def sure_iso(sn):
    return f"PT{sn // 60}M{sn % 60}S"


AMBLEM = """<svg class="amblem" viewBox="0 0 200 200" aria-hidden="true" focusable="false">
  <circle class="halka" cx="100" cy="100" r="95" stroke-width="10"/>
  <path class="dalga dalga--1" d="M 70.6 100 A 34 34 0 0 1 129.4 100" stroke-width="12"/>
  <path class="dalga dalga--2" d="M 51.5 89 A 56 56 0 0 1 148.5 89" stroke-width="12"/>
  <path class="dalga dalga--3" d="M 32.5 78 A 78 78 0 0 1 167.5 78" stroke-width="12"/>
  <circle class="nokta" cx="100" cy="117" r="11"/>
  <path class="kitap" d="M 58 131 C 72 135 88 140 100 145 C 112 140 128 135 142 131 L 142 151 C 128 157 112 161 100 161 C 88 161 72 157 58 151 Z" stroke-width="5"/>
  <path class="sirt" d="M 100 146.5 L 100 157.5" stroke-width="4"/>
</svg>"""

OK_DIS = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 17 17 7M8 7h9v9"/></svg>'
          '<span class="gizli"> (yeni sekmede açılır)</span>')

OYNAT_IKON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 4.5v15l12.5-7.5z"/></svg>'


def oynatici(s, yukle="lazy", oncelik=False):
    yt = s["youtube"]
    baslik = s["ad"] + (f" ({s['alt']})" if s.get("alt") else "")
    fp = ' fetchpriority="high"' if oncelik else ""
    return f"""<div class="oynatici" data-yt="{e(yt)}" data-baslik="{e(baslik)}">
  <a class="oynatici__kapak" href="https://www.youtube.com/watch?v={e(yt)}">
    <img src="https://i.ytimg.com/vi/{e(yt)}/maxresdefault.jpg"
         srcset="https://i.ytimg.com/vi/{e(yt)}/mqdefault.jpg 320w, https://i.ytimg.com/vi/{e(yt)}/maxresdefault.jpg 1280w"
         sizes="(max-width: 960px) 100vw, 680px"
         width="1280" height="720" alt="" loading="{yukle}" decoding="async"{fp}>
    <span class="oynatici__dugme">{OYNAT_IKON}</span>
    <span class="gizli">{e(baslik)} klibini oynat</span>
  </a>
</div>"""


def parca(s):
    alt = f' <span class="parca__alt">{e(s["alt"])}</span>' if s.get("alt") else ""
    capa = s["capa"]
    if capa["dil"] == "ar":
        capa_html = f'<span class="parca__capa" lang="ar" dir="rtl">{e(capa["metin"])}</span>'
    else:
        capa_html = f'<span class="parca__capa" lang="tr">“{e(capa["metin"])}”</span>'
    meal = ""
    if s.get("meal"):
        meal = f"""<blockquote class="meal">
        <p>“{e(s["meal"]["metin"])}”</p>
        <footer>{e(s["meal"]["kaynak"])}</footer>
      </blockquote>"""
    ses = f' {e(s["ses"])}' if s.get("ses") else ""
    baglantilar = [
        f'<li><a href="https://www.youtube.com/watch?v={e(s["youtube"])}" target="_blank" rel="noopener">YouTube’da izle{OK_DIS}</a></li>'
    ]
    if s.get("short"):
        baglantilar.append(
            f'<li><a href="https://www.youtube.com/shorts/{e(s["short"])}" target="_blank" rel="noopener">Kısa kesit{OK_DIS}</a></li>')
    for d in s.get("dinle", []):
        baglantilar.append(
            f'<li><a href="{e(d["url"])}" target="_blank" rel="noopener">{e(d["etiket"])}{OK_DIS}</a></li>')
    notlar = "".join(f"<p>{e(n)}</p>" for n in s.get("notlar", []))
    notlar += f'<p>Yayın: <time datetime="{e(s["yayin"][:10])}">{e(s["yayin_tr"])}</time></p>'
    return f"""<li>
  <details class="parca" id="{e(s["slug"])}" name="klip" style="--renk: {e(s["renk"])}">
    <summary class="parca__ozet">
      <h3 class="parca__ad">{e(s["ad"])}{alt}</h3>
      <span class="parca__kanca">“{e(s["kanca"])}”</span>
      <span class="parca__cizgi" aria-hidden="true"></span>
      {capa_html}
      <span class="parca__kaynak">{e(capa["kaynak"])}</span>
      <span class="parca__sure"><span class="gizli">Süre </span>{e(s["sure"])}</span>
      <span class="parca__ac" aria-hidden="true"></span>
    </summary>
    <div class="parca__ayrinti">
      {oynatici(s)}
      <div class="parca__metin">
        <p class="parca__aciklama">{e(s["aciklama"])}{ses}</p>
        {meal}
        <ul class="baglantilar">
          {"".join(baglantilar)}
        </ul>
        <div class="parca__notlar">{notlar}</div>
      </div>
    </div>
  </details>
</li>"""


def json_ld():
    alan = SITE["alan_adi"]
    graf = [
        {
            "@type": "MusicGroup",
            "@id": f"{alan}/#sanatci",
            "name": SITE["ad"],
            "url": f"{alan}/",
            "description": SITE["slogan"],
            "genre": ["Hip Hop/Rap", "World"],
            "image": f"{alan}/assets/img/og-zamansiz-cagri.jpg?v=2",
            "logo": f"{alan}/assets/img/icon-512.png?v=2",
            "sameAs": [p["url"] for p in SITE["platformlar"]],
        },
        {
            "@type": "WebSite",
            "@id": f"{alan}/#site",
            "url": f"{alan}/",
            "name": SITE["ad"],
            "inLanguage": "tr",
            "publisher": {"@id": f"{alan}/#sanatci"},
        },
    ]
    for s in SARKILAR:
        ad = s["ad"] + (f" ({s['alt']})" if s.get("alt") else "")
        graf.append({
            "@type": "VideoObject",
            "name": f"{ad} – {SITE['ad']} | Sözlü Klip",
            "description": s["aciklama"],
            "thumbnailUrl": [f"https://i.ytimg.com/vi/{s['youtube']}/maxresdefault.jpg"],
            "uploadDate": s["yayin"],
            "duration": sure_iso(s["sure_sn"]),
            "embedUrl": f"https://www.youtube.com/embed/{s['youtube']}",
            "url": f"https://www.youtube.com/watch?v={s['youtube']}",
            "inLanguage": "tr",
            "creator": {"@id": f"{alan}/#sanatci"},
        })
    metin = json.dumps({"@context": "https://schema.org", "@graph": graf}, ensure_ascii=False, indent=1)
    return metin.replace("</", "<\\/")


def sayfa():
    alan = SITE["alan_adi"]
    yeni = SARKILAR[0]
    yeni_ad = yeni["ad"] + (f" ({yeni['alt']})" if yeni.get("alt") else "")
    platformlar = "".join(f"""
      <li><a href="{e(p["url"])}" target="_blank" rel="noopener">
        <span class="platform__ad">{e(p["ad"])}</span>
        <span class="platform__ne">{e(p["ne"])}</span>
        <span class="platform__hesap">{e(p["hesap"])}</span>
        <svg class="platform__ok" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 17 17 7M8 7h9v9"/></svg>
        <span class="gizli"> (yeni sekmede açılır)</span>
      </a></li>""" for p in SITE["platformlar"])
    alt_baglantilar = "".join(
        f'<li><a href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["ad"])}</a></li>' for p in SITE["platformlar"])
    parcalar = "\n".join(parca(s) for s in SARKILAR)

    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(SITE["ad"])} – {e(SITE["slogan"].rstrip("."))}</title>
<meta name="description" content="{e(SITE["aciklama"])}">
<link rel="canonical" href="{alan}/">
<meta name="theme-color" content="#2A231C">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:site_name" content="{e(SITE["ad"])}">
<meta property="og:title" content="{e(SITE["ad"])}">
<meta property="og:description" content="{e(SITE["slogan"])}">
<meta property="og:url" content="{alan}/">
<meta property="og:image" content="{alan}/assets/img/og-zamansiz-cagri.jpg?v=2">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Zamansız Çağrı amblemi ve sloganı">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico?v=2" sizes="32x32">
<link rel="icon" href="/favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/site.webmanifest?v=2">
<link rel="preload" href="/assets/fonts/cormorant-garamond-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://i.ytimg.com">
<link rel="stylesheet" href="/assets/css/site.css">
<script type="application/ld+json">
{json_ld()}
</script>
</head>
<body>
<a class="atla" href="#icerik">İçeriğe geç</a>

<header class="ust">
  <div class="kap ust__ic">
    <a class="marka" href="/" aria-label="Zamansız Çağrı, ana sayfa">
      {AMBLEM}
      <span class="marka__ad" aria-hidden="true">Zamansız Çağrı</span>
    </a>
    <nav aria-label="Sayfa bölümleri">
      <a href="#klipler">Klipler</a>
      <a href="#dinle">Dinle</a>
      <a href="#hakkinda">Hakkında</a>
    </nav>
    <a class="dugme dugme--kucuk" href="{e(SITE["abone_url"])}" target="_blank" rel="noopener">Abone ol<span class="gizli"> (YouTube, yeni sekmede açılır)</span></a>
  </div>
</header>

<main id="icerik">
  <section class="giris" aria-labelledby="giris-baslik">
    <svg class="giris__halkalar" viewBox="0 0 200 200" aria-hidden="true" focusable="false">
      <circle cx="100" cy="100" r="28" vector-effect="non-scaling-stroke"/>
      <circle cx="100" cy="100" r="50" vector-effect="non-scaling-stroke"/>
      <circle cx="100" cy="100" r="72" vector-effect="non-scaling-stroke"/>
      <circle cx="100" cy="100" r="94" vector-effect="non-scaling-stroke"/>
    </svg>
    <div class="kap giris__ic">
      <div class="giris__metin">
        <h1 id="giris-baslik">{e(SITE["slogan"])}</h1>
        <p class="giris__alt">Her şarkı bir âyete yaslanır; hadisle, Risale-i Nur’la ve Türk edebiyatının mısralarıyla örülür, bugünün bir derdine dokunur.</p>
        <div class="giris__dugmeler">
          <a class="dugme" href="{e(SITE["abone_url"])}" target="_blank" rel="noopener">YouTube’da abone ol<span class="gizli"> (yeni sekmede açılır)</span></a>
          <a class="dugme dugme--cizgi" href="#dinle">Platformlarda dinle</a>
        </div>
      </div>
      <figure class="giris__klip" style="--renk: {e(yeni["renk"])}">
        {oynatici(yeni, yukle="eager", oncelik=True)}
        <figcaption>
          <span><span class="giris__klip-yazi">En yeni klip: </span><a class="giris__klip-ad" href="#{e(yeni["slug"])}">{e(yeni_ad)}</a></span>
          <span class="giris__klip-kaynak">{e(yeni["capa"]["kaynak"])}, <time datetime="{e(yeni["yayin"][:10])}">{e(yeni["yayin_tr"])}</time></span>
        </figcaption>
      </figure>
    </div>
  </section>

  <section class="bolum" id="klipler" aria-labelledby="klipler-baslik">
    <div class="kap">
      <div class="bolum__bas">
        <h2 id="klipler-baslik">Klipler</h2>
        <p>Her şarkının dayandığı âyet ya da söz hemen yanında. Bir şarkıyı açın: klip, mealiyle âyet ve dinleme bağlantıları orada.</p>
      </div>
      <ul class="fihrist">
{parcalar}
      </ul>
    </div>
  </section>

  <section class="bolum" id="dinle" aria-labelledby="dinle-baslik">
    <div class="kap">
      <div class="bolum__bas">
        <h2 id="dinle-baslik">Dinle ve takip et</h2>
        <p>Sözlü klipler YouTube’da; şarkıların ses sürümleri dinleme platformlarında.</p>
      </div>
      <ul class="platformlar">{platformlar}
      </ul>
    </div>
  </section>

  <section class="bolum" id="hakkinda" aria-labelledby="hakkinda-baslik">
    <div class="kap hakkinda">
      <div class="hakkinda__metin">
        <h2 id="hakkinda-baslik">Hakkında</h2>
        <p class="hakkinda__giris">Zamansız Çağrı, Kur’an’ın ve imanın hakikatlerini akılda kalan şarkılara dönüştüren bir müzik kanalı. Adını Dosdoğru’nun kapanışındaki “Çağrı zamansız” dizesinden alır.</p>
        <p>Şarkılar bireyin iç dünyasından toplumun derdine uzanır: istikamet, ümit ve tevbe, kalp kırmamak, kardeşlik, anne-baba hakkı, paylaşmak, şükür ve iktisat, tevekkül ve helal kazanç, beş vakit namaz, yuvada sevgi ve merhamet, Peygamberimizin güzel örnekliği, dua ve O’nun yakınlığı, sabır ve beklerken büyümek. Her klibin kendi sesi ve kendi görsel dünyası vardır; yukarıdaki renkler de kliplerin renkleridir.</p>
        <p class="hakkinda__beyan">Şarkılar yapay zekâ destekli müzik araçlarıyla üretilir. Her klibin sözleri ve dayandığı âyet, YouTube açıklamasında yer alır.</p>
      </div>
      <div class="hakkinda__yol">
        <h3>Bir şarkı nasıl doğar</h3>
        <ol class="adimlar">
          <li><strong>Âyet</strong>Şarkı tek bir âyete yaslanır; nakaratın kancası çoğu zaman o âyetin kendisidir.</li>
          <li><strong>Kaynaklar</strong>Konuyla ilgili hadisler, Risale-i Nur’dan vecizeler ve Türk edebiyatından mısralar toplanır, kaynağından doğrulanır.</li>
          <li><strong>Söz</strong>Kaynaklar bugünün bir derdiyle buluşturulur ve sözler yazılır.</li>
          <li><strong>Şarkı ve klip</strong>Her şarkıya kendi sesi, kendi renkleri ve bir sözlü klip verilir; ardından kısa kesitler gelir.</li>
        </ol>
      </div>
    </div>
  </section>
</main>

<footer class="alt">
  <div class="kap alt__ic">
    <div>
      <a class="marka" href="/" aria-label="Zamansız Çağrı, ana sayfa">
        {AMBLEM}
        <span class="marka__ad" aria-hidden="true">Zamansız Çağrı</span>
      </a>
      <p class="alt__slogan">{e(SITE["slogan"])}</p>
    </div>
    <ul class="alt__baglantilar">{alt_baglantilar}</ul>
    <p class="alt__telif">© 2026 Zamansız Çağrı</p>
  </div>
</footer>

<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def sitemap():
    son = max(s["yayin"][:10] for s in SARKILAR)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE["alan_adi"]}/</loc>
    <lastmod>{son}</lastmod>
  </url>
</urlset>
"""


if __name__ == "__main__":
    arapca_dogrula()
    (KOK / "index.html").write_text(sayfa(), encoding="utf-8")
    (KOK / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    print(f"index.html ve sitemap.xml yazıldı ({len(SARKILAR)} klip).")
