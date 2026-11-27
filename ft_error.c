/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_error.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/27 14:34:30 by jayam             #+#    #+#             */
/*   Updated: 2026/11/27 14:36:40 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	ft_error(void)
{
	write(2, "Error\n", 6);
	exit(1);
}

void	free_stack(t_data *data)
{
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

void	free_error(t_data *data)
{
	free_data(data);
	ft_error();
}
