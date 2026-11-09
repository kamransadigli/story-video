---
name: story-video
description: Make a short vertical (9:16) narrated story video, like true-crime / detective / history Shorts, from a topic. Writes the script, draws or generates one image per shot, records narration, adds word-by-word captions, music and sound effects, and renders an MP4. Use when the user asks for a story video, a Short/Reel/TikTok about a topic, or runs /story-video.
---

# /story-video

Turn a topic into a 30–50 second vertical video with narration, captions, music and camera motion.

```
/story-video "The Phantom of Heilbronn"            # free: SVG illustrations
/story-video "The Phantom of Heilbronn" --ai        # AI images via fal.ai (paid, ask first)
```

The repo's example is `stories/phantom-of-heilbronn/`. Read its `story.json` and a couple of its scenes before you start: match that structure and quality bar.

## 1. Setup check
- `models/kokoro-v1.0.onnx` exists. If not, run `./setup.sh`.
- `ffmpeg` and Node with Playwright are available (`node -e "require('playwright')"`).

## 2. Research and script
- Get the facts right. Prefer the user's facts; otherwise use what you know well. Don't invent names, dates or numbers. Soften anything you're unsure of.
- Structure: **hook** (first line must create a question, ≤ 12 words) → escalation (3–6 short beats) → **twist / reveal** → one-line payoff that echoes the hook.
- 85–120 words total, 10–14 shots, one sentence or fragment per shot. Short words, spoken rhythm.
- Keep it respectful toward real victims: no gore, no mocking.

## 3. Write `stories/<slug>/story.json`
```json
{
  "title": "...", "voice": "am_michael", "speed": 1.05, "music": "noir", "music_volume": 0.8,
  "style": "one style line appended to every AI image prompt",
  "shots": [
    {"id": "01", "narration": "Caption + spoken text.", "say": "optional spoken override (numbers, names)",
     "svg": "scenes/01-name.svg", "prompt": "AI image prompt for this shot (no text in image)",
     "motion": "push_in", "sfx": "hit"}
  ]
}
```
- `motion`: `push_in`, `pull_out`, `pan_left`, `pan_right`, `pan_up`, `pan_down`, `still`. Alternate them; never the same twice in a row.
- `sfx`: `hit` (hook, reveals), `whoosh` (normal cuts), `glass`, `click`, `static`, `riser` (before the twist), `end` (last shot). Or omit.
- Use `say` when Kokoro would misread something: years ("two thousand seven"), currency, abbreviations, foreign names.
- Voices: `am_michael`, `am_fenrir`, `bm_george`, `bm_fable`, `af_heart`, `af_bella`.

## 4a. Free images: draw SVG scenes
- Copy `stories/phantom-of-heilbronn/scenes/_defs.svg` into the new story's `scenes/` and reuse its gradients, filters, `#pin`, `#mug` symbols and classes (`.ink`, `.thin`, `.marker`, `.type`, `.head`).
- Each scene: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">`, full-bleed background, a clear focal object, dark ink outlines, lamp/moon/spot lighting, and end with `<rect width="1080" height="1920" filter="url(#grit)"/>`.
- Fonts available inside SVG: `Marker` (handwriting), `Typewriter`, `Oswald` (headlines).
- Keep the area around y=1100–1300 calm enough for captions. Keep key objects within the middle 80% (the camera crops).
- Preview before rendering the video:
  `node tools/svg2png.mjs /tmp/preview 0.5 stories/<slug>/scenes/_defs.svg stories/<slug>/scenes/*.svg`
  then look at the PNGs and fix anything ugly, overlapping or unreadable.

## 4b. AI images (paid, fal.ai)
- Only when the user asked for AI images. Tell them the estimate first: shots × price (≈ $0.025/image on `fal-ai/flux/dev`, ≈ $0.04 on `fal-ai/nano-banana`) and wait for OK.
- Write a strong shared `style` and specific per-shot `prompt`s (subject, setting, lighting, camera angle; no text).
- Run with `--images fal [--fal-model fal-ai/nano-banana] --max-cost <usd>`. Images are cached in `build/images-fal/`; delete one PNG to regenerate just that shot.

## 5. Render and review
```
python3 -m storyvideo stories/<slug>            # add --images fal for AI images
```
Output: `stories/<slug>/output/video.mp4` (1080×1920, 30 fps).
Review: extract frames (`ffmpeg -ss <t> -i video.mp4 -frames:v 1 f.png`) at the hook, the twist and the end; check captions are readable and in sync. Fix and re-render (voice and images are cached, so re-renders are fast).

## 6. Report
Give the user the video path, length, the script, and what it cost (if paid). Offer one or two concrete improvements.
