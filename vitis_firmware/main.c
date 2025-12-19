#include <stdio.h>
#include <stdlib.h>
#include "platform.h"
#include "xil_printf.h"
#include "xparameters.h"
#include "xuartpsv.h"
#include "xil_types.h"
#include "xgpio.h"
#include "systolic_params.h"
//#########################################################################
#define HANDSHAKE_ID XPAR_GPIO_0_DEVICE_ID
#define DONE_CHANNEL 1
#define ACK_CHANNEL 2
#define DIR_OUTPUT 0
#define DIR_INPUT 1
//#########################################################################
#define PACKET_LENGTH 8 + N
#define NUM_OF_PACKETS N + 2
//#########################################################################
void request_packet();
void read_packet(u32* packet);
void write_packet(u32* packet);
void sync_to_placer(XGpio* handshake_device_ptr);
void read_placement();
//#########################################################################
int main()
{
	//*********************************************************************
	// Init
    init_platform();

    XGpio_Config *gpio_cfg_ptr;
    XGpio handshake_device;

    gpio_cfg_ptr = XGpio_LookupConfig(HANDSHAKE_ID);
    XGpio_CfgInitialize(&handshake_device, gpio_cfg_ptr, gpio_cfg_ptr->BaseAddress);

    XGpio_SetDataDirection(&handshake_device, DONE_CHANNEL, DIR_OUTPUT);
    XGpio_SetDataDirection(&handshake_device, ACK_CHANNEL, DIR_INPUT);

	while(1)
	{
		//*****************************************************************
		// Load the placer
		u32 packet[PACKET_LENGTH];

		// Wait for loader/unloader connection
		inbyte();

		for(u32 x = 0; x < NUM_OF_PACKETS; x++)
		{
			request_packet();
			read_packet(packet);
			write_packet(packet);
			sync_to_placer(&handshake_device);
		}
		//*****************************************************************
		// Start Placement
		sync_to_placer(&handshake_device);
		//*****************************************************************
		// Get placement data
		read_placement();
		//*****************************************************************
	}

    cleanup_platform();
    return 0;
}
//#########################################################################
// Request packet from UART
void request_packet()
{
	xil_printf("[Requesting packet]\n");
}
//#########################################################################
// Read packet from UART
void read_packet(u32* packet)
{
	char data[4];
	u32 index;
	for(u32 x = 0; x < PACKET_LENGTH; x++)
	{
		index = 0;
		while(1)
		{
			data[index] = inbyte();
			if(data[index] == '\n')
			{
				break;
			}
			index += 1;
		}
		packet[x] = strtol(data,NULL,16);
	}
}
//#########################################################################
// Write packet to BRAM
void write_packet(u32* packet)
{
	UINTPTR address = XPAR_BRAM_0_BASEADDR;
	for(u32 x = 0; x < PACKET_LENGTH; x++)
	{
		Xil_Out32(address,packet[x]);
		address += 4;
	}
}
//#########################################################################
void sync_to_placer(XGpio* handshake_device_ptr)
{
	// Assert Done
	XGpio_DiscreteWrite(handshake_device_ptr, DONE_CHANNEL, 1);

	// Wait for Ack
	while(XGpio_DiscreteRead(handshake_device_ptr, ACK_CHANNEL) == 0){}

	// Deassert Done
	XGpio_DiscreteWrite(handshake_device_ptr, DONE_CHANNEL, 0);

	// Wait for Ack to deassert
	while(XGpio_DiscreteRead(handshake_device_ptr, ACK_CHANNEL) == 1){}
}
//#########################################################################
void read_placement()
{
	UINTPTR address = XPAR_BRAM_0_BASEADDR;
	for(u32 x = 0; x < N; x++)
	{
		u32 data = Xil_In32(address);
		xil_printf("%d\n",data);
		address += 4;
	}
}
//#########################################################################