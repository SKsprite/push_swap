/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strmapi.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/26 18:08:24 by jayam             #+#    #+#             */
/*   Updated: 2026/10/20 10:21:11 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strmapi(char const *s, char (*f)(unsigned int, char))
{
	char			*nstr;
	unsigned int	i;

	if (!s || !f)
		return (NULL);
	nstr = ft_calloc(ft_strlen(s) + 1, sizeof(char));
	if (!nstr)
		return (NULL);
	i = 0;
	while (*(s + i))
	{
		*(nstr + i) = f(i, *(s + i));
		i++;
	}
	return (nstr);
}
