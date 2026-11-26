*This project has been created as part of the 42 curriculum by stkoh, jayam.*

## Description

`Push_swap` is an algorithm project where 2 stacks of integer values and a set of operations are used to manipulate them. The stacks of data will be sorted with a constrained set of instructions, using as little possible number of actions. How to use different types of algorithms and selecting the most optimal one for data sorting is a learning goal.

## Instructions

### Compilation

A `Makefile` compiles all source C files using `cc` with the required flags.

Available `Makefile` rules:
- `make` or `make all`: Source files are compiled
- `make clean`: Removes all generated object (`.o`) files.
- `make fclean`: Removes all generated object (`.o`) files.
- `make re`: Executes `fclean` before running `all`.

## Resources

- `man 2 read`
- `man 2 write`

### Websites

- Loop analysis in algorithms: https://www.geeksforgeeks.org/dsa/how-to-analyse-loops-for-complexity-analysis-of-algorithms/
- On asymptotic notation, insertion sort, and selection sort: https://www.khanacademy.org/computing/computer-science/algorithms
- Visualization of sorting simple sorting algorithms: https://visualgo.net/en/sorting
- Using enum: https://www.geeksforgeeks.org/c/enumeration-enum-c/
- Command-line arguments:
	- https://www.geeksforgeeks.org/cpp/command-line-arguments-in-c-cpp/
	- https://ece.uwaterloo.ca/~dwharder/icsrts/C/05/
- exit() in C:
	- https://www.geeksforgeeks.org/cpp/exit-vs-_exit-c-cpp/
	- https://www.geeksforgeeks.org/cpp/exit-codes-in-c-c-with-examples/

### AI usage

Gemini was used for the following tasks:

- Provision of online resources on Big-O notation
- Evaluation on ideas of current project outline
- Differences between command-line arguments and standard input for passing arguments
- Explanation for split- and multi- argument parsing
- Considerations to make during validation (Incremental vs Batch)
- Configuration of data structures used

## Algorithms

### Simple algorithm



### Medium algorithm

### Complex algorithm

### Custom adaptive algorithm (learner's design)

## Technical choices

1. Enum data type for clarity when reading code
2. Validation of flags and list of integers as command-line arguments are first done before stack construction. This architectural choice would prevent invalid states early on in the program.
3. For the data structure, a circular array is used.

## Authors

- Stanley Koh (stkoh)
- Jarel Yam (jayam)