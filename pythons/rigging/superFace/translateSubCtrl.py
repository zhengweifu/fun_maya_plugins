from maya.cmds import *
def translate():
    sel = ls(sl = True)[0]
    nodes = listHistory(sel, levels=1)
    for node in nodes:
        if nodeType(node) == 'blendShape':
            bsnode = node
    baseMesh, goalMesh = listConnections(bsnode, source = True, destination = True, shapes = True, type = 'mesh')
    folObj = listConnections('%s.outMesh'%goalMesh)
    for obj in folObj:
        try:
            connectAttr( '%s.outMesh'%baseMesh, '%s.inputMesh'%obj, f = True )
            connectAttr( '%s.worldMatrix[0]'%baseMesh, '%s.inputWorldMatrix'%obj, f = True )
        except:
            pass
