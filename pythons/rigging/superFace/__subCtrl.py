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
			#attrs = mc.listAttr(ctrl,k=1,u=1,v=1,s=1)
			#for attr in attrs:
			#	mc.setAttr('%s.%s'%(ctrl,attr),0)
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
		state = mc.symmetricModelling(query=True, symmetry=True)
		for loc in locList:
			if mc.progressWindow( query=True, isCancelled=True ) :
				done = 0
				break
			vtxName, posC, pU, pV = self.LockPosition(mesh, loc, cpom, positionNode)

			if int(mc.about(v=1).split()[0]) > 2008:
				self.selectVtx(vtxName, softArea)
				self.SoftToCluster(loc)
			else:
				self.softToCluster2(loc, vtxName, softArea)
			self.ctrlCreate(g.SUB_CTRL_ORIENTER, posC, scaleValue, loc, cpom, pU, pV, mesh, subMesh)
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
		mc.symmetricModelling(symmetry=state)
		mc.softSelect(softSelectEnabled = False)
		mc.progressWindow(endProgress=1)
		


#--------------------------------
# Lock the position
#--------------------------------

	def LockPosition(self, mesh, loc, cpom, positionNode):
		
		## Get The Position Of The Loc
		#pos = mc.xform(loc, q = True, ws = True, t = True)
		
		## Get The Closest Point On The Mesh
		meshShape=mc.listRelatives(mesh,shapes=True)
		
		mc.delete(mc.pointConstraint(loc, positionNode))
		#mc.connectAttr((meshShape[0]+'.worldMesh[0]'),(cpom+'.inMesh'))
		#mc.connectAttr(meshShape[0]+'.worldMatrix[0]',cpom+'.inputMatrix')
		
		#positionNode=mc.createNode('transform')
		#mc.pointConstraint(loc, positionNode)
		#mc.connectAttr((positionNode+'.t'), cpom + '.inPosition')
		pos = mc.xform(positionNode, q=True, ws=True, t=True)
		num = mc.getAttr((cpom + ".closestVertexIndex"))
		pU = mc.getAttr(cpom + '.parameterU')
		pV = mc.getAttr(cpom + '.parameterV')
		#print num
		#mc.delete(positionNode)
		#mc.delete(cpom)
		vtxName = mesh + '.vtx[' + str(num) +']'
		return vtxName, pos, pU, pV

	#--------------------------------
	# Change the soft to cluster
	#--------------------------------

	def SoftToCluster(self, loc):
	
		selection = mc.ls(sl=True)
		
		if 'vtx' not in selection[0]:
			raise RuntimeError , 'You must select a vertex first! '
	
		# +-----------------------------------+
		# |Strip selection of any attributes  |
		# +-----------------------------------+
	
		sel = string.split(selection[0], '.')
	 
		richSel = om.MRichSelection()
		om.MGlobal.getRichSelection(richSel)
	 
		richSelList = om.MSelectionList()
		richSel.getSelection(richSelList)
	 
		path = om.MDagPath()
		component = om.MObject()
		richSelList.getDagPath(0, path, component)
	 
		componentFn = om.MFnSingleIndexedComponent(component)
	 
		cluster = mc.cluster(n = loc.replace('Loc', 'subCluster'), rel=True )
		clusterSet = mc.listConnections( cluster, type="objectSet" )
	 
		mc.select (selection[0], r=True)
		for i in range(0,componentFn.elementCount()):
			weight = componentFn.weight(i)
			v = componentFn.element(i)
			w = weight.influence()
			#print "The selection weight of vertex %d is %f." % (v, w)
			vtx = (sel[0]+'.vtx[%d]') % v
			mc.sets(vtx, add=clusterSet[0])
			mc.percent(cluster[0], vtx,  v=w )
		

		mc.select(cluster)
		return cluster
		print 'Conversion complete'
		
	def selectVtx(self, vtxName, softArea):
		
		mc.select(vtxName)
		mc.symmetricModelling(e = 1, symmetry = 0)
		mc.softSelect(softSelectEnabled = True)
		#mm.eval('setSoftSelectFalloffMode( "Surface")')
		mc.softSelect(softSelectDistance = softArea)
		mc.softSelect(softSelectFalloff = 1)
		
	def returnVtx(self, vtxName, softArea):
		
		mc.select(vtxName)
		orgPos = mc.xform(vtxName, q = True, ws = True, t = True)
		vtxList = [vtxName]
		while 1:
			key = True
			selList = mc.ls(sl = True, fl = True)
			mm.eval('GrowPolygonSelectionRegion')
			newSelList = mc.ls(sl = True, fl = True)
			for item in newSelList:
				if item not in selList:
					vtxPos = mc.xform(item, q = True, ws = True, t = True)
					dis = ((vtxPos[0] - orgPos[0])**2 + (vtxPos[1] - orgPos[1])**2 + (vtxPos[2] - orgPos[2])**2) ** 0.5
					if dis < softArea:
						vtxList.append(item)
						key = False
			if key == 1:
				mc.select(cl = True)
				return vtxList		
			
	def softToCluster2(self, loc, vtxName, softArea):
		
		cluster = mc.cluster(vtxName, n = loc.replace('Loc', 'subCluster'), rel=True )
		clusterSet = mc.listConnections( cluster, type="objectSet" )
		vtxList = self.returnVtx(vtxName, softArea)
		orgPos = mc.xform(vtxName, q = True, ws = True, t = True)
		for item in vtxList:
			vtxPos = mc.xform(item, q = True, ws = True, t = True)
			weight = ( (softArea - ((vtxPos[0] - orgPos[0])**2 + (vtxPos[1] - orgPos[1])**2 + (vtxPos[2] - orgPos[2])**2) ** 0.5) / softArea ) ** 0.5
			#currentDis = ((vtxPos[0] - orgPos[0])**2 + (vtxPos[1] - orgPos[1])**2 + (vtxPos[2] - orgPos[2])**2) ** 0.5
			#string = "vector $tmp = hermite(<<0, 1, 0>>,<<%g, 0, 0>>,<<1, 0, 0>>,<<1, 0, 0>>, %g)" % (softArea, currentDis)
			#vector = mm.eval(string)
			#print currentDis
			#print vector
			#weight = vector[1]
			#print "The selection weight of vertex %d is %f." % (item, weight)
			mc.sets(item, add = clusterSet[0])
			mc.percent(cluster[0], item, v = weight)
		mc.select(cluster)			
		
		
	def clusterToList(self):
		sel = mc.ls(sl=True)
		if len(sel) > 1:
			cluster = sel
			return cluster
		else:
			clusterNode = mc.listConnections(sel[0],d = True, type='cluster')
			cluster = [clusterNode[0] , sel[0]]
			
		return cluster
		
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
	def ctrlCreate(self, orientConObj, posC, scaleValue, loc, cpom, pU, pV, mesh, subMesh):

		#------------------------------------------
		#get the position of the UV of the cluster
		#------------------------------------------

		cluster=self.clusterToList()
		mc.hide(cluster)
		meshShape=mc.listRelatives(mesh,shapes=True)
		subMeshShape = mc.listRelatives(subMesh, s = True)
		#mc.delete(mc.pointConstraint(cluster[1], positionNode))
		#pos = mc.xform(positionNode, q=True, ws=True, t=True)
		#pU = mc.getAttr(cpom + '.parameterU')
		#pV = mc.getAttr(cpom + '.parameterV')
	
		#-----------------------
		#create the follicle
		#-----------------------
	
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
	
		#------------------------
		# Create the controller
		#------------------------
		
		#getAttr "subLocGrp.boundingBox.boundingBoxMin.boundingBoxMinX"
		#getAttr "subLocGrp.boundingBox.boundingBoxMax.boundingBoxMaxX"

		
		ctrl = mc.curve(n=loc.replace('Loc', 'Ctrl'), d=1,p = [(0.5, 0.5, -0.5), (0.5, 0.5, 0.5), 
							(0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), 
							(-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), 
							(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), 
							(-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
							(0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), 
							(0.5, 0.5, 0.5), (0.5, 0.5, -0.5)], 
							k = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])
		ctrlShape = mc.listRelatives(ctrl, shapes = True)[0]
		mc.rename(ctrlShape, loc.replace('Loc', 'CtrlShape'))
		
		mc.scale(scaleValue, scaleValue, scaleValue, ctrl)
		mc.makeIdentity(ctrl, apply = True, s = 1, n = 0)
		
		grpMid = mc.group(ctrl, n = ctrl+'_neg')
		grpTop = mc.group(grpMid, n = ctrl+'_fol')
		mc.xform(grpTop, ws=True, t=(posC[0], posC[1], posC[2]))
		#rotY = mc.getAttr(fol[0] + '.ry')
		#mc.setAttr(grpTop + '.ry', rotY * -1)
		#mc.delete(mc.orientConstraint(fol[0], grpTop, offset = (0,0,0), skip = 'x', sk='z', weight = 1))
		mc.pointConstraint(fol[0],grpTop,mo=True,weight=1)
		if len(orientConObj) == 0:
			mc.orientConstraint(sel[0], grpTop, mo=True, weight=1)
			mc.scaleConstraint(sel[0], grpTop, mo=True, weight=1)
		else:
			mc.orientConstraint(orientConObj, grpTop, mo=True, weight=1)
			mc.scaleConstraint(orientConObj, grpTop, mo=True, weight=1)

		mc.connectAttr(ctrl+'.t', cluster[1]+'.t', force = True)
		mc.connectAttr(ctrl+'.r', cluster[1]+'.r', force = True)
		mc.connectAttr(ctrl+'.s', cluster[1]+'.s', force = True)
	
		#------------------------
		# Create the *+/ node
		#------------------------
	
		mdNode = mc.createNode('multiplyDivide',n = 'md_neg_' + ctrl)
		mc.connectAttr(ctrl + '.t',mdNode + '.input1',force=True)
		mc.setAttr(mdNode + '.input2X',-1)
		mc.setAttr(mdNode + '.input2Y',-1)
		mc.setAttr(mdNode + '.input2Z',-1)
		mc.connectAttr(mdNode+'.output',grpMid+'.t')
	
		#---------------------------------
		# Change the order of the history
		#---------------------------------
	
		hisList = mc.listHistory(mesh,pdo = True)
		for his in hisList:
			hisType = mc.nodeType(his)
			if hisType == 'skinCluster' :
				mc.reorderDeformers(his,cluster[0], mesh)
				
		# +----------Set To Group----------+ #
		clusGRP = 'ClusterGRP'
		if mc.objExists(clusGRP):
			mc.parent(cluster[1],clusGRP)
		else:
			mc.createNode( 'transform', n= clusGRP, p = g.SUB_CTRL_GRP)
			mc.parent(cluster[1],clusGRP)
		mc.setAttr(clusGRP + '.inheritsTransform', 0)
		    
		folGRP = 'FolGRP'
		ctrlGRP = g.SUB_CTRL_LIST_GRP
		    
		if mc.objExists(folGRP):
		        
			mc.parent(fol[0],folGRP)
		else:
			mc.createNode( 'transform', n= folGRP, p = g.SUB_CTRL_GRP)
			mc.parent(fol[0],folGRP)
		mc.setAttr(folGRP + '.inheritsTransform', 0)
		

		if mc.objExists(ctrlGRP):
			mc.parent(grpTop,ctrlGRP)
		else:
			mc.createNode( 'transform', n= ctrlGRP, p = g.SUB_CTRL_GRP)
			mc.parent(grpTop,ctrlGRP)
			
		# ------------------Lock And Hide The Attrs---------------------- #
		attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
		[mc.setAttr('%s.%s' % (obj, attr), lock = True, keyable = False, channelBox = False) for obj in [grpMid, grpTop] for attr in attrs]
		
		[mc.setAttr('%s.%s' % (ctrl, at), lock = True, keyable = False, channelBox = False) for at in ['sx', 'sy', 'sz', 'v']]
		
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
			clusObj = mc.listConnections(obj, d = True)[0]
			print folObj
			mc.delete(obj, topGrp, relObj, folObj, folObjS, clusObj)
			
	def setWeight(self, skinGeo, softArea):
		subCtrlList = u.getNodeInGrp(g.SUB_CTRL_GRP, 'nurbsCurve')
		selList = mc.ls(sl = True)
		if selList == None:
			raise RuntimeError, 'There is no ctrl selected!'
		for obj in subCtrlList:
			if obj not in selList:
				warningString = 'warning "The object %s is fit the condition"' % obj
				mm.eval(warningString)
				continue
			else:
				self.setWeightFn(skinGeo, obj, softArea)
	def setWeightFn(self, skinGeo, ctrl, softArea):
		mc.waitCursor( state=True )
		cpom, positionNode = self.cpomNode(skinGeo)
		if int(mc.about(v=1).split()[0]) > 2008:
			# Get info ---> skinGeo, vtxName, orgMesh, orgVtxName, eVtxList, cluster, clusterSet
			vtxName = self.LockPosition(skinGeo, ctrl, cpom, positionNode)[0]
			orgMeshes = mc.listRelatives(skinGeo, shapes = True)
			if len(orgMeshes) > 1:
				orgMesh = orgMeshes[1]
			else:
				orgMesh = orgMeshes[0]
			orgVtxName = vtxName.replace(skinGeo, orgMesh)
			clusterHandle = mc.listConnections(ctrl, d = True, type = 'transform')[0]
			cluster = mc.listConnections(clusterHandle, d = True, type = 'cluster')[0]
			clusterSet = mc.listConnections( cluster, type="objectSet" )[0]
			
			# | Select orgVtxName and get the information of the vertexes and the soft value |
			self.selectVtx(orgVtxName, softArea)
			
			selection = mc.ls(sl=True)
			
			if 'vtx' not in selection[0]:
				raise RuntimeError , 'You must select a vertex first! '
				
			# |Strip selection of any attributes  |
			sel = string.split(selection[0], '.')
		 
			richSel = om.MRichSelection()
			om.MGlobal.getRichSelection(richSel)
		 
			richSelList = om.MSelectionList()
			richSel.getSelection(richSelList)
		 
			path = om.MDagPath()
			component = om.MObject()
			richSelList.getDagPath(0, path, component)
		 
			componentFn = om.MFnSingleIndexedComponent(component)
		 
		 	vtxList = []
		 	weightList = []
		 
			mc.select (selection[0], r=True)
			for i in range(0,componentFn.elementCount()):
				weight = componentFn.weight(i)
				v = componentFn.element(i)
				w = weight.influence()
				#print "The selection weight of vertex %d is %f." % (v, w)
				vtx = (sel[0]+'.vtx[%d]') % v
				
				vtxList.append(vtx)
				weightList.append(w)
			
		else:
			vtxList = self.returnVtx(vtxName, softArea)
			weightList = []
			orgPos = mc.xform(vtxName, q = True, ws = True, t = True)
			for item in vtxList:
				vtxPos = mc.xform(item, q = True, ws = True, t = True)
				weight = (softArea - ((vtxPos[0] - orgPos[0])**2 + (vtxPos[1] - orgPos[1])**2 + (vtxPos[2] - orgPos[2])**2) ** 0.5) / softArea
				weightList.append(weight)
			
		# Get the influence vertex in the set
		eVexList = mc.sets(clusterSet, q = True)
		eVexList = mc.ls(eVexList, fl = True)
		
		# Remove the old vertexes and add the new vertexes
		[mc.sets(item, rm = clusterSet) for item in eVexList if item != vtxName]
		for i in range(len(vtxList)):
			vtx = vtxList[i].replace(orgMesh, skinGeo)
			if vtx != vtxName:
				mc.sets(vtx, add = clusterSet)
				mc.percent(cluster, vtx, v = weightList[i])
		mc.select(ctrl)
		mc.waitCursor( state=False )
		
	
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
			
