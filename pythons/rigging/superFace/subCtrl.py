#------------JOINT-----------#

#-----------------------
# Import modules
#-----------------------

import maya.OpenMaya as om
import maya.cmds as mc
import string
import maya.mel as mm
from sfGlobal import *
#from jointCtrl import *
from time import *
import utility as u

class subCtrl:
    
    
    def mirror(self, arg):
        nodes = self.locList()
        for node in nodes:
            other = None
            if g.LEFT_KEY in node:
                if arg==1:
                    other = node.replace(g.LEFT_KEY,g.RIGHT_KEY)
                else:
                    continue
            elif g.RIGHT_KEY in node:
                if arg==-1:
                    other = node.replace(g.RIGHT_KEY,g.LEFT_KEY)
                else:
                    continue
            else:
                mc.setAttr('%s.tx'%node,0)
                continue
            try:
                tx = -1 * mc.getAttr('%s.tx'%node)
                ty = mc.getAttr('%s.ty'%node)
                tz = mc.getAttr('%s.tz'%node)
                mc.setAttr('%s.tx'%other,tx)
                mc.setAttr('%s.ty'%other,ty)
                mc.setAttr('%s.tz'%other,tz)
            except:
                print 'No exists object:',other
        
    def locList(self):
        nodes = []
        locs = mc.listRelatives(g.SUB_LOC_GRP,ad=1,type='locator')
        if locs is not None:
            for loc in locs:
                nodes.append(mc.listRelatives(loc,p=1)[0])
        return nodes
        
    def zeroSubCtrls(self):
        ctrls =self.getCtrlList()
        for ctrl in ctrls:
            try:
                mc.setAttr('%s.t'%ctrl,0,0,0,type='double3')
                mc.setAttr('%s.r'%ctrl,0,0,0,type='double3')
                mc.setAttr('%s.s'%ctrl,1,1,1,type='double3')
            except:
                print 'No exists object:',ctrl
    def getCtrlList(self):
        try:
            allShapes = mc.listRelatives(g.SUB_CTRL_LIST_GRP, ad = True, ni = False, type = 'nurbsCurve')
        except:
            return []
        if allShapes == None:
            return []
        ctrlList = []
        for shape in allShapes:
            ctrlList.append(mc.listRelatives(shape, parent = True)[0])
            
        return ctrlList

        
    # +-------------------------------------------------------------------------------------------------+
    # |                                        Main Function                                            |
    # +-------------------------------------------------------------------------------------------------+
    def buildSubCtrl(self, mesh, locList, softArea = 0.75):
        if mesh == '' :
            raise RuntimeError, 'Fuck, There is no model assigned!'
        subLocChn = mc.listRelatives(g.SUB_LOC_GRP)
        if subLocChn == None:
            raise RuntimeError, 'Oops! Ther is no sub Templete loaded!'
        if locList == None:
            raise RuntimeError, 'Oops! Ther is no locators to get the infomation!'

        amount = 0
        total = len(locList)
        mc.progressWindow(title='Building Sub Controller...',
                          min=0,max=total,
                          progress=amount,
                          status='Starting...',
                          isInterruptable=1)
        startTime = time()
        
        meshShape = mc.listRelatives(mesh, s= True)[0]
        bsNodes = mc.listConnections(meshShape, s = False, d = True, type = 'blendShape')
        if bsNodes == None:
            subMesh = mc.duplicate(mesh, n = '%s_subGeo'%mesh)[0]

            bsnode = mc.blendShape(mesh, subMesh, n = 'subBS_On_Off', foc = True)[0]
            mc.setAttr('%s.%s'%(bsnode, mesh), 1)
            mc.hide(subMesh)
        else:
            subMesh = mc.listConnections(bsNodes[0], s = False, d = True, type = 'mesh')[0]
        cpom, positionNode = self.cpomNode(mesh)
        if mc.getAttr(g.CENTER_LOC + '.v') == 0:
            mc.showHidden(g.CENTER_LOC)
            maxX = mc.getAttr(g.CENTER_LOC + '.boundingBox.boundingBoxMax.boundingBoxMaxX')
            minX = mc.getAttr(g.CENTER_LOC + '.boundingBox.boundingBoxMin.boundingBoxMinX')
            mc.hide(g.CENTER_LOC)
        else:
            maxX = mc.getAttr(g.CENTER_LOC + '.boundingBox.boundingBoxMax.boundingBoxMaxX')
            minX = mc.getAttr(g.CENTER_LOC + '.boundingBox.boundingBoxMin.boundingBoxMinX')
        dis = abs(maxX - minX)
        BBSX = mc.getAttr(g.JOINT_CTRL_GRP + '.scaleX')
        BBSY = mc.getAttr(g.JOINT_CTRL_GRP + '.scaleY')
        BBSZ = mc.getAttr(g.JOINT_CTRL_GRP + '.scaleZ')
        boundingBoxScale = (BBSX + BBSY +BBSZ) / 3
        scaleValue = boundingBoxScale * dis * 0.03
        softArea = softArea * dis * boundingBoxScale / 4
        # Create the subBaseJnt to get the rest weights
        subBaseJnt = 'subBaseJnt'
        state = mc.symmetricModelling(query=True, symmetry=True)
        if not mc.objExists(subBaseJnt):
            mc.select(cl = True)
            subBaseJnt = mc.joint(n = subBaseJnt)
            subBaseJntGrp = mc.group(subBaseJnt, n = subBaseJnt + '_zero')
            mc.delete(mc.pointConstraint( g.HEAD_SKIN_JNT_GRP,subBaseJntGrp ))
            mc.parent( subBaseJntGrp, g.SUB_CTRL_GRP )
            #mc.parent(subBaseJnt, g.HEAD_SKIN_JNT_GRP)
            #mc.setAttr(subBaseJnt + '.t', 0,0,0)
            skinCluster = mc.skinCluster(subBaseJnt, mesh, tsb = True, n = 'subSkinCluster')[0]
            mc.hide(subBaseJnt)
        else:
            skinCluster = mc.listConnections(subBaseJnt, s = False, d = True, type = 'skinCluster')[0]
        
        # Start the loop
        for loc in locList:
            if mc.progressWindow( query=True, isCancelled=True ) :
                done = 0
                break
            vtxName, posC, pU, pV = self.LockPosition(mesh, loc, cpom, positionNode)
            mc.select(cl = True)
            deformer = self.createJoint(loc, posC, mesh)
            self.selectVtx(vtxName, softArea)
            self.setJntWeight(deformer, skinCluster)
            self.ctrlCreate(g.FACE_ROOT_LOC, posC, scaleValue, loc, cpom, pU, pV, subMesh, deformer)
            amount += 1
            localTime = time()
            speed = (localTime - startTime) / amount / 60.0
            remainTime = (total - amount) * speed
            #mc.progressWindow( edit=True, progress=amount, status=('Completed: %d/%d (%d%%) Remain:%.2fm'%(amount,total,amount*100.0/total, remainTime) ) )
            m = int(remainTime)
            s = int((remainTime-m)*60)
            st = ''
            if m==1:
                st += str(m)+'m'
            elif m>1:
                st += str(m)+'m'
            if s==1:
                st += str(s)+'s'
            elif s>1:
                st += str(s)+'s'
            mc.progressWindow( edit=True, progress=amount, status=('Completed: %d/%d %s Remaining'%(amount,total, st) ) )
            done = 1
        mc.delete(cpom, positionNode)
        if done:
            mc.hide(g.CENTER_LOC)
            mc.hide()
        mc.progressWindow(endProgress=1)
        mc.symmetricModelling(symmetry=state)
        mc.softSelect(softSelectEnabled = False)
        mc.progressWindow(endProgress=1)
        


