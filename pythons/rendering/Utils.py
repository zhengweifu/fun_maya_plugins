import maya.cmds as cmds
import os

class Utils(object):
    Instance = None

    def __init__(self):
        pass

    def changeFilePath(self, path, forceDel = False, ext = None):
        files = cmds.ls(type='file')
        for f in files:
            oldPath = cmds.getAttr('%s.fileTextureName'%f).replace('\\', '/')
            if ext:
                mSplit = os.path.splitext(oldPath)
                if len(mSplit) > 0:
                   oldPath = mSplit[0] + ext
            name = os.path.basename(oldPath)
            newPath = os.path.join(path, name)
            if os.path.isfile(newPath):
                cmds.setAttr('%s.fileTextureName'%f, newPath, type="string")
            else:
                if forceDel:
                    cmds.delete(f)
                print "Not found %s"%newPath

    @staticmethod
    def create():
        Utils.Instance = Utils()
        return Utils.Instance

if __name__ == "__main__":
    Utils.create().changeFilePath("/Users/zwf/Documents/zwf/templates/yinpian_2018-6-6/textures_jpg", True, ".jpg")
