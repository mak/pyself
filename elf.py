from struct import *


class phdr(object):

    PT_TYPE = {
      0: 'PT_NULL'
     ,1: 'PT_LOAD'
     ,2: 'PT_DYNAMIC'
     ,3: 'PT_INTERP'
     ,4: 'PT_NOTE'
     ,5: 'PT_SHLIB'
     ,6: 'PT_PHDR'
     ,7: 'PT_TLS'
     ,8: 'PT_NUM'
     ,0x6474e550: 'PT_GNU_EH_FRAME'
     ,0x6474e551: 'PT_GNU_STACK'
     ,0x6474e552: 'PT_GNU_RELRO'
    }

    PF_X = 1 << 0
    PF_W = 1 << 1
    PF_R = 1 << 2

    def __init__(self,addr,is32,endi):
        # extra
        self.address = addr
        self.is32 = is32
        self.endianes = endi

        self.p_type   = None
        self.p_offset = None
        self.p_vaddr  = None
        self.p_paddr  = None
        self.p_filesz = None
        self.p_memsz  = None
        self.p_flags  = None
        self.p_align  = None

        for k,v in self.PT_TYPE.items():
            setattr(self,v,k)

    def parse(self,mem): # whole file

        fmt = self.endianes
        if self.is32:
            fmt += 'IIIIIIII'
        else:
            fmt += 'IIQQQQQQ'

        ( self.p_type \
        , self.p_offset \
        , self.p_vaddr \
        , self.p_paddr \
        , self.p_filesz \
        , self.p_memsz \
        , self.p_flags \
        , self.p_align \
        ) = unpack_from(fmt,mem,self.address)

        if not self.is32: ## hacki-hacki
            tmp = self.p_memsz
            self.p_flags = self.p_memsz
            self.p_memsz = tmp

    def aligned(self,from_file = False):
        ad = self.p_filesz if from_file else self.p_memsz
        return self.align(ad)

    def align(self,value):
        a_s = self.p_align
        am = ~(a_s-1)
        return (value + a_s) & am

    def prety_flag(self):
        ret = ''
        ret += "R" if self.p_flags & self.PF_R else ' '
        ret += "W" if self.p_flags & self.PF_W else ' '
        ret += "X" if self.p_flags & self.PF_X else ' '
        return ret

    def dump(self):

        if not self.p_type:
            return ""
        ret = ''
        ret += "%s\t"  % self.PT_TYPE[self.p_type]
        ret += "%x   " % self.p_offset
        ret += "%x   " % self.p_vaddr
        ret += "%x   " % self.p_paddr
        ret += "%x   " % self.p_filesz
        ret += "%x   " % self.p_memsz
        ret += "%s   " % self.prety_flag()
        ret += "%x   " % self.p_align
        return ret


    def __str__(self):
        return self.dump()

class ehdr(object):

    def __init__(self,mem=None):

        self.mem = mem

        self.e_ident     = None
        self.e_type      = None
        self.e_machine   = None
        self.e_version   = None
        self.e_entry     = None
        self.e_phoff     = None
        self.e_shoff     = None
        self.e_flags     = None
        self.e_ehsize    = None
        self.e_phentsize = None
        self.e_phnum     = None
        self.e_shentsize = None
        self.e_shnum     = None
        self.e_shstrndx  = None



    def parse(self,mem=None):

        nmem = self.mem if not mem else mem

        self.e_ident = unpack_from('16B',nmem,0)
        self.is32    = self.e_ident[4] == 1
        self.endines = '<' if self.e_ident[5] == 1 else '>'

        fmt = self.endines
        if self.is32:
            fmt += 'HHIIIIIHHHHHH'
        else:
            fmt += 'HHIQQQIHHHHHH'

        (self.e_type      \
        ,self.e_machine   \
        ,self.e_version   \
        ,self.e_entry     \
        ,self.e_phoff     \
        ,self.e_shoff     \
        ,self.e_flags     \
        ,self.e_ehsize    \
        ,self.e_phentsize \
        ,self.e_phnum     \
        ,self.e_shentsize \
        ,self.e_shnum     \
        ,self.e_shstrndx  \
        ) = unpack_from(fmt,nmem,16)

        return self

    def enum_phdr(self):

        if not self.e_ident and self.mem:
            self.parse(self.mem)

        if not self.e_ident:
            print "[-] parse youre memory first dude"
            return

        for i in range(0,self.e_phnum):

            addr = self.e_phoff + (i*self.e_phentsize)
            #print "phdr @ %x" % addr

            ph = phdr(addr,self.is32,self.endines)
            ph.parse(self.mem)

            yield ph
