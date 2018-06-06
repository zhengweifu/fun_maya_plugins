import maya.cmds as cmds
import os

class Utils(object):
    Instance = None

    def __init__(self):
        pass

    def changeFilePath(self, path):
        files = cmds.ls(type='file')
        for f in files:
            oldPath = cmds.getAttr('%s.fileTextureName'%f)
            name = os.path.basename(oldPath)
            newPath = os.path.join(path, name)
            if os.path.isfile(newPath):
                cmds.setAttr('%s.fileTextureName'%f, newPath, type="string")
            else:
                print "Not found %s"%newPath

    @staticmethod
    def create():
        Utils.Instance = Utils()
        return Utils.Instance

if __name__ == "__main__":
    Utils.create().changeFilePath("E:/BaiduNetdiskDownload/yinpian/textures")
