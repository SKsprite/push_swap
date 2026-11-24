/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_utils1.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: stkoh <stkoh@student.42singapore.sg>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/25 12:48:26 by stkoh             #+#    #+#             */
/*   Updated: 2026/10/25 13:00:41 by stkoh            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

t_stack	stack_new(int i)
{
	t_stack	num;

	num = malloc(sizeof(s_stack));
	if (!num)
		return (NULL);
	num->num = i;
	num->prev = NULL;
	num->next = NULL;
	return (num);
}

t_stack	get_last(t_stack **head)
{
	t_stack	*next;

	if (!*head)
		return (NULL);
	next = **head;
	while (next->next != *head)
		next = next->next;
	return next;
}

