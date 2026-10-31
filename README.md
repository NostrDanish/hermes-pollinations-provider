# hermes-pollinations-provider

Hermes skill + model-provider plugin that registers [Pollinations](https://gen.pollinations.ai)
as a named provider without switching your default model.

## What it does

- Installs the bundled `pollinations` model-provider plugin under your Hermes home.
- Adds a `providers.pollinations` entry using the live model catalog.
- Leaves `model.provider` and `model.default` untouched.
- Does **not** write an API key or send a completion.

## Install

Add this repo as a skill tap, then install the skill:

```bash
hermes skills tap add NostrDanish/hermes-pollinations-provider
hermes skills install NostrDanish/hermes-pollinations-provider/skills/hermes-pollinations-provider --yes
cd "$HOME/.hermes/skills/hermes-pollinations-provider"
python3 scripts/add_pollinations.py --apply
```

Or clone and run directly:

```bash
git clone https://github.com/NostrDanish/hermes-pollinations-provider.git
cd hermes-pollinations-provider/skills/hermes-pollinations-provider
python3 scripts/add_pollinations.py --apply
```

## Add your key

Get a secret key at https://enter.pollinations.ai/keys, then set it in your
environment:

```bash
export HERMES_CUSTOM_POLLINATIONS_API_KEY="sk_..."
```

Never paste the key into chat.

## Why not `polli harness hermes on`?

The official Pollinations CLI harness switches `model.provider` and `model.default`
onto Pollinations (default `openai/gpt-6-sol`) and writes a dedicated key. This
skill keeps your existing default model and lets you choose Pollinations only
when you want it.

## Repo layout

```
.
├── LICENSE
├── README.md
└── skills/
    └── hermes-pollinations-provider/
        ├── SKILL.md
        ├── scripts/add_pollinations.py
        └── plugins/model-providers/pollinations/
```

The `skills/` layout is required for `hermes skills tap add`.

## License

MIT
