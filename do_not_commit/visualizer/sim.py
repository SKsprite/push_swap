"""Pure push_swap simulator: no UI, no subprocesses."""
from collections import deque

OPS = ("sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr")
INVERSE = {"sa": "sa", "sb": "sb", "ss": "ss", "pa": "pb", "pb": "pa",
           "ra": "rra", "rb": "rrb", "rr": "rrr",
           "rra": "ra", "rrb": "rb", "rrr": "rr"}
SPLIT = {"ss": ("sa", "sb"), "rr": ("ra", "rb"), "rrr": ("rra", "rrb")}
CHECKPOINT_EVERY = 500

# adjacent pairs that cancel out or could be merged into one op
WASTE = {("ra", "rra"), ("rra", "ra"), ("rb", "rrb"), ("rrb", "rb"),
         ("pa", "pb"), ("pb", "pa"), ("sa", "sa"), ("sb", "sb"),
         ("ss", "ss"), ("rr", "rrr"), ("rrr", "rr"),
         ("ra", "rb"), ("rb", "ra"), ("rra", "rrb"), ("rrb", "rra"),
         ("sa", "sb"), ("sb", "sa")}


def to_ranks(values):
    """Replace every value by its rank 0..n-1."""
    idx = {v: i for i, v in enumerate(sorted(values))}
    return [idx[v] for v in values]


def disorder(values):
    """Fraction of inverted pairs, in [0, 1]."""
    n = len(values)
    if n < 2:
        return 0.0
    inv = sum(1 for i in range(n) for j in range(i + 1, n)
              if values[i] > values[j])
    return inv / (n * (n - 1) / 2)


def wasted_moves(ops):
    """Indices i where ops[i], ops[i+1] cancel or could merge."""
    return [i for i in range(len(ops) - 1) if (ops[i], ops[i + 1]) in WASTE]


class Stacks:
    """Stacks a and b, index 0 = top."""

    def __init__(self, a=(), b=()):
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
        """Apply op; return True if the state changed."""
        a, b = self.a, self.b
        if op == "sa":
            return self._swap(a)
        if op == "sb":
            return self._swap(b)
        if op == "ss":
            return self._swap(a) | self._swap(b)
        if op == "pa":
            return self._push(b, a)
        if op == "pb":
            return self._push(a, b)
        if op == "ra":
            return self._rot(a, -1)
        if op == "rb":
            return self._rot(b, -1)
        if op == "rr":
            return self._rot(a, -1) | self._rot(b, -1)
        if op == "rra":
            return self._rot(a, 1)
        if op == "rrb":
            return self._rot(b, 1)
        if op == "rrr":
            return self._rot(a, 1) | self._rot(b, 1)
        raise ValueError(f"unknown op: {op!r}")

    def touched(self, op):
        """Ranks moved by op, assuming op was just applied."""
        a, b = self.a, self.b
        out = []
        if op in ("sa", "ss"):
            out += list(a)[:2]
        if op in ("sb", "ss"):
            out += list(b)[:2]
        if op == "pa" and a:
            out.append(a[0])
        if op == "pb" and b:
            out.append(b[0])
        if op in ("ra", "rr") and a:
            out.append(a[-1])
        if op in ("rb", "rr") and b:
            out.append(b[-1])
        if op in ("rra", "rrr") and a:
            out.append(a[0])
        if op in ("rrb", "rrr") and b:
            out.append(b[0])
        return out

    def is_sorted(self):
        a = self.a
        return not self.b and all(a[i] < a[i + 1] for i in range(len(a) - 1))


class History:
    """An op list plus a cursor; move to any position cheaply."""

    def __init__(self, ranks, ops):
        self.ops = list(ops)
        self.pos = 0
        self.state = Stacks(ranks)
        self.checkpoints = {0: self.state.copy()}
        self.counts = dict.fromkeys(OPS, 0)
        self._undo = [None] * len(self.ops)    # how to reverse each step

    def __len__(self):
        return len(self.ops)

    def forward(self):
        if self.pos >= len(self.ops):
            return False
        op = self.ops[self.pos]
        # double ops (ss/rr/rrr) may be effective on one stack only, so record
        # the exact inverse sequence instead of a single bool
        if op in SPLIT:
            inv = [INVERSE[s] for s in SPLIT[op] if self.state.apply(s)]
        else:
            inv = [INVERSE[op]] if self.state.apply(op) else []
        self._undo[self.pos] = inv
        self.counts[op] += 1
        self.pos += 1
        if self.pos % CHECKPOINT_EVERY == 0 and self.pos not in self.checkpoints:
            self.checkpoints[self.pos] = self.state.copy()
        return True

    def back(self):
        if self.pos == 0:
            return False
        self.pos -= 1
        for inv in self._undo[self.pos]:
            self.state.apply(inv)
        self.counts[self.ops[self.pos]] -= 1
        return True

    def seek(self, target):
        target = max(0, min(target, len(self.ops)))
        if abs(target - self.pos) > CHECKPOINT_EVERY:
            cp = max(k for k in self.checkpoints if k <= target)
            if cp > self.pos or target < self.pos:
                self._jump(cp)
        while self.pos > target:
            self.back()
        while self.pos < target:
            self.forward()

    def _jump(self, cp):
        self.pos = cp
        self.state = self.checkpoints[cp].copy()
        self.counts = dict.fromkeys(OPS, 0)
        for op in self.ops[:cp]:
            self.counts[op] += 1

    def last_op(self):
        return self.ops[self.pos - 1] if self.pos else None
