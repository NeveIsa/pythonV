

class Disk:
    def __init__(self,BlockDevice):
        self.devname = BlockDevice
    
    def seek(self,addr):
        self.dev.seek(addr)

    def read(self,n):
        return self.dev.read(n)

    def vbrReadWord(self,addr):
        return ord(self.vbr[addr]) + 256*ord(self.vbr[addr+1])
    
    def vbrReadByte(self,addr):
        return ord(self.vbr[addr])

    def open(self):
        self.dev = open(self.devname,'rb')
        self.vbr = self.read(512)
        self.vbr_oemId=self.vbr[3:11]
        
        self.BPS=self.vbrReadWord(11)
        self.SPC=self.vbrReadByte(13)
        self.resvSec=self.vbrReadWord(14)
        self.nFat=self.vbrReadByte(16)
        self.nRootEntries=self.vbrReadWord(17)

        self.SPF=self.vbrReadWord(0x16)
        self.nHiddenSec=self.vbrReadWord(28)+256*256*self.vbrReadWord(30)
        self.nVolTotalSec=self.vbrReadWord(32)+256*256*self.vbrReadWord(34)
    
        self.vbr_systemId=""
        for x in range(8):
            self.vbr_systemId+=chr(self.vbrReadByte(0x36+x))


        self.BPC=self.BPS*self.SPC
        self.startFAT=self.resvSec*self.BPS
        self.startROOT=self.startFAT + self.nFat*self.SPF*self.BPS
        self.startFILEAREA=self.startROOT + self.nRootEntries*32 

        #self.seek(self.startROOT+32)
        #print self.read(32)

        print "=============== vbr ==============="
        print "OEMID:",self.vbr_oemId.replace(" ","*")
        print "BPS:",self.BPS
        print "SPC:",self.SPC
        print "**BPC:",self.BPC/1024,"kB"
        print "RESERVED SECTORS:",self.resvSec
        print "N FATS:",self.nFat
        print "N ROOT ENTRIES:",self.nRootEntries
        print "SPF:",self.SPF
        print "N HIDDEN SECTORS:",self.nHiddenSec
        print "N TOTAL SECTORS ON DISK:",self.nVolTotalSec
        print "SYSTEM ID:",self.vbr_systemId.replace(" ","*")
        print "=============== vbr ==============="


    def listFiles(self,search=None):
        self.seek(self.startROOT+32)
        
        print "======================= ROOT DIR ======================"
        
        if search:
            search=search.upper()
            sName,sExt=search.split(".")
            assert len(sName)<=8
            assert len(sExt)<=3
            sName=sName+" "*(8-len(sName))
            sExt=sExt+" "*(3-len(sExt))
            search=sName+sExt
            print "Searching for --->",search
            #return

        for i in range(self.nRootEntries):
            #print "RootEntry Number --->",i
            entry=self.read(32)
            if ord(entry[0])==0xe5 or ord(entry[0])==0x00 or ord(entry[0])==0xff:
                pass 
            else:
                filename=entry[:11]
                if not search:
                    print filename
                elif search==filename:
                    fileStartCluster = ord(entry[26]) + ord(entry[27])*256
                    fileLength= ord(entry[28]) + ord(entry[29])*256 + ord(entry[30])*256*256 + ord(entry[31])*256*256*256
                    print "Found file at cluster,size: %s , %s" % (fileStartCluster,fileLength)
                    return (fileStartCluster,fileLength)
                     
                #print "This file:",filename
                #print "File not found:",search

            #print filename,search
        return 0,0


        print "======================= ROOT DIR ======================"
        

    def readFileByClusterAddr(self,fileStartCluster,fileSize):
        # Note -- The first cluster in FILEAREA is treated as Cluster No. 2 as entries for Cluster1 and Cluster2 entries in are marked by speacial bytes in FAT Table
        
        import sys
        out=sys.stdout
        
        while fileSize:
            self.seek(self.startFILEAREA + (fileStartCluster-2) * self.BPC)
            
            if fileSize <= self.BPC:
                print self.read(fileSize)
                #out.write(self.read(fileSize))
                #out.flush()
                break
            else:
                out.write(self.read(self.BPC))
                self.seek(self.startFAT + fileStartCluster*2)

                #Use FAT Table
                fileStartCluster= ord(self.read(1)) + ord(self.read(1))*256

                #Check end of file, for safety, this point will not be reached as it will break in the above if condn
                if fileStartCluster >= 0xfff8:
                    break

                fileSize-=self.BPC


    def readFile(self,name):

        fCluster,fSize=self.listFiles(name)
        if not fSize:
            print "FILE NOT FOUND OR FILE IS 0 BYTES"

        print "================================== FILE CONTENTS ==================================="
        self.readFileByClusterAddr(fCluster,fSize) 
        print "================================== FILE CONTENTS ==================================="


if __name__=="__main__":
    import sys
    search=None
    if len(sys.argv)>1:
        search=sys.argv[1]

    d=Disk("/dev/sdb5")
    d.open()
    if not search:
        d.listFiles()
    else:
        d.readFile(search)

