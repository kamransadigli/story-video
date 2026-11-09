"""story-video: turn a story folder (story.json + scenes) into a vertical narrated video.

    python -m storyvideo stories/<name>                 # free: SVG scenes + Kokoro voice
    python -m storyvideo stories/<name> --images fal    # AI images from fal.ai (paid)
"""
import argparse
import json
import sys
from pathlib import Path

import soundfile as sf

from . import audio, images, tts, video

LEAD_IN = 0.15      # silence before the first word
PRE_VOICE = 0.12    # silence after each cut before the line starts
GAP = 0.30          # breath after each line
TAIL = 1.8          # hold on the last shot


def main():
    ap = argparse.ArgumentParser(prog="storyvideo")
    ap.add_argument("story", type=Path, help="story folder containing story.json")
    ap.add_argument("--images", choices=["svg", "fal"], default="svg")
    ap.add_argument("--fal-model", default="fal-ai/flux/dev")
    ap.add_argument("--max-cost", type=float, default=2.0, help="refuse paid runs estimated above this (USD)")
    ap.add_argument("--voice", help="override the Kokoro voice, e.g. am_michael, bm_george")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    story_dir = args.story.resolve()
    story = json.loads((story_dir / "story.json").read_text())
    shots = story["shots"]
    build = story_dir / "build"
    out = args.out or (story_dir / "output" / "video.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. images
    if args.images == "fal":
        est = images.fal_estimate(shots, args.fal_model)
        print(f"fal.ai estimate: {len(shots)} images x {args.fal_model} ~= ${est:.2f}")
        if est > args.max_cost:
            sys.exit(f"Estimated cost ${est:.2f} is above --max-cost ${args.max_cost:.2f}. Stopping.")
        img_paths = images.render_fal(story, shots, build / "images-fal", args.fal_model)
    else:
        print("1/4 drawing scenes (SVG)")
        img_paths = images.render_svg(story_dir, shots, build / "images-svg")

    # 2. voice + timeline
    print("2/4 recording narration (Kokoro)")
    voice = args.voice or story.get("voice", "am_michael")
    speed = story.get("speed", 1.0)
    t = LEAD_IN
    plan_shots, clips, sfx_events, captions = [], [], [], []
    for i, s in enumerate(shots):
        x, sr = tts.speak(s.get("say", s["narration"]), voice, speed, build / "voice")
        dur = len(x) / sr
        start = t
        v_start = start + PRE_VOICE
        end = v_start + dur + GAP + (story.get("tail", TAIL) if i == len(shots) - 1 else 0)
        clips.append((v_start, x, sr))
        if s.get("sfx"):
            sfx_events.append((start, s["sfx"]))
        captions += video.caption_events(s["narration"], v_start, dur, min(end, v_start + dur + 0.25))
        plan_shots.append({"id": s["id"], "start": start if i else 0.0, "end": end, "motion": s.get("motion", "push_in"),
                           "caption_y": s.get("caption_y", video.CAPTION_Y)})
        t = end
    total = t
    print(f"   length {total:.1f}s, {len(shots)} shots")

    # 3. audio
    print("3/4 mixing music + sound effects")
    wav = build / "mix.wav"
    sf.write(wav, audio.mix(total, clips, sfx_events, story.get("music", "noir")), audio.SR)

    # 4. video
    print("4/4 rendering video")
    plan = {"shots": plan_shots, "badge": story.get("badge"), "captions": captions, "total": total,
            "images": {k: str(v) for k, v in img_paths.items()}}
    video.render(plan, wav, out, workers=args.workers)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
