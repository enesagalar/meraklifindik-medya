"""Pilot hafta (8–16 Ekim 2026) yayın takvimi → Buffer gönderileri.
python otomasyon/pilot_plan.py show            # takvimi yazdır
python otomasyon/pilot_plan.py drafts          # hepsini Buffer'a TASLAK yükle (state: yayin/plan-state.json)
python otomasyon/pilot_plan.py schedule [N]    # onaylı taslakları sırayla zamanla (kanal başı 10 sınırına kadar)
Medya: https://enesagalar.github.io/meraklifindik-medya/ (repo: enesagalar/meraklifindik-medya)
"""
import json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

BASE = "https://enesagalar.github.io/meraklifindik-medya"
IG, TT, YT = "6ac6afed6a5c39ccb6460e6d", "6ac6b0566a5c39ccb6461106", "6ac6b0b16a5c39ccb6461382"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plan-state.json")
TZ = "+03:00"

# ---------- video açıklamaları (IG/TikTok aynı) ----------
CAP = {
"000": """Merhaba, ben Fındık! 🐿️ Her "Neden?" sorusunun peşine düşerim.
40 saniyelik, kâğıttan, kaynağı belli bilim. Her cevap Merak Defteri'ne yeni bir sayfa 📓
Sorunuzu yorumlara yazın; belki bir sonraki video onun olur 👇
#merakliFindik #bilim #neden #merak #eğitim""",
"001": """Çoğumuz denizi yansıttığı için sanırız… ama asıl sebep güneşin ışığında saklı! ☀️
Güneş ışığının içinde bütün renkler var; hava mavi ışığı her yöne saçıyor. Başını nereye kaldırırsan kaldır, o saçılan maviyi görüyorsun. 💙

Merak Defteri · sayfa 1/8 ✓ · Sıradaki: Gün batımı neden turuncu? Tahmininizi yorumlara yazın 👇
Bunu merak eden birine gönderin 🐿️

Kaynak: NASA Space Place
#merakliFindik #bilim #neden #gökyüzü #merak""",
"002": """Geçen sefer maviyi konuştuk, şimdi sıra turuncuda! 🌅
Öğlen güneş tepemizde, ışığı havada kısa bir yol gider. Akşam güneş alçalınca ışık havada çok daha uzun yol yürür. Bu yolda mavi ışık saçılıp kalır; bize kırmızı ve turuncu ulaşır. 🧡

Merak Defteri · sayfa 2/8 ✓ · Sıradaki: Bulutlar neden beyaz? Tahmininizi yorumlara yazın 👇
Bunu merak eden birine gönderin 🐿️

Kaynak: NASA Space Place · Met Office
#merakliFindik #bilim #neden #günbatımı #merak""",
"003": """Hava sadece maviyi saçıyordu… peki bulutlar? ☁️
Bulutlar milyonlarca minik su damlacığından oluşur. Bu damlacıklar havanın parçacıklarından çok daha büyüktür ve bütün renkleri birden saçar. Bütün renkler karışınca: beyaz! 🤍

Merak Defteri · sayfa 3/8 ✓ · Sıradaki: Bu kadar su neden üstümüze düşmüyor? Tahmininizi yorumlara yazın 👇
Bunu merak eden birine gönderin 🐿️

Kaynak: NOAA SciJinks
#merakliFindik #bilim #neden #bulutlar #merak""",
"004": """Bulutlarda o kadar su var… peki neden üstümüze düşmüyor? ☁️
Bulut damlacıkları inanılmaz küçük: bir yağmur damlasına yaklaşık bir milyon tanesi sığar! Bu kadar minik olunca çok yavaş düşerler; yerden yükselen sıcak hava da onları havada tutar.

Merak Defteri · sayfa 4/8 ✓ · Sıradaki: Yağmur nasıl oluşur? Tahmininizi yorumlara yazın 👇

Kaynak: NOAA SciJinks
#merakliFindik #bilim #neden #bulutlar #merak""",
"005": """Bulutlar havada kalıyorsa yağmur nereden geliyor? 🌧️
Güneş suyu ısıtır, su buhar olup yükselir, yukarıda soğuyup damlacığa dönüşür. Damlacıklar çarpışıp birleşir, ağırlaşınca da… yağmur!

Merak Defteri · sayfa 5/8 ✓ · Sıradaki: Şimşek neden çakar? Tahmininizi yorumlara yazın 👇

Kaynak: USGS Water Science School
#merakliFindik #bilim #neden #yağmur #merak""",
"006": """Fırtınada gökyüzü bir anda parlıyor… ⚡
Fırtına bulutunda buz parçaları ve damlalar çarpışıp elektrik biriktirir. Elektrik çok fazla olunca dev bir kıvılcım olup atlar: şimşek!

Merak Defteri · sayfa 6/8 ✓ · Sıradaki: Gök gürültüsü neden sonra gelir? Tahmininizi yorumlara yazın 👇

Kaynak: NOAA National Severe Storms Laboratory
#merakliFindik #bilim #neden #şimşek #merak""",
"007": """Önce şimşek, sonra gümm! 🔊
Şimşek havayı Güneş'in yüzeyinden bile sıcak yapar; hava hızla genişler = gök gürültüsü. Işık anında gelir, ses ise 1 km'yi ~3 saniyede gider. Saydığınız saniyeyi 3'e bölün: fırtına o kadar km uzakta!

Merak Defteri · sayfa 7/8 ✓ · Sıradaki: Gökkuşağı! 🌈 Tahmininizi yorumlara yazın 👇

Kaynak: NOAA NSSL · NWS
#merakliFindik #bilim #neden #fırtına #merak""",
"008": """Sezon finali! 🌈 Güneş ışığının içindeki bütün renkleri hatırlıyor musunuz?
Işık yağmur damlasına girerken bükülür, renkler ayrılır, damlanın içinde seker ve çıkar. Milyonlarca damla gökyüzüne kocaman bir yay çizer. Gökkuşağını görmek için güneş arkanızda, yağmur önünüzde olmalı!

Merak Defteri 8/8 tamam ✓ · Sezon 2: Vücudumuz geliyor — ilk soru: Neden esneriz? 👇

Kaynak: NOAA SciJinks · Met Office
#merakliFindik #bilim #gökkuşağı #neden #merak""",
}
CAP["009"] = """Yağmur damlası gözyaşı şeklinde değil! 💧 Minik damlalar yuvarlaktır; büyüdükçe alttan çarpan hava onları yassıltır ve damla bir hamburger ekmeğine benzer. Çok büyürse paraşüt gibi açılıp parçalanır. 🍔
Merak Defteri · ek sayfa 1/5 ✓ · Sıradaki: Dolu neden yazın yağar? Tahmininizi yorumlara yazın 👇 Bunu merak eden birine gönderin 🐿️
Kaynak: USGS Water Science School
#merakliFindik #bilim #neden #yağmur #merak"""
CAP["013"] = """Uçağın arkasındaki beyaz çizgi duman değil… buz! ✈️ Yükseklerde hava eksi kırk dereceden bile soğuk; motordan çıkan su buharı anında donar ve milyonlarca minik buz kristali gökyüzüne bir yol çizer.
Merak Defteri · ek sayfa 5/5 ✓ · Sırada yepyeni bir sezon var: Vücudumuz! Bunu merak eden birine gönderin 🐿️
Kaynak: NASA · NOAA JetStream
#merakliFindik #bilim #neden #gökyüzü #merak"""
CAP["010"] = """En büyük dolu taneleri kışın değil, yazın düşer! 🧊 Dolu, yaz fırtınalarının dev bulutlarında aşağı yukarı gidip her turda yeni bir buz katmanı ekler; tıpkı soğanın katmanları gibi. Bulunan en büyüğü neredeyse bir voleybol topu kadardı!
Merak Defteri · ek sayfa 2/5 ✓ · Sıradaki: Sahilde rüzgâr neden yön değiştirir? Tahmininizi yorumlara yazın 👇 Bunu merak eden birine gönderin 🐿️
Kaynak: NOAA National Severe Storms Laboratory
#merakliFindik #bilim #neden #dolu #merak"""
CAP["011"] = """Sahilde gündüz rüzgâr denizden eser, gece karadan! 🌊 Güneş karayı denizden daha hızlı ısıtır; karada yükselen sıcak havanın yerine denizin serin havası koşar. Gece kara daha çabuk soğur ve rüzgâr ters döner.
Merak Defteri · ek sayfa 3/5 ✓ · Sıradaki: Yağmurun kokusu nereden gelir? Tahmininizi yorumlara yazın 👇 Bunu merak eden birine gönderin 🐿️
Kaynak: Met Office · NOAA JetStream
#merakliFindik #bilim #neden #rüzgar #merak"""
CAP["012"] = """Yağmurun kokusu aslında yağmurdan gelmiyor! 🌧️ O koku topraktan gelir: topraktaki minicik canlıların ürettiği bir koku. Bilim insanları, damlaların çıkardığı minik kabarcıkların bu kokuyu havaya taşıdığını düşünüyor. Adı da var: petrikor!
Merak Defteri · ek sayfa 4/5 ✓ · Sıradaki: Uçak izi duman mı? Tahmininizi yorumlara yazın 👇 Bunu merak eden birine gönderin 🐿️
Kaynak: MIT News (2015) · Smithsonian Magazine
#merakliFindik #bilim #neden #yağmur #merak"""
TITLE = {"012": 'Yağmurun kokusu nereden gelir?', "011": 'Sahilde rüzgâr neden yön değiştirir?', "010": 'Dolu neden yazın yağar?', "013": 'Uçak izi duman mı?', "009": 'Yağmur damlası gözyaşı şeklinde mi?', "000": "Merhaba, ben Fındık! 🐿️", "001": "Gökyüzü neden mavi?", "002": "Gün batımı neden turuncu?", "003": "Bulutlar neden beyaz?",
         "004": "Bulutlar neden düşmüyor?", "005": "Yağmur nasıl oluşur?", "006": "Şimşek neden çakar?", "007": "Gök gürültüsü neden sonra gelir?",
         "008": "Gökkuşağı nasıl oluşur? (Sezon finali)"}
