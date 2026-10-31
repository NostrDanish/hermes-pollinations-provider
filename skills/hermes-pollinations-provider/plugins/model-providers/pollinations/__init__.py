"""Pollinations provider (OpenAI-compatible, secret key, spends Pollen).

Base URL is the public gen gateway. Model listing works without a key.
A chat completion spends Pollen (Quest or paid). Do not send one to
"see if it works." Override the endpoint with ``POLLINATIONS_BASE_URL``.
"""

from __future__ import annotations

from providers import register_provider
from providers.base import ProviderProfile

_DEFAULT_BASE = "https://gen.pollinations.ai/v1"


pollinations = ProviderProfile(
    name="pollinations",
    aliases=("pollinations-ai", "gen-pollinations"),
    display_name="Pollinations",
    description="Pollinations — OpenAI-compatible text and media (spends Pollen)",
    signup_url="https://enter.pollinations.ai/keys",
    # Desktop custom-endpoint saves use HERMES_CUSTOM_POLLINATIONS_API_KEY.
    # POLLINATIONS_API_KEY is the docs name. POLLI_HERMES_API_KEY is what
    # `polli harness hermes` writes. Last entry is the base-URL override.
    env_vars=(
        "HERMES_CUSTOM_POLLINATIONS_API_KEY",
        "POLLINATIONS_API_KEY",
        "POLLI_HERMES_API_KEY",
        "POLLINATIONS_BASE_URL",
    ),
    base_url=_DEFAULT_BASE,
    auth_type="api_key",
    api_mode="chat_completions",
    aggregator=True,
    supports_vision=True,
    default_aux_model="openai/gpt-5.4-nano",
    default_headers={"User-Agent": "pollinations-hermes-plugin/0.1.0"},
    # Cheap tool-calling text ids first. Live GET /v1/models replaces this
    # list when it succeeds. Image/video/audio ids are not chat models.
    fallback_models=(
        "openai/gpt-5.4-nano",
        "openai/gpt-5-nano",
        "deepseek/deepseek-v4-flash",
        "google/gemini-2.5-flash-lite",
        "openai/gpt-oss-20b",
        "openai/gpt-4o-mini",
    ),
)

register_provider(pollinations)
