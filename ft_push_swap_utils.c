/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_push_swap_utils.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 16:12:23 by jayam             #+#    #+#             */
/*   Updated: 2026/11/27 14:57:54 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

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
	int 	j;
	long	mistakes;
	long	pairs;

	if (!stack_a || stack_a->size < 2)
		return (0.0);
	mistakes = 0;
	pairs = 0;
	while (i < stack_a->size - 1)
	{
		j = i + 1;
		while (j < stack_a->size)
		{
			pairs++;
			
			j++;
		}
		i++;
	}
	return ((double)mistakes / (double)pairs);
}
