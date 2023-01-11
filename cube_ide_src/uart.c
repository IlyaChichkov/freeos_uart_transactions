/*
 * uart.c
 *
 *  Created on: Dec 6, 2022
 *      Author: Ilya
 */

#include "uart.h"

uint8_t input_buf[1];
uint8_t package[12];
int package_len = 0;

void uart3_handler(){

    while(1){
        if(HAL_UART_Receive(&uart4, input_buf, 1, 100) == HAL_OK){
            receiveDataHandler();
        }
        osDelay(1);
    }
}

void sendPackageData(){
	uint8_t package_data[8];

	for(int i = 0; i < 8; i++){
		package_data[i] = package[i + 3];
	}

	// packet address
	uint8_t addr[2];
	addr[0] = package[1];
	addr[1] = package[2];

	int addr_int = 0;
	if(addr[1] == '1'){
		addr_int += 1;
	}else{
		addr_int = 0;
	}
	if(addr[0] == '1'){
		addr_int += 2;
	}else{
		addr_int += 0;
	}

	switch (addr_int) {
		case 0:	// UART 5 (address - 00)
			if(HAL_UART_Transmit(&uart5, package_data, 8, 100) == HAL_OK){
				HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
			}
			break;
		case 1:	// UART 5 (address - 01)
			if(HAL_UART_Transmit(&uart3, package_data, 8, 100) == HAL_OK){
				HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
			}
			break;
	}
}


uint8_t ansErr[] = "0\0"; // set answer - error
uint8_t ansOk[] = "1\0"; // set answer - error

void sendAnswer(int ans){
	if(ans == 1){
		HAL_UART_Transmit(&uart4, ansOk, 1, 100);
	}else{
		HAL_UART_Transmit(&uart4, ansErr, 1, 100);
	}
}

void receiveDataHandler(){
	uint8_t read[1];
	read[0] = input_buf[0];

	if(package_len == 0 && read[0] != '0'){
		sendAnswer(0);
		return;
	}

	package[package_len] = read[0];   // add data to packet (12 bits)

	if(package_len > 10){ // when full packet received
		// check start and end of packet
		if(package[0] == '0' && package[11] == '1'){
			sendPackageData();
			sendAnswer(1);
		}else{
			sendAnswer(0);
		}
		package_len = 0;
	}else{
		package_len++;
	}
}
