# -*- coding: utf-8 -*-
import maya.api.OpenMaya as nm
import maya.OpenMaya as om
import maya.cmds as cmds
import struct

class MeshFileManager(object):
    '''初始化方法'''
    def __init__(self):
        self.out_uv = True
        self.out_normal = True
        self.init()

    def init(self):
        self.uvs = []
        self.vertices = []
        self.normals = []
        self.faces = []


    '''读并解析文件方法'''
    def readDatas(self, meshPath):
        f = open(meshPath, "rb")
        try:
            point = 0
            uvLayers = struct.unpack('B', f.read(1))[0]
            point += 1
            
            uv_counts = []
            for uvLayer in range(uvLayers):
                f.seek(point, 0)
                
                uv_counts.append(struct.unpack('I', f.read(4))[0])
                point += 4

            f.seek(point, 0)
            normal_count = struct.unpack('I', f.read(4))[0]
            point += 4

            f.seek(point, 0)
            vertex_count = struct.unpack('I', f.read(4))[0]
            point += 4

            f.seek(point, 0)
            face_infos = struct.unpack('I', f.read(4))[0]
            point += 4

            # uvs
            for i in uv_counts:
                uv = {'u' : [], 'v' : []}
                for j in range(i * 2):
                    f.seek(point, 0)
                    if not (j % 2):
                        uv['u'].append(struct.unpack('f', f.read(4))[0])
                    else:
                        uv['v'].append(struct.unpack('f', f.read(4))[0])
                    point += 4
                if uv['u'] and uv['v'] and len(uv['u']) == len(uv['v']):
                    self.uvs.append(uv)

            # normals
            for i in range(0, normal_count * 3, 3):
                f.seek(point, 0)
                self.normals.append(nm.MVector(struct.unpack('fff', f.read(12))).normal())
                point += 12

            # vertices
            for i in range(0, vertex_count * 3, 3):
                f.seek(point, 0)
                self.vertices.append(nm.MPoint(struct.unpack('fff', f.read(12))))
                point += 12

            # faces
            for i in range(face_infos):
                f.seek(point, 0)
                self.faces.append(struct.unpack('I', f.read(4))[0])
                point += 4

        finally:
            f.close()

    def getFaceType(self, isTriangle, hasMaterial, hasFaceUvs, hasFaceVertexUvs, hasFaceNormals, hasFaceVertexNormals, hasFaceColors, hasFaceVertexColors):
        faceType = 0
        faceType = self.setBit(faceType, 0, not isTriangle)
        faceType = self.setBit(faceType, 1, hasMaterial)
        faceType = self.setBit(faceType, 2, hasFaceUvs)
        faceType = self.setBit(faceType, 3, hasFaceVertexUvs)
        faceType = self.setBit(faceType, 4, hasFaceNormals)
        faceType = self.setBit(faceType, 5, hasFaceVertexNormals)
        faceType = self.setBit(faceType, 6, hasFaceColors)
        faceType = self.setBit(faceType, 7, hasFaceVertexColors)
        return faceType

    def setBit(self, value, position, on):
        if on:
            mask = 1 << position
            return (value | mask)
        else:
            mask = ~(1 << position)
            return (value & mask)

    def isBitSet(self, value, position):
        return value & (1 << position)  

    '''在maya中生成模型方法'''
    def createMesh(self, meshPath):
        self.readDatas(meshPath)
        polygon_counts = []
        polygon_connects = []
        uv_counts = []
        uvs_ids = []
        normal_connects = []
        if self.faces:
            offset = 0
            while offset<len(self.faces):
                _type = self.faces[offset];
                isTriangle = not self.isBitSet(_type, 0)
                hasMaterial = self.isBitSet(_type, 1)
                hasFaceVertexUv = self.isBitSet(_type, 3)
                hasFaceNormal = self.isBitSet(_type, 4)
                hasFaceVertexNormal = self.isBitSet(_type, 5)
                hasFaceColor = self.isBitSet(_type, 6)
                hasFaceVertexColor = self.isBitSet(_type, 7)
                offset += 1
                if isTriangle:
                    polygon_counts.append(3)
                    polygon_connects.extend([self.faces[offset], self.faces[offset+1], self.faces[offset+2]])
                    offset += 3

                    if hasMaterial:
                        offset += 1

                    if self.uvs:
                        if hasFaceVertexUv:
                            uv_counts.append(3)
                            for _uv in range(len(self.uvs)):
                                try:
                                    uvs_ids[_uv]
                                except:
                                    uvs_ids.append([])
                                for i in range(3):
                                    uvs_ids[_uv].append(self.faces[offset])
                                    offset += 1
                    if hasFaceNormal:
                        offset += 1

                    if hasFaceVertexNormal:
                        normal_connects.extend([self.faces[offset], self.faces[offset+1], self.faces[offset+2]])
                        offset += 3

                    if hasFaceColor:
                        offset += 1

                    if hasFaceVertexColor:
                        for i in range(3):
                            offset += 1

        if self.vertices and polygon_counts and polygon_connects:
            # new MFnMesh class
            m = nm.MFnMesh()

            # set some datas for MFnMesh
            m.create(self.vertices, polygon_counts, polygon_connects)
            
            # add material (default material)
            cmds.sets(m.name(), e=True, forceElement="initialShadingGroup")

            # set UV for Mesh
            if self.uvs:
                for e in range(len(self.uvs)):
                    # create uvset names
                    uv_name = "map%d"%(e+1)
                    if uv_name not in m.getUVSetNames():
                        m.createUVSet(uv_name)
                    m.setUVs(self.uvs[e]['u'], self.uvs[e]['v'], uv_name)
                    m.assignUVs(uv_counts, uvs_ids[e], uv_name)
            # set Normal for Mesh
            if self.normals:
                _faceIds = [] # polygon/face id list
                _normals = [] # polygon/face each vertex normal
                for faceId in range(m.numPolygons):
                    for fvid in range(3):
                        _faceIds.append(faceId)
                        vid = faceId*3+fvid
                        norm = self.normals[normal_connects[vid]] # get normal
                        _normals.append(norm)
                m.setFaceVertexNormals(_normals, _faceIds, polygon_connects)

    '''从maya中得到数据(vertices, uvs, normals, faces, ...)方法''' 
    def setDatas(self, dagPath):
        isTriangle = True
        hasMaterial = False
        hasFaceUvs = False
        hasFaceVertexUvs = False
        hasFaceNormals = False
        hasFaceVertexNormals = False
        hasFaceColors = False
        hasFaceVertexColors = False

        vertex_offset = len(self.vertices) / 3
        normal_offset = len(self.normals) / 3
        uv_offset_list = [0, 0]
        for uv_index in range(len(self.uvs)):
            uv_offset_list[uv_index] = len(self.uvs[uv_index]) / 2

        fnMesh = om.MFnMesh(dagPath);
        # vertice
        vertexIterator = om.MItMeshVertex(dagPath)

        while not vertexIterator.isDone():

            p = vertexIterator.position(om.MSpace.kWorld)

            self.vertices.extend([p.x, p.y, p.z])

            vertexIterator.next()

        if fnMesh.numUVs()>0 and self.out_uv:
            hasFaceVertexUvs = True

        if fnMesh.numNormals()>0 and self.out_normal:
            hasFaceVertexNormals = True

        # uvs
        uvsetNames = []
        fnMesh.getUVSetNames(uvsetNames)

        _index = 0

        if hasFaceVertexUvs:
            for uvsetName in uvsetNames:
                uArray = om.MFloatArray()
                vArray = om.MFloatArray()
                fnMesh.getUVs(uArray, vArray, uvsetName)

                uvLength = uArray.length()
                if len(self.uvs) <= _index:
                    self.uvs.append([])
                
                for euv_idx in range(uvLength):
                    self.uvs[_index].extend([uArray[euv_idx], vArray[euv_idx]])

                _index += 1

        # normals
        if hasFaceVertexNormals:
            normals = om.MFloatVectorArray()

            fnMesh.getNormals(normals, om.MSpace.kWorld)

            normalLength = normals.length();

            for enormal_idx in range(normalLength):

                self.normals.extend([normals[enormal_idx].x, normals[enormal_idx].y, normals[enormal_idx].z])


        # Get shader index of face
        _shaders = om.MObjectArray()
        _faceIndices = om.MIntArray()
        fnMesh.getConnectedShaders(0, _shaders, _faceIndices)
        # print _faceIndices

        faceType = self.getFaceType(isTriangle, hasMaterial, hasFaceUvs, hasFaceVertexUvs, hasFaceNormals, hasFaceVertexNormals, hasFaceColors, hasFaceVertexColors)

        # face info
        faceIndex = 0
        polyonIterator = om.MItMeshPolygon(dagPath)
        while not polyonIterator.isDone():
            polygonVertexCount = polyonIterator.polygonVertexCount()
            shaderIndex = _faceIndices[faceIndex]
            for vtx in range(polygonVertexCount):
                if vtx < polygonVertexCount - 2:
                    vtx += 1
                    if shaderIndex > 0:
                        hasMaterial = True
                        faceType = self.getFaceType(isTriangle, hasMaterial, hasFaceUvs, hasFaceVertexUvs, hasFaceNormals, hasFaceVertexNormals, hasFaceColors, hasFaceVertexColors)
                    face = [faceType]
                    if shaderIndex > 0:
                        face.append(shaderIndex)
                    face.extend([polyonIterator.vertexIndex(0)+vertex_offset, polyonIterator.vertexIndex(vtx)+vertex_offset, polyonIterator.vertexIndex(vtx+1)+vertex_offset])
                    if hasFaceVertexUvs:
                        _index = 0
                        for uvsetName in uvsetNames:
                            util = om.MScriptUtil(0)
                            uv_idx = util.asIntPtr();
                            polyonIterator.getUVIndex(0, uv_idx, uvsetName)
                            face.append(util.getInt(uv_idx)+uv_offset_list[_index])
                            polyonIterator.getUVIndex(vtx, uv_idx, uvsetName)
                            face.append(util.getInt(uv_idx)+uv_offset_list[_index])
                            polyonIterator.getUVIndex(vtx+1, uv_idx, uvsetName)
                            face.append(util.getInt(uv_idx)+uv_offset_list[_index])
                            _index += 1
                    if hasFaceVertexNormals:
                        face.extend([polyonIterator.normalIndex(0)+normal_offset, polyonIterator.normalIndex(vtx)+normal_offset, polyonIterator.normalIndex(vtx+1)+normal_offset])
                    self.faces.extend(face);
            polyonIterator.next()
            faceIndex += 1
        # print "vertices", self.vertices
        # print "normals", self.normals
        # print "uvs", self.uvs
        # print "faces", self.faces

    '''输出保存文件'''
    def write(self, outMeshPath):

        # defined head
        uid = 0                 #unsigned int  => I
        uv_layers = 0           #unsigned char  => B
        uv_counts = []          #[unsigned int  => I ...] ,一组两个
        normals_count = 0     #unsigned int  => I ,一组三个
        vertices_count = 0    #unsigned int  => I ,一组三个
        face_infos = 0        #unsigned char  => I
        
        # uv
        uv_layers = len(self.uvs)
        for single in self.uvs:
            uv_counts.append(len(single) / 2)
        #normal
        normals_count = len(self.normals) / 3
        
        # vertex
        vertices_count = len(self.vertices) / 3
        
        #face
        face_infos = len(self.faces)
        
        f = open(outMeshPath, "wb")
        
        try:
            #f.write(struct.pack("I", uid))
            
            f.write(struct.pack("B", uv_layers))
            for uvc in uv_counts:
                f.write(struct.pack("I", uvc))

            f.write(struct.pack("I", normals_count))
            
            f.write(struct.pack("I", vertices_count))
            
            f.write(struct.pack("I", face_infos))
            
            for uv in self.uvs:
                for uve in uv:
                    f.write(struct.pack("f", uve))
            
            for n in self.normals:
                f.write(struct.pack("f", n))
                
            for v in self.vertices:
                f.write(struct.pack("f", v))
                
            # write faces info
            for face in self.faces:
                if face == -1: #一般是没有uv或者法线
                    face = 0
                f.write(struct.pack("I", face))
                
        finally:
            f.close()

    '''输出保存所有的mesh文件'''
    def writeAll(self):
        self.init()

        dagIterator = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kInvalid);

        while not dagIterator.isDone():
            dagPath = om.MDagPath()
            dagIterator.getPath(dagPath)
            dagNode = om.MFnDagNode(dagPath)

            dagIterator.next() # iterator 跳到下一个

            if dagNode.isIntermediateObject():
                continue

            if dagPath.hasFn(om.MFn.kNurbsSurface) and dagPath.hasFn(om.MFn.kTransform):
                print "Warning: skipping Nurbs Surface.\n"

            elif dagPath.hasFn(om.MFn.kMesh) and dagPath.hasFn(om.MFn.kTransform):
                continue

            elif dagPath.hasFn(om.MFn.kMesh):
                self.setDatas(dagPath)

    '''输出保存被选中的mesh文件'''
    def writeSelected(self):
        selected = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selected)
        selectionIterator = om.MItSelectionList(selected)

        if selectionIterator.isDone():
            print "Error: Nothing is selectionIterator.\n"
            return

        while not selectionIterator.isDone():
            dagPath = om.MDagPath()
            selectionIterator.getDagPath(dagPath)
            dagNode = om.MFnDagNode(dagPath)
            # print dagPath.hasFn(om.MFn.kTransform), dagPath.hasFn(om.MFn.kMesh)
            selectionIterator.next() # iterator 跳到下一个

            if dagNode.isIntermediateObject():
                continue

            if dagPath.hasFn(om.MFn.kNurbsSurface) and dagPath.hasFn(om.MFn.kTransform):
                print "Warning: skipping Nurbs Surface.\n"

            #elif dagPath.hasFn(om.MFn.kMesh) and dagPath.hasFn(om.MFn.kTransform):
                #continue

            elif dagPath.hasFn(om.MFn.kMesh):
                self.setDatas(dagPath)


    '''ui part'''
    def ui(self):
        window_name = "MESH_FILE_MANAGER_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        
        window = cmds.window(window_name, title="Project File Manager", widthHeight=(300, 500))
        cmds.columnLayout(adj=True)
        tabs = cmds.tabLayout()
        import_column = cmds.columnLayout(adj=True)
        cmds.button(label="import mesh", c=self._import)
        cmds.setParent('..')
        export_column = cmds.columnLayout(adj=True)
        self.uv_cb = cmds.checkBox(label='export uvs', value=True)
        self.normal_cb = cmds.checkBox(label='export normals', value=True)
        cmds.button(label="export all meshes", c=self._exportAll)
        cmds.button(label="export selected meshes", c=self._exportSelected)
        cmds.setParent('..')
        cmds.tabLayout(tabs, edit=True, tabLabel=((import_column, "Import"), (export_column, "Export")))
        cmds.showWindow(window)

    def _import(self, argas):
        multipleFilters = "Mesh (*.mesh)"
        mesh_paths = cmds.fileDialog2(fileFilter=multipleFilters, fm=1, dialogStyle=2)
        if(mesh_paths):
            for mesh_path in mesh_paths:
                self.createMesh(mesh_path)
                self.init()

    def _exportAll(self, argas):
        mesh_paths = self._export()
        if mesh_paths:
            self.writeAll()
            self.write(mesh_paths[0])
            self.init()

    def _exportSelected(self, argas):
        mesh_paths = self._export()
        if mesh_paths:
            self.writeSelected()
            self.write(mesh_paths[0])
            self.init()

    def _exportProject(self, argas):
        project_paths = self._export("Project (*.project)")
        if project_paths:
            self.writeAll()
            print self.setDatas
            self.init()

    def _export(self, filter = "Mesh (*.mesh)"):
        paths = cmds.fileDialog2(fileFilter=filter, dialogStyle=2)
        self.out_uv = cmds.checkBox(self.uv_cb, q = True, v=True)
        self.out_normal = cmds.checkBox(self.normal_cb, q = True, v=True)
        return paths

def main():
    mfm = MeshFileManager();
    mfm.ui()

if __name__ == '__main__':
    main();