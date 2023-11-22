#include <stdint.h>
#include <stdio.h>
#include "e220400.h"

//////// FUNCTIONS //////////
void e2204_init( struct E220400 *e220400 ) {
	//Factory default parameter：c0 00 00 62 00 17
	uint8_t data[] = { 0xC1,0x00,0x06,0x00,0x00,0x62,0x00,0x17,0x00 };
	e220400_consume( e220400 , data );
}

void e220400_setMode( struct E220400 *e220400, uint8_t m0 , uint8_t m1 ){
	e220400->mode = m0&0b1 | ( (m1&0b1)<<1);
}	

uint8_t e220400_strip_rssi( struct E220400 *e220400, uint8_t* data, uint8_t len){
	if ( e220400->enableRssi == 1 ) {
		e220400->strengthRx = data[ len - 1 ];
		data[ len - 1 ] = '\0';
		return len - 1;
	}
	return len;
}

void e220400_consume( struct E220400 *e220400, uint8_t* data){
	if ( data[0] != 0xC1 ) return;
	uint8_t reg = data[1];
	uint8_t length = data[2];
	uint8_t ptr = 3;

	while ( ptr < length ){
		switch( reg ){
			case ADDRESS: {
				if ( length == 1 ) {
					e220400->noise = data[ptr];
					return;
				} 
				e220400->address = data[ptr++] | data[ptr++]<<8;
				reg += 2;
			} break;
			case 1: {
				if ( length == 1 ) e220400->strengthRx = data[ptr];
				return;
			} break;
			case REG0: {
				e220400->serialBaud = (data[ptr]>>5)&0b111;
				e220400->serialParity = (data[ptr]>>3)&0b11;
				e220400->airBaud = data[ptr++]&0b111;
				reg += 1;
			} break;
			case REG1: {
				e220400->subPacket = (data[ptr]>>6)&0b11; 
				e220400->rssiNoiseDetect = (data[ptr]>>5)&0b1;
				e220400->power = data[ptr++]&0b11;
				reg+=1;
			} break;
			case CHANNEL: {
				e220400->channel = data[ptr];
				reg +=1;		
			} break;
			case REG3: {
				e220400->enableRssi = (data[ptr]>>7)&0b1;
				e220400->transmissionMode= (data[ptr]>>6)&0b1;
				e220400->listenBeforeTransmit= (data[ptr]>>4)&0b1;
				e220400->wakeOnRadioCyle= data[ptr++]&0b1;
				reg +=1;
			} break;
			default: {
				ptr = 0xFF;
			} break;
		}
	}

}

uint8_t e220400_R_packet( struct E220400 * e220400, int what, void* data, uint8_t* out) {
	uint8_t len = 0;
	out[len++] = 0xC1;
	switch( what ){
		case ADDRESS: {
			out[len++] = ADDRESS;
			out[len++] = 2;
		} break;
		case REG0:
		case REG1:
		case REG3:
		case CHANNEL: {
			out[len++] = what;
			out[len++] = 1;
		} break;
		case REGISTER_BLOCK:{
			out[len++] = ADDRESS;
			out[len++] = 6;
		} break;
		case SIGNAL_RX_STRENGTH:
		case NOISE: {
			out[0] = 0xC0;
			out[1] = 0xC1;
			out[2] = 0xC2;
			out[3] = 0xC3;
			out[4] = what == NOISE ? 0x00 : 0x01;
			out[5] = 0x01;
			len = 6;
		} break;
	}
	return len;
}

