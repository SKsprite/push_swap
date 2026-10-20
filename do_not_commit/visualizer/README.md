# push_swap visualiser

Python 3 + tkinter, stdlib only. Design notes: `../push_swap_visualizer.md`.

```sh
python3 visualizer.py                          # 100 random, --adaptive, ../../push_swap
python3 visualizer.py -n 500 -s complex
python3 visualizer.py -s simple 5 4 3 2 1
python3 visualizer.py -- -3 7 -1 0             # negative numbers need --
python3 visualizer.py -b ./fake_push_swap.py   # test without the C binary
../../push_swap 3 1 2 | python3 visualizer.py --ops - 3 1 2
python3 visualizer.py -t synthwave --mute      # theme, start silent
```

Themes: `midnight` (default), `light`, `synthwave`, `solarized`,
`viridis` (colour-blind friendly), `mono`. Switch live from the dropdown or `t`.

Sound: one tone per op (at high speed, one per frame so audio never lags).
Pitch = rank of the element the op moved (220 Hz → 1760 Hz); the waveform
tells you the op family: swaps = square, pushes = triangle, rotates = sine,
reverse rotates = saw. Audio is streamed to `pacat`, `pw-play` or `aplay`
(first one found) — no Python packages needed. Toggle with the checkbox or `m`;
the small slider next to it is volume.

| Key | Action |
|-----|--------|
| `Space` | play / pause (restarts if at the end) |
| `←` / `→` | step back / forward |
| `Home` / `End` | jump to start / end |
| `+` / `-` | faster / slower |
| `m` | sound on / off |
| `t` | next theme |

- Click a line in the op log or drag the scrubber to jump anywhere.
- White outline = elements moved by the last op.
- Red rows in the op log = adjacent pairs that cancel (`ra rra`, `pa pb`, …)
  or could merge (`ra rb` → `rr`); "next waste" jumps to the next one.
- The status line shows the disorder computed in Python; compare it with
  your `[bench] disorder` line to test `disorder.c`.

| File | Role |
|------|------|
| `sim.py` | simulator: ops, undo, checkpoints, disorder, waste detection |
| `runner.py` | runs push_swap (`--<strategy> --bench`), reads op files |
| `ui.py` | tkinter window |
| `themes.py` | colour themes + gradient helper |
| `sound.py` | tone synthesis + audio streaming thread |
| `visualizer.py` | CLI entry point |
| `fake_push_swap.py` | min-extraction stand-in with the same CLI, for testing |
