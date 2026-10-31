# Pollinations Hermes provider

Registers [Pollinations](https://gen.pollinations.ai) as a named Hermes provider
without changing your default model or spending Pollen.

## What it does

- Installs the bundled `pollinations` model-provider plugin under your Hermes home.
- Adds a `providers.pollinations` entry using the live model catalog.
- Leaves `model.provider` and `model.default` untouched.
- Does not write an API key or send a completion.

## Quick start

```bash
python3 scripts/add_pollinations.py --apply
```

The script probes `https://gen.pollinations.ai/v1/models` (no key required),
picks a capable default model, copies the plugin, and runs `hermes config set`.

## Add your key

Get a secret key at https://enter.pollinations.ai/keys, then set it in your
environment:

```bash
export HERMES_CUSTOM_POLLINATIONS_API_KEY="sk_..."
```

Never paste the key into chat.

## Why not the Pollinations CLI harness?

`polli harness hermes on` switches your default model onto Pollinations
(`openai/gpt-6-sol`) and mints a dedicated key. This provider leaves your
default model alone and only adds Pollinations to the provider list.

## Files

- `SKILL.md` — skill manifest
- `scripts/add_pollinations.py` — installer
- `plugins/model-providers/pollinations/` — model-provider plugin

## License

MIT
