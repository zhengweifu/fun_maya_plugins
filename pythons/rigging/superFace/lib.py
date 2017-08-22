from maya.cmds import *

class lib:
    def __init__(self):
        self.path = ''
        self.file = ''
        
    def setPath(self, p):
        self.path = p
        
    def setFile(self, f):
        self.file = f
        
    def setGroup(self, g):
        self.group = g
        
    def load(self):
        fullPath = self.path + '/' + self.file + '.mel'
        string = 'source ' + '"' + fullPath + '";' + self.file
        #print string
        import maya.mel as mm
        self.ctrlRootGrp = mm.eval(string)
        self.selObj = ls(sl=1)

    def moveToGroup(self):
        #print self.ctrlRootGrp
        #print self.group
        #print 'move to group'
        try:
            import maya.cmds as mc
            mc.parent(self.ctrlRootGrp, self.group, r=1)
        except:
            pass
        select(self.selObj)
    def libList(self):
        import os
        list = os.listdir(self.path)
        for i in range(len(list)):
                       list[i] = list[i].split('.')[0]
        return list
'''
obj = lib()
obj.setPath(g.ROOT_CTRL_LIB_PATH)
obj.setFile(item)
obj.load()
'''