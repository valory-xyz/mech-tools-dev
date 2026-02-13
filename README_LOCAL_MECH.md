# Local Mech Setup and Tooling Guide

This guide explains how to set up and run a Mech locally with `mech-tools-dev`, add tools, configure API keys, and deploy as a service.

## 1. Setup of a local Mech (from `mech-tools-dev`)

1. Clone and enter the repo:

```bash
git clone https://github.com/valory-xyz/mech-tools-dev.git
cd mech-tools-dev
```

2. Install dependencies:

```bash
poetry shell
poetry install
autonomy packages sync --update-packages
```

3. Run initial setup (creates/updates `.env`, keys, and local operate config):

```bash
python utils/setup.py
```

4. Make sure `.env` has the required values (at least these):

- `ON_CHAIN_SERVICE_ID`
- `NUM_AGENTS`
- `ALL_PARTICIPANTS`
- `SAFE_CONTRACT_ADDRESS`
- `GNOSIS_LEDGER_RPC_0`
- `GNOSIS_LEDGER_CHAIN_ID`
- `MECH_TO_CONFIG`
- `MECH_MARKETPLACE_ADDRESS`
- `CHECKPOINT_ADDRESS`
- `COMPLEMENTARY_SERVICE_METADATA_ADDRESS`
- `SERVICE_REGISTRY_ADDRESS`

## 2. Adding tools (package hashes) and what is supported

`TOOLS_TO_PACKAGE_HASH` in `.env` is the runtime mapping used by the agent.

This section documents only the `*_latest_request` tools, how to call them, current hashes, and API keys.

### Package Hashes (Current)

- `custom/valory/openai_latest_request/0.1.0`: `bafybeidpetruoohs22tdkt24nkplcuiao7imqir3gb2zhynv5nbkmiy77i`
- `custom/valory/gemini_latest_request/0.1.0`: `bafybeiak7gcpp3iowsas3sizts7g6c57d43gvwhn5xnujfytkfeowrtwsm`
- `custom/valory/anthropic_latest_request/0.1.0`: `bafybeihrrszk6spwfptpcwnxoosoatq44iwhb6dir75ihbbmwcvy6hkhw4`

### Add these packages and sync

Add these entries to `packages/packages.json` under `third_party`:

```json
"custom/valory/anthropic_latest_request/0.1.0": "bafybeihrrszk6spwfptpcwnxoosoatq44iwhb6dir75ihbbmwcvy6hkhw4",
"custom/valory/gemini_latest_request/0.1.0": "bafybeiak7gcpp3iowsas3sizts7g6c57d43gvwhn5xnujfytkfeowrtwsm",
"custom/valory/openai_latest_request/0.1.0": "bafybeidpetruoohs22tdkt24nkplcuiao7imqir3gb2zhynv5nbkmiy77i"
```

Then run:

```bash
autonomy packages sync --update-packages
```

Tool source code references:

- `gemini_latest_request`: https://github.com/valory-xyz/mech-predict/tree/feat/add-anthropic-tool/packages/valory/customs/gemini_latest_request
- `anthropic_latest_request`: https://github.com/valory-xyz/mech-predict/tree/feat/add-anthropic-tool/packages/valory/customs/anthropic_latest_request
- `openai_latest_request`: https://github.com/valory-xyz/mech-predict/tree/feat/add-anthropic-tool/packages/valory/customs/openai_latest_request

### `TOOLS_TO_PACKAGE_HASH` (Copy/Paste)

```bash
TOOLS_TO_PACKAGE_HASH='{
  "openai-gpt-5.2-chat-latest": "bafybeidpetruoohs22tdkt24nkplcuiao7imqir3gb2zhynv5nbkmiy77i",
  "gemini-2.5-flash": "bafybeiak7gcpp3iowsas3sizts7g6c57d43gvwhn5xnujfytkfeowrtwsm",
  "anthropic-claude-opus-4-5-latest": "bafybeihrrszk6spwfptpcwnxoosoatq44iwhb6dir75ihbbmwcvy6hkhw4"
}'
```

### Model Name Format (Explicit)

These tools are dynamic wrappers. They do not keep a hardcoded allow-list of models; they route by prefix + model id.

- OpenAI tool format: `openai-<openai_model_id>`
- Gemini tool format: `gemini-<gemini_model_id>`
- Anthropic tool format: `anthropic-<anthropic_model_id>`

Examples:

- OpenAI valid: `openai-gpt-5.2-chat-latest`
- OpenAI valid: `openai-gpt-4.1-2025-04-14`
- OpenAI invalid: `gpt-5.2-chat-latest` (missing `openai-` prefix)
- Gemini valid: `gemini-2.5-flash`
- Gemini valid: `gemini-2.5-pro`
- Gemini invalid: `google-gemini-2.5-flash` (wrong prefix)
- Anthropic valid: `anthropic-claude-opus-4-5-latest`
- Anthropic valid: `anthropic-claude-4-sonnet-latest`
- Anthropic invalid: `claude-opus-4-5-latest` (missing `anthropic-` prefix)

Notes:

- The model id is everything after the prefix. Example: in `openai-gpt-5.2-chat-latest`, model id is `gpt-5.2-chat-latest`.
- If a model id is invalid or deprecated, provider API returns an error.
- You can also pass `"model": "<provider_model_id>"` in payload; if provided, it overrides model parsed from `tool`.

### Known Working Examples

Use these as safe starting points in requests:

- OpenAI: `openai-gpt-5.2-chat-latest`
- Gemini: `gemini-2.5-flash`
- Anthropic: `anthropic-claude-opus-4-5-latest`

### How To Call

1) `valory/openai_latest_request`
- Tool prefix: `openai-`
- Dynamic model wrapper (simple prompt -> OpenAI response).

