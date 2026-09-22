# Mutolaa: Telegram → RSS → LinkedIn kunlik post

Har kuni `@mutolaaxona` Telegram kanalidagi o'tgan kunning barcha postlari
orasidan **eng muhim va ma'noli bittasi** tanlanadi va bitta RSS feed
(`docs/feed.xml`, GitHub Pages orqali ochiq)ga yangi element sifatida
qo'shiladi. LinkedIn'ning **kompaniya sahifasidagi o'z "RSS source"
funksiyasi** (Settings → Manage sources → Add source) shu feedni kuzatib
turadi va yangi element chiqqanda uni Mutolaa LinkedIn sahifasida e'lon
qiladi — LinkedIn Developer App, app verification yoki access token kerak
emas.

**Muhim:** GitHub Actions serverlarining IP manzillari Telegram tomonidan
bloklanadi/cheklanadi, shuning uchun kunlik ishlov **mahalliy kompyuterda**
(sizning yoki biror doim yoniq turadigan kompyuter/serverda) cron/Task
Scheduler orqali ishga tushiriladi, natija esa GitHub'ga push qilinadi.
GitHub Actions faqat GitHub Pages'ni avtomatik deploy qilish uchun
ishlatiladi.

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
   yozadi — kuniga bitta yozuv qoidasi shu bilan ta'minlanadi.
5. `scripts/run_daily.sh` (yoki Windows uchun `run_daily.ps1`) — yuqoridagi
   hammasini ishga tushiradi va natijani (`docs/feed.xml`,
   `docs/history.json`, `state/last_post.json`) git orqali push qiladi.

## Sozlash

### 1. Repo'ni kompyuteringizga klonlash

```bash
git clone https://github.com/sirojiddinolimov/linkedin-post
cd linkedin-post
git checkout claude/telegram-linkedin-posts-safyyk
pip install -r requirements.txt
```

`git push` ishlashi uchun kompyuteringizda shu repo uchun GitHub
autentifikatsiyasi sozlangan bo'lishi kerak (masalan `gh auth login`, yoki
SSH kalit, yoki avvalroq shu repo'ni klonlab push qilgan bo'lsangiz odatda
allaqachon sozlangan).

### 2. Telegram

1. https://my.telegram.org → API development tools'dan `api_id` va
   `api_hash` oling.
2. Session string yarating:
   ```bash
   cd src
   python generate_session.py
   cd ..
   ```
   Telefon raqamingiz va Telegram yuborgan kodni kiriting. Natijada chiqqan
   `TELEGRAM_SESSION_STRING` qiymatini saqlab qo'ying (bu sizning
   hisobingizga to'liq kirish huquqi beradi — hech kimga bermang).
3. Hisobingiz `@mutolaaxona` kanalini kuzatib turishi kerak (ochiq kanal
   bo'lgani uchun a'zolik shart emas, lekin bir marta kanalni ochib
   ko'rish tavsiya etiladi).

Kompyuteringizning oddiy uy/ofis interneti Telegram uchun bloklanmagani
sababli, bu yerda **proxy kerak emas** (`TELEGRAM_PROXY_*` maydonlarini
`.env`da bo'sh qoldiring).

### 3. (Ixtiyoriy) Claude bilan tanlash/qayta yozish

`ANTHROPIC_API_KEY` berilsa, eng muhim post AI yordamida tanlanadi va
qisqa, tushunarli matnga moslashtiriladi. Berilmasa, oddiy heuristika
ishlatiladi.

### 4. GitHub Pages'ni yoqish

1. Repo → **Settings → Pages**.
2. **Source**: "Deploy from a branch", **Branch**: `main` (yoki default
   branch) / **`/docs`** ni tanlang, **Save**.
3. Bir necha daqiqadan so'ng sahifangiz manzili paydo bo'ladi, masalan:
   `https://sirojiddinolimov.github.io/linkedin-post/`
4. Feed'ning o'zi shu manzil + `feed.xml` bo'ladi:
   `https://sirojiddinolimov.github.io/linkedin-post/feed.xml`

### 5. `.env` faylini to'ldirish

```bash
cp .env.example .env
```

`.env` faylida quyidagilarni to'ldiring: `TELEGRAM_API_ID`,
`TELEGRAM_API_HASH`, `TELEGRAM_SESSION_STRING`, `FEED_BASE_URL` (4-qadamda
olingan Pages manzili), ixtiyoriy `ANTHROPIC_API_KEY`. `TELEGRAM_PROXY_*`
maydonlarini bo'sh qoldiring.

Avval qo'lda sinab ko'ring:
```bash
export DRY_RUN=true
bash scripts/run_daily.sh   # yoki: powershell scripts/run_daily.ps1
```
Bu hech narsani commit qilmasdan, tanlangan postni terminalga chiqaradi.
Hammasi to'g'ri ko'rinsa, `DRY_RUN`siz ishga tushirib, haqiqatan ham
`docs/feed.xml` yangilanib, GitHub'ga push bo'lishini tekshiring.

### 6. Kunlik avtomatik ishga tushirish

**macOS / Linux (cron):**
```bash
crontab -e
```
Quyidagi qatorni qo'shing (har kuni soat 08:00 da ishga tushadi):
```
0 8 * * * cd /to'liq/yo'l/linkedin-post && bash scripts/run_daily.sh >> /tmp/mutolaa-daily.log 2>&1
```

**Windows (Task Scheduler):**
1. Task Scheduler → **Create Basic Task**.
2. Trigger: **Daily**, vaqt: 08:00.
3. Action: **Start a program** → Program: `powershell.exe`, Arguments:
   `-ExecutionPolicy Bypass -File "C:\to'liq\yo'l\linkedin-post\scripts\run_daily.ps1"`.

Kompyuteringiz shu vaqtda yoqiq va internetga ulangan bo'lishi kifoya —
doimiy ishlab turishi shart emas.

### 7. LinkedIn'da RSS manbani ulash

1. https://www.linkedin.com/company/102440497/admin/settings/manage-content/
   sahifasiga o'ting (Mutolaa admin sifatida).
2. **Add source** tugmasini bosing.
3. Feed manzilini kiriting:
   `https://sirojiddinolimov.github.io/linkedin-post/feed.xml`
4. LinkedIn ko'rsatmalariga amal qiling — feed tasdiqlangach, LinkedIn har
   safar unda yangi element paydo bo'lganda (kuniga bir marta) uni
   sahifangizda taklif qiladi/e'lon qiladi.

Shundan keyin butun jarayon avtomatik: kompyuteringizdagi kunlik vazifa →
`docs/feed.xml` yangilanadi va GitHub'ga push bo'ladi → GitHub Pages uni
darhol serve qiladi → LinkedIn shu feedni kuzatib, yangi postni sahifada
chiqaradi.

## GitHub Actions haqida

`.github/workflows/daily-linkedin-post.yml` endi faqat **qo'lda sinash**
uchun (`workflow_dispatch`, standart `dry_run: true`) — Telegram
serverlarga GitHub Actions IP'laridan ulanib bo'lmagani uchun avtomatik
`schedule` olib tashlangan. Agar kelajakda baribir GitHub Actions orqali
ishlatmoqchi bo'lsangiz, `TELEGRAM_PROXY_HOST`/`PORT`/`USERNAME`/`PASSWORD`
Secrets'larini SOCKS5 proxy bilan to'ldiring (kod buni qo'llab-quvvatlaydi),
lekin hozircha tavsiya etilgan yo'l — mahalliy cron.
