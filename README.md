# Mutolaa: Telegram → RSS → LinkedIn kunlik post

Har kuni (avtomatik, GitHub Actions orqali) `@mutolaaxona` Telegram kanalidagi
o'tgan kunning barcha postlari orasidan **eng muhim va ma'noli bittasi**
tanlanadi va bitta RSS feed (`docs/feed.xml`, GitHub Pages orqali ochiq)ga
yangi element sifatida qo'shiladi. LinkedIn'ning **kompaniya sahifasidagi
o'z "RSS source" funksiyasi** (Settings → Manage sources → Add source) shu
feedni kuzatib turadi va yangi element chiqqanda uni Mutolaa LinkedIn
sahifasida e'lon qiladi — LinkedIn Developer App, app verification yoki
access token kerak emas.

Kuniga faqat bitta yozuv qo'shiladi — `state/last_post.json` faylida oxirgi
qayta ishlangan sana saqlanadi, shu sana uchun ikkinchi marta yozuv
qo'shilmaydi.

## Ishlash tartibi

1. `src/telegram_fetch.py` — Telethon (user session) orqali kanalning
   kechagi (`POST_TIMEZONE`, standart `Asia/Tashkent`) barcha matnli
   postlarini oladi.
2. `src/select_post.py` — agar `ANTHROPIC_API_KEY` berilgan bo'lsa, Claude
   eng mazmunli postni tanlaydi va uni qisqa, ixcham matnga (o'zbek tilida,
   hashtaglar bilan) qayta yozadi. Kalit berilmagan bo'lsa, ko'rishlar/
   forward/reaksiyalar va uzunlik bo'yicha oddiy heuristika ishlatiladi va
   post matni o'zgartirilmasdan ishlatiladi.
3. `src/rss_feed.py` — tanlangan postni `docs/history.json`ga qo'shadi va
   `docs/feed.xml` (RSS 2.0) faylini shundan qayta yaratadi (oxirgi
   `FEED_MAX_ITEMS` ta yozuv saqlanadi).
4. `src/state.py` — oxirgi qayta ishlangan sanani `state/last_post.json`'ga
   yozadi (workflow buni avtomatik commit qiladi) — kuniga bitta yozuv
   qoidasi shu bilan ta'minlanadi.

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
3. Hisobingiz `@mutolaaxona` kanalini kuzatib turishi kerak (ochiq kanal
   bo'lgani uchun a'zolik shart emas, lekin bir marta kanalni ochib
   ko'rish tavsiya etiladi).

### 2. (Ixtiyoriy) Claude bilan tanlash/qayta yozish

`ANTHROPIC_API_KEY` berilsa, eng muhim post AI yordamida tanlanadi va
qisqa, tushunarli matnga moslashtiriladi. Berilmasa, oddiy heuristika
ishlatiladi.

### 3. GitHub Pages'ni yoqish

1. Repo → **Settings → Pages**.
2. **Source**: "Deploy from a branch", **Branch**: `main` / **`/docs`** ni
   tanlang, **Save**.
3. Bir necha daqiqadan so'ng sahifangiz manzili paydo bo'ladi, masalan:
   `https://sirojiddinolimov.github.io/linkedin-post/`
4. Shu manzilni `FEED_BASE_URL` GitHub Variable sifatida qo'shing (pastga
   qarang). Feed'ning o'zi shu manzil + `feed.xml` bo'ladi:
   `https://sirojiddinolimov.github.io/linkedin-post/feed.xml`

### 4. GitHub sozlamalari

**Settings → Secrets and variables → Actions → Secrets:**

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`
- `ANTHROPIC_API_KEY` (ixtiyoriy)

**Settings → Secrets and variables → Actions → Variables:**

- `FEED_BASE_URL` = 2-bosqichda olingan GitHub Pages manzili (oxirida `/`
  bilan yoki bo'lmasa ham farqi yo'q), masalan
  `https://sirojiddinolimov.github.io/linkedin-post/`
- `TELEGRAM_CHANNEL` = `mutolaaxona` (ixtiyoriy, standart shu)
- `POST_TIMEZONE` = `Asia/Tashkent` (ixtiyoriy, standart shu)
- `FEED_TITLE` = `Mutolaa | Kunlik tanlov` (ixtiyoriy)

Sozlangach, **Actions → Daily Telegram digest -> RSS feed for LinkedIn →
Run workflow** orqali birinchi marta qo'lda ishga tushiring (`dry_run: true`
bilan avval sinab ko'rish mumkin, hech narsa commit qilinmaydi).

### 5. LinkedIn'da RSS manbani ulash

1. https://www.linkedin.com/company/102440497/admin/settings/manage-content/
   sahifasiga o'ting (Mutolaa admin sifatida).
2. **Add source** tugmasini bosing.
3. Feed manzilini kiriting:
   `https://sirojiddinolimov.github.io/linkedin-post/feed.xml`
4. LinkedIn ko'rsatmalariga amal qiling — feed tasdiqlangach, LinkedIn har
   safar unda yangi element paydo bo'lganda (kuniga bir marta, workflow
   ishlaganda) uni sahifangizda taklif qiladi/e'lon qiladi.

Shundan keyin butun jarayon avtomatik: workflow → `docs/feed.xml` yangilanadi
→ LinkedIn shu feedni kuzatib, yangi postni sahifada chiqaradi.

## Lokal sinash

```bash
cp .env.example .env
# .env faylini to'ldiring (FEED_BASE_URL'ni ham)
export $(grep -v '^#' .env | xargs)
export DRY_RUN=true
cd src && python main.py
```
