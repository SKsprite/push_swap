/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_main.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:50:49 by jayam             #+#    #+#             */
/*   Updated: 2026/11/23 17:19:28 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	main(int argc, char *argv[])
{
	int	i;

	i = 1;
	if (argc == 1)
		exit(0);
	else
	{
		while (argv[i] != NULL)
		{
			// Flag parsing
			// Integer parsing
			i++;
		}
		// Validate
	}
	return (0);
}

// Outline
// 1. Flag parsing
// 2. Parse integers into data structure
// 3. Validate data; some issues which display error on the stderr:
// - Arguments that are not integers
// - Integers outside valid range (INT_MIN/INT_MAX)
// - Duplicate values
// 4. Stack initialization & operations (stack formatting; 2-3 files)
// 5. Initial disorder calculation:
// - What if initial disorder is 0?
// 6. Strategy selection and execution - default strategy is adaptive