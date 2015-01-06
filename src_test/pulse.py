from pyo import *


s=Server().boot().start()

t1=Trig()
t2=Trig()
h=SampHold(t1,t1+t2,1.0)
pr=Print(h,method=1)


s.gui(locals())

