#import sys
from ctypes import *

libc = CDLL("libc.so.6")

base_adddr = 0x2000
CFUNC = CFUNCTYPE(c_int,c_void_p)
x=libc.fork(None)

if x == 0:
    print libc.getpid()
    addr = c_void_p(base_adddr)
    libc.mmap(addr,1024,7,0x32,0,0)
    libc.memcpy(addr,"\xcc\xcc\xcc",3)
    cfun = cast(addr,CFUNC)
    cfun(addr)
    exit()

else:
    print "Parent"
    exit()
