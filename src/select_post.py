from config import Config
from telegram_fetch import ChannelPost


def _heuristic_score(post: ChannelPost) -> float:
    length_score = min(len(post.text), 1200) / 1200
    engagement = post.views * 0.01 + post.forwards * 2 + post.reactions * 3
    return engagement + length_score * 5


def pick_best_heuristic(posts: list[ChannelPost]) -> ChannelPost:
    return max(posts, key=_heuristic_score)


def pick_and_polish_with_claude(posts: list[ChannelPost], config: Config) -> tuple[ChannelPost, str]:
    """Ask Claude to choose the most important/meaningful post and turn it into
    a polished LinkedIn company-page post. Falls back to the heuristic pick's
    raw text if the model call fails."""
    import anthropic

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    numbered = "\n\n".join(
        f"[{i}] (views={p.views}, forwards={p.forwards}, reactions={p.reactions})\n{p.text}"
        for i, p in enumerate(posts)
    )

    prompt = (
        "Quyida @{channel} Telegram kanalidagi kechagi barcha postlar keltirilgan. "
        "Ulardan ENG MUHIM va ENG MA'NOLISINI tanlang (mazmuni chuqur, o'quvchiga foydali, "
        "kitobxonlik/bilim mavzusida eng qimmatlisi bo'lsin; faqat ko'p ko'rilgani emas, "
        "mazmuniga qarab tanlang).\n\n"
        "Keyin uni Mutolaa kompaniyasining LinkedIn sahifasi uchun professional, ixcham "
        "postga aylantiring: asl fikr va ma'noni saqlang, o'zbek tilida yozing, ortiqcha "
        "emoji ishlatmang, oxiriga 3-5 ta mos hashtag qo'shing (masalan #Mutolaa #Kitob "
        "#Kitobxonlik kabi, mavzuga mos ravishda).\n\n"
        "Javobni FAQAT quyidagi formatda bering, boshqa hech narsa yozmang:\n"
        "INDEX: <tanlangan post raqami>\n"
        "POST:\n<linkedin posti matni>\n\n"
        f"Postlar:\n\n{numbered}"
    ).format(channel="mutolaaxona")

    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()

    index = None
    post_text_lines: list[str] = []
    in_post = False
    for line in raw.splitlines():
        if line.startswith("INDEX:"):
            index = int(line.split(":", 1)[1].strip())
        elif line.startswith("POST:"):
            in_post = True
        elif in_post:
            post_text_lines.append(line)

    if index is None or not (0 <= index < len(posts)) or not post_text_lines:
        raise ValueError(f"Unexpected Claude response format: {raw!r}")

    polished_text = "\n".join(post_text_lines).strip()
    return posts[index], polished_text


def select_daily_post(posts: list[ChannelPost], config: Config) -> tuple[ChannelPost, str]:
    if config.anthropic_api_key:
        try:
            return pick_and_polish_with_claude(posts, config)
        except Exception as exc:  # noqa: BLE001
            print(f"Claude selection failed ({exc}); falling back to heuristic pick.")

    chosen = pick_best_heuristic(posts)
    return chosen, chosen.text