#			i = 0
			while 1:

				cpomPZ = mc.getAttr(cpom + '.positionZ')
#				traP = mc.xform(positionNode, q = True, ws = True, t = True)
#				traPZ = traP[2]
#				if abs(cpomPZ - traPZ) <= 0.000001:
#					string = 'warning "The locator %s is not on the mesh!" '% loc
#					mm.eval(string)
#					break
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
				
#				i += 1
			mc.delete(mc.pointConstraint(positionNode, loc))
			
			mc.delete(cpom)
			mc.delete(positionNode)
		mc.waitCursor( state=False )
				
	# | From The Rig Back To The Preview |

	def subLocReset(self, model):

		selList = mc.ls(sl = True)
		if len(selList) != 0:
			locList = []
			for obj in selList:
				locs = u.getNodeInGrp(obj, 'locator')
				locList.append(locs[0])
		else:
			print 'hello'
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
			mc.showHidden(g.CENTER_LOC)
			mc.select(g.CENTER_LOC)
			[mc.delete(obj) for obj in delObjs]
			
	# | Add The Extra Locator |
	def addLoc(self):
		extLoc = mc.spaceLocator(n = 'extraLoc#')[0]
		extLocGrp = mc.group(extLoc, n = extLoc + '_zero')
		mc.parent(extLocGrp, g.FACE_LOC_GRP)
		mc.setAttr(extLocGrp + '.t', 0, 0, 0)
		[mc.setAttr(extLoc + '.' + attr, 0.02) for attr in ['localScaleX', 'localScaleY', 'localScaleZ']]
		mc.pointConstraint(g.CENTER_LOC, extLocGrp, mo = 1)
		mc.select(extLoc)
		
	# | Remove The Locator |
	def removeLoc(self):
		selList = mc.ls(sl = True)
		for loc in selList:
			locGrp = mc.listRelatives(loc, parent = True)[0]
			mc.delete(locGrp)
		
	def subJointCtrl(self):
		pass