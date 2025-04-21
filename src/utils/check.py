import os
import json
from typing import Dict


def check_exist_json_file(path: str) -> Dict[str, str]:
    """
    Check if a JSON file exists and return its contents.
    
    Args:
        path (str): Path to the JSON file
        
    Returns:
        dict: JSON file contents or empty dictionary if file doesn't exist/is empty
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}