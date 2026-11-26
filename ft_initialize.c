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
 * @brief Creates the stack and initialise the data
 *
 * Malloc a data structure for both stack a and stack b.
 *
 * @param size_of_stack  The number of elements in the stack.
 * @param data  The data of the entire program
 * @return Returns 1 if its able to initalize the stack, 0 if it fails.
 */
int	init_stacks(int size_of_stack, t_data *data)
{
	data->stack_a->cap = size_of_stack;
	data->stack_a->size = size_of_stack;
	data->stack_a->head = -1;
	data->stack_a->values = ft_calloc(sizeof(t_element), size_of_stack);
	data->stack_b->cap = size_of_stack;
	data->stack_b->size = 0;
	data->stack_b->head = -1;
	data->stack_b->values = ft_calloc(sizeof(t_element), size_of_stack);
	if (data->stack_a->values && data->stack_b->values)
		return (1);
	free(data->stack_a->values);
	free(data->stack_b->values);
	return (0);
}

/**
 * @brief Creates an empty data structure on the heap.
 *
 * Malloc a data structure storing stack a, stack b and configurations
 * set for the program.
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
	if (!data->stack_a || !data->stack_b || !init_stacks(size_of_stack, data))
		return (free(data->stack_a), free(data->stack_b), free(data), NULL);
	data->cfg = malloc(sizeof(t_config));
	if (!data->cfg)
		return (free_stack(data), free(data), NULL);
	return (data);
}

void	free_stack(t_data *data)
{
	int	i;
	
	i = 0;
	while (i < data->stack_a->cap)
	{
		free(&data->stack_a->values[i]);
		free(&data->stack_b->values[i]);
		i++;
	}
	free(data->stack_a->values);
	free(data->stack_b->values);
	free(data->stack_a);
	free(data->stack_b);
}

/**
 * @brief Frees the data structure of the program.
 *
 * Frees the given data structure and all elements within stack a, stack b
 * and the configurations set for the program.
 *
 * @param data  The data of the entire program.
 */
void	free_data(t_data *data)
{
	free_stack(data);
	free(data->cfg);
	free(data);
}
