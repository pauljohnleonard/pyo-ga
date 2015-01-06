from pyo import *
import math
import time

srate=44100.0
chunkSize=256
s=Server(sr=srate,duplex=0,buffersize=chunkSize).boot().start()


freq=400.0
size=int(srate/freq)
dur=size/srate


samps=[0]*size

for i in range(size):
        samps[i]=((i-size/2)+0.5)/(size-1)
        

trig=Trig()

tab=NewTable(length=dur,chnls=1,init=samps)

print size,tab.getSize()

conv=Convolve(trig,tab,size)

conv.out()

s.gui(locals())
