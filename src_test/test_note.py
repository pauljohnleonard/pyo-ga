from  ga import *

if __name__ == "__main__":
    
    s=pyo.Server(sr=srate,duplex=0).boot()
   
    pheno1=Pheno()
    pheno1.randomize(sequence_len=1,
                     n_noise=0,
                     n_amp_seq=1,
                     n_note_seq=1,
                     n_osc=1,
                     n_envelope=1,
                     n_enveloped_noise=1,
                     n_offbeat=0,
                     n_filter=1) #n_src,n_delay,n_connect, n_voice)     
    pheno1.build()
    
    print "Pheno \n",pheno1

    pheno1.play()
    
    s.gui(locals())
