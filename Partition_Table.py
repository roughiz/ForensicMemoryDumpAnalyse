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

        self.data_Bs_Fat = file.read(63*512)
        # 32 s pour le boot et 31 pour le fat, divisé ainsi
        # 3 s reserver au boot, 3 s vide, 3 s copie du secteur boot, 23 réservé à l'os svt remplis de 00
        #
        self.boot= self.data_Bs_Fat[:3*512] #3 secteurs
        self.boot_sec1= self.boot[:512]
        self.boot_sec2= self.boot[512:1024]
        self.boot_sec3 = self.boot[1024:1536]
        ######################################## Analyse du boot sector 1 ######################
        self.system_fichier = struct.unpack(b'8s', self.boot_sec1[3:11])[0]
        self.bytes_per_sector=struct.unpack("<h", self.boot_sec1[11:13])[0]
        self.sectors_by_cluster = struct.unpack("<B", self.boot_sec1[13:14])[0]
        self.reserved_sector = struct.unpack("<h", self.boot_sec1[14:16])[0]
        self.number_of_fat_copis = struct.unpack("<B", self.boot_sec1[16:17])[0]
        self.number_of_root_directory_entry = struct.unpack("<h", self.boot_sec1[17:19])[0] # tjr a 0 pourles partit fat32
        self.total_sectors_by_filesystem = struct.unpack("<h", self.boot_sec1[19:21])[0] # tjr a 0 pourles partit fat32
        self.type_media = struct.unpack("<c", self.boot_sec1[21:22])[0] #f8: hard disk, f0 floppy
        self.fileSystem_version = struct.unpack("<h", self.boot_sec1[42:44])[0]
        self.extended_signature = struct.unpack("<c", self.boot_sec1[66:67])[0] # 29 en hexa
        self.serial_numberOfPartit = struct.unpack("<l", self.boot_sec1[67:71])[0] # numéro de serie du device
        self.volume_label = struct.unpack(b'11s', self.boot_sec1[71:82])[0] # le nom du device crée lors du formatage
        self.fileSystem_type = struct.unpack(b'8s', self.boot_sec1[82:90])[0] # type de file system ici FAT32
        ######################################## Analyse du boot sector 2 ############################
        self.fileSystemInfo = struct.unpack(b'4s', self.boot_sec2[0:4])[0]
        self.nbrOctetsLibre = struct.unpack("<l", self.boot_sec1[488:492])[0]
        self.marqueRra = struct.unpack(b'4s', self.boot_sec2[484:488])[0]
        self.premier_cluster_disponible =struct.unpack("<l", self.boot_sec1[492:496])[0]




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
                curentP= self.partitsLIst[i]
                print(Affichage.dumpHex(curentP.boot_sec1))
                print()
                print(Affichage.dumpAscii(curentP.boot_sec1))
                print(curentP.bytes_per_sector)
                print(curentP.sectors_by_cluster)
                print(curentP.reserved_sector)
                print(curentP.number_of_fat_copis)
                print(curentP.type_media)
                print(curentP.number_of_root_directory_entry)
                print (curentP.total_sectors_by_filesystem)
                print(Affichage.dumpAscii(curentP.system_fichier))
                print(curentP.fileSystem_version)
                print(Affichage.dumpHex(curentP.extended_signature))
                print (curentP.serial_numberOfPartit)
                print (Affichage.dumpAscii(curentP.volume_label))
                print (Affichage.dumpAscii(curentP.fileSystem_type))
                print()
                print(Affichage.dumpAscii(curentP.fileSystemInfo))
                print (Affichage.dumpAscii(curentP.marqueRra))
                print(curentP.nbrOctetsLibre)
                print (curentP.premier_cluster_disponible)

                #print("copy")
                #print(Affichage.dumpHex(self.partitsLIst[i].bootCopy))
                #print()
                #print(Affichage.dumpAscii(self.partitsLIst[i].bootCopy))


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
