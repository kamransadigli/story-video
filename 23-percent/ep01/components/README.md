# "23%" chat episodes

Each episode is a folder with `episode.json` (and an `assets/` folder for photos).
Render it with:

```bash
python3 -m storyvideo.chat stories/23-percent/ep02 --out 23-percent/ep02/ep02-instagram.mp4
python3 -m storyvideo.chat stories/23-percent/ep02 --out frame0.png --still 0   # one frame only
```

Code: `storyvideo/chat.py`. Components: lock screen + notification, chat header, message
bubbles (spring pop-in, scrolling, smooth fade at the top), typing dots, photo messages with
a lightbox, the battery bar, the choice screen, gentle push-in + phone float. Sounds are
added automatically (pop for her messages, swoosh for yours, shutter for photos, beep when
the battery bar appears).

## episode.json

```json
{
  "duration": 33.0,
  "contact": "Unknown", "subtitle": "mobile", "clock": "2:51",
  "ep_label": "EP 2", "fiction_label": "Fiction",

  "lock": {"until": 2.0, "time": "2:51", "date": "Friday, March 13",
           "notification": {"from": "Unknown", "text": "you called them didn't you"}},

  "messages": [
    {"t": 2.3, "from": "her", "text": "you called them didn't you"},
    {"t": 4.0, "from": "you", "text": "no. i'm here"},
    {"t": 5.5, "typing": true, "until": 6.4},
    {"t": 6.4, "from": "her", "text": "he's at the door"},
    {"t": 9.0, "from": "her", "photo": "assets/photo2.png", "open": [9.6, 13.0]}
  ],

  "battery": {"show_from": 0.5, "percent": 17, "label": "HER BATTERY"},

  "choice": {"t": 25.0, "question": "What do you text back?",
             "a": "Tell her to run", "b": "Tell her to hide",
             "note": "Look at the photo 👀 what do you see?",
             "send": "📲 Send this to the friend you'd text at 3 AM", "send_at": 4.2},

  "vo": [{"at": 25.3, "text": "What do I text back? A or B.", "voice": "am_michael", "speed": 1.05}],

  "sfx": [{"at": 0.05, "name": "buzz"}],
  "heartbeat": [6.0, 23.0],
  "silence": [23.0, 25.0],
  "music": "drone", "music_volume": 0.6
}
```

| Field | Meaning |
|---|---|
| `messages[].t` | When the message appears (seconds). `from`: `"her"` (left, grey) or `"you"` (right, blue). |
| typing | `{"t": start, "typing": true, "until": end}`: dots appear at `t` and vanish at `until`. Keep pauses ≤ 1.5 s. A typing bubble with no message after it = she stopped. |
| photo | `{"t": ..., "from": "her", "photo": "assets/x.png", "open": [start, end]}`: thumbnail in chat, then a larger view with a slow zoom between `open` times. 4:5 images work best. |
| `battery` | Bar appears at `show_from` with a pulse and beep. Lower `percent` each episode. Omit `show_from`'s delay (use 0.5) once the series has started. |
| `lock` | Optional lock screen with a notification that is readable from frame 0 (good for the cover). |
| `choice` | Choice card over a blurred chat at `t`. `note` and `send` lines are optional. |
| `vo` | Voice-over lines (Kokoro voices). |
| `heartbeat` / `silence` | Heartbeat between two times; `silence` dips the drone music to almost nothing (tension beat). |
| `sfx` | Extra sounds: `buzz`, `pop`, `swoosh`, `beep`, `shutter`, `hit`, `whoosh`, `tick1`… |

Safe zones are built in: content stays left of 900 px (right 15% free), messages stay above
y=1300 (bottom 30% free), the battery bar sits at y≈410 (below the top 8%).
