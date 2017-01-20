# -*- coding: utf-8 -*-
# 
import maya.cmds as cmds
import maya.mel as mel

class Volume :
    def __init__(self):
        self.ui()

    '''ui part'''
    def ui(self):
        window_name = "VOLUME_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        window = cmds.window(window_name, title="Volume Tool", widthHeight=(500, 200))
        cmds.columnLayout(adj = True)
        cmds.gridLayout( numberOfColumns = 2, cellWidth = 150)
        cmds.text( label=u'体积:', align='left' )
        self.Mvolume = cmds.text( label=u'', align='left' )
        cmds.text( label=u'925 银重量:', align='left' )
        self.yingG = cmds.text( label=u'', align='left' )
        cmds.text( label=u'18k 金重量:', align='left' )
        self.jin18kG = cmds.text( label=u'', align='left' )
        cmds.text( label=u'24k 金重量:', align='left' )
        self.jin24kG = cmds.text( label=u'', align='left' )
        cmds.setParent('..');
        cmds.button( label=u'计算', c = self.compute)
        cmds.showWindow(window)

    def compute(self, argas):
        v = mel.eval('computePolysetVolume')
        cmds.text(self.Mvolume, e = True, label = u'%0.5f 立方厘米'%v)
        cmds.text(self.yingG, e = True, label = u'%0.5f 克'%(10.35 * v) )
        cmds.text(self.jin18kG, e = True, label = u'%0.5f 克'%(16.65 * v))
        cmds.text(self.jin24kG, e = True, label = u'%0.5f 克'%(19.3 * v))

def main():
    vm = Volume();

if __name__ == '__main__':
    main()