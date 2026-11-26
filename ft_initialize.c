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

/**
 * @brief Creates an empty data structure on the heap.
 *
 * Malloc a data structure storing stack a, stack b and configurations set for the program.
 *
 * @param size_of_stack  The number of elements in the stack.
 * @return The address of the initalized data if its created and NULL on error.
 */
t_data	*init_data(int size_of_stack)
{
	t_data	*data;

	data = malloc(sizeof(t_data));
	if (!data)
		return (NULL);
	data->stack_a = malloc(sizeof(t_stack));
	data->stack_b = malloc(sizeof(t_stack));
	// ft_calloc(size_of_stack, sizeof(s_element));
	// data->stack_b = ft_calloc(size_of_stack, sizeof(s_element));
	if (!data->stack_a || !data->stack_b)
		return (free(data->stack_a), free(data->stack_b), free(data), NULL);
	data->cfg = malloc(sizeof(t_config));
	if (!data->cfg)
		return (free(data->stack_a), free(data->stack_b), free(data), NULL);
	data->stack_a->cap = size_of_stack;
	data->stack_b->cap = size_of_stack;
	return (data);
}

/**
 * @brief Frees the data structure of the program.
 *
 * Frees the given data structure and all elements within stack a, stack b and the configurations set for the program.
 *
 * @param size_of_stack  The number of elements in the stack.
 * @return The address of the initalized data if its created and NULL on error.
 */
void	free_data(t_data *data)
{
	free(data->stack_a);
	free(data->stack_b);
	free(data->cfg);
	free(data);
}