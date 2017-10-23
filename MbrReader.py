import struct
import binascii
from Partition_Table import PartitionTable
from affichage import Affichage



PartitionTypes = {
   '00': "Empty",
   '01': "FAT12,CHS",
   '04': "FAT16 16-32MB,CHS",
   '05': "Microsoft Extended",
   '06': "FAT16 32MB,CHS",
   '07': "NTFS",
   '0b': "FAT32,CHS",
   '0c': "FAT32,LBA",
   '0e': "FAT16, 32MB-2GB,LBA",
   '0f': "Microsoft Extended, LBA",
   '11': "Hidden FAT12,CHS",
   '14': "Hidden FAT16,16-32MB,CHS",
   '16': "Hidden FAT16,32MB-2GB,CHS",
   '18': "AST SmartSleep Partition",
   '1b': "Hidden FAT32,CHS",
   '1c': "Hidden FAT32,LBA",
   '1e': "Hidden FAT16,32MB-2GB,LBA",
   '27': "PQservice",
   '39': "Plan 9 partition",
   '3c': "PartitionMagic recovery partition",
   '42': "Microsoft MBR,Dynamic Disk",
   '44': "GoBack partition",
   '51': "Novell",
   '52': "CP/M",
   '63': "Unix System V",
   '64': "PC-ARMOUR protected partition",
   '82': "Solaris x86 or Linux Swap",
   '83': "Linux",
   '84': "Hibernation",
   '85': "Linux Extended",
   '86': "NTFS Volume Set",
   '87': "NTFS Volume Set",
   '9f': "BSD/OS",
   'a0': "Hibernation",
   'a1': "Hibernation",
   'a5': "FreeBSD",
   'a6': "OpenBSD",
   'a8': "Mac OSX",
   'a9': "NetBSD",
   'ab': "Mac OSX Boot",
   'af': "MacOS X HFS",
   'b7': "BSDI",
   'b8': "BSDI Swap",
   'bb': "Boot Wizard hidden",
   'be': "Solaris 8 boot partition",
   'd8': "CP/M-86",
   'de': "Dell PowerEdge Server utilities (FAT fs)",
   'df': "DG/UX virtual disk manager partition",
   'eb': "BeOS BFS",
    "ee": "EFI GPT Disk",
    "ef":"EFI System Parition",
    "fb":  "VMWare File System",
    "fc": "VMWare Swap",
}


class PartitionEntry:
    def __init__(self, data,part_number):
        self.BootableFlag = struct.unpack("<c", data[:1])[0]
        self.Start_chs_H = struct.unpack("<B", data[1:2])[0]
        self.Start_chs_S = struct.unpack("<B", data[2:3])[0]
        self.Start_chs_C = struct.unpack("<B", data[3:4])[0]
        self.PartitionType = struct.unpack("<c", data[4:5])[0]
        self.End_chs_H = struct.unpack("<B", data[5:6])[0]
        self.End_chs_S = struct.unpack("<B", data[6:7])[0]
        self.End_chs_C = struct.unpack("<B", data[7:8])[0]
        self.StartLBA = struct.unpack("<I", data[8:12])[0]
        self.SectorsSizes = struct.unpack("<i", data[12:16])[0]
        self.part_number = part_number

    def get_Part_Type(self,PartitionType):
        return PartitionTypes.get(binascii.hexlify(PartitionType).decode("utf-8"))

    def affichage(self):
        print()
        print ("------------------Table de partitition "+str(self.part_number)+"------------------")
        if self.BootableFlag == b'\x80':
            print ("Partition Bootable")
        else:
            print ("Partition Non Bootable")
        print ("Adresse CHS du premier secteur : "+str(self.Start_chs_C),str(self.Start_chs_H),str(self.Start_chs_S))
        print ("Adresse CHS du dernier secteur : " + str(self.End_chs_C),str(self.End_chs_H),str(self.End_chs_S))
        print ("Type de partition : "+self.get_Part_Type(self.PartitionType))
        print ("Adresse du premier secteur logique(LBA) : "+str(self.StartLBA))
        print ("Nombre de secteurs dans la partition : "+str(self.SectorsSizes))
        taille=(self.SectorsSizes*512)//(1024**3)
        rd = (self.SectorsSizes*512)%(1024**3)
        if rd >=0.50:
            taille+=1
        print ("Taille de la partition en GB: "+str(taille))

class MBRParser:
    def __init__(self, file):
        isMbr, data,offset =self.findMbr(file)
        if isMbr:
            self.file=file
            self.offsetFirstSector=offset # Cylindre commence a 0, Head aussi, mais Sector à 1  !!!
            self.data=data
            self.BootCode = self.data[:440]
            self.signature= self.data[440:444]
            self.TablePartit = self.data[446:510]
            self.MagiqueNumber = self.data[510:512]
            self.isMbr=True
            self.partEntry1 = PartitionEntry(self.TablePartit[:16],1)
            self.partEntry2 = PartitionEntry(self.TablePartit[16:32],2)
            self.partEntry3 = PartitionEntry(self.TablePartit[32:48],3)
            self.partEntry4 = PartitionEntry(self.TablePartit[48:64],4)
            self.partEntrys={}
            self.partEntrys[0] = self.partEntry1
            self.partEntrys[1] = self.partEntry2
            self.partEntrys[2] = self.partEntry3
            self.partEntrys[3] = self.partEntry4
        else:
            self.isMbr=False

    def affichage(self):
        print ("------------------ Analyse du Master Boot Record (MBR) ------------------")
        print ("Affichag Hexa du Boot code:")
        print(Affichage.dumpAscii(self.BootCode))
        print()
        print ("La signature du disque : "+Affichage.dumpHex(self.signature))
        for i in range(4):
            self.partEntrys[i].affichage()
        print()
        print ("Vérification de la signature MBR(55AA) : "+Affichage.dumpHex(self.MagiqueNumber))


    def istMbr(self):
        return self.isMbr

    def get_data(self):
        return self.data



    def findMbr(self,file):
        i=1
        res={}
        for chunk in iter(lambda:file.read(2), b''):
            res[i]=binascii.hexlify(chunk).decode("utf-8")
            if '55aa' == res[i] and i >= 256 and ('80' == res[i - 32][:2] or '00' == res[i - 32][:2]) and ('0000' == res[i - 33]):
                file.seek(i*2-512)
                data=file.read(512)
                file.seek(i*2-512)
                return True,data,i*2-512
            i+=1
        return False,None,None

        		
if __name__ == "__main__":

    file = open('physical-memory2.dmp', 'rb')
    mbr = MBRParser(file)
    if(mbr.istMbr()):
       #print(mbr.dumpHex(mbr.data))
        mbr.affichage()
        parttable= PartitionTable(mbr)


