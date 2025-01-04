"""
MoviePyを使って動画を合成し、テキストやBGMを付加するロジックを呼び出す。
"""

from typing import List
from rich.console import Console
import yaml

from vlogger.core.editor import VideoEditor
from vlogger.models.config_model import VlogConfig

console = Console()

def create_vlog(config_path: str, output_path: str) -> None:
    """
    YAML設定ファイルを読み込み、動画の合成と書き出しを行う。
    """
    console.log(f"Loading config from: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)

    # Pydanticでバリデーションしながらモデル化
    vlog_config = VlogConfig(**config_dict)

    # Editorクラスを使って実際の編集処理を行う
    editor = VideoEditor(config=vlog_config)
    editor.process(output_path=output_path)

    console.log(f"Vlog created successfully at: {output_path}")
