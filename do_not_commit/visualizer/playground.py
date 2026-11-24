#!/usr/bin/env python3
"""Interactive push_swap playground: type numbers, run ops by hand, replay.

  python3 playground.py                       subject example 2 1 3 6 5 8
  python3 playground.py 5 4 3 2 1
  python3 playground.py --ops "sa pb pb pb rr rrr sa pa pa pa" 2 1 3 6 5 8
  python3 playground.py -- -3 7 -1            negative numbers need --
"""
import argparse
import random
import re
import time
import tkinter as tk
from tkinter import messagebox, ttk

from sim import OPS, History, disorder, to_ranks
from sound import Sound
from themes import DEFAULT_THEME, THEMES, apply_ttk, gradient

INT_RE = re.compile(r"[+-]?\d+")
INT_MIN, INT_MAX = -2 ** 31, 2 ** 31 - 1
DEFAULT_NUMBERS = [2, 1, 3, 6, 5, 8]
OP_GRID = (("sa", "sb", "ss"), ("pa", "pb", None),
           ("ra", "rb", "rr"), ("rra", "rrb", "rrr"))
FRAME_MS = 16
ROW_MAX = 30                     # max bar height in px
TEXT_MIN = 12                    # draw values only if bars are this tall


def parse_numbers(text):
    """push_swap-style validation. Returns (values, error)."""
    tokens = text.replace(",", " ").split()
    if not tokens:
        return None, "enter some numbers"
    values = []
    for tok in tokens:
        if not INT_RE.fullmatch(tok):
            return None, f"not an integer: {tok!r}"
        v = int(tok)
        if not INT_MIN <= v <= INT_MAX:
            return None, f"out of int range: {tok}"
        values.append(v)
    if len(set(values)) != len(values):
        dup = next(v for v in values if values.count(v) > 1)
        return None, f"duplicate: {dup}"
    return values, None


def parse_ops(text):
    """Split typed ops on whitespace/commas/semicolons. Returns (ops, error)."""
    ops = re.split(r"[\s,;]+", text.strip())
    ops = [op.lower() for op in ops if op]
    bad = [op for op in ops if op not in OPS]
    if bad:
        return None, f"unknown op: {bad[0]!r}  (valid: {' '.join(OPS)})"
    return ops, None


def speed_from_slider(v):
    """Slider 0..100 -> 0.5..50 ops/s."""
    return 0.5 * 100 ** (float(v) / 100)


class Playground:
    def __init__(self, root, args):
        self.root = root
        self.theme = THEMES[args.theme]
        self.sound = Sound()
        self.values = []
        self.ranks_to_value = []
        self.hist = History([], [])
        self.lit = []
        self.playing = False
        self.syncing = False
        self.budget = 0.0
        self.last_tick = 0.0
        self.cmd_history, self.cmd_index = [], 0
        self.message = ("", "dim")
        self._build(args)
        self.apply_theme(args.theme)
        if not args.mute:
            self.sound_var.set(True)
            self.toggle_sound()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.load_numbers(" ".join(map(str, args.numbers or DEFAULT_NUMBERS)),
                          confirm=False)
        if args.ops:
            self.run_command(args.ops)

    # ------------------------------------------------------------ layout
    def _build(self, args):
        root = self.root
        self.style = ttk.Style(root)
        self.style.theme_use("clam")

        # numbers row
        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(top, text="numbers (first = top of a)").pack(side="left")
        self.numbers_var = tk.StringVar()
        self.numbers_entry = ttk.Entry(top, textvariable=self.numbers_var,
                                       width=40)
        self.numbers_entry.pack(side="left", padx=6, fill="x", expand=True)
        self.numbers_entry.bind(
            "<Return>", lambda e: self.load_numbers(self.numbers_var.get()))
        ttk.Button(top, text="Load", command=lambda: self.load_numbers(
            self.numbers_var.get())).pack(side="left")
        ttk.Label(top, text="  random N").pack(side="left")
        self.n_var = tk.IntVar(value=8)
        n_entry = ttk.Entry(top, textvariable=self.n_var, width=4)
        n_entry.pack(side="left", padx=4)
        n_entry.bind("<Return>", lambda e: self.randomise())
        ttk.Button(top, text="Random", command=self.randomise).pack(
            side="left")
        ttk.Label(top, text="   theme").pack(side="left")
        self.theme_var = tk.StringVar(value=args.theme)
        ttk.OptionMenu(top, self.theme_var, args.theme, *THEMES,
                       command=self.apply_theme).pack(side="left", padx=4)
        self.sound_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="sound", variable=self.sound_var,
                        command=self.toggle_sound).pack(side="left",
                                                        padx=(8, 0))

        # middle: canvas + history
        mid = ttk.Frame(root)
        self.canvas = tk.Canvas(mid, width=760, height=460,
                                highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        side = ttk.Frame(mid)
        side.pack(side="right", fill="y", padx=(8, 0))
        ttk.Label(side, text="history (click to jump)",
                  style="Dim.TLabel").pack(anchor="w")
        box = ttk.Frame(side)
        box.pack(fill="y", expand=True)
        self.log = tk.Listbox(box, width=16, borderwidth=0,
                              highlightthickness=0, font=("Courier", 11),
                              activestyle="none", exportselection=False)
        sb = ttk.Scrollbar(box, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        self.log.pack(side="left", fill="y", expand=True)
        sb.pack(side="left", fill="y")
        self.log.bind("<<ListboxSelect>>", self._on_log_click)
        btns = ttk.Frame(side)
        btns.pack(fill="x", pady=(4, 0))
        ttk.Button(btns, text="Copy ops", command=self.copy_ops).pack(
            side="left", fill="x", expand=True)
        ttk.Button(btns, text="Reset", command=self.reset).pack(
            side="left", fill="x", expand=True)

        # ops: buttons + typed command
        opf = ttk.Frame(root)
        grid = ttk.Frame(opf)
        grid.pack(side="left")
        for c, column in enumerate(OP_GRID):
            for r, op in enumerate(column):
                if op:
                    ttk.Button(grid, text=op, width=5,
                               command=lambda o=op: self.run_ops([o])).grid(
                        row=r, column=c, padx=1, pady=1)
        cmd = ttk.Frame(opf)
        cmd.pack(side="left", fill="both", expand=True, padx=(12, 0))
        ttk.Label(cmd, text="type ops and press Enter  "
                            "(e.g.  pb pb ra rra pa)  — ↑/↓ recalls").pack(
            anchor="w")
        row = ttk.Frame(cmd)
        row.pack(fill="x", pady=4)
        self.cmd_var = tk.StringVar()
        self.cmd_entry = ttk.Entry(row, textvariable=self.cmd_var,
                                   font=("Courier", 12))
        self.cmd_entry.pack(side="left", fill="x", expand=True)
        self.cmd_entry.bind("<Return>",
                            lambda e: self.run_command(self.cmd_var.get()))
        self.cmd_entry.bind("<Up>", lambda e: self._recall(-1))
        self.cmd_entry.bind("<Down>", lambda e: self._recall(1))
        ttk.Button(row, text="Run", command=lambda: self.run_command(
            self.cmd_var.get())).pack(side="left", padx=(4, 0))
        self.msg_label = ttk.Label(cmd, style="Mono.TLabel")
        self.msg_label.pack(anchor="w")

        # replay controls
        ctl = ttk.Frame(root)
        for text, fn in (("⏮", lambda: self.seek(0)),
                         ("◀ undo", self.step_back),
                         ("▶ replay / ❚❚", self.toggle_play),
                         ("redo ▶", self.step),
                         ("⏭", lambda: self.seek(len(self.hist)))):
            ttk.Button(ctl, text=text, command=fn).pack(side="left", padx=1)
        ttk.Label(ctl, text="  speed").pack(side="left")
        self.speed_var = tk.DoubleVar(value=50)
        ttk.Scale(ctl, from_=0, to=100, variable=self.speed_var, length=120,
                  command=lambda v: self._show_speed()).pack(side="left")
        self.speed_label = ttk.Label(ctl, width=9)
        self.speed_label.pack(side="left")
        self._show_speed()
        self.scrub = ttk.Scale(ctl, from_=0, to=1, command=self._on_scrub)
        self.scrub.pack(side="left", fill="x", expand=True, padx=6)

        info = ttk.Frame(root)
        self.status = ttk.Label(info, style="Mono.TLabel")
        self.status.pack(anchor="w")
        self.counts_label = ttk.Label(info, style="Mono.TLabel")
        self.counts_label.pack(anchor="w")

        info.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        ctl.pack(side="bottom", fill="x", padx=8, pady=4)
        opf.pack(side="bottom", fill="x", padx=8, pady=4)
        mid.pack(fill="both", expand=True, padx=8)

        for key, fn in (("<Control-z>", self.step_back),
                        ("<Control-y>", self.step),
                        ("<Control-Z>", self.step),
                        ("<Left>", self.step_back), ("<Right>", self.step),
                        ("<space>", self.toggle_play),
                        ("<Home>", lambda: self.seek(0)),
                        ("<End>", lambda: self.seek(len(self.hist)))):
            root.bind(key, self._key(fn, ctrl=key.startswith("<Control")))
        self.cmd_entry.focus_set()

    def _key(self, fn, ctrl=False):
        def handler(event):
            # plain keys belong to the entry being typed in; Ctrl keys don't
            if not ctrl and isinstance(event.widget, (tk.Entry, ttk.Entry)):
                return None
            fn()
            return "break"
        return handler

    # ------------------------------------------------------------ theme/sound
    def apply_theme(self, name):
        self.theme_var.set(name)
        th = self.theme = THEMES[name]
        apply_ttk(self.root, self.style, th)
        self.canvas.configure(bg=th["bg"])
        self.log.configure(bg=th["panel"], fg=th["fg"],
                           selectbackground=th["select"],
                           selectforeground="#ffffff")
        if self.values:
            self.redraw()

    def toggle_sound(self):
        on = self.sound_var.get()
        if on and not self.sound.proc and not self.sound.start():
            self.sound_var.set(False)
            self._say(f"sound unavailable: {self.sound.error}", "ko")
            on = False
        self.sound.enabled = on

    def _play_note(self):
        op = self.hist.last_op()
        if op and self.lit and self.sound.enabled:
            dur = 0.12 if not self.playing else \
                min(0.12, max(0.04, 1 / speed_from_slider(
                    self.speed_var.get())))
            self.sound.note(op, self.lit[0], len(self.values), round(dur, 3))

    def quit(self):
        self.sound.stop()
        self.root.destroy()

    # ------------------------------------------------------------ input
    def load_numbers(self, text, confirm=True):
        values, err = parse_numbers(text)
        if err:
            self._say(f"numbers: {err}", "ko")
            return
        if confirm and len(self.hist) and not messagebox.askyesno(
                "Load numbers", "Loading new numbers clears the history. "
                                "Continue?", parent=self.root):
            return
        self.playing = False
        self.values = values
        self.ranks_to_value = sorted(values)
        self.numbers_var.set(" ".join(map(str, values)))
        self.hist = History(to_ranks(values), [])
        self._say(f"loaded {len(values)} numbers, disorder "
                  f"{disorder(values) * 100:.2f}%", "dim")
        self._refresh_log()
        self.redraw()
        self.cmd_entry.focus_set()

    def randomise(self):
        try:
            n = min(500, max(1, int(self.n_var.get())))
        except (tk.TclError, ValueError):
            n = 8
        self.n_var.set(n)
        nums = random.sample(range(-max(50, 5 * n), max(50, 5 * n)), n)
        self.load_numbers(" ".join(map(str, nums)))

    def reset(self):
        if len(self.hist) and messagebox.askyesno(
                "Reset", "Clear all ops and go back to the starting stack?",
                parent=self.root):
            self.load_numbers(" ".join(map(str, self.values)), confirm=False)

    def run_command(self, text):
        ops, err = parse_ops(text)
        if err:
            self._say(err, "ko")
            return
        if not ops:
            return
        if not self.cmd_history or self.cmd_history[-1] != text.strip():
            self.cmd_history.append(text.strip())
        self.cmd_index = len(self.cmd_history)
        self.cmd_var.set("")
        self.run_ops(ops)

    def run_ops(self, ops):
        self.playing = False
        dropped = 0
        for op in ops:
            dropped += self.hist.push(op)
        msg = f"ran {' '.join(ops)}" if len(ops) <= 12 else \
            f"ran {len(ops)} ops"
        if dropped:
            msg += f"  (discarded {dropped} later op{'s' * (dropped > 1)})"
        self._say(msg, "dim")
        self._refresh_log()
        self.redraw()
        self._play_note()

    def _recall(self, d):
        if not self.cmd_history:
            return "break"
        self.cmd_index = min(len(self.cmd_history),
                             max(0, self.cmd_index + d))
        self.cmd_var.set(self.cmd_history[self.cmd_index]
                         if self.cmd_index < len(self.cmd_history) else "")
        self.cmd_entry.icursor("end")
        return "break"

    def copy_ops(self):
        ops = self.hist.ops[:self.hist.pos]
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(ops) + ("\n" if ops else ""))
        self._say(f"copied {len(ops)} ops (up to the cursor) to the "
                  f"clipboard", "dim")

    def _say(self, text, tone):
        self.message = (text, tone)
        self.msg_label.configure(text=text, foreground=self.theme[tone])

    # ------------------------------------------------------------ replay
    def toggle_play(self):
        if not self.playing and self.hist.pos >= len(self.hist):
            if not len(self.hist):
                return
            self.seek(0)
        self.playing = not self.playing
        if self.playing:
            self.budget = 1.0                      # first step immediately
            self.last_tick = time.perf_counter()
            self._tick()
        else:
            self._update_info()

    def _tick(self):
        if not self.playing:
            return
        now = time.perf_counter()
        self.budget += (now - self.last_tick) * speed_from_slider(
            self.speed_var.get())
        self.last_tick = now
        steps = int(self.budget)
        self.budget -= steps
        for _ in range(steps):
            if not self.hist.forward():
                self.playing = False
                break
        if steps:
            self.redraw()
            self._play_note()
        if self.playing:
            self.root.after(FRAME_MS, self._tick)

    def step(self):
        self.playing = False
        if self.hist.forward():
            self.redraw()
            self._play_note()

    def step_back(self):
        self.playing = False
        if self.hist.back():
            self.redraw()
            self._play_note()

    def seek(self, i):
        self.hist.seek(int(i))
        self.redraw()

    def _show_speed(self):
        self.speed_label.configure(
            text=f"{speed_from_slider(self.speed_var.get()):.1f} op/s")

    def _on_scrub(self, v):
        if not self.syncing:
            self.playing = False
            self.seek(round(float(v)))

    def _on_log_click(self, _):
        sel = self.log.curselection()
        if sel and not self.syncing:
            self.playing = False
            self.seek(sel[0])           # row 0 = start, row k = after op k

    def _refresh_log(self):
        self.log.delete(0, "end")
        ops = self.hist.ops
        width = len(str(len(ops)))
        self.log.insert("end", f"{0:>{width}} (start)")
        self.log.insert("end", *(f"{i + 1:>{width}} {op}"
                                 for i, op in enumerate(ops)))
        self.scrub.configure(to=max(1, len(ops)))

    # ------------------------------------------------------------ drawing
    def redraw(self):
        c, th = self.canvas, self.theme
        c.delete("all")
        W, H = c.winfo_width(), c.winfo_height()
        n = max(1, len(self.values))
        st = self.hist.state
        head = 28
        bh = min(ROW_MAX, (H - head - 6) / n)
        gap = 2 if bh >= 8 else 0
        col_w = W // 2
        bar_max = col_w - 80

        op = self.hist.last_op()
        self.lit = st.touched(op) if op else []
        lit = set(self.lit)
        font_px = max(8, min(12, int(bh * 0.6)))
        for col, (name, stack) in enumerate((("a", st.a), ("b", st.b))):
            x0 = col * col_w + 12
            c.create_text(x0, 6, anchor="nw", fill=th["dim"],
                          text=f"stack {name}  ({len(stack)})   ↑ top",
                          font=("TkDefaultFont", 10))
            for i, rank in enumerate(stack):
                y = head + i * bh
                w = 4 + bar_max * (rank + 1) / n
                hl = rank in lit
                c.create_rectangle(
                    x0, y, x0 + w, y + bh - gap,
                    fill=gradient(th["gradient"], rank / max(1, n - 1)),
                    outline=th["highlight"] if hl else "",
                    width=2 if hl else 0)
                if bh >= TEXT_MIN:
                    c.create_text(x0 + w + 6, y + (bh - gap) / 2, anchor="w",
                                  text=str(self.ranks_to_value[rank]),
                                  fill=th["highlight"] if hl else th["fg"],
                                  font=("Courier", font_px,
                                        "bold" if hl else "normal"))
        c.create_line(col_w, 0, col_w, H, fill=th["divider"])
        if op:
            c.create_text(W - 10, H - 8, anchor="se", text=op,
                          fill=th["dim"], font=("Courier", 28, "bold"))
        self._sync_widgets()
        self._update_info()

    def _sync_widgets(self):
        self.syncing = True
        self.scrub.set(self.hist.pos)
        self.log.selection_clear(0, "end")
        self.log.selection_set(self.hist.pos)
        self.log.see(self.hist.pos)
        self.syncing = False

    def _update_info(self):
        h, th = self.hist, self.theme
        if h.state.is_sorted():
            state, col = "SORTED ✓  (a ascending, b empty)", th["ok"]
        elif not h.state.b and len(h.state.a) == len(self.values):
            state, col = "not sorted", th["fg"]
        else:
            state, col = f"not sorted  ({len(h.state.b)} in b)", th["fg"]
        where = f"op {h.pos}/{len(h)}"
        if h.pos < len(h):
            where += (f"  ◀ viewing history — running an op here discards "
                      f"{len(h) - h.pos} later")
            col = th["select"] if not h.state.is_sorted() else col
        if self.playing:
            where += "  ▶ replaying"
        self.status.configure(text=f"{where}   |   {state}", foreground=col)
        self.counts_label.configure(
            text="  ".join(f"{o} {h.counts[o]}" for o in OPS))


def main():
    ap = argparse.ArgumentParser(description="interactive push_swap playground")
    ap.add_argument("numbers", nargs="*", help="initial stack a (first = top)")
    ap.add_argument("--ops", help='ops to run at start, e.g. "sa pb pb"')
    ap.add_argument("-t", "--theme", default=DEFAULT_THEME,
                    choices=list(THEMES))
    ap.add_argument("--mute", action="store_true", help="start with sound off")
    args = ap.parse_args()
    if args.numbers:
        vals, err = parse_numbers(" ".join(args.numbers))
        if err:
            ap.error(err)
        args.numbers = vals
    root = tk.Tk()
    root.title("push_swap playground")
    root.geometry("1050x760")
    root.minsize(800, 600)
    Playground(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
