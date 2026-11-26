/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_normalize_rank.c                                :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: stkoh <stkoh@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/26 16:17:21 by stkoh             #+#    #+#             */
/*   Updated: 2026/11/26 16:18:23 by stkoh            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	normalize_rank(t_data *data)
{
	int			i;
	int			j;
	int			counter;
	t_element	*index;

	i = 0;
	index = data->stack_a->values;
	while (i < data->stack_a->size)
	{
		j = 0;
		counter = 0;
		while (j < data->stack_a->size)
		{
			if (index[j].value < index[i].value)
				counter++;
			j++;
		}
		index[i].rank = counter;
		i++;
	}
}
