/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_main.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:50:49 by jayam             #+#    #+#             */
/*   Updated: 2026/11/22 17:32:47 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	ft_flags(char *argv)
{
	// Check whether there is bench present
	// Check what strategy is indicated on flag
	// Store flag indicated
}

int	main(int argc, char *argv[])
{
	int	i;

	i = 1;
	if (argc == 1)
		exit(0);
	else
	{
		while (*argv[i])
		{
			// Check flags
			// Read and validate
		}
	}
	return (0);
}

// Outline
// 1. Flag parsing - .c file for benchmark?
// 2. Read integers into data structure from stdin
// 3. Integer validation; some issues which display error on the stderr:
// - Arguments that are not integers
// - Integers outside valid range
// - Duplicate values
// 4. Stack initialization & operations (stack formatting)
// 5. Initial disorder calculation:
// - what if initial disorder is 0?
// 6. Strategy selection and execution