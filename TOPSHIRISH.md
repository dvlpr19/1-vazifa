# 1-vazifa: Topshirish

**Ism-familiya:** Ermamatov Nurullokh
**Sana:** 08.10.2026

## Linklar

- Ishlab turgan ilova: https://nurullokh77.pythonanywhere.com
- GitHub repozitoriy: https://github.com/dvlpr19/1-vazifa
- AI chat tarixi (link yoki fayl nomi): https://github.com/dvlpr19/3-vazifalar/blob/main/ai-chat-tarixi.md (Claude Code sessiyasi, uchala vazifa bitta suhbatda)

## Qanday texnologiyalar ishlatdingiz va nega?

- **Flask** — kichik ilova uchun eng sodda freymvork: 3 ta marshrut (`/`, `/book`, `/cancel/<id>`), ortiqcha narsa yo'q, kodni oxirigacha tushuntirib bera olaman.
- **SQLite** — alohida server kerak emas, bitta fayl. Ma'lumot server qayta ishga tushganda ham saqlanadi (6-talab). Ikki kishi bir vaqtda band qilsa, `BEGIN IMMEDIATE` tranzaksiyasi ustma-ust tushishning oldini oladi.
- **Oddiy HTML/CSS + bir oz JavaScript** — React kabi freymvork bu hajmdagi ilova uchun ortiqcha. JS faqat sig'imdan oshganda darhol ogohlantirish uchun.
- **pytest** — 31 ta test: kesishish qoidasi, ish vaqti, sig'im, bekor qilish, ma'lumot saqlanishi.
- **PythonAnywhere** — bepul tarifda disk saqlanib qoladi. Render/Railway bepul tarifida disk har qayta joylashda tozalanadi va SQLite fayli yo'qoladi.

## Vaqt qanday taqsimlandi? (taxminan)

Kodni AI (Claude Code) yozdi, men vazifani berdim, qarorlarni ko'rib chiqdim va deployni boshqardim.

| Ish | Vaqt |
|---|---|
| Rejalashtirish (texnologiya va hosting tanlash) | 15 daqiqa |
| Asosiy kod (AI bilan) | 20 daqiqa |
| Xatolarni tuzatish va tekshirish | 15 daqiqa |
| Internetga joylash (deploy) | 30 daqiqa |
| Kodni o'qib tushunish | |

## Eng ko'p qayerda qiynaldingiz va qanday hal qildingiz?

1. **Hosting tanlash.** Birinchi xayol Render edi, lekin uning bepul tarifida disk vaqtinchalik — har qayta ishga tushganda SQLite fayli o'chib ketadi va 6-talab bajarilmaydi. Shuning uchun fayllar saqlanadigan PythonAnywhere tanlandi.
2. **Vaqt mintaqasi.** PythonAnywhere serveri UTC vaqtida ishlaydi, Toshkent esa UTC+5. Toshkent vaqti bilan 00:00–05:00 orasida server hali "kecha" deb hisoblardi: noto'g'ri sana ko'rsatilardi va o'tib ketgan kunga band qilish mumkin bo'lardi. WSGI faylida `TZ=Asia/Tashkent` o'rnatib hal qilindi.
3. **"O'z bandini bekor qilish" — login yo'q.** Kim qaysi bandni yaratganini bilish kerak edi. Yechim: band qilingan `id` imzolangan cookie'ga (Flask `session`) yoziladi, bekor qilish tugmasi faqat shu bandlar uchun chiqadi va server ham tekshiradi (boshqaning bandini o'chirishga urinish — 403).

## AI qayerda noto'g'ri javob berdi yoki xato kod yozdi? Buni qanday sezdingiz?

1. **Vaqt mintaqasini hisobga olmadi.** AI `date.today()` ishlatdi va README'dagi deploy ko'rsatmasida ham bu haqda hech narsa yo'q edi. Deploy paytida server UTC'da ishlashi ma'lum bo'lgach sezildi va tuzatildi.
2. **Talabdan chetga chiqdi.** Vazifada sig'imdan oshsa "ogohlantirish chiqishi" kerak deyilgan, AI esa bunday bandni butunlay rad etadigan qilib yozdi. Talab bilan solishtirganda sezildi. Rad etish qoldirildi (sig'imdan oshgan majlis baribir xonaga sig'maydi), lekin bu ongli qaror sifatida README'ga yozildi.
3. **Birinchi tekshiruv noto'g'ri natija berdi.** Ilovani gunicorn bilan sinashda AI tanlagan port (8765) boshqa dastur tomonidan band edi va so'rov 404 qaytardi. Server logini ko'rib sezildi, boshqa port bilan qayta tekshirildi.

## Nima qilishga ulgurmadingiz?

- **Login yo'q.** Bandni faqat uni yaratgan brauzerdan bekor qilish mumkin; cookie o'chirilsa yoki boshqa qurilmadan kirilsa — bekor qilib bo'lmaydi.
- **Bandni tahrirlash** (vaqtini o'zgartirish) yo'q — faqat bekor qilib, qaytadan band qilish mumkin.
- **Dam olish kunlari** ham band qilish mumkin (talabda aytilmagan).
- **Brauzerdagi ogohlantirish (JavaScript) uchun test** yo'q — testlar faqat server tomonini tekshiradi.
- **Administrator sahifasi** (hamma bandlarni boshqarish) yo'q.
