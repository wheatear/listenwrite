" Simple multiprocessing test.pystones benchmark "
" Anders Wallin 2008Jun15 anders.e.e.wallin (at) gmail.com "

import test
# from test import pystone
import multiprocessing
import time

STONES_PER_PROCESS= 10*test.pystone.LOOPS

def f(q):
    t=test.pystone.pystones(STONES_PER_PROCESS)
    q.put(t,block=True)

if __name__ == '__main__':
    print 'multiprocessing test.pystones() benchmark'
    print 'You have '+str(multiprocessing.cpuCount()) + ' CPU(s)'
    print 'Processes\tPystones\tWall time\tpystones/s'

    results = multiprocessing.Queue()
    for N in range(1,multiprocessing.cpuCount()+3):
        p=[]
        q=multiprocessing.Queue()
        results=[]

        for m in range(1,N+1):
            p.append( multiprocessing.Process(target=f,args=(q,)) )

        start=time.time()
        for pr in p:
            pr.start()
        for r in p:
            results.append( q.get() )
        stop=time.time()

        cputime = stop-start

        print str(N)+'\t\t'+str(N*STONES_PER_PROCESS) \
              +'\t\t'+ str(cputime)+'\t'+str( N*STONES_PER_PROCESS / cputime )
