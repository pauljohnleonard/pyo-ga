import subprocess,inspect
import atexit,time,Queue,threading

class Client:
    """
    
    Usage
    
    c=gaclient.Clinet(debug=False,srate=44100.0)
    c.build(nome)             # build Pheno on the server from the clinets nome
    c.send("pheno.play()")
    
    
    """
    
    def __init__(self,debug=False,srate=44100.0,dolog=True):
        self.debug=debug
        self.proc=None
        if  not debug:
            self.proc=subprocess.Popen(["python -i gaserver.py"], shell=True,
                                       stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
#            ,
#                                       stderr=subprocess.STDOUT,
#                                       stdout=subprocess.PIPE)
            
            self.pipe   = self.proc.stdin
            self.stdout = self.proc.stdout
            #print self.proc.pid
        if dolog:
            self.log=open("galient.log","w")
        else:
            self.log =None

     
        self.err_t=threading.Thread(target=self.pipe_reader)
        self.daemon=False
        self.q=Queue.Queue()
        self.err_t.start()
        atexit.register(quit)
        
    def pipe_reader(self):
        while True:
           
            text=self.stdout.readline()
            if len(text) == 0:
                print " end of file "
                return
            #print ":",text
            if self.err_t == None:
                return 
            self.q.put(text)
               

    def send(self,cmd):
        
        if self.debug:
            print cmd
        else:
            if self.log != None:
                self.log.write(cmd+"\n")
                self.log.flush()
            self.pipe.write(cmd+"\n")


    def build(self,pheno):
        self.send("pheno=Pheno()")
        for g in pheno.genes:
            cmd=g.__class__.__name__+"(pheno"
            ms=inspect.getmembers(g.data)
        
            for m in ms[2:]:
                cmd+=","+m[0].__str__()+"="+str(m[1])

            cmd +=")"
            self.send(cmd)
        #self.send("build.play()")
         
    def quit(self):
        print "quitting  .... "
        if self.proc == None:
            return
        self.send("server.stop()")
        self.send("time.sleep(0.5)")
        #self.send("quit()")
        
        self.pipe.close()
        #self.stdout.close()
        print " waiting for client to die"
        self.proc.wait()
        print " dead"
        self.proc = None
        print " . . . . . quitted "
        
     
 
if __name__ == "__main__":
   
   
    import ga
   
        
    n_voice=3
    n_delay=3
    n_envelope=3
    n_beat_modulation=3
    
   
    pheno=ga.Pheno()
    pheno.randomize(n_envelope=n_envelope,n_beat_modulation=n_beat_modulation,n_delay=n_delay,n_voice=n_voice) #n_src,n_delay,n_connect, n_voice)
    
    print "-----------------------------------------------"   
    #quit
    
    c=Client(debug=False)
    c.build(pheno)
    c.send("build.play()")
  
    while True:
        try:
            text=c.q.get(block=True)
            print text
        except Queue.Empty:
            pass    
    
    while True:
        foo=raw_input('cmd (type "quit" to exit):')
        print foo
        if foo == "quit":
            c.quit()
            time.sleep(1.0)
            break
        c.send(foo)
    
    
    print "OK I quit" 
        