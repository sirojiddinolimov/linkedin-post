# Mutolaa: Telegram → LinkedIn kunlik post

Har kuni (avtomatik, GitHub Actions orqali) `@mutolaaxona` Telegram kanalidagi
o'tgan kunning barcha postlari orasidan **eng muhim va ma'noli bittasi**
tanlanadi, LinkedIn uchun ixcham qilib qayta ishlanadi va Mutolaa kompaniya
sahifasida (`https://www.linkedin.com/company/102440497/admin/dashboard/`)
e'lon qilinadi. Kuniga faqat bitta post qilinadi — `state/last_post.json`
faylida oxirgi e'lon qilingan sana saqlanadi va shu sana uchun ikkinchi marta
post qilinmaydi.

## Ishlash tartibi

1. `src/telegram_fetch.py` — Telethon (user session) orqali kanalning
   kechagi (`POST_TIMEZONE`, standart `Asia/Tashkent`) barcha matnli
   postlarini oladi.
2. `src/select_post.py` — agar `ANTHROPIC_API_KEY` berilgan bo'lsa, Claude
   eng mazmunli postni tanlaydi va uni LinkedIn uslubida (o'zbek tilida,
   hashtaglar bilan) qayta yozadi. Kalit berilmagan bo'lsa, ko'rishlar/
   forward/reaksiyalar va uzunlik bo'yicha oddiy heuristika ishlatiladi va
   post matni o'zgartirilmasdan joylanadi.
3. `src/linkedin_publish.py` — LinkedIn Posts API (`w_organization_social`)
   orqali tayyor matnni kompaniya sahifasida e'lon qiladi.
4. `src/state.py` — oxirgi e'lon qilingan sanani `state/last_post.json`'ga
   yozadi (workflow buni avtomatik commit qiladi), shu bilan kuniga bitta
   post qoidasi ta'minlanadi.

Workflow (`.github/workflows/daily-linkedin-post.yml`) har kuni soat 08:00
(Asia/Tashkent) da ishga tushadi, `workflow_dispatch` orqali qo'lda ham
(`dry_run` bilan sinab ko'rish mumkin) ishga tushirish mumkin.

## Sozlash

### 1. Telegram

1. https://my.telegram.org → API development tools'dan `api_id` va
   `api_hash` oling.
2. Lokal kompyuteringizda:
   ```bash
   pip install -r requirements.txt
   cd src
   python generate_session.py
   ```
   Telefon raqamingiz va Telegram yuborgan kodni kiriting. Natijada chiqqan
   `TELEGRAM_SESSION_STRING` qiymatini saqlab qo'ying (bu sizning
   hisobingizga to'liq kirish huquqi beradi — hech kimga bermang).
3. Hisobingiz (yoki bot sifatida ishlatilayotgan alohida akkaunt)
   `@mutolaaxona` kanalini kuzatib turishi kerak (a'zo bo'lishi kifoya,
   ochiq kanal bo'lsa a'zolik ham shart emas).

### 2. LinkedIn

1. https://www.linkedin.com/developers/apps → yangi app yarating, Mutolaa
   kompaniya sahifasiga bog'lang.
2. "Community Management API" mahsulotini qo'shing (LinkedIn tasdiqlashi
   kerak bo'lishi mumkin) va `w_organization_social` scope'ini oling.
3. Admin sifatida OAuth orqali access token oling (3Legged OAuth flow) —
   tokenni yangilab turish kerak bo'lishi mumkin (odatda 60 kunlik).
4. Kompaniya URN'i: admin dashboard URL'idagi raqam, masalan
   `urn:li:organization:102440497`.

### 3. (Ixtiyoriy) Claude bilan tanlash/qayta yozish

`ANTHROPIC_API_KEY` berilsa, eng muhim post AI yordamida tanlanadi va
LinkedIn uslubiga moslashtiriladi. Berilmasa, oddiy heuristika ishlatiladi.

## GitHub sozlamalari

**Settings → Secrets and variables → Actions → Secrets:**

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`
- `LINKEDIN_ACCESS_TOKEN`
- `ANTHROPIC_API_KEY` (ixtiyoriy)

**Settings → Secrets and variables → Actions → Variables:**

- `LINKEDIN_ORG_URN` = `urn:li:organization:102440497`
- `TELEGRAM_CHANNEL` = `mutolaaxona` (ixtiyoriy, standart shu)
- `POST_TIMEZONE` = `Asia/Tashkent` (ixtiyoriy, standart shu)

Barcha kalitlar qo'shilgach, workflow avtomatik ravishda har kuni ishlab
turadi. Sinash uchun **Actions → Daily LinkedIn post from Telegram → Run
workflow** (`dry_run: true` bilan, hech narsa joylanmaydi, faqat log'da
ko'rsatiladi).

## Lokal sinash

```bash
cp .env.example .env
# .env faylini to'ldiring
export $(grep -v '^#' .env | xargs)
export DRY_RUN=true
cd src && python main.py
```
