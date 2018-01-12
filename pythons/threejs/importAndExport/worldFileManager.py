# -*- coding: utf-8 -*-
import maya.api.OpenMaya as nm
import maya.OpenMaya as om
import maya.cmds as cmds
import geoFileManager, common, uuid, time, json, os, shutil, math
import pymel.core as pm
reload(common)
reload(geoFileManager)
class WorldFileManager(object):
    '''初始化方法'''
    def __init__(self):
        self.geoFileManager = geoFileManager.GeoFileManager();
        self.remove_old_data = False
        self.use_md5_name = True
        self.out_uv = True
        self.out_normal = True
        self.init()

    def init(self):
        self.geoFileManager.out_uv = self.out_uv
        self.geoFileManager.out_normal= self.out_normal
        self.geometries = {}
        self.materials = {}
        self.materialName2UUID = {}
        self.textures = {}
        self.textureName2UUID = {}
        self.faceMaterials = []
        self.objectTree = {'type': 'Group', 'children': [], 'uuid': common.Common.MD532ToUUID(common.Common.MD5(cmds.file(q = True, sn = True)))}

    def addNeedAttrs(self, argas):
        mats = cmds.ls(mat = True)
        for mat in mats:
            self.addAttrs(mat)

    def addAttrs(self, obj):
        if not cmds.objExists('%s.side'%obj):
            cmds.addAttr(obj, ln = 'side', at = 'enum', en='front=0:back=1:double=2')
        if not cmds.objExists('%s.aoMap'%obj):
            cmds.addAttr(obj, ln = 'aoMap', at = 'double3')
            cmds.addAttr(obj, ln = 'aoMapR', at = 'double', p = 'aoMap')
            cmds.addAttr(obj, ln = 'aoMapG', at = 'double', p = 'aoMap')
            cmds.addAttr(obj, ln = 'aoMapB', at = 'double', p = 'aoMap')
            cmds.addAttr(obj, ln = "aoMapIntensity", at = 'double', min = 0, max = 1, dv = 1)
        if not cmds.objExists('%s.lightMap'%obj):
            cmds.addAttr(obj, ln = 'lightMap', at = 'double3')
            cmds.addAttr(obj, ln = 'lightMapR', at = 'double', p = 'lightMap')
            cmds.addAttr(obj, ln = 'lightMapG', at = 'double', p = 'lightMap')
            cmds.addAttr(obj, ln = 'lightMapB', at = 'double', p = 'lightMap')
            cmds.addAttr(obj, ln = "lightMapIntensity", at = 'double', min = 0, max = 1, dv = 1)

        if not cmds.objExists('%s.static'%obj):
            cmds.addAttr(obj, ln = 'static', at = 'bool')

        if not cmds.objExists('%s.typeid'%obj):
            cmds.addAttr(obj, ln = 'typeid', dt = 'string')

    def addAttrsForMesh(self, argas):
        objs = cmds.ls(type = "mesh")
        for obj in objs:
            self.addAttrs(obj);
            
    def intoTexture(self, copyFolder, inputObject, pNode, srcProp, distProp, outTextureFolder = './textures/'):
        # print pNode.attr(srcProp).inputs()
        _inputs = pNode.attr(srcProp).inputs()
        if len(_inputs) > 0:
            _input = _inputs[0]
            # print _input.type()
            if _input.type() == 'bump2d':
                _cinputs = _input.bumpValue.inputs()
                if len(_cinputs) > 0:
                    if _input.getAttr('bumpInterp') > 0:
                        distProp = 'normalMap'
                    else:
                        inputObject['parameters']['bumpScale'] = _input.getAttr('bumpDepth')
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
                        # _uuidTex = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
                        _uuidTex = common.Common.MD532ToUUID(_fileMD5)
                        inputObject['parameters'][distProp] = _uuidTex
                        self.textureName2UUID[_input] = _uuidTex
                        # print ;
                        _textureObject = {
                           # 'uuid': _uuidTex, 
                           'url': outTextureFolder + _newFile,
                           'wrapS': 1000, 
                           'wrapT' : 1000
                        }

                        # self.textures.append(_textureObject)
                        if not inputObject.has_key("textures"):
                            inputObject["textures"] = {}
                        inputObject["textures"][_uuidTex] = _textureObject
                    else:
                        inputObject['parameters'][distProp] = self.textureName2UUID[_input]

    def setTransparent(self, param, materialObject, material):
        _transparency = material.getAttr(param)
        if _transparency[0] != 0 or _transparency[1] != 0 or _transparency[2] != 0:
            materialObject['parameters']['opacity'] = 1 - (_transparency[0] + _transparency[1] + _transparency[2]) / 3

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

            _name = self.getName(_transform, _dagPath)
            _object = {
                'type': 'Group',
                'name': _name,
                # 'uuid': str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
                'uuid': common.Common.MD532ToUUID(common.Common.MD5(_name))
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
            # _uuidGeo = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))

            # _object = {'type': 'Mesh', 'geometry': _uuidGeo, 'material': ''}
            # if 'children' not in treeParent:
            #     treeParent['children'] = []
            treeParent['type'] = 'Mesh'
            # treeParent['geometry'] = _uuidGeo

            _mesh =  om.MFnMesh(tObject)
            
            om.MDagPath.getAPathTo(tObject, _dagPath)
            self.geoFileManager.setDatas(_dagPath)
            # print _dagPath.fullPathName()
            _afName = self.getName(_mesh, _dagPath)

            treeParent['name'] = _afName
            _afPath = '%s.mesh'%_afName
            _projectFolder = os.path.join(os.path.dirname(self.projectPath), 'worlds')  # This is folder for project file
            # Create non-existent folders
            if not os.path.isdir(_projectFolder):
                os.makedirs(_projectFolder)

            _meshFolder = os.path.realpath(os.path.join(_projectFolder, '../meshes')) # This is folder for mesh file
            # Create non-existent folders
            if not os.path.isdir(_meshFolder):
                os.makedirs(_meshFolder)

            # Save a .mesh file
            _meshUrl = os.path.join(_meshFolder, _afPath)
            self.geoFileManager.write(_meshUrl)
            self.geoFileManager.init()

            _meshMD5 = common.Common.fileMD5(_meshUrl);
            _newMeshFile = _meshMD5 + '.geo'

            _newFile = os.path.join(_meshFolder, _newMeshFile)

            if not os.path.isfile(_newFile):
                os.rename(_meshUrl, _newFile);
            else:
                os.remove(_meshUrl)

            _uuidGeo = common.Common.MD532ToUUID(_meshMD5)
            treeParent['geometry'] = _uuidGeo

            # export lightMap
            _texFolder = os.path.realpath(os.path.join(_projectFolder, '../textures'));
            _intputObject = {"parameters": {}}
            _pNode = pm.PyNode(_afName)
            if cmds.objExists('%s.lightMap'%_pNode):
                self.intoTexture(_texFolder, _intputObject, _pNode, 'lightMap', 'lightMap', '../textures/')
                if _intputObject["parameters"].has_key('lightMap'):
                    treeParent['lightMap'] = _intputObject["parameters"]['lightMap']
            
            if _intputObject.has_key('textures'):
                for _tex in _intputObject["textures"]:
                    self.textures[_tex] = _intputObject["textures"][_tex]

            # export static attr
            if cmds.objExists('%s.static'%_pNode):
                _staticAttr = _pNode.getAttr('static')
                if _staticAttr:
                    treeParent['static'] = _staticAttr

            # export typeid attr
            if cmds.objExists('%s.typeid'%_pNode):
                _typeidAttr = _pNode.getAttr('typeid')
                if _typeidAttr:
                    treeParent['typeid'] = _typeidAttr

            self.geometries[_uuidGeo] = {'url': '../meshes/' + _newMeshFile};

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
                    # _uuidMat = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
                    # # treeParent['material'] = _uuidMat
                    # _useMaterials.append(_uuidMat)
                    # self.materialName2UUID[_materialName] = _uuidMat
                    _pMaterial = pm.PyNode(_materialName);
                    _materialObject = {
                        'parameters': {}
                    }

                    _materialType = cmds.objectType(_materialName)
                    _diffuse = 1.0
                    _specular = 1.0
                    _matTexFolder = os.path.realpath(os.path.join(_projectFolder, '../materials/textures'))
                    if _materialType == "surfaceShader":
                        _materialObject['type'] = "Simple"
                        _materialObject['parameters']['color'] = list(_pMaterial.getAttr('outColor'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'outColor', 'map')
                        self.setTransparent('outTransparency', _materialObject, _pMaterial)
                    elif _materialType == "lambert":
                        _materialObject['type'] = "MeshLambertMaterial"
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['parameters']['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        _materialObject['parameters']['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'color', 'map')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                    elif _materialType == "blinn":
                        _materialObject['type'] = "MeshPhongMaterial"
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['parameters']['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        _materialObject['parameters']['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'color', 'map')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                        _specular = _pMaterial.getAttr('specularRollOff')
                        _materialObject['parameters']['specular'] = common.Common.listMultiplyValue(list(_pMaterial.getAttr('specularColor')), _specular)
                        _specularIntersity = _pMaterial.getAttr('eccentricity')
                        if _specularIntersity == 0:
                            _specularIntersity = 0.001
                        _materialObject['parameters']['shininess'] = 10 / _specularIntersity
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'specularColor', 'specularMap')
                        _materialObject['parameters']['reflectivity'] = _pMaterial.getAttr('reflectivity')
                    elif _materialType == "phong":
                        _materialObject['type'] = "MeshPhongMaterial"
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['parameters']['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        _materialObject['parameters']['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'color', 'map')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                        _materialObject['parameters']['specular'] = list(_pMaterial.getAttr('specularColor'))
                        _materialObject['parameters']['shininess'] = _pMaterial.getAttr('cosinePower')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'specularColor', 'specularMap')
                        _materialObject['parameters']['reflectivity'] = _pMaterial.getAttr('reflectivity')

                    if 'map' in _materialObject['parameters']:
                        _materialObject['parameters']['color'] = [_diffuse, _diffuse, _diffuse]

                    if 'specularMap' in _materialObject['parameters']:
                        _materialObject['parameters']['specular'] = [_specular, _specular, _specular]

                    # side
                    if cmds.objExists('%s.side'%_pMaterial) and _pMaterial.getAttr('side') != 0:
                        _materialObject['parameters']['side'] = _pMaterial.getAttr('side')
                    
                    # light map
                    if cmds.objExists('%s.lightMapIntensity'%_pMaterial):
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'lightMap', 'lightMap')
                        _materialObject['parameters']['lightMapIntensity'] = _pMaterial.getAttr('lightMapIntensity')

                    # ao map
                    if cmds.objExists('%s.aoMapIntensity'%_pMaterial):
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'aoMap', 'aoMap')
                        _materialObject['parameters']['aoMapIntensity'] = _pMaterial.getAttr('aoMapIntensity')
                    
                    _matFolder = os.path.realpath(os.path.join(_projectFolder, '../materials/'))# This is folder for material file
                    # Create non-existent folders
                    if not os.path.isdir(_matFolder):
                        os.makedirs(_matFolder)
                    _matContains = json.dumps(_materialObject, sort_keys = True, indent = 2, separators = (',', ': '))
                    _matMD5 = common.Common.MD5(_matContains)
                    _matUrl = os.path.join(_matFolder, _matMD5 + '.mat')
                    if not os.path.isfile(_matUrl):
                        _matFile = open(_matUrl, 'w')
                        try:
                            _matFile.write(_matContains)
                        finally:
                            _matFile.close()

                    _uuidMat = common.Common.MD532ToUUID(_matMD5)
                    # treeParent['material'] = _uuidMat
                    _useMaterials.append(_uuidMat)
                    self.materialName2UUID[_materialName] = _uuidMat

                    self.materials[_uuidMat] = {"url": '../materials/' + _matMD5 + '.mat'}

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
                        # print _transform.typeName(), _transform.name()
                        if _transform.typeName() not in extraTypeNames and _transform.name() not in extraNames:
                            # print _transform.name()
                            tObjects.append(_child)
                break

        self.projectPath = url
        # print tObjects
        for tObject in tObjects:
            self.loopFind(tObject, self.objectTree)
            # print mTransform.child(0).apiType()
        # print self.textures
        _outputTree = {
            "metadata": {
                "version": 1.0,
                'author': 'fun.zheng'
            },
            'geometries': self.geometries,
            'materials': self.materials,
            'textures': self.textures,
            'object': self.objectTree
        }
        if isPutty:
            _outputJson = json.dumps(_outputTree, indent = 2, separators = (',', ': '))
        else:
            _outputJson = json.dumps(_outputTree,separators = (',', ':'))
        # print _outputJson
        if self.use_md5_name:
            url = os.path.join(os.path.dirname(url), 'worlds', common.Common.MD5(_outputJson) + os.path.splitext(url)[1])

        _f = open(url, 'w')
        try:
            _f.write(_outputJson)
        finally:
            _f.close()
        # print _outputJson
        self.init()

    '''ui part'''
    def ui(self):
        window_name = "WORLD_FILE_MANAGER_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        
        window = cmds.window(window_name, title="World File Manager", widthHeight=(300, 500))
        cmds.columnLayout(adj=True)
        tabs = cmds.tabLayout()
        import_column = cmds.columnLayout(adj=True)
        cmds.button(label="import mesh", c=self.geoFileManager._import)
        cmds.setParent('..')
        export_column = cmds.columnLayout(adj=True)
        self.remove_old_data_cb = cmds.checkBox(label='remove old data', value=self.remove_old_data)
        self.use_md5_cb = cmds.checkBox(label='use md5 name', value=self.use_md5_name)
        self.uv_cb = cmds.checkBox(label='export uvs', value=self.out_uv)
        self.normal_cb = cmds.checkBox(label='export normals', value=self.out_normal)
        # cmds.button(label="export all meshes", c=self.geoFileManager._exportAll)
        # cmds.button(label="export selected meshes", c=self.geoFileManager._exportSelected)
        # cmds.button(label="add need attrs", c=self.addNeedAttrs)
        cmds.button(label="add attrs for mesh", c=self.addAttrsForMesh)
        cmds.button(label="export World", c=self._exportProject)
        cmds.setParent('..')
        cmds.tabLayout(tabs, edit=True, tabLabel=((import_column, "Import"), (export_column, "Export")))
        cmds.showWindow(window)

    def _exportProject(self, argas):
        project_paths = self._export("World (*.world)")
        if project_paths:
            _projectUrl = project_paths[0]

            if self.remove_old_data:
                _pFolder = os.path.dirname(_projectUrl)
                _pSubs = os.listdir(_pFolder)
                try:
                    for _pSub in _pSubs:
                        if _pSub != 'cover.jpg':
                            shutil.rmtree(os.path.join(_pFolder, _pSub))
                except Exception, e:
                    print e.message

            self.writeProject(_projectUrl)
            print "Export project finish."
        # self.writeProject('d:/documents/maya/outpro/test.project')
        # self.writeProject('/Users/zwf/Documents/zwf/templates/outpro/test.project')

    def _export(self, filter = "Geo (*.geo)"):
        paths = cmds.fileDialog2(fileFilter=filter, dialogStyle=2)
        self.remove_old_data = cmds.checkBox(self.remove_old_data_cb, q = True, v = True)
        self.use_md5_name = cmds.checkBox(self.use_md5_cb, q = True, v=True)
        self.out_uv = cmds.checkBox(self.uv_cb, q = True, v=True)
        self.out_normal = cmds.checkBox(self.normal_cb, q = True, v=True)
        return paths

def main():
    wfm = WorldFileManager();
    wfm.ui()

if __name__ == '__main__':
    main();