COVER = {"012": 600, "011": 400, "010": 100, "013": 2600, "009": 1200, "000": 2000, "001": 2900, "002": 3900, "003": 4900, "004": 4000, "005": 4000, "006": 4800, "007": 4000, "008": 4400}

# Revize video dosyaları (2026-10-09: açılış kuralı + −14 LUFS; eski v/NNN.mp4 kaldırıldı)
VFILE = {n: n + "-r2" for n in ("003", "004", "005", "006", "007", "008")}
VFILE.update({n: n + "-k" for n in ("010", "011", "012", "013")})  # 2026-10-17 kitleye hitap kaldırılmış sürüm

# ---------- statik gönderiler (IG; TikTok'ta foto gönderisi) ----------
STATIC = {
"carousel-001": (7, "Merak Defteri · Sayfa 1", """Gökyüzü neden mavi? Merak Defteri'nin ilk sayfası 📓
Videoyu izlediniz mi? Kaydırın →  Kaydedin 📌
#merakliFindik #bilim #neden #gökyüzü #merak"""),
"carousel-ebeveyn-rehberi-gokyuzu": (5, "Ebeveyn rehberi", """Çocuğunuz "Gökyüzü neden mavi?" diye sorarsa yaşına göre 1 cümlelik cevaplar 👇
5–7 yaş, 8–10 yaş ve 11+ için ayrı ayrı. Kaydedin, eşinize gönderin ✈️
#merakliFindik #bilim #merak #neden"""),
"carousel-merak-defteri-003": (6, "Merak Defteri · Sayfa 3", """Bulutlar neden beyaz? Merak Defteri'nin 3. sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: NOAA SciJinks
#merakliFindik #bilim #neden #bulutlar #merak"""),
"carousel-merak-defteri-004": (6, "Merak Defteri · Sayfa 4", """Bulutlar neden düşmüyor? Merak Defteri'nin 4. sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: NOAA SciJinks · UCAR
#merakliFindik #bilim #neden #bulutlar #merak"""),
"carousel-merak-defteri-006": (6, "Merak Defteri · Sayfa 6", """Şimşek neden çakar? Merak Defteri'nin 6. sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: NOAA National Severe Storms Laboratory
#merakliFindik #bilim #neden #şimşek #merak"""),
"carousel-merak-defteri-008": (7, "Merak Defteri · Sayfa 8", """Gökkuşağı nasıl oluşur? Merak Defteri'nin son sayfası 📓 Defter doldu: 8 soru, 8 cevap!
Hangi sayfa en sevdiğiniz oldu? Yorumlara yazın 👇 Kaydedin 📌
Kaynak: NOAA SciJinks · Met Office
#merakliFindik #bilim #neden #gökkuşağı #merak"""),
"carousel-merak-defteri-009": (6, "Merak Defteri · ek sayfa 1", """Yağmur damlası gözyaşı şeklinde mi? Merak Defteri'nin ek sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: USGS Water Science School
#merakliFindik #bilim #neden #yağmur #merak"""),
"carousel-merak-defteri-010": (6, "Merak Defteri · ek sayfa 2", """Dolu neden yazın yağar? Merak Defteri'nin ek sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: NOAA National Severe Storms Laboratory
#merakliFindik #bilim #neden #dolu #merak"""),
"carousel-merak-defteri-011": (6, "Merak Defteri · ek sayfa 3", """Sahilde rüzgâr neden yön değiştirir? Merak Defteri'nin ek sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: Met Office · NOAA JetStream
#merakliFindik #bilim #neden #rüzgar #merak"""),
"carousel-merak-defteri-012": (6, "Merak Defteri · ek sayfa 4", """Yağmurun kokusu nereden gelir? Merak Defteri'nin ek sayfası 📓
Videoyu izlediniz mi? Kaydırın, sonra kaydedin 📌
Kaynak: MIT News · Smithsonian Magazine
#merakliFindik #bilim #neden #yağmur #merak"""),
"tek-sence-neden": (0, "Sence neden?", """Bulutlarda tonlarca su var… peki neden üstümüze düşmüyor? ☁️
A mı, B mi? Cevabınızı yorumlara yazın; doğru cevap akşamki videoda 🐿️
#merakliFindik #neden #bulutlar #bilim #merak"""),
"carousel-evde-dene-kavanozda-yagmur": (7, "Merak Defteri · Sayfa 5", """Merak Defteri · sayfa 5: yağmurun nasıl oluştuğunu kavanozda görün 🫙 5 dakikalık mutfak deneyi!
⚠️ Sıcak suyu bir yetişkin döksün, kaynar su kullanmayın. Denediyseniz ne gördüğünüzü yorumlara yazın 👇
#merakliFindik #evdeDeney #bilim #yağmur #merak"""),
"tek-simsek-mi-gurultu-mu": (0, "Fırtınada hangisi önce?", """Fırtınada hangisi önce gelir: şimşek mi, gök gürültüsü mü? ⚡
Tahmininizi yorumlara yazın 👇 Cevap bu hafta Merak Defteri'nde!
#merakliFindik #neden #şimşek #bilim #merak"""),
"carousel-uc-saniye-kurali": (5, "Merak Defteri · Sayfa 7", """Merak Defteri · sayfa 7: fırtına ne kadar uzakta? 3 saniye kuralıyla saniye sayarak bulun ⚡
Unutmayın: fırtınada içeride kalın! Kaydedin 📌
Kaynak: NOAA National Weather Service
#merakliFindik #bilim #fırtına #neden #merak"""),
"tek-gokkusagi-gunes": (0, "Güneş nerede?", """Gökkuşağını görmek için güneş nerede olmalı: önümüzde mi, arkamızda mı? 🌈
Tahmininizi yorumlara yazın; cevap akşamki sezon finalinde!
#merakliFindik #neden #gökkuşağı #bilim #merak"""),
"carousel-sezon1-ozet": (3, "Sezon 1 özeti", """8 soru, 8 cevap — Gökyüzü Sezonu tamam! 🎉
Hangisi en sevdiğiniz oldu? Yorumlara yazın 👇 Sırada Sezon 2: Vücudumuz 🫁
#merakliFindik #bilim #neden #merak #eğitim"""),
}
# Yeniden üretilen statik görsellerin dosya sürümü (Buffer yeni URL'den çeker): 2026-10-17 kitleye hitap kaldırıldı
GSURUM = {f"carousel-merak-defteri-{n}": "b" for n in ("009", "010", "011", "012")}
ALT = "Kâğıt kesik tarzında, defter sayfası üzerinde sincap maskot Fındık ve bir bilim sorusu"

