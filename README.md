# Majlislar xonasini band qilish

3 ta xona ("Katta zal" — 20, "Kichik xona" — 6, "Kabinet" — 4 kishi) ni band qilish uchun veb-ilova.

**Texnologiyalar:** Python, Flask, SQLite, oddiy HTML/CSS (frontend freymvorksiz), pytest.

## Imkoniyatlar

- Ism, xona, odamlar soni, sana, boshlanish va tugash vaqtini kiritib band qilish
- Vaqtlar ustma-ust tushmaydi: 10:00–11:00 band bo'lsa, 10:30–11:30 rad etiladi, 11:00–12:00 mumkin
- Tanlangan kun uchun barcha xonalar jadvali (vaqt chizig'i + ro'yxat), kunlar orasida o'tish
- O'z bandini bekor qilish (faqat shu brauzerdan yaratilgan bandlar)
- Faqat ish vaqtida: 09:00–18:00; o'tgan kunga band qilib bo'lmaydi
- Sig'imdan ko'p odam kiritilsa — darhol ogohlantirish, server esa bunday bandni qabul qilmaydi
- Mobil telefonga moslashgan
- Ma'lumotlar SQLite faylida saqlanadi — server qayta ishga tushsa ham yo'qolmaydi

## Ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug        # http://127.0.0.1:5000
python -m pytest                   # testlar
```

Sozlamalar (muhit o'zgaruvchilari):

| O'zgaruvchi | Ma'nosi | Standart qiymat |
|---|---|---|
| `SECRET_KEY` | cookie'ni imzolash uchun kalit (productionda **albatta** o'rnating) | `dev-only-secret` |
| `DATABASE` | SQLite fayl yo'li | `bookings.db` loyiha papkasida |

## Tuzilma

```
app.py       — Flask marshrutlari: /, /book, /cancel/<id>
booking.py   — qoidalar: tekshiruvlar, kesishish, bandni saqlash
db.py        — SQLite ulanishi, sxema, xonalar ro'yxati
templates/   — HTML
static/      — CSS
tests/       — pytest testlari
```

## Muhim qarorlar

- **Kesishish sharti:** `yangi.boshlanish < eski.tugash VA eski.boshlanish < yangi.tugash`.
  Qat'iy `<` ishlatilgani uchun chegarasi tegib turgan bandlar (11:00 da tugaydi / 11:00 da boshlanadi) ruxsat etiladi.
- **Bir vaqtda kelgan ikki so'rov:** tekshirish va yozish `BEGIN IMMEDIATE` tranzaksiyasi ichida.
  Aks holda ikki kishi bir paytda bir xil vaqtni band qilsa, ikkalasi ham tekshiruvdan o'tib ketishi mumkin edi.
- **Vaqtlar `HH:MM` satri sifatida saqlanadi.** Har doim 2 xonali bo'lgani uchun satrlarni SQL'da solishtirish to'g'ri ishlaydi.
- **"O'z bandi" qanday aniqlanadi:** login yo'q (vazifada talab qilinmagan). Band qilinganda uning `id`si
  imzolangan cookie'ga (Flask `session`) yoziladi. Bekor qilish tugmasi faqat shu bandlar uchun chiqadi,
  server ham `/cancel` da cookie'ni tekshiradi — boshqaning bandini o'chirib bo'lmaydi (403).
  Kamchiligi: cookie o'chirilsa yoki boshqa qurilmadan kirilsa, bandni bekor qilib bo'lmaydi.
- **Sig'imdan oshish:** brauzerda ogohlantirish chiqadi va server bandni rad etadi.

## Internetga joylash (PythonAnywhere)

Render/Railway bepul tarifida disk har qayta joylashda tozalanadi — SQLite ma'lumotlari yo'qoladi.
PythonAnywhere'da fayllar saqlanib qoladi, shuning uchun u tanlandi.

1. pythonanywhere.com da bepul akkaunt oching.
2. **Consoles → Bash**:
   ```bash
   git clone https://github.com/<USERNAME>/<REPO>.git xona-band
   cd xona-band
   python3.12 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Web → Add a new web app → Manual configuration → Python 3.12**.
4. **Virtualenv:** `/home/<USERNAME>/xona-band/.venv`
5. **WSGI configuration file** ni ochib, hammasini quyidagiga almashtiring:
   ```python
   import os, sys, time
   # Server UTC vaqtida ishlaydi — "bugun" Toshkent vaqti bo'yicha bo'lishi uchun
   os.environ["TZ"] = "Asia/Tashkent"
   time.tzset()
   path = "/home/<USERNAME>/xona-band"
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ["SECRET_KEY"] = "<uzun-tasodifiy-satr>"
   os.environ["DATABASE"] = path + "/bookings.db"
   from app import app as application
   ```
   Tasodifiy kalit: `python -c "import secrets; print(secrets.token_hex(32))"`
6. **Static files:** URL `/static/` → `/home/<USERNAME>/xona-band/static`
7. **Reload** tugmasini bosing. Ilova `https://<USERNAME>.pythonanywhere.com` da ochiladi.

Yangilash: `git pull` → Web sahifasida **Reload**.
