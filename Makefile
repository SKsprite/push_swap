NAME		= push_swap
BONUS_NAME	= checker
CC			= cc
CFLAGS		= -Wall -Wextra -Werror
INC			= -Iincludes -Ilibft

RM			= rm -f

SRCS		= 
OBJS		= $(SRCS:.c=.o)

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
	$(RM) $(OBJS) $(BONUS_OBJS)

fclean: clean
	$(MAKE) -C libft fclean
	$(RM) $(NAME) $(BONUS_NAME)

re: fclean all

.PHONY: all clean fclean re bonus