# ---------- takvim ----------
# gün: (tarih, statik@12:30 | None, [videolar (saat, no)], [story (saat, dosya)])
DAYS = [
 ("2026-10-08", None, [("12:30", "000"), ("19:30", "001")], [("13:00", "story-merhaba"), ("16:00", "story-001-a-soru"), ("19:40", "story-001-b-video"), ("21:30", "story-001-c-cevap")]),
 ("2026-10-09", "carousel-001", [("19:30", "002")], [("10:00", "story-002-a-soru"), ("19:40", "story-002-b-video"), ("21:30", "story-002-c-cevap")]),
 ("2026-10-10", "carousel-ebeveyn-rehberi-gokyuzu", [("19:30", "003")], [("10:00", "story-003-a-soru"), ("19:40", "story-003-b-video"), ("21:30", "story-003-c-cevap")]),
 ("2026-10-11", "carousel-merak-defteri-003", [("19:30", "004")], [("10:00", "story-004-a-soru"), ("19:40", "story-004-b-video"), ("21:30", "story-004-c-cevap")]),
 ("2026-10-12", "carousel-merak-defteri-004", [("19:30", "005")], [("10:00", "story-005-a-soru"), ("19:40", "story-005-b-video"), ("21:30", "story-005-c-cevap")]),
 ("2026-10-13", "carousel-evde-dene-kavanozda-yagmur", [("19:30", "006")], [("10:00", "story-006-a-soru"), ("19:40", "story-006-b-video"), ("21:30", "story-006-c-cevap")]),
 ("2026-10-14", "carousel-merak-defteri-006", [("19:30", "007")], [("10:00", "story-007-a-soru"), ("19:40", "story-007-b-video"), ("21:30", "story-007-c-cevap")]),
 ("2026-10-15", "carousel-uc-saniye-kurali", [("19:30", "008")], [("10:00", "story-008-a-soru"), ("19:40", "story-008-b-video"), ("21:30", "story-008-c-cevap")]),
 ("2026-10-16", "carousel-merak-defteri-008", [], [("13:00", "story-sezon2")]),
 ("2026-10-17", None, [("19:30", "009")], []),
 ("2026-10-18", "carousel-merak-defteri-009", [("19:30", "010")], []),
 ("2026-10-21", "carousel-merak-defteri-012", [("19:30", "013")], []),
 ("2026-10-19", "carousel-merak-defteri-010", [("19:30", "011")], []),
 ("2026-10-20", "carousel-merak-defteri-011", [("19:30", "012")], []),
]

