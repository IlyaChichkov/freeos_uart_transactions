/*
 * uart.h
 *
 *  Created on: Dec 6, 2022
 *      Author: Ilya
 */

#ifndef INC_UART_H_
#define INC_UART_H_

#include <stdio.h>
#include "main.h"
#include "string.h"

UART_HandleTypeDef uart3;
UART_HandleTypeDef uart4;
UART_HandleTypeDef uart5;

void uart3_handler();
void uart4_handler();
void uart5_handler();

void sendPackage();

void sendData();

void manageIncomePackage();

#endif /* INC_UART_H_ */
