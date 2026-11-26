/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:34:05 by jayam             #+#    #+#             */
/*   Updated: 2026/11/26 13:13:21 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <stdlib.h>
# include <unistd.h>
# include <limits.h>
# include "libft/libft.h"

typedef enum e_strategies
{
	SIMPLE,
	MEDIUM,
	COMPLEX,
	ADAPTIVE
}	t_strategies;

/**
 * @brief The structure of the elements storing a number and their rank value.
 */
typedef struct s_element
{
	/** The actual value of the inputs*/
	int	value;
	/** The normalized number of the inputs*/
	int	rank;

}	t_element;

/**
 * @brief The structure of the implemented stack.
 *
 * Stores data and metadata relating to a dynamic array-based stack.
 */
typedef struct s_stack
{
	/** The actual data and elements in the stack. */
	t_element	*values;
	/** The current index for the element at the top of the stack. 
	 * if head is < 0, size should be 0.
	*/
	int			head;
	/** The current size of the stack (number of elements). */
	int			size;
	/** The total capacity of the stack (maximum size). */
	int			cap;
}	t_stack;

/**
 * @brief The structure storing the configurations and
 * information about the current sorting.
 */
typedef struct s_config
{
	int				bench_mode;
	t_strategies	strategy;
	double			disorder;
	int				total_count;
	int				sa_count;
	int				sb_count;
	int				ss_count;
	int				pa_count;
	int				pb_count;
	int				ra_count;
	int				rb_count;
	int				rr_count;
	int				rra_count;
	int				rrb_count;
	int				rrr_count;
}					t_config;

/**
 * @brief The structure of the data in the current program.
 */
typedef struct s_data
{
	t_stack		*stack_a;
	t_stack		*stack_b;
	t_config	*cfg;
}	t_data;

void	ft_error(void);
t_data	*init_data(int size_of_stack);
void	free_data(t_data *data);
void	normalize_rank(t_data *data);

#endif
