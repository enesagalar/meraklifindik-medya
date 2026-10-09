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
"000": """Merhaba, ben Fındık! 🐿️ Çocuklar "Neden?" diye sorar, ben de cevabı ararım.
40 saniyelik, kâğıttan, kaynağı belli bilim. Her cevap Merak Defteri'ne yeni bir sayfa 📓
Çocuğunuzun sorusunu yorumlara yazın; belki bir sonraki video onun olur 👇
#merakliFindik #çocuklaraBilim #neden #anneBaba #eğitim""",
"001": """Çoğumuz denizi yansıttığı için sanırız… ama asıl sebep güneşin ışığında saklı! ☀️
Güneş ışığının içinde bütün renkler var; hava mavi ışığı her yöne saçıyor. Başını nereye kaldırırsan kaldır, o saçılan maviyi görüyorsun. 💙

Merak Defteri · sayfa 1/8 ✓ · Sıradaki: Gün batımı neden turuncu? Tahmininizi yorumlara yazın 👇
Bunu soran bir çocuk tanıyorsanız gönderin 🐿️

Kaynak: NASA Space Place
#merakliFindik #çocuklaraBilim #neden #gökyüzü #anneBaba""",
"002": """Geçen sefer maviyi konuştuk, şimdi sıra turuncuda! 🌅
Öğlen güneş tepemizde, ışığı havada kısa bir yol gider. Akşam güneş alçalınca ışık havada çok daha uzun yol yürür. Bu yolda mavi ışık saçılıp kalır; bize kırmızı ve turuncu ulaşır. 🧡

Merak Defteri · sayfa 2/8 ✓ · Sıradaki: Bulutlar neden beyaz? Tahmininizi yorumlara yazın 👇
Bunu soran bir çocuk tanıyorsanız gönderin 🐿️

Kaynak: NASA Space Place · Met Office
#merakliFindik #çocuklaraBilim #neden #günbatımı #anneBaba""",
"003": """Hava sadece maviyi saçıyordu… peki bulutlar? ☁️
Bulutlar milyonlarca minik su damlacığından oluşur. Bu damlacıklar havanın parçacıklarından çok daha büyüktür ve bütün renkleri birden saçar. Bütün renkler karışınca: beyaz! 🤍

Merak Defteri · sayfa 3/8 ✓ · Sıradaki: Bu kadar su neden üstümüze düşmüyor? Çocuğunuzun tahminini yorumlara yazın 👇
Bunu soran bir çocuk tanıyorsanız gönderin 🐿️

Kaynak: NOAA SciJinks
#merakliFindik #çocuklaraBilim #neden #bulutlar #anneBaba""",
"004": """Bulutlarda o kadar su var… peki neden üstümüze düşmüyor? ☁️
Bulut damlacıkları inanılmaz küçük: bir yağmur damlasına yaklaşık bir milyon tanesi sığar! Bu kadar minik olunca çok yavaş düşerler; yerden yükselen sıcak hava da onları havada tutar.

Merak Defteri · sayfa 4/8 ✓ · Sıradaki: Yağmur nasıl oluşur? Çocuğunuzun tahminini yorumlara yazın 👇

Kaynak: NOAA SciJinks
#merakliFindik #çocuklaraBilim #neden #bulutlar #anneBaba""",
"005": """Bulutlar havada kalıyorsa yağmur nereden geliyor? 🌧️
Güneş suyu ısıtır, su buhar olup yükselir, yukarıda soğuyup damlacığa dönüşür. Damlacıklar çarpışıp birleşir, ağırlaşınca da… yağmur!

Merak Defteri · sayfa 5/8 ✓ · Sıradaki: Şimşek neden çakar? Tahmininizi yorumlara yazın 👇

Kaynak: USGS Water Science School
#merakliFindik #çocuklaraBilim #neden #yağmur #anneBaba""",
"006": """Fırtınada gökyüzü bir anda parlıyor… ⚡
Fırtına bulutunda buz parçaları ve damlalar çarpışıp elektrik biriktirir. Elektrik çok fazla olunca dev bir kıvılcım olup atlar: şimşek!

Merak Defteri · sayfa 6/8 ✓ · Sıradaki: Gök gürültüsü neden sonra gelir? Tahmininizi yorumlara yazın 👇

Kaynak: NOAA National Severe Storms Laboratory
#merakliFindik #çocuklaraBilim #neden #şimşek #anneBaba""",
"007": """Önce şimşek, sonra gümm! 🔊
Şimşek havayı Güneş'in yüzeyinden bile sıcak yapar; hava hızla genişler = gök gürültüsü. Işık anında gelir, ses ise 1 km'yi ~3 saniyede gider. Saydığınız saniyeyi 3'e bölün: fırtına o kadar km uzakta!

Merak Defteri · sayfa 7/8 ✓ · Sıradaki: Gökkuşağı! 🌈 Tahmininizi yorumlara yazın 👇

Kaynak: NOAA NSSL · NWS
#merakliFindik #çocuklaraBilim #neden #fırtına #anneBaba""",
"008": """Sezon finali! 🌈 Güneş ışığının içindeki bütün renkleri hatırlıyor musunuz?
Işık yağmur damlasına girerken bükülür, renkler ayrılır, damlanın içinde seker ve çıkar. Milyonlarca damla gökyüzüne kocaman bir yay çizer. Gökkuşağını görmek için güneş arkanızda, yağmur önünüzde olmalı!

Merak Defteri 8/8 tamam ✓ · Sezon 2: Vücudumuz geliyor — ilk soru: Neden esneriz? 👇

Kaynak: NOAA SciJinks · Met Office
#merakliFindik #çocuklaraBilim #gökkuşağı #neden #anneBaba""",
}
TITLE = {"000": "Merhaba, ben Fındık! 🐿️", "001": "Gökyüzü neden mavi?", "002": "Gün batımı neden turuncu?", "003": "Bulutlar neden beyaz?",
         "004": "Bulutlar neden düşmüyor?", "005": "Yağmur nasıl oluşur?", "006": "Şimşek neden çakar?", "007": "Gök gürültüsü neden sonra gelir?",
         "008": "Gökkuşağı nasıl oluşur? (Sezon finali)"}
