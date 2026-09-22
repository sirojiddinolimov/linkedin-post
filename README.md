# Mutolaa: Telegram → RSS → LinkedIn daily post

Every day, the single most important/meaningful post from the previous day
in the `@mutolaaxona` Telegram channel is picked, translated to English, and
added as a new item to an RSS feed (`docs/feed.xml`, served publicly via
GitHub Pages). LinkedIn's own company-page **RSS source** feature
(Settings → Manage sources → Add source) watches that feed and publishes the
new item to the Mutolaa LinkedIn page — no LinkedIn Developer App, app
verification, or access token needed.

Only one entry is added per day — `state/last_post.json` tracks the last
processed date so the same day is never published twice.

## Architecture

Telegram's raw user-login protocol (MTProto/Telethon) gets blocked/throttled
from cloud IPs like GitHub Actions runners, which is why this uses the
**Telegram Bot API** instead (plain HTTPS - works fine from GitHub Actions):

1. **`src/bot_collect.py`** — a Telegram bot (must be an admin of the
   channel) polls for new channel posts every 15 minutes via GitHub Actions
   and appends them to `data/messages.jsonl` (a simple git-committed log,
   since the Bot API has no "channel history" endpoint - only new posts as
   they happen).
2. **`src/select_post.py`** — once a day, Claude picks the most
   meaningful post from yesterday's collected messages and translates it
   into a polished English LinkedIn post. Without `ANTHROPIC_API_KEY` it
   falls back to just picking the longest post, untranslated.
3. **`src/media.py`** — if the chosen post has a photo, downloads it via the
   Bot API and saves it to `docs/images/<message_id>.jpg` so it can be
   served publicly and attached to the RSS item.
4. **`src/rss_feed.py`** — appends the chosen post (and image, if any) to
   `docs/history.json` and regenerates `docs/feed.xml` (RSS 2.0, last
   `FEED_MAX_ITEMS` entries, image as an `<enclosure>`).
5. **`src/state.py`** — records the last processed date in
   `state/last_post.json` so a day is never published twice.

Two GitHub Actions workflows run this automatically:
- `.github/workflows/collect-messages.yml` — every 15 minutes, runs the
  collector.
- `.github/workflows/daily-linkedin-post.yml` — once a day at 11:00
  Asia/Tashkent, picks yesterday's best post and updates the RSS feed.

## Setup

### 1. Telegram bot

1. You already have a bot (e.g. via @BotFather) and its token.
2. Add the bot as an **administrator** of `@mutolaaxona` (Settings →
   Administrators → Add Admin in the channel). This is required - the Bot
   API only delivers channel posts to bots that are channel admins.
3. Save the bot's token as the `TELEGRAM_BOT_TOKEN` GitHub secret (below).

### 2. Anthropic API key (for English translation + selection)

Get one at https://console.anthropic.com → API Keys → Create Key, and save
it as the `ANTHROPIC_API_KEY` GitHub secret. Without it, the daily post
falls back to the original Uzbek text, untranslated - so this key is
effectively required for the "post in English" behavior.

### 3. Enable GitHub Pages

1. Repo → **Settings → Pages**.
2. **Source**: "Deploy from a branch", **Branch**: your default branch /
   **`/docs`**, **Save**.
3. After a couple of minutes your Pages URL appears, e.g.
   `https://sirojiddinolimov.github.io/linkedin-post/`. The feed itself is
   that URL + `feed.xml`.

### 4. GitHub secrets & variables

**Settings → Secrets and variables → Actions → Secrets:**

- `TELEGRAM_BOT_TOKEN`
- `ANTHROPIC_API_KEY`

**Settings → Secrets and variables → Actions → Variables:**

- `FEED_BASE_URL` = your GitHub Pages URL from step 3
- `TELEGRAM_CHANNEL` = `mutolaaxona` (optional, this is the default)
- `POST_TIMEZONE` = `Asia/Tashkent` (optional, this is the default)
- `FEED_TITLE` = `Mutolaa | Daily pick` (optional)

### 5. Test it

1. **Actions → Collect Telegram channel posts → Run workflow.** Check the
   log; it should say `Collected N new post(s)`. If `N` stays 0 even after
   the channel has posted recently, double check the bot is really an admin
   of the channel.
2. Wait for at least one day's worth of posts to accumulate (or run the
   collector a few times across a day), then run **Actions → Daily digest
   -> RSS feed for LinkedIn → Run workflow** with `dry_run: true` to see the
   picked/translated post in the log without publishing it. Run again with
   `dry_run: false` to actually update `docs/feed.xml`.

### 6. Connect LinkedIn to the RSS feed

1. Go to https://www.linkedin.com/company/102440497/admin/settings/manage-content/
   as a Mutolaa admin.
2. Click **Add source**.
3. Enter the feed URL: `https://sirojiddinolimov.github.io/linkedin-post/feed.xml`
4. Follow LinkedIn's prompts - once approved, LinkedIn publishes a post
   whenever a new item appears in the feed (once a day, when the daily
   workflow runs).

From then on it's fully automatic: bot collects posts → daily workflow
picks + translates the best one → `docs/feed.xml` updates → GitHub Pages
serves it → LinkedIn picks it up from the RSS source and posts it.

**About images:** when the chosen Telegram post has a photo, it's included
in the RSS item as an `<enclosure>`. Whether LinkedIn's RSS source actually
attaches that image to the published post is up to LinkedIn's own feature
(not something this repo controls) - it's best-effort, not guaranteed.

## Local testing

```bash
cp .env.example .env
# fill in TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, FEED_BASE_URL
export $(grep -v '^#' .env | xargs)
cd src
python bot_collect.py        # collect any new posts
DRY_RUN=true python main.py  # preview the daily pick without publishing
```
