# Stacks: array vs doubly linked list, and checking for duplicates

> Notes for stkoh and jayam: which data structure to use for the stacks, and
> how to reject duplicate numbers. Every C snippet below has been compiled with
> `cc -Wall -Wextra -Werror` and tested (see the end).

---

## 1. Short answer

- **Use a plain array.** It's much easier to get right, and its slowness doesn't
  matter: the grade counts the **ops you print**, not how long your program takes.
- **Duplicates:** you have to make a **sorted copy** anyway (to turn values into
  ranks 0…n-1). Duplicates sit next to each other in a sorted list, so you can
  catch them **inside the sort you already wrote**. No extra loop, no hash table.

---

## 2. What the stack needs to do

All 11 ops come down to 4 actions:

| Action | Used by |
|--------|---------|
| swap the top two | sa sb ss |
| take off the top / put on the top | pa pb |
| top goes to the bottom | ra rb rr |
| bottom comes to the top | rra rrb rrr |

The algorithms also keep asking *"what's at position i from the top?"*
(finding the min, cost of rotating, chunk checks).

---

## 3. Option A: plain array, top at index 0 (recommended)

```c
typedef struct s_stack
{
	int	*data;   /* data[0] = top, data[size - 1] = bottom */
	int	size;    /* how many elements are in it right now */
}	t_stack;
```
Both stacks get `malloc(sizeof(int) * n)` once at the start. Neither can ever
hold more than n elements, so they never need to grow. "Position i from the
top" is just `data[i]`.

### The 4 actions

```c
/* make room at the top: everything moves one place down */
static void	shift_down(t_stack *s)
{
	int	i;

	i = s->size;
	while (i > 0)
	{
		s->data[i] = s->data[i - 1];
		i--;
	}
}

/* close the gap at the top: everything moves one place up */
static void	shift_up(t_stack *s)
{
	int	i;

	i = 0;
	while (i < s->size - 1)
	{
		s->data[i] = s->data[i + 1];
		i++;
	}
}

void	swap_top(t_stack *s)                 /* sa / sb */
{
	int	tmp;

	if (s->size < 2)
		return ;
	tmp = s->data[0];
	s->data[0] = s->data[1];
	s->data[1] = tmp;
}

void	push(t_stack *dst, t_stack *src)     /* pa = push(a, b), pb = push(b, a) */
{
	if (src->size == 0)
		return ;
	shift_down(dst);
	dst->data[0] = src->data[0];
	dst->size++;
	shift_up(src);
	src->size--;
}

void	rotate(t_stack *s)                   /* ra / rb */
{
	int	top;

	if (s->size < 2)
		return ;
	top = s->data[0];
	shift_up(s);
	s->data[s->size - 1] = top;
}

void	reverse_rotate(t_stack *s)           /* rra / rrb */
{
	int	bottom;

	if (s->size < 2)
		return ;
	bottom = s->data[s->size - 1];
	s->size--;
	shift_down(s);
	s->size++;
	s->data[0] = bottom;
}
```
(`ft_memmove` from libft can replace the two shift loops if you like.)

### Example trace: `./push_swap 2 1 3`

```
start   a = [2, 1, 3]  size 3     b = [ ]  size 0
pb      b: shift_down, b[0] = 2 -> [2]        a: shift_up -> [1, 3]
ra      a: top = 1, shift_up -> [3, _], a[size-1] = 1 -> [3, 1]
rra     a: bottom = 1, shift_down -> [_, 3], a[0] = 1 -> [1, 3]
pa      a: shift_down -> [_, 1, 3], a[0] = 2 -> [2, 1, 3]   b: [ ]
sa      a: [1, 2, 3]   sorted
```
(Silly sequence on purpose; it uses every action once.)
Everything happens in one block of memory and nothing is malloc'd during sorting.

### "But shifting is slow!"
Each push or rotate moves up to n ints. Worst case for 500 numbers:
~6 000 ops × 500 moves = 3 million int copies, which takes **about a
millisecond**. The evaluator never times your program; it only counts the lines
you print. So this slowness costs you nothing.

---

## 4. Option B: doubly linked list (why it feels hard)

```c
typedef struct s_node
{
	int				value;
	struct s_node	*prev;
	struct s_node	*next;
}	t_node;
```
Here is `pb` alone on a **circular** doubly linked list (the version that makes
rotate cheap):

```c
void	pb(t_node **a, t_node **b)
{
	t_node	*n;

	if (!*a)
		return ;
	n = *a;
	if (n->next == n)                 /* special case: last element of a */
		*a = NULL;
	else
	{
		n->prev->next = n->next;      /* unlink from a: 2 pointers */
		n->next->prev = n->prev;
		*a = n->next;
	}
	if (!*b)                          /* special case: b was empty */
	{
		n->next = n;
		n->prev = n;
	}
	else
	{
		n->next = *b;                 /* link into b: 4 pointers */
		n->prev = (*b)->prev;
		(*b)->prev->next = n;
		(*b)->prev = n;
	}
	*b = n;
}
```
Compare that with the 6 lines of `push()` in the array version. What makes lists
harder:

| | Array | Doubly linked list |
|---|---|---|
| Code per op | a few lines | 4–6 pointer updates + empty/one-element cases |
| Easy mistakes | off-by-one on `size` | a wrong or missing pointer = segfault or infinite loop |
| "Element at position i" | `data[i]` | walk i nodes from the head |
| Memory | 2 mallocs total | one malloc per number; every node must be freed (leaks) |
| Debugging | print the array | follow pointers |
| CPU cost of rotate | O(n) shift | O(1): `*a = (*a)->next` |

