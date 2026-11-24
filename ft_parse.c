/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_parse.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:54:09 by jayam             #+#    #+#             */
/*   Updated: 2026/11/23 17:22:44 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	ft_flags(char *argv[])
{
	int	i;

	i = 1;
	while (argv[i])
	{
		if (ft_strncmp(argv[i], "--bench") == 0)
			// Set bench
		// Check for strategy
	}
	return (i);
}

// Function(s) for benchmark

// Function(s) to parse integers into data structure
// - Multi-argument (2 1 3 6 5 8)
// - Split-argument ("4 67 3 87 24")