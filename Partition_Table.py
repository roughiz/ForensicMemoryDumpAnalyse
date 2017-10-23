import struct
import binascii
from affichage import Affichage


class Fat32:
    def __init__(self, partitionEntry,firstDiskOffset,file):
        self.partitionEntry = partitionEntry

        self.offsetdebutPartition = PartitionTable.firstOffsetOfAPartition(partitionEntry.Start_chs_C,partitionEntry.Start_chs_H,partitionEntry.Start_chs_S,firstDiskOffset)
        #print (file.tell(),self.offsetdebutPartition)

        # self.test=file.read(63*512)
        sctornumbers = PartitionTable.findPartitSector(file)
        cc=sctornumbers //16128
        rcc=sctornumbers %16128
        hh=rcc//63
        rhh=rcc%63
        print (sctornumbers)
        print(cc-1,hh-1,rhh)

        #file.seek(self.offsetdebutPartition)
        self.data_Bs_Fat = file.read(63*512)
        # 32 s pour le boot et 31 pour le fat, divisé ainsi
         # 3 s reserver au boot, 3 s vide, 3 s copie du secteur boot, 23 réservé à l'os svt remplis de 00
        #
        self.boot= self.data_Bs_Fat[:3*512] #3 secteurs
        self.secempty = self.data_Bs_Fat[3*512:6*512] #3 secteurs
        self.bootCopy = self.data_Bs_Fat[6*512:9*512]  # 3 secteurs
        self.osSector = self.data_Bs_Fat[9*512:32*512]  # 23 secteurs
        self.fat = self.data_Bs_Fat[32*512:]#31 restant



class PartitionTable:
    def __init__(self,mbrReader):
        self.mbr= mbrReader
        self.partitsLIst={}
        for i in range(4):
            if self.mbr.partEntrys[i].PartitionType == b'\x0b': # si c'est un fat32
                self.partitsLIst[i]=Fat32(self.mbr.partEntrys[i],self.mbr.offsetFirstSector,self.mbr.file)
                print(Affichage.dumpHex(self.partitsLIst[i].boot))
                print()
                print(Affichage.dumpAscii(self.partitsLIst[i].boot))


    def findPartitSector(file):
        i=1
        j=0
        res={}
        place=""
        for chunk in iter(lambda:file.read(2), b''):
            res[i]=binascii.hexlify(chunk).decode("utf-8")
            if '55aa' == res[i] and i >= 256 and res[i-255]=="eb58" and res[i-254]=="904d":
                file.seek(file.tell() - 512)
                return  (i*2)/512
            i+=1


    def firstOffsetOfAPartition(cylindre,head,sector,firstDiskOffset):
        return firstDiskOffset + (((cylindre*256*63)+(head*63)+sector-1)*512)