# ---------- Kaydırmalı formatlar (2026-10-09 kullanıcı kararı; kaynak studio/karusel/, görseller yayin/kr/<id>-NN.jpg, 4:5) ----------
# dy = Doğru mu Yanlış mı · hm = Hiç merak ettin mi · mt = Merak Testi. Video/12:30 içeriğini TEKRAR ETME.
KARUSEL = [
 ("2026-10-10", "17:00", "dy-hava", 10, "Doğru mu, Yanlış mı? Hava", """Bu 4 bilginin kaçı doğru? 🤔 Her kartta kaydırmadan önce tahminini yorumlara yaz: D mi, Y mi? 👇
Sonuna kadar kaydır, puanını gör! Bunu bilmeyen birine gönder ✈️ Kaydet 📌
Kaynak: NOAA · Met Office · USGS
#merakliFindik #doğrumuyanlışmı #neden #bilim #merak"""),
 ("2026-10-11", "17:00", "hm-vucut", 7, "Hiç merak ettin mi? Vücudumuz", """Kendini neden gıdıklayamazsın? 🤭 Vücudumuzla ilgili 5 tuhaf soru ve cevabı, kaydır 👉
En çok hangisi şaşırttı? Yorumlara yaz; sıradaki "Neden?"i sen seç 👇 Kaydet 📌
Kaynak: NHS · NIH · Scientific American
#merakliFindik #hiçmerakettinmi #vücudumuz #bilim #merak"""),
 ("2026-10-12", "17:00", "mt-hayvanlar", 8, "Merak Testi: Hayvanlar", """Merak Testi: Hayvanlar 🐾 5 soru, cevaplar son kartta!
Kâğıt kalem al, cevaplarını yaz, sonra puanını yorumlara bırak: 5/5 mi? 👇 Arkadaşına gönder, kim kazanacak? ✈️
Kaynak: National Geographic · Smithsonian · WWF
#merakliFindik #meraktesti #hayvanlar #bilim #merak"""),
 ("2026-10-13", "17:00", "dy-hayvanlar", 10, "Doğru mu, Yanlış mı? Hayvanlar", """Japon balığının hafızası gerçekten 3 saniye mi? 🐠 4 bilgi, her kartta önce tahmin et: D mi, Y mi? 👇
Kaç tanesini bildin? Puanını yaz, bilmeyen birine gönder ✈️ Kaydet 📌
Kaynak: National Geographic · Smithsonian
#merakliFindik #doğrumuyanlışmı #hayvanlar #bilim #merak"""),
 ("2026-10-14", "17:00", "hm-uzay", 7, "Hiç merak ettin mi? Uzay", """Güneş'in içine yaklaşık 1,3 milyon Dünya sığar! ☀️ Uzayla ilgili 5 soru ve cevabı, kaydır 👉
Hangisi aklını uçurdu? Yorumlara yaz; sıradaki "Neden?"i sen seç 👇 Kaydet 📌
Kaynak: NASA
#merakliFindik #hiçmerakettinmi #uzay #bilim #merak"""),
 ("2026-10-15", "17:00", "dy-vucut", 10, "Doğru mu, Yanlış mı? Vücudumuz", """Beynimizin sadece %10'unu mu kullanıyoruz? 🧠 4 bilgi, her kartta önce tahmin et: D mi, Y mi? 👇
Kaç tanesini bildin? Puanını yaz, bilmeyen birine gönder ✈️ Kaydet 📌
Kaynak: NIH · Mayo Clinic · Smithsonian
#merakliFindik #doğrumuyanlışmı #vücudumuz #bilim #merak"""),
 ("2026-10-16", "17:00", "mt-dunya", 8, "Merak Testi: Dünyamız", """Merak Testi: Dünyamız 🌍 5 genel kültür sorusu, cevaplar son kartta!
Cevaplarını yaz, puanını yorumlara bırak: 5/5 mi? 👇 Testi arkadaşına gönder ✈️
Kaynak: NASA · NOAA · National Geographic
#merakliFindik #meraktesti #genelkültür #bilim #merak"""),
 ("2026-10-17", "12:30", "hm-bitkiler", 7, 'Sinek kapan bitkisi sayabilir mi? 5 bitki sorusu', """Bir bitki sayı sayabilir mi? 🌱
Sinek kapan, küstüm otu, 2.000 yıllık tohum… Bitkilerle ilgili 5 şaşırtıcı soru. Önce tahmin edin, sonra kaydırın!
Kaynak: Kew Bahçeleri, Britannica, Smithsonian Magazine, National Geographic
#merakliFindik #hiçmerakettinmi #bitkiler #bilim #merak"""),
 ("2026-10-17", "17:00", "mt-okyanus", 8, 'Okyanus testi: en derin nokta kaç metre?', """Okyanusun en derin noktası kaç metre? 🌊
5 soruluk okyanus testi. Cevaplarınızı yazın, sonda puanınızı yorumlara bırakın!
Kaynak: NOAA Ocean Service, NOAA Fisheries, USGS
#merakliFindik #meraktesti #okyanus #bilim #merak"""),
 ("2026-10-18", "17:00", "dy-bitkiler", 10, 'Ayçiçeği güneşi izler mi? Doğru mu yanlış mı?', """Ayçiçeği gerçekten güneşi izler mi? 🌻
4 bitki bilgisi: hangisi doğru, hangisi yanlış? Kaydırmadan önce tahminini yaz, sonra puanını paylaş!
Kaynak: Britannica, Science (2016), UC Davis, ABD Tarım Bakanlığı (USDA)
#merakliFindik #doğrumuyanlışmı #bitkiler #bilim #merak"""),
 ("2026-10-19", "17:00", "hm-dunya", 7, "Dünya'nın merkezi ne kadar sıcak? 5 soru", """Ayağımızın altındaki Dünya ne kadar sıcak? 🌍
Kıtalar, pusula, en derin kuyu ve Dünya'nın yaşı: 5 soru, 5 kısa cevap. En çok hangisi şaşırttı?
Kaynak: NASA, USGS, NOAA, Smithsonian Magazine
#merakliFindik #hiçmerakettinmi #dünya #bilim #merak"""),
 ("2026-10-20", "17:00", "mt-rekorlar", 8, 'Doğanın rekorları: en hızlı hayvan hangisi?', """Dünyanın en hızlı hayvanı çita değil! 🦅
Doğanın 5 rekoru: en hızlı, en uzun, en küçük, en yaşlı, en büyük. Puanınızı yorumlara yazın, testi bir arkadaşınıza gönderin!
Kaynak: ABD Milli Parklar Servisi, Britannica, Kew Bahçeleri, Science (2016)
#merakliFindik #meraktesti #rekorlar #bilim #merak"""),
 ("2026-10-21", "17:00", "dy-dunya", 10, "Kuzey Kutbu'nun altında kara var mı? D mi Y mi?", """Kuzey Kutbu'nda ayağının altında kara var mı? 🧭
4 Dünya bilgisi: biri Sahra Çölü'yle ilgili! Kaydırmadan önce tahminini yaz; kaç tanesini bildiniz?
Kaynak: NOAA, NSIDC, NASA JPL, NASA Earth Observatory
#merakliFindik #doğrumuyanlışmı #dünya #bilim #merak"""),
]

