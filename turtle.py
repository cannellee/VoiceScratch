import wx
from wx.lib.agw import aui
from audioa import TranscriptPanel
from commands import CommandsPanel
from tcanvas import TurtleCanvas

# create The wxApp instance
TheApp = wx.App(redirect=False)

# Main window definition
class TurtleMainFrame(wx.Frame):
    def __init__(self):    #ici on initialise les variables, on y touche pas
        wx.Frame.__init__(self, None, title='Turtle voice', size=(1024,768))

        self._mgr = aui.AuiManager(self)
        self._transcriptPanel = TranscriptPanel(self)
        self._commandsPanel = CommandsPanel(self)
        self._tcanvas = TurtleCanvas(self, self._commandsPanel)

        self._mgr.AddPane(self._transcriptPanel, aui.AuiPaneInfo().Caption('Transcript').Bottom())
        self._mgr.AddPane(self._commandsPanel, aui.AuiPaneInfo().Caption('Commands').Right())
        self._mgr.AddPane(self._tcanvas, aui.AuiPaneInfo().Caption('Canvas').Center())
        self._mgr.Update()

        self._transcriptPanel.Bind(wx.EVT_TEXT, self.onTextUpdate)
        self._tcanvas.Bind(wx.EVT_SIZE, self.onCanvasSize)
        
    def onTextUpdate(self, event): #On récupère le texte, on appelle l'analyse
        # new text is available
        # --> analyse it
        text = self._transcriptPanel.getText()
        a_t=self._commandsPanel.analyseText(text)
        self._transcriptPanel.setText(a_t[1])
        self._tcanvas.Refresh()
        
    def onCanvasSize(self, event): #Création du canva, ne pas toucher (je crois)
        canvasRect = self._tcanvas.GetClientRect()
        w, h = canvasRect.GetSize()

        # Init the Turtle position
        if not self._commandsPanel.haveCommands() :
            self._commandsPanel.setTurtlePosition((w/2, h/2))
            self._tcanvas.Refresh()

        event.Skip()


# The application begin here
win = TurtleMainFrame()
win.Show()

# Run main infinite loop
TheApp.MainLoop()