The list's only real advantage is that last row, and CPU time isn't graded.

**A note on "cache":** arrays are also what a **CPU cache** handles best. All
the numbers sit side by side in memory, so the processor loads many at once.
List nodes are scattered around memory and get fetched one at a time. That's a
different thing from a hash table (next section), even though both get called
"fast".

(Middle ground, only if you ever want O(1) rotations: a **ring buffer**, i.e. an
array plus a `head` index where "rotate" just moves `head`. You don't need it.)

---

## 5. Checking for duplicates

### 5.1 Two loops (the "obvious" way)
```c
i = 0;
while (i < n)
{
	j = i + 1;
	while (j < n)
		if (vals[i] == vals[j++])
			return (0);    /* duplicate */
	i++;
}
```
For 500 numbers that's 124 750 comparisons, well under a millisecond. It's
**perfectly acceptable** for push_swap. "More loops" isn't a problem at this size.

### 5.2 Recommended: catch duplicates inside the sort you already need
Every strategy works on **ranks** (smallest = 0, next = 1, …), and you get those
by sorting a copy of the input. While insertion sort places each number, it
compares the number with its neighbours, so if two values are equal, the sort
**runs into it by itself**:

```c
/* sorts s[0..n-1] ascending; returns 0 if two values are equal */
int	sort_and_check(int *s, int n)
{
	int	i;
	int	j;
	int	key;

	i = 1;
	while (i < n)
	{
		key = s[i];
		j = i - 1;
		while (j >= 0 && s[j] >= key)
		{
			if (s[j] == key)
				return (0);          /* duplicate found, no extra loop */
			s[j + 1] = s[j];
			j--;
		}
		s[j + 1] = key;
		i++;
	}
	return (1);
}
```
Example: input `5 3 9 3`
```
copy:            [5, 3, 9, 3]
place 3:         [3, 5, 9, 3]
place 9:         [3, 5, 9, 3]
place 3: compare with 9 (bigger, shift), 5 (bigger, shift), 3 → EQUAL → Error
```
Then turn values into ranks using the sorted copy:
```
input a:   [ 42, -7, 100, 3 ]
sorted:    [ -7,  3,  42, 100 ]   index = rank
ranks a:   [  2,  0,   3,  1 ]    (42 is at index 2 in sorted, etc.)
```
One sort gives you both the duplicate check and the ranks.
(Watch out: `+5` and `5` are duplicates. You compare **parsed ints**, never strings.)

### 5.3 Hash tables: what they are and why they're fast
**The problem with 5.1:** to know whether a new number is a duplicate, you
compare it with **every** number seen so far.

**The hash table idea:** use the number itself to work out *where* it would be
stored, and look only there. It's like lockers: number 37 always goes in locker
`37 % 11 = 4`. To check whether 37 is already stored, open locker 4 only, not
all of them.

If two numbers want the same locker (a **collision**), try the next locker
along (**linear probing**).

Walkthrough: table of 11 slots, input `5 16 27 16`
```
5  -> 5 % 11 = 5   slot 5 empty        -> store at 5
16 -> 16 % 11 = 5  slot 5 holds 5 (≠16) -> try 6, empty -> store at 6
27 -> 27 % 11 = 5  5 taken, 6 taken     -> store at 7
16 -> 16 % 11 = 5  slot 5 holds 5, slot 6 holds 16 → DUPLICATE
```
The last check looked at 2 slots instead of all 3 earlier numbers. With 500
numbers and a table of ~1000 slots, a check usually looks at 1–2 slots instead
of up to 499. So the whole input takes about **n** steps instead of **n²/2**.

```c
typedef struct s_slot
{
	int	value;
	int	used;
}	t_slot;

/* table: calloc'd array of `size` slots, size >= 2 * n.
   returns 0 if v was already in the table */
int	hash_insert(t_slot *table, int size, int v)
{
	long	h;

	h = ((long)v % size + size) % size;   /* handles negative numbers */
	while (table[h].used)
	{
		if (table[h].value == v)
			return (0);
		h = (h + 1) % size;
	}
	table[h].used = 1;
	table[h].value = v;
	return (1);
}
```
**Why not use it here?** It's extra code, an extra malloc and free, and more
Norm functions, all to speed up something that already takes under a
millisecond. And you still need the sort for ranks. It's useful to understand,
and worth using on big inputs (100 000+ values), but not needed for push_swap.

---

## 6. Recommendation
1. Stack = **plain int array, top at index 0**, `t_stack { int *data; int size; }`.
   Two `malloc(n * sizeof(int))` calls at the start, freed at the end.
2. Parse → copy → `sort_and_check()` (duplicates) → replace values with ranks.
3. Skip the hash table; mention in your README/defence that you considered it and why.

---

## 7. Tested
All snippets were compiled together with `cc -Wall -Wextra -Werror` and run
under valgrind (no errors, no leaks):
- The subject's ops `sa pb pb pb rr rrr sa pa pa pa` on `2 1 3 6 5 8`, using the
  array functions, give exactly the subject's diagram, ending with `1 2 3 5 6 8`.
- The §3 trace on `2 1 3` gives exactly the values shown.
- rotate, reverse_rotate, swap and push on an empty or 1-element stack do
  nothing (no crash).
- `sort_and_check`: `5 3 9 3` → 0, `0 -0` → 0, `3 -2 7` → 1 (sorted to `-2 3 7`).
- Ranks of `42 -7 100 3` → `2 0 3 1`.
- `hash_insert`: rejects the second 16 in `5 16 27 16`; `-7` and `INT_MIN` work.
- The linked-list `pb` correctly moves 3 nodes, and both circular lists stay intact.
