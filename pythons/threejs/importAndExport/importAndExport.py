# -*- coding: utf-8 -*-
import maya.api.OpenMaya as nm
import maya.OpenMaya as om
import maya.cmds as cmds
import meshFileManager, common
reload(common)
class ImportAndExport(object):
    '''初始化方法'''
    def __init__(self):
        self.meshFileManager = meshFileManager.MeshFileManager();
        self.out_uv = True
        self.out_normal = True

    '''输出保存project文件'''           
    def writeProject(self):
        extraTypeNames = ['textManip2D', 'xformManip', 'translateManip', 'cubeManip']
        extraNames = ['groundPlane_transform', 'persp', 'top', 'front', 'side']
        mTransfroms = []
        dagIterator = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kInvalid);
        while not dagIterator.isDone():
            dagPath = om.MDagPath()
            dagIterator.getPath(dagPath)
            dagIterator.next() # iterator 跳到下一个
            if dagPath.apiType() == om.MFn.kWorld:
                for i in range(dagPath.childCount()):
                    if dagPath.child(i).hasFn(om.MFn.kTransform):
                        transform = om.MFnTransform(dagPath.child(i))
                        if transform.typeName() not in extraTypeNames and transform.name() not in extraNames:
                            print transform.name()
                            mTransfroms.append(transform)
                break

        for mTransform in mTransfroms:
            print mTransform.child(0).apiType()

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
        cmds.button(label="export all meshes", c=self.meshFileManager._exportAll)
        cmds.button(label="export selected meshes", c=self.meshFileManager._exportSelected)
        cmds.button(label="export project", c=self._exportProject)
        cmds.setParent('..')
        cmds.tabLayout(tabs, edit=True, tabLabel=((import_column, "Import"), (export_column, "Export")))
        cmds.showWindow(window)

    def _exportProject(self, argas):
        # project_paths = self._export("Project (*.project)")
        # if project_paths:
        self.writeProject()

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