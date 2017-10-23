import struct
import binascii

class Affichage:
    def dumpAscii(data):
        ligne=""
        dtlen=len(data)
        for i in range(dtlen):
            bts = struct.unpack("<c", data[i:i+1])[0]
            if ord(bts) > 32 and ord(bts) < 127 :
                ligne+=chr(ord(bts))
            else:
                ligne+='.'
            if (i+1)%16==0:
                ligne+='\n'
        return ligne

    def dumpHex(data):
        ligne=""
        for i in range(len(data)):
           chunk=struct.unpack("<c", data[i:i+1])[0]
           ligne+=binascii.hexlify(chunk).decode("utf-8")
           if (i+1)%16==0:
            ligne+='\n'
        return ligne