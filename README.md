# hermes-pollinations-provider

Hermes skill + model-provider plugin that registers [Pollinations](https://gen.pollinations.ai)
as a named provider without switching your default model.

## What it does

- Copies `plugins/model-providers/pollinations/` into `$HERMES_HOME/plugins/model-providers/pollinations/`
- Writes `providers.pollinations` in `config.yaml` via `hermes config set`
- Leaves `model.provider` and `model.default` untouched
- Does **not** write an API key or send a completion

## Install

```bash
hermes skills install NostrDanish/hermes-pollinations-provider
cd "$(hermes skills path hermes-pollinations-provider)"
python3 scripts/add_pollinations.py --apply
```

Or clone and run:

```bash
git clone https://github.com/NostrDanish/hermes-pollinations-provider.git
cd hermes-pollinations-provider
python3 scripts/add_pollinations.py --apply
```

## Add your key

Get a secret key at https://enter.pollinations.ai/keys, then either:

```bash
hermes auth add pollinations
```

or write it to `~/.hermes/.env` (mode 600):

```bash
HERMES_CUSTOM_POLLINATIONS_API_KEY="sk_..."
```

Never paste the key into chat.

## Why not `polli harness hermes on`?

The official Pollinations CLI harness switches `model.provider` and `model.default`
onto Pollinations (default `openai/gpt-6-sol`) and writes a dedicated key. This
skill keeps your existing default model and lets you choose Pollinations only
when you want it.

## License

MIT
