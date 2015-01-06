from ga import OffBeatGene

# allow GUI to run even if sqlalchemy is absent
try:
    import sqlalchemy
    import database
    db_loaded = True 
except ImportError: 
    print "sqlalchemy  not found. No database capabilities."
    db_loaded = False
        
import ga     
import wx
import gaclient 
#import threading
import Queue

import wx.lib.scrolledpanel

from Widgets import *
from Plugins import *
    
N_DELAY=10
N_ENV=10
N_MOD=10
N_VOICE=10
labelCol=wx.BLUE

def error_message(mess,parent):
    wx.MessageDialog(parent,message=mess, caption="MessageBoxCaptionStr",style=wx.OK).ShowModal()
    
    
class GeneEditPanel(wx.Panel):

    def __init__(self,gene,parent, pheno, title="Nome Edit"):   # ,size=(300, 50)):

        wx.Panel.__init__(self, parent, -1,style=wx.BORDER)
        
        self.pheno=pheno
        self.knobs=[]
        sizer = wx.BoxSizer(wx.HORIZONTAL)
    
        maps=gene.__class__.maps
        if maps == None:
            print "No maps for ", gene
            return
            
        self.gene=gene  
        for attr,mapx in maps.items():
            try: 
                val=getattr(self.gene.data,attr)
            except AttributeError:
                print sys.exc_info()[0]
                print self.gene 
                continue
            
            if   isinstance(val, list):
                assert len(self.knobs) == 0    # only one list 
                for v in val:        
                    knob1 = PluginKnob(self, mapx.min,mapx.max,v,log=mapx.scale=='log',outFunction=self.callbacklist,size=(43,70), label=attr,key=attr)
                    self.knobs.append(knob1)
                    sizer.Add(knob1)
                
            else:
                if mapx.scale == "choice":
                    knob1 = CustomMenu(self, choice=mapx.unit, init=mapx.unit[val], size=(93,18), colour=CPOLY_COLOUR, outFunction=self.callbackchoice,key=attr)
                else:
                    knob1 = PluginKnob(self, mapx.min,mapx.max, val,log=mapx.scale=='log',outFunction=self.callback,size=(43,70), label=attr,key=attr)
                
                sizer.Add(knob1)
            
        self.SetSizer(sizer)

        self.maps=maps
      
        
    def callback(self,val,attr):
        index=self.pheno.genes.index(self.gene)
        cmd="pheno.genes["+str(index)+"].setAttr(\'"+attr+"\',"+str(val)
        cmdRemote=cmd+",build=True)"
        client.send(cmdRemote)
        self.gene.setAttr(attr,val,build=False)

      
    def callbackchoice(self,ival,lab,attr):
        #print "index of",lab,"=",ival," attr=",attr
        index=self.pheno.genes.index(self.gene)
        cmd="pheno.genes["+str(index)+"].setAttr(\'"+attr+"\',"+str(ival)
        cmdRemote=cmd+",build=True)"
        client.send(cmdRemote)
        self.gene.setAttr(attr,ival,build=False)


    def callbacklist(self,dmy,attr):
        index=self.pheno.genes.index(self.gene)
        vv=[]
        for k in self.knobs:
            vv.append(k.getValue())
        
        cmd="pheno.genes["+str(index)+"].setAttr(\'"+attr+"\',"+str(vv)
        cmdRemote=cmd+",build=True)"
        client.send(cmdRemote)
        self.gene.setAttr(attr,vv,build=False)
        

class WidgetPanel(wx.Panel):
    
    def __init__(self,parent,id=-1,style=wx.BORDER):
        wx.Panel.__init__(self, parent,id,style=wx.BORDER)
        self.widgets=[]
        
    def inport(self,ii):
        rectP=self.Parent.GetRect()
        rectC=self.widgets[ii].GetRect()
        return rectP.x+rectC.x,rectP.y+rectC.y+rectC.height/2        

    def outport(self,ii):
        rectP=self.Parent.GetRect()
        rectC=self.widgets[ii].GetRect()
        return rectP.x+rectC.x+rectC.Width,rectP.y+rectC.y+rectC.height/2        
    
class SequencePanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Sequences",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for g in pheno.sequences:
            str1=str(g.data.seq)
            label=wx.StaticText(self,-1,str1)
            self.widgets.append(label)
            sizer.Add(label)
            
        self.SetSizer(sizer)
        
   
     
class AmpMapPanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Amp Maps",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for g in pheno.amps:
            str1=""
            for x in g.data.map:
                str1 +=  "{0:.1f} ".format(x)
            label=wx.StaticText(self,-1,str1)
            self.widgets.append(label)
            sizer.Add(label)
            
        self.SetSizer(sizer)
        
               
class NoteMapPanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Note Maps",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for g in pheno.notes:
            str1=str(g.data.map)
            label=wx.StaticText(self,-1,str1)
            self.widgets.append(label)
   
            sizer.Add(label)
            
        self.SetSizer(sizer)
        
        
               
class NoisePanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Sources",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for g in pheno.noises:
            if isinstance(g,ga.NoiseGene):
                label=wx.StaticText(self,-1,"Noise")
            elif isinstance(g,ga.OscGene):
                label=GeneEditPanel(g,self,pheno)
             
            self.widgets.append(label)
      
            sizer.Add(label)
            
        self.SetSizer(sizer)
        

class EnvelopePanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Envelopes",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)
        self.widgets=[]  
        for g in pheno.envelopes:
           
            label=GeneEditPanel(g,self,pheno)
            self.widgets.append(label)    
            sizer.Add(label)
            
        self.SetSizer(sizer)

class TriggerPanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        
        
      
        sizerH=wx.BoxSizer(wx.HORIZONTAL)
        
#        label=wx.StaticText(self,-1,"Triggers",style=wx.RAISED_BORDER)
#        label.SetForegroundColour(labelCol)
#        sizer.Add(label)  
#        
        sizerV=wx.BoxSizer(wx.VERTICAL)

        for g in pheno.triggers:

            if isinstance(g,ga.BeatGene):
                label=GeneEditPanel(g,self,pheno)
                sizerH.Add(label)
            else:
                mapx=ga.OffBeatGene.maps['pos'] 
                val=g.data.pos                
                label = ControlSlider(self, mapx.min,mapx.max, val,log=mapx.scale=='log',outFunction=self.callback,size=(100,10),key=g)
                sizerV.Add(label)
           
            self.widgets.append(label)
            
            
            
        sizerH.Add(sizerV)
        self.SetSizer(sizerH)
        
    def callback(self,val,g):
        index=g.pheno.genes.index(g)
        cmd="pheno.genes["+str(index)+"].setAttr('pos',"+str(val)
        cmdRemote=cmd+",build=True)"
        client.send(cmdRemote)
        g.setAttr('pos',val,build=False)
  
        
class FilterPanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Filters")
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for g in pheno.filters:
           
            label=GeneEditPanel(g,self,pheno)
            self.widgets.append(label)  
            sizer.Add(label)
            
        self.SetSizer(sizer)        


        
class FilterInPanel(WidgetPanel):
    
    def __init__(self,parent,pheno):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.VERTICAL)
        
      
        label=wx.StaticText(self,-1,"Filter Ins",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for _ in pheno.filterIns:
            label=wx.StaticText(self,-1,"IN")
            self.widgets.append(label)  
            sizer.Add(label)
            
        self.SetSizer(sizer)        

class FiltPanel:
    def __init__(self,sizer,panel,pheno,filt):
        
        
        filter_in=pheno.filters.get(filt.data.input_id)
        
        mod_noise=pheno.filterIns.get(filter_in.data.input_id)
        
         
        env=pheno.envelopes.get(mod_noise.data.env_id)
        noise=pheno.noises.get(mod_noise.data.noise_id)
        
        if noise.__class__.maps != None:
            noisePanel=GeneEditPanel(noise,panel,pheno)
            sizer.Add(noisePanel)
        
        envPanel=GeneEditPanel(env,panel,pheno)
        sizer.Add(envPanel)
        
        
        label=wx.StaticText(panel,-1,"Phrase")
        #self.widgets.append(label)  
        sizer.Add(label)
     
        
        
        sizerV=wx.BoxSizer(wx.VERTICAL)
        
        str1=""
        
        phrase_id=env.data.phrase_id
        phrase=pheno.phrases.get(phrase_id)
        
        for x in pheno.sequences.get(phrase.data.amp_seq_id).data.seq:
                str1 +=  "{0:.1f} ".format(x)
        label=wx.StaticText(panel,-1,str1)  
        
        #self.widgets.append(label)  
        sizerV.Add(label)
            
        str1=""
        for x in pheno.sequences.get(phrase.data.pitch_seq_id).data.seq:
                str1 +=  str(x)+" "
        label=wx.StaticText(panel,-1,str1)  
        
        #self.widgets.append(label)  
        sizerV.Add(label)
        sizer.Add(sizerV)
     
    
        filtPanel=GeneEditPanel(filt, panel, pheno, "Filter")
        sizer.Add(filtPanel)
            
            

class PhrasePanel(WidgetPanel):
    def __init__(self,parent,pheno,phrase):
        WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        
    
        label=wx.StaticText(self,-1,"Phrase")
        self.widgets.append(label)  
        sizer.Add(label)
     
        
        
        sizerV=wx.BoxSizer(wx.VERTICAL)
        
        str1=""
        
        for x in pheno.sequences.get(phrase.data.amp_seq_id).data.seq:
                str1 +=  "{0:.1f} ".format(x)
        label=wx.StaticText(self,-1,str1)  
        
        self.widgets.append(label)  
        sizerV.Add(label)
            
        str1=""
        for x in pheno.sequences.get(phrase.data.pitch_seq_id).data.seq:
                str1 +=  str(x)+" "
        label=wx.StaticText(self,-1,str1)  
        
        self.widgets.append(label)  
        sizerV.Add(label)
        sizer.Add(sizerV)
            
        self.SetSizer(sizer)        


class VoicesPanel:
    
    def __init__(self,sizer,pheno,parent):
        #WidgetPanel.__init__(self, parent, -1,style=wx.BORDER)
         
        label=wx.StaticText(parent,-1,"Filters",style=wx.RAISED_BORDER)
        label.SetForegroundColour(labelCol)
        sizer.Add(label)  
        for filt in pheno.filters:
            
            
            sizer1=wx.BoxSizer(wx.HORIZONTAL)
            widget=FiltPanel(sizer1,parent,pheno,filt)
            sizer.Add(sizer1)
            
        #self.SetSizer(sizer)        
        
        
                
                  

class NomeEditFrame(wx.Frame):
    def __init__(self,pheno,parent, title="Nome Edit", pos=(100,100), size=(300, 250)):
        wx.Frame.__init__(self, parent, -1, title,style =  wx.DEFAULT_FRAME_STYLE) 
        self.pheno=pheno
       
        self.makeGuiPJL()
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        
    def OnPaint(self,evt):
        dc = wx.PaintDC(self.panel)
        rect=self.panel.GetRect()
        dc.BeginDrawing()
      
        dc.DrawLine(0,0,rect.Width,rect.Height)
        dc.EndDrawing()
        print "ONPAINT"     
       
        
    def rebuildNome(self):
        print "rebuild"
     
 
    def makeGuiPJL(self):
        
        #sizerH=wx.BoxSizer(wx.HORIZONTAL)
        
        
        self.panel=wx.lib.scrolledpanel.ScrolledPanel(self, -1)
        panel=self.panel
        
        sizerV=wx.BoxSizer(wx.VERTICAL)
        
       
        
        p=TriggerPanel(panel,self.pheno) 
        sizerV.Add(p)
        self.trigPan=p
        
            
        #----------------------------------------------------
        #sizer=wx.BoxSizer(wx.VERTICAL)
  
        self.voices=VoicesPanel(sizerV,self.pheno,panel) 
        #sizerV.Add(sizer)
                   
        
        panel.SetSizer(sizerV)
        
        panel.SetAutoLayout(1)
        panel.SetupScrolling()
        
#        sizer.Add((40,1))
#
#        #----------------------------------------------------
#    
#        
#        sizer.Add((20,1))
#      
#        #-----------------------------------------------
#        sizerV=wx.BoxSizer(wx.VERTICAL)
#   
#        p=NoisePanel(panel,self.pheno)
#        sizerV.Add(p)     
#        self.noisePan=p
#        
#        p=AmpMapPanel(panel,self.pheno) 
#        sizerV.Add(p)
#        self.ampPan=p
#    
#        self.envPan=EnvelopePanel(panel,self.pheno)
#        sizerV.Add(self.envPan)
#        
#        
#        
#        sizer.Add(sizerV)
#        sizer.Add((20,1))
#        
#        #---------------------------------------------------
#        self.filtInPan=FilterInPanel(panel,self.pheno)
#        sizer.Add(self.filtInPan)
#        
#        sizer.Add((50,1))
#        #---------------------------------------------------
#        
#        
#        sizer.Add((50,1))
#        #---------------------------------------------------
#        p=FilterPanel(panel,self.pheno)
#        sizer.Add(p)
#        self.filtPan=p
#        
#        #--------------------------------------------------
#        panel.SetSizer(sizer)
#        
  
#         
#        print
#        
#        print self.envPan.GetRect()
#        for p in self.envPan.widgets:
#            print p.GetRect()
      
      
      
    
    def makeGuiLine(self,panel):
        
        sizerH=wx.BoxSizer(wx.HORIZONTAL)
        
        _iter = self.pheno.genes.__iter__()
        
        while(True):
            
            try:    
                g=_iter.next()
            
                maps=g.__class__.maps
                
                if maps == None:
                    continue
        
                p=GeneEditPanel(g,panel,self.pheno)
                sizerH.Add(p)
                
            except StopIteration:
                break
             
        panel.SetSizer(sizerH)    
     
    
class MyFrame(wx.Frame):
   
        
    def __init__(self,parent, title, pos, size=(300, 250)):
        wx.Frame.__init__(self, parent, -1, title, pos, size)
        self.pheno=None
        self.make_panels()
        if db_loaded:
            self.db=database.DataBase()
        else:
            self.db=None
            
        self.playing=False
        self.Bind(wx.EVT_IDLE,self.monit)
        self.editor=None
        
    
    def monit(self,evt):
        
        try:
            text=client.q.get(block=False)
            self.console.AppendText(text)
        except Queue.Empty:
            pass    
        
        #self.text=client.stdout.readline()
        #print self.text
            
    
    def make_panels(self):
        
        
        spin=self.make_spin_panel(self)
        
        but=self.make_button_panel(self)
        self.cmdbox = wx.TextCtrl (self, -1, style=wx.TE_PROCESS_ENTER )
        self.console = wx.TextCtrl(self, -1, " server console ", style=wx.TE_MULTILINE)
        
        box = wx.BoxSizer(wx.VERTICAL)
        
        box.Add(spin, 2, wx.EXPAND)
        box.Add(but, 1, wx.EXPAND)
        box.Add(self.cmdbox,0,wx.EXPAND)
        box.Add(self.console,4,wx.EXPAND)
        
        self.cmdbox.Bind(wx.EVT_TEXT_ENTER,self.cmd)
        
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
        
    def cmd(self,ev):
        print " CMD : ",self.cmdbox.GetValue()
        strx=self.cmdbox.GetValue()
        client.send(strx)
        self.cmdbox.Clear()
        
    def add_spinner(self,parent,minV,maxV,val,tit):
        
        panel=wx.Panel(parent,-1,style=wx.SUNKEN_BORDER)
     
        
        box = wx.BoxSizer(wx.VERTICAL)
      
        tit=wx.StaticText(panel, -1, tit)
      
        ctrl=wx.SpinCtrl(panel, -1, '')
        ctrl.SetRange(minV, maxV)
        ctrl.SetValue(val)
        
        box.Add(tit)
        box.Add(ctrl)
        
        panel.SetSizer(box)
        
        
        return ctrl,panel
        
        
        
        
    def  make_spin_panel(self,parent):
        
        panel=wx.Panel(parent,-1, style=wx.SUNKEN_BORDER)
        
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        
        self.n_offbeat,pan=self.add_spinner(panel,1,10,10,"Offbeats")
        sizer.Add(pan)
 
        self.n_sequence,pan=self.add_spinner(panel,1,10,4,"n Seq")
        sizer.Add(pan)
   
        self.sequence_len,pan=self.add_spinner(panel,1,10,4,"Seq Len")
        sizer.Add(pan)
        
        self.n_amp_map,pan=self.add_spinner(panel,1,10,4,"Amp map size")
        sizer.Add(pan)
        
        self.n_note_map,pan=self.add_spinner(panel,1,10,4,"Note map size")
        sizer.Add(pan)
   
        self.n_osc,pan=self.add_spinner(panel,1,10,10,"Oscillators")
        sizer.Add(pan)
 
        self.n_enveloped_noise,pan=self.add_spinner(panel,1,10,10,"Noise Env")
        sizer.Add(pan)
 
        self.n_envelope,pan=self.add_spinner(panel,1,10,10,"Envelopes")
        sizer.Add(pan)
 
        self.n_filter,pan=self.add_spinner(panel,1,10,10,"Filters")
        sizer.Add(pan)
   
   
             
        panel.SetSizer(sizer)
        
        return panel
           
    def  make_button_panel(self,parent):
        
        
        panel=wx.Panel(parent,-1, style=wx.SUNKEN_BORDER)
        box = wx.BoxSizer(wx.HORIZONTAL)
        
        
        creat=wx.Button(panel, 1, 'Create')    
        box.Add(creat,1,wx.EXPAND)
        
        kill=wx.Button(panel, 1, 'Kill')    
        box.Add(kill,1,wx.EXPAND)
 
        load=wx.Button(panel, 1, 'Load')    
        box.Add(load,1,wx.EXPAND)
        
        breed=wx.Button(panel, 1, 'Breed')    
        box.Add(breed,1,wx.EXPAND)
        
        edit=wx.Button(panel, 1, 'Edit')    
        box.Add(edit,1,wx.EXPAND)
        
        save=wx.Button(panel, 1, 'Save')    
        box.Add(save,1,wx.EXPAND)  
        
        quit=wx.Button(panel, 1, 'Quit')    
        box.Add(quit,1,wx.EXPAND)
        
        
        quit.Bind(wx.EVT_BUTTON, self.OnClose)
        kill.Bind(wx.EVT_BUTTON, self.kill_pheno)
        
        creat.Bind(wx.EVT_BUTTON, self.create_pheno)   
        edit.Bind(wx.EVT_BUTTON, self.edit_pheno)     
        breed.Bind(wx.EVT_BUTTON,self.breed_pheno)
        save.Bind(wx.EVT_BUTTON,self.save_pheno)
        load.Bind(wx.EVT_BUTTON,self.load_pheno)
                         
        #panel.SetAutoLayout(True)

        panel.SetSizer(box)
        #panel.Layout()
        return panel
        
        
   
    def OnClose(self,event):
        print "CLosing"
        self.err_t = None
        client.quit()
       
        # wait for the pipes to flush
        time.sleep(.2)
        self.Destroy()
        

    def edit_pheno(self,event):
        
        if self.pheno == None:
            error_message("Nothing to edit yet",self)
            return
            
        self.editor=NomeEditFrame(self.pheno,self)
        self.editor.Show()
        
    def kill_pheno(self,event=None):
        if self.playing:
            client.send("kill.play()") 
            # need to wait a for ticks so this gets called before 
            # attempt to build a new pheno
            client.send("time.sleep(0.3)")
            # client.send("print server.getNumberOfStreams()")
            if self.editor != None:
                try:                #  avoid error message if user has already closed editor
                    self.editor.Destroy()
                except:
                    pass
                
                self.editor=None
        
        
    def create_pheno(self,evt):

        self.kill_pheno()
                        
        pheno=ga.Pheno()
        
                                  
        pheno.randomize(n_sequences=self.n_sequence.GetValue(),
                        n_amp_map=self.n_amp_map.GetValue(),
                        n_note_map=self.n_note_map.GetValue(),
                        n_noise=1,
                        n_envelope=self.n_envelope.GetValue(),
                        n_osc=self.n_osc.GetValue(),
                        n_offbeat=self.n_offbeat.GetValue(),
                        n_enveloped_noise=self.n_enveloped_noise.GetValue(),
                        n_filter=self.n_filter.GetValue(),
                        sequence_len=self.sequence_len.GetValue()) 
        
        self.pheno=pheno
        self.build_server_pheno()
    
    def build_server_pheno(self):
    
        client.build(self.pheno)
        client.send("print pheno")
        client.send("build.play()")
                
        self.playing=True
     
 
        
    def load_pheno(self,evt):
        if not db_loaded:
            return
               
        self.kill_pheno()
        self.pheno=self.db.load_random()
        self.build_server_pheno()
        
    def breed_pheno(self,evt):
        self.kill_pheno()
        b=ga.Breeder()
        dad=self.pheno
        mum=self.db.load_random()
        child=b.mate(mum,dad)
        self.pheno=child
        print child
        self.build_server_pheno()
        
    def save_pheno(self,evt):
        self.db.save_nome(self.pheno)
        
    def load_pool(self):
        self.db.load_all_nomes()

  
if __name__ == "__main__":
    
    #random.seed(0)
    print random.getstate()
    
    srate=ga.srate
    client=gaclient.Client(debug=False,srate=srate)
     
    app = wx.PySimpleApp()
    mainFrame = MyFrame(None, title='PYO-GA', pos=(50,50), size=(800,300))
    mainFrame.Show()
    app.MainLoop()
