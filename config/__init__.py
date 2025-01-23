import os
import tomllib

__config_file = f"config.toml"

if os.getenv("dev"):
    __config_file = "dev.toml"

__config_dir = os.path.dirname(os.path.abspath(__file__))
__config_path = os.path.join(__config_dir, __config_file)

if not os.path.exists(__config_path):
    raise Exception("Config file not found!")

with open(__config_path, "rb") as f:
    config = tomllib.load(f)
