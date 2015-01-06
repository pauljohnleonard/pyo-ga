import gaclient

import ga
import time
  
  
c=gaclient.Client(debug=False)
count=0
while True:         
    n_voice=10
    n_delay=10
    n_envelope=10
    n_beat_modulation=10
    
    
   
    pheno=ga.Pheno()
    pheno.randomize(n_envelope=n_envelope,
                    n_beat_modulation=n_beat_modulation,
                    n_delay=n_delay,
                    n_voice=n_voice,
                    sequence_len=4) #n_src,n_delay,n_connect, n_voice)
    
    print "--------",count,"---------------------------------------"   
    count=count+1
    
   
    c.build(pheno)

    c.send("build.play()")
    
    
    time.sleep(1.5)
    c.send("kill.play()")
    time.sleep(1.5)
    
    