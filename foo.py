import sys,os
from ctypes import *

libc = CDLL("libc.so.6")

base_adddr = 0x0219a000 #0x20000
CFUNC = CFUNCTYPE(c_int,c_void_p)
#x=libc.fork(None)

MYSELF = os.path.abspath(os.path.expanduser(__file__))
if os.path.islink(MYSELF):
    HEAPFILE = os.readlink(MYSELF)
sys.path.append(os.path.dirname(MYSELF))

from builder import Builder



b = Builder('./foo'+sys.argv[1]         \
           ,['a','b','c']               \
           ,["PATH=/tmp/",'EVIL=dupa']  \
           )

payload = b.payload()
lpayload = (len(payload) + 0x1000) & ~(0x1000-1)
#exit()

x = libc.fork()
if x == 0:
    libc.sleep(15)
    addr = c_void_p(base_adddr)
    libc.mmap(addr,lpayload,7,0x32,0,0)
    libc.memcpy(addr,payload,len(payload))
    cfun = cast(addr,CFUNC)
    cfun(addr)
    exit()

else:
    print "[Parent] Child pid: %d" % x
    x=raw_input()
    exit()
