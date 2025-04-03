<p align="center">
   <img src="./docs/images/mechs-logo.png" width=300>
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

## Set up your environment

Follow these instructions to have your local environment prepared to run the demo below, as well as to build your own AI Mech.

1. Create a Poetry virtual environment and install the dependencies:

    ```bash
    poetry install && poetry shell
    ```

2. Fetch the software packages using the [Open Autonomy](https://docs.autonolas.network/open-autonomy/) CLI:

    ```bash
    autonomy packages sync --update-packages
    ```

    This will populate the Open Autonomy [local registry](https://docs.autonolas.network/open-autonomy/guides/set_up/#the-registries-and-runtime-folders) (folder `./packages`) with the required components to run the worker services.

## Instructions

In order to develop your own mech, simply fork this repository and start adding your tools.
You can find more information on how to create, publish, and run your own mech tools in 
[our documentation](https://docs.olas.network/mech-tool/).
