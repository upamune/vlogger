"""
JSON Schemaに日本語タイトル・説明を付与するためのヘルパー。
"""

from typing import Dict, Any

def schema_with_title(title: str, description: str) -> Dict[str, Any]:
    return {
        "title": title,
        "description": description,
    }
