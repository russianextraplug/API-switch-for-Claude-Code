
import os
import json
import subprocess
import shutil
import getpass
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "providers": {
        "Anthropic": {
            "type": "official"
        },
        "DeepSeek": {
            "base_url": "https://api.deepseek.com/anthropic",
            "model": "deepseek-chat",
            "api_key": ""
        }
    }
}


def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("=" * 45)
    print("          CLAUDE CODE LAUNCHER")
    print("=" * 45)


def select_provider(config):
    providers = config["providers"]

    print("\nAVAILABLE API PROVIDERS\n")

    names = list(providers.keys())

    for i, name in enumerate(names, 1):
        print(f"[{i}] {name}")

    print(f"[{len(names) + 1}] Add custom API")

    choice = input("\nSelect provider: ").strip()

    if not choice.isdigit():
        return None

    choice = int(choice)

    if choice == len(names) + 1:
        return add_custom_provider(config)

    if 1 <= choice <= len(names):
        return names[choice - 1]

    return None


def add_custom_provider(config):
    print("\nADD CUSTOM API\n")

    name = input("Provider name: ").strip()
    if not name:
        return None

    base_url = input("API Base URL: ").strip()
    model = input("Model ID: ").strip()
    api_key = getpass.getpass("API Key: ")

    if not base_url or not model or not api_key:
        print("All fields are required.")
        input("Press Enter...")
        return None

    config["providers"][name] = {
        "base_url": base_url,
        "model": model,
        "api_key": api_key
    }

    save_config(config)

    return name


def get_project():
    print("\nPROJECT DIRECTORY\n")

    path = input("Enter project path: ").strip().strip('"')
    project = Path(path).expanduser()

    if not project.exists() or not project.is_dir():
        print("Invalid project directory.")
        return None

    return project.resolve()


def launch_claude(provider_name, config, project):
    provider = config["providers"][provider_name]

    claude_path = shutil.which("claude")

    if not claude_path:
        print("\nClaude Code was not found in PATH.")
        print("Install Claude Code first.")
        return

    env = os.environ.copy()

    variables = [
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "CLAUDE_CODE_SUBAGENT_MODEL"
    ]

    for variable in variables:
        env.pop(variable, None)

    if provider.get("type") == "official":
        print("\nUsing existing Anthropic authentication.")

    else:
        base_url = provider.get("base_url")
        model = provider.get("model")
        api_key = provider.get("api_key")

        if not api_key:
            api_key = getpass.getpass("Enter API Key: ")
            provider["api_key"] = api_key
            save_config(config)

        env["ANTHROPIC_BASE_URL"] = base_url
        env["ANTHROPIC_AUTH_TOKEN"] = api_key
        env["ANTHROPIC_MODEL"] = model

        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model

    print("\n" + "=" * 45)
    print("PROVIDER:", provider_name)
    print("MODEL:", provider.get("model", "Default"))
    print("PROJECT:", project)
    print("=" * 45)

    input("\nPress Enter to launch Claude Code...")

    try:
        subprocess.run(
            [claude_path],
            cwd=str(project),
            env=env,
            check=False
        )
    except KeyboardInterrupt:
        print("\nClaude Code interrupted.")
    except Exception as error:
        print(f"\nLaunch error: {error}")


def main():
    while True:
        clear_screen()
        banner()

        config = load_config()

        provider = select_provider(config)

        if provider is None:
            print("\nInvalid selection.")
            input("Press Enter...")
            continue

        project = get_project()

        if project is None:
            input("Press Enter...")
            continue

        launch_claude(provider, config, project)

        print("\nClaude Code closed.")
        again = input("Launch again? (y/n): ").lower()

        if again != "y":
            break


if __name__ == "__main__":
    main()
