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
        if(HAL_UART_Receive(&uart4, input_buf, 1, 1000) == HAL_OK){
            HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_11);
            sendData();
        }
        osDelay(1);
    }
}

void sendPackage(){
	// packet address
	uint8_t package_data[8];

	for(int i = 0; i < 8; i++){
		package_data[i] = package[i + 3];
	}

	// packet address
	uint8_t addr[2];
	addr[0] = package[1];
	addr[1] = package[2];

	/*
	if(HAL_UART_Transmit(&uart3, read, 12, 1000) == HAL_OK){
		HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
	}*/
	/*
	int addr_int = 0;

	if(addr[1] == '1'){
		addr_int += 1;
	}else{
		addr_int = 0;
	}
	if(addr[0] == '1'){
		addr_int += 2;
	}*/
	/*
	if(HAL_UART_Transmit(&uart3, addr, 2, 1000) == HAL_OK){
		HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
	}*/

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
		case 0:
			if(HAL_UART_Transmit(&uart5, package_data, 8, 1000) == HAL_OK){
				HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
			}
			break;
		case 1:
			if(HAL_UART_Transmit(&uart3, package_data, 8, 1000) == HAL_OK){
				HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
			}
			break;
	}
}

void sendData(){
	uint8_t read[1];
    read[0] = input_buf[0];

    if(package_len == 0 && read[0] != '0'){
    	return;
    }

    package[package_len] = read[0];   // add data to packet (12 bits)

    if(package_len > 10){ // when packet received
    	if(package[0] == '0' && package[11] == '1'){
    		sendPackage();
			uint8_t ans[] = "1\0";
			HAL_UART_Transmit(&uart4, ans, 1, 1000);
    	}else{
			uint8_t ans[] = "0\0";
			HAL_UART_Transmit(&uart4, ans, 1, 1000);
    	}
        package_len = 0;
    }else{
        package_len++;
    }
}

void uart4_handler(){
    uint8_t buf[10];
    while(1) {

        if(HAL_UART_Receive(&uart4, buf, 1, 1000) == HAL_OK){
            //HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_11);
            if(HAL_UART_Transmit(&uart4, buf, 1, 1000) == HAL_OK){
                HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_11);
            }
        }
        //manageIncomePackage();
        osDelay(100);
    }
}

void manageIncomePackage(){

    while(1) {
        //HAL_UART_Transmit(&uart4, str, strlen(str), 1000);
        //HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_9);
        osDelay(500);
    }
}

void uart5_handler(){
    //uint8_t buf[2];

    while(1){
        osDelay(100);/*
        if(HAL_UART_Receive(&uart4, buf, 1, 1000) == HAL_OK){
        	uint8_t read[2];
        	read[0] = buf[0];
        	read[1] = buf[1];
            if(HAL_UART_Transmit(&uart5, read, 1, 1000) == HAL_OK){
                HAL_GPIO_TogglePin(GPIOE, GPIO_PIN_11);
            }
        }
        osDelay(1);*/
    }
}
