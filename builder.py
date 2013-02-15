
import sys,os,binascii


MYSELF = os.path.abspath(os.path.expanduser(__file__))
if os.path.islink(MYSELF):
    HEAPFILE = os.readlink(MYSELF)
sys.path.append(os.path.dirname(MYSELF))


from  elf import *
from chunk import Chunk


class Builder(object):

    def __init__(self,file=None,argv=None,envp=None):
        self.mem= open(file if file else sys.argv[1]).read()
        self.argv = argv if argv else sys.argv[2].split(';')
        self.envp = envp if envp else sys.argv[3].split(';')
        self.elf  = ehdr(self.mem).parse()

    def loader(self):

        if self.elf.is32:

            sh = (
                # nop sled just for some posible fuckups
                '909090909090'
                ## actual code - look load_x86.asm
e9930000005d31c0668b450083f801740c83f802744c83f803745feb6f8b5d028b4d0681c10010000081e100f0ffff60b85b000000cd806155ba07000000be32000000bf00000000bd00000000b8c0000000cd805d8d750a8b7d028b4d06f3a4eb0d8d750a8b7d028b4d06f3a4eb008d450a8b5d068d2c18eb8c8b45028b650631db31c931d231f631ffffe0bb01000000b801000000cd80e868ffffff

                 )
        else:
            sh  =''

        return binascii.a2b_hex(sh)



    def payload(self):
        c = Chunk(self.mem,self.argv,self.envp)
        print "Type\tOffset  VirtAddr  PsychAddr  FileSz   MemSz   Flg   Align"
        for ph in self.elf.enum_phdr():
            print ph
            if ph.p_type in  [ph.PT_LOAD,ph.PT_GNU_STACK] :
                c.append(ph)

        c.append(self.elf)
        return self.loader() + ''.join(c.chunks)
