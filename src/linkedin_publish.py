import requests

from config import Config

LINKEDIN_API_VERSION = "202409"


def publish_post(text: str, config: Config) -> str:
    """Publish a text post to the LinkedIn organization page. Returns the post URN."""
    url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {config.linkedin_access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": LINKEDIN_API_VERSION,
    }
    payload = {
        "author": config.linkedin_org_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code >= 300:
        raise RuntimeError(
            f"LinkedIn API error {response.status_code}: {response.text}"
        )
    return response.headers.get("x-restli-id", "")
