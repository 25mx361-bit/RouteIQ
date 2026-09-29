import json
from pathlib import Path
from datetime import datetime

REGISTRY_PATH = Path(__file__).parent / 'checkpoints' / 'model_registry.json'

def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    return {"versions": [], "active_version": None}

def save_registry(registry: dict):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

def register_model(version: str, config_dict: dict, train_metrics: dict, val_metrics: dict, test_metrics: dict, checkpoint_path: str, train_date_range: dict, features_used: list):
    registry = load_registry()
    entry = {
        "version": version,
        "config": config_dict,
        "train_metrics": train_metrics,
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "checkpoint_path": checkpoint_path,
        "train_date_range": train_date_range,
        "features_used": features_used,
        "registered_at": datetime.utcnow().isoformat()
    }
    registry['versions'].append(entry)
    save_registry(registry)
    return entry

def get_active_version() -> str | None:
    registry = load_registry()
    return registry.get('active_version')

def promote_model(version: str):
    registry = load_registry()
    versions = [v['version'] for v in registry['versions']]
    if version in versions:
        registry['active_version'] = version
        save_registry(registry)
        print(f"Promoted model version {version} to active.")
    else:
        print(f"Model version {version} not found in registry.")

def get_version_info(version: str) -> dict | None:
    registry = load_registry()
    for v in registry['versions']:
        if v['version'] == version:
            return v
    return None

def list_versions() -> list:
    registry = load_registry()
    return registry['versions']

def should_promote(new_val_metrics: dict, current_val_metrics: dict | None) -> bool:
    if current_val_metrics is None:
        return True
    return new_val_metrics.get('mae', float('inf')) < current_val_metrics.get('mae', float('inf'))
