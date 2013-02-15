
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

            sh = ('e8c400665d66678b450066a901000000741366a902000000746f66a903000000747b'
                  'e9940066678b5d0266678b4d066681c1001000006681e100f0ffff6066b85b000000'
                  'cd8061665566ba0700000066be3200000066bf0000000066bd0000000066b8c00000'
                  '00cd80665d66678d750a66678b7d0266678b4d06f3a466678d450a66678d6806e97c'
                  'ff66678d750a66678b7d0266678b4d06f3a4e968ff66678b450266678b65066631db'
                  '6631c96631d26631f66631ff66ffe066bb0100000066b801000000cd80e939ff'
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