#--------------------------------
# Lock the position
#--------------------------------

    def LockPosition(self, mesh, loc, cpom, positionNode):
        meshShape=mc.listRelatives(mesh,shapes=True)
        
        mc.delete(mc.pointConstraint(loc, positionNode))
        pos = mc.xform(positionNode, q=True, ws=True, t=True)
        num = mc.getAttr((cpom + ".closestVertexIndex"))
        pU = mc.getAttr(cpom + '.parameterU')
        pV = mc.getAttr(cpom + '.parameterV')
        vtxName = mesh + '.vtx[' + str(num) +']'
        return vtxName, pos, pU, pV
 
    def createJoint(self, loc, pos, mesh):
        subJnt = mc.joint(n = loc.replace('Loc', 'Jnt'))
        subJntGrp = mc.group(subJnt, n = subJnt + '_zero')
        mc.setAttr('%s.radius'%subJnt, 0.3)
        mc.xform(subJntGrp, ws = True, t = (pos[0], pos[1], pos[2]))
        his = mc.listHistory(mesh,levels=2)
        skinClusters = [i for i in his if mc.nodeType(i)== 'skinCluster']
        if skinClusters != []:
            skinCluster = skinClusters[0]
            mc.skinCluster(skinCluster, e = True, ug = True, dr = 30, ps = 0, ns = 10, lw = True, wt = 0, ai = subJnt)
        else:
            pass
        mc.select(cl=True)
        return subJnt
    
    def selectVtx(self, vtxName, softArea):
        mc.select(vtxName)
        mc.symmetricModelling(e = 1, symmetry = 0)
        mc.softSelect(softSelectEnabled = True)
        #mm.eval('setSoftSelectFalloffMode( "Surface")')
        mc.softSelect(softSelectDistance = softArea)
        mc.softSelect(softSelectFalloff = 1)
    
    def setJntWeight(self, jnt, jntSet):
 
        selection = mc.ls(sl=True)
         
        # Strip selection of any attributes
        sel = string.split(selection[0], '.')
         
        richSel = om.MRichSelection()
        om.MGlobal.getRichSelection(richSel)
         
        richSelList = om.MSelectionList()
        richSel.getSelection(richSelList)
         
        path = om.MDagPath()
        component = om.MObject()
        richSelList.getDagPath(0, path, component)
         
        componentFn = om.MFnSingleIndexedComponent(component)
        
        mc.select (selection[0], r=True)
        for i in range(0,componentFn.elementCount()):
           weight = componentFn.weight(i)
           v = componentFn.element(i)
           w = weight.influence()
           #print "The selection weight of vertex %d is %f." % (v, w)
           vtx = (sel[0]+'.vtx[%d]') % v
           mc.skinPercent(jntSet, vtx, transformValue = [(jnt, w)])
        mc.select(cl = True)

        
        
    ## | Create cpom Node| #
    def cpomNode(self, mesh):
        meshShape = mc.listRelatives(mesh, shapes = 1)[0]
        cpom = mc.createNode('closestPointOnMesh')
        try:
            mc.connectAttr(meshShape + '.worldMesh[0]', cpom+ '.inMesh')
            mc.connectAttr(meshShape + '.worldMatrix[0]', cpom+ '.inputMatrix')
        except:
            pass
    
        positionNode=mc.createNode('transform')
        #mc.delete(mc.pointConstraint(locObj, positionNode))
        mc.connectAttr(positionNode+'.t', cpom + '.inPosition')
        #pos = mc.xform(positionNode, q=True, ws=True, t=True)
        #pU = mc.getAttr(cpom + '.parameterU')
        #pV = mc.getAttr(cpom + '.parameterV')
        #mc.delete(positionNode)
        #mc.delete(cpom)
        return cpom, positionNode
    
    # +-----------------------------+ #
    # |    Create The Controller    | #
    # +-----------------------------+ #
    def ctrlCreate(self, orientConObj, posC, scaleValue, loc, cpom, pU, pV, subMesh, deformer):

        #get the position of the UV of the cluster
        subMeshShape = mc.listRelatives(subMesh, s = True)
    
        #create the follicle
    
        fols = mc.createNode('follicle',n = loc.replace('Loc', 'subFolShape'))
        fol = mc.listRelatives(fols, parent=True)
        mc.connectAttr(subMeshShape[0]+'.outMesh',fols+'.inputMesh')
        mc.connectAttr(subMeshShape[0]+'.worldMatrix[0]',fols+'.inputWorldMatrix')
        mc.connectAttr(fols+'.outTranslate',fol[0]+'.translate')
        mc.connectAttr(fols+'.outRotate',fol[0]+'.rotate')
        mc.setAttr(fols+'.parameterU',pU)
        mc.setAttr(fols+'.parameterV',pV)
        
        mc.setAttr(fol[0]+'.visibility',0)
        tAttrs = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v']
        [mc.setAttr(fol[0] + tAttr,lock=True,keyable=False,channelBox=False) for tAttr in tAttrs]

    
        attrs=['rsp','ptl','sim','sdr','fld','ovd','cld','dmp','stf','lfl','cwm','sct','ad','dml','cml','ctf','brd','cbl','cr','cg','cb','fsl','sgl','sdn','dgr','cw']
        for attr in attrs:
            mc.setAttr((fols+'.'+attr),lock=True,keyable=False,channelBox=False)
    
        # Create the controller
        ctrl = mc.curve(n=loc.replace('Loc', 'subCtrl'), d=1,p = [(0.5, 0.5, -0.5), (0.5, 0.5, 0.5), 
                            (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), 
                            (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), 
                            (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), 
                            (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
                            (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), 
                            (0.5, 0.5, 0.5), (0.5, 0.5, -0.5)], 
                            k = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])
        ctrlShape = mc.listRelatives(ctrl, shapes = True)[0]
        mc.rename(ctrlShape, loc.replace('Loc', 'subCtrlShape'))
        
        mc.scale(scaleValue, scaleValue, scaleValue, ctrl)
        mc.makeIdentity(ctrl, apply = True, s = 1, n = 0)
        
        grpMid = mc.group(ctrl, n = ctrl+'_neg')
        grpTop = mc.group(grpMid, n = ctrl+'_fol')
        mc.xform(grpTop, ws=True, t=(posC[0], posC[1], posC[2]))
        mc.pointConstraint(fol[0],grpTop,mo=True,weight=1)
        if len(orientConObj) == 0:
            mc.orientConstraint(sel[0],grpTop,mo=True,weight=1)
            
        else:
            mc.orientConstraint(orientConObj,grpTop,mo=True,weight=1)
        mc.connectAttr(ctrl+'.t', deformer+'.t', force = True)
        mc.connectAttr(ctrl+'.r', deformer+'.r', force = True)
        mc.connectAttr(ctrl+'.s', deformer+'.s', force = True)
    
        # Create the *+/ node
        mdNode = mc.createNode('multiplyDivide',n = 'md_neg_' + ctrl)
        mc.connectAttr(ctrl + '.t',mdNode + '.input1',force=True)
        mc.setAttr(mdNode + '.input2X',-1)
        mc.setAttr(mdNode + '.input2Y',-1)
        mc.setAttr(mdNode + '.input2Z',-1)
        mc.connectAttr(mdNode+'.output',grpMid+'.t')
    
        # Change the order of the history
        if deformer == 'cluster':
            hisList = mc.listHistory(mesh,pdo = True)
            clus = mc.listConnections(defromer, s = False, d = True, type = 'cluster')[0]
            for his in hisList:
                hisType = mc.nodeType(his)
                if hisType == 'skinCluster' :
                    mc.reorderDeformers(his,clus, mesh)
        print fol, fol[0], 'foooo'
        # +----------Set To Group----------+ #
            
        folGRP = 'subFolGRP'
        if mc.objExists(folGRP): 
            mc.parent(fol[0],folGRP)
        else:
            mc.createNode( 'transform', n= folGRP, p = g.SUB_CTRL_GRP)
            mc.parent(fol[0],folGRP)
        mc.setAttr(folGRP + '.inheritsTransform', 0)
        
        ctrlGRP = g.SUB_CTRL_LIST_GRP
        if mc.objExists(ctrlGRP):
            mc.parent(grpTop,ctrlGRP)
        else:
            mc.createNode( 'transform', n= ctrlGRP, p = g.SUB_CTRL_GRP)
            mc.parent(grpTop,ctrlGRP)
            
        subJntGRP = 'subJntGRP'
        deformerGrp = mc.listRelatives(deformer, p = True)[0]
        if mc.objExists(subJntGRP):
            mc.parent(deformerGrp,subJntGRP)
        else:
            mc.createNode( 'transform', n= subJntGRP, p = g.SUB_CTRL_GRP)
            mc.parent(deformerGrp,subJntGRP)
            mc.hide(subJntGRP)
        #mc.setAttr(subJntGRP + '.inheritsTransform', 0)
            
        # ------------------Lock And Hide The Attrs---------------------- #
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        [mc.setAttr('%s.%s' % (obj, attr), lock = True, keyable = False, channelBox = False) for obj in [grpMid, grpTop] for attr in attrs]
        
        # ----------------Deal With The Loc----------------------------#
        mc.parent(loc, ctrl)
        mc.hide(loc)
        
        mc.select(cl = True)
        
    def removeSub(self):
        selList = mc.ls(sl = True)
        for obj in selList:
            objShape = mc.listRelatives(obj, shapes = True)
            objType = mc.nodeType(objShape)
            if objType != u'nurbsCurve':
                raise RuntimeError, 'This function just can be used on the subController with the nurbsCurve shape!'
            topGrp = obj + '_fol'
            relObj = mc.listConnections(obj, d = True)
            con = mc.listConnections(topGrp, s = True)[0]
            folObj = mc.listConnections(con + '.target[0].targetParentMatrix', s = True)[0]
            folObjS = mc.listConnections(folObj, s = True)[0]
            jntObj = mc.listConnections(obj, d = True, type = 'joint')[0]
            jntGrp = mc.listRelatives(jntObj, p = True)[0]
            skinClus = mc.listConnections(jntObj, s = False, d = True, type = 'skinCluster')[0]
            infList = mc.skinCluster(skinClus, q = True, inf = True)
            for inf in infList:
                mc.skinCluster(skinClus, e = True, lw = False, inf = inf)
            mc.skinCluster(skinClus, e = True, ri = jntObj)
            mc.delete(obj, topGrp, relObj, folObj, folObjS, jntGrp)        
    
    def snapToGeo(self, mesh, locList):
        if mesh == '' :
            raise RuntimeError, 'Fuck, There is no model assigned!'
        mc.waitCursor( state=True )
        if mesh == '' :
            raise RuntimeError, 'Fuck, There is no model assigned!'
            
        meshShape=mc.listRelatives(mesh,shapes=True)
        for loc in locList:
            cpom = mc.createNode('closestPointOnMesh')
        
            mc.connectAttr((meshShape[0]+'.worldMesh[0]'),(cpom+'.inMesh'))
            #mc.connectAttr(meshShape[0]+'.worldMatrix[0]',cpom+'.inputMatrix')
            
            positionNode=mc.createNode('transform')
            mc.pointConstraint(loc, positionNode)
            mc.connectAttr((positionNode+'.t'), cpom + '.inPosition')
            
            mc.delete(mc.pointConstraint(loc, positionNode))
            
#            i = 0
            while 1:

                cpomPZ = mc.getAttr(cpom + '.positionZ')

                mc.setAttr(positionNode + '.tz', cpomPZ)
                traP = mc.xform(positionNode, q = True, ws = True, t = True)
                traPX = traP[0]
                traPY = traP[1]
                traPZ = traP[2]
                cpomPX = mc.getAttr(cpom + '.positionX')
                cpomPY = mc.getAttr(cpom + '.positionY')
                cpomPZ = mc.getAttr(cpom + '.positionZ')
                
                dis = ((traPX - cpomPX) ** 2 + (traPY - cpomPY) ** 2 + (traPZ - cpomPZ) ** 2) ** 0.5
                if abs(cpomPZ - traPZ) <= 0.000001:
                    if dis <= 0.001:
                        break
                    else:
                        string = 'warning "The locator %s is not on the mesh!" '% loc
                        mm.eval(string)
                        break
                
#                i += 1
            mc.delete(mc.pointConstraint(positionNode, loc))
            
            mc.delete(cpom)
            mc.delete(positionNode)
        mc.waitCursor( state=False )
                
    # | From The Rig Back To The Preview |

    def subLocReset(self, mesh):

        selList = mc.ls(sl = True)
        if len(selList) != 0:
            locList = []
            for obj in selList:
                locs = u.getNodeInGrp(obj, 'locator')
                locList.append(locs[0])
        else:
            #print 'hello'
            subLocChn = mc.listRelatives(g.SUB_LOC_GRP)
            if subLocChn == None:
                raise RuntimeError, 'Oops! Ther is no sub Templete loaded!'
            locList = u.getNodeInGrp(g.SUB_CTRL_LIST_GRP, 'locator')
        locNums = len(u.getNodeInGrp(g.SUB_CTRL_LIST_GRP, 'locator'))
        # | Loc Back |
        for loc in locList:
            parentGrp = loc + '_zero'
            if mc.objExists(parentGrp) == 0:
                parentGrp = mc.createNode('transform', n = parentGrp, p = g.FACE_LOC_GRP)
                pos = mc.xform(loc, q = True, ws = True, t = True)
                mc.xform(parentGrp, ws = True, t = pos)
                mc.pointConstraint(g.CENTER_LOC, parentGrp)
            ctrlObj = mc.listRelatives(loc, p = True)
            mc.showHidden(loc)
            mc.parent(loc, parentGrp)
            mc.select(ctrlObj)
            self.removeSub()
            #pointConstraint(center, locGrp, mo = 1)
        
        delObjs = mc.listRelatives(g.SUB_CTRL_GRP, c = True)
        delObjs.remove(g.SUB_LOC_GRP)
        if len(locList) == locNums:
            shape = mc.listRelatives(mesh, s = True)[0]
            skinCluster = mc.listConnections(shape, s = True, d = False, type = 'skinCluster')[0]
            print 'skinCluster: ',skinCluster
            mc.skinCluster(skinCluster, e = True, ub = True)
            try:
                mc.delete('subBaseJnt')
            except:
                pass
            mc.showHidden(g.CENTER_LOC)
            mc.select(g.CENTER_LOC)
            [mc.delete(obj) for obj in delObjs]
            
    # | Add The Extra Locator |
    def addLoc(self):
        extLoc = mc.spaceLocator(n = 'extraLoc#')[0]
        extLocGrp = mc.group(extLoc, n = extLoc + '_zero')
        mc.parent(extLocGrp, g.FACE_LOC_GRP)
        mc.setAttr(extLocGrp + '.t', 0, 0, 0)
        [mc.setAttr(extLoc + '.' + attr, 0.2) for attr in ['localScaleX', 'localScaleY', 'localScaleZ']]
        mc.pointConstraint(g.CENTER_LOC, extLocGrp, mo = 1)
        mc.select(extLoc)
        
    # | Remove The Locator |
    def removeLoc(self):
        selList = mc.ls(sl = True)
        for loc in selList:
            locGrp = mc.listRelatives(loc, parent = True)[0]
            mc.delete(locGrp)
        
        