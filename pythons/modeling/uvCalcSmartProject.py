# -*- coding: utf-8 -*-
# 
import maya.cmds as cmds
import pymel.core as pc

class ThickFace(object):
    def __init__(self, face):
        self.normal = face.getNormal()
        self.area = face.getArea()

class SmartProjectUV(object):
    def __init__(self, angleLimit = 66, margin = 0.01, areaWeight = 0.0, correntAspect = True, stretchUvBounds = True):
        self.angleLimit = angleLimit
        self.islandMargin = margin
        self.areaWeight = areaWeight
        self.correntAspect = correntAspect
        self.stretchUvBounds = stretchUvBounds
        self.ui()

    def ui(self):
        window_name = "UV_SMART_PROJECT_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        window = cmds.window(window_name, title="UV Smart Project", widthHeight=(300, 200))
        cmds.columnLayout(adj = True)
        cmds.gridLayout( numberOfColumns = 2, cellWidth = 150)
        cmds.text( label='Angle Limit', align='left' )
        self.angleLimit_u = cmds.intField( minValue = 1, maxValue = 89, step = 1, value = self.angleLimit)
        cmds.text( label='Island Margin', align='left' )
        self.islandMargin_u = cmds.floatField( minValue = 0, maxValue = 1, step = 0.01, value = self.islandMargin)
        cmds.text( label='Area Weight', align='left' )
        self.areaWeight_u = cmds.floatField( minValue = 0, maxValue = 1, step = 0.01, value = self.areaWeight)
        self.correntAspect_u = cmds.checkBox( label='Correct Aspect', value = self.correntAspect )
        self.stretchUvBounds_u = cmds.checkBox( label='Stretch To UV Bounds', value = self.stretchUvBounds )
        cmds.setParent('..');
        cmds.button( label='ok', c = self.run)
        cmds.showWindow(window)

    def changeProps(self):
        self.angleLimit = cmds.intField(self.angleLimit_u, q = True, value = True)
        self.islandMargin = cmds.floatField(self.islandMargin_u, q = True, value = True)
        self.areaWeight = cmds.floatField(self.areaWeight_u, q = True, value = True)
        self.correntAspect = cmds.checkBox(self.correntAspect_u, q = True, value = True)
        self.stretchUvBounds = cmds.checkBox(self.stretchUvBounds_u, q = True, value = True)

    def run(self, argas):
        self.changeProps()
        selectMeshes = pc.ls(sl = True, type = "mesh", dag = True)

        for mesh in selectMeshes:
            meshVerts = list(mesh.verts)
            meshFaces = [ThickFace(f) for i, f in enumerate(mesh.faces)]
            meshFaces.sort(key=lambda a: -a.area)

            print meshFaces


def main():
    SmartProjectUV()

if __name__ == "__main__":
    main()