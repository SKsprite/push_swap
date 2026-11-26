/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_parse.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/22 15:54:09 by jayam             #+#    #+#             */
/*   Updated: 2026/11/25 20:34:37 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	*ft_flags(char *argv[], int *p, t_config *cfg)
{
	if (argv[*p++] == "--bench")
		cfg->bench_mode = 1;
	if (argv[*p] == "--simple")
		cfg->strategy = SIMPLE;
	else if (argv[*p] == "--medium")
		cfg->strategy = MEDIUM;
	else if (argv[*p] == "--complex")
		cfg->strategy = COMPLEX;
	(*p)++;
	return (p);
}

// Function(s) for benchmark