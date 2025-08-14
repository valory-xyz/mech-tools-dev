import json
from pathlib import Path
from operate.cli import OperateApp, run_service

CURR_DIR = Path(__file__).resolve().parent
BASE_DIR = CURR_DIR.parent
GNOSIS_TEMPLATE_CONFIG_PATH = BASE_DIR / "config" / "config_mech_gnosis.json"
OPERATE_DIR = BASE_DIR / ".operate"
OPERATE_CONFIG_PATH = "services/sc-*/config.json"


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


if __name__ == "__main__":
    main()
