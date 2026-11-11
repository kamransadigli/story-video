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
    ap.add_argument("--timing-only", action="store_true", help="print the timeline and stop")
    args = ap.parse_args()

    story_dir = args.story.resolve()
    story = json.loads((story_dir / "story.json").read_text())
    shots = story["shots"]
    build = story_dir / "build"
    out = args.out or (story_dir / "output" / "video.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. images (a shot can reuse another shot's picture with "image_of")
    own = [s for s in shots if "image_of" not in s]
    if args.images == "fal":
        est = images.fal_estimate(own, args.fal_model)
        print(f"fal.ai estimate: {len(own)} images x {args.fal_model} ~= ${est:.2f}")
        if est > args.max_cost:
            sys.exit(f"Estimated cost ${est:.2f} is above --max-cost ${args.max_cost:.2f}. Stopping.")
        img_paths = images.render_fal(story, own, build / "images-fal", args.fal_model)
    else:
        print("1/4 drawing scenes (SVG)")
        img_paths = images.render_svg(story_dir, own, build / "images-svg")
    for s in shots:
        if "image_of" in s:
            img_paths[s["id"]] = img_paths[s["image_of"]]

    video.LAYOUT.update(story.get("layout", {}))  # caption chunking uses it too

    # 2. voice + timeline
    print("2/4 recording narration (Kokoro)")
    voice = args.voice or story.get("voice", "am_michael")
    speed = story.get("speed", 1.0)
    pre_voice = story.get("pre_voice", PRE_VOICE)
    gap = story.get("gap", GAP)
    t = story.get("lead_in", LEAD_IN)
    plan_shots, clips, sfx_events, captions = [], [], [], []
    for i, s in enumerate(shots):
        start = 0.0 if i == 0 else t
        last = i == len(shots) - 1
        text = s.get("narration")
        if text:
            x, sr = tts.speak(s.get("say", text), s.get("voice", voice), s.get("speed", speed), build / "voice")
            dur = len(x) / sr
            v_start = (t if i else story.get("lead_in", LEAD_IN)) + s.get("pre_voice", pre_voice)
            end = v_start + dur + s.get("gap", gap) + (story.get("tail", TAIL) if last else 0)
            clips.append((v_start, x, sr))
            captions += video.caption_events(text, v_start, dur, min(end, v_start + dur + 0.25),
                                             samples=x, sr=sr, caption_y=s.get("caption_y"))
        else:
            end = t + s.get("duration", 2.0)
        end = max(end, start + s.get("min_duration", 0))
        if "duration" in s and text is None:
            end = start + s["duration"]
        end = round(end * video.FPS) / video.FPS  # cuts land exactly on frames
        sfx = s.get("sfx")
        if isinstance(sfx, str):
            sfx_events.append((start, sfx))
        elif isinstance(sfx, list):
            for e in sfx:
                sfx_events.append((start + e.get("at", 0), e["name"]))
        cd = s.get("countdown")
        if cd:
            for k in range(cd.get("from", 3)):
                sfx_events.append((start + cd["at"] + k * cd.get("step", 1.0), "tick1"))
        ps = {k: v for k, v in s.items() if k in ("id", "fx", "flashes", "overlays", "countdown",
                                                  "caption_y", "punch", "rain_box")}
        ps.update({"id": s["id"], "start": start, "end": end, "motion": s.get("motion", "push_in")})
        plan_shots.append(ps)
        t = end
    total = t

    # Narration on its own timeline (story["lines"]), so a sentence can run across cuts.
    for ln in story.get("lines", []):
        x, sr = tts.speak(ln.get("say", ln["text"]), ln.get("voice", voice), ln.get("speed", speed), build / "voice")
        dur = len(x) / sr
        clips.append((ln["at"], x, sr))
        cap_end = ln["at"] + dur + 0.25
        if not story.get("fade", True):  # looping video: clear captions before the final frames
            cap_end = min(cap_end, total - 0.3)
        captions += video.caption_events(ln["text"], ln["at"], dur, cap_end,
                                         samples=x, sr=sr, caption_y=ln.get("caption_y"))
        print(f"   line {ln['at']:.2f}-{ln['at'] + dur:.2f}s  {ln['text'][:50]}")
        if ln["at"] + dur > total:
            print(f"   WARNING: line ends after the video ({total:.2f}s)")
    print(f"   length {total:.2f}s, {len(shots)} shots")
    if args.timing_only:
        return

    # 3. audio
    print("3/4 mixing music + sound effects")
    wav = build / "mix.wav"
    babble = None
    if story.get("chatter"):
        chat_lines = ["Could you pass the salt, please?", "We arrive in the morning, I think.",
                      "This soup is still very hot.", "Did you see the storm outside?",
                      "I'll have another coffee, thank you.", "My brother lives in the city.",
                      "The train is quite late tonight.", "Oh, that is a lovely story.",
                      "Shall we play cards after dinner?", "I never sleep well on trains.",
                      "Waiter, could we have the bill?", "Yes, yes, I remember him."]
        chat_voices = ["af_bella", "bm_daniel", "af_sarah", "am_eric", "bf_isabella", "am_liam"]
        chat = [tts.speak(t_, chat_voices[k % len(chat_voices)], 1.0, build / "voice")
                for k, t_ in enumerate(chat_lines)]
        babble = audio.make_babble(chat, total)
    sf.write(wav, audio.mix(total, clips, sfx_events, story.get("music", "noir"),
                            story.get("music_volume", 0.8), story.get("ambience"),
                            fades=story.get("fade", True), babble=babble,
                            babble_volume=story.get("chatter_volume", 0.05),
                            ambience_volume=story.get("ambience_volume", 0.16)), audio.SR)

    # 4. video
    print("4/4 rendering video")
    plan = {"shots": plan_shots, "badge": story.get("badge"), "captions": captions, "total": total,
            "fade": story.get("fade", True), "layout": story.get("layout", {}),
            "vignette": story.get("vignette", 200),
            "images": {k: str(v) for k, v in img_paths.items()}}
    (build / "plan.json").write_text(json.dumps(plan, indent=1))
    video.render(plan, wav, out, workers=args.workers)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
