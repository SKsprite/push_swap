/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/26 18:07:35 by jayam             #+#    #+#             */
/*   Updated: 2026/10/20 10:21:43 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	count_digits(int n)
{
	int	i;

	i = 0;
	if (n < 0)
	{
		n *= -1;
		i++;
	}
	if (n == 0)
		return (1);
	while (n != 0)
	{
		i++;
		n /= 10;
	}
	return (i);
}

char	*ft_itoa(int n)
{
	char	*str;
	int		len;

	if (n == -2147483648)
		return (ft_strdup("-2147483648"));
	if (n == 0)
		return (ft_strdup("0"));
	len = count_digits(n);
	str = ft_calloc(len + 1, sizeof(char));
	if (!str)
		return (NULL);
	if (n < 0)
	{
		n *= -1;
		*str = '-';
	}
	while (n != 0)
	{
		*(str + len - 1) = (n % 10) + '0';
		n /= 10;
		len--;
	}
	return (str);
}
