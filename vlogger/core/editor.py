"""
Configuration that allows setting overlay text for each video.
Process each video using MoviePy to add overlays, concatenate them, and add BGM.
"""

import math
from typing import Optional
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    TextClip,
    concatenate_videoclips,
    concatenate_audioclips,
)
from vlogger.models.config_model import VlogConfig, VideoItem
from moviepy.config import change_settings

class VideoEditor:
    TEXT_POSITION = {
        'left_bottom': (0.025, 0.9),   
        'center': ("center", "center"),          
        'right_top': ("right", "top"),     
    }

    def __init__(self, config: VlogConfig):
        self.config = config

        new_settings = {}
        if self.config.ffmpeg_binary and self.config.ffmpeg_binary.strip():
            new_settings["FFMPEG_BINARY"] = self.config.ffmpeg_binary.strip()
        if self.config.imagemagick_binary and self.config.imagemagick_binary.strip():
            new_settings["IMAGEMAGICK_BINARY"] = self.config.imagemagick_binary.strip()
        if new_settings:
            change_settings(new_settings)

    def process(self, output_path: str) -> None:
        """
        Apply individual overlays to each video in config.videos,
        concatenate all clips, and combine with BGM for final output.
        """

        # 1. Process each video individually (text overlays)
        processed_clips = []
        for video_item in self.config.videos:
            base_clip = VideoFileClip(video_item.path)

            # Handle audio muting based on settings
            should_mute = video_item.mute if video_item.mute is not None else self.config.global_mute
            if should_mute:
                base_clip = base_clip.without_audio()

            # この動画固有の overlays
            text_clips = []
            for overlay in video_item.overlays:
                # Skip if text is None or empty
                if not overlay.text or not overlay.text.strip():
                    continue

                font_path = self.config.global_font.font_path
                font_size = self.config.global_font.font_size

                if overlay.font and overlay.font.font_path:
                    font_path = overlay.font.font_path
                if overlay.font and overlay.font.font_size is not None:
                    font_size = overlay.font.font_size

                txt_clip = (
                    TextClip(
                        txt=f"  {overlay.text}  ",
                        fontsize=font_size,
                        font=font_path if font_path else "DejaVu-Sans",
                        color="black",
                        bg_color="white",
                        stroke_color=None,
                        print_cmd=True,
                    )
                    .set_position(self.TEXT_POSITION.get(overlay.position, self.TEXT_POSITION['left_bottom']), relative=True)
                )

                # Handle different combinations of start_time and duration
                if overlay.start_time is not None and overlay.duration is not None:
                    # Both specified - use as is
                    txt_clip = txt_clip.set_start(overlay.start_time).set_duration(overlay.duration)
                elif overlay.start_time is not None:
                    # Only start_time specified - show until end of clip
                    txt_clip = txt_clip.set_start(overlay.start_time)
                elif overlay.duration is not None:
                    # Only duration specified - start from beginning
                    txt_clip = txt_clip.set_start(0).set_duration(overlay.duration)
                else:
                    # Neither specified - show for entire clip duration
                    txt_clip = txt_clip.set_start(0).set_duration(base_clip.duration)

                text_clips.append(txt_clip)

            if text_clips:
                # Combine video and text overlays
                composite_clip = CompositeVideoClip([base_clip, *text_clips])
            else:
                composite_clip = base_clip

            processed_clips.append(composite_clip)

        if not processed_clips:
            raise ValueError("No videos specified.")

        # 2. Concatenate all clips
        final_video = concatenate_videoclips(
            processed_clips,
            method="chain",
        )
        
        # 3. Combine BGM (infinite loop + fade in/fade out)
        bgm_clips = []  # Keep track of all BGM clips for proper cleanup
        final_audio_clips = []
        
        try:
            # First, add original video audio if it exists (this would be None if muted)
            if final_video.audio is not None:
                final_audio_clips.append(final_video.audio)

            # Then add BGM if specified (BGM is added regardless of mute settings)
            if self.config.bgm and self.config.bgm.path.strip():
                bgm_clip = AudioFileClip(self.config.bgm.path)
                bgm_clips.append(bgm_clip)
                video_duration = final_video.duration

                # Calculate how many times we need to loop the BGM
                loop_count = math.ceil(video_duration / bgm_clip.duration)

                # Create the full-length BGM by concatenating copies
                bgm_parts = []
                for _ in range(loop_count):
                    new_clip = AudioFileClip(self.config.bgm.path)
                    bgm_clips.append(new_clip)
                    bgm_parts.append(new_clip)

                merged_bgm = concatenate_audioclips(bgm_parts)

                # Trim BGM to match total duration
                merged_bgm = merged_bgm.subclip(0, video_duration)

                # Apply volume adjustment
                if self.config.bgm.volume_percentage != 100.0:
                    merged_bgm = merged_bgm.volumex(self.config.bgm.volume_percentage / 100.0)

                # Apply fade in/fade out
                if self.config.bgm.fade_in > 0:
                    merged_bgm = merged_bgm.audio_fadein(self.config.bgm.fade_in)
                if self.config.bgm.fade_out > 0:
                    merged_bgm = merged_bgm.audio_fadeout(self.config.bgm.fade_out)

                final_audio_clips.append(merged_bgm)

            # Create final audio mix if we have any audio clips
            if final_audio_clips:
                composite_audio = CompositeAudioClip(final_audio_clips)
                final_video = final_video.set_audio(composite_audio)

            codec = self.config.encoding.codec
            bitrate = self.config.encoding.bitrate
            preset = self.config.encoding.preset

            final_video.write_videofile(
                output_path,
                codec=codec,
                bitrate=bitrate,
                preset=preset,
                write_logfile=True,
                threads="auto",
                audio_codec="aac",
            )
        finally:
            # Cleanup all clips
            if final_video:
                final_video.close()
            for clip in processed_clips:
                clip.close()
            for clip in bgm_clips:
                clip.close()
