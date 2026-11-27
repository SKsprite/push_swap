/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_push_swap_utils.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 16:12:23 by jayam             #+#    #+#             */
/*   Updated: 2026/11/27 21:19:14 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	ft_getval(t_stack *stack_a, int offset)
{
	return (stack_a->values[(stack_a->head + offset) % stack_a->cap].value);
}

/**
 * @brief Calculates disorder which reflects how far the stack is from being
 * sorted
 * 
 * Looks through all possible pairs of numbers within the stack. When a bigger
 * number appears before a smaller one, it is considered a mistake.
 * 
 * @param stack_a  Stack containing the parsed and validated data.
 * @return Returns disorder value calculated by dividing number of mistakes by
 * pairs
 */
double	ft_disorder(t_stack *stack_a)
{
	int		i;
	int		j;
	long	mistakes;

	if (!stack_a || stack_a->size < 2)
		return (0.0);
	i = 0;
	mistakes = 0;
	while (i < stack_a->size - 1)
	{
		j = i + 1;
		while (j < stack_a->size)
		{
			if (ft_getval(stack_a, i) > ft_getval(stack_a, j))
				mistakes++;
			j++;
		}
		i++;
	}
	return ((double)mistakes / ((long)stack_a->size
			* (stack_a->size - 1) / 2.0));
}

static char	*ft_stratlabel(t_config *cfg)
{
	char	*s;

	if (cfg->strategy == SIMPLE)
		s = "Simple / O(n^2)";
	else if (cfg->strategy == MEDIUM)
		s = "Medium / O(n√n)";
	else if (cfg->strategy == COMPLEX)
		s = "Complex / O(n log n)";
	else
	{
		if (cfg->disorder < 0.2)
			s = "Adaptive / O(n^2)";
		else if (cfg->disorder >= 0.2 && cfg->disorder < 0.5)
			s = "Adaptive / O(n√n)";
		else
			s = "Adaptive / O(n log n)";
	}
	return (s);
}

void	ft_bench(t_config *cfg)
{
	ft_printf("[bench] disorder: %d\n", cfg->disorder);
	ft_printf("[bench] strategy: %s\n", ft_stratlabel(cfg));
	ft_printf("[bench] total_ops: %d\n", cfg->total_count);
	ft_printf("[bench] sa: %a sb: %a ss: %a pa: %a pb: %a\n");
	ft_printf("[bench] ra: %a rb: %a rr: %a rra: %a rrb: %a rrr: %a\n");
}
// Helper function for disorder (variable type is a double)