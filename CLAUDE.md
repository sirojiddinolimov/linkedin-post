# CLAUDE.md

## ElevenLabs audio (Mutolaa hikoyalari)

Foydalanuvchi Google Drive'dagi "Mutolaa" papkasidan hikoya matnini olib, ElevenLabs orqali ko'p ovozli audio yaratishni so'raydi. Qoidalar:

- **Ovozlar faqat foydalanuvchining "My Voices" ro'yxatidan.** ElevenLabs'ning standart (premade) ovozlarini (George, Bill, Sarah va h.k.) ishlatma.
  - Ro'yxatni `GET https://api.elevenlabs.io/v2/voices` orqali ol (`xi-api-key: $ELEVENLABS_API_KEY`) va `category` = `premade` bo'lganlarini chiqarib tashla.
  - Kalitda `voices_read` ruxsati bo'lmasa (401), taxmin qilma — foydalanuvchidan ruxsatni yoqishni yoki Voice ID'larni yuborishni so'ra.
- **Faqat o'zbek tilini qo'llab-quvvatlaydigan model.** Hozircha bu `eleven_v3`. Ishni boshlashdan oldin `GET /v1/models` bilan tekshir; o'zbek tili yo'q modelni ishlatma.
- Kalit muhit o'zgaruvchisida: `ELEVENLABS_API_KEY`. Qiymatini hech qachon chiqarma.
- **Kreditni tejash:** to'liq audiodan oldin har bir rol uchun bitta qisqa sinov jumlasini yaratib, foydalanuvchiga eshittir va tasdiqlat. Matn uzunligini (1 belgi ≈ 1 kredit) qolgan kredit bilan solishtir va yetmasa oldindan ayt.
- Foydalanuvchi bilan o'zbek tilida gaplash.