COVER = {"000": 2000, "001": 2900, "002": 3900, "003": 4900, "004": 4000, "005": 4000, "006": 4800, "007": 4000, "008": 4400}

# Revize video dosyaları (2026-10-09: açılış kuralı + −14 LUFS; eski v/NNN.mp4 kaldırıldı)
VFILE = {n: n + "-r2" for n in ("003", "004", "005", "006", "007", "008")}

# ---------- statik gönderiler (IG; TikTok'ta foto gönderisi) ----------
STATIC = {
"carousel-001": (7, "Merak Defteri · Sayfa 1", """Gökyüzü neden mavi? Merak Defteri'nin ilk sayfası 📓
Videoyu izlediniz mi? Akşam çocuğunuzla konuşmak için kaydedin 📌 Kaydırın →
#merakliFindik #çocuklaraBilim #neden #gökyüzü #anneBaba"""),
"carousel-ebeveyn-rehberi-gokyuzu": (5, "Ebeveyn rehberi", """Çocuğunuz "Gökyüzü neden mavi?" diye sorarsa yaşına göre 1 cümlelik cevaplar 👇
5–7 yaş, 8–10 yaş ve 11+ için ayrı ayrı. Kaydedin, eşinize gönderin ✈️
#merakliFindik #çocuklaraBilim #anneBaba #çocukEğitimi #neden"""),
"tek-sence-neden": (0, "Sence neden?", """Bulutlarda tonlarca su var… peki neden üstümüze düşmüyor? ☁️
A mı, B mi? Çocuğunuzun cevabını yorumlara yazın; doğru cevap akşamki videoda 🐿️
#merakliFindik #neden #bulutlar #çocuklaraBilim #anneBaba"""),
"carousel-evde-dene-kavanozda-yagmur": (7, "Evde Dene", """Evde Dene: kavanozda yağmur 🫙 5 dakikalık mutfak deneyi!
⚠️ Sıcak suyu bir yetişkin döksün, kaynar su kullanmayın. Denediyseniz ne gördüğünüzü yorumlara yazın 👇
#merakliFindik #evdeDeney #çocuklaraBilim #yağmur #anneBaba"""),
"tek-simsek-mi-gurultu-mu": (0, "Fırtınada hangisi önce?", """Fırtınada hangisi önce gelir: şimşek mi, gök gürültüsü mü? ⚡
Çocuğunuzla tahmin edin, cevabınızı yorumlara yazın 👇 Cevap bu hafta Merak Defteri'nde!
#merakliFindik #neden #şimşek #çocuklaraBilim #anneBaba"""),
"carousel-uc-saniye-kurali": (5, "3 saniye kuralı", """Fırtına ne kadar uzakta? 3 saniye kuralıyla saniye sayarak bulun ⚡
Unutmayın: fırtınada içeride kalın! Kaydedin 📌
#merakliFindik #çocuklaraBilim #fırtına #neden #anneBaba"""),
"tek-gokkusagi-gunes": (0, "Güneş nerede?", """Gökkuşağını görmek için güneş nerede olmalı: önümüzde mi, arkamızda mı? 🌈
Tahmininizi yorumlara yazın; cevap akşamki sezon finalinde!
#merakliFindik #neden #gökkuşağı #çocuklaraBilim #anneBaba"""),
"carousel-sezon1-ozet": (3, "Sezon 1 özeti", """8 soru, 8 cevap — Gökyüzü Sezonu tamam! 🎉
Hangisi en sevdiğiniz oldu? Yorumlara yazın 👇 Sırada Sezon 2: Vücudumuz 🫁
#merakliFindik #çocuklaraBilim #neden #anneBaba #eğitim"""),
}
ALT = "Kâğıt kesik tarzında, defter sayfası üzerinde sincap maskot Fındık ve çocuklar için bilim sorusu"

