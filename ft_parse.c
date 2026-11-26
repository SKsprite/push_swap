/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_parse.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:54:09 by jayam             #+#    #+#             */
/*   Updated: 2026/11/26 16:45:54 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	ft_strat(char *argv, t_config *cfg, int *strat_set)
{
	if (ft_strncmp(argv, "--simple", 9) == 0)
		cfg->strategy = SIMPLE;
	else if (ft_strncmp(argv, "--medium", 9) == 0)
		cfg->strategy = MEDIUM;
	else if (ft_strncmp(argv, "--complex", 10) == 0)
		cfg->strategy = COMPLEX;
	else if (ft_strncmp(argv, "--adaptive", 11) == 0)
		cfg->strategy = ADAPTIVE;
	else
		ft_error();
	*strat_set = 1;
}

int	ft_flags(char *argv[], t_config *cfg)
{
	int	i;
	int	strat_set;

	i = 1;
	strat_set = 0;
	while (argv[i] && ft_strncmp(argv[i], "--", 2) == 0)
	{
		if (ft_strncmp(argv[i], "--bench", 8) == 0)
			cfg->bench_mode = 1;
		else if (strat_set == 0)
			ft_strat(argv[i], cfg, &strat_set);
		else
			ft_error();
		i++;
	}
	return (i);
}