# ---------- TikTok'a özel keşif kaydırmalıları (15:00; 2026-10-13 — TikTok'ta büyüme motoru carousel) ----------
KARUSEL_TT = [
 ("2026-10-14", "15:00", "dy-okyanus", 10, 'Denizyıldızı balık mı? 4 okyanus bilgisi: D mi Y mi?', """Denizyıldızı gerçekten bir balık mı? 🌊
4 okyanus bilgisi: her birinde kaydırmadan önce tahminini yorumlara yaz, D mi Y mi? Kaç tanesini bildiniz? Puanınızı yazın!
Kaynak: NOAA Ocean Service, NOAA Fisheries, National Geographic
#merakliFindik #doğrumuyanlışmı #okyanus #bilim #merak"""),
 ("2026-10-15", "15:00", "hm-bocekler", 7, 'Kelebekler tadı nereden alır? 5 böcek sorusu', """Kelebekler tadı nereden alır? Cevap sizi şaşırtacak 🦋
Böceklerle ilgili 5 tuhaf soru ve kısa cevapları. Kaçını biliyordunuz? En şaşırtıcısını yorumlara yazın.
Kaynak: AMNH, Natural History Museum, Britannica, ABD Milli Parklar Servisi
#merakliFindik #hiçmerakettinmi #böcekler #bilim #merak"""),
 ("2026-10-16", "15:00", "mt-dinozorlar", 8, 'Dinozor testi: 5 sorudan kaçını bilirsin?', """Dinozor uzmanı mısınız? 🦖
5 soruluk test: kâğıt kalem alın, cevapları yazın, sonda puanınızı hesaplayın. 5 üzerinden puanınızı yorumlara yazın!
Kaynak: Natural History Museum (Londra), AMNH, Britannica
#merakliFindik #meraktesti #dinozorlar #bilim #merak"""),
 ("2026-10-17", "15:00", "dy-dinozorlar", 10, 'İnsanlar dinozorları gördü mü? Doğru mu yanlış mı?', """İnsanlar hiç dinozor gördü mü? 🦕
4 dinozor bilgisi: biri bahçedeki kuşlarla ilgili! Kaydırmadan önce D mi Y mi, yorumlara yazın; kaç tanesini bildiniz?
Kaynak: Natural History Museum (Londra), Smithsonian Human Origins
#merakliFindik #doğrumuyanlışmı #dinozorlar #bilim #merak"""),
 ("2026-10-18", "15:00", "hm-gezegenler", 7, 'Hangi gezegen yan yatmış döner? 5 uzay sorusu', """Bir gezegen yan yatmış dönebilir mi? 🪐
Mars'ın rengi, Satürn'ün halkaları, Neptün'ün yılı… Gezegenlerle ilgili 5 soru. Sıradaki soruyu yorumlara siz bırakın!
Kaynak: NASA
#merakliFindik #hiçmerakettinmi #gezegenler #bilim #merak"""),
 ("2026-10-19", "15:00", "mt-bocekler", 8, 'Böcek testi: dünyada kaç karınca var?', """Dünyada kaç karınca var? Tahmin edin 🐜
5 soruluk böcek testi. Kâğıt kalem alın; sonda puanınızı hesaplayıp yorumlara yazın. Testi bir arkadaşınıza gönderin!
Kaynak: ABD Orman Servisi, Natural History Museum, PNAS (2022), Smithsonian
#merakliFindik #meraktesti #böcekler #bilim #merak"""),
 ("2026-10-20", "15:00", "dy-gezegenler", 10, "Venüs'te bir gün, bir yıldan uzun mu? D mi Y mi?", """Bir günün bir yıldan uzun sürdüğü gezegen var mı? 🪐
4 gezegen bilgisi: kaydırmadan önce D mi Y mi, yorumlara yazın. Kaç tanesini bildiniz?
Kaynak: NASA
#merakliFindik #doğrumuyanlışmı #gezegenler #bilim #merak"""),
 ("2026-10-21", "15:00", "hm-okyanus", 7, 'Okyanusta altın var mı? 5 deniz sorusu', """Denizin dibinde göl olabilir mi? 🌊
Altın, gelgit, kendi ışığını yapan canlılar ve en uzun dağ sırası: okyanusla ilgili 5 soru. Sıradaki soruyu siz seçin!
Kaynak: NOAA Ocean Service, NOAA Ocean Exploration
#merakliFindik #hiçmerakettinmi #okyanus #bilim #merak"""),
]

# ---------- Kanca testleri (2026-10-09; sadece TikTok, 15:00; kaynak videos/K0N-*/, ses mevcut VO'dan tam cümleler) ----------
KANCA = [
 ("2026-10-10", "15:00", "K01", 300, "Şimşek Güneş'ten sıcak!", """Şimşek, Güneş'in yüzeyinden yaklaşık 5 kat daha sıcak! ⚡ Sonra da… GÜM! 🔊
Gök gürültüsü neden hep şimşekten sonra gelir? Tahminini yorumlara yaz 👇
Kaynak: NOAA
#merakliFindik #şimşek #neden #bilim #bilim"""),
 ("2026-10-11", "15:00", "K02", 1200, "1 damlaya 1 milyon damlacık", """Tek bir yağmur damlasına 1 milyon bulut damlacığı sığıyor! 💧 Peki bulutlar neden üstümüze düşmüyor? Cevap bir tüyde 🪶
Tahminini yorumlara yaz 👇
Kaynak: NOAA SciJinks
#merakliFindik #bulutlar #neden #bilim #bilim"""),
]

def yt_desc(t):
    lines = [l for l in t.splitlines() if "yorum" not in l.lower()]
    tags = lines.pop() if lines and lines[-1].startswith("#") else ""
    return "\n".join(lines).strip() + "\n\nSorunuzu Instagram'da @meraklifindik'e yazın 📩\n" + (tags + " #shorts").strip()

