/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf_utils.c                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: jayam <jayam@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/02 17:25:24 by jayam             #+#    #+#             */
/*   Updated: 2026/11/26 14:22:15 by jayam            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_putchar(char c)
{
	ft_putchar_fd(c, 1);
	return (1);
}

int	ft_putstr(char *s)
{
	if (!s)
		s = "(null)";
	ft_putstr_fd(s, 1);
	return (ft_strlen(s));
}

int	ft_putptr(void *ptr)
{
	int				i;
	unsigned long	address;

	if (!ptr)
		return (write(1, "(nil)", 5));
	address = (uintptr_t)ptr;
	i = write(1, "0x", 2);
	i += ft_putbase(address, "0123456789abcdef", 16);
	return (i);
}

int	ft_putnbr(int nb)
{
	char	*s;
	int		i;

	s = ft_itoa(nb);
	if (!s)
		return (0);
	ft_putstr_fd(s, 1);
	i = ft_strlen(s);
	free(s);
	return (i);
}

int	ft_putbase(unsigned long nb, char *base, unsigned int base_len)
{
	int	i;

	i = 0;
	if (nb >= base_len)
		i += ft_putbase(nb / base_len, base, base_len);
	i += write(1, &base[nb % base_len], 1);
	return (i);
}
