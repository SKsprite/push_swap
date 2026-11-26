NAME		= push_swap
CC			= cc
CFLAGS		= -Wall -Wextra -Werror
INC			= push_swap.h

LIBFT_DIR	= ./libft
LIBFT		= $(LIBFT_DIR)/libft.a

AR			= ar rcs
RM			= rm -f

SRCS		= ft_initialize.c \
			ft_main.c \
			ft_operations.c \
			ft_parse.c \
			ft_push_swap_utils.c \
			ft_sort.c

OBJS		= $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(LIBFT) $(OBJS)
		cp $(LIBFT) $(NAME)
		$(AR) $(NAME) $(OBJS)

$(LIBFT):
		$(MAKE) -C $(LIBFT_DIR)

%.o: %.c $(INC)
		$(CC) $(CFLAGS) -c $< -o $@

clean:
		$(RM) $(OBJS)
		$(MAKE) -C $(LIBFT_DIR) clean

fclean: clean
		$(RM) $(NAME)
		$(MAKE) -C $(LIBFT_DIR) fclean

re: fclean all

.PHONY: all clean fclean re bonus