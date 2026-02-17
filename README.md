<p align="center">
   <img src="./docs/imgs/mechs-logo.png" width=300>
</p>

<h1 align="center" style="margin-bottom: 0;">
    Mech Tools Dev
    <br>
    <a href="https://github.com/valory-xyz/mech-tools-dev/blob/main/LICENSE">
        <img alt="License: Apache-2.0" src="https://img.shields.io/github/license/valory-xyz/mech-tools-dev">
    </a>
    <a href="https://github.com/valory-xyz/mech/releases/tag/v0.10.0">
        <img alt="Mech Core: Mech 0.10.0" src="https://img.shields.io/badge/Mech%20Core%20-0.10.0-blueviolet">
    </a>
</h1>

Development toolkit for the Mech ecosystem.
Provides the mech core logic, supporting easy tools integration, streamlining their development and testing.

## Requirements

You need the following requirements installed in your system:

- [Python](https://www.python.org/) (recommended `3.10`)
- [Poetry](https://python-poetry.org/docs/)
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Tendermint](https://docs.tendermint.com/v0.34/introduction/install.html) `==0.34.19`

## CLI

All mech service operations are available through the `mtd` CLI. Install the package and run `mtd --help` to see available commands.

### Commands

| Command | Description |
|---|---|
| `mtd setup -c <chain>` | Full first-time setup: operate build, env config, key setup, metadata generation, IPFS publish, and on-chain update |
| `mtd run -c <chain>` | Run the mech service via Docker deployment |
| `mtd run -c <chain> --dev` | Dev mode: push local packages to IPFS, then run via host deployment (no Docker) |
| `mtd stop -c <chain>` | Stop a running mech service |
| `mtd push-metadata` | Generate `metadata.json` from packages and publish to IPFS |
| `mtd update-metadata` | Update the metadata hash on-chain via Safe transaction |
| `mtd add-tool` | Scaffold a new mech tool (interactive) |

Supported chains: `gnosis`, `base`, `polygon`, `optimism`.

### Setup

Run the full setup flow for a new mech deployment:

```bash
mtd setup -c gnosis
```

This runs the following steps in order:

1. **Operate build** - Creates the service via olas-operate-middleware (skipped if service already exists)
2. **Env configuration** - Sets up the `.env` file with required variables
3. **Private key setup** - Configures operator and agent keys
4. **Metadata generation** - Generates `metadata.json` from package definitions
5. **IPFS publish** - Pushes metadata to IPFS
6. **On-chain update** - Updates the metadata hash on-chain via Safe transaction

### Running the service

**Production mode** (Docker deployment):

```bash
mtd run -c gnosis
```

**Dev mode** (host deployment, no Docker):

```bash
mtd run -c gnosis --dev
```

Dev mode pushes your local packages to IPFS, updates the config template with the new service hash, and runs the service directly on the host using `olas-operate-middleware` with `use_docker=False`.

### Stopping the service

```bash
mtd stop -c gnosis
```

### Metadata operations

Generate and publish metadata independently of the full setup:

```bash
# Generate metadata.json and publish to IPFS
mtd push-metadata

# Use a custom IPFS node
mtd push-metadata --ipfs-node /dns/custom.node/tcp/5001/http

# Update the on-chain metadata hash
mtd update-metadata
```

## Instructions

Find more information on how to create, publish, and run your own mech tools in
[our documentation](https://stack.olas.network).
