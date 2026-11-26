/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_push_swap_utils.c                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 16:12:23 by jayam             #+#    #+#             */
/*   Updated: 2026/11/23 13:54:14 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

float	ft_disorder(void)
{
	return (0.0);
}

void	ft_error(void)
{
	write(2, "Error\n", 6);
	exit(1);
}

void	free_error(t_data *data)
{
	free_data(data);
	ft_error();
}

void	ft_validate(void)
{
}
