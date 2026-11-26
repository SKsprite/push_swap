/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:34:05 by jayam             #+#    #+#             */
/*   Updated: 2026/11/26 15:52:14 by jayam            ###   ########.fr       */
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

typedef struct s_element
{
	int	value;
	int	rank;

}	t_element;

typedef struct s_stack
{
	t_element	*values;
	int			head;
	int			size;
	int			cap;
}	t_stack;

typedef struct s_data
{
	t_stack		*stack_a;
	t_stack		*stack_b;
	t_config	*cfg;
}	t_data;

void	ft_error(void);

#endif
