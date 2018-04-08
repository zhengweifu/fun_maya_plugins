# -*- coding: utf-8 -*-
import maya.api.OpenMaya as nm
import maya.OpenMaya as om
import maya.cmds as cmds
import geoFileManager, common, uuid, time, json, os, shutil, math
import pymel.core as pm
import pymel.core.datatypes as dt
import maya.mel as mel
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
        self.geo_space_is_local = True
        self.out_new_shader_type = True
        self.out_compression = True
        self.outputNodes = []
        self.init()

    def init(self):
        self.geoFileManager.out_uv = self.out_uv
        self.geoFileManager.out_normal = self.out_normal
        self.geoFileManager.space_is_local = self.geo_space_is_local
        self.initData()

    def initData(self):    
        self.geometries = {}
        self.materials = {}
        self.materialName2UUID = {}
        self.textures = {}
        self.textureName2UUID = {}
        self.faceMaterials = []
        self.outputNodes = []
        self.objectTree = {'type': 0, 'children': []}

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

    def addOutputNode(self, argas):
        output_node = pm.createNode( 'transform', n='OUTPUT_NODE1' )
        pm.addAttr(output_node, ln = 'isExport', at = 'bool')
        output_node.isExport.set(True)
        pm.addAttr(output_node, ln = 'elementId', dt = 'string')

    def getOutputNode(self):
        _transforms = pm.ls(tr = 1, v = 1)
        for _transform in _transforms:
            if not pm.parent(_transform) and pm.listRelatives(_transform) and pm.objExists('%s.isExport'%_transform) and pm.getAttr('%s.isExport'%_transform):
                print _transform
                self.outputNodes.append(_transform)

            
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
                           'url'   : outTextureFolder + _newFile,
                           'wrapS' : 0, 
                           'wrapT' : 0
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
        _type = tObject.nodeType()
        # _dagPath = om.MDagPath()
        _name = tObject.name()
        if _type == "transform":
            if 'children' not in treeParent:
                treeParent['children'] = []

            _object = {
                'type': 0, # Group
                # 'name': _name,
                # 'uuid': str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
                'uuid': common.Common.MD532ToUUID(common.Common.MD5(_name))
            }

            try: 
                if not tObject.visibility.get():
                    _object['visible'] = False
            except Exception, e:
                print e.message

            if self.geo_space_is_local:
                _matrix = tObject.getMatrix(objectSpace = 1)
                if _matrix != dt.Matrix.identity:
                    _object['matrix'] = common.Common.List2ToList1(_matrix.data)

            treeParent['children'].append(_object)

            for _child in tObject.getChildren():
                self.loopFind(_child, _object)
        elif _type == "directionalLight":
            _color = tObject.color.get()
            treeParent['color'] = [_color[0], _color[1], _color[2]]
            treeParent['intensity'] = tObject.intensity.get()
            treeParent['type'] ='DirectionalLight'

        elif _type == "pointLight":
            _color = tObject.color.get()
            treeParent['color'] = [_color[0], _color[1], _color[2]]
            treeParent['intensity'] = tObject.intensity.get()
            treeParent['type'] ='PointLight'

        elif _type == "spotLight":
            _color = tObject.color.get()
            treeParent['color'] = [_color[0], _color[1], _color[2]]
            treeParent['intensity'] = tObject.intensity.get()
            treeParent['type'] ='SpotLight'
            treeParent['angle'] = tObject.coneAngle.get() * math.pi / 180;

        elif _type == "mesh":
            treeParent['type'] = 1 # Mesh
            _dagPath = common.Common.GetMDagPathFromName(_name)
            _mesh =  om.MFnMesh(_dagPath)
            
            self.geoFileManager.setDatas(_dagPath)

            _afName = self.getName(_mesh, _dagPath)

            _afPath = '%s.geo'%common.Common.Uuid()
            _projectFolder = os.path.join(self.projectRoot, 'scenes')  # This is folder for project file
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
            _pNode = tObject
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
                    _pMaterial = pm.PyNode(_materialName);
                    _materialObject = {
                        'parameters': {}
                    }

                    _materialType = cmds.objectType(_materialName)
                    _diffuse = 1.0
                    _specular = 1.0
                    _matTexFolder = os.path.realpath(os.path.join(_projectFolder, '../materials/textures'))
                    if _materialType == "surfaceShader":
                        _materialObject['type'] = 0 # Simple
                        _materialObject['parameters']['color'] = list(_pMaterial.getAttr('outColor'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'outColor', 'map')
                        self.setTransparent('outTransparency', _materialObject, _pMaterial)
                    elif _materialType == "lambert":
                        _materialObject['type'] = 1 # Lambert
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        # _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['parameters']['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        _materialObject['parameters']['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'color', 'map')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                    elif _materialType == "blinn":
                        _materialObject['type'] = 2 # Phong
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        # _diffuse = _pMaterial.getAttr('diffuse')
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
                        _materialObject['type'] = 2 # Phong
                        self.setTransparent('transparency', _materialObject, _pMaterial)
                        # _diffuse = _pMaterial.getAttr('diffuse')
                        _materialObject['parameters']['color'] =  common.Common.listMultiplyValue(list(_pMaterial.getAttr('color')), _diffuse)
                        _materialObject['parameters']['emissive'] = list(_pMaterial.getAttr('incandescence'))
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'color', 'map')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'incandescence', 'emissiveMap')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'normalCamera', 'bumpMap')
                        _materialObject['parameters']['specular'] = list(_pMaterial.getAttr('specularColor'))
                        _materialObject['parameters']['shininess'] = _pMaterial.getAttr('cosinePower')
                        self.intoTexture(_matTexFolder, _materialObject, _pMaterial, 'specularColor', 'specularMap')
                        _materialObject['parameters']['reflectivity'] = _pMaterial.getAttr('reflectivity')

                    if self.out_new_shader_type:
                        _materialObject['type'] = 3 # new shader system type

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
                    if not self.out_compression:
                        _matContains = json.dumps(_materialObject, sort_keys = True, indent = 2, separators = (',', ': '))
                    else:
                        _matContains = json.dumps(_materialObject,separators = (',', ':'))
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

    '''输出保存component文件'''
    def writeOne(self, top, isPutty):
        self.objectTree["uuid"] = common.Common.MD532ToUUID(common.Common.MD5(top.name()))
        self.loopFind(top, self.objectTree)
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
        
        worldFile = ''
        if self.use_md5_name:
            worldFile = common.Common.MD5(_outputJson)
        else:
            worldFile = top.name()

        componentFolder = os.path.join(self.projectRoot, 'components')
        if not os.path.isdir(componentFolder):
            os.makedirs(componentFolder)

        url = os.path.join(componentFolder, worldFile + ".scene")


        _f = open(url, 'w')
        try:
            _f.write(_outputJson)
        finally:
            _f.close()
        # print _outputJson
        self.initData()

        return {"uuid": common.Common.MD532ToUUID(worldFile), "type": 2, "url" : "../components/%s.scene"%worldFile}

    '''获取相机参数'''
    def _getCameraParas(self):
        _currentCamera = pm.optionMenu(self.camera_menu, q = 1, v = 1)
        _currentCamera = pm.PyNode(_currentCamera)

        if _currentCamera.exists() and _currentCamera.nodeType() == "camera":
            _fov = _currentCamera.focalLength.get()
            _near = _currentCamera.nearClipPlane.get()
            _far = _currentCamera.farClipPlane.get()

            _parent = _currentCamera.getParent()

            _matrix = _parent.getMatrix()

            _matrix = common.Common.List2ToList1(_matrix.data)

            return {
                "matrix": _matrix,
                "fov": _fov,
                "near": _near,
                "far": _far
            }

        return None

    '''获取系统参数'''
    def _getSystemParas(self):
        _linear = pm.currentUnit(q = 1, l = 1)
        if _linear == "mm":
            _linear = 0
        elif _linear == "cm":
            _linear = 1
        elif _linear == "m":
            _linear = 2
        else:
            _linear = 0

        return {
            "unit": _linear,
            "up": pm.upAxis(q = 1, ax = 1)
        }

    '''输出保存project文件'''           
    def writeProject(self, url, isPutty = True):
        # 获取输出的父节点
        self.getOutputNode()

        if not self.outputNodes:
            pm.error("Not output nodes, please checked.")
            return

        self.projectRoot = os.path.dirname(url)
        
        _outputTree = {
            "metadata": {
                "version": 1.0,
                'author': 'fun.zheng'
            },
            'object': {'type': 0, 'children': [], 'uuid': common.Common.MD532ToUUID(common.Common.MD5(cmds.file(q = True, sn = True)))}
        }
        # 相机参数
        _camera_set = self._getCameraParas()
        if _camera_set:
            _outputTree["camera"] = _camera_set
        # 系统参数
        _system_set = self._getSystemParas()
        _outputTree["systemset"] = _system_set

        for node in self.outputNodes:
            _outputTree["object"]["children"].append(self.writeOne(node, isPutty))

        if isPutty:
            _outputJson = json.dumps(_outputTree, indent = 2, separators = (',', ': '))
        else:
            _outputJson = json.dumps(_outputTree,separators = (',', ':'))
        # print _outputJson
        if self.use_md5_name:
            url = os.path.join(self.projectRoot, 'scenes', common.Common.MD5(_outputJson) + os.path.splitext(url)[1])

        _f = open(url, 'w')
        try:
            _f.write(_outputJson)
        finally:
            _f.close()
        # print _outputJson
        self.init()

    def _setCameraItems(self, argas):
        try:
            pm.deleteUI(self.camera_menu)
        except:
            pass
        self.camera_menu = pm.optionMenu(l = "cameras", p = self.colum_camera_menu)
        _cameras = pm.ls(type = "camera")
        for _camera in _cameras:
            pm.menuItem(l = _camera.name(), p = self.camera_menu)

    '''ui part'''
    def ui(self):
        window_name = "WORLD_FILE_MANAGER_WINDOW"
        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name)
        
        window = cmds.window(window_name, title="Scene File Manager", widthHeight=(300, 500))
        cmds.columnLayout(adj=True)
        tabs = cmds.tabLayout()
        # import_column = cmds.columnLayout(adj=True)
        # cmds.button(label="import mesh", c=self.geoFileManager._import)
        # cmds.setParent('..')
        export_column = cmds.columnLayout(adj=True)
        self.remove_old_data_cb = cmds.checkBox(label='remove old data', value=self.remove_old_data)
        self.use_md5_cb = cmds.checkBox(label='use md5 name', value=self.use_md5_name)
        self.out_new_shader_cb = cmds.checkBox(label='out new shader type', value=self.out_new_shader_type)
        self.out_compression_cb = cmds.checkBox(label='out compression', value=self.out_compression)
        self.uv_cb = cmds.checkBox(label='export uvs', value=self.out_uv)
        self.normal_cb = cmds.checkBox(label='export normals', value=self.out_normal)
        self.geo_space_is_local_cb = cmds.checkBox(label='geometry use local space', value=self.geo_space_is_local)
        cmds.separator(style='in', h = 20)
        self.colum_camera_menu = cmds.columnLayout(adj=True)
        self.update_camera_menu = cmds.button(label="update cameras", c=self._setCameraItems)
        cmds.setParent("..")
        cmds.separator(style='in', h = 20)
        # cmds.button(label="export all meshes", c=self.geoFileManager._exportAll)
        # cmds.button(label="export selected meshes", c=self.geoFileManager._exportSelected)
        # cmds.button(label="add need attrs", c=self.addNeedAttrs)
        cmds.button(label="add output node", c=self.addOutputNode)
        cmds.button(label="add attrs for mesh", c=self.addAttrsForMesh)
        cmds.separator(style='in', h = 20)
        cmds.button(label="export Scene", c=self._exportProject)
        cmds.setParent('..')
        # cmds.tabLayout(tabs, edit=True, tabLabel=((import_column, "Import"), (export_column, "Export")))
        cmds.tabLayout(tabs, edit=True, tabLabel=((export_column, "Export")))
        cmds.showWindow(window)

        self._setCameraItems(None)

    def _exportProject(self, argas):
        # 删除历史
        mel.eval("DeleteAllHistory")

        project_paths = self._export("Scene (*.scene)")
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

            self.writeProject(_projectUrl, not self.out_compression)
            print u"导出完成."
        # self.writeProject('d:/documents/maya/outpro/test.project')
        # self.writeProject('/Users/zwf/Documents/zwf/templates/outpro/test.project')

    def _export(self, filter = "Geo (*.geo)"):
        paths = cmds.fileDialog2(fileFilter=filter, dialogStyle=2)
        self.remove_old_data = cmds.checkBox(self.remove_old_data_cb, q = True, v = True)
        self.use_md5_name = cmds.checkBox(self.use_md5_cb, q = True, v=True)
        self.out_new_shader_type = cmds.checkBox(self.out_new_shader_cb, q = True, v=True)
        self.out_compression = cmds.checkBox(self.out_compression_cb, q = True, v=True)
        self.out_uv = cmds.checkBox(self.uv_cb, q = True, v=True)
        self.out_normal = cmds.checkBox(self.normal_cb, q = True, v=True)
        self.geo_space_is_local = cmds.checkBox(self.geo_space_is_local_cb, q = True, v=True)
        return paths

def main():
    wfm = WorldFileManager();
    wfm.ui()

if __name__ == '__main__':
    main();