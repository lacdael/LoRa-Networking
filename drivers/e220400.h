#ifndef H_E220440
#define H_E220440

//e22400_v1

//////// DATA      //////////
#define BAUD_1200 0
#define BAUD_2400 1
#define BAUD_4800 2
#define BAUD_9600 3
#define BAUD_19200 4
#define BAUD_38400 5
#define BAUD_57600 6
#define BAUD_115200 7
#define PARITY_8N1 0
#define PARITY_801 1
#define PARITY_8E1 2
#define AIR_BAUD_2400000 0
#define AIR_BAUD_2400000_ 1
#define AIR_BAUD_2400000__ 2
#define AIR_BAUD_4800000 3
#define AIR_BAUD_9600000 4
#define AIR_BAUD_19200000 5
#define AIR_BAUD_38400000 6
#define AIR_BAUD_62500000 7
#define SUB_PACKET_200 0
#define SUB_PACKET_128 1
#define SUB_PACKET_64 2
#define SUB_PACKET_32 3
#define POWER_22 0
#define POWER_17 1
#define POWER_13 2
#define POWER_10 3
#define WAKE_ON_RADIO_TIME_500 0
#define WAKE_ON_RADIO_TIME_1000 1
#define WAKE_ON_RADIO_TIME_1500 2
#define WAKE_ON_RADIO_TIME_2000 3
#define WAKE_ON_RADIO_TIME_2500 4
#define WAKE_ON_RADIO_TIME_3000 5
#define WAKE_ON_RADIO_TIME_3500 6
#define WAKE_ON_RADIO_TIME_4000 7
#define ADDRESS 0 //2B
#define REG0 2 //1B
#define REG0_baud 0x25 //3b
#define REG0_parity 0x23 //2b
#define REG0_air_baud 0x20 //3b
#define REG1 3 //1B
#define REG1_subpacket 0x36 //2b
#define REG1_rssi_noise 0x35 //1b
#define REG1_power 0x30 //2b
#define CHANNEL 4 // 1B (REG2)
#define REG3 5
#define REG3_rssi_byte 0x57 //1b
#define REG3_tx_mode 0x56 //1b
#define REG3_LBT_enable 0x54 //1b
#define REG3_WOR_cycle 0x50 //3b
#define ENCRYPTION 6
#define SIGNAL_RX_STRENGTH 0xFD
#define NOISE 0xFE
#define REGISTER_BLOCK 0xFF

#define MODE_TRANSMISSION 0b00
#define MODE_WOR_TRANSMITTING 0b01
#define MODE_WOR_RECEIVING 0b10
#define MODE_SLEEP_CONFIG 0b11

struct E220400 {
	uint16_t address; //default 0x0000
	uint8_t serialBaud; //device default 9600
	uint8_t serialParity; // device default 8n1
	uint8_t airBaud; // device default 2.4k
	uint8_t rssiNoiseDetect; // device default 0
	uint8_t subPacket; // device default 200 bytes
	uint8_t power; // device default 22dbm
	uint8_t channel;
	uint8_t enableRssi; // device default off
	uint8_t listenBeforeTransmit; // device default off
	uint8_t wakeOnRadioCyle;
	uint8_t transmissionMode; //device default transparent (0)
	uint16_t encryption; // default 0x0000
	uint8_t noise;
	uint8_t strengthRx;
	//0b00: trx,0b01:wor tx,0b10 wor rx, 0b11 conf/sleep
	uint8_t mode;
};


//////// FUNCTIONS //////////

void e2204_init( struct E220400 *e220400 );
void e220400_setMode( struct E220400 *e220400, uint8_t m0 , uint8_t m1 );
uint8_t e220400_strip_rssi( struct E220400 *e220400, uint8_t* data, uint8_t len);
void e220400_consume( struct E220400 *e220400, uint8_t* data);
uint8_t e220400_W_packet( struct E220400 * e220400, int what, void* data, uint8_t* out);
uint8_t e220400_R_packet( struct E220400 * e220400, int what, void* data, uint8_t* out);

#endif // H_E220440

