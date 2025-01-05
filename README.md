# vlogger

<img src="https://i.gyazo.com/f4a1d30bf5101796a1f3093038929dab.jpg" alt="logo" width="500">

A Python CLI tool to create simple Vlog videos with text overlays, BGM, etc.,  
using [MoviePy](https://github.com/Zulko/moviepy).

## Features

- Python 3.13+
- MoviePy-based video editing
- Multiple videos concatenation (no special OP/ED concept, just a list)
- Per-video text overlays
- Infinite looping BGM with fade in/out
- YAML-based configuration with Pydantic validation
- JSON Schema generation for auto-completion support
- Automatic config template generation command
- Shell completion command

## Installation

...


## Usage

```bash
# Generate a config template
vlogger generate-config --dir /path/to/videos --extension "mp4,mov"

# Create final vlog
vlogger create --config config_template.yaml --output final_vlog.mp4

# Generate JSON Schema (for developers)
vlogger generate-schema
```

## Example

```bash
$ uv run vlogger generate-config --dir tmp
# edit generated config_template.yaml
$ uv run vlogger create --config config_template.yaml
```

```yaml:config_template.yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/upamune/vlogger/refs/tags/v0.1.0/config_schema.json
# vim: set ts=2 sw=2 tw=0 fo=cnqoj

videos:
- path: tmp/DJI_20250103153221_0203_D.MP4
  overlays:
    - text: "1年ぶりのヨシカミ!!"
      position: left_bottom
    - text: "洋食 ヨシカミ"
      position: right_top
- path: tmp/DJI_20250103154227_0204_D.MP4
  overlays:
    - text: "かに入りヤキメシ(not チャーハン)"
      position: left_bottom
    - text: "洋食 ヨシカミ"
      position: right_top
- path: tmp/DJI_20250103154515_0207_D.MP4
  overlays:
    - text: "そして、ヒレステーキ。最高でした。"
      position: left_bottom
    - text: "洋食 ヨシカミ"
      position: right_top
- path: tmp/DJI_20250103161714_0209_D.MP4
  overlays:
    - text: "初詣に浅草寺に行ってみたけど、激混み..."
      position: left_bottom
    - text: "浅草寺"
      position: right_top
- path: tmp/DJI_20250103162006_0210_D.MP4
  overlays:
    - text: "ありえないくらい並んでいたので断念"
      position: left_bottom
    - text: "浅草寺"
      position: right_top

bgm:
  path: ./tmp/bgm.mp3
  volume_percentage: 80

global_font:
  font_path: ./zen-kakugothic/fonts/ttf/ZenKakuGothicNew-Bold.ttf
  font_size: 100

encoding:
  codec: "h264_videotoolbox"
```