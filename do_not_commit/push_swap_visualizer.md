# push_swap Visualiser — Design & Build Guide

> Internal dev tool for **stkoh** and **jayam**. Not part of the submission
> (the subject only allows `*.c`, `*.h`, `Makefile`). Keep it in `do_not_commit/`
> or a separate repo.

---

## Table of contents

1. [Goals](#1-goals)
2. [Technology choice](#2-technology-choice)
3. [Features](#3-features)
4. [Architecture](#4-architecture)
5. [Module specs](#5-module-specs)
6. [UI layout](#6-ui-layout)
7. [Reference implementation](#7-reference-implementation)
8. [Usage](#8-usage)
9. [Debugging workflows](#9-debugging-workflows)
10. [Stretch goals](#10-stretch-goals)
11. [Build checklist](#11-build-checklist)

---

## 1. Goals

The visualiser animates the op stream produced by `./push_swap` on stacks a and b
so we can:

- **see** each strategy (simple / medium / complex / adaptive) work,
- spot wasted moves (e.g. `ra` followed by `rra`, rotations that could be `rr`),
- tune chunk sizes / pivots by watching where elements land,
- verify correctness independently of `checker_linux` (OK/KO at the end),
- read `--bench` stats side-by-side with the animation,
- demo the project during evaluation (nice-to-have, not graded).

Non-goals: being part of the 42 build, editing the C code, network features.

---

## 2. Technology choice

| Option | Pros | Cons |
|--------|------|------|
| **Python 3 + tkinter** (recommended) | stdlib only — works on 42 machines without `pip`; `Canvas` handles 500 bars fine | less smooth than a game loop |
| Python 3 + pygame | smooth, 60 fps, easy | needs `pip install --user pygame` |
| Single HTML file (JS + `<canvas>`) | no install, shareable | can't run `./push_swap` itself — paste args + ops |

Go with **Python 3 + tkinter**. The simulator module is UI-independent, so a
pygame or web front-end can be added later.

---

## 3. Features

### 3.1 MVP

- **Input**
  - Numbers via CLI args, or `-n N` to generate N random distinct ints.
  - Strategy dropdown: `adaptive` (default), `simple`, `medium`, `complex`.
  - Path to the `push_swap` binary (default `../push_swap`).
- **Run** `push_swap` as a subprocess with `--bench`: stdout = ops, stderr = bench.
- **Render** stacks a and b as horizontal bars, side by side, top of stack at top:
  - bar width ∝ rank (0 … n-1),
  - colour = gradient by rank (blue → red) so sorted order looks like a smooth ramp.
- **Playback**: Play / Pause, Step ▶, Step ◀, Reset, Jump to end, speed slider
  (1 → 2000 ops/sec), progress scrubber.
- **Info panel**: current op index / total, last op name, per-op counts so far,
  final OK/KO, parsed `--bench` lines.
- **Error display**: if push_swap prints `Error`, show it; if an op line is
  unknown, stop and show the line number.

### 3.2 Nice-to-have

- Highlight the elements touched by the current op (e.g. white outline).
- Op log list that scrolls with playback; click an op to jump to it.
- Keyboard shortcuts: `Space` play/pause, `→`/`←` step, `Home`/`End`, `+`/`-` speed.
- "Wasted move" detector: flag adjacent pairs that cancel or could merge
  (`ra rra`, `pa pb`, `ra rb` → `rr`) — a live lint for our peephole optimiser.
- Load ops from a file / stdin instead of running the binary (to visualise
  someone else's output or `checker` test cases).
- Disorder generator: start sorted, apply k random swaps → test adaptive regimes.

---

## 4. Architecture

```
visualizer/
  visualizer.py      entry point: argparse, wires everything
  sim.py             pure simulator (no UI) — Stacks, apply(), undo()
  runner.py          subprocess call to push_swap, parse stdout/stderr
  ui.py              tkinter window, canvas rendering, controls
```

(Section 7 gives everything in one file for simplicity — split it once it grows.)

Data flow:

```
args/strategy ──► runner.run() ──► ops: list[str], bench: list[str], error
                                   │
                                   ▼
                     sim.History(initial_ranks, ops)
                     ├─ states computed on demand (apply forward / undo backward)
                     ▼
                     ui.Renderer.draw(state, highlight)
```

### 4.1 Why apply/undo instead of storing every state

500 numbers × ~6 000 ops × 500 ints = 1.5 M ints per snapshot set — fine in
C, heavy in Python. Instead store only the current state and implement **undo**
for every op (each op has an exact inverse). Scrubbing far = replay from the
nearest **checkpoint** (snapshot every 500 ops).

| Op | Inverse |
|----|---------|
| `sa` / `sb` / `ss` | itself |
| `pa` | `pb` |
| `pb` | `pa` |
| `ra` / `rb` / `rr` | `rra` / `rrb` / `rrr` |
| `rra` / `rrb` / `rrr` | `ra` / `rb` / `rr` |

⚠ Inverses are only exact when the op actually did something. `pa` on an empty
b is a no-op, so its "inverse" `pb` would corrupt state. Record per step whether
the op was effective (`apply()` returns a bool) and skip undo for no-ops.

---

## 5. Module specs

### 5.1 `sim.py`

```python
class Stacks:
    a: collections.deque[int]   # index 0 = top
    b: collections.deque[int]

    def apply(op: str) -> bool        # True if state changed; raises ValueError on unknown op
    def undo(op: str, effective: bool)
    def is_sorted() -> bool           # a ascending and b empty
    def copy() -> Stacks
```

- Use `deque`: `rotate(-1)` = `ra`, `rotate(1)` = `rra`, `appendleft/popleft` for push.
- Work on **ranks** (0 … n-1) computed from the input values — makes colouring
  and bar widths trivial. Keep a `rank → original value` map for tooltips.

### 5.2 `runner.py`

```python
def run(binary: str, strategy: str, values: list[int]) -> RunResult
# RunResult: ops: list[str], bench: list[str], error: str | None, returncode: int
```

- `subprocess.run([binary, f"--{strategy}", "--bench", *map(str, values)],
  capture_output=True, text=True, timeout=30)`.
- `stderr.strip() == "Error"` → error.
- Ops = `stdout.split("\n")` dropping the trailing empty string. Any blank line
  in the middle is a bug in push_swap — report it.
- Validate each op against the 11 legal names.

### 5.3 `ui.py`

- `Canvas` split into two halves (a | b). For n bars, bar height
  `h = canvas_height / n` (min 1 px). For n = 500 at 800 px → 1.6 px — fine.
- Redraw strategy:
  - n ≤ 200: delete + recreate rectangles each frame (simple).
  - n > 200: pre-create `n` rectangles once and `canvas.coords()` / `itemconfig()`
    them each frame — much faster than recreating.
- Animation loop via `root.after(delay_ms, tick)`. At high speed apply **several
  ops per tick** (`ops_per_tick = max(1, speed // 60)`) and redraw once — redraw
  is the bottleneck, not the simulation.

---

## 6. UI layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ Strategy [adaptive ▼]  N [100]  [Random] [Run]       binary: ../push_swap │
├───────────────────────────────────┬────────────────────────────────────┤
│              stack a              │              stack b               │
│ ████                              │ ██████████████                     │
│ ██████████                        │ ███                                │
│ ███████████████████               │ ███████████                        │
│ ██                                │                                    │
│ ...                               │ ...                                │
├───────────────────────────────────┴────────────────────────────────────┤
│ [⏮] [◀] [▶ Play] [▶|] [⏭]   speed ━━━━●━━━━ 240 op/s                   │
│ progress ━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━  2311 / 5321   last: rrr       │
├────────────────────────────────────────────────────────────────────────┤
│ sa 0 sb 0 ss 0 pa 412 pb 500 ra 640 rb 301 rr 210 rra 120 rrb 88 rrr 40 │
│ [bench] disorder: 49.93%  strategy: Adaptive / O(n log n)  total: 5321  │
│ Result: — (shows OK in green / KO in red at the end)                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Reference implementation

Single-file MVP (~200 lines, stdlib only). Save as
`do_not_commit/visualizer.py`.

```python
#!/usr/bin/env python3
"""push_swap visualiser — tkinter, stdlib only."""
import argparse
import random
import subprocess
import tkinter as tk
from collections import deque
from tkinter import ttk

OPS = ("sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr")
INVERSE = {"sa": "sa", "sb": "sb", "ss": "ss", "pa": "pb", "pb": "pa",
           "ra": "rra", "rb": "rrb", "rr": "rrr",
           "rra": "ra", "rrb": "rb", "rrr": "rr"}
CHECKPOINT_EVERY = 500


# ---------------------------------------------------------------- simulator
class Stacks:
    def __init__(self, a, b=()):
        self.a = deque(a)
        self.b = deque(b)

    def copy(self):
        return Stacks(self.a, self.b)

    @staticmethod
    def _swap(s):
        if len(s) < 2:
            return False
        s[0], s[1] = s[1], s[0]
        return True

    @staticmethod
    def _push(src, dst):
        if not src:
            return False
        dst.appendleft(src.popleft())
        return True

    @staticmethod
    def _rot(s, d):
        if len(s) < 2:
            return False
        s.rotate(d)
        return True

    def apply(self, op):
        a, b = self.a, self.b
        if op == "sa":  return self._swap(a)
        if op == "sb":  return self._swap(b)
        if op == "ss":  return self._swap(a) | self._swap(b)
        if op == "pa":  return self._push(b, a)
        if op == "pb":  return self._push(a, b)
        if op == "ra":  return self._rot(a, -1)
        if op == "rb":  return self._rot(b, -1)
        if op == "rr":  return self._rot(a, -1) | self._rot(b, -1)
        if op == "rra": return self._rot(a, 1)
        if op == "rrb": return self._rot(b, 1)
        if op == "rrr": return self._rot(a, 1) | self._rot(b, 1)
        raise ValueError(f"unknown op: {op!r}")

    def is_sorted(self):
        return not self.b and all(self.a[i] < self.a[i + 1]
                                  for i in range(len(self.a) - 1))


class History:
    """Holds the op list and lets you move to any index."""

    def __init__(self, ranks, ops):
        self.ops = ops
        self.pos = 0
        self.state = Stacks(ranks)
        self.checkpoints = {0: self.state.copy()}
        self.effective = []          # per applied op: did it change state?

    def forward(self):
        if self.pos >= len(self.ops):
            return False
        op = self.ops[self.pos]
        changed = self.state.apply(op)
        if self.pos < len(self.effective):
            self.effective[self.pos] = changed
        else:
            self.effective.append(changed)
        self.pos += 1
        if self.pos % CHECKPOINT_EVERY == 0 and self.pos not in self.checkpoints:
            self.checkpoints[self.pos] = self.state.copy()
        return True

    def back(self):
        if self.pos == 0:
            return False
        self.pos -= 1
        if self.effective[self.pos]:
            self.state.apply(INVERSE[self.ops[self.pos]])
        return True

    def seek(self, target):
        target = max(0, min(target, len(self.ops)))
        if target < self.pos or target - self.pos > CHECKPOINT_EVERY:
            cp = max(k for k in self.checkpoints if k <= target)
            self.pos, self.state = cp, self.checkpoints[cp].copy()
        while self.pos < target:
            self.forward()

    def counts(self):
        c = dict.fromkeys(OPS, 0)
        for op in self.ops[:self.pos]:
            c[op] += 1
        return c


# ------------------------------------------------------------------- runner
def to_ranks(values):
    order = sorted(values)
    idx = {v: i for i, v in enumerate(order)}
    return [idx[v] for v in values]


def run_push_swap(binary, strategy, values):
    cmd = [binary, f"--{strategy}", "--bench", *map(str, values)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, [], f"failed to run {binary}: {e}"
    if p.stderr.strip() == "Error":
        return None, [], "push_swap printed Error"
    lines = p.stdout.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    for i, op in enumerate(lines):
        if op not in OPS:
            return None, [], f"invalid op on line {i + 1}: {op!r}"
    bench = [l for l in p.stderr.splitlines() if l.strip()]
    return lines, bench, None


# ----------------------------------------------------------------------- UI
def colour(rank, n):
    t = rank / max(1, n - 1)
    r = int(40 + 215 * t)
    g = int(90 + 80 * (1 - abs(t - 0.5) * 2))
    b = int(255 - 215 * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class App:
    W, H = 1000, 640

    def __init__(self, root, args):
        self.root, self.args = root, args
        self.hist = None
        self.playing = False
        self.values = args.numbers or random.sample(range(-1000, 1000), args.n)
        self._build()
        self.run()

    # layout
    def _build(self):
        top = ttk.Frame(self.root); top.pack(fill="x", padx=6, pady=4)
        self.strategy = tk.StringVar(value=self.args.strategy)
        ttk.OptionMenu(top, self.strategy, self.args.strategy,
                       "adaptive", "simple", "medium", "complex").pack(side="left")
        ttk.Label(top, text="  N").pack(side="left")
        self.n_var = tk.IntVar(value=len(self.values))
        ttk.Entry(top, textvariable=self.n_var, width=6).pack(side="left")
        ttk.Button(top, text="Random", command=self.randomise).pack(side="left", padx=4)
        ttk.Button(top, text="Run", command=self.run).pack(side="left")

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#111", highlightthickness=0)
        self.canvas.pack()

        ctl = ttk.Frame(self.root); ctl.pack(fill="x", padx=6, pady=4)
        for text, cmd in (("⏮", lambda: self.seek(0)), ("◀", self.step_back),
                          ("▶/❚❚", self.toggle), ("▶|", self.step),
                          ("⏭", lambda: self.seek(len(self.hist.ops)))):
            ttk.Button(ctl, text=text, width=5, command=cmd).pack(side="left")
        ttk.Label(ctl, text="  speed").pack(side="left")
        self.speed = tk.IntVar(value=120)
        ttk.Scale(ctl, from_=1, to=2000, variable=self.speed,
                  length=200).pack(side="left")
        self.scrub = tk.IntVar(value=0)
        self.scrubber = ttk.Scale(ctl, from_=0, to=1, variable=self.scrub,
                                  command=lambda v: self.seek(int(float(v))))
        self.scrubber.pack(side="left", fill="x", expand=True, padx=6)

        self.info = tk.StringVar()
        ttk.Label(self.root, textvariable=self.info, font=("Courier", 10),
                  justify="left").pack(fill="x", padx=6, pady=4)

        self.root.bind("<space>", lambda e: self.toggle())
        self.root.bind("<Right>", lambda e: self.step())
        self.root.bind("<Left>", lambda e: self.step_back())
        self.root.bind("<Home>", lambda e: self.seek(0))
        self.root.bind("<End>", lambda e: self.seek(len(self.hist.ops)))

    # actions
    def randomise(self):
        n = max(1, self.n_var.get())
        self.values = random.sample(range(-10 * n, 10 * n), n)
        self.run()

    def run(self):
        self.playing = False
        ops, bench, err = run_push_swap(self.args.binary,
                                        self.strategy.get(), self.values)
        self.bench = bench
        self.error = err
        self.hist = History(to_ranks(self.values), ops or [])
        self.n = len(self.values)
        self.scrubber.configure(to=max(1, len(self.hist.ops)))
        self._create_bars()
        self.redraw()

    def toggle(self):
        self.playing = not self.playing
        if self.playing:
            self.tick()

    def step(self):
        self.hist.forward(); self.redraw()

    def step_back(self):
        self.hist.back(); self.redraw()

    def seek(self, i):
        self.hist.seek(i); self.redraw()

    def tick(self):
        if not self.playing:
            return
        per_tick = max(1, self.speed.get() // 60)
        for _ in range(per_tick):
            if not self.hist.forward():
                self.playing = False
                break
        self.redraw()
        if self.playing:
            self.root.after(16, self.tick)

    # drawing
    def _create_bars(self):
        self.canvas.delete("all")
        self.bars = [self.canvas.create_rectangle(0, 0, 0, 0, width=0,
                                                  fill=colour(r, self.n))
                     for r in range(self.n)]
        self.canvas.create_line(self.W // 2, 0, self.W // 2, self.H, fill="#444")

    def redraw(self):
        st, n = self.hist.state, self.n
        bh = self.H / max(1, n)
        half = self.W // 2 - 10
        for x0, stack in ((5, st.a), (self.W // 2 + 5, st.b)):
            for i, rank in enumerate(stack):
                w = 2 + half * (rank + 1) / n
                self.canvas.coords(self.bars[rank], x0, i * bh, x0 + w,
                                   (i + 1) * bh)
        self.scrub.set(self.hist.pos)
        self._update_info()

    def _update_info(self):
        h = self.hist
        last = h.ops[h.pos - 1] if h.pos else "-"
        counts = "  ".join(f"{k} {v}" for k, v in h.counts().items())
        if self.error:
            result = f"ERROR: {self.error}"
        elif h.pos == len(h.ops):
            result = "OK" if h.state.is_sorted() else "KO"
        else:
            result = "…"
        self.info.set(f"op {h.pos}/{len(h.ops)}   last: {last}   "
                      f"result: {result}\n{counts}\n" + "\n".join(self.bench))


def main():
    ap = argparse.ArgumentParser(description="push_swap visualiser")
    ap.add_argument("numbers", nargs="*", type=int)
    ap.add_argument("-n", type=int, default=100, help="random count if no numbers")
    ap.add_argument("-s", "--strategy", default="adaptive",
                    choices=["adaptive", "simple", "medium", "complex"])
    ap.add_argument("-b", "--binary", default="../push_swap")
    args = ap.parse_args()
    if len(set(args.numbers)) != len(args.numbers):
        ap.error("duplicate numbers")
    root = tk.Tk()
    root.title("push_swap visualiser")
    App(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
```

Notes on the reference code:

- `counts()` is O(pos) per redraw — fine up to ~10 k ops. For `--simple` on 500
  (60 k+ ops) maintain counts incrementally in `forward`/`back` instead.
- Bars are indexed **by rank**, so each rank owns one rectangle that just moves
  between stacks — no create/delete per frame.
- `History.seek` jumps via checkpoints, so dragging the scrubber stays responsive.
- negative numbers on the CLI: `python3 visualizer.py -- -5 3 -1` (the `--` stops
  argparse treating `-5` as an option).

---

## 8. Usage

```sh
cd do_not_commit
python3 visualizer.py                          # 100 random, adaptive
python3 visualizer.py -n 500 -s complex        # 500 random, radix/quick
python3 visualizer.py -s simple 5 4 3 2 1      # specific input
python3 visualizer.py -b ../push_swap -- -3 7 -1 0
```

On 42 machines tkinter is normally available with the system Python
(`python3 -c "import tkinter"` to check). If running over SSH, you need X
forwarding (`ssh -X`).

---

## 9. Debugging workflows

| Symptom | How the visualiser helps |
|---------|--------------------------|
| KO from checker | Scrub to the end, step back until the wrong element appears; the op log tells you which phase of the algorithm misbehaved. |
| Too many ops on medium | Watch phase 1: if a is rotated full circle many times per chunk, chunk size is too small; if b ends up badly interleaved (long `rb`/`rrb` hunts in phase 2), it's too large. |
| Radix count higher than 2n·log n | Watch for wasted passes when a is already sorted mid-way. |
| Adaptive picks the wrong regime | Read `[bench] disorder` vs. strategy line in the info panel. Use the disorder generator (§10) to test values near 0.2 and 0.5. |
| Peephole optimiser not catching things | Enable the wasted-move lint (§10) — any remaining `ra rra` / `pa pb` / `ra rb` pair is highlighted. |

---

## 10. Stretch goals

1. **Wasted-move lint**: scan `ops` once, mark indices of cancellable/mergeable
   adjacent pairs, show count + jump-to-next button.
2. **Disorder slider**: generate input with a target disorder (start sorted,
   apply random adjacent/remote swaps until inversion ratio ≈ target). Display
   computed disorder in the UI and compare with push_swap's `[bench]` value
   (they must match — a free test for `disorder.c`).
3. **Compare mode**: run two strategies on the same input; render both pairs of
   stacks one above the other and play in lock-step; final counts side-by-side.
4. **Batch benchmark tab**: run K random inputs per strategy for n = 100 / 500,
   plot histogram of op counts with the 700/1500/2000 and 5500/8000/12000 lines.
   (`matplotlib` if available, else draw on the canvas.)
5. **Stdin / file mode**: `./push_swap 3 1 2 | python3 visualizer.py --ops - 3 1 2`
   to visualise any op stream, including hand-written checker tests.
6. **Web port**: reuse the same simulator logic in a single HTML file
   (paste numbers + ops) for sharing with peers who don't have the repo.
7. **GIF export**: save frames (`canvas.postscript` → convert) for the README or
   evaluation demo.

---

## 11. Build checklist

- [ ] `sim.Stacks` — all 11 ops, no-op edge cases (empty/single-element stacks)
- [ ] Unit test: random op sequences, apply then undo → original state
- [ ] Unit test: simulator result matches `checker_linux` OK/KO on 100 random runs
- [ ] `runner` — Error handling, invalid op lines, timeout
- [ ] Canvas rendering with persistent per-rank rectangles
- [ ] Play / pause / step / step back / seek / speed
- [ ] Info panel: position, last op, live counts, bench lines, OK/KO
- [ ] Keyboard shortcuts
- [ ] Handles n = 1, n = 2, already-sorted (0 ops), n = 500 smoothly
- [ ] Never committed (`do_not_commit/` in `.gitignore`)
