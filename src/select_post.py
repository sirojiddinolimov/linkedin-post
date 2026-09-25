from typing import TYPE_CHECKING

from config import Config

if TYPE_CHECKING:
    from messages_store import ChannelPost


def pick_best_heuristic(posts: "list[ChannelPost]") -> "ChannelPost":
    """Bot API channel posts carry no view/forward counts, so the fallback
    just favors the longest (likely most substantive) post."""
    return max(posts, key=lambda p: len(p.text))


def pick_and_translate_with_claude(
    posts: "list[ChannelPost]", config: Config
) -> "tuple[ChannelPost, str]":
    """Ask Claude to choose the most important/meaningful post and turn it into
    a polished, English LinkedIn company-page post."""
    import anthropic

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    numbered = "\n\n".join(f"[{i}]\n{p.text}" for i, p in enumerate(posts))

    prompt = (
        f"Below are posts from the @{config.telegram_channel} Telegram channel "
        "(Uzbek-language, about books/reading). Pick the ONE "
        "most important and meaningful post - the one with the deepest, most "
        "useful content for readers, not simply the longest.\n\n"
        "Then turn it into a polished, professional LinkedIn post for the "
        "Mutolaa company page, IN ENGLISH: translate the meaning faithfully "
        "(don't add facts that weren't there), keep it concise, no excessive "
        "emoji, and end with 3-5 relevant hashtags (e.g. #Mutolaa #Books "
        "#Reading, adapted to the topic).\n\n"
        "Reply in EXACTLY this format and nothing else:\n"
        "INDEX: <chosen post number>\n"
        "POST:\n<LinkedIn post text in English>\n\n"
        f"Posts:\n\n{numbered}"
    )

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

    translated_text = "\n".join(post_text_lines).strip()
    return posts[index], translated_text


def select_daily_post(posts: "list[ChannelPost]", config: Config) -> "tuple[ChannelPost, str]":
    if config.anthropic_api_key:
        try:
            return pick_and_translate_with_claude(posts, config)
        except Exception as exc:  # noqa: BLE001
            print(f"Claude selection failed ({exc}); falling back to heuristic pick.")

    chosen = pick_best_heuristic(posts)
    print("WARNING: no ANTHROPIC_API_KEY - publishing the original Uzbek text untranslated.")
    return chosen, chosen.text
