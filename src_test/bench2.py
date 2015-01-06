from pyo import *
#import time

srate=44100.0
s=Server(sr=srate,duplex=0).boot()
s.start()
s.verbosity=15

T=0.5

def foo():
  #print "X"
  #try : 
    global t1,count
    t2=time.time()
    dt=t2-t1
    print (dt/T-1.0),count
    t1=t2
    for _ in range(100):
        oo=Sig(src).out()
        o.append(oo)
        count += 1
  #except:
     
  #  print "Unexpected error:", sys.exc_info()[0]
  #  raise

src=Sine(freq=500).out()
src2=Sine(freq=400)
src3=Sine(freq=300)
met=Metro(.5).play()
ff=TrigFunc(met,foo)

count=0
o=[]
t1=time.time()
    
s.gui(locals())