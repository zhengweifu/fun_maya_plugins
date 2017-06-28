# -*- coding: utf-8 -*-
import maya.api.OpenMaya as nm
import maya.OpenMaya as om
import maya.cmds as cmds
import struct, re

class StlFileManager(object):
    def __init__(self):
        self.init()

    def init(self):
        self.vertices = []
        self.normals = []
        self.polygonCounts = []
        self.polygonConnects = []

    def read(self, stlPath):
        self._getData(stlPath)
        if self.vertices and self.polygonCounts and self.polygonConnects:
            # new MFnMesh class
            m = nm.MFnMesh()
            
            # set some datas for MFnMesh
            m.create(self.vertices, self.polygonCounts, self.polygonConnects)

            _name = m.name()
            
            # add material (default material)
            cmds.sets(_name, e=True, forceElement="initialShadingGroup")

            cmds.polyMergeVertex(_name, d = 0.00001, am = 1, ch = 1)

            cmds.select(_name, r = True)

    def write(self, stlPath):
        f = open(stlPath, "wb")
        f.seek(80)
        try:
            _faceCount = len(self.normals)
            print _faceCount
            f.write(struct.pack("I", _faceCount))
            for index in range(_faceCount):
                _normal = self.normals[index]
                _vertices = self.vertices[index]
                for _en in _normal:
                    f.write(struct.pack("f", _en))
                for _ev in _vertices:
                    f.write(struct.pack("f", _ev))
                f.write(struct.pack("H", 0))
        finally:
            f.close()

    '''读并解析文件方法'''
    def _getData(self, stlPath):
        f = open(stlPath, "rb")
        try:
            f.seek(80)
            _faceCount = struct.unpack('I', f.read(4))[0]
            _index = 0
            while _index < _faceCount:
                f.seek(12, 1)

                self.vertices.append(nm.MPoint(struct.unpack('fff', f.read(12))))
                self.vertices.append(nm.MPoint(struct.unpack('fff', f.read(12))))
                self.vertices.append(nm.MPoint(struct.unpack('fff', f.read(12))))

                self.polygonCounts.append(3)

                self.polygonConnects.extend([_index * 3, _index * 3 + 1, _index * 3 + 2])

                f.seek(2, 1)

                _index += 1
        finally:
            f.close()

    def _setData(self, meshName):
        needToTriangle = False
        faceCount = cmds.polyEvaluate(meshName, f = True)
        faceTriCount = cmds.polyEvaluate(meshName, t = True)

        if faceCount != faceTriCount:
            needToTriangle = True
            cmds.polyTriangulate(meshName)
            faceCount = cmds.polyEvaluate(meshName, f = True)
        # file.write(struct.pack("I", faceCount))
        for faceIndex in range(faceCount):
            currentFace = '%s.f[%d]'%(meshName, faceIndex)
            currentNormalsString = cmds.polyInfo(currentFace, fn = True)[0].split(' \n')[0]
            currentIndicesString = cmds.polyInfo(currentFace, fv = True)[0].split(' \n')[0]
            currentNormals = re.sub(r'\s+', ':', re.sub(r':(\s+)', ':', currentNormalsString).split(':')[1]).split(':')
            currentIndices = re.sub(r'\s+', ':', re.sub(r':(\s+)', ':', currentIndicesString).split(':')[1]).split(':')
            self.normals.append([float(currentNormals[0]), float(currentNormals[1]), float(currentNormals[2])])
            _vertices = []
            for index in currentIndices:
                _pos =  cmds.pointPosition('%s.vtx[%s]'%(meshName, index), w = True)
                _vertices.extend(_pos)
            self.vertices.append(_vertices)
        if needToTriangle:
            cmds.polyQuad(meshName)

    '''ui part'''
    def ui(self):
        window_name = "STL_FILE_MANAGER_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        
        window = cmds.window(window_name, title="Stl File Manager", widthHeight=(300, 200))
        cmds.columnLayout(adj = True)
        tabs = cmds.tabLayout()
        import_column = cmds.columnLayout(adj = True)
        cmds.button(label="import stl file", c = self._import)
        cmds.setParent('..')
        export_column = cmds.columnLayout(adj = True)
        cmds.button(label="export all", c = self._exportAll)
        cmds.button(label="export selected", c = self._exportSelected)
        cmds.setParent('..')
        cmds.tabLayout(tabs, edit=True, tabLabel=((import_column, "Import"), (export_column, "Export")))
        cmds.showWindow(window)

    def _import(self, argas):
        multipleFilters = "Stl (*.stl)"
        stl_paths = cmds.fileDialog2(fileFilter=multipleFilters, fm=1, dialogStyle=2)
        if(stl_paths):
            for stl_path in stl_paths:
                self.read(stl_path)


    def _export(self, filter = "Stl (*.stl)"):
        paths = cmds.fileDialog2(fileFilter=filter, dialogStyle=2)
        return paths

    def _exportAll(self, argas):
        stl_paths = self._export()
        if stl_paths:
            _meshes = cmds.ls(type = 'mesh')
            for _mesh in _meshes:
                self._setData(_mesh);
            self.write(stl_paths[0])
            self.init()

    def _exportSelected(self, argas):
        stl_paths = self._export()
        if stl_paths:
            _meshes = cmds.ls(type = 'mesh', sl = True)
            for _mesh in _meshes:
                self._setData(_mesh);
            self.write(stl_paths[0])
            self.init()

def main():
    sfm = StlFileManager();
    # sfm.write('d:/testrer.stl') 
    sfm.ui()

if __name__ == '__main__':
    main()