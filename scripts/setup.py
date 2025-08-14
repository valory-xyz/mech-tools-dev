import json
from pathlib import Path
from operate.cli import OperateApp, run_service

CURR_DIR = Path(__file__).resolve().parent
BASE_DIR = CURR_DIR.parent
GNOSIS_TEMPLATE_CONFIG_PATH = BASE_DIR / "config" / "config_mech_gnosis.json"
OPERATE_DIR = BASE_DIR / ".operate"
OPERATE_CONFIG_PATH = "services/sc-*/config.json"
AGENT_KEY = "ethereum_private_key.txt"
SERVICE_KEY = "keys.json"


def read_and_update_env(data: dict) -> None:
    with open(".example.env", "r") as f:
        lines = f.readlines()

    filled_lines = []
    for line in lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            value = data["env_variables"].get(key, {}).get("value", "")
            filled_lines.append(f"{key}={value!r}\n")
        else:
            filled_lines.append(line)

    with open(".1env", "w") as f:
        f.writelines(filled_lines)


def setup_env() -> None:
    matching_paths = OPERATE_DIR.glob(OPERATE_CONFIG_PATH)
    data = {}
    for file_path in matching_paths:
        print(f"Reading from: {file_path}")
        with open(file_path, "r") as f:
            content = f.read()
            data = json.loads(content)

    read_and_update_env(data)
    return


def create_private_key_files(data: dict) -> None:
    agent_key_path = BASE_DIR / AGENT_KEY
    if agent_key_path.exists():
        print(f"Agent key found at: {agent_key_path}. Skipping creation")
    else:
        agent_key_path.write_text(data["private_key"])

    service_key_path = BASE_DIR / SERVICE_KEY
    if service_key_path.exists():
        print(f"Service key found at: {service_key_path}. Skipping creation")
    else:
        service_key_path.write_text(json.dumps([data], indent=2))

    return


def setup_private_keys() -> None:
    keys_dir = OPERATE_DIR / "keys"
    if keys_dir.is_dir():
        key_file = next(keys_dir.glob("*"), None)
        if key_file and key_file.is_file():
            print(f"Key file found at: {key_file}")
            with open(key_file, "r") as f:
                content = f.read()
                data = json.loads(content)

        create_private_key_files(data)

    return


def setup_operate() -> None:
    operate = OperateApp()
    operate.setup()

    run_service(
        operate=operate,
        config_path=GNOSIS_TEMPLATE_CONFIG_PATH,
        build_only=True,
        skip_dependency_check=False,
    )


def main() -> None:
    if not OPERATE_DIR.is_dir():
        print("Setting up operate...")
        setup_operate()

    print("Setting up env...")
    setup_env()

    print("Setting up private keys...")
    setup_private_keys()


if __name__ == "__main__":
    main()
