/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_initialize.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: stkoh <stkoh@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/26 12:08:19 by stkoh             #+#    #+#             */
/*   Updated: 2026/11/26 13:05:02 by stkoh            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

*t_data	init_data(int size_of_stack)
{
	t_data	*data;

	data = malloc(sizeof(s_data));
	if (!data)
		return (NULL);
	data->stack_a = malloc(sizeof(size_of_stack));
	data->stack_b = malloc(sizeof(size_of_stack));
	if (!data->stack_a || !data->stack_b)
		return (free(data->stack_a), free(data->stack_b), free(data), NULL);
	data->cfg = malloc(sizeof(s_config));
	if (!data->cfg)
		return (free(data->stack_a), free(data->stack_b), free(data), NULL);
	return (data);
}


void	free_data(t_data *data)
{
	free(data->stack_a);
	free(data->stack_b);
	free(data->cfg);
	free(data);
}
