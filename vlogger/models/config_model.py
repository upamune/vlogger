"""
Added VideoItem model to manage overlay settings per video,
using videos: List[VideoItem] for management.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from vlogger.models.schema_utils import schema_with_title
from enum import Enum

class EncodingSettings(BaseModel):
    codec: Optional[str] = Field(default="libx264", description="Codec used for encoding")
    bitrate: Optional[str] = Field(default="8000k", description="Bitrate")
    preset: Optional[str] = Field(default="medium", description="Encoding preset")

class FontSettings(BaseModel):
    font_path: Optional[str] = Field(default=None, description="Font file path")
    font_size: Optional[int] = Field(default=24, description="Font size")

class PositionEnum(str, Enum):
    LEFT_BOTTOM = "left_bottom"
    RIGHT_TOP = "right_top"
    CENTER = "center"

class OverlayText(BaseModel):
    text: str = Field(..., description="Text to display")
    start_time: Optional[float] = Field(default=None, description="Text display start time in seconds")
    duration: Optional[float] = Field(default=None, description="Duration to display text in seconds")
    position: PositionEnum = Field(
        default=PositionEnum.LEFT_BOTTOM,
        description="Text position on the video"
    )
    font: Optional[FontSettings] = Field(default=None, description="Custom font settings for this text")

class BGMSettings(BaseModel):
    path: str = Field(..., description="Path to BGM audio file")
    fade_in: float = Field(default=0.0, description="BGM fade in duration in seconds")
    fade_out: float = Field(default=0.0, description="BGM fade out duration in seconds")
    volume_percentage: float = Field(default=100.0, description="BGM volume percentage (0-100)")

class VideoItem(BaseModel):
    """
    Represents a single video clip.
    Holds individual overlay settings specific to this video.
    """
    path: str = Field(..., description="Path to video file")
    overlays: List[OverlayText] = Field(default_factory=list, description="List of text overlays for this video")

class VlogConfig(BaseModel):
    """
    Configuration for video concatenation, including global BGM and encoding settings.
    """
    videos: List[VideoItem] = Field(
        default_factory=list,
        description="List of videos to concatenate. Combined in order."
    )
    bgm: Optional[BGMSettings] = Field(default=None, description="BGM settings")
    encoding: EncodingSettings = Field(default_factory=EncodingSettings)

    # Default font settings used when individual overlays don't specify their own
    global_font: FontSettings = Field(default_factory=FontSettings)

    # Add binary path configurations
    ffmpeg_binary: Optional[str] = Field(
        default="ffmpeg",
        description="Path to FFmpeg binary. Defaults to 'ffmpeg' (assumes it's in PATH)"
    )
    imagemagick_binary: Optional[str] = Field(
        default="convert",
        description="Path to ImageMagick convert binary. Defaults to 'convert' (assumes it's in PATH)"
    )

    @classmethod
    def construct_example(cls) -> "VlogConfig":
        """
        Generate sample data for template creation
        """
        return cls(
            videos=[
                VideoItem(
                    path="op.mp4",
                    overlays=[
                        OverlayText(text="Welcome to OP", position="center"),
                    ],
                ),
                VideoItem(
                    path="video1.mp4",
                    overlays=[
                        OverlayText(text="Video 1", position="left_bottom"),
                        OverlayText(text="Video 1 :)", position="right_top"),
                    ],
                ),
                VideoItem(
                    path="ed.mp4",
                    overlays=[
                        OverlayText(text="This is ED", position="center"),
                    ],
                ),
            ],
            bgm=BGMSettings(path="bgm.mp3", fade_in=2.0, fade_out=3.0, volume_percentage=100.0),
            encoding=EncodingSettings(codec="libx264", bitrate="8000k", preset="medium"),
            global_font=FontSettings(font_path=None, font_size=100),
        )

    class Config:
        schema_extra = schema_with_title("VlogConfig", "Schema for Vlog creation configuration")
