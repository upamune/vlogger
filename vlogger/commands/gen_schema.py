"""
For developers: Generate JSON Schema for VlogConfig
"""

import json
from rich.console import Console
from vlogger.models.config_model import VlogConfig

console = Console()

def generate_schema_command() -> None:
    schema_json = VlogConfig.schema_json(indent=2)
    output_path = "config_schema.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(schema_json)

    console.log(f"JSON Schema file generated: {output_path}")
