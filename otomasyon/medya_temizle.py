"""Yayınlanmış gönderilerin medyasını depodan siler (GitHub Pages 1 GB sınırı).
Kural: bir dosya, onu kullanan TÜM gönderilerin zamanı en az SAKLA_GUN gün önce geçmişse silinir.
Takvimde hiç geçmeyen dosyalara dokunulmaz. Asıl kopyalar yerelde (videos/…/renders, assets/…) durur.
python otomasyon/medya_temizle.py [--dry]
"""
import os, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilot_plan as pp

SAKLA_GUN = 3
ROOT = os.path.abspath(os.path.join(HERE, ".."))
now = datetime.datetime.now(datetime.timezone.utc)
son = {}  # dosya yolu -> onu kullanan en geç gönderi zamanı
for p in pp.build():
    when = datetime.datetime.fromisoformat(p["when"])
    for a in p["args"].get("assets", []):
        url = (a.get("image") or a.get("video") or {}).get("url", "")
        if url.startswith(pp.BASE + "/"):
            rel = url[len(pp.BASE) + 1:]
            son[rel] = max(son.get(rel, when), when)
sil = [rel for rel, t in son.items() if now - t > datetime.timedelta(days=SAKLA_GUN) and os.path.exists(os.path.join(ROOT, rel))]
for rel in sorted(sil):
    print(("(deneme) " if "--dry" in sys.argv else "") + "silindi:", rel)
    if "--dry" not in sys.argv:
        os.remove(os.path.join(ROOT, rel))
print(f"{len(sil)} dosya silindi · takipte {len(son)} dosya · saklama {SAKLA_GUN} gün")
