#!/usr/bin/env python3
import traceback
import math
from termcolor import colored

def blue( s ):
    return colored( s , "cyan" );

if __name__ == '__main__':
    try:
        #wire_dia = 1.3
        #frequency = 433
        #coil_dia = 1.65 / 100;
        #turns_per_m = 60
        wire_dia = float(input(blue("> What is the diameter of the wire (mm)?")))
        turns_per_m = float(input(blue("> How many tight turns per 10cm ?"))) * 10
        frequency = float(input(blue("> What is the opperating frequency (MHz)?")))
        coil_dia = float(input(blue("> What is the diameter of the coil (cm)"))) / 100;

        def getInductance( diameter, length, turns ):
            TO_INCH = 39.37008
            diameter *= TO_INCH
            length *= TO_INCH
            return ( pow(diameter,2) * pow(turns,2 ) ) / ( 18*diameter + 40*length )

        # Equations use length of dipole
        def calculateLoading( totalDipoleLen, distFromBase, diameter, frequency ):
            """
            1 foor = 0.3048m
            1 inch = 25.4mm
            """

            f1 = 1e6 / ( 68 * (math.pi*math.pi) * frequency*frequency );

            f2 = math.log( 24 * ( (234 / frequency) - ( distFromBase/0.3048 )) / (diameter/25.4)) - 1;
            f3 = math.pow( 1 - ( ( frequency * (distFromBase/0.3048) / 234 ) ) , 2 ) - 1;
            f4 = ( 234 / frequency ) - ( distFromBase / 0.3048 );
            f5 = math.log( 24 * ( ( ( totalDipoleLen / 0.3048 ) / 2 ) - ( distFromBase / 0.3048 ) ) / ( diameter /25.4 ) ) - 1;
            f6 = math.pow( ( ( ( frequency * ( totalDipoleLen / 0.3048 ) / 2 )  - ( frequency * ( distFromBase / 0.3048 ) ) ) / 234 ) , 2 ) - 1;
            f7 = ( totalDipoleLen / 0.3048 ) / 2 - ( distFromBase / 0.3048 )
            lmh = f1 * ((f2 * f3 / f4) - (f5 * f6 / f7))
            print(colored("calculateLoading(\n\tlength: {}(m)\n\tFrom Base: {}(m)\n\tDiameter: {}(mm)\n\tfrequency: {}(MHz) ) => inductance: {:6.4f}".format(totalDipoleLen,distFromBase,diameter,frequency,lmh),"yellow"));
            return lmh

        def waveLength( f ): # in Hz
            return 299792458 / f; # in m

        #length = 10 / 100;
        #pos = 1 / 100;
        length = float(input(blue("> What is the desired length of the 1/4 wave antenna? ( < {:5.3f} cm )".format( waveLength( frequency*1000000 )*100 / 4 )))) / 100;
        pos = float(input(blue("> What is the disance of the coil from the base? (cm)"))) / 100;

        if (pos<0):
            pos=0
        if (pos>0.9*length):
           pos=0.9*length

        uH = calculateLoading( length*2, pos, wire_dia, frequency );

        for i in range(50000):
            _l = 0 +(i/1000);
            j = getInductance( coil_dia , _l, _l * turns_per_m );
            if j > 0 and j > ( uH ):
                if _l > length:
                    print(colored("ERROR: calculated: {:6.4f}uH\n\tcoil length: {:5.4f}m".format( j , _l ),"red"));
                else:
                    print(colored("calculated: {:6.4f}uH\n\tcoil length: {:5.4f}m".format( j , _l ),"green"));
                break;

    except:
        traceback.print_exc();


