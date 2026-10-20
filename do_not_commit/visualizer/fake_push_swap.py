#!/usr/bin/env python3
"""Stand-in for ./push_swap while the C version doesn't exist.

Same CLI shape (strategy flag, --bench, numbers). Every strategy is just
min-extraction, so don't read anything into the op counts.
"""
import sys

from sim import OPS, Stacks, disorder, to_ranks


def main(argv):
    nums, bench = [], False
    for arg in argv:
        if arg == "--bench":
            bench = True
        elif arg.startswith("--"):
            continue
        else:
            try:
                nums.append(int(arg))
            except ValueError:
                sys.stderr.write("Error\n")
                return 1
    if len(set(nums)) != len(nums):
        sys.stderr.write("Error\n")
        return 1
    st, ops = Stacks(to_ranks(nums)), []

    def do(op):
        st.apply(op)
        ops.append(op)

    while list(st.a) != sorted(st.a):
        p = list(st.a).index(min(st.a))
        up = p <= len(st.a) // 2
        for _ in range(p if up else len(st.a) - p):
            do("ra" if up else "rra")
        if list(st.a) != sorted(st.a):
            do("pb")
    while st.b:
        do("pa")
    sys.stdout.write("".join(op + "\n" for op in ops))
    if bench:
        err = sys.stderr.write
        err(f"[bench] disorder: {disorder(nums) * 100:.2f}%\n")
        err("[bench] strategy: fake min-extraction / O(n^2)\n")
        err(f"[bench] total_ops: {len(ops)}\n")
        err("[bench] " + " ".join(f"{o}: {ops.count(o)}" for o in OPS) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
