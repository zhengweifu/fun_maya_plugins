
class mirrorBS:
	def mirrorBSGeo(self, skinGeo, sideGeo, nodeName):
		wrapGrp, mirGeo, inputBSNode= self.construct(orgGeoShape, sideGeo, 0)
		setAttr(inputBSNode + '.' + sideGeo, 1)
		delete(mirGeo, ch = True)
		delete(wrapGrp)
		return otherSideGeo
	
	def doubleDisplay(self, orgGeoShape, sideGeos, nodeName):
		wrapGrp, otherSideGeo, inputBSNode, doubleGeo = self.construct(orgGeoShape, sideGeos, 1)
		setAttr(inputBSNode + '.' + nodeName, 1)
		
	def construct(self, skinGeo, sideGeo, arg = 0):
		orgGeoShape = listRelatives(skinGeo)[0]
		dis = getAttr(sideGeo)
		wrapGeoShape, wrapGeo = self.createBSShape(orgGeoShape)
		wrapGeoShape = rename(wrapGeoShape, 'wrapGeoShape')
		wrapGeo = rename(wrapGeo, 'wrapGeo')
		setAttr(wrapGeo + '.tx', dis)
		setAttr(wrapGeo + '.sx', -1)
		
		mirGeo = duplicate(wrapGeo, n ='mirGeo')
		
		doubleGeo = duplicate(wrapGeo, n ='doubleGeo')
		setAttr(doubleGeo + '.tx', dis * 3)
		
		select(mirGeo, r =True)
		select(wrapGeo, add = True)
		CreateWrap()
		wrapGrp = group(wrapGeo, wrapGeo + 'Base')
		hide(wrapGeo)
		
		inputBSNode = blendShape(sideGeo, wrapGeo, foc = True, n = 'inputBS')
		#iNodes = blendShape(inputBSNode, q = True, t=True)
		#[setAttr(doubleBSNode + '.' + iNode, 1) for iNode in iNodes]
		
		if arg == 1:
			doubleGeo = duplicate(wrapGeo, n ='doubleGeo')
			setAttr(doubleGeo + '.tx', dis * 3)
			doubleBSNode = blendShape(otherSideGeo, sideGeo, doubleGeo, foc = True, n = 'doubleBS')
			nodes = blendShape(doubleBSNode, q = True, t=True)
			[setAttr(doubleBSNode + '.' + node, 1) for node in nodes]
			parent(doubleGeo, wrapGrp)
			return wrapGrp, otherSideGeo, inputBSNode, doubleGeo
		select(cl = True)
		return wrapGrp, mirGeo, inputBSNode