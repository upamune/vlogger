"""
動画ごとにオーバーレイテキストを設定可能な構成。
MoviePyを使って各動画を加工→連結し、BGMを載せる。
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
        config.videos に含まれる各動画に対して個別のオーバーレイを乗せ、
        全クリップを連結し、BGMを合成して出力する。
        """

        # 1. 各動画を個別に加工（テキストオーバーレイ）
        processed_clips = []
        for video_item in self.config.videos:
            base_clip = VideoFileClip(video_item.path)

            # この動画固有の overlays
            text_clips = []
            for overlay in video_item.overlays:
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
                # 動画 + テキストたちをまとめる
                composite_clip = CompositeVideoClip([base_clip, *text_clips])
            else:
                composite_clip = base_clip

            processed_clips.append(composite_clip)

        if not processed_clips:
            raise ValueError("No videos specified.")

        # 2. 全部連結
        final_video = concatenate_videoclips(processed_clips, method="compose")

        # 3. BGMの合成 (無限ループ + フェードイン/フェードアウト)
        if self.config.bgm and self.config.bgm.path.strip():
            bgm_clip = AudioFileClip(self.config.bgm.path)
            video_duration = final_video.duration

            loop_count = math.ceil(video_duration / bgm_clip.duration)
            merged_bgm = bgm_clip
            for _ in range(loop_count - 1):
                merged_bgm = merged_bgm.append(AudioFileClip(self.config.bgm.path))

            # 合計時間に合わせて BGM を切り詰め
            merged_bgm = merged_bgm.subclip(0, video_duration)

            # フェードイン・フェードアウト
            if self.config.bgm.fade_in > 0:
                merged_bgm = merged_bgm.audio_fadein(self.config.bgm.fade_in)
            if self.config.bgm.fade_out > 0:
                merged_bgm = merged_bgm.audio_fadeout(self.config.bgm.fade_out)

            # 既存音声と BGM をミックス
            if final_video.audio:
                composite_audio = CompositeAudioClip([final_video.audio, merged_bgm])
            else:
                composite_audio = CompositeAudioClip([merged_bgm])

            final_video = final_video.set_audio(composite_audio)

        codec = self.config.encoding.codec
        bitrate = self.config.encoding.bitrate
        preset = self.config.encoding.preset

        final_video.write_videofile(
            output_path,
            codec=codec,
            bitrate=bitrate,
            preset=preset,
            threads=4,
        )

        final_video.close()
        for c in processed_clips:
            c.close()
