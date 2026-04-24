import json
from typing import List, Dict

def load_dataset(filepath: str) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_users(dataset: Dict) -> List[Dict]:
    return dataset.get("users", [])
