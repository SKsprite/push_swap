*This project has been created as part of the 42 curriculum by jayam.*

# Libft

## Description

`libft` is a project where one creates their own library. It contains functions from `libc`, additional ones outside of it, and those that can manipulate a linked list. Through this project, there would be deeper understanding of these functions and effective applications of them. This library will aid in future C projects, particularly within the 42 curriculum.

## Instructions

### Compilation

A `Makefile` manages the library which compiles all source C files using `cc` with the required flags.

The available `Makefile` rules are:
- `make` or `make all`: Source files are compiled where a static library file `libft.a` is generated at the root directory.
- `make clean`: Removes all generated object (`.o`) files.
- `make fclean`: Removes all generated object (`.o`) files and the `libft.a` static library.
- `make re`: Executes `fclean` before running `all` to rebuild `libft.a`.

## Detailed library description

### Part 1 - Libc functions

Reimplementation of a set of functions from `libc` with the `ft_` prefixed.

- Character checks & conversions: `ft_isalpha`, `ft_isdigit`, `ft_isalnum`, `ft_isascii`, `ft_isprint`, `ft_toupper`, `ft_tolower`
- String operations: `ft_strlen`, `ft_strchr`, `ft_strrchr`, `ft_strncmp`, `ft_strnstr`, `ft_strdup`
- Memory management: `ft_memset`, `ft_bzero`, `ft_memcpy`, `ft_memmove`, `ft_memchr`, `ft_memcmp`, `ft_calloc`
- Size-bound string functions: `ft_strlcpy`, `ft_strlcat`
- Conversions: `ft_atoi`

### Part 2 - Additional functions

Functions not included in `libc` for string formatting, dynamic memory operations, and writing output to file descriptors.

- String manipulations: `ft_substr`, `ft_strjoin`, `ft_strtrim`, `ft_split`
- Conversions: `ft_itoa`
- Function applications: `ft_strmapi`, `ft_striteri`
- File descriptor output: `ft_putchar_fd`, `ft_putstr_fd`, `ft_putendl_fd`, `ft_putnbr_fd`

### Part 3 - linked list

Functions allowing the manipulation of single linked list nodes.

- Node operations: `ft_lstnew`, `ft_lstadd_front`, `ft_lstsize`, `ft_lstlast`, `ft_lstadd_back`
- Node deletion & clearing: `ft_lstdelone`, `ft_lstclear`
- Node iteration & mapping: `ft_lstiter`, `ft_lstmap`

## Resources

### Websites

#### Technical considerations

- Makefile references:
	- https://web.stanford.edu/class/archive/cs/cs107/cs107.1174/guide_make.html
	- https://makefiletutorial.com/#makefile-cookbook
- Readings on how compilation works in C:
	- https://www.geeksforgeeks.org/c/types-of-c-files-after-its-compilation/
	- https://www.geeksforgeeks.org/c/compiling-a-c-program-behind-the-scenes/
	- https://www.geeksforgeeks.org/c/how-does-a-c-program-executes/
- On memory: https://educatedguesswork.org/posts/memory-management-1/?ref=dailydev#how-malloc-works
- On processes: https://www.codequoi.com/en/creating-and-killing-child-processes-in-c/

#### Part 1 - Libc functions

- On being able to modify a void pointer: https://stackoverflow.com/questions/18851835/create-my-own-memset-function-in-c
- Understanding the difference between `void *` and `const void *` for `ft_memcpy` and `ft_memmove`: https://stackoverflow.com/questions/5547131/c-question-const-void-vs-void
- Further understanding for `ft_memcpy` and `ft_memmove`: https://learnmandu.com/blog/memc/blogs/memset-memcpy-memmove-c
- Reference for `ft_memcpy` and `ft_memmove`: https://www.geeksforgeeks.org/cpp/write-memcpy/
- Clarification of what `calloc` does and how it differs from `malloc`: https://www.geeksforgeeks.org/c/dynamic-memory-allocation-in-c-using-malloc-calloc-free-and-realloc/
- Further readings on `malloc`, `free`, and `calloc`:
	- https://stackoverflow.com/questions/46853908/how-to-implement-calloc
	- https://stackoverflow.com/questions/2688466/why-mallocmemset-is-slower-than-calloc/2688522#2688522
- Reference for `ft_strdup`: https://stackoverflow.com/questions/37132549/implementation-of-strdup-in-c-programming

#### Part 2 - Additional functions

- Clarification on data types for `ft_split`: https://stackoverflow.com/questions/9834067/difference-between-char-and-const-char
- Ideas for `ft_split`: https://github.com/jermucode/string_splitter/blob/master/string_split.c
- Syntax in function prototypes of `ft_strmapi` and `ft_striteri`: https://stackoverflow.com/questions/25283815/what-is-the-meaning-of-the-declaration-char-f
- Guide on file descriptors: https://linuxvox.com/blog/linux-file-descriptor/
More on file descriptors: https://www.codequoi.com/en/handling-a-file-by-its-descriptor-in-c/

#### Part 3 - linked list

- Introduction to linked list: https://www.geeksforgeeks.org/dsa/what-is-linked-list/
- Insertion at various parts of a linked list: https://www.geeksforgeeks.org/dsa/insertion-in-linked-list/
- More on deleting nodes from linked list: https://learningc.org/chapters/chapter13-linked-lists/delete-nodes

### AI usage

Gemini was used for the following tasks:

- `Makefile`: Understanding targets, dependencies, and basic syntax.
- Formatting improvements: `README.md` and `libft.h`.
- Handling of edge cases:
	- `ft_strlcpy`: Buffer bounds logic when `size` could be 0.
	- `ft_strlcat`: Understanding how the `size` parameter relates to destination length.
	- `ft_atoi`: Reviewing logic on whitespace skipping and sign handling.
	- `ft_itoa`: Optimization of string conversion, memory allocation sizing, and handling edge cases.
- Function pointer syntax: Clarification argument and passing syntax for function pointers in `ft_strmapi`, `ft_striteri`, `ft_lstiter`, and `ft_lstmap`.