/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_main.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:50:49 by jayam             #+#    #+#             */
/*   Updated: 2026/11/26 14:01:21 by stkoh            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	main(int argc, char *argv[])
{
	int			i;
	t_data		data;

	i = 1;
	if (argc == 1)
		return (0);
	// Initialize t_data
	data->cfg.strategy = ADAPTIVE;
	while (argv[i] != NULL)
	{
		i = ft_flags(argv, &data.cfg);
		if (argv[i] == NULL)
			ft_error();
	}
	return (0);
}

// Outline
// 1. Flag parsing
// 2. Count, allocate, and initialize stacks
// 3. Validate data, populate stack and assign ranks
// 4. Initial disorder calculation
// 5. Strategy selection and execution - default strategy is adaptive
// 6. Benchmark report and cleanup

// How can an array indexed by enum be used to track operation counters?
