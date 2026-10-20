"""tkinter front-end for the push_swap visualiser."""
import random
import time
import tkinter as tk
from tkinter import ttk

from runner import read_ops_file, run_push_swap
from sim import OPS, History, disorder, to_ranks, wasted_moves
from sound import Sound
from themes import THEMES, gradient

STRATEGIES = ("adaptive", "simple", "medium", "complex")
FRAME_MS = 16


def speed_from_slider(v):
    """Slider 0..100 -> 1..3000 ops/s, exponential."""
    return round(3000 ** (float(v) / 100))


class App:
    def __init__(self, root, args):
        self.root = root
        self.args = args
        self.ops_mode = args.ops is not None
        self.values = list(args.numbers) or random.sample(
            range(-10 * args.n, 10 * args.n), args.n)
        self.hist = History([], [])
        self.n = 0
        self.bars = []
        self.lit = []
        self.waste = []
        self.playing = False
        self.syncing = False
        self.budget = 0.0
        self.last_tick = 0.0
        self.W, self.H = 900, 600
        self.theme = THEMES[args.theme]
        self.sound = Sound()
        self._build()
        self.apply_theme(args.theme)
        if not args.mute:
            self.sound_var.set(True)
            self.toggle_sound()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.load()

    # ------------------------------------------------------------ layout
    def _build(self):
        root = self.root
        self.style = ttk.Style(root)
        self.style.theme_use("clam")

        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=6)
        self.strategy = tk.StringVar(value=self.args.strategy)
        self.n_var = tk.IntVar(value=len(self.values))
        ttk.Label(top, text="strategy").pack(side="left")
        self.strategy_menu = ttk.OptionMenu(
            top, self.strategy, self.args.strategy, *STRATEGIES,
            command=lambda _: self.load())
        self.strategy_menu.pack(side="left", padx=(4, 12))
        ttk.Label(top, text="N").pack(side="left")
        self.n_entry = ttk.Entry(top, textvariable=self.n_var, width=6)
        self.n_entry.pack(side="left", padx=4)
        self.n_entry.bind("<Return>", lambda e: self.randomise())
        self.random_btn = ttk.Button(top, text="Random",
                                     command=self.randomise)
        self.random_btn.pack(side="left", padx=4)
        self.run_btn = ttk.Button(top, text="Re-run", command=self.load)
        self.run_btn.pack(side="left")
        if self.ops_mode:
            for w in (self.n_entry, self.random_btn, self.run_btn,
                      self.strategy_menu):
                w.state(["disabled"])

        ttk.Label(top, text="   theme").pack(side="left")
        self.theme_var = tk.StringVar(value=self.args.theme)
        ttk.OptionMenu(top, self.theme_var, self.args.theme, *THEMES,
                       command=self.apply_theme).pack(side="left", padx=4)
        self.sound_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="sound", variable=self.sound_var,
                        command=self.toggle_sound).pack(side="left",
                                                        padx=(12, 2))
        self.volume_var = tk.DoubleVar(value=self.sound.volume * 100)
        ttk.Scale(top, from_=0, to=100, variable=self.volume_var, length=80,
                  command=self._set_volume).pack(side="left")

        src = f"ops: {self.args.ops}" if self.ops_mode else \
            f"binary: {self.args.binary}"
        ttk.Label(top, text=src, style="Dim.TLabel").pack(side="right")

        mid = ttk.Frame(root)
        self.canvas = tk.Canvas(mid, width=self.W, height=self.H,
                                highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        side = ttk.Frame(mid)
        side.pack(side="right", fill="y", padx=(8, 0))
        ttk.Label(side, text="op log", style="Dim.TLabel").pack(anchor="w")
        self.log = tk.Listbox(side, width=14, borderwidth=0,
                              highlightthickness=0, font=("Courier", 10),
                              activestyle="none", exportselection=False)
        sb = ttk.Scrollbar(side, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        self.log.pack(side="left", fill="y")
        sb.pack(side="left", fill="y")
        self.log.bind("<<ListboxSelect>>", self._on_log_click)

        ctl = ttk.Frame(root)
        for text, cmd in (("⏮", lambda: self.seek(0)),
                          ("◀", self.step_back),
                          ("▶ / ❚❚", self.toggle),
                          ("▶|", self.step),
                          ("⏭", lambda: self.seek(len(self.hist)))):
            ttk.Button(ctl, text=text, width=6, command=cmd).pack(side="left")
        ttk.Label(ctl, text="  speed").pack(side="left")
        self.speed_var = tk.DoubleVar(value=55)
        ttk.Scale(ctl, from_=0, to=100, variable=self.speed_var, length=160,
                  command=lambda v: self._show_speed()).pack(side="left")
        self.speed_label = ttk.Label(ctl, width=10)
        self.speed_label.pack(side="left")
        self._show_speed()
        self.scrub = ttk.Scale(ctl, from_=0, to=1, command=self._on_scrub)
        self.scrub.pack(side="left", fill="x", expand=True, padx=6)

        info = ttk.Frame(root)
        self.status = ttk.Label(info, style="Mono.TLabel")
        self.status.pack(anchor="w")
        self.counts_label = ttk.Label(info, style="Mono.TLabel")
        self.counts_label.pack(anchor="w")
        row = ttk.Frame(info)
        row.pack(anchor="w", fill="x")
        self.waste_label = ttk.Label(row, style="Mono.TLabel")
        self.waste_label.pack(side="left")
        ttk.Button(row, text="next waste", command=self.next_waste).pack(
            side="left", padx=8)
        self.sound_label = ttk.Label(row, style="Dim.TLabel")
        self.sound_label.pack(side="left", padx=8)
        self.bench_label = ttk.Label(info, style="Mono.TLabel",
                                     justify="left")
        self.bench_label.pack(anchor="w")

        # bottom-up so the canvas is the one that shrinks on small windows
        info.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        ctl.pack(side="bottom", fill="x", padx=8, pady=6)
        mid.pack(fill="both", expand=True, padx=8)

        for key, fn in (("<space>", self.toggle), ("<Right>", self.step),
                        ("<Left>", self.step_back),
                        ("<Home>", lambda: self.seek(0)),
                        ("<End>", lambda: self.seek(len(self.hist))),
                        ("<plus>", lambda: self._nudge_speed(5)),
                        ("<equal>", lambda: self._nudge_speed(5)),
                        ("<minus>", lambda: self._nudge_speed(-5)),
                        ("<m>", self._toggle_mute_key),
                        ("<t>", self._next_theme)):
            root.bind(key, self._key(fn))

    def _key(self, fn):
        def handler(event):
            if isinstance(event.widget, (tk.Entry, ttk.Entry)):
                return None
            fn()
            return "break"
        return handler

    # ------------------------------------------------------------ theme
    def apply_theme(self, name):
        self.theme_var.set(name)
        th = self.theme = THEMES[name]
        bg, fg, panel, btn = th["bg"], th["fg"], th["panel"], th["button"]
        s = self.style
        self.root.configure(bg=bg)
        for w in ("TFrame", "TLabel", "TCheckbutton"):
            s.configure(w, background=bg, foreground=fg)
        s.map("TCheckbutton", background=[("active", bg)],
              indicatorbackground=[("selected", th["select"]),
                                   ("!selected", panel)])
        s.configure("Dim.TLabel", background=bg, foreground=th["dim"])
        s.configure("Mono.TLabel", background=bg, foreground=fg,
                    font=("Courier", 10))
        for w in ("TButton", "TMenubutton"):
            s.configure(w, background=btn, foreground=fg,
                        bordercolor=th["divider"], lightcolor=btn,
                        darkcolor=btn, arrowcolor=fg)
            s.map(w, background=[("disabled", bg), ("active", th["select"])],
                  foreground=[("disabled", th["dim"]), ("active", fg)])
        s.configure("TEntry", fieldbackground=panel, foreground=fg,
                    insertcolor=fg, bordercolor=th["divider"])
        s.map("TEntry", fieldbackground=[("disabled", bg)],
              foreground=[("disabled", th["dim"])])
        s.configure("Horizontal.TScale", background=btn,
                    troughcolor=panel, bordercolor=th["divider"],
                    lightcolor=btn, darkcolor=btn)
        s.configure("Vertical.TScrollbar", background=btn, troughcolor=panel,
                    bordercolor=th["divider"], arrowcolor=fg,
                    lightcolor=btn, darkcolor=btn)
        self.root.option_add("*Menu.background", panel)
        self.root.option_add("*Menu.foreground", fg)
        self.root.option_add("*Menu.activeBackground", th["select"])

        self.canvas.configure(bg=bg)
        self.canvas.itemconfigure("divider", fill=th["divider"])
        self.canvas.itemconfigure("label", fill=th["dim"])
        for rank, bar in enumerate(self.bars):
            self.canvas.itemconfigure(bar, fill=self._bar_colour(rank))
        self.log.configure(bg=panel, fg=fg, selectbackground=th["select"],
                           selectforeground="#ffffff")
        self._paint_waste()
        self.lit, old = [], self.lit
        for r in old:
            self.canvas.itemconfigure(self.bars[r], outline="", width=0)
        if self.n:
            self.redraw()

    def _next_theme(self):
        names = list(THEMES)
        self.apply_theme(names[(names.index(self.theme_var.get()) + 1)
                               % len(names)])

    def _bar_colour(self, rank):
        return gradient(self.theme["gradient"], rank / max(1, self.n - 1))

    # ------------------------------------------------------------ sound
    def toggle_sound(self):
        on = self.sound_var.get()
        if on and not self.sound.proc:
            if not self.sound.start():
                self.sound_var.set(False)
                on = False
        self.sound.enabled = on
        self._show_sound_status()

    def _toggle_mute_key(self):
        self.sound_var.set(not self.sound_var.get())
        self.toggle_sound()

    def _set_volume(self, v):
        self.sound.volume = round(float(v)) / 100

    def _show_sound_status(self):
        if self.sound.error and not self.sound.proc:
            text = f"sound unavailable: {self.sound.error}"
        elif self.sound.enabled:
            text = f"sound: {self.sound.player}"
        else:
            text = "sound off (m)"
        self.sound_label.configure(text=text)

    def _play_note(self):
        """Tone for the op that produced the current state."""
        op = self.hist.last_op()
        if not (op and self.lit and self.sound.enabled):
            return
        speed = speed_from_slider(self.speed_var.get()) if self.playing else 8
        duration = min(0.12, max(0.03, 1 / speed))
        self.sound.note(op, self.lit[0], self.n, round(duration, 3))

    def quit(self):
        self.sound.stop()
        self.root.destroy()

    # ------------------------------------------------------------ loading
    def randomise(self):
        try:
            n = max(1, int(self.n_var.get()))
        except (tk.TclError, ValueError):
            n = 100
        self.n_var.set(n)
        self.values = random.sample(range(-10 * n, 10 * n), n)
        self.load()

    def load(self):
        self.playing = False
        if self.ops_mode:
            res = read_ops_file(self.args.ops)
        else:
            res = run_push_swap(self.args.binary, self.strategy.get(),
                                self.values)
        self.error = res.error
        self.bench = res.bench
        self.n = len(self.values)
        self.disorder = disorder(self.values)
        self.hist = History(to_ranks(self.values), res.ops)
        self.waste = wasted_moves(self.hist.ops)
        self.scrub.configure(to=max(1, len(self.hist)))
        self._fill_log()
        self._create_bars()
        self.redraw()

    def _fill_log(self):
        self.log.delete(0, "end")
        ops = self.hist.ops
        width = len(str(len(ops)))
        self.log.insert("end", *(f"{i + 1:>{width}} {op}"
                                 for i, op in enumerate(ops)))
        self._paint_waste()

    def _paint_waste(self):
        for i in self.waste:
            self.log.itemconfigure(i, bg=self.theme["waste"])
            self.log.itemconfigure(i + 1, bg=self.theme["waste"])

    # ------------------------------------------------------------ playback
    def toggle(self):
        if not self.playing and self.hist.pos >= len(self.hist):
            self.seek(0)
        self.playing = not self.playing
        if self.playing:
            self.budget = 0.0
            self.last_tick = time.perf_counter()
            self._tick()
        else:
            self._update_info()

    def _tick(self):
        if not self.playing:
            return
        now = time.perf_counter()
        self.budget += (now - self.last_tick) * \
            speed_from_slider(self.speed_var.get())
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

    def next_waste(self):
        later = [i for i in self.waste if i + 1 > self.hist.pos]
        if later:
            self.playing = False
            self.seek(later[0] + 1)

    def _nudge_speed(self, d):
        self.speed_var.set(min(100, max(0, self.speed_var.get() + d)))
        self._show_speed()

    def _show_speed(self):
        self.speed_label.configure(
            text=f"{speed_from_slider(self.speed_var.get())} op/s")

    def _on_scrub(self, v):
        if not self.syncing:
            self.playing = False
            self.seek(round(float(v)))

    def _on_log_click(self, _):
        sel = self.log.curselection()
        if sel and not self.syncing:
            self.playing = False
            self.seek(sel[0] + 1)

    # ------------------------------------------------------------ drawing
    def _on_resize(self, event):
        self.W, self.H = event.width, event.height
        self.canvas.coords("divider", self.W // 2, 0, self.W // 2, self.H)
        self.canvas.coords("label_b", self.W // 2 + 8, 4)
        self.redraw()

    def _create_bars(self):
        c, th = self.canvas, self.theme
        c.delete("all")
        self.lit = []
        self.bars = [c.create_rectangle(0, 0, 0, 0, width=0,
                                        fill=self._bar_colour(r))
                     for r in range(self.n)]
        c.create_line(self.W // 2, 0, self.W // 2, self.H,
                      fill=th["divider"], tags="divider")
        c.create_text(8, 4, text="a", anchor="nw", fill=th["dim"],
                      tags=("label", "label_a"))
        c.create_text(self.W // 2 + 8, 4, text="b", anchor="nw",
                      fill=th["dim"], tags=("label", "label_b"))

    def redraw(self):
        st, n = self.hist.state, max(1, self.n)
        top_pad = 20
        bh = (self.H - top_pad) / n
        gap = 1 if bh >= 4 else 0
        half = self.W // 2 - 16
        for x0, stack in ((8, st.a), (self.W // 2 + 8, st.b)):
            for i, rank in enumerate(stack):
                y = top_pad + i * bh
                w = 2 + half * (rank + 1) / n
                self.canvas.coords(self.bars[rank], x0, y, x0 + w,
                                   y + bh - gap)
        self._highlight()
        self._sync_widgets()
        self._update_info()

    def _highlight(self):
        for r in self.lit:
            self.canvas.itemconfigure(self.bars[r], outline="", width=0)
        op = self.hist.last_op()
        self.lit = self.hist.state.touched(op) if op else []
        for r in self.lit:
            self.canvas.itemconfigure(self.bars[r],
                                      outline=self.theme["highlight"],
                                      width=2)

    def _sync_widgets(self):
        self.syncing = True
        self.scrub.set(self.hist.pos)
        self.log.selection_clear(0, "end")
        if self.hist.pos:
            self.log.selection_set(self.hist.pos - 1)
            self.log.see(self.hist.pos - 1)
        self.syncing = False

    def _update_info(self):
        h, th = self.hist, self.theme
        if self.error:
            result, col = f"ERROR: {self.error}", th["ko"]
        elif h.pos == len(h):
            ok = h.state.is_sorted()
            result, col = ("OK", th["ok"]) if ok else ("KO", th["ko"])
        else:
            result, col = ("running…" if self.playing else "paused"), th["fg"]
        self.status.configure(
            text=f"op {h.pos}/{len(h)}   last: {h.last_op() or '-':<4}"
                 f"   n={self.n}   disorder={self.disorder * 100:.2f}%"
                 f"   result: {result}", foreground=col)
        self.counts_label.configure(
            text="  ".join(f"{op} {h.counts[op]}" for op in OPS))
        self.waste_label.configure(
            text=f"wasted/mergeable adjacent pairs: {len(self.waste)}",
            foreground=th["ko"] if self.waste else th["dim"])
        self.bench_label.configure(text="\n".join(self.bench))
        self._show_sound_status()
