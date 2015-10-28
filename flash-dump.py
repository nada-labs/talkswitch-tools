#!/usr/bin/env python

from serial import Serial
from sys import stdout
import re

spinny = ['-', '\\', '|', '/']

def dump_mem(ser, ffile, fbase, fsize):
    spinny_idx = 0
    count = 0

    while count < fsize:
        ser.write("dm 0x%08X 0xFF\n" % (fbase+count)) #read 256 byte blocks
        for l in ser.readlines():
            parts = l.split(' ')
            if len(parts) >= 7:
                #actually a hexdump line, write the data
                data = (parts[1] + parts[2] + parts[3] + parts[4]).decode('hex')
                addr = int(parts[0][:10], base=16)
                if addr != (fbase+count):
                    print("Out of sync: got data for address 0x%08X, expecting 0x%08X" % (addr, fbase+count))
                    return
                ffile.write(data)
                count += len(data)

        stdout.write('\r[%s] Reading flash: %i bytes transferred (%3.1f%%)' % (spinny[spinny_idx], count, (100.0*float(count)/float(fsize))))
        stdout.flush()
        spinny_idx = ((spinny_idx + 1) % 4)

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
    ser = Serial(argv[1], 115200, timeout=0.005)

    print("Dumping 0x%08X (%i) bytes of memory at 0x%08X" % (fsize, fsize, fbase))

    dump_mem(ser, ffile, fbase, fsize)
    ffile.close()
