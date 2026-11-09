# story-video

Automatic vertical story videos (Shorts / Reels / TikTok) with Claude Code.

One command turns a topic into a narrated 30–50 second 1080×1920 video:
script → one image per shot → voiceover → word-by-word captions → camera moves → music and sound effects → MP4.

```
/story-video "The Phantom of Heilbronn"
```

Example: [`samples/phantom-of-heilbronn.mp4`](samples/phantom-of-heilbronn.mp4) (made fully free).

## How it works

| Step | Free version | Paid upgrade |
|---|---|---|
| Script and shot list | Claude Code (the `/story-video` skill) | – |
| Images | SVG illustrations Claude draws, rendered with Chromium | fal.ai (Flux / Nano Banana), about $0.03–0.04 each |
| Voice | [Kokoro](https://github.com/thewh1teagle/kokoro-onnx), runs locally | – |
| Captions | Word-by-word with the spoken word highlighted, timed to the voice | – |
| Music and SFX | Synthesized noir bed and effects, no licenses needed | – |
| Motion | Ken Burns push/pull/pan, punch-in on cuts, film grain, vignette | AI motion clips (Kling), planned |

## Setup

Needs Python 3.10+, Node 18+, FFmpeg.

```bash
./setup.sh
npm install && npx playwright install chromium
```

## Use

In Claude Code, inside this repo:

```
/story-video "your topic"
```

Or render an existing story folder directly:

```bash
python3 -m storyvideo stories/phantom-of-heilbronn
python3 -m storyvideo stories/phantom-of-heilbronn --voice bm_george
FAL_KEY=... python3 -m storyvideo stories/phantom-of-heilbronn --images fal --max-cost 1
```

The fal.ai image step has not been tested against the live API yet.

A story is a folder with `story.json` (the shots) and `scenes/` (SVGs). See [`.claude/skills/story-video/SKILL.md`](.claude/skills/story-video/SKILL.md) for the format.

## Credits

Fonts: Poppins, Permanent Marker, Special Elite and Oswald (SIL Open Font License, see `assets/fonts/`). Voice: Kokoro-82M (Apache 2.0).
