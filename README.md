# zamansizcagri.com

Zamansız Çağrı'nın web sitesi. GitHub Pages'te `main` dalının kökünden yayınlanır; alan adı `CNAME` dosyasında.

## Yapı

| Yol | Ne |
|---|---|
| `index.html` | Ana sayfa (üretilir, elle düzenlenmez) |
| `_kaynak/sarkilar.json` | Site bilgisi ve klip listesi (en yeni en üstte) |
| `_kaynak/build.py` | `index.html` ve `sitemap.xml` üretici |
| `assets/css/site.css` | Stiller (vizon teması, Cormorant Garamond + Manrope + Amiri) |
| `assets/js/site.js` | Tıklayınca yüklenen YouTube oynatıcısı, klip satırları |
| `assets/fonts/` | Sitede barındırılan yazı tipleri (Fontsource, OFL) |
| `assets/img/` | Paylaşım görseli ve uygulama simgeleri |
| `404.html`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, `favicon.*` | Yardımcı dosyalar |

Klip kapakları YouTube'dan (`i.ytimg.com`) gelir; video, kapağa tıklanınca `youtube-nocookie.com` üzerinden yüklenir.

Ziyaret istatistikleri Google Analytics 4 ile tutulur (Ölçüm Kimliği `G-762Y2RGWQN`). Etiket `build.py`'deki `GA_KIMLIK` ile `index.html`'e, elle de `404.html`'e eklenmiştir.

## Yeni klip eklemek

1. `_kaynak/sarkilar.json` içindeki `sarkilar` listesinin **başına** yeni bir kayıt ekleyin (diğer kayıtlarla aynı alanlar: `slug`, `ad`, `alt`, `kanca`, `renk`, `capa`, `meal`, `aciklama`, `ses`, `youtube`, `short`, `sure`, `sure_sn`, `yayin`, `yayin_tr`, `dinle`, `notlar`).
2. `python3 _kaynak/build.py` çalıştırın. İlk kayıt ana sayfada "en yeni klip" olur.
3. Değişen dosyaları (`index.html`, `sitemap.xml`, `_kaynak/sarkilar.json`) GitHub'a yükleyin.

Arapça âyet parçaları (`capa.metin`) elle yazılmaz: kanalın yayımladığı metinden kod noktası olarak alınır. `capa.kontrol` alanındaki uzunluk, kod noktası toplamı ve FNV-1a değeri tutmazsa `build.py` durur.

## Alan adı (Spaceship DNS)

| Tür | Ad | Değer |
|---|---|---|
| A | @ | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 |
| CNAME | www | zamansizcagri.github.io |
| TXT | _github-pages-challenge-zamansizcagri | GitHub alan adı doğrulama kodu |
