import maya.cmds as mc
class mirrorClusterFn:

	def mirrorCluster(self, meshObj, deriction):
		allHistory = mc.listHistory(meshObj)
		allCluster = []
		[allCluster.append(his) for his in allHistory if mc.nodeType(his) == 'cluster']
		allHandle = []
		[allHandle.append(mc.listConnections(item, s = 1, type = 'transform')) for item in allCluster]
		
		oneSideHandle = []
		if deriction == 1:
			[oneSideHandle.append(itemL) for itemL in allHandle if mc.getAttr(mc.listRelatives(itemL,s=1)[0] + '.originX') >= 0]
		if deriction == -1:
			[LHandle.append(itemL) for itemL in allHandle if mc.getAttr(mc.listRelatives(itemL,s=1)[0] + '.originX') <= 0]
		for obj in oneSideHandle:
			mc.waitCursor( state=True )
			self.mirrorClusterPitch(meshObj, obj[0], deriction)
			mc.waitCursor( state=False )

	#the main func
	def mirrorClusterPitch(self, meshObj,clusterHandle, deriction):
		mesh = mc.listRelatives(meshObj,s = 1,c = 1)[0]
		mirHandle, clusStr, clusSet = self.getMirCluster(mesh, clusterHandle)
		oldList = self.mirroClusterFilter(meshObj,clusterHandle)
		newList = []
		node = mc.createNode('closestPointOnMesh')
		try:
			mc.connectAttr((mesh + ".outMesh"),(node + ".inMesh"),f = 1)
			mc.select(cl = 1)
		except:
			pass
		for pair in oldList:
			
			pointPos = mc.pointPosition(pair[0],l = 1)
			
			#node = mc.createNode('closestPointOnMesh')
			
			mc.setAttr((node + ".inPosition"),-pointPos[0],pointPos[1],pointPos[2])
	#		if deriction == 1:
	#			mc.setAttr((node + ".inPosition"),-pointPos[0],pointPos[1],pointPos[2])
	#		elif deriction == 2:
	#			mc.setAttr((node + ".inPosition"),pointPos[0],-pointPos[1],pointPos[2])
	#		else:
	#			mc.setAttr((node + ".inPosition"),pointPos[0],pointPos[1],-pointPos[2])
			
			#try:
			#	mc.connectAttr((mesh + ".outMesh"),(node + ".inMesh"),f = 1)
			#	mc.select(cl = 1)
			#except:
			#	pass
			num = mc.getAttr((node + ".closestVertexIndex"))
			newPoint = (meshObj + ".vtx[" + str(num) + "]")
			pair[0] = newPoint
			newList.append(pair)
		mc.delete(node)
		useList = []
		if deriction > 0:
			[useList.append(item) for item in newList if mc.xform(item[0], q = 1, ws = 1, t = 1)[0] < 0]
		if deriction < 0:
			[useList.append(item) for item in newList if mc.xform(item[0], q = 1, ws = 1, t = 1)[0] > 0]
		#print useList
		#print len(useList)
#		if mirHandle == clusterHandle:
#			print 'OOOO'
#			[newList.append(item) for item in oldList if item not in newList]
#			print newList, 'LLLLLL'
#			print len(newList)
		amount = len(useList)
		newPoints = [useList[x][0] for x in range(amount)]

		#mc.sets(cl=clusSet)
		[mc.sets(newPoint,fe=clusSet) for newPoint in newPoints]
		[mc.percent(clusStr,useList[x][0],v = useList[x][1]) for x in range (amount)]
	
		mc.select(clusStr)
		print("done")
		
	
	#this func is in order to getting all vertex and its value of a cluster
	#require one preferences
	    
	def mirrorClusterDefine(self, clusterHandle):
	    
		clusDeformer = mc.listConnections(clusterHandle + ".worldMatrix[0]",type ="cluster",d = 1)
		#print clusDeformer
		
		clusSets = mc.listConnections(clusDeformer, type = "objectSet" )
		
		components = mc.sets(clusSets[0],q = 1)
		
		components = mc.filterExpand(components,sm = (28,31,36,46))
		#print components
		backTo = []
		for vertex in components:
			pair = [vertex]       
			valueW = mc.percent(clusDeformer[0],vertex,q = 1,v = 1)
			pair.append(valueW[0])
			backTo.append(pair)
		
		return backTo
	
	#sometime, a cluster may effect several object
	#in order to removing the unwanted vertexs,I create this func
	
	def mirroClusterFilter(self, meshObj, clusterHandle):
		CODEC = 'utf-8'
		backTo = self.mirrorClusterDefine(clusterHandle)
		returnTo = []
		
		for pair in backTo:
			name = pair[0].encode(CODEC)
			
			if name.startswith(meshObj):
				returnTo.append(pair)
		return returnTo
	
	def getClostestPoint(self, mesh, clusterHandle):
		cpom = mc.createNode('closestPointOnMesh')
		mc.connectAttr((mesh+'.worldMesh[0]'),(cpom+'.inMesh'))
		positionNode = mc.createNode('transform')
		mc.delete( mc.pointConstraint ( clusterHandle, positionNode ) )
		pos = mc.xform(positionNode, q=True, ws=True, t=True)
		mc.setAttr((cpom + ".inPosition"),pos[0],pos[1],pos[2])
		indexVer = mc.getAttr(cpom+'.closestVertexIndex')
		clusPoint = (mesh + ".vtx[" + str(indexVer) + "]")
		vtxPos = mc.getAttr(cpom + '.position')
		#mc.delete(cpom)
		mc.delete(positionNode)
		return cpom, clusPoint, vtxPos[0]
		
	def getMirCluster(self, mesh, clusterHandle):
		cpomM = self.getClostestPoint(mesh, clusterHandle)[0]
		px = mc.getAttr(cpomM + '.inPositionX')
		mc.setAttr(cpomM + '.inPositionX', px * -1)
	#	if direction == 1:
	#		px = mc.getAttr(cpomM + '.inPositionX')
	#		mc.setAttr(cpomM + '.inPositionX', px * -1)
	#	elif direction == 2:
	#		py = mc.getAttr(cpomM + '.inPositionY')
	#		mc.setAttr(cpomM + '.inPositionY', py * -1)
	#	else:
	#		pz = mc.getAttr(cpomM + '.inPositionZ')
	#		mc.setAttr(cpomM + '.inPositionZ', pz * -1)
		mirPos = mc.getAttr(cpomM + '.position')[0]
		mc.delete(cpomM)
		
		allHistory = mc.listHistory(mesh)
		allCluster = []
		[allCluster.append(his) for his in allHistory if mc.nodeType(his) == 'cluster']
		allHandle = []
		[allHandle.append(mc.listConnections(item, s = 1, type = 'transform')[0]) for item in allCluster]
		for handle in allHandle:
			#print handle
			vexPos = self.getClostestPoint(mesh, handle)[2]
			dis = ((vexPos[0] - mirPos[0]) ** 2 + (vexPos[1] - mirPos[1]) ** 2 + (vexPos[2] - mirPos[2]) ** 2) ** 0.5
			#print dis
			if dis < 0.1:
				clusDeformer = mc.listConnections(handle + ".worldMatrix[0]",type ="cluster",d = 1)[0]
				clusSet = mc.listConnections(clusDeformer, type = "objectSet" )[0]
				return handle, clusDeformer, clusSet
			
		
