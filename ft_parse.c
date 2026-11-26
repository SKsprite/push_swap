/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_parse.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:54:09 by jayam             #+#    #+#             */
/*   Updated: 2026/11/26 14:00:43 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	ft_flags(char *argv[], t_config *cfg)
{
	int	i;
	int	strat_set;

	i = 1;
	strat_set = 0;
	// Check that it starts with "--"
	while (argv[i] != NULL && )
	{
		// Use ft_strncmp
		if (argv[i] == "--bench")
			cfg->bench_mode = 1;
		if (strat_set == 0)
		{
			if (argv[i] == "--simple")
				cfg->strategy = SIMPLE;
			else if (argv[i] == "--medium")
				cfg->strategy = MEDIUM;
			else if (argv[i] == "--complex")
				cfg->strategy = COMPLEX;
		}
		else
			ft_error();
		i++;
	}
	return (i);
}
