NAME		= push_swap
BONUS_NAME	= checker
CC			= cc
CFLAGS		= -Wall -Wextra -Werror
INC			= push_swap.h

RM			= rm -f

SRCS		= ft_main.c \
			ft_parse.c \
			ft_push_swap_utils.c \
			ft_sort.c

OBJS		= $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS) libft/libft.a
	$(CC) $(CFLAGS) $(OBJS) -Llibft -lft -o $(NAME)

libft/libft.a:
	$(MAKE) -C libft

%.o: %.c $(INC)
		$(CC) $(CFLAGS) -c $< -o $@

bonus: $(BONUS_NAME)
$(BONUS_NAME): $(BONUS_OBJS) $(SHARED_OBJS) libft/libft.a
	$(CC) $(CFLAGS) $^ -Llibft -lft -o $@

clean:
	$(MAKE) -C libft clean
	$(RM) $(OBJS) $(BONUS_OBJS)

fclean: clean
	$(MAKE) -C libft fclean
	$(RM) $(NAME) $(BONUS_NAME)

re: fclean all

.PHONY: all clean fclean re bonus