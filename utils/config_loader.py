import yaml

def load_config(path: str) -> dict:
    """
    Load YAML config file into dict
    """
    with open(path, 'r') as f:
        return yaml.safe_load(f)
