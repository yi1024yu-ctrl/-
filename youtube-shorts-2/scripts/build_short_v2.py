#!/usr/bin/env python3
"""
YouTube Shorts ビルドスクリプト v2 - 悩みカード除去版
複数セグメントをtrm+concatで結合し、女性ナレーション・悩みカードを排除する
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


def build(clip_id: str, segments: list[tuple], catchcopy_lines: list[str], output_name: str):
    layout = load_layout()
    cv = layout["canvas"]
    sec = layout["sections"]
    src_cfg = layout["source_video"]

    print(f"[1/4] キャッチコピー画像を生成中...")
    catchcopy_png = make_catchcopy_image(catchcopy_lines, layout)

    print(f"[2/4] バナー画像を生成中...")
    banner_png = make_banner_image(layout)

    output_dir = BASE_DIR / "output" / "final_v2"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{output_name}.mp4"

    vid_h = sec["video"]["height"]
    vid_w = sec["video"]["width"]
    top_h = sec["top"]["height"]
    bot_h = sec["bottom"]["height"]

    total_duration = sum(e - s for s, e in segments)
    seg_desc = " + ".join(f"{s}〜{e}s({e-s}s)" for s, e in segments)
    print(f"[3/4] FFmpegで合成中... {seg_desc} / 合計{total_duration}s")

    src_path = str(BASE_DIR / src_cfg["path"])
    n = len(segments)

    # Build filter_complex for multi-segment trim + concat + layout
    filters = []
    v_labels = []
    a_labels = []

    for i, (s, e) in enumerate(segments):
        filters.append(
            f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]"
        )
        filters.append(
            f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]"
        )
        v_labels.append(f"[v{i}]")
        a_labels.append(f"[a{i}]")

    # Concat all video/audio segments
    if n == 1:
        filters.append(f"[v0]scale={vid_w}:{vid_h}:force_original_aspect_ratio=decrease,"
                       f"pad={vid_w}:{vid_h}:(ow-iw)/2:(oh-ih)/2:color=#1E2030[vid]")
        filters.append(f"[a0]acopy[aud]")
    else:
        v_concat_in = "".join(v_labels)
        a_concat_in = "".join(a_labels)
        filters.append(
            f"{v_concat_in}concat=n={n}:v=1:a=0[vid_raw]"
        )
        filters.append(
            f"{a_concat_in}concat=n={n}:v=0:a=1[aud]"
        )
        filters.append(
            f"[vid_raw]scale={vid_w}:{vid_h}:force_original_aspect_ratio=decrease,"
            f"pad={vid_w}:{vid_h}:(ow-iw)/2:(oh-ih)/2:color=#1E2030[vid]"
        )

    # Static image inputs come after the source video
    # Input 1: catchcopy (loop), Input 2: banner (loop)
    filters.append(f"[1:v]scale={vid_w}:{top_h}[top]")
    filters.append(f"[2:v]scale={vid_w}:{bot_h}[bot]")
    filters.append(f"[top][vid][bot]vstack=inputs=3[out]")

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", src_path,
        "-loop", "1", "-t", str(total_duration), "-i", str(catchcopy_png),
        "-loop", "1", "-t", str(total_duration), "-i", str(banner_png),
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "[aud]",
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
    print(f"[4/4] 完成: {output_path} ({size_kb} KB / {total_duration}s)")
    return output_path


# 悩みカードを除去した会長セグメントのみ
CLIPS = {
    "SHORT_01": {
        # Q10答え + Q11答え(不登校がメイン) + Q12答え冒頭
        # 切除: Q10カード[~215-220], Q11カード[~233-238], Q12カード[263-273], Q13カード[284-287]
        "segments": [(221, 233), (239, 263), (274, 284)],
        "catchcopy": ["不登校の子どもに", "父の答えがやばすぎた"],
        "output": "SHORT_01_v2",
    },
    "SHORT_02": {
        # Q7答え(ゴミ隣人)+Q8答え(ぽっちゃり)+Q9答え(還暦)
        # 切除: Q7カード[~140-142], Q8カード[~152-156], Q9カード[~188-197], Q10カード[~212-220]
        "segments": [(143, 151), (157, 188), (198, 212)],
        "catchcopy": ["ゴミを出すたびに", "見てくる隣人が怖い"],
        "output": "SHORT_02_v2",
    },
    "SHORT_03": {
        # Q1〜Q8答えをまとめた主婦悩み集（各答えは短い）
        # 切除: 各悩みカード
        "segments": [(66, 79), (85, 93), (99, 109), (114, 119), (130, 135)],
        "catchcopy": ["3食全部作らされて", "外にも出れない主婦"],
        "output": "SHORT_03_v2",
    },
    "SHORT_04": {
        # Q13答え(匂い)+Q14答え(無料持ち帰り旦那がメイン)
        # 切除: Q13カード[~313-319]
        "segments": [(298, 314), (320, 362)],
        "catchcopy": ["無料のものは", "なんでも持ち帰る旦那"],
        "output": "SHORT_04_v2",
    },
    "SHORT_05": {
        # Q17答え(浮気癖)+Q18答え(施設)+Q19答え(燃え尽き)
        # 切除: Q18カード[374-381], Q19カード[404-412], 巣鴨アウトロカード[431-432]
        "segments": [(362, 374), (382, 404), (413, 431)],
        "catchcopy": ["浮気癖が治る方法を", "会長に聞いてみた"],
        "output": "SHORT_05_v2",
    },
}


def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts ビルド v2（悩みカード除去）")
    parser.add_argument("clip_id", nargs="?", help="例: SHORT_01 (省略時は全件)")
    args = parser.parse_args()

    targets = [args.clip_id] if args.clip_id else list(CLIPS.keys())

    for clip_id in targets:
        if clip_id not in CLIPS:
            print(f"[ERROR] 不明なクリップID: {clip_id}")
            sys.exit(1)
        c = CLIPS[clip_id]
        total_s = sum(e - s for s, e in c["segments"])
        print(f"\n{'='*50}")
        print(f"  ビルド開始: {clip_id}  予定尺:{total_s}s  セグメント:{len(c['segments'])}個")
        print(f"{'='*50}")
        build(clip_id, c["segments"], c["catchcopy"], c["output"])

    print("\n全ビルド完了！")


if __name__ == "__main__":
    main()
