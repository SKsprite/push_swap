/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_main.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:50:49 by jayam             #+#    #+#             */
/*   Updated: 2026/11/27 21:21:20 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	main(int argc, char *argv[])
{
	int			i;
	t_data		*data;

	i = 1;
	if (argc == 1)
		return (0);
	// get_size_from_params 
	data = init_data(get_size_from_params(argv));
	// data->cfg->strategy = ADAPTIVE;
	// while (argv[i] != NULL)
	// {
	// 	i = ft_flags(argv, data->cfg);
	// 	if (argv[i] == NULL)
	// 		ft_error();
	// }
	free_data(data);
	return (0);
}

// Outline
// 1. Flag parsing[]
// 2. Count, allocate[], and initialize stacks[]
// 3. Validate data, populate stack and assign ranks[]
// 4. Initial disorder calculation[]
// 5. Strategy selection and execution
// - Default strategy is adaptive
// - How can an array indexed by enum be used to track operation counters?
// 6. Benchmark report[] and cleanup[]