#!/usr/bin/env python3

import serial.tools.list_ports
import serial
import time
import traceback

port = None;
DEFAULT_BAUD = 9600;

class E220400():

    _port = None;
    _conf = {
        "reg0": {
            "serialBaud":9600,
            "serialParity":"8N1",
            "airBaud":"2.4k"
        },
        "reg1": {
            "rssiNoiseDetect":0,
            "subPacket":"200 bytes",
            "power":"22dBm"
        },
        "reg3": {}
    };

    ADDRESS = "address";
    CHANNEL = "channel";
    ENCRYPTION = "encryption";
    REG0 = "reg0";
    REG1 = "reg1";
    REG3 = "reg3"
    SERIAL_BAUD = "serialBaud";
    SERIAL_PARITY = "serialParity";
    AIR_BAUD = "airBaud"
    SUB_PACKET = "subPacket";
    RSSI_NOISE_DETECT = "rssiNoiseDetect";
    POWER = "power";
    RSSI_BYTE = "rssiByte";
    FIXED_TRANSMISSION = "fixedTransmission";
    LISTEN_BEFORE_TALK = "listenBeforeTalk";
    WAKE_ON_RADIO_TIME = "wakeOnRadioTime";
    NOISE = "noise";

    ARRAY_BAUD = [1200,2400,4800,9600,19200,38400,57600,115200];
    ARRAY_PARITY = ["8N1","8O1","8E1"]
    ARRAY_AIR_BAUD = ["2.4k","2.4k","2.4k","4.8k","9.6k","19.2k","38.4k","62.5k"]
    ARRAY_SUB_PACKET = ["200 bytes","128 bytes","64 bytes","32 bytes"]
    ARRAY_POWER = ["22dBm","17dBm","13dBm","10dBm"];
    ARRAY_WAKE_ON_RADIO_TIME = [500,1000,1500,2000,2500,3000,3500,4000]

    def __init__(self, **kwargs):
        if "port" in kwargs:
            self._port = kwargs.get("port");

    def forMachine( self, what , data ):
        print("forMachine {} {}".format(what,data));
        if what == self.SERIAL_BAUD:
            if data in self.ARRAY_BAUD:
                return self.ARRAY_BAUD.index(data);
            else:
                return 4; #9600
        elif what == self.SERIAL_PARITY:
            if data in self.ARRAY_PARITY:
                return self.ARRAY_PARITY.index(data)
            else: # 8N1
                return 0; #8N1
        elif what == self.AIR_BAUD:
            if data in self.ARRAY_AIR_BAUD:
                return self.ARRAY_AIR_BAUD.index(data)
            else:
                return 2 # 2.4k
        elif self.SUB_PACKET:
            if data == self.ARRAY_SUB_PACKET:
                return self.ARRAY_SUB_PACKET.index(data)
            else:
                return 0;
        elif what == self.POWER:
            if data in self.ARRAY_POWER:
                return self.ARRAY_POWER.index(data)
            else:
                return 0;
        elif what == self.WAKE_ON_RADIO_TIME:
            if data in self.ARRAY_WAKE_ON_RADIO_TIME:
                return self.ARRAY_WAKE_ON_RADIO_TIME.index(data)

    def forHuman( self, what , data ):
        if what == self.SERIAL_BAUD:
            if data >= 0 and data < len(self.ARRAY_BAUD):
                return self.ARRAY_BAUD[data];
            else:
                return 9600
        elif what == self.SERIAL_PARITY:
            if data >= 0 and data < len(self.ARRAY_PARITY):
                return self.ARRAY_PARITY[data];
            else:
                return "8N1";
        elif what == self.AIR_BAUD:
            if data >= 0 and data < len(self.ARRAY_AIR_BAUD):
                return self.ARRAY_AIR_BAUD[data];
            else:
                return "2.4k";
        elif what == self.SUB_PACKET:
            if data >= 0 and data < len(self.ARRAY_SUB_PACKET):
                return self.ARRAY_SUB_PACKET[data];
            else:
                return "200 bytes";
        elif what == self.POWER:
            if data >= 0 and data < len(self.ARRAY_POWER):
                return self.ARRAY_POWER[data];
            else:
                return "22dBm";
        elif what == self.WAKE_ON_RADIO_TIME:
            if data >= 0 and data < len(self.ARRAY_WAKE_ON_RADIO_TIME):
                return self.ARRAY_WAKE_ON_RADIO_TIME[data];

    def consume( self, what , data ):
        if what == self.ADDRESS:
            self._conf[self.ADDRESS] = data[0]<<8 | data[1];
        elif what == self.NOISE:
            self._conf[self.NOISE] = "-{} dBm".format( 256 - data[0] );
        elif what == self.REG0:
            self._conf[self.REG0][self.SERIAL_BAUD] = self.forHuman(self.SERIAL_BAUD,(data[0]>>5)&0b111);
            self._conf[self.REG0][self.SERIAL_PARITY] = self.forHuman(self.SERIAL_PARITY, (data[0]>>3)&0b11);
            self._conf[self.REG0][self.AIR_BAUD] = self.forHuman(self.AIR_BAUD,data[0]&0b111);
        elif what == self.REG1:
            self._conf[self.REG1][self.SUB_PACKET] = self.forHuman(self.SUB_PACKET,(data[0]>>6)&0b11);
            self._conf[self.REG1][self.RSSI_NOISE_DETECT] = (data[0]>>5)&0b1;
            self._conf[self.REG1][self.POWER] = self.forHuman(self.POWER,data[0]&0b11);
        elif what == self.CHANNEL:
            self._conf[self.CHANNEL] = data[0] + 1;
        elif what == self.REG3:
            self._conf[self.REG3][self.RSSI_BYTE] = (data[0]>>7)&0b1;
            self._conf[self.REG3][self.FIXED_TRANSMISSION] = (data[0]>>6)&0b1;
            self._conf[self.REG3][self.LISTEN_BEFORE_TALK] = (data[0]>>4)&0b1;
            self._conf[self.REG3][self.WAKE_ON_RADIO_TIME] = self.forHuman(self.WAKE_ON_RADIO_TIME,data[0]&0b111);
        elif what == None:
            if len(data) >= 6:
                self._conf |= self.consume(self.ADDRESS, data[0:2]);
                self._conf |= self.consume(self.REG0, data[2:]);
                self._conf |= self.consume(self.REG1, data[3:]);
                self._conf |= self.consume(self.CHANNEL, data[4:]);
                self._conf |= self.consume(self.REG3, data[5:]);
        return self._conf if what == None else {  what : self._conf[ what ] };

def initComms():
    global port;
    ports = serial.tools.list_ports.comports();
    for i in range(0,len(ports)):
        print("\t[{}] - {} {}".format( i+1,ports[i].device,ports[i].description));
    selection = -1;
    while selection < 0 or selection > len(ports):
        try:
            selection = int(input("select a port: "));
        except:
            print("invalid selection");
    port = serial.Serial( ports[ selection - 1 ].device, DEFAULT_BAUD, timeout=0.5,xonxoff=False,dsrdtr=False,rtscts=False);
    return port.is_open;

def printHeader():
    s = "\n[L]isten   [S]end  se[T]tings";
    if e220 and e220._conf[e220.REG1][e220.RSSI_NOISE_DETECT] == 1:
        s += " [N]oise"
    print(s);

STATE_LISTEN = "l";
STATE_SEND = "s";
STATE_SETTINGS = "t";
STATE_HOME = "h";
_state = STATE_HOME;

e220 = None;

def work(  ):
    global _state, e220;
    if initComms():
        e220 = E220400();
        printHeader();
        try:
            while True:
                if _state == STATE_HOME:
                    v = input();
                    if v in [ STATE_LISTEN,STATE_SEND,STATE_SETTINGS]:
                        _state = v;
                    elif v == "n":
                        d = bytes([0xC0,0xC1,0xC2,0xC3,0x00,0x01]);
                        port.write(d);
                        port.flush();
                        rsp = port.read(200);
                        if len(rsp) == 4:
                            print( e220.consume(e220.NOISE,rsp[3:]));

                if _state == STATE_LISTEN:
                    try:
                        while True:
                            rsp = port.read(200);
                            if len(rsp) > 0:
                                print("\t<<--",rsp.hex(),", ",rsp.decode("utf-8",errors="ignore") );
                            #time.sleep(0.2);
                    except KeyboardInterrupt:
                        print("- STOPPED LISTENING - ");
                        _state = STATE_HOME;
                        printHeader();
                    except:
                        traceback.print_exc();
                elif _state == STATE_SEND:
                    try:
                        a = int(input("Input address: "),0);
                        c = int(input("Input Channel:"));
                        d = input("Input data to send, (prefix 0x for bytes)");
                        data = bytearray([(a>>8)&0xFF,a&0xFF,c - 1]);
                        data += d.encode();
                        port.write( data );
                        port.flush();
                        print("\t-->>", data.hex(),", ",d );
                        rsp = port.read(200);
                        if rsp:
                            print("\t<<--",rsp.hex(),", ",rsp.decode("utf-8",errors="ignore") );
                    except KeyboardInterrupt:
                        print("- STOPPED LISTENING - ");
                        _state = STATE_HOME;
                        printHeader();
                    except:
                        pass;
                        traceback.print_exc();
                elif _state == STATE_SETTINGS:
                    print("""
    [ 01 ] - Address
    [ 02 ] - REG 0
    [ 03 ] - REG 1
    [ 04 ] - Channel
    [ 05 ] - REG 3
    [ 06 ] - CRYPT BYTES
    [ 07 ] - READ ALL Settings
                          """);
                    v = -1;
                    while v < 1 or v > 8:
                        try:
                            v = input("Make a Section: ")
                            v = int(v);
                        except KeyboardInterrupt:
                            printHeader();
                            _state = STATE_HOME;
                            break;
                        except:
                            v = -1;
                            pass;
                    if v == 1:
                        r_w = input("[R]ead/[W]rite(R):");
                        if r_w == "w":
                            try:
                                addr = int(input("Input an address(e.g. 1234):"),0);
                                addrH = (addr>>8)&0xFF;
                                addrL = addr&0xFF;
                                d = bytes([0xC0,0x00,0x02,addrH,addrL]);
                                port.write(d);
                                port.flush();
                                rsp = port.read(200);
                                print("<<--",rsp.hex());
                                if len(rsp) == 5:
                                    print( e220.consume(e220.ADDRESS,rsp[3:]));
                            except:
                                traceback.print_exc();
                                print("Err");
                        else:
                            d = bytes([0xC1,0x00,0x02]);
                            port.write(d);
                            port.flush();
                            rsp = port.read(200);
                            print("<<--",rsp.hex());
                            if len(rsp) == 5:
                                print( e220.consume(e220.ADDRESS,rsp[3:]));

                    elif v == 2:
                        r_w = input("[R]ead/[W]rite(R):");
                        if r_w == "w":
                            try:
                                d = bytes([0xC1,0x02,0x01]);
                                port.write(d);
                                port.flush();
                                rsp = port.read(200);
                                serialBaudBits = 0;
                                serialParityBits = 0;
                                airBuadBits = 0;
                                if len(rsp) == 4:
                                    d = e220.consume(e220.REG0,rsp[3:])[ e220.REG0 ];
                                    serialBaudBits = e220.forMachine(e220.SERIAL_BAUD,d[e220.SERIAL_BAUD]);
                                    serialParityBits = e220.forMachine(e220.SERIAL_PARITY,d[e220.SERIAL_PARITY]);
                                    airBuadBits = e220.forMachine(e220.AIR_BAUD,d[e220.AIR_BAUD]);
                                    print("""
    [ 01 ] - UART Serial baud rate
    [ 02 ] - Serial Parity Bit
    [ 03 ] - Air Data Rate
                                      """);
                                    v = input("Input a selection");
                                    if v == "1":
                                        for i in range(0,len(e220.ARRAY_BAUD)):
                                            print("\t[{}] - {}".format(i+1,e220.ARRAY_BAUD[i]))
                                        v1 = int(input("Input a selection:"));
                                        if (v1 >= 1 and v1 <= 8 ):
                                            serialBaudBits = v1 - 1;
                                            b = serialBaudBits<<5 | serialParityBits<<4 | airBuadBits;
                                            d = bytes([0xC0,0x02,0x01, b]);
                                            port.write(d);
                                            rsp = port.read(200);
                                            if len(rsp) == 4:
                                                print( e220.consume(e220.REG0,rsp[3:]));
                                    elif v == "2":
                                        for i in range(0,len(e220.ARRAY_PARITY)):
                                            print("\t[{}] - {}".format(i+1,e220.ARRAY_PARITY[i]))
                                        v1 = int(input("Input a selection:"));
                                        if (v1 >= 1 and v1 <= 8 ):
                                            serialParityBits = v1 - 1;
                                            b = serialBaudBits<<5 | serialParityBits<<3 | airBuadBits;
                                            d = bytes([0xC0,0x02,0x01, b]);
                                            port.write(d);
                                            rsp = port.read(200);
                                            if len(rsp) == 4:
                                                print( e220.consume(e220.REG0,rsp[3:]));
                                    elif v == "3":
                                        #serial 1200, 8N1
                                        for i in range(0,len(e220.ARRAY_AIR_BAUD)):
                                            print("\t[{}] - {}".format(i+1,e220.ARRAY_AIR_BAUD[i]))
                                        v1 = int(input("Input a selection:"));
                                        if (v1 >= 1 and v1 <= 8 ):
                                            airBuadBits = v1 - 1;
                                            b = serialBaudBits<<5 | serialParityBits<<3 | airBuadBits;
                                            #print( bin( b  ) );
                                            d = bytes([0xC0,0x02,0x01, b]);
                                            port.write(d);
                                            rsp = port.read(200);
                                            if len(rsp) == 4:
                                                print( e220.consume(e220.REG0,rsp[3:]));
                            except:
                                traceback.print_exc();
                                print("Err");
                        else:
                            d = bytes([0xC1,0x02,0x01]);
                            port.write(d);
                            rsp = port.read(200);
                            if len(rsp) == 4:
                                print( e220.consume(e220.REG0,rsp[3:]));
                    elif v == 3:
                        r_w = input("[R]ead/[W]rite(R):");
                        if r_w == "w":
                            try:
                                d = bytes([0xC1,0x03,0x01]);
                                port.write(d);
                                rsp = port.read(200);
                                subPacketBits = 0;
                                rssiNoiseBit = 0;
                                powerBits = 0;
                                if len(rsp) == 4:
                                    d = e220.consume(e220.REG1,rsp[3:])[e220.REG1];
                                    print( d );
                                    subPacketBits = e220.forMachine(e220.SUB_PACKET,d[e220.SUB_PACKET]);
                                    rssiNoiseBit = d[e220.RSSI_NOISE_DETECT];
                                    powerBits = e220.forMachine(e220.POWER,d[e220.POWER]);

                                    print( subPacketBits )
                                    print( rssiNoiseBit )
                                    print( powerBits )

                                    print("""
    [ 01 ] - Sub-Packet
    [ 02 ] - RSSI noise bit
    [ 03 ] - Power
                                      """);
                                    v = input("Input a selection");
                                    if v == "1":
                                        for i in range(0,len(e220.ARRAY_SUB_PACKET)):
                                            print("\t[{}] - {}".format(i+1,e220.ARRAY_SUB_PACKET[i]))
                                        v1 = int(input("Input a selection:"));
                                        if v1 >= 1 and v1 <= len(e220.ARRAY_SUB_PACKET):
                                            subPacketBits = v1 - 1;
                                            b = (subPacketBits<<6) | rssiNoiseBit<<5 | powerBits;
                                            print( bin(b  ));
                                            d = bytes([0xC0,0x03,0x01, b]);
                                            port.write(d);
                                            rsp = port.read(200);
                                            if len(rsp) == 4:
                                                print( e220.consume(e220.REG1,rsp[3:]));
                                    elif v == "2":
                                        v1 = input("[Y]es/[N]o (no):");
                                        rssiNoiseBit = 1 if v1 == "y" else 0;
                                        b = (subPacketBits<<7) | rssiNoiseBit<<5 | powerBits;
                                        d = bytes([0xC0,0x03,0x01, b]);
                                        port.write(d);
                                        rsp = port.read(200);
                                        if len(rsp) == 4:
                                            print( e220.consume(e220.REG1,rsp[3:]));
                                    elif v == "3":
                                        for i in range(0,len(e220.ARRAY_POWER)):
                                            print("\t[{}] - {}".format(i+1,e220.ARRAY_POWER[i]))
                                        v1 = int(input("Input a selection:"));
                                        if (v1 >= 1 and v1 <= len(e220.ARRAY_POWER) ):
                                            powerBits = v1 - 1;
                                            b = (subPacketBits<<6) | rssiNoiseBit<<5 | powerBits;
                                            d = bytes([0xC0,0x03,0x01, b]);
                                            port.write(d);
                                            rsp = port.read(200);
                                            if len(rsp) == 4:
                                                print( e220.consume(e220.REG1,rsp[3:]));
                            except:
                                traceback.print_exc();
                                print("Err");
                        else:
                            d = bytes([0xC1,0x03,0x01]);
                            port.write(d);
                            rsp = port.read(200);
                            if len(rsp) == 4:
                                print( e220.consume(e220.REG1,rsp[3:])[e220.REG1]);
                    elif v == 4:
                        r_w = input("[R]ead/[W]rite(R):");
                        if r_w == "w":
                            try:
                                channel = int(input("Input a channel (1-84):"));
                                if ( channel >=1 and channel <= 84 ):
                                    channel -= 1;
                                    d = bytes([0xC0,0x04,0x01,channel]);
                                    port.write(d);
                                    rsp = port.read(200);
                                    if len(rsp) == 4:
                                        print( e220.consume(e220.CHANNEL,rsp[3:]));
                                else:
                                    print("invalid channel");
                            except:
                                traceback.print_exc();
                                print("Err");
                        else:
                            d = bytes([0xC1,0x04,0x01]);
                            port.write(d);
                            rsp = port.read(200);
                            if len(rsp) == 4:
                                print( e220.consume(e220.CHANNEL,rsp[3:]));
                    elif v == 5:
                        r_w = input("[R]ead/[W]rite(R):");
                        if r_w == "w":
                            try:
                                d = bytes([0xC1,0x05,0x01]);
                                port.write(d);
                                rsp = port.read(200);
                                worBits = 0;
                                lbtBit = 0;
                                rssiByteBit = 0;
                                methodBit = 0;
                                if len(rsp) == 4:
                                    d = e220.consume(e220.REG3,rsp[3:])[e220.REG3];
                                    print( d );
                                    worBits = e220.forMachine(e220.WAKE_ON_RADIO_TIME,d[e220.WAKE_ON_RADIO_TIME]);
                                    lbtBit = d[e220.LISTEN_BEFORE_TALK];
                                    rssiByte = d[e220.RSSI_BYTE];
                                    methodBit = d[e220.FIXED_TRANSMISSION]
                                    print("""
    [ 01 ] - Wake on Radio
    [ 02 ] - Listen Before Talk
    [ 03 ] - RSSI byte
    [ 04 ] - Fixed Transmission
                                      """);
                                    v = input("Input a selection");
                                    if v == "1":
                                        for i in range(0,len(e220.ARRAY_WAKE_ON_RADIO_TIME)):
                                            print("\t[{}] - {}".format(i+1,e220.ARRAY_WAKE_ON_RADIO_TIME[i]))
                                        v1 = int(input("Input a selection:"));
                                        if (v1 >= 1 and v1 <= len(e220.ARRAY_WAKE_ON_RADIO_TIME) ):
                                            worBits = v1 - 1;
                                            b = rssiByte<<7| (methodBit<<6) | lbtBit<<4 | worBits;
                                            d = bytes([0xC0,0x05,0x01, b]);
                                            port.write(d);
                                            rsp = port.read(200);
                                            if len(rsp) == 4:
                                                print( e220.consume(e220.REG3,rsp[3:])[e220.REG3]);
                                    elif v == "2":
                                        v1 = input("[Y]es/[N]o (no):");
                                        listenBeforeTalk = 1 if v1 == "y" else 0;
                                        b = rssiByte<<7| (methodBit<<6) | lbtBit<<4 | worBits;
                                        d = bytes([0xC0,0x05,0x01, b]);
                                        port.write(d);
                                        rsp = port.read(200);
                                        if len(rsp) == 4:
                                            print( e220.consume(e220.REG3,rsp[3:])[e220.REG3]);
                                    elif v == "3":
                                        v1 = input("[Y]es/[N]o (no):");
                                        rssiByte = 1 if v1 == "y" else 0;
                                        b = rssiByte<<7| (methodBit<<6) | lbtBit<<4 | worBits;
                                        d = bytes([0xC0,0x05,0x01, b]);
                                        port.write(d);
                                        rsp = port.read(200);
                                        if len(rsp) == 4:
                                            print( e220.consume(e220.REG3,rsp[3:])[e220.REG3]);
                                    elif v == "4":
                                        v1 = input("[Y]es/[N]o (no):");
                                        methodBit = 1 if v1 == "y" else 0;
                                        b = rssiByte<<7| (methodBit<<6) | lbtBit<<4 | worBits;
                                        d = bytes([0xC0,0x05,0x01, b]);
                                        port.write(d);
                                        rsp = port.read(200);
                                        if len(rsp) == 4:
                                            print( e220.consume(e220.REG3,rsp[3:])[e220.REG3]);
                            except:
                                traceback.print_exc();
                                print("Err");
                        else:
                            d = bytes([0xC1,0x03,0x01]);
                            port.write(d);
                            rsp = port.read(200);
                            if len(rsp) == 4:
                                print( e220.consume(e220.REG3,rsp[3:])[e220.REG3]);
                    elif v == 6:
                        try:
                            encry = int(input("Input an encryption value (e.g. 563765):"));
                            eH = (encry>>8)&0xFF;
                            eL = encry&0xFF;
                            d = bytes([0xC0,0x06,0x02,eH,eL]);
                            port.write(d);
                            print("-Written-");
                        except:
                            traceback.print_exc();
                            print("Err");
                    elif v == 7:
                        d = bytes([0xC1,0x00,0x06]);
                        port.write(d);
                        rsp = port.read(200);
                        if len(rsp) > 4:
                            print( e220.consume(None,rsp[3:]));
        except:
            traceback.print_exc();
            print("err")

def help( name ):
    pass

if __name__ == '__main__':
    work();
