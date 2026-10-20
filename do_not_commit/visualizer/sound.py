"""Per-op tones, streamed as raw PCM to pacat / pw-play / aplay (stdlib only).

Pitch follows the rank of the element the op moved (low rank = low note);
each op family has its own waveform so you can hear the phases of a sort.
"""
import array
import math
import queue
import shutil
import subprocess
import threading
import time

RATE = 22050
LOW_HZ, OCTAVES = 220.0, 3          # ranks map onto 220 Hz .. 1760 Hz
MAX_AHEAD = 0.04                    # never buffer more than 40 ms of audio

PLAYERS = (
    ("pacat", ["pacat", "--raw", "--format=s16le", f"--rate={RATE}",
               "--channels=1", "--latency-msec=30"]),
    ("pw-play", ["pw-play", "--format=s16", f"--rate={RATE}",
                 "--channels=1", "-"]),
    ("aplay", ["aplay", "-q", "-t", "raw", "-f", "S16_LE", "-r", str(RATE),
               "-c", "1", "-B", "50000"]),
)

WAVE = {"sa": "square", "sb": "square", "ss": "square",
        "pa": "triangle", "pb": "triangle",
        "ra": "sine", "rb": "sine", "rr": "sine",
        "rra": "saw", "rrb": "saw", "rrr": "saw"}


def _osc(kind, phase):
    """One sample in [-1, 1] at phase in [0, 1)."""
    if kind == "sine":
        return math.sin(2 * math.pi * phase)
    if kind == "triangle":
        return 4 * abs(phase - 0.5) - 1
    if kind == "square":
        return 0.6 if phase < 0.5 else -0.6       # quieter: square is loud
    return 0.7 * (2 * phase - 1)                  # saw


def synth(freq, kind, duration, volume):
    n = int(RATE * duration)
    attack = max(1, int(RATE * 0.004))
    out = array.array("h", bytes(2 * n))
    for i in range(n):
        env = min(1.0, i / attack) * math.exp(-4.0 * i / n)
        out[i] = int(32767 * volume * env * _osc(kind, (freq * i / RATE) % 1))
    return out.tobytes()


class Sound:
    def __init__(self):
        self.player = None
        self.proc = None
        self.enabled = False
        self.volume = 0.3
        self.error = None
        self._q = queue.Queue(maxsize=2)
        self._cache = {}
        self._thread = None

    def start(self):
        for name, cmd in PLAYERS:
            if shutil.which(name):
                try:
                    self.proc = subprocess.Popen(
                        cmd, stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except OSError as e:
                    self.error = f"{name}: {e}"
                    continue
                self.player = name
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()
                return True
        self.error = self.error or "no audio player (pacat/pw-play/aplay)"
        return False

    def stop(self):
        if self.proc:
            self._q.put(None)
            try:
                self.proc.stdin.close()
            except OSError:
                pass
            self.proc.terminate()
            self.proc = None

    def note(self, op, rank, n, duration):
        """Queue a tone; silently dropped if audio is behind."""
        if not (self.enabled and self.proc):
            return
        t = rank / max(1, n - 1)
        freq = LOW_HZ * 2 ** (t * OCTAVES)
        try:
            self._q.put_nowait((round(freq), WAVE[op], duration))
        except queue.Full:
            pass

    def _run(self):
        ahead_until = time.perf_counter()
        while True:
            item = self._q.get()
            if item is None or not self.proc:
                return
            freq, kind, duration = item
            key = (freq, kind, duration, self.volume)
            pcm = self._cache.get(key)
            if pcm is None:
                if len(self._cache) > 4000:
                    self._cache.clear()
                pcm = self._cache[key] = synth(freq, kind, duration,
                                               self.volume)
            try:
                self.proc.stdin.write(pcm)
                self.proc.stdin.flush()
            except (BrokenPipeError, OSError, AttributeError):
                self.error = f"{self.player} stopped"
                self.proc = None
                return
            # pace to real time so the pipe never holds seconds of audio
            now = time.perf_counter()
            ahead_until = max(now, ahead_until) + duration
            if ahead_until - now > MAX_AHEAD:
                time.sleep(ahead_until - now - MAX_AHEAD)
