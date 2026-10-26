#!/usr/bin/env python3
"""
YouTube Shorts ビルドスクリプト - プロジェクト2（ぶった斬り20本ノック）
3段構成（キャッチコピー上段 / 元動画中段 / バナー下段）を合成してMP4出力する
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent


def load_layout():
    with open(BASE_DIR / "config" / "layout.json") as f:
        return json.load(f)


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def make_catchcopy_image(lines: list[str], layout: dict) -> Path:
    cfg = layout["catchcopy"]
    top = layout["sections"]["top"]
    canvas_w = layout["canvas"]["width"]
    canvas_h = top["height"]
    bg = hex_to_rgb(top["bg_color"])
    fg = hex_to_rgb(cfg["color"])
    stroke = hex_to_rgb(cfg["stroke_color"])

    img = Image.new("RGB", (canvas_w, canvas_h), bg)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(cfg["font_path"], cfg["font_size"])
    except OSError:
        print(f"[WARN] フォントが見つかりません: {cfg['font_path']} → デフォルトフォントを使用")
        font = ImageFont.load_default()

    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=cfg["stroke_width"])
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    line_gap = 20
    total_text_h = sum(line_heights) + line_gap * (len(lines) - 1)
    y = (canvas_h - total_text_h) // 2

    for i, line in enumerate(lines):
        x = (canvas_w - line_widths[i]) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=fg,
            stroke_width=cfg["stroke_width"],
            stroke_fill=stroke,
        )
        y += line_heights[i] + line_gap

    out_path = BASE_DIR / "previews" / "_catchcopy_tmp.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    return out_path


def make_banner_image(layout: dict) -> Path:
    cfg = layout["banner"]
    bottom = layout["sections"]["bottom"]
    canvas_w = layout["canvas"]["width"]
    canvas_h = bottom["height"]
    bg = hex_to_rgb(layout["sections"]["top"]["bg_color"])

    src = Image.open(BASE_DIR / cfg["source"]).convert("RGB")
    padding = cfg["padding"]
    max_w = canvas_w - padding * 2
    max_h = canvas_h - padding * 2

    src.thumbnail((max_w, max_h), Image.LANCZOS)
    result = Image.new("RGB", (canvas_w, canvas_h), bg)
    paste_x = (canvas_w - src.width) // 2
    paste_y = (canvas_h - src.height) // 2
    result.paste(src, (paste_x, paste_y))

    out_path = BASE_DIR / "previews" / "_banner_tmp.png"
    result.save(str(out_path))
    return out_path


def build(clip_id: str, start: int, end: int, catchcopy_lines: list[str], output_name: str):
    layout = load_layout()
    cv = layout["canvas"]
    sec = layout["sections"]
    src_cfg = layout["source_video"]

    print(f"[1/4] キャッチコピー画像を生成中...")
    catchcopy_png = make_catchcopy_image(catchcopy_lines, layout)

    print(f"[2/4] バナー画像を生成中...")
    banner_png = make_banner_image(layout)

    output_dir = BASE_DIR / "output" / "drafts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{output_name}.mp4"

    vid_h = sec["video"]["height"]
    vid_w = sec["video"]["width"]
    top_h = sec["top"]["height"]
    bot_h = sec["bottom"]["height"]
    duration = end - start

    print(f"[3/4] FFmpegで合成中... ({start}s〜{end}s / {duration}s)")

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(duration),
        "-i", str(BASE_DIR / src_cfg["path"]),
        "-loop", "1", "-t", str(duration), "-i", str(catchcopy_png),
        "-loop", "1", "-t", str(duration), "-i", str(banner_png),
        "-filter_complex",
        (
            f"[0:v]scale={vid_w}:{vid_h}:force_original_aspect_ratio=decrease,"
            f"pad={vid_w}:{vid_h}:(ow-iw)/2:(oh-ih)/2:color=#1E2030[vid];"
            f"[1:v]scale={vid_w}:{top_h}[top];"
            f"[2:v]scale={vid_w}:{bot_h}[bot];"
            f"[top][vid][bot]vstack=inputs=3[out]"
        ),
        "-map", "[out]",
        "-map", "0:a",
        "-c:v", cv["video_codec"],
        "-crf", str(cv["crf"]),
        "-preset", cv["preset"],
        "-c:a", cv["audio_codec"],
        "-b:a", "128k",
        "-r", str(cv["fps"]),
        "-movflags", "+faststart",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERROR] FFmpeg失敗:")
        print(result.stderr[-3000:])
        sys.exit(1)

    size_kb = output_path.stat().st_size // 1024
    print(f"[4/4] 完成: {output_path} ({size_kb} KB)")
    return output_path


CLIPS = {
    "SHORT_01": {
        "start": 215, "end": 285,
        "catchcopy": ["不登校の子どもに", "父の答えがやばすぎた"],
        "output": "SHORT_01_draft",
    },
    "SHORT_02": {
        "start": 140, "end": 220,
        "catchcopy": ["ゴミを出すたびに", "見てくる隣人が怖い"],
        "output": "SHORT_02_draft",
    },
    "SHORT_03": {
        "start": 75, "end": 140,
        "catchcopy": ["3食全部作らされて", "外にも出れない主婦"],
        "output": "SHORT_03_draft",
    },
    "SHORT_04": {
        "start": 298, "end": 362,
        "catchcopy": ["無料のものは", "なんでも持ち帰る旦那"],
        "output": "SHORT_04_draft",
    },
    "SHORT_05": {
        "start": 362, "end": 432,
        "catchcopy": ["浮気癖が治る方法を", "会長に聞いてみた"],
        "output": "SHORT_05_draft",
    },
}


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts ビルド")
    parser.add_argument("clip_id", nargs="?", help="例: SHORT_01 (省略時は全件)")
    args = parser.parse_args()

    targets = [args.clip_id] if args.clip_id else list(CLIPS.keys())

    for clip_id in targets:
        if clip_id not in CLIPS:
            print(f"[ERROR] 不明なクリップID: {clip_id}")
            sys.exit(1)
        c = CLIPS[clip_id]
        print(f"\n{'='*50}")
        print(f"  ビルド開始: {clip_id}")
        print(f"{'='*50}")
        build(clip_id, c["start"], c["end"], c["catchcopy"], c["output"])

    print("\n全ビルド完了！")


if __name__ == "__main__":
    main()