# ---------- takvim ----------
# gün: (tarih, statik@12:30 | None, [videolar (saat, no)], [story (saat, dosya)])
DAYS = [
 ("2026-10-08", None, [("12:30", "000"), ("19:30", "001")], [("13:00", "story-merhaba"), ("16:00", "story-001-a-soru"), ("19:40", "story-001-b-video"), ("21:30", "story-001-c-cevap")]),
 ("2026-10-09", "carousel-001", [("19:30", "002")], [("10:00", "story-002-a-soru"), ("19:40", "story-002-b-video"), ("21:30", "story-002-c-cevap")]),
 ("2026-10-10", "carousel-ebeveyn-rehberi-gokyuzu", [("19:30", "003")], [("10:00", "story-003-a-soru"), ("19:40", "story-003-b-video"), ("21:30", "story-003-c-cevap")]),
 ("2026-10-11", "tek-sence-neden", [("19:30", "004")], [("10:00", "story-004-a-soru"), ("19:40", "story-004-b-video"), ("21:30", "story-004-c-cevap")]),
 ("2026-10-12", "carousel-evde-dene-kavanozda-yagmur", [("19:30", "005")], [("10:00", "story-005-a-soru"), ("19:40", "story-005-b-video"), ("21:30", "story-005-c-cevap")]),
 ("2026-10-13", "tek-simsek-mi-gurultu-mu", [("19:30", "006")], [("10:00", "story-006-a-soru"), ("19:40", "story-006-b-video"), ("21:30", "story-006-c-cevap")]),
 ("2026-10-14", "carousel-uc-saniye-kurali", [("19:30", "007")], [("10:00", "story-007-a-soru"), ("19:40", "story-007-b-video"), ("21:30", "story-007-c-cevap")]),
 ("2026-10-15", "tek-gokkusagi-gunes", [("19:30", "008")], [("10:00", "story-008-a-soru"), ("19:40", "story-008-b-video"), ("21:30", "story-008-c-cevap")]),
 ("2026-10-16", "carousel-sezon1-ozet", [], [("13:00", "story-sezon2")]),
]

# ---------- Kaydırmalı formatlar (2026-10-09 kullanıcı kararı; kaynak studio/karusel/, görseller yayin/kr/<id>-NN.jpg, 4:5) ----------
# dy = Doğru mu Yanlış mı · hm = Hiç merak ettin mi · mt = Merak Testi. Video/12:30 içeriğini TEKRAR ETME.
KARUSEL = [
 ("2026-10-10", "17:00", "dy-hava", 10, "Doğru mu, Yanlış mı? Hava", """Bu 4 bilginin kaçı doğru? 🤔 Her kartta kaydırmadan önce tahminini yorumlara yaz: D mi, Y mi? 👇
Sonuna kadar kaydır, puanını gör! Bunu bilmeyen birine gönder ✈️ Kaydet 📌
Kaynak: NOAA · Met Office · USGS
#merakliFindik #doğrumuyanlışmı #neden #çocuklaraBilim #anneBaba"""),
 ("2026-10-11", "17:00", "hm-vucut", 7, "Hiç merak ettin mi? Vücudumuz", """Kendini neden gıdıklayamazsın? 🤭 Vücudumuzla ilgili 5 tuhaf soru ve cevabı, kaydır 👉
En çok hangisi şaşırttı? Yorumlara yaz; sıradaki "Neden?"i sen seç 👇 Kaydet, akşam sofrada sor 📌
Kaynak: NHS · NIH · Scientific American
#merakliFindik #hiçmerakettinmi #vücudumuz #çocuklaraBilim #anneBaba"""),
 ("2026-10-12", "17:00", "mt-hayvanlar", 8, "Merak Testi: Hayvanlar", """Merak Testi: Hayvanlar 🐾 5 soru, cevaplar son kartta!
Kâğıt kalem al, cevaplarını yaz, sonra puanını yorumlara bırak: 5/5 mi? 👇 Arkadaşına gönder, kim kazanacak? ✈️
Kaynak: National Geographic · Smithsonian · WWF
#merakliFindik #meraktesti #hayvanlar #çocuklaraBilim #anneBaba"""),
 ("2026-10-13", "17:00", "dy-hayvanlar", 10, "Doğru mu, Yanlış mı? Hayvanlar", """Japon balığının hafızası gerçekten 3 saniye mi? 🐠 4 bilgi, her kartta önce tahmin et: D mi, Y mi? 👇
Kaç tanesini bildin? Puanını yaz, bilmeyen birine gönder ✈️ Kaydet 📌
Kaynak: National Geographic · Smithsonian
#merakliFindik #doğrumuyanlışmı #hayvanlar #çocuklaraBilim #anneBaba"""),
 ("2026-10-14", "17:00", "hm-uzay", 7, "Hiç merak ettin mi? Uzay", """Gördüğün Güneş aslında 8 dakika önceki Güneş! ☀️ Uzayla ilgili 5 soru ve cevabı, kaydır 👉
Hangisi aklını uçurdu? Yorumlara yaz; sıradaki "Neden?"i sen seç 👇 Kaydet 📌
Kaynak: NASA
#merakliFindik #hiçmerakettinmi #uzay #çocuklaraBilim #anneBaba"""),
 ("2026-10-15", "17:00", "dy-vucut", 10, "Doğru mu, Yanlış mı? Vücudumuz", """Beynimizin sadece %10'unu mu kullanıyoruz? 🧠 4 bilgi, her kartta önce tahmin et: D mi, Y mi? 👇
Kaç tanesini bildin? Puanını yaz, bilmeyen birine gönder ✈️ Kaydet 📌
Kaynak: NIH · Mayo Clinic · Smithsonian
#merakliFindik #doğrumuyanlışmı #vücudumuz #çocuklaraBilim #anneBaba"""),
 ("2026-10-16", "17:00", "mt-dunya", 8, "Merak Testi: Dünyamız", """Merak Testi: Dünyamız 🌍 5 genel kültür sorusu, cevaplar son kartta!
Cevaplarını yaz, puanını yorumlara bırak: 5/5 mi? 👇 Ailece çözün, testi arkadaşına gönder ✈️
Kaynak: NASA · NOAA · National Geographic
#merakliFindik #meraktesti #genelkültür #çocuklaraBilim #anneBaba"""),
]

