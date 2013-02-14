from struct import *


## i dont realy care for rest right now
PT_LOAD = 1
PT_GNU_STACK = 0x6474e551

class phdr(object):
    def __init__(self,addr,is32,endi):
        # extra
        self.address = addr
        self.is32 = is32
        self.endianes = endi

        self.p_type   = None
        self.p_offset = None
        self.p_vaddr  = None
        self.p_filesz = None
        self.p_memsz  = None
        self.p_flags  = None
        self.p_align  = None

    def parse(self,mem): # whole file

        fmt = self.endianes
        if self.isx86:
            fmt += 'IIIIIIII'
        else:
            fmt += 'IIQQQQQQ'

        ( self.p_type \
        , self.p_offset \
        , self.p_vaddr \
        , self.p_filesz \
        , self.p_memsz \
        , self.palign \
        ) = unpack_from(fmt,mem,self.address)

        if not self.is32: ## hacki-hacki
            tmp = self.p_memsz
            self.p_flags = self.p_memsz
            self.p_memsz = tmp


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


        (self.e_ident     \
        ,self.e_type      \
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


    def enum_phdr(self):

        if not self.e_ident and not self.mem:
            self.parse(self.mem)

        if not self.e_ident:
            print "[-] parse youre memory first dude"
            return

        for i in range(0,self.e_phnum):

            addr = self.e_phoff + (i*self.e_phoff)
            ph = phdr(addr,self.is32,self.endines)
            ph.parse(mem)

            yield ph
