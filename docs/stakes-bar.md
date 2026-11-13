# Stakes bar (THE DETECTIVE DID IT)

A reusable meter shown at the top of each episode:

    🚨 SUSPICION %   ·   🧾 EVIDENCE   ·   🤝 TRUST %

Code: `storyvideo/stakes.py`. It is drawn by the normal renderer whenever a
story has a `"stakes"` block, and tick sounds are added automatically.

## Set it per episode (story.json)

```json
"stakes": {
  "y": 228,
  "width": 880,
  "show_from": 6.2,
  "hide_from": 40.0,
  "start":   {"suspicion": 10, "evidence": 3, "trust": 100},
  "changes": [
    {"at": 12.0, "suspicion": 25},
    {"at": 18.5, "evidence": 2},
    {"at": 21.0, "trust": 80},
    {"at": 24.0, "pulse": "evidence"}
  ]
}
```

| Key | Meaning |
|---|---|
| `y` | Vertical centre in pixels. Keep it at 228 or more (below the top 8%). |
| `width` | Bar width; 880 keeps it out of the right 15%. |
| `show_from` / `hide_from` | When the bar slides in / out (seconds). `hide_from` is optional. |
| `start` | Values at the start of the episode. Day N should start where Day N-1 ended, after the vote. |
| `changes` | Each change counts up/down over 0.6s with a pulse and tick sounds. `{"pulse": "evidence"}` pulses a value without changing it. Add `"flash": [255, 60, 60]` to a change to show the value in that colour while it pulses. |

## Carrying values between days
Keep a running log in `stories/detective-did-it/STATE.md`: the values at the end of
each day and which choice won. Copy the final values into the next day's `start`.