# ---------- Kanca testleri (2026-10-09; sadece TikTok, 15:00; kaynak videos/K0N-*/, ses mevcut VO'dan tam cümleler) ----------
KANCA = [
 ("2026-10-10", "15:00", "K01", 300, "Şimşek Güneş'ten sıcak!", """Şimşek, Güneş'in yüzeyinden yaklaşık 5 kat daha sıcak! ⚡ Sonra da… GÜM! 🔊
Gök gürültüsü neden hep şimşekten sonra gelir? Tahminini yorumlara yaz 👇
Kaynak: NOAA
#merakliFindik #şimşek #neden #çocuklaraBilim #bilim"""),
 ("2026-10-11", "15:00", "K02", 1200, "1 damlaya 1 milyon damlacık", """Tek bir yağmur damlasına 1 milyon bulut damlacığı sığıyor! 💧 Peki bulutlar neden üstümüze düşmüyor? Cevap bir tüyde 🪶
Tahminini yorumlara yaz 👇
Kaynak: NOAA SciJinks
#merakliFindik #bulutlar #neden #çocuklaraBilim #bilim"""),
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
                "text": CAP[no], "assets": [v], "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True, "isAiGenerated": True}}}})
            P.append({"key": f"{no}-tt", "when": at(hm), "label": f"TikTok {no}", "args": {"channelId": TT, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": at(hm),
                "text": CAP[no], "assets": [v], "metadata": {"tiktok": {"isAiGenerated": True}}}})
            P.append({"key": f"{no}-yt", "when": at(hm), "label": f"Shorts {no}", "args": {"channelId": YT, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": at(hm),
                "text": yt_desc(CAP[no]), "assets": [v], "metadata": {"youtube": {"title": f"{TITLE[no]} | Meraklı Fındık #shorts", "categoryId": "27",
                "privacy": "public", "madeForKids": True, "notifySubscribers": True, "embeddable": True, "license": "youtube"}}}})
        if st:
            n, title, cap = STATIC[st]
            files = [f"{st}-{i}.jpg" for i in range(1, n + 1)] if n else [f"{st}.jpg"]
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
    for day, hm, kid, cover, title, cap in KANCA:
        at = f"{day}T{hm}:00{TZ}"
        P.append({"key": f"kanca-{kid}-tt", "when": at, "label": f"Kanca {kid} {title} (TikTok)", "args": {"channelId": TT, "schedulingType": "automatic",
            "mode": "customScheduled", "dueAt": at, "text": cap, "assets": [{"video": {"url": f"{BASE}/v/{kid}.mp4", "metadata": {"thumbnailOffset": cover}}}],
            "metadata": {"tiktok": {"isAiGenerated": True}}}})
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