Example request payload:

```json
{
  "tool": "openai-gpt-5.2-chat-latest",
  "prompt": "Give me a 3-point thesis."
}
```

2) `valory/gemini_latest_request`
- Tool prefix: `gemini-`
- Dynamic model wrapper (simple prompt -> Gemini response).

Example request payload:

```json
{
  "tool": "gemini-2.5-flash",
  "prompt": "Extract key risks from this statement."
}
```

3) `valory/anthropic_latest_request`
- Tool prefix: `anthropic-`
- Dynamic model wrapper (simple prompt -> Anthropic response).

Example request payload:

```json
{
  "tool": "anthropic-claude-opus-4-5-latest",
  "prompt": "Estimate probability and explain briefly."
}
```

### Required dependency wiring (`component.yaml` and `aea-config.yaml`)

If you use the `*_latest_request` tools, declare these pinned libraries in both files:

- `openai==1.93.0`
- `google-generativeai==0.6.0`
- `anthropic==0.23.1`

1. Tool component file:
- `packages/<author>/customs/<tool_name>/component.yaml`
- Add under `dependencies`:

```yaml
dependencies:
  openai:
    version: ==1.93.0
  google-generativeai:
    version: ==0.6.0
  anthropic:
    version: ==0.23.1
```

2. Agent package config:
- `packages/valory/agents/mech/aea-config.yaml`
- Add the same pinned libraries under top-level `dependencies`:

```yaml
dependencies:
  openai:
    version: ==1.93.0
  google-generativeai:
    version: ==0.6.0
  anthropic:
    version: ==0.23.1
```

Why both:
- `component.yaml` keeps tool package dependencies explicit and reproducible.
- `aea-config.yaml` ensures the fetched/running agent environment includes those libraries.

If you skip this, you can hit runtime errors like `No module named '<library>'`.

### Update flow after changing tools

1. Add these fixed tool hashes to `packages/packages.json` under `third_party`:

```json
"custom/valory/anthropic_latest_request/0.1.0": "bafybeihrrszk6spwfptpcwnxoosoatq44iwhb6dir75ihbbmwcvy6hkhw4",
"custom/valory/gemini_latest_request/0.1.0": "bafybeiak7gcpp3iowsas3sizts7g6c57d43gvwhn5xnujfytkfeowrtwsm",
"custom/valory/openai_latest_request/0.1.0": "bafybeidpetruoohs22tdkt24nkplcuiao7imqir3gb2zhynv5nbkmiy77i"
```

2. Download/sync those packages locally:

```bash
autonomy packages sync --update-packages
```

3. Republish metadata and update on-chain metadata hash:

```bash
python utils/generate_metadata.py
python utils/publish_metadata.py
python utils/update_metadata.py
```

It will look like this (example only, not a real hash):

```bash
(mech-tools-dev-py3.11) user@host mech-tools-dev % python utils/publish_metadata.py
Metadata successfully pushed to ipfs. The metadata hash is: f01701220aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Copy the hash shown after `The metadata hash is:` and paste it into `.env` as `METADATA_HASH`.

4. Update `.env`:
- `TOOLS_TO_PACKAGE_HASH` with package hashes from `packages/packages.json`.
- `METADATA_HASH` with the hash printed by `utils/publish_metadata.py` (copy this value manually).

### If you edit `TOOLS_TO_PACKAGE_HASH` again later

Repeat this checklist:

1. Re-run `autonomy packages lock` after any tool code/config/dependency change.
2. Update `.env` `TOOLS_TO_PACKAGE_HASH` from the latest `packages/packages.json`.
3. If tool metadata changed (tool names/descriptions/available tools), re-run:
   - `python utils/generate_metadata.py`
   - `python utils/publish_metadata.py`
   - copy the printed hash manually and set new `METADATA_HASH` in `.env`
   - `python utils/update_metadata.py`
4. Restart your running mech:
   - local run: stop and re-run `./run_agent.sh`
   - docker run: re-run `./run_service.sh`

If you only changed `.env` key values (no package or metadata change), a restart is still required for changes to take effect.

## 3. Adding API keys

`API_KEYS` in `.env` must be a JSON object where each key maps to a list of values:

```bash
API_KEYS='{"service_name":["key1","key2"]}'
```

Example:

```bash
API_KEYS='{
  "openai": ["YOUR_OPENAI_KEY"],
  "anthropic": ["YOUR_ANTHROPIC_KEY"],
  "gemini": ["YOUR_GEMINI_KEY"]
}'
```

Notes:

- Keep the value as a single-quoted JSON string in `.env`.
- Use list values so keys can be rotated.
- Service names depend on the tools you run. If a tool expects a missing service name, execution fails with `Service '<name>' not found in KeyChain`.

API keys:

- `valory/openai_latest_request`: `api_keys["openai"]`
- `valory/gemini_latest_request`: `api_keys["gemini"]`
- `valory/anthropic_latest_request`: `api_keys["anthropic"]`

## 4. Deploying service

Deploy the full dockerized service:

```bash
./run_service.sh
```

What this does:

- Cleans prior local mech build artifacts.
- Pushes packages (`autonomy push-all`).
- Fetches `valory/mech` service locally.
- Builds image and deployment bundle.
- Runs deployment detached with Docker.

Stop the deployed service:

```bash
./stop_service.sh
```

## 5. Steps to run local Mech

For local debugging (non-docker, single process):

```bash
./run_agent.sh
```

This starts Tendermint and runs the agent locally.

To test the mech from another terminal:

```bash
source .env
poetry run mechx request --prompts "hello, mech!" --priority-mech <your_mech_address> --tools <your_tool_name> --chain-config gnosis
```

`<your_mech_address>` should match the address in `MECH_TO_CONFIG`.
