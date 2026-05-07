#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"

#define BUFFER_SIZE 32
char buffer[BUFFER_SIZE];
int buffer_index = 0;

// Inicialización de UART0 (PA0 y PA1) a 9600 baudios
void UART0_Init(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, SysCtlClockGet(), 9600,
                        (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));
}

// Inicialización de pines para Puente H (Motores) en Puerto B
void Motores_Init(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    GPIOPinTypeGPIOOutput(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3);
}

// Detener todos los motores
void Detener(void) {
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, 0);
}

// Procesar comandos recibidos de la Raspberry Pi
void ProcesarComando(char* cmd) {
    if (strcmp(cmd, "fwd") == 0) {
        // Adelante (IN1 e IN3 encendidos)
        GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_0 | GPIO_PIN_2);
    } 
    else if (strcmp(cmd, "izq") == 0) {
        // Giro Izquierda (Solo motor derecho IN3)
        GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_2);
    } 
    else if (strcmp(cmd, "der") == 0) {
        // Giro Derecha (Solo motor izquierdo IN1)
        GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_0);
    } 
    else if (strcmp(cmd, "buscar") == 0) {
        // Modo Búsqueda: Giro sobre eje (IN1 adelante, IN4 atrás)
        // PB0=IN1, PB1=IN2, PB2=IN3, PB3=IN4
        GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_0 | GPIO_PIN_3);
    }
    else {
        Detener();
    }
}

int main(void) {
    // Reloj a 40MHz
    SysCtlClockSet(SYSCTL_SYSDIV_5 | SYSCTL_USE_PLL | SYSCTL_OSC_MAIN | SYSCTL_XTAL_16MHZ);
    
    UART0_Init();
    Motores_Init();
    Detener();

    while (1) {
        // Leer datos de UART si están disponibles
        while (UARTCharsAvail(UART0_BASE)) {
            char c = UARTCharGet(UART0_BASE);
            
            // Detectar fin de línea enviado por Python (ser.write(b'...\n'))
            if (c == '\n' || c == '\r') {
                buffer[buffer_index] = '\0';
                if (buffer_index > 0) {
                    ProcesarComando(buffer);
                    // Pequeño retardo para ejecutar el movimiento
                    SysCtlDelay(SysCtlClockGet() / 30); 
                    Detener();
                }
                buffer_index = 0;
            } else {
                if (buffer_index < BUFFER_SIZE - 1) {
                    buffer[buffer_index++] = c;
                }
            }
        }
    }
}