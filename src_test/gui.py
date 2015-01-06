import wx


class MyFrame(wx.Frame):
        
    def __init__(self, parent, title, size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, wx.DefaultPosition, size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.x=1
      
    def OnPaint(self, evt):
        print "hello"
        self.dc=wx.PaintDC(self)
        self.dc.BeginDrawing()
        self.dc.DrawLine(self.x,0,self.x+100,100)
        self.dc.EndDrawing()
        self.x += 1
        print "Hello2"
  
  
app = wx.PySimpleApp()
mainFrame = MyFrame(None,"MyApp")
mainFrame.Show()
app.MainLoop()