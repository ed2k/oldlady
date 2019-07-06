from floater_client import *

from threading import Thread
class PP(Thread):
    def __init__(self,id, vfunc):
        Thread.__init__(self)
        self.vfunc = vfunc
        self.id = id
    def run(self):
        self.vfunc(State())
        print self.id, 'done'
   
if __name__ == "__main__":
   th = [PP(i,one_client) for i in xrange(3) ]
   for x in th: x.start()
   #for x in th: x.join()
   
