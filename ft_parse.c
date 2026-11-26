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

int	ft_flags(char *argv[], t_data *data)
{
	int	i;
	int	strat_set;
	t_config	*cfg;

	i = 1;
	strat_set = 0;
	cfg = data->cfg;
	while (argv[i] && ft_strncmp(argv[i], "--", 2) == 0)
	{
		if (ft_strncmp(argv[i], "--bench", 8) == 0)
			cfg->bench_mode = 1;
		else if (strat_set == 0)
			ft_strat(argv[i], cfg, &strat_set);
		else
			free_error(data);
		i++;
	}
	return (i);
}

int	check_is_digit(char *str)
{
	int	i;
	int	j;
	int count;

	i = 0;
	count = 0;
	while (str[i])
	{
		while (str[i] == ' ')
			i++;
		j = i;
		while (str[i] && str[i] != ' ')
		{
			if (i == j && (str[j] == '-' || ft_isdigit(str[i])))
				i++;
			else if (ft_isdigit(str[i]))
				i++;
			else
				return (-1);
		}
		count++;
	}
	return (count);
}

/**
 * @brief Frees the data structure of the program.
 *
 * Frees the given data structure and all elements within stack a, stack b
 * and the configurations set for the program.
 *
 * @param data  The data of the entire program.
 */
int	get_size_from_params(char *argv[])
{
	char	*str;
	int		count;
	int		result;

	count = 0;
	argv++;
	while (*argv)
	{
		str = *argv;
		result = check_is_digit(str);
		if (result < 0)
			ft_error();
		count += result;
		argv++;
	}
	ft_printf("%d\n", count);
	return (count);
}