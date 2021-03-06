# -*- coding: utf-8 -*-
import maya.api.OpenMaya as nm
import maya.OpenMaya as om
import maya.cmds as cmds
import meshFileManager, common, uuid, time, json, os, shutil, math
import pymel.core as pm
reload(common)
reload(meshFileManager)
class ImportAndExport(object):
    '''初始化方法'''
    def __init__(self):
        self.meshFileManager = meshFileManager.MeshFileManager();
        self.out_uv = True
        self.out_normal = True
        self.init()

    def init(self):
        self.lightmapUUID = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
        self.meshFileManager.out_uv = self.out_uv
        self.meshFileManager.out_normal= self.out_normal
        self.geometries = []
        self.materials = []
        self.materialName2UUID = {}
        self.textures = []
        self.textureName2UUID = {}
        self.faceMaterials = []
        self.objectTree = {'type': 'Group', 'children': []}

    def addNeedAttrs(self, argas):
        mats = cmds.ls(mat = True)
        for mat in mats:
            if not cmds.objExists('%s.side'%mat):
                cmds.addAttr(mat, ln = 'side', at = 'enum', en='front=0:back=1:double=2')
            if not cmds.objExists('%s.aoMap'%mat):
                cmds.addAttr(mat, ln = 'aoMap', at = 'double3')
                cmds.addAttr(mat, ln = 'aoMapR', at = 'double', p = 'aoMap')
                cmds.addAttr(mat, ln = 'aoMapG', at = 'double', p = 'aoMap')
                cmds.addAttr(mat, ln = 'aoMapB', at = 'double', p = 'aoMap')
                cmds.addAttr(mat, ln = "aoMapIntensity", at = 'double', min = 0, max = 1, dv = 1)
            if not cmds.objExists('%s.lightMap'%mat):
                cmds.addAttr(mat, ln = 'lightMap', at = 'double3')
                cmds.addAttr(mat, ln = 'lightMapR', at = 'double', p = 'lightMap')
                cmds.addAttr(mat, ln = 'lightMapG', at = 'double', p = 'lightMap')
                cmds.addAttr(mat, ln = 'lightMapB', at = 'double', p = 'lightMap')
                cmds.addAttr(mat, ln = "lightMapIntensity", at = 'double', min = 0, max = 1, dv = 1)
            
    def intoTexture(self, copyFolder, materialObject, material, srcProp, distProp):
        # print material.attr(srcProp).inputs()
        _inputs = material.attr(srcProp).inputs()
        if len(_inputs) > 0:
            _input = _inputs[0]
            # print _input.type()
            if _input.type() == 'bump2d':
                _cinputs = _input.bumpValue.inputs()
                if len(_cinputs) > 0:
                    if _input.getAttr('bumpInterp') > 0:
                        distProp = 'normalMap'
                    else:
                        materialObject['bumpScale'] = _input.getAttr('bumpDepth')
                        distProp = 'bumpMap'
                    _input = _cinputs[0]
            if _input.type() == 'file':
                _textureUrl = _input.getAttr('fileTextureName')
                if os.path.isfile(_textureUrl):
                    if _input not in self.textureName2UUID:
                        if not os.path.isdir(copyFolder):
                            os.makedirs(copyFolder)
                        _fileMD5 = common.Common.fileMD5(_textureUrl)
                        # print _fileMD5
                        _newFile = _fileMD5 + os.path.splitext(_textureUrl)[1]
                        shutil.copy(_textureUrl, os.path.join(copyFolder, _newFile))
                        _uuidTex = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
                        materialObject[distProp] = _uuidTex
                        self.textureName2UUID[_input] = _uuidTex
                        # print ;
                        _textureObject = {
                           'uuid': _uuidTex, 
                           'url': './textures/' + _newFile,
                           'wrapS': 1000, 
                           'wrapT' : 1000
                        }

                        self.textures.append(_textureObject)
                    else:
                        materialObject[distProp] = self.textureName2UUID[_input]

    def setTransparent(self, param, materialObject, material):
        _transparency = material.getAttr(param)
        if _transparency[0] != 0 or _transparency[1] != 0 or _transparency[2] != 0:
            materialObject['opacity'] = 1 - (_transparency[0] + _transparency[1] + _transparency[2]) / 3

    def getName(self, target, dagPath, isReplace = True):
        if target.hasUniqueName():
            return target.name()
        else:
            if isReplace:
                return dagPath.fullPathName().replace('|', '_')[1:]
            else:
                return dagPath.fullPathName()

    def loopFind(self, tObject, treeParent):
        _type = tObject.apiType()
        _dagPath = om.MDagPath()
        # print tObject.hasFn(om.MFn.kTransform) and tObject.hasFn(om.MFn.kMesh)
        if _type == om.MFn.kTransform:
            _transform = om.MFnTransform(tObject)
            # print _transform.name(), tObject.hasFn(om.MFn.kMesh)
            if 'children' not in treeParent:
                treeParent['children'] = []

            _object = {
                'type': 'Group',
                'name': self.getName(_transform, _dagPath),
                'uuid': str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
            }

            try: 
                if not cmds.getAttr('%s.visibility'%self.getName(_transform, _dagPath, False)):
                    _object['visible'] = False
            except Exception, e:
                print e.message

            _matrix = _transform.transformation().asMatrix()
            if _matrix != om.MMatrix.identity:
                _object['matrix'] = common.Common.MMatrixToArray(_matrix)

            treeParent['children'].append(_object)

            _childCount = _transform.childCount()
            for i in range(_childCount):
                _child = _transform.child(i)
                self.loopFind(_child, _object)
        elif _type == om.MFn.kDirectionalLight:
            _light = om.MFnDirectionalLight(tObject)
            _color = _light.color()
            treeParent['name'] = self.getName(_light, _dagPath)
            treeParent['color'] = [_color[0], _color[1], _color[2]]
            treeParent['intensity'] = _light.intensity()
            treeParent['type'] ='DirectionalLight'

        elif _type == om.MFn.kPointLight:
            _light = om.MFnPointLight(tObject)
            _color = _light.color()
            treeParent['name'] = self.getName(_light, _dagPath)
            treeParent['color'] = [_color[0], _color[1], _color[2]]
            treeParent['intensity'] = _light.intensity()
            treeParent['type'] ='PointLight'
            # _pLight = pm.PyNode(_dagPath.fullPathName())

        elif _type == om.MFn.kSpotLight:
            _light = om.MFnSpotLight(tObject)
            _color = _light.color()
            treeParent['name'] = self.getName(_light, _dagPath)
            treeParent['color'] = [_color[0], _color[1], _color[2]]
            treeParent['intensity'] = _light.intensity()
            treeParent['type'] ='SpotLight'
            _pLight = pm.PyNode(self.getName(_light, _dagPath, False))
            treeParent['angle'] = _pLight.getAttr('coneAngle') * math.pi / 180;

        elif _type == om.MFn.kMesh:
            _uuidGeo = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))

            # _object = {'type': 'Mesh', 'geometry': _uuidGeo, 'material': ''}
            # if 'children' not in treeParent:
            #     treeParent['children'] = []
            treeParent['type'] = 'Mesh'
            treeParent['geometry'] = _uuidGeo

            _mesh =  om.MFnMesh(tObject)
            
            om.MDagPath.getAPathTo(tObject, _dagPath)
            self.meshFileManager.setDatas(_dagPath)
            # print _dagPath.fullPathName()
            _afName = self.getName(_mesh, _dagPath)
            treeParent['name'] = _afName
            _afPath = u'%s.mesh'%_afName
            _projectFolder = os.path.dirname(self.projectPath) # This is folder for project file
            _meshFolder = _projectFolder + '/meshes/' # This is folder for mesh file
            # Create non-existent folders
            if not os.path.isdir(_meshFolder):
                os.makedirs(_meshFolder)

            # Save a .mesh file
            _meshUrl = _meshFolder + _afPath;
            self.meshFileManager.write(_meshUrl)
            self.meshFileManager.init()

            _meshMD5 = common.Common.fileMD5(_meshUrl);
            _newMeshFile = _meshMD5 + '.mesh';

            os.rename(_meshUrl, _meshFolder + _newMeshFile);

            self.geometries.append({'uuid': _uuidGeo, 'url': './meshes/' + _newMeshFile});

            _numInstances = _mesh.parentCount()

            _materials = []
            for i in range(_numInstances):
                _shaders = om.MObjectArray()
                _faceIndices = om.MIntArray()
                _mesh.getConnectedShaders(i, _shaders, _faceIndices)
                for j in range(_shaders.length()):
                    _connections = om.MPlugArray()
                    _shaderGroup = om.MFnDependencyNode(_shaders[j])
                    _shaderPlug = _shaderGroup.findPlug("surfaceShader")
                    _shaderPlug.connectedTo(_connections, True, False)

                    for k in range(_connections.length()):
                        _materials.append(_connections[k].node())
            _useMaterials = []
            for _material in _materials:
                _materialName = om.MFnDependencyNode(_material).name()
                if _materialName not in self.materialName2UUID:
                    _uuidMat = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
                    # treeParent['material'] = _uuidMat
                    _useMaterials.append(_uuidMat)
                    self.materialName2UUID[_materialName] = _uuidMat
                    _pMaterial = pm.PyNode(_materialName);
                    _materialObject = {
                        'uuid': _uuidMat
                    }

                    _materialType = cmds.objectType(_materialName)
                    _diffuse = 1.0
                    _specular = 1.0
                    if _materialType == "surfaceShader":
                        _materialObject['type'] = "MeshBasicMaterial"
                        _materialObject['color'] = list(_pMaterial.getAttr('outColor'))
                        self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'outColor', 'map')
                        self.setTransparent('outTransparency', _materialObject, _pMaterial)
                    elif _materialType == "lambert":
                        _materialObject['type'] = "MeshLambertMaterial"
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        # _materialObject['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'color', 'map')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                    elif _materialType == "blinn":
                        _materialObject['type'] = "MeshPhongMaterial"
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        # _materialObject['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'color', 'map')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                        # _specular = _pMaterial.getAttr('specularRollOff')
                        # _materialObject['specular'] = common.Common.listMultiplyValue(list(_pMaterial.getAttr('specularColor')), _specular)
                        # _specularIntersity = _pMaterial.getAttr('eccentricity')
                        # if _specularIntersity == 0:
                        #     _specularIntersity = 0.001
                        # _materialObject['shininess'] = 10 / _specularIntersity
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'specularColor', 'specularMap')
                        # _materialObject['reflectivity'] = _pMaterial.getAttr('reflectivity')
                    elif _materialType == "phong":
                        _materialObject['type'] = "MeshPhongMaterial"
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        # _materialObject['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'color', 'map')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                        # _materialObject['specular'] = list(_pMaterial.getAttr('specularColor'))
                        # _materialObject['shininess'] = _pMaterial.getAttr('cosinePower')
                        # self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'specularColor', 'specularMap')
                        _materialObject['reflectivity'] = _pMaterial.getAttr('reflectivity')

                    if 'map' in _materialObject:
                        _materialObject['color'] = [_diffuse, _diffuse, _diffuse]

                    if 'specularMap' in _materialObject:
                        _materialObject['specular'] = [_specular, _specular, _specular]

                    # side
                    if cmds.objExists('%s.side'%_pMaterial) and _pMaterial.getAttr('side') != 0:
                        _materialObject['side'] = _pMaterial.getAttr('side')
                    
                    # light map
                    if cmds.objExists('%s.lightMapIntensity'%_pMaterial):
                        self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'lightMap', 'lightMap')
                        _materialObject['lightMapIntensity'] = _pMaterial.getAttr('lightMapIntensity')
                    # _materialObject["lightMap"] = self.lightmapUUID
                    # _materialObject['lightMapIntensity'] = 1.0
                     # ao map
                    if cmds.objExists('%s.aoMapIntensity'%_pMaterial):
                        self.intoTexture(_projectFolder + '/textures/', _materialObject, _pMaterial, 'aoMap', 'aoMap')
                        _materialObject['aoMapIntensity'] = _pMaterial.getAttr('aoMapIntensity')
                    _materialObject['type'] = "MeshBasicMaterial" # test
                    self.materials.append(_materialObject)

                else:
                    _useMaterials.append(self.materialName2UUID[_materialName])
                    # treeParent['material'] = self.materialName2UUID[_materialName]
            if len(_useMaterials) == 1:
                treeParent['material'] = _useMaterials[0]
            elif len(_useMaterials) > 1:
                treeParent['material'] = _useMaterials

                
            # treeParent['children'].append(_object)


    '''输出保存project文件'''           
    def writeProject(self, url, isPutty = True):
        extraTypeNames = ['textManip2D', 'xformManip', 'translateManip', 'cubeManip', 'objectSet']
        extraNames = ['groundPlane_transform', 'persp', 'top', 'front', 'side', 'shaderBallCamera1', 'shaderBallGeom1', 'MayaMtlView_KeyLight1', 'MayaMtlView_FillLight1', 'MayaMtlView_RimLight1']
        tObjects = []
        dagIterator = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kInvalid);
        while not dagIterator.isDone():
            dagPath = om.MDagPath()
            dagIterator.getPath(dagPath)
            dagIterator.next() # iterator 跳到下一个
            if dagPath.apiType() == om.MFn.kWorld:
                for i in range(dagPath.childCount()):
                    _child = dagPath.child(i)
                    if _child.hasFn(om.MFn.kTransform):
                        _transform = om.MFnTransform(_child)
                        print _transform.typeName(), _transform.name()
                        if _transform.typeName() not in extraTypeNames and _transform.name() not in extraNames:
                            # print _transform.name()
                            tObjects.append(_child)
                break

        self.projectPath = url
        print tObjects
        for tObject in tObjects:
            self.loopFind(tObject, self.objectTree)
            # print mTransform.child(0).apiType()
            # 
        _outputTree = {
            'information': {
                'author': 'fun.zheng'
            },
            'geometries': self.geometries,
            'materials': self.materials,
            'textures': self.textures,
            'object': self.objectTree
        }
        if isPutty:
            _outputJson = json.dumps(_outputTree, sort_keys = True, indent = 2, separators = (',', ': '))
        else:
            _outputJson = json.dumps(_outputTree,separators = (',', ':'))

        _f = open(url, 'w')
        try:
            _f.write(_outputJson)
        finally:
            _f.close()
        # print _outputJson
        self.init()

    '''ui part'''
    def ui(self):
        window_name = "MESH_FILE_MANAGER_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        
        window = cmds.window(window_name, title="Project File Manager", widthHeight=(300, 500))
        cmds.columnLayout(adj=True)
        tabs = cmds.tabLayout()
        import_column = cmds.columnLayout(adj=True)
        cmds.button(label="import mesh", c=self.meshFileManager._import)
        cmds.setParent('..')
        export_column = cmds.columnLayout(adj=True)
        self.uv_cb = cmds.checkBox(label='export uvs', value=True)
        self.normal_cb = cmds.checkBox(label='export normals', value=True)
        # cmds.button(label="export all meshes", c=self.meshFileManager._exportAll)
        # cmds.button(label="export selected meshes", c=self.meshFileManager._exportSelected)
        cmds.button(label="add need attrs", c=self.addNeedAttrs)
        cmds.button(label="export project", c=self._exportProject)
        cmds.setParent('..')
        cmds.tabLayout(tabs, edit=True, tabLabel=((import_column, "Import"), (export_column, "Export")))
        cmds.showWindow(window)

    def _exportProject(self, argas):
        project_paths = self._export("Project (*.project)")
        if project_paths:
            _pFolder = os.path.dirname(project_paths[0])
            _pSubs = os.listdir(_pFolder)
            try:
                for _pSub in _pSubs:
                    if _pSub != 'cover.jpg':
                        shutil.rmtree(os.path.join(_pFolder, _pSub))
            except Exception, e:
                print e.message
            self.writeProject(project_paths[0])
            print "Export project finish."
        # self.writeProject('d:/documents/maya/outpro/test.project')
        # self.writeProject('/Users/zwf/Documents/zwf/templates/outpro/test.project')

    def _export(self, filter = "Mesh (*.mesh)"):
        paths = cmds.fileDialog2(fileFilter=filter, dialogStyle=2)
        self.out_uv = cmds.checkBox(self.uv_cb, q = True, v=True)
        self.out_normal = cmds.checkBox(self.normal_cb, q = True, v=True)
        return paths

def main():
    imExport = ImportAndExport();
    imExport.ui()

if __name__ == '__main__':
    main();