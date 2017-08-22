from sfGlobal import *
import maya.cmds as mc
import maya.mel as mm

class jointCtrl:
	locGrp = None
	rigGrp = None
	def getPosition(self,locator):
		return mc.xform(locator,q=1,ws=1,t=1)

	def checkState(self):
		return mc.objExists(self.rigGrp)
	
	def getLocList(self, grps):
		list = []
		for item in grps:
			loc = mc.listRelatives(item, c=1)
			if loc!=None:
				list.extend(loc)
		return list
	def getArgs(self, grps):
		list = []
		for item in grps:
			loc = mc.listRelatives(item, c=1)
			if loc!=None:
				list.append(loc)
		return list
	def getLocGrpList(self, grp):
		output = []
		if mc.objExists(grp):
			output = mc.listRelatives(grp,c=1)
			if output==None:
				output = []
		return output
	
	def mirror(self, arg=1):
		grpList = self.getLocGrpList(self.locGrp)               # getLocGrpList()
		list = self.getLocList(grpList)                 # getLocList()
		for obj in list:
			posObj = mc.xform(obj, q = True, ws = True, t = True)
			if g.LEFT_KEY in obj:
				if arg==1:
					mc.xform(obj.replace(g.LEFT_KEY,g.RIGHT_KEY), ws = True, t = (posObj[0] * -1, posObj[1], posObj[2]))
			elif g.RIGHT_KEY in obj:
				if arg==-1:
					mc.xform(obj.replace(g.RIGHT_KEY,g.LEFT_KEY), ws = True, t = (posObj[0] * -1, posObj[1], posObj[2]))
			else:
				mc.xform(obj, ws = True, t = (0, posObj[1], posObj[2]))
	def createAll(self):
		# [ [locName,...], ... ]
		locGrpList = self.getLocGrpList(self.locGrp)            # getLocGrpList()
		list = self.getArgs(locGrpList)
		for item in list:
			self.create(item)
		try:
			mc.delete(self.locGrp)
		except:
			pass
	def locBack(self):
		import utility as u
		locList = u.getNodeInGrp(self.rigGrp, 'locator')
		rigsGrp = mc.listRelatives(self.rigGrp, c = True)
		ctrlGrp = mc.listRelatives(self.rigGrp, p = True)[0]
		if mc.objExists(self.locGrp) == 0:
			mc.createNode('transform', n = self.locGrp, p = ctrlGrp)
		for loc in locList:
			for item in rigsGrp:
				string = 'isParentOf("%s", "%s")' % (item, loc)
				if mm.eval(string):
					locsGrp = item.replace('Rig', 'Loc')
					if mc.objExists(locsGrp) == 0:
						mc.createNode('transform', n = locsGrp, p = self.locGrp)
					mc.parent(loc, locsGrp)
					mc.showHidden(loc)
		mc.delete(self.rigGrp)
		mc.select(loc)

	def create(self, List):
		#[ locName, ... ]
		pass
	

class skinGeoASGoal:
	import goalCtrl as gc
	obj = gc.goalCtrl()
	def __init__(self):
		pass
	def convertSkinGeoToGoal(self, skinGeo):
		skinGeo, skinGeoShape, bsMesh, bsMeshShape, shownGeo, shownGeoShape, bsNode = self.getElements(skinGeo)
#		mc.disconnectAttr(bsNode + '.outputGeometry[0]', skinGeo + '.inMesh')
#		mc.connectAttr(bsNode + '.outputGeometry[0]', shownGeoShape + '.inMesh')
		mc.delete(bsNode)
		bsNode = mc.blendShape(bsMesh, shownGeo, n = 'BS_On_Off', foc = True)[0]
		mc.setAttr( '%s.%s'%(bsNode, bsMesh), 1 )
		print bsNode
		sorBSNodes = mc.listConnections(bsMeshShape, s = True, d = False, type = 'blendShape')
		if sorBSNodes == None:
			sorBSNode = mc.blendShape(skinGeo, bsMesh, n = 'BS_List', foc = True)[0]
			mc.setAttr( '%s.%s'%(sorBSNode, skinGeo), 1 )
		else:
			BSDict = self.gc.blendShapeData(BSNodes[0])
			#print 'BSDict',BSDict
			if BSDict == None:
				numKeys = 0
			else:
				keys = BSDict.keys()
				#print 'keys',keys
				indexList = []
				for key in keys:
					#print BSDict[key]
					indexList.append(BSDict[key][0])
				#print indexList
				numKeys = max(indexList) + 1
			#print numKeys,'lllllllllllllllllllllllllllllllllllllllllll'
			mc.blendShape(sorBSNodes[0], edit = True, t = (bsMesh, numKeys, skinGeo, 1))
		mc.hide(skinGeo)
		mc.select(cl = True)
		
	def getElements(self, skinGeo):
		skinGeoName = skinGeo
		skinGeoShape = mc.listRelatives(skinGeo, s = True)[0]
		bsMesh = self.obj.findBSGeo(skinGeo)
		print 'bsMesh: %s' % bsMesh
		bsMeshShape = mc.listRelatives(bsMesh, s = True)[0]
		orgShape = mc.listRelatives(skinGeo, s = True)[1]
		shownGeoShape, shownGeo = self.obj.createBSShape(orgShape)
		mc.select(cl=True)
		mc.setAttr(shownGeo + '.tx', 0)
		parent = mc.listRelatives(skinGeo, p = True)
		if parent != None:
			mc.parent(shownGeo, parent[0])
		else:
			mc.parent(shownGeo, w = True)
		his = mc.listHistory(skinGeo)
		bsNode = [i for i in his if mc.nodeType(i)== 'blendShape'][0]
		#bsNode = mc.listConnections(skinGeoShape, s = True, d = False, type = 'blendShape')[0]
		skinGeo = mc.rename(skinGeo, skinGeoName + '_Skin')
		shownGeoShape = mc.rename(shownGeoShape, skinGeoShape)
		shownGeo = mc.rename(shownGeo, skinGeoName)
		return skinGeo, skinGeoShape, bsMesh, bsMeshShape, shownGeo, shownGeoShape, bsNode