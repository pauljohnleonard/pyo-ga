from pyo import *
from ga import  *  
import time,gc
import atexit
  
srate=44100.0        
server=Server(sr=srate,duplex=0)
#server.verbosity=15
server.boot()
server.start()
pheno=None 
kill=None

def myquit():
    server.stop()
    
atexit.register(myquit)
  
def pheno_kill():
    global pheno
    if pheno == None:
        return
    if pheno.built==False:
        print " ---------- killing unbuilt pheno? "
    pheno.kill()
    pheno=None
 

    
def pheno_build():
    global kill,trig_kill
    if pheno == None:
        return
    pheno.build()
    kill=Trig().stop()
    trig_kill=TrigFunc(kill,pheno_kill)     



build=Trig().stop()
trig_build=TrigFunc(build,pheno_build)


