

class Disk:
    def __init__(self,BlockDevice):
        self.devname = BlockDevice
    
    def open(self):
        self.dev = open(self.devname,'rb')
        self.mbr = self.dev.read(512)
        print "=== MBR ==="
        print self.mbr

        


if __name__=="__main__":
    d=Disk("/dev/sdb5")
    d.open()
