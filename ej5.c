#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"

#define BUFFER_SIZE 64
char buffer[BUFFER_SIZE];
int buffer_index = 0;

void UART0_Init(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, SysCtlClockGet(), 9600,
                        (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));
}

void Motores_Init(void) {
    // Configuracion de pines para el puente H (IN1, IN2, IN3, IN4)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    GPIOPinTypeGPIOOutput(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3);
}

void Detener_Motores(void) {
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, 0);
}

int main(void) {
    SysCtlClockSet(SYSCTL_SYSDIV_4 | SYSCTL_USE_PLL | SYSCTL_OSC_MAIN | SYSCTL_XTAL_16MHZ);
    
    UART0_Init();
    Motores_Init();
    Detener_Motores();

    while (1) {
        if (UARTCharsAvail(UART0_BASE)) {
            char c = UARTCharGet(UART0_BASE);
            
            if (c == '\n' || c == '\r') {
                buffer[buffer_index] = '\0';
                
                if (strcmp(buffer, "motor1") == 0) {
                    // Girar motor 1 (Izquierda)
                    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0, GPIO_PIN_0);
                    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_1, 0);
                } 
                else if (strcmp(buffer, "motor2") == 0) {
                    // Girar motor 2 (Derecha)
                    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, GPIO_PIN_2);
                    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_3, 0);
                }
                else if (strcmp(buffer, "stop") == 0) {
                    Detener_Motores();
                }
                
                buffer_index = 0;
                // Pequeño delay para evitar saturacion
                SysCtlDelay(SysCtlClockGet() / 100); 
                Detener_Motores(); 
            } else {
                if (buffer_index < BUFFER_SIZE - 1) {
                    buffer[buffer_index++] = c;
                }
            }
        }
    }
}