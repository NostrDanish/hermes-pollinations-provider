# Pollinations provider plugin

OpenAI-compatible Pollinations gateway for Hermes. Does not mint a key,
does not change `model.default`, and does not send a completion.

## Endpoint

- Default: `https://gen.pollinations.ai/v1` (live catalog, no auth required for `/v1/models`)
- Override: `POLLINATIONS_BASE_URL`
- Auth: `HERMES_CUSTOM_POLLINATIONS_API_KEY` (Desktop slot), or `POLLINATIONS_API_KEY`, or `POLLI_HERMES_API_KEY`
- Keys: https://enter.pollinations.ai/keys (`sk_` secret key)

A request spends Pollen. Quest Pollen is a finite earned balance, not a free pool. HTTP 402 means the key budget or wallet is empty.

## Connect

```bash
# add the key yourself — do not paste it into chat
hermes auth add pollinations
# or write HERMES_CUSTOM_POLLINATIONS_API_KEY into ~/.hermes/.env (mode 600)

# optional, only for this session:
# hermes model    # pick provider pollinations
```

Do not run `polli harness hermes on` to "finish" this. That command registers a provider **and** sets `model.provider` / `model.default` to Pollinations (default `openai/gpt-6-sol`) and writes `POLLI_HERMES_API_KEY`. It spends Pollen on the next turn. This registration leaves the Nous default alone.

Other profiles do not see this plugin. Copy the directory into `~/.hermes/profiles/<name>/plugins/model-providers/pollinations/` only when that profile should use it.