uint8_t e220400_W_packet( struct E220400 * e220400, int what, void* data, uint8_t* out) {
	uint8_t len = 0;
	out[len++] = 0xC0;
	switch( what ){
		case ADDRESS: {
			out[len++] = ADDRESS;
			out[len++] = 2;
			out[len++] = (( uint8_t*)data)[0];
			out[len++] = (( uint8_t*)data)[1];
			return len;
		} break; //2B
		case REG0: {
			out[len++] = REG0;
			out[len++] = 1;
			out[len++] = *( uint8_t*)data;
			return len;
		} break; //1B
		case REG0_baud: {
			out[len++] = REG0;
			out[len++] = 1;
			out[len++] = (( *( uint8_t*)data )&0b111)<<5;
			out[len] |= ((e220400->serialParity)&0b11)<<3;
			out[len] |= ((e220400->airBaud)&0b111);
			return len;
		} break;
		case REG0_parity: {
			out[len++] = REG0;
			out[len++] = 1;
			out[len++] = ((e220400->serialBaud)&0b111)<<5;
			out[len] |= ( ( *( uint8_t*)data )&0b11)<<3;
			out[len] |= ((e220400->airBaud)&0b111);
			return len;
		} break;
		case REG0_air_baud: {
			out[len++] = REG0;
			out[len++] = 1;
			out[len++] = ((e220400->serialBaud)&0b111)<<5;
			out[len] |= ((e220400->serialParity)&0b11)<<3;
			out[len] |= ( *( uint8_t*)data )&0b111;
			return len;
		} break;
		case REG1: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = *( uint8_t*)data;
			return len;
		} break; //1B
		case REG1_subpacket: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ( ( *( uint8_t*)data )&0b11)<<6;
			out[len] |= ((e220400->rssiNoiseDetect)&0b1)<<5;
			out[len] |= ((e220400->power)&0b11);
			return len;
		} break; //2b
		case REG1_rssi_noise: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ((e220400->subPacket)&0b11)<<6;
			out[len] |= ( ( *( uint8_t*)data )&0b1)<<5;
			out[len] |= ((e220400->power)&0b11);
			return len;
		} break; //1b#
		case REG1_power: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ((e220400->subPacket)&0b11)<<6;
			out[len] |= ((e220400->rssiNoiseDetect)&0b1)<<5;
			out[len] |= ( *( uint8_t*)data )&0b11;
			return len;
		} break; //2b
		case CHANNEL: {
			out[len++] = CHANNEL;
			out[len++] = 1;
			out[len++] = *( uint8_t*)data;
			return len;
		} break; // 1B (REG2)
		case REG3: {
			out[len++] = REG3;
			out[len++] = 1;
			out[len++] = *( uint8_t*)data;
			return len;
		} break;
		case REG3_rssi_byte: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ( ( *( uint8_t*)data )&0b1)<<7;
			out[len] |= ((e220400->transmissionMode)&0b1)<<6;
			out[len] |= ((e220400->listenBeforeTransmit)&0b1)<<4;
			out[len] |= ((e220400->wakeOnRadioCyle)&0b1);
			return len;	
		} break; //1b
		case REG3_tx_mode: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ((e220400->enableRssi)&0b1)<<7;
			out[len] |= ( ( *( uint8_t*)data )&0b1)<<6;
			out[len] |= ((e220400->listenBeforeTransmit)&0b1)<<4;
			out[len] |= ((e220400->wakeOnRadioCyle)&0b1);
			return len;	
		} break; //1b
		case REG3_LBT_enable: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ((e220400->enableRssi)&0b1)<<7;
			out[len] |= ((e220400->transmissionMode)&0b1)<<6;
			out[len] |= (( *( uint8_t*)data )&0b1)<<4;
			out[len] |= ((e220400->wakeOnRadioCyle)&0b1);
			return len;	
		} break; //1b
		case REG3_WOR_cycle: {
			out[len++] = REG1;
			out[len++] = 1;
			out[len++] = ((e220400->enableRssi)&0b1)<<7;
			out[len] |= ((e220400->transmissionMode)&0b1)<<6;
			out[len] |= ((e220400->listenBeforeTransmit)&0b1)<<4;
			out[len] |= ( *( uint8_t*)data )&0b1;
			return len;	
		} break; //1b
		case REGISTER_BLOCK: {
			out[len++] = ADDRESS;
			out[len++] = 6;
			out[len++] = (( uint8_t*)data)[0];
			out[len++] = (( uint8_t*)data)[1];
			out[len++] = (( uint8_t*)data)[2];
			out[len++] = (( uint8_t*)data)[3];
			out[len++] = (( uint8_t*)data)[4];
			out[len++] = (( uint8_t*)data)[5];
			return len;
		} break;
		default: {
			return 0;
		} 
	}
}

//struct E220400 e220400;
//int main( void ) {
//	e2204_init( &e220400 );
//	printf("hello world\n%d\n%d",e220400.address,e220400.serialBaud);
//}
