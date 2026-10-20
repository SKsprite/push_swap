# push_swap — Project Breakdown & Implementation Plan

> Internal working notes for **stkoh** and **jayam**. Not for submission.
> Source: 42 subject, sections VI.3.3 – VIII (the part pasted into the session).
> Anything marked **⚠ VERIFY** depends on a part of the subject that was not pasted
> (e.g. the exact disorder formula). Check it against the full PDF before you rely on it.

---

## Table of contents

1. [What the project is](#1-what-the-project-is)
2. [The operation model](#2-the-operation-model)
3. [Program contract (mandatory)](#3-program-contract-mandatory)
4. [Argument parsing & error handling](#4-argument-parsing--error-handling)
5. [The disorder metric](#5-the-disorder-metric)
6. [The four strategies](#6-the-four-strategies)
7. [Benchmark mode (`--bench`)](#7-benchmark-mode---bench)
8. [Performance targets](#8-performance-targets)
9. [Suggested architecture](#9-suggested-architecture)
10. [Makefile](#10-makefile)
11. [Bonus: the `checker` program](#11-bonus-the-checker-program)
12. [README.md requirements](#12-readmemd-requirements)
13. [Testing plan](#13-testing-plan)
14. [Evaluation checklist](#14-evaluation-checklist)
15. [Suggested work split](#15-suggested-work-split)

---

## 1. What the project is

You are given a list of distinct integers on **stack a**, and an empty **stack b**.
Using only a fixed set of 11 stack operations, you must output a sequence of
operations that leaves **a** sorted in ascending order (smallest on top) and **b**
empty.

Grading is on **number of operations output**, not CPU time. "Complexity" in this
project means *how many push_swap operations the algorithm emits as a function of n*.

This version of the subject adds:

- **Four selectable strategies** (`--simple`, `--medium`, `--complex`, `--adaptive`),
  each with a complexity class you must be able to justify.
- A **disorder metric** used by the adaptive strategy.
- A **`--bench`** mode that prints statistics to stderr.
- A **README** with algorithm justification.

---

## 2. The operation model

| Op    | Effect |
|-------|--------|
| `sa`  | swap the top 2 elements of a (no-op if < 2) |
| `sb`  | swap the top 2 elements of b (no-op if < 2) |
| `ss`  | `sa` + `sb` |
| `pa`  | take top of b, put it on top of a (no-op if b empty) |
| `pb`  | take top of a, put it on top of b (no-op if a empty) |
| `ra`  | rotate a up: top element becomes the bottom |
| `rb`  | rotate b up |
| `rr`  | `ra` + `rb` |
| `rra` | reverse-rotate a: bottom element becomes the top |
| `rrb` | reverse-rotate b |
| `rrr` | `rra` + `rrb` |

Key cost facts that drive every algorithm:

- Bringing the element at index `i` (0 = top) of a stack of size `s` to the top costs
  `min(i, s - i)` rotations (`ra` × i, or `rra` × (s − i)).
- `rr` / `rrr` let you rotate both stacks for the price of one op — combining
  rotations is the single biggest optimisation in cost-based algorithms.
- `pa`/`pb` are the only way to move data between stacks; every element must be
  pushed to b and back at least once unless it is already in place.

### Worked example from the subject (top of stack first)

```
start      a: 2 1 3 6 5 8      b: -
sa         a: 1 2 3 6 5 8      b: -
pb pb pb   a: 6 5 8            b: 3 2 1
ra rb (rr) a: 5 8 6            b: 2 1 3
rra rrb    a: 6 5 8            b: 3 2 1
sa         a: 5 6 8            b: 3 2 1
pa pa pa   a: 1 2 3 5 6 8      b: -
```
12 ops. (Note the `rr`/`rrr` pair is wasted — it shows why peephole cancellation
is worth doing; see §9.4.)

---

## 3. Program contract (mandatory)

| Item | Value |
|------|-------|
| Program name | `push_swap` |
| Files | `Makefile`, `*.h`, `*.c` |
| Makefile rules | `NAME`, `all`, `clean`, `fclean`, `re` (+ `bonus` for checker) |
| Allowed functions | `read`, `write`, `malloc`, `free`, `exit`, your own `ft_printf` |
| Libft | allowed |
| Globals | **forbidden** |

Behaviour:

1. `./push_swap` with **no arguments** → print nothing, exit (status 0).
2. Arguments = stack a, **first argument is the top**.
3. Optional strategy selector: `--simple`, `--medium`, `--complex`, `--adaptive`
   (default = `--adaptive`).
4. Optional `--bench` flag → stats on **stderr** after sorting.
5. Output: operations on **stdout**, each followed by `\n`, nothing else.
6. Already-sorted input → output **nothing** (0 ops).
7. On error → `Error\n` on **stderr**, non-zero exit status, nothing on stdout.
8. Every selector must work for **every** valid input (any size, any disorder).
   `--simple` on 500 numbers must still sort correctly — just with more ops.
9. The binary embeds all four strategies; `--bench` must report the strategy name
   and its complexity class.

Usage examples from the subject:

```sh
./push_swap 2 1 3 6 5 8
ARG="4 67 3 87 23"; ./push_swap --adaptive $ARG | wc -l      # 13 in subject
./push_swap --simple 5 4 3 2 1
ARG="4 67 3 87 23"; ./push_swap --complex $ARG | ./checker_linux $ARG   # OK
shuf -i 0-9999 -n 500 > args.txt ; ./push_swap $(cat args.txt) | wc -l
./push_swap --bench $ARG 2> bench.txt | ./checker_linux $ARG
./push_swap --bench $ARG > /dev/null          # metrics only
./push_swap --adaptive 0 one 2 3   # Error
./push_swap --simple 3 2 3         # Error
```

---

## 4. Argument parsing & error handling

### 4.1 Decisions to make (and document in README)

| Question | Recommended choice |
|----------|--------------------|
| Can flags appear anywhere, or only before numbers? | Accept flags **anywhere** in argv (simplest to explain, most robust in evaluation). |
| Two strategy flags (`--simple --complex`)? | `Error` (ambiguous). Alternatively "last wins" — pick one and document it. |
| Repeated `--bench`? | Accept (idempotent) or Error — document. |
| Quoted lists (`"3 2 1"`)? | **Accept** — split each argv on spaces. Many evaluators test this. |
| Empty string `""` or `"   "`? | `Error` (matches checker example `./checker "" 1` → Error). |
| Only flags, no numbers (`./push_swap --bench`)? | Print nothing, exit 0 (same as no parameters). Document it. |
| Unknown flag (`--foo`)? | `Error`. |

### 4.2 Integer validation

A token is valid iff it matches `[+-]?[0-9]+` and the value fits in `int`
(`-2147483648` … `2147483647`).

Must reject:

- `one`, `1a`, `--`, `+`, `-`, `1-`, `1.5`, `0x10`
- `2147483648`, `-2147483649`, `99999999999999999999` (overflow — accumulate in
  `long` and check **at every digit**, otherwise very long strings overflow `long`)
- duplicates — note `+5` and `5`, and `0`, `-0`, `+0`, `00` are all duplicates
  of each other because you compare **parsed values**, not strings.

Accept: `+5`, `-0`, `007` (unless you decide otherwise — document it).

### 4.3 Error path

```
write(2, "Error\n", 6);
free everything;
exit(1);
```
Never print partial operations before detecting an error: parse and validate
**everything** first, then sort.

### 4.4 Duplicate detection

O(n²) pairwise check is fine for n ≤ a few thousand. Cleaner: you will build a
sorted copy anyway for rank normalisation (§6.0) — check adjacent equal elements
there in O(n log n).

---

## 5. The disorder metric

> **⚠ VERIFY:** the formal definition is in a section of the subject that wasn't
> pasted. The standard definition used for this project version is below.

**Disorder = fraction of inverted pairs**

```
inversions = #{ (i, j) : i < j  and  a[i] > a[j] }      (i, j = positions from top)
disorder   = inversions / (n * (n - 1) / 2)             in [0, 1]
```

- Sorted → `0.00`, reverse sorted → `1.00`, uniformly random → ≈ `0.50`.
- For n ≤ 1, define disorder = 0.
- Counting is O(n²) CPU with two loops — fine, CPU time isn't graded. (Merge-sort
  counting in O(n log n) is optional polish.)
- Use `double` (or count in `long` — for n = 500 there are 124 750 pairs; fine).
- `--bench` prints it as a **percentage with two decimals**: `49.93%`.
  `ft_printf` probably has no `%f` — print it yourself:
  `pct100 = (long)(disorder * 10000 + 0.5)` → print `pct100 / 100`, `.`,
  `pct100 % 100` zero-padded to 2 digits.

The disorder must be computed on the **input**, before any operations.

---

## 6. The four strategies

### 6.0 Preprocessing common to all strategies

1. **Rank normalisation (index compression).** Replace every value by its rank
   `0 … n-1`. All algorithms then work on ranks — makes chunks, radix bits and
   "target position" logic trivial and independent of the actual values.
2. **Early exits.**
   - already sorted → emit nothing;
   - n = 2 → `sa` if needed;
   - n = 3 → hard-coded optimal (≤ 2 ops);
   - n ≤ 5 → push the 1–2 smallest to b (cheapest rotation direction), sort 3, `pa`.
     (≤ 12 ops for 5; the subject's `4 67 3 87 23` example gives 13 — beat it.)

   Decide whether these small-n shortcuts apply to *every* strategy or only
   adaptive. Recommended: apply to every strategy (they're O(1) and don't change
   the complexity class), and document it.

### 6.1 Simple — O(n²): min extraction (selection sort)

```
while size(a) > 3:
    find position p of the minimum in a
    if p <= size(a)/2:  ra × p   else: rra × (size(a) - p)
    pb
sort3(a)
pa × size(b)
```

- **Ops bound:** each extraction costs ≤ n/2 rotations + 1 push →
  Σ (k/2 + 1) for k = n…4 ≈ n²/4 + 2n → **O(n²)**.
- **Space:** O(n) (the two stacks), O(1) extra.
- 100 random ≈ 2 500–3 000 ops — **fails** the 2000 target, which is fine:
  the simple strategy only has to be correct and O(n²). Adaptive won't use it for
  random input.
- Matches the subject's `--simple 5 4 3 2 1` output style (rra/pb repeatedly).

Alternative: insertion-style — push everything to b in order then insert each
back into a at its sorted position using cheapest rotation. Also O(n²).

### 6.2 Medium — O(n√n): chunk sort

Split ranks into `k ≈ √n` chunks (tune the constant). Push chunk by chunk to b,
then pull back the maximum each time.

```
chunk = tuned size (≈ √n * c; e.g. ~15–20 for n=100, ~30–40 for n=500)
limit = chunk
pushed = 0
while a not empty:
    if top(a).rank < limit:
        pb
        if top(b).rank < limit - chunk/2:  rb      # keep lower half deeper in b
        pushed++
        if pushed == limit: limit += chunk
    else:
        ra                                       # (or rra if the next in-range
                                                 #  element is nearer the bottom)
# b now holds "roughly descending" chunks
while b not empty:
    bring max(b) to top with rb or rrb (cheapest direction)
    pa
```

A popular variant is the "sliding window": push if `rank <= pushed + window`;
`rb` if `rank <= pushed`. Same complexity, usually fewer ops.

- **Ops bound:**
  - Phase 1: for each of √n chunks, at most one full pass over a (≤ n `ra`) →
    √n · n = **O(n√n)**, plus n `pb` and ≤ n `rb`.
  - Phase 2: the max of b lies within the current chunk region (≈ √n · const
    positions away, because chunks are stacked contiguously), so each `pa` costs
    O(√n) rotations → n · √n = **O(n√n)**.
  - Total **O(n√n)**. Space O(n).
- Typical: 100 → ~650–1100, 500 → ~5500–7500 depending on tuning.
  Good enough to **pass** both targets, often "good".

### 6.3 Complex — O(n log n)

Two solid options; **pick one as the "complex" strategy and justify it**.

#### Option A — LSD binary radix sort (safe, easy to prove)

```
bits = number of bits needed for (n - 1)
for bit in 0 .. bits-1:
    repeat size(a) times:
        if (top(a).rank >> bit) & 1 == 0:  pb
        else:                               ra
    pa × size(b)
```

- **Ops bound:** each pass = n (`pb`/`ra`) + ≤ n `pa` ≤ 2n; there are ⌈log₂ n⌉
  passes → ≤ 2n⌈log₂ n⌉ = **O(n log n)**. Space O(n).
- Exact counts: 100 → **1084**, 500 → **6784** (this is the number in the subject
  example!). Passes the minimum; "good" for 100 and 500; never "excellent".
- Cheap wins: skip a pass early if a is already sorted; skip the final `pa`s
  stall on the last bit by checking sortedness.

#### Option B — Quicksort-style stack partitioning (better ops)

Recursive partition of ranges between a and b using one or two pivots
(e.g. 3-way: split the range into thirds; small third → b bottom (`pb rb`),
middle third → b top (`pb`), large third stays in a (`ra`)), recurse on each part,
with hard-coded sorts for sizes ≤ 3.

- **Ops bound:** each level of recursion moves every element a constant number of
  times (push + ≤ 1 rotate), recursion depth is O(log n) with fixed-fraction
  pivots (ranks make perfect pivots trivial: the median rank of a range is known
  exactly) → **O(n log n)** worst case, since rank-based pivots are exact.
- Typical: 100 → ~600–750, 500 → ~4800–5500 → **can reach "excellent"**.
- Harder to implement and debug (track which stack/position each sub-range is in).

#### About the "Turk" / greedy cost algorithm

Extremely popular (100 → ~550, 500 → ~5000), but its **worst-case op bound is
O(n²)** (one insertion can cost O(n) rotations, n insertions). Do **not** label
it O(n log n). It can, however, be the **O(n²) low-disorder** method inside
adaptive (§6.4), where its claimed class is O(n²) — honest and fast.

### 6.4 Adaptive — learner's design

Required regime contract:

| Disorder `d` | Required class | Recommended method |
|--------------|----------------|--------------------|
| `d < 0.2` | O(n²) | **LIS-keep + greedy insertion** (or simple min-extraction) |
| `0.2 ≤ d < 0.5` | O(n√n) | **Chunk sort** (§6.2) |
| `d ≥ 0.5` | O(n log n) | **Complex** (§6.3) |

#### Low disorder method: LIS-keep + greedy cheapest insertion

1. Compute the **longest increasing subsequence** of a (circularly is a nice
   bonus). Those elements are "already in order" and stay in a.
2. Push every non-LIS element to b (rotate a, `pb` when the top is not in the LIS).
3. Repeatedly pick the element of b whose total cost to insert at its correct
   position in a is minimal (cost = combined rotations of a and b, using
   `rr`/`rrr` overlap), do it, `pa`.
4. Rotate a so the minimum is on top.

- With low disorder, the LIS is long, so very few elements move → very few ops.
- **Ops bound:** ≤ n elements inserted, each ≤ n rotations → **O(n²)**. ✔
- Space: O(n) for the stacks + O(n) for LIS arrays.

(Fallback if time is short: just use the simple strategy for `d < 0.2`.
It satisfies the class requirement but wastes the opportunity.)

#### Rationale for thresholds (for the README)

- **< 0.2:** input is mostly ordered; most elements are already in a long
  increasing run. An O(n²)-bounded method that *only moves misplaced elements*
  beats any method that blindly moves all n elements log n times.
- **0.2–0.5:** substantial local order remains; chunking moves every element
  ~twice with modest rotations, which in practice beats radix at these sizes.
- **≥ 0.5:** essentially random or reversed; structure no longer helps, so use
  the method with the best asymptotic guarantee.
- Note the subject *fixes* these thresholds — your job is to justify them and to
  explain the method per regime. Back the rationale with your own measured
  numbers (see §13 — make a table of avg ops per regime per strategy).

#### Complexity argument (upper bounds, push_swap model)

- Disorder computation: O(n²) CPU, **0 operations** emitted.
- Each regime's bound is the bound of the method it dispatches to
  (O(n²), O(n√n), O(n log n)); the dispatch itself emits no ops.
- Space: O(n) in all regimes (two stacks of total size n + O(n) helper arrays +
  the op buffer, whose length is bounded by the regime's op bound).

---

## 7. Benchmark mode (`--bench`)

Printed **to stderr**, **after** sorting, **only** when the flag is present.
Must include:

- disorder as a percentage with 2 decimals,
- strategy name + theoretical complexity class,
- total number of operations,
- count of each of the 11 ops.

Suggested format (mirrors the subject's `[bench]` notation):

```
[bench] disorder: 49.93%
[bench] strategy: Adaptive / O(n log n)
[bench] total_ops: 5321
[bench] sa: 0 sb: 0 ss: 0 pa: 500 pb: 500
[bench] ra: 1203 rb: 840 rr: 512 rra: 801 rrb: 690 rrr: 275
```

For `--adaptive`, show which internal regime was chosen, e.g.
`Adaptive (high disorder → radix) / O(n log n)`.

Counts must reflect the **final, optimised** op stream (the one actually printed).

---

## 8. Performance targets

| n | Pass | Good | Excellent |
|---|------|------|-----------|
| 100 | < 2000 | < 1500 | < 700 |
| 500 | < 12000 | < 8000 | < 5500 |

Measured with the provided `checker_linux` on random inputs during evaluation.
The bonus is **only graded if all benchmarks pass**.

What each strategy realistically achieves on random input:

| Strategy | 100 | 500 | Verdict |
|----------|-----|-----|---------|
| Simple (min extraction) | ~2 500+ | ~60 000+ | fails (allowed — not the default) |
| Medium (chunks, tuned) | ~700–1100 | ~5 500–7 500 | pass / good |
| Radix | 1084 | 6784 | pass / good |
| Quicksort partition | ~600–750 | ~4 800–5 500 | good / excellent |

Since random input has disorder ≈ 0.5, **the default (adaptive) run on random
input uses the high-disorder method** — that's the one the evaluator's numbers
come from. Make sure it is your best one.

---

## 9. Suggested architecture

### 9.1 Data structures

```c
typedef struct s_stack
{
	int		*data;      /* ring buffer of ranks, capacity = n */
	int		cap;
	int		head;       /* index of top */
	int		size;
}	t_stack;

typedef enum e_op
{
	OP_SA, OP_SB, OP_SS, OP_PA, OP_PB, OP_RA, OP_RB, OP_RR,
	OP_RRA, OP_RRB, OP_RRR, OP_COUNT
}	t_op;

typedef struct s_ops
{
	t_op	*buf;       /* recorded ops (growable array) */
	int		len;
	int		cap;
}	t_ops;

typedef enum e_strategy
{
	STRAT_SIMPLE, STRAT_MEDIUM, STRAT_COMPLEX, STRAT_ADAPTIVE
}	t_strategy;

typedef struct s_ctx            /* passed everywhere — no globals */
{
	t_stack		a;
	t_stack		b;
	t_ops		ops;
	t_strategy	strategy;
	int			bench;
	double		disorder;
	const char	*used_name;     /* filled by dispatcher, for --bench */
	const char	*used_class;
}	t_ctx;
```

A ring buffer makes every op O(1) and index access O(1) (`data[(head+i) % cap]`),
which simplifies cost calculations. A circular doubly linked list also works.

### 9.2 Ops: record, don't print

Every op function **applies** the op and **appends** it to `ctx->ops`. Nothing is
printed until the algorithm is finished. Benefits:

- peephole optimisation pass (§9.4),
- exact counts for `--bench`,
- one buffered `write` at the end (fast for 60 000 ops in `--simple` on 500).

### 9.3 File layout (Norm: ≤ 5 functions / file, ≤ 25 lines / function)

```
Makefile
includes/push_swap.h
includes/checker.h          (bonus)
srcs/
  main.c                    entry, dispatch, output
  parse_args.c              flags + tokenising
  parse_int.c               strict atoi with overflow check
  parse_validate.c          duplicates, rank normalisation
  stack_init.c / stack_utils.c
  ops_swap.c ops_push.c ops_rotate.c ops_rrotate.c
  ops_record.c              buffer append / grow
  ops_optimize.c            peephole pass
  ops_print.c               write op stream
  disorder.c
  sort_small.c              2, 3, 4/5
  sort_simple.c
  sort_medium.c
  sort_complex.c (+ helpers)
  sort_adaptive.c
  sort_lis.c / sort_greedy.c  (low-disorder helpers)
  bench.c
bonus/
  checker_main.c checker_read.c checker_exec.c
libft/
```
Share parsing and op code between push_swap and checker (compile the same
object files into both).

### 9.4 Peephole optimiser

Run repeatedly over the op buffer until nothing changes:

| Pattern | Replace with |
|---------|--------------|
| `ra rb` / `rb ra` | `rr` |
| `rra rrb` / `rrb rra` | `rrr` |
| `sa sb` / `sb sa` | `ss` |
| `pa pb` / `pb pa` | *(nothing)* |
| `ra rra` / `rra ra` (same for b) | *(nothing)* |
| `sa sa`, `sb sb` | *(nothing)* |

Only merge **adjacent** pairs — moving ops past unrelated ops is possible
(e.g. an `ra` commutes with a `rb`) but needs care around `pa`/`pb`.
Always re-verify with the checker after optimisation.

### 9.5 Main flow

```
main(argc, argv):
    if argc == 1: return 0
    parse flags + numbers      -> Error on failure
    if no numbers: return 0
    normalise to ranks
    disorder = compute_disorder(a)
    if !is_sorted(a): dispatch(strategy)
    optimise(ops)
    print(ops)                 -> stdout
    if bench: print_bench()    -> stderr
    free all; return 0
```

### 9.6 Memory

- Free on **every** path, including error paths (`valgrind --leak-check=full`).
- Check every `malloc` return.
- No globals: everything lives in `t_ctx`.

---

## 10. Makefile

```make
NAME        = push_swap
BONUS_NAME  = checker
CC          = cc
CFLAGS      = -Wall -Wextra -Werror
INC         = -Iincludes -Ilibft

SRCS        = ...
OBJS        = $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS) libft/libft.a
	$(CC) $(CFLAGS) $(OBJS) -Llibft -lft -o $(NAME)

libft/libft.a:
	$(MAKE) -C libft

%.o: %.c includes/push_swap.h
	$(CC) $(CFLAGS) $(INC) -c $< -o $@

bonus: $(BONUS_NAME)
$(BONUS_NAME): $(BONUS_OBJS) $(SHARED_OBJS) libft/libft.a
	$(CC) $(CFLAGS) $^ -Llibft -lft -o $@

clean:
	$(MAKE) -C libft clean
	rm -f $(OBJS) $(BONUS_OBJS)

fclean: clean
	$(MAKE) -C libft fclean
	rm -f $(NAME) $(BONUS_NAME)

re: fclean all

.PHONY: all clean fclean re bonus
```

**No relink:** run `make` twice — the second must print "Nothing to be done".
Watch out: making `$(NAME)` depend on a phony libft rule causes relinks; depend
on the actual `libft/libft.a` file. Same for `bonus` (it should not relink either).

---

## 11. Bonus: the `checker` program

Only evaluated if the mandatory part is **perfect** (all benchmarks pass).

| Item | Value |
|------|-------|
| Name | `checker` |
| Rule | `make bonus` |
| Args | stack a (first = top) |

Behaviour:

1. No args → print nothing, exit.
2. Parse args exactly like push_swap (reuse code) → `Error\n` on stderr if invalid.
3. Read ops from **stdin** until EOF, one per line, each terminated by `\n`.
   - Use `read` + your own `get_next_line`.
   - Invalid instruction (`foo`, `sa ` with trailing space, `SA`, empty line,
     missing final `\n` if you're strict) → `Error\n` on stderr.
   - Decide: stop at the first bad line, or read everything first? Reading all
     first then executing is safer (no partial state issues). Free the GNL buffer.
4. Execute, then:
   - a sorted ascending **and** b empty → `OK\n` on stdout,
   - otherwise → `KO\n` on stdout.

Examples:
```
./checker 3 2 1 0   <<< $'rra\npb\nsa\nrra\npa'   → OK
./checker 3 2 1 0   <<< $'sa\nrra\npb'            → KO
./checker 3 2 one 0                               → Error
./checker "" 1                                    → Error
```

Edge: `./checker 1 2 3` with empty stdin (Ctrl-D) → `OK`.
`./checker 2 1` with empty stdin → `KO`.

---

## 12. README.md requirements

At the **repo root** (already started). Must contain:

1. **First line, italic:**
   `*This project has been created as part of the 42 curriculum by stkoh, jayam.*` ✔
2. **Description** — goal and overview.
3. **Instructions** — build (`make`, `make bonus`), run, flags, examples.
4. **Resources** — classic references + **how AI was used** (which tasks, which
   parts of the project). Be honest and specific.
5. **Detailed explanation and justification of the algorithms**, including for
   the adaptive strategy:
   - rationale for thresholds,
   - internal technique per regime,
   - complexity argument (time **and** space upper bounds in the push_swap model).

Recommended extra sections: Usage examples, `--bench` output format, parsing
decisions (§4.1), measured benchmark table, project structure.

Reference ideas for "Resources":
- Wikipedia: Selection sort, Radix sort, Quicksort, Longest increasing subsequence,
  Inversion (discrete mathematics)
- CLRS — *Introduction to Algorithms* (sorting chapters, LIS via DP)
- Knuth — *TAOCP Vol. 3: Sorting and Searching* (inversions as a measure of presortedness)
- Estivill-Castro & Wood, "A survey of adaptive sorting algorithms" (1992)

---

## 13. Testing plan

### 13.1 Correctness loop

```sh
for n in 1 2 3 5 10 50 100 500; do
  for s in --simple --medium --complex --adaptive; do
    for i in $(seq 1 50); do
      ARG=$(shuf -i -10000-10000 -n $n | tr '\n' ' ')
      r=$(./push_swap $s $ARG | ./checker_linux $ARG)
      [ "$r" = "OK" ] || echo "FAIL $s n=$n: $ARG"
    done
  done
done
```

### 13.2 Performance stats

For n = 100 and 500, run ≥ 500 random cases per strategy; record **min / avg /
max**. The **max** is what matters for evaluation. Also generate inputs at
controlled disorder levels (start sorted, do k random swaps) to tune and justify
adaptive thresholds.

### 13.3 Edge cases

| Input | Expected |
|-------|----------|
| *(none)* | nothing |
| `42` | nothing |
| `1 2 3 4 5` | nothing |
| `2 1` | `sa` |
| `3 2 1`, all 6 perms of 3 | ≤ 2–3 ops each |
| all 120 perms of 5 | ≤ 12 ops each |
| `"3 2 1"` (quoted) | sorts (if supported) |
| `--bench` only | nothing |
| `2147483647 -2147483648 0` | sorts |
| `2147483648` | Error |
| `1 2 2` / `0 -0` / `+1 1` | Error |
| `1 a 2` / `1 "" 2` / `--` / `-` | Error |
| `--simple --complex 1 2` | Error (or documented behaviour) |
| `--fast 1 2` | Error |

### 13.4 Tooling

- `valgrind --leak-check=full --show-leak-kinds=all ./push_swap ...` (also on Error paths)
- `norminette`
- `make && make` (no relink), `make bonus && make bonus`
- Use the visualiser (`push_swap_visualizer.md`) to watch the algorithms and spot
  wasted rotations.

---

## 14. Evaluation checklist

- [ ] Makefile: all rules, no relink, `-Wall -Wextra -Werror`
- [ ] No globals, no forbidden functions (`printf`, `strtol`, `qsort`, …)
- [ ] Norminette clean
- [ ] No params → nothing
- [ ] Error cases → `Error\n` on stderr only
- [ ] Sorted input → 0 ops
- [ ] 3 numbers ≤ 3 ops (aim ≤ 2), 5 numbers ≤ 12 ops
- [ ] 100 random → < 700 (excellent) / < 1500 / < 2000
- [ ] 500 random → < 5500 (excellent) / < 8000 / < 12000
- [ ] All four selectors sort all inputs correctly
- [ ] `--bench` prints disorder (2 dp %), strategy name + class, total, 11 counts — to stderr
- [ ] No leaks (incl. error paths)
- [ ] README: italic first line, Description, Instructions, Resources + AI usage,
      algorithm justification, adaptive thresholds + complexity argument
- [ ] Both team members can explain every algorithm and its complexity
- [ ] Bonus checker: OK / KO / Error behaviour, `make bonus`

---

## 15. Suggested work split

| Area | Owner |
|------|-------|
| Parsing, validation, ranks, error handling, Makefile | A |
| Stack + ops + recorder + optimiser + output | B |
| Small sorts + Simple | A |
| Medium (chunk) + tuning | B |
| Complex (radix first, then quicksort partition if time) | A + B |
| Disorder + Adaptive + low-disorder LIS/greedy | A |
| `--bench` | B |
| Checker bonus | B |
| Test scripts + visualiser | A |
| README | both |

Milestones:
1. Parse + ops + checker-verified simple sort working end-to-end.
2. Radix in place → all benchmarks *pass*.
3. Medium + adaptive + bench → feature complete.
4. Optimise high-disorder path toward excellent; finish README; bonus checker.