def build():
    P = []
    for day, st, vids, stories in DAYS:
        at = lambda hm: f"{day}T{hm}:00{TZ}"
        for hm, no in vids:
            v = {"video": {"url": f"{BASE}/v/{VFILE.get(no, no)}.mp4", "metadata": {"thumbnailOffset": COVER[no]}}}
            P.append({"key": f"{no}-ig", "when": at(hm), "label": f"Reels {no} {TITLE[no]}", "args": {"channelId": IG, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": at(hm),
                "text": CAP[no], "assets": [v], "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True, "isAiGenerated": False}}}})
            P.append({"key": f"{no}-tt", "when": at(hm), "label": f"TikTok {no}", "args": {"channelId": TT, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": at(hm),
                "text": CAP[no], "assets": [v], "metadata": {"tiktok": {"isAiGenerated": False}}}})
            P.append({"key": f"{no}-yt", "when": at(hm), "label": f"Shorts {no}", "args": {"channelId": YT, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": at(hm),
                "text": yt_desc(CAP[no]), "assets": [v], "metadata": {"youtube": {"title": f"{TITLE[no]} | Meraklı Fındık #shorts", "categoryId": "27",
                "privacy": "public", "madeForKids": False, "isAiGenerated": False, "notifySubscribers": True, "embeddable": True, "license": "youtube"}}}})
        if st:
            n, title, cap = STATIC[st]
            fs = st + GSURUM.get(st, "")
            files = [f"{fs}-{i}.jpg" for i in range(1, n + 1)] if n else [f"{fs}.jpg"]
            imgs = [{"image": {"url": f"{BASE}/g/{f}", "metadata": {"altText": f"{title}: {ALT}"}}} for f in files]
            P.append({"key": f"{st}-ig", "when": at("12:30"), "label": f"IG statik {title} ({len(files)} görsel)", "args": {"channelId": IG, "schedulingType": "automatic", "mode": "customScheduled",
                "dueAt": at("12:30"), "text": cap, "assets": imgs, "metadata": {"instagram": {"type": "post", "shouldShareToFeed": True}}}})
            P.append({"key": f"{st}-tt", "when": at("12:30"), "label": f"TikTok foto {title}", "args": {"channelId": TT, "schedulingType": "automatic", "mode": "customScheduled",
                "dueAt": at("12:30"), "text": cap, "assets": imgs, "metadata": {"tiktok": {"title": title}}}})
        for hm, f in stories:
            P.append({"key": f"{f}", "when": at(hm), "label": f"Story {f}", "args": {"channelId": IG, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": at(hm),
                "assets": [{"image": {"url": f"{BASE}/s/{f}.jpg", "metadata": {"altText": f"Story: {ALT}"}}}], "metadata": {"instagram": {"type": "story", "shouldShareToFeed": False}}}})
    for day, hm, pid, n, title, cap in KARUSEL:
        at = f"{day}T{hm}:00{TZ}"
        imgs = [{"image": {"url": f"{BASE}/kr/{pid}-{k:02d}.jpg", "metadata": {"altText": f"{title} · kart {k}/{n} — {ALT}"}}} for k in range(1, n + 1)]
        for ch, meta, tag in ((IG, {"instagram": {"type": "post", "shouldShareToFeed": True}}, "ig"), (TT, {"tiktok": {"title": title}}, "tt")):
            P.append({"key": f"kr-{pid}-{tag}", "when": at, "label": f"Kaydırmalı {title} ({tag}, {n} kart)", "args": {"channelId": ch, "schedulingType": "automatic",
                "mode": "customScheduled", "dueAt": at, "text": cap, "assets": imgs, "metadata": meta}})
    for day, hm, pid, n, title, cap in KARUSEL_TT:
        at = f"{day}T{hm}:00{TZ}"
        imgs = [{"image": {"url": f"{BASE}/kr/{pid}-{k:02d}.jpg", "metadata": {"altText": f"{title} · kart {k}/{n} — {ALT}"}}} for k in range(1, n + 1)]
        P.append({"key": f"kr-{pid}-tt", "when": at, "label": f"Kaydırmalı {title} (tt, {n} kart)", "args": {"channelId": TT, "schedulingType": "automatic",
            "mode": "customScheduled", "dueAt": at, "text": cap, "assets": imgs, "metadata": {"tiktok": {"title": title}}}})
    for day, hm, kid, cover, title, cap in KANCA:
        at = f"{day}T{hm}:00{TZ}"
        P.append({"key": f"kanca-{kid}-tt", "when": at, "label": f"Kanca {kid} {title} (TikTok)", "args": {"channelId": TT, "schedulingType": "automatic",
            "mode": "customScheduled", "dueAt": at, "text": cap, "assets": [{"video": {"url": f"{BASE}/v/{kid}.mp4", "metadata": {"thumbnailOffset": cover}}}],
            "metadata": {"tiktok": {"isAiGenerated": False}}}})
    P.sort(key=lambda p: p["when"])
    return P

def load_state():
    return json.load(open(STATE, encoding='utf-8')) if os.path.exists(STATE) else {}

def save_state(s):
    json.dump(s, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    P = build(); cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        for p in P: print(p["when"][:16].replace("T", " "), "|", p["label"])
        print(len(P), "gönderi")
    else:
        import buffer as b
        b.init(); st = load_state()
        if cmd == "drafts":
            for p in P:
                if p["key"] in st: continue
                a = dict(p["args"], saveToDraft=True)
                res = b.rpc("tools/call", {"name": "create_post", "arguments": a})
                txt = "".join(c.get("text", "") for c in res.get("content", []))
                if res.get("isError"): print("HATA", p["key"], txt[:300]); continue
                pid = re.search(r'"id"\s*:\s*"([a-f\d]{24})"', txt).group(1)
                st[p["key"]] = {"id": pid, "status": "draft", "when": p["when"]}; save_state(st); print("taslak", p["key"], pid)
        elif cmd == "guncelle":
            # ileri tarihli (taslak + zamanlı) gönderileri güncel metin/medya ile yeniden yaz; durumları korunur. İsteğe bağlı: anahtar süzgeci (alt dize)
            import datetime
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime("%Y-%m-%dT%H:%M:%S") + TZ
            suz = sys.argv[2] if len(sys.argv) > 2 else ""
            for p in P:
                s = st.get(p["key"])
                if not s or p["when"] <= now or suz not in p["key"]: continue
                a = {k: v for k, v in p["args"].items() if k != "channelId"}
                res = b.rpc("tools/call", {"name": "edit_post", "arguments": dict(a, postId=s["id"], saveToDraft=s["status"] == "draft")})
                txt = "".join(c.get("text", "") for c in res.get("content", []))
                print("HATA" if res.get("isError") else "güncellendi", p["key"], s["status"], txt[:200] if res.get("isError") else "")
        elif cmd == "schedule":
            # kanal başına en fazla `lim` zamanlı gönderi (Buffer ücretsiz plan = 10); kalanlar taslakta bekler, her gün doldurulur
            import datetime
            lim = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime("%Y-%m-%dT%H:%M:%S") + TZ
            q = b.rpc("tools/call", {"name": "list_posts", "arguments": {"organizationId": "6ac67630aa0fa7453ca4d570", "status": ["scheduled"], "first": 100}})
            busy = {}
            for m in re.finditer(r'"channelId"\s*:\s*"([a-f\d]{24})"', "".join(c.get("text", "") for c in q.get("content", []))): busy[m.group(1)] = busy.get(m.group(1), 0) + 1
            for p in P:
                s = st.get(p["key"])
                if not s or s["status"] != "draft": continue
                ch = p["args"]["channelId"]
                if p["when"] <= now: print("GEÇMİŞ", p["key"]); continue
                if busy.get(ch, 0) >= lim:
                    # öncelik: kuyruk doluysa ve bu taslak, kuyruktaki en uzak gönderiden ERKENSE → en uzak olanı taslağa geri al, yerine bunu koy
                    later = [q for q in P if q["args"]["channelId"] == ch and st.get(q["key"], {}).get("status") == "scheduled" and q["when"] > p["when"] and q["when"] > now]
                    if not later: continue
                    far = max(later, key=lambda q: q["when"]); fs = st[far["key"]]
                    fa = {k: v for k, v in far["args"].items() if k != "channelId"}
                    r2 = b.rpc("tools/call", {"name": "edit_post", "arguments": dict(fa, postId=fs["id"], saveToDraft=True)})
                    if r2.get("isError"): print("ATLANDI(öncelik)", far["key"], r2["content"][0].get("text", "")[:200]); continue
                    fs["status"] = "draft"; busy[ch] -= 1; save_state(st); print("taslağa alındı (yer açmak için)", far["key"])
                a = {k: v for k, v in p["args"].items() if k != "channelId"}  # edit = tüm gönderi yeniden doğrulanır
                res = b.rpc("tools/call", {"name": "edit_post", "arguments": dict(a, postId=s["id"], saveToDraft=False)})
                txt = "".join(c.get("text", "") for c in res.get("content", []))
                if res.get("isError"): print("ATLANDI", p["key"], txt[:200]); continue
                s["status"] = "scheduled"; busy[ch] = busy.get(ch, 0) + 1; save_state(st); print("zamanlandı", p["key"])
