# vlogger

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

# Shell completion script
vlogger completion --shell bash

# Generate JSON Schema (for developers)
vlogger generate-schema
```