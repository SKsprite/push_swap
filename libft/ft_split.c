/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/26 18:07:04 by jayam             #+#    #+#             */
/*   Updated: 2026/10/15 17:10:59 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	count_words(char const *s, char c)
{
	int	i;
	int	words;
	int	word_switch;

	i = 0;
	words = 0;
	word_switch = 0;
	while (s[i])
	{
		if (s[i] != c && word_switch == 0)
		{
			word_switch = 1;
			words++;
		}
		if (s[i] == c)
			word_switch = 0;
		i++;
	}
	return (words);
}

static void	free_split(char **split, int slots)
{
	while (slots > 0)
	{
		slots--;
		free(split[slots]);
	}
	free(split);
	return ;
}

static size_t	word_length(char const *s, char c)
{
	size_t	i;

	i = 0;
	while (s[i] && s[i] != c)
		i++;
	return (i);
}

char	**ft_split(char const *s, char c)
{
	char	**split;
	int		i;
	int		slots;

	split = ft_calloc(count_words(s, c) + 1, sizeof(char *));
	if (!split)
		return (NULL);
	i = 0;
	slots = 0;
	while (s[i])
	{
		if (s[i] != c)
		{
			split[slots] = ft_substr(s, (unsigned int)i, word_length(&s[i], c));
			if (!split[slots])
				return (free_split(split, slots), NULL);
			slots++;
			i += word_length(&s[i], c);
		}
		else
			i++;
	}
	return (split);
}
