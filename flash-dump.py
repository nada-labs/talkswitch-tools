#!/usr/bin/env python

from serial import Serial
from sys import stdout
import re

def dump_mem(ser, ffile, fbase, fsize):
    ser.write("dm 0x%08X\n" % fbase)
    
    while fsize > 0:
        for l in ser.readlines():
            parts = l.split(' ')
            if len(parts) >= 7:
                #actually a hexdump line, write the data
                data = (parts[1] + parts[2] + parts[3] + parts[4]).decode('hex')
                ffile.write(data)
                fsize -= len(data)

                stdout.write('.')
                stdout.flush()

        if fsize > 0:
            ser.write("dm\n")

    stdout.write("\n")

if __name__ == '__main__':
    from sys import argv,exit

    if len(argv) != 5:
        print("usage: %s serial_device filename address size" % (argv[0]))
        print("\te.g.: %s /dev/ttyUSB0 flash.img 0xB0000000 0x00800000" % (argv[0]))
        exit(0)

    ffile = open(argv[2], 'wb')
    fbase = int(argv[3], base=0)
    fsize = int(argv[4], base=0)
    ser = Serial(argv[1], 115200, timeout=1)

    print("Dumping 0x%08X (%i) bytes of memory at 0x%08X" % (fsize, fsize, fbase))

    dump_mem(ser, ffile, fbase, fsize)
    ffile.close()
