import maya.cmds as mc
import maya.mel as mm
from sfGlobal import *
import sfUI

class main:
    def __init__(self):
        ui = self.start()
        #cmd = 'source "' + g.SCRIPTJOB_FILE + '";' + g.SCRIPTJOB_CMD + '("'+ui+'");';
        #print cmd
        #mm.eval(cmd)

    def start(self):
        win = sfUI.mainUI(g.MAIN_UI)
        win.build()
        win.show()
        return win.win
'''
import superFace as sf
start = sf.main()
'''