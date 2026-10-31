---
name: hermes-pollinations-provider
description: Use when adding Pollinations. Register it in the list without switching the default model.
version: 0.1.0
author: NousResearch
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pollinations, hermes, provider, pollen]
---

# Hermes Pollinations Provider

Registers Pollinations (`gen.pollinations.ai`) as a named Hermes provider so it
shows in Desktop's provider list. Does not change the default model, write a
key, install the Polli CLI, or send a completion (that spends Pollen).

## When to Use

- The user wants Pollinations in the Hermes provider list.
- A Pollinations plugin was added and the picker still does not show it.

Don't use for: switching the default model onto Pollinations, minting a key,
installing the Polli CLI, or running the official `polli harness hermes on`
command (that sets `model.provider` and `model.default` to Pollinations).

## Prerequisites

- `hermes` on `PATH` (`hermes config set` / `hermes config get`).
- Network access to `https://gen.pollinations.ai/v1/models` (no key required).
- No API key. Keys stay in the user's own secret storage, never in `config.yaml`.

## Procedure

1. Run the bundled script. It probes `/v1/models`, copies the bundled
   model-provider plugin into `$HERMES_HOME/plugins/model-providers/pollinations`,
   then writes only `providers.pollinations.*` via `hermes config set`.

   `terminal(command="python3 scripts/add_pollinations.py --apply", workdir="<skill dir>", timeout=60)`

   Done when the script prints `verified` and exits 0.

2. Read back the entry and the untouched default.

   `terminal(command="hermes config get providers.pollinations --json && hermes config get model.provider && hermes config get model.default", timeout=20)`

   Done when `providers.pollinations.base_url` is the probed node, and
   `model.provider` / `model.default` match the values from before the apply.

3. Tell the user to reopen the provider picker. The key slot is
   `HERMES_CUSTOM_POLLINATIONS_API_KEY`. They add it themselves via
   `hermes auth add pollinations` or by exporting that variable in their shell.
   Do not ask them to paste an `sk_` key into chat.

## Pitfalls

- A model-provider plugin alone does not appear in Desktop's list. The list
  reads `providers:` in `config.yaml`. Add it with `hermes config set`.
- `https://gen.pollinations.ai/v1/models` requires no authentication. Do not
  point Hermes at a non-existent host; the script probes before writing.
- Keys are Pollinations-account-scoped. Use a secret key from
  https://enter.pollinations.ai/keys.
- Do not set `model.provider`, `model.default`, or a fallback. Pollinations
  spends Pollen per request.
- HTTP 402 after a key is added means the Pollen balance or key budget is
  empty, not a Hermes bug.
- Other profiles do not inherit this entry. Re-run with `HERMES_HOME` set to
  that profile's home.
- Reopen the picker if it was already open. The API reads config on each
  request; a cached panel will not.
- Do not run `polli harness hermes on` to finish setup. That command
  switches the default model onto Pollinations (`openai/gpt-6-sol`) and
  writes a key.

## Verification

- `hermes config get providers.pollinations --json` shows `name`, `base_url`,
  `model`, `discover_models: true`, `api_mode: chat_completions`, and
  `key_env: HERMES_CUSTOM_POLLINATIONS_API_KEY`.
- `model.provider` and `model.default` are unchanged.
- No key was written. `hermes auth status pollinations` may still say logged out.
- Do not send a chat completion to prove it.
