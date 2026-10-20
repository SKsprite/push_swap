#!/usr/bin/env python3
"""push_swap visualiser.

  python3 visualizer.py                         100 random, --adaptive
  python3 visualizer.py -n 500 -s complex
  python3 visualizer.py -s simple 5 4 3 2 1
  python3 visualizer.py -- -3 7 -1 0            negative numbers
  python3 visualizer.py -t synthwave --mute     theme, no sound
  ../push_swap 3 1 2 | python3 visualizer.py --ops - 3 1 2
"""
import argparse
import os
import tkinter as tk

from themes import DEFAULT_THEME, THEMES
from ui import STRATEGIES, App

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BINARY = os.path.normpath(os.path.join(HERE, "..", "..", "push_swap"))


def main():
    ap = argparse.ArgumentParser(description="push_swap visualiser")
    ap.add_argument("numbers", nargs="*", type=int,
                    help="stack a, first = top (default: random)")
    ap.add_argument("-n", type=int, default=100,
                    help="how many random numbers if none given (default 100)")
    ap.add_argument("-s", "--strategy", default="adaptive",
                    choices=STRATEGIES)
    ap.add_argument("-b", "--binary", default=DEFAULT_BINARY,
                    help=f"push_swap binary (default {DEFAULT_BINARY})")
    ap.add_argument("--ops", metavar="FILE",
                    help="read ops from FILE ('-' = stdin) instead of "
                         "running push_swap; numbers are then required")
    ap.add_argument("-t", "--theme", default=DEFAULT_THEME,
                    choices=list(THEMES))
    ap.add_argument("--mute", action="store_true",
                    help="start with sound off (toggle with m)")
    args = ap.parse_args()
    if len(set(args.numbers)) != len(args.numbers):
        ap.error("duplicate numbers")
    if args.ops and not args.numbers:
        ap.error("--ops needs the input numbers too")
    if args.n < 1:
        ap.error("-n must be >= 1")

    root = tk.Tk()
    root.title("push_swap visualiser")
    root.minsize(700, 500)
    App(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
