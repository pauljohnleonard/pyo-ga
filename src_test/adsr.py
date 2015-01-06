from pyo import *
s = Server().boot()
s.start()


trig1=Trig().stop()
trig2=Trig().stop()



#c=Counter(trig,min=0,max=2,dir=0)
c=Iter(trig,choice=[1,0])
p2=Print(c,method=1,message="count")


f = MidiDelAdsr(c,attack=.01, decay=.02, sustain=.05, release=.01)
a = BrownNoise(mul=f).mix(2)
v = Biquad(a, freq=1000, q=1, type=0, mul=1, add=0).out()


#
#
#v.ctrl()

#
#def repeat():
#    f.play()
#
#
#pat = Pattern(function=repeat, time=2).play()
#
#for _ in range(6):
#    time.sleep(1.0)
#    trig.play()
#    
#s.stop()
#time.sleep(1)

s.gui(locals())