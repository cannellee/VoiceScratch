import wx
import threading
import queue
import time
import re
from math import pi

results_list=[]
command_class_list=[]

###############################################################################
# Command display panel
###############################################################################

class CommandsPanel(wx.Panel):
    def __init__(self, parent):   #ici on initialise les variables, on y touche pas
        wx.Panel.__init__(self, parent, size=(200,100))

        self._turtle = Turtle()
        self._commands = []

        self._text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY)

        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(self._text, 1, wx.EXPAND)

    def analyseText(self, text):    #analyse du texte + renvoi du span() + coupe du texte
        # search for commands and create them if found
        global results_list
        print("Texte : ", text)
        for command_class in command_class_list:
            cmd=command_class()
            #print(cmd.word_reference(text))
            result_func=cmd.word_reference(text)
            if result_func!=None:   #si on a une correspondance,
                results_list.append((cmd, result_func))
            else:  #si c'est None
                pass
            
        if len(results_list)==0: #aucune commande n'est exécuté
            pass #on fait rien
        else: #si une commande s'est reconnue
            results_list.sort(key=lambda x: x[1])
            print("La liste - départ - triée :", results_list)
            for cmd, span in results_list:
                self._addCommand(cmd)
            text=text[span[1]:]    #on coupe la partie comprise du texte
            results_list.clear()
                    
        # return number of created commands and text which is not part of a command
        self._refreshCommandDisplay()
        return 0, text

    def getTurtlePosition(self):
        return self._turtle.getPosition()

    def setTurtlePosition(self, pos):
        self._turtle.setPosition(pos)

    def haveCommands(self):
        return len(self._commands) > 0

    def _addCommand(self, cmd):
        self._commands.append(cmd)

    def _refreshCommandDisplay(self):
        self._text.SetValue('\n'.join([cmd.getText() for cmd in self._commands]))

    def executeCommands(self, gc):
        for cmd in self._commands :
            cmd.execute(gc, self._turtle)

        # draw the turtle
        self._drawTurtle(gc)

    def _drawTurtle(self, gc):
        self._turtle.draw(gc)




###############################################################################
# The Turtle
###############################################################################

class Turtle :
    def __init__(self):
        self._position = (0, 0)
        self._size = 8

    def getPosition(self):
        return self._position

    def setPosition(self, pos):
        self._position = pos

    def draw(self, gc):
        # draw the Turtle
        # basicaly a triangle pointing in the current direction
        tx, ty = self._position

        path = gc.CreatePath()
        path.AddRectangle(tx, ty, 0.5, 0.5)
        path.MoveToPoint(tx - self._size, ty - 10)
        path.AddLineToPoint(tx + self._size, ty)
        path.AddLineToPoint(tx - self._size, ty + 10)
        path.CloseSubpath()

        gc.StrokePath(path)




###############################################################################
# Commands
###############################################################################

class TurtleCommand :
    def __init__(self):
        pass

    def getText(self):
        return 'not implemented'

    def execute(self, gc, turtle):
        # for more info about "gc" see:
        # https://docs.wxpython.org/wx.GraphicsContext.html#wx-graphicscontext
        pass
    
############################### --> AVANCER <-- ###############################
class MoveForward(TurtleCommand):
    def __init__(self):
        TurtleCommand.__init__(self)
        self._length = 1
        
    def getText(self):
        return "Avancer : %d" % self._length
        
    def word_reference(self, text):
        match_moveForward=re.search("av[ae]ncer? \D*(\d+)", text, re.IGNORECASE)
        
        if match_moveForward!=None:
            self._length=int(match_moveForward.group(1))
            return match_moveForward.span()
        else:
            return None #passe à quelqu'un d'autre
        return True
    
    def execute(self, gc, turtle):
        tx, ty = turtle.getPosition()
        newx, newy = tx+self._length, ty

        path = gc.CreatePath()
        path.MoveToPoint(tx, ty)
        path.AddLineToPoint(newx, newy)
        gc.StrokePath(path)

        turtle.setPosition((newx, newy))   ###pas oublier !!

command_class_list.append(MoveForward)

############################### --> TOURNER A GAUCHE <-- ###############################
class TurnLeft(TurtleCommand):
    def __init__(self):
        TurtleCommand.__init__(self)
        self._angle = 90
        
    def getText(self):
        return "Tourner à gauche : %d" % self._angle
        
    def word_reference(self, text):
        match_TurnLeft=re.search("tourn[ea][zr]?\W.*gauche\D*(\d+)?°?", text, re.IGNORECASE)
        
        if match_TurnLeft!=None:
            self._angle=int(match_TurnLeft.group(1)) if match_TurnLeft.group(1) else 90
            return match_TurnLeft.span()
        else:
            return None #passe à quelqu'un d'autre
        return True
    
    def execute(self, gc, turtle):
        # rotate in radian
        tx, ty = turtle.getPosition()
        rad_angle = (-self._angle)*(pi/180)

        # rotate the drawing using the transformation matrix
        matrix = gc.GetTransform()
        matrix.Rotate(rad_angle)
        gc.SetTransform(matrix)
        # use another matrix to compute the new turtle position in the rotated canvas
        idMat = gc.CreateMatrix()
        idMat.Rotate(rad_angle)
        idMat.Invert()
        newx, newy = idMat.TransformPoint(tx, ty)
        # update turtle position
        turtle.setPosition((newx, newy))

command_class_list.append(TurnLeft)

############################### --> TOURNER A DROITE <-- ###############################
class TurnRight(TurtleCommand):
    def __init__(self):
        TurtleCommand.__init__(self)
        self._angle = 0
        
    def getText(self):
        return "Tourner à droite : %d" % self._angle
        
    def word_reference(self, text):
        match_TurnRight=re.search("tourn[ea][zr]?\W.*droite\D*(\d+)?°?", text, re.IGNORECASE)
        
        if match_TurnRight!=None:
            self._angle=int(match_TurnRight.group(1)) if match_TurnRight.group(1) else 90
            return match_TurnRight.span()
        else:
            return None #passe à quelqu'un d'autre
        return True
    
    def execute(self, gc, turtle):
        # rotate in radian
        tx, ty = turtle.getPosition()
        rad_angle = self._angle*(pi/180)

        # rotate the drawing using the transformation matrix
        matrix = gc.GetTransform()
        matrix.Rotate(rad_angle)
        gc.SetTransform(matrix)
        # use another matrix to compute the new turtle position in the rotated canvas
        idMat = gc.CreateMatrix()
        idMat.Rotate(rad_angle)
        idMat.Invert()
        newx, newy = idMat.TransformPoint(tx, ty)
        # update turtle position
        turtle.setPosition((newx, newy))

command_class_list.append(TurnRight)

###################### --> ANNULER DERNIERE COMMANDE <-- ######################
class Undo(TurtleCommand):
    def __init__(self):
        TurtleCommand.__init__(self)
        
    def getText(self):
        return "Annuler la dernière commande"
        
    def word_reference(self, text):
        match_Undo=re.search("ann?ul.?", text, re.IGNORECASE)
        
        if match_Undo!=None:
            return True  #ici on peut pas renvoyer le span car il n'y en a pas (=> on a pas de group car pas d'info en plus)
        else:
            return None #passe à quelqu'un d'autre
        return True
    
    def execute(self, gc, turtle):
        pass

command_class_list.append(Undo)

####################### --> SUPPRIMER LES COMMANDES <-- #######################
class DeleteAllCommands(TurtleCommand):
    def __init__(self):
        TurtleCommand.__init__(self)
        
    def getText(self):
        return "Supprimer toutes les commandes"
        
    def word_reference(self, text):
        match_DeleteAllCommands=re.search("supprim.?", text, re.IGNORECASE)
        
        if match_DeleteAllCommands!=None:
            return True  #ici on peut pas renvoyer le span car il n'y en a pas (=> on a pas de group car pas d'info en plus)
        else:
            return None #passe à quelqu'un d'autre
        return True
    
    def execute(self, gc, turtle):
        pass

command_class_list.append(DeleteAllCommands)

############################### --> RECULER <-- ###############################
class MoveBackward(TurtleCommand):
    def __init__(self):
        TurtleCommand.__init__(self)
        self._length = 1
        
    def getText(self):
        return "Reculer : %d" % self._length
        
    def word_reference(self, text):
        match_MoveBackward=re.search("recul.? \D*?(\d+)", text, re.IGNORECASE)
        
        if match_MoveBackward!=None:
            self._length=int(match_MoveBackward.group(1))
            return match_MoveBackward.span()
        else:
            return None #passe à quelqu'un d'autre
        return True
    
    def execute(self, gc, turtle):
        tx, ty = turtle.getPosition()
        newx, newy = tx-self._length, ty
        
        path = gc.CreatePath()
        path.MoveToPoint(tx, ty)
        path.AddLineToPoint(newx, newy)
        gc.StrokePath(path)
        
        turtle.setPosition((newx, newy))   ###pas oublier !!

command_class_list.append(MoveBackward)