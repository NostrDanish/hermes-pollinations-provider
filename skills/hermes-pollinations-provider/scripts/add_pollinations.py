#!/usr/bin/env python3
"""Register Pollinations in Hermes providers: so the Desktop list shows it.

Probes /v1/models, copies the bundled model-provider plugin into
$HERMES_HOME/plugins/model-providers/pollinations, then writes
providers.pollinations.* via `hermes config set`.

Does not change model.provider or model.default, does not write a key, and
does not send a completion (that spends Pollen).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROVIDER = "pollinations"
DEFAULT_BASE = "https://gen.pollinations.ai/v1"
PREFERRED_MODELS = (
    "openai/gpt-5.4-nano",
    "openai/gpt-5-nano",
    "deepseek/deepseek-v4-flash",
    "google/gemini-2.5-flash-lite",
    "openai/gpt-oss-20b",
    "openai/gpt-4o-mini",
)
USER_AGENT = "hermes-pollinations-provider/0.1"


def key_env_for(identity: str) -> str:
    """Match Hermes custom_endpoint_key_env: HERMES_CUSTOM_<SLUG>_API_KEY."""
    slug = re.sub(r"[^A-Z0-9]+", "_", str(identity or "").upper()).strip("_")
    return f"HERMES_CUSTOM_{slug}_API_KEY" if slug else "HERMES_CUSTOM_API_KEY"


def models_url(base_url: str) -> str:
    base = base_url.strip().rstrip("/")
    if base.endswith("/v1"):
        return base + "/models"
    return base + "/v1/models"


def parse_model_ids(payload: object) -> list[str]:
    if isinstance(payload, dict):
        items = payload.get("data")
    elif isinstance(payload, list):
        items = payload
    else:
        return []
    if not isinstance(items, list):
        return []
    ids: list[str] = []
    for item in items:
        if isinstance(item, dict) and item.get("id"):
            ids.append(str(item["id"]))
        elif isinstance(item, str) and item.strip():
            ids.append(item.strip())
    return ids


def pick_model(ids: list[str], override: str | None = None) -> str:
    if override:
        return override.strip()
    have = set(ids)
    for preferred in PREFERRED_MODELS:
        if preferred in have:
            return preferred
    return ids[0] if ids else ""


def probe(base_url: str, timeout: float = 12.0) -> list[str] | None:
    """Return model ids on HTTP 200 JSON, else None. Never sends a completion."""
    url = models_url(base_url)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            body = resp.read()
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    ids = parse_model_ids(payload)
    return ids or None


def choose_endpoint(candidates: list[str]) -> tuple[str, list[str]]:
    errors: list[str] = []
    for base in candidates:
        ids = probe(base)
        if ids:
            return base.rstrip("/"), ids
        errors.append(f"{base}: no public /v1/models")
    raise SystemExit("no live Pollinations catalog\n" + "\n".join(errors))


def hermes_bin() -> str:
    found = shutil.which("hermes")
    if not found:
        raise SystemExit("hermes not on PATH")
    return found


def hermes_env(home: str | None) -> dict[str, str]:
    env = os.environ.copy()
    if home:
        env["HERMES_HOME"] = home
    return env


def hermes_get(key: str, env: dict[str, str], *, as_json: bool = False) -> str:
    cmd = [hermes_bin(), "config", "get", key]
    if as_json:
        cmd.append("--json")
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise SystemExit(f"hermes config get {key} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def hermes_set(key: str, value: str, env: dict[str, str]) -> None:
    proc = subprocess.run(
        [hermes_bin(), "config", "set", key, value],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise SystemExit(f"hermes config set {key} failed: {proc.stderr.strip() or proc.stdout.strip()}")


def snapshot_defaults(env: dict[str, str]) -> tuple[str, str]:
    return hermes_get("model.provider", env), hermes_get("model.default", env)


def install_plugin(home: str | None) -> Path:
    """Copy the bundled model-provider plugin into $HERMES_HOME/plugins/model-providers/pollinations."""
    script_dir = Path(__file__).resolve().parent
    plugin_src = script_dir.parent / "plugins" / "model-providers" / PROVIDER
    if not plugin_src.exists():
        raise SystemExit(f"bundled plugin not found at {plugin_src}")
    target_home = Path(home).expanduser().resolve() if home else Path.home() / ".hermes"
    target = target_home / "plugins" / "model-providers" / PROVIDER
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(plugin_src, target)
    return target


def apply_entry(base_url: str, model: str, env: dict[str, str]) -> None:
    key_env = key_env_for(PROVIDER)
    fields = {
        f"providers.{PROVIDER}.name": PROVIDER,
        f"providers.{PROVIDER}.base_url": base_url,
        f"providers.{PROVIDER}.model": model,
        f"providers.{PROVIDER}.discover_models": "true",
        f"providers.{PROVIDER}.api_mode": "chat_completions",
        f"providers.{PROVIDER}.key_env": key_env,
    }
    for key, value in fields.items():
        hermes_set(key, value, env)


def verify(base_url: str, model: str, before: tuple[str, str], env: dict[str, str]) -> dict:
    raw = hermes_get(f"providers.{PROVIDER}", env, as_json=True)
    entry = json.loads(raw)
    expected = {
        "name": PROVIDER,
        "base_url": base_url,
        "model": model,
        "api_mode": "chat_completions",
        "key_env": key_env_for(PROVIDER),
    }
    mismatches = [k for k, v in expected.items() if entry.get(k) != v]
    if entry.get("discover_models") is not True:
        mismatches.append("discover_models")
    after = snapshot_defaults(env)
    if after != before:
        raise SystemExit(f"default model changed: {before} -> {after}")
    if mismatches:
        raise SystemExit(f"readback mismatch: {mismatches} entry={entry}")
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Add Pollinations to the Hermes provider list.")
    parser.add_argument("--apply", action="store_true", help="Write providers.pollinations and install the plugin.")
    parser.add_argument("--base-url", default="", help="Force this endpoint. Still probed. No write if probe fails.")
    parser.add_argument("--model", default="", help="Provider-row default model. Must be in live catalog unless --allow-missing-model.")
    parser.add_argument("--allow-missing-model", action="store_true")
    parser.add_argument("--home", default="", help="HERMES_HOME for this run. Does not change the process default.")
    args = parser.parse_args(argv)

    candidates = [args.base_url.strip()] if args.base_url.strip() else [DEFAULT_BASE]
    base_url, ids = choose_endpoint(candidates)
    model = pick_model(ids, args.model or None)
    if args.model and model not in ids and not args.allow_missing_model:
        raise SystemExit(f"model {model!r} is not in the live catalog")
    if not model:
        raise SystemExit("catalog returned no model id")

    print(f"node {base_url}")
    print(f"model {model}")
    print(f"catalog {len(ids)}")
    print(f"key_env {key_env_for(PROVIDER)}")
    if not args.apply:
        print("dry-run (pass --apply to write providers.pollinations and install plugin)")
        return 0

    env = hermes_env(args.home.strip() or None)
    plugin_dir = install_plugin(args.home.strip() or None)
    print(f"plugin {plugin_dir}")
    before = snapshot_defaults(env)
    apply_entry(base_url, model, env)
    entry = verify(base_url, model, before, env)
    print("verified")
    print(json.dumps({"providers.pollinations": entry, "model.provider": before[0], "model.default": before[1]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
