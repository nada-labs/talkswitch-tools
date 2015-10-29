#!/usr/bin/env python
#
# Dumps files from a FFS flash filesystem image
#
# Reverse engineering of the format documented at
# http://nada-labs.net/2015/

from struct import unpack

class FFSFileEntry:
    Parent = None
    Mode = None
    Timestamp = None
    User = None
    Group = None
    Name = None
    Length = None
    A = None
    Unk1 = None
    Unk2 = None
    Offset = None

    MODE_DIRECTORY = 0x200  #flag indicating a directory

    def __init__(self, f):
        header = f.read(23) #read in the header data
        self.Parent, self.Mode, self.Timestamp, self.User, self.Group, namelen, self.Length, self.Unk1, self.Unk2 = unpack('<HHLBBBLLL', header)
        self.Name = f.read(namelen)
        self.A = self.Length >> 24
        self.Length = self.Length & 0xFFFFFF

        self.Offset = f.tell()  #record the current file pointer
        f.seek(self.Length, 1)  #skip the file contents

    def info(self):
        print("%04X %i:%i %3i %3i %08X %08X %08X %8i %s" % \
                (self.Mode, self.User, self.Group, self.A, self.Parent, \
                self.Timestamp, self.Unk1, self.Unk2, self.Length, \
                self.Name))

class FFS:
    Files = None
    Length = None
    Signature = 0x00534646

    def __init__(self, filename):
        self.f = open(filename, 'rb')
        header = self.f.read(8)
        sig, self.Length = unpack("<LL", header)

        if sig != FFS.Signature:
            raise ValueError("Invalid signature in FFS file")

        self.Files = {}
        while self.f.tell() < self.Length:
            fe = FFSFileEntry(self.f)
            if fe.Mode != 0xFFFF:
                self.Files[fe.Name] = fe
            else:
                break

    def dump(self, filename):
        if self.Files.has_key(filename):
            fileentry = self.Files[filename]
            self.f.seek(fileentry.Offset)

            wSize = 0
            fo = open(filename, 'wb')
            while wSize < fileentry.Length:
                rSize = min(fileentry.Length - wSize, 8192)
                data = self.f.read(rSize)
                fo.write(data)
                wSize += len(data)
            fo.close()
        else:
            raise ValueError("Invalid filename")

    def ls(self):
        print("Mode U:G A   P   Date     Unk1     Unk2     Size     Filename")
        for v in self.Files.values():
            v.info()

if __name__ == '__main__':
    from sys import argv

    if len(argv) != 2:
        print("usage: %s ffs.img")

    ffs = FFS(argv[1])
    ffs.ls()
    for fe in ffs.Files.values():
        if fe.Mode & fe.MODE_DIRECTORY == 0:    #not a directory
            ffs.dump(fe.Name)
            print("Dumped %s" % (fe.Name))
