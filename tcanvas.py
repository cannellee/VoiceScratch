import wx


###############################################################################
# Command display panel
###############################################################################

class TurtleCanvas(wx.Panel):
    def __init__(self, parent, commandsPanel):
        wx.Panel.__init__(self, parent)

        self._commandsPanel = commandsPanel

        self.Bind(wx.EVT_PAINT, self.onPaint)

    def onPaint(self, event):
        # Paint event
        # execute all commands in sequence

        # Create graphics context
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if gc :
            # default bkg color and pen
            gc.SetBrush(wx.WHITE_BRUSH)
            gc.SetPen(wx.BLACK_PEN)

            # execute commands
            self._commandsPanel.executeCommands(gc)


###############################################################################
# Commands
###############################################################################

class TurtleCommand :
    def __init__(self):
        pass

    def getText(self):
        return 'not implemented'

    def execute(self, dc):
        pass
