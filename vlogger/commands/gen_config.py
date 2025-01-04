"""
指定したディレクトリ内の動画ファイルを一覧し、YAML設定ファイルの雛形を自動生成する。
"""

import os
import glob
import yaml
from typing import Optional
from rich.console import Console

from vlogger.models.config_model import VlogConfig, VideoItem, OverlayText

console = Console()

def generate_config_command(directory: Optional[str], extension: str) -> None:
    if directory is None:
        console.log("No directory specified. Generating a generic config template...")
        config_data = VlogConfig.construct_example().dict(exclude_unset=True)
    else:
        console.log(f"Generating config template for directory: {directory}")
        exts = [ext.strip() for ext in extension.split(",") if ext.strip()]
        video_files = []
        for ext in exts:
            pattern_lower = os.path.join(directory, f"*.{ext.lower()}")
            pattern_upper = os.path.join(directory, f"*.{ext.upper()}")
            video_files.extend(glob.glob(pattern_lower))
            video_files.extend(glob.glob(pattern_upper))

        if not video_files:
            console.log(f"No video files (.{extension}) found in the directory. Generating a generic template...")
            config_data = VlogConfig.construct_example().dict(exclude_unset=True)
        else:
            # ディレクトリ内の動画をベースに、簡易的な VideoItem を作ってみる例
            items = []
            for vf in video_files:
                # 実際にはオーバーレイなど付けず、空のまま
                items.append(VideoItem(path=vf, overlays=[]))

            example_config = VlogConfig.construct_example()
            example_config.videos = items
            config_data = example_config.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True)

    output_path = "config_template.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/upamune/vlogger/refs/tags/v0.1.0/config_schema.json\n")
        f.write("# vim: set ts=2 sw=2 tw=0 fo=cnqoj\n\n")
        yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)

    console.log(f"Config template generated: {output_path}")
