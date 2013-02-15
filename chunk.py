import sys,os


MYSELF = os.path.abspath(os.path.expanduser(__file__))
if os.path.islink(MYSELF):
    HEAPFILE = os.readlink(MYSELF)
sys.path.append(os.path.dirname(MYSELF))


from  elf import *

class Chunk(object):

    LOAD_TYPE  = 1
    STACK_TYPE = 2
    ENTRY_TYPE = 3

    def __init__(self,mem,argv,env):
        self.mem = mem
        self.argv = argv
        self.env = env
        self.chunks = []

    def make_stack(self,ph,sf):

        stack_top = 0xc0000000 if ph.is32 else 0x800000000000
        data = [pack('I',len(self.argv))]

        stack_top -= ph.p_align
        tmpenv  = ["\x00"*ph.p_align]
        tmpaddrenv = [stack_top]
        for ev in self.env:
            l = len(ev)
            l += ph.align(l)
            a = ev + "\x00" *l
            stack_top -= l
            tmpenv.append(a)
            tmpaddrenv.append(stack_top)

        stack_top -= ph.p_align
        tmpargv  = ["\x00"*ph.p_align]
        tmpaddrargv = [stack_top]
        for ar in reversed(self.argv):
            l = len(ar)
            l += ph.align(l)
            a = ar + "\x00" *l
            stack_top -= l
            tmpargv.append(a)
            tmpaddrargv.append(stack_top)

        for a in reversed(tmpaddrargv):
            data.append(pack(sf,a))

        for a in tmpaddrenv:
            data.append(pack(sf,a))

        for a in reversed(tmpargv):
            data.append(a)

        for a in reversed(tmpenv):
            data.append(a)

        data = ''.join(data)
        alen = ph.align(len(data))
        data += ("\x00"*(alen-len(data)))

        self.stack = ph.align(stack_top)

        return pack('H',self.STACK_TYPE) + \
               pack(sf*2,ph.align(stack_top),alen) + \
               data

    def make_load(self,ph,sf):
        data = self.mem[ph.p_offset:ph.p_offset+ph.p_filesz]
        data += "\x00" * (ph.p_memsz - ph.p_filesz) ## .bss
        data += "\x00" * (ph.aligned() - ph.p_memsz)

        return pack("H",self.LOAD_TYPE) + \
               pack(sf*2,ph.p_vaddr,ph.aligned()) +\
               data


    def make_entryp(self,ehdr,sf):

        if not self.stack:
            raise ValueError("Build stack first!")

        return pack("H",self.ENTRY_TYPE) + pack(sf*2,ehdr.e_entry,self.stack)


    def make_chunk(self,hdr):
        sf = 'I' if hdr.is32 else 'Q'

        if not hdr.__class__ in [ehdr,phdr]:
            raise TypeError('Wrong header type')

        if hdr.__class__ == ehdr :
            return self.make_entryp(hdr,sf)

        else:
            if hdr.p_type == hdr.PT_LOAD:
                return self.make_load(hdr,sf)
            elif hdr.p_type == hdr.PT_GNU_STACK:
                return self.make_stack(hdr,sf)

    def append(self,hdr):
        self.chunks.append(self.make_chunk(hdr))
