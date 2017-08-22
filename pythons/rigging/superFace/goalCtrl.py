## Import Standard Modules
from sfGlobal import *
from maya.cmds import *
import maya.mel as mm
import re
import utility

## The Main Function	
class goalCtrl():
	def __init__(self):
		pass

	def getCloseMath(self, num, keep = 2):
		data = 10.0 ** (keep + 1)
		if num > 0:
			if int(str(int(num * data))[-1]) >= 5:
				num = float(str(int(num * data / 10 + 1))[:-2] + '.' + str(int(num * data / 10 + 1))[-2:])
			else:
				num = float(str(int(num * data / 10 + 0))[:-2] + '.' + str(int(num * data / 10 + 0))[-2:])
		elif num < 0:
			if int(str(int(num * data))[-1]) >= 5:
				num = float(str(int(num * data / 10 - 1))[:-2] + '.' + str(int(num * data / 10 - 1))[-2:])
			else:
				num = float(str(int(num * data / 10 + 0))[:-2] + '.' + str(int(num * data / 10 + 0))[-2:])
		return num
	
	
	## Create The Circle As The Controller
	def createCircle(self,  string):
		cirCtrl = circle(n = string + '_ctrl#', c = (0, 0, 0), nr = (0, 0, 1), sw = 360, r = 0.2, d = 3, ut = 0, tol = 0.01, s = 8, ch = 0)
		cirCtrlShape = listRelatives(cirCtrl, shapes = True)[0]
		rename(cirCtrlShape, string + '_ctrlShape#')
		cirCtrlZero = group(cirCtrl, n = cirCtrl[0] + '_zero')
		try:
			parent(cirCtrlZero, g.FACE_CTRL_PANEL)
		except:
			parent(cirCtrlZero, g.GOAL_CTRL_GRP)
		finally:
			pass
		attrs = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v']
		[setAttr(cirCtrl[0] + attr, lock = True, keyable = False, channelBox = False) for attr in attrs]
		return cirCtrl[0], cirCtrlZero
		
	## Create The Controller Icon
	
	# ____________________________
	# |                           |
	# |                           |
	# |           ______          |
	# |          |   A  |         |
	# |          |______|         |
	# |                           |
	# |                           |
	# |___________________________|
	def ctrlA(self, name = 'typeA'):
		if name == '':
			name = 'typeA'
		cirCtrl, cirCtrlZero = self.createCircle(name)
		self.limitAttr(cirCtrl, ['tx', -1, 1])
		self.limitAttr(cirCtrl, ['ty', -1, 1])
		select(cirCtrlZero)
		
	# ____________________________
	# |                           |
	# |                           |
	# |           ______          |
	# |          |   B  |         |
	# |          |______|         |
	# |___________________________|
	def ctrlB(self, name = 'typeB'):
		if name == '':
			name = 'typeB'
		cirCtrl, cirCtrlZero = self.createCircle(name)
		self.limitAttr(cirCtrl, ['tx', -1, 1])
		self.limitAttr(cirCtrl, ['ty', 0, 1])
		select(cirCtrlZero)
		
	# ____________________________
	# |           ______          |
	# |          |   C  |         |
	# |          |______|         |
	# |___________________________|
	def ctrlC(self, name = 'typeC'):
		if name == '':
			name = 'typeC'
		cirCtrl, cirCtrlZero = self.createCircle(name)
		self.limitAttr(cirCtrl, ['tx', -1, 1])
		select(cirCtrlZero)
		
	# ____________________________
	# | ______                    |
	# ||   D  |                   |
	# ||______|                   |
	# |___________________________|
	def ctrlD(self, name = 'typeD'):
		if name == '':
			name = 'typeD'
		cirCtrl, cirCtrlZero = self.createCircle(name)
		self.limitAttr(cirCtrl, ['tx', 0, 1])
		select(cirCtrlZero)
		
	# _________
	# |        |
	# |        |
	# | ______ |
	# ||   E  ||
	# ||______||
	# |        |
	# |        |
	# |________|
	def ctrlE(self, name = 'ctrlE'):
		if name == '':
			name = 'ctrlE'
		cirCtrl, cirCtrlZero = self.createCircle(name)
		self.limitAttr(cirCtrl, ['ty', -1, 1])
		select(cirCtrlZero)
		
	# _________
	# |        |
	# |        |
	# |        |  
	# |        |       
	# | ______ |
	# ||   F  ||
	# ||______||
	# |________| 
	def ctrlF(self, name = 'ctrlF'):
		if name == '':
			name = 'ctrlF'
		cirCtrl, cirCtrlZero = self.createCircle(name)
		self.limitAttr(cirCtrl, ['ty', 0, 1])
		select(cirCtrlZero)
	
	## Limit The Attributes
	def limitAttr(self, obj, listAttrs):
		attr = '.' + listAttrs[0]
		sumNum = listAttrs[1] + listAttrs[2]
		setAttr(obj+ attr, lock = False, keyable = True, channelBox = True)
		setAttr(obj+ attr, keyable = True)
		if listAttrs[0] == 'tx':
			if sumNum > 0:
				transformLimits(obj, tx = (0, 1), etx = (1, 1))
			elif sumNum == 0:
				transformLimits(obj, tx = (-1, 1), etx = (1, 1))
			elif sumNum < 0:
				transformLimits(obj, tx = (-1, 0), etx = (1, 1))
		elif listAttrs[0] == 'ty':
			if sumNum > 0:
				transformLimits(obj, ty = (0, 1), ety = (1, 1))
			elif sumNum == 0:
				transformLimits(obj, ty = (-1, 1), ety = (1, 1))
			elif sumNum < 0:
				transformLimits(obj, ty = (-1, 0), ety = (1, 1))
	
	# Move the object your selected to the side
	def moveToSide(self, transform):
		
		minX = getAttr(transform + '.boundingBoxMinX')
		maxX = getAttr(transform + '.boundingBoxMaxX')
		move(abs(minX - maxX) + 2, transform, x = True, r = True)
	
	# Connect the new controller to drive the no deformed blendshape node 
#	def connectCtrlToBS(self, ctrlList, obj):   # ok
#		for ctrl in ctrlList:
#			attrList = listAttr(ctrl, k=1, u=1, v=1, s=1)
#			for attr in attrList:
#				valueList = self.getLimitValue(ctrl,attr)
#				for value in valueList:
#					self.createBS(ctrl, attr, value, obj)

	# Get the information of the controllers' limit
#	def getLimitValue(self, ctrl, attr):    # ok
#		value = []
#		if attr=='tx':
#			value = transformLimites(ctrl,q=1,tx=1)
#		elif attr=='ty':
#			value = transformLimites(ctrl,q=1,ty=1)
#		elif attr=='tz':
#			value = transformLimites(ctrl,q=1,tz=1)
#		output = []
#		for v in value:
#			if v!=0:
#				output.append(v)
#		return output

	# Create the goal mesh shape
	def createBSShape(self, shape, transformNode=None): # ok
		if transformNode==None:
			transformNode = createNode('transform')
			
		shapeType = objectType(shape)
		goalShape = createNode(shapeType,p=transformNode)
		self.transferShape(shape,goalShape)
		sets(goalShape,e=1,forceElement='initialShadingGroup')
		self.moveToSide(transformNode)
		
		self.hideAllGoal()
		self.showGoal(transformNode)
		return (goalShape, transformNode)
		#setAttr('%s.intermediateObject'%goalShape,1)
		
	# Transfer the points from one geomtry to another
	def transferShape(self, orig, shape):   # ok
		shapeType = objectType(orig)
		outAttr = inAttr = ''
		if shapeType=='mesh':
			outAttr = 'outMesh'
			inAttr = 'inMesh'
		elif shapeType=='nurbsSurface':
			outAttr = 'local'
			inAttr = 'create'
		tmpT = createNode('transform')
		tmpS = createNode(shapeType,p=tmpT)
		connectAttr('%s.%s'%(orig,outAttr),'%s.%s'%(tmpS,inAttr))
		connectAttr('%s.%s'%(tmpS,outAttr),'%s.%s'%(shape,inAttr))
		transferAttributes(tmpS, shape, transferPositions = 1, transferNormals = 1, transferUVs = 2, transferColors = 2, sampleSpace = 4, flipUVs = 0, colorBorders = 1)
		delete(shape, ch = 1)
		delete(tmpT)
	
	# Create The Blend Shape Goal Geometry
	def createBS(self, drvObj, attr, drvValue, skinGeo):
		if drvValue == 0:
			raise RuntimeError, 'The value of attribute can not be zero!'
		elif skinGeo == '':
			raise RuntimeError, 'Fuck, There is no model assigned!'
		baseBSObj = self.findBSGeo(skinGeo)
		skinGeoShapes = listRelatives(skinGeo, shapes = True)
		findit = self.findAniNode(drvObj, attr, drvValue)
		
		# Dudge the way how to create the goalGeom
		sel = ls(sl = True)
		
		if len(sel) != 0:
			selShape = listRelatives(sel[0], s = True)[0]
			if nodeType(selShape) == 'mesh':
				try:
					goalObjShape, goalObj = self.createBSShape(selShape)
					#delete(sel)
				except:
					raise RuntimeError, 'The topology are not the same!'
			else:
				goalObjShape, goalObj = self.createBSShape(skinGeoShapes[0])
		else:
			goalObjShape, goalObj = self.createBSShape(skinGeoShapes[0])
			
		midstr = drvObj.split('_')
		if drvObj.count('_') > 1:
			newstr = '_'.join(midstr[1:-1])
		else:
			newstr = '_'.join(midstr[:-1])
		if attr == 'translateX' or attr == 'tx':
			if drvValue > 0:
				state = 'Out'
			else:
				state = 'In'
		elif attr == 'translateY' or attr == 'ty':
			if drvValue > 0:
				state = 'Up'
			else:
				state = 'Dn'
		elif attr == 'rotateX' or attr == 'rx':
			if drvValue > 0:
				state = 'Up'
			else:
				state = 'Dn'
		elif attr == 'rotateY' or attr == 'ry':
			if drvValue > 0:
				state = 'Out'
			else:
				state = 'In'
		
		goalObjShape = rename(goalObjShape, '%s_%s_GoalShape#' % (newstr, state))
		goalObj = rename(goalObj, '%s_%s_Goal#' % (newstr, state))

		if findit is 'con2' or findit is 'con1':
			self.addInbetween(baseBSObj, goalObj, drvObj, attr, drvValue)
		elif findit is 'none':
			self.connectBS(baseBSObj, goalObj, drvObj, attr, drvValue)

	# Create A New BlendShape Node/Attribute And Drive it
	def connectBS(self, baseBSObj, goalObj, drvObj, attr, drvValue):
		# Dict{'L1' : [0, { 0.3 : ['inputTarget[0].inputTargetGroup[0].inputTargetItem[5200].inputGeomTarget', 'L3'],  0.6 : ['[0][5200]' , 'L2'],  1 : ['[0][5200]','L1']} ] ............}
		drvAttr = drvObj + '.' + attr
		BSNodeShape = listRelatives(baseBSObj, shapes = True)[0]
		BSNodes = listConnections(BSNodeShape, destination = False, source = True, type = 'blendShape')
		
		if BSNodes == None:
			BSNodes = blendShape(goalObj, baseBSObj, foc = True, n = 'BS_List')

		else:
			BSDict = self.blendShapeData(BSNodes[0])
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
			blendShape(BSNodes[0], edit = True, t = (baseBSObj, numKeys, goalObj, 1))
		print 'Add Successfully!'

		setDrivenKeyframe(BSNodes[0] + '.' + goalObj, currentDriver = drvAttr, driverValue = 0, value = 0)
		
		if 0 <drvValue < 1:
			drvValue = 1
			warningString = 'warning "This goal is driven by int 1!"'
			mm.eval(warningString)
		elif -1 < drvValue < 0:
			drvValue = -1
			warningString = 'warning "This goal is driven by int -1!"'
			mm.eval(warningString)
		elif drvValue == 0:
			raise RuntimeError, 'The value of attribute can not be zero!'
		setDrivenKeyframe(BSNodes[0] + '.' + goalObj, driverValue = drvValue, value = 1)
	
	## Use the clamp construction to build the blendshape.
	def clampBS(self, baseBSObj, goalObj, drvObj, attrList, drvValueList):
		# Dict{'L1' : [0, { 0.3 : ['inputTarget[0].inputTargetGroup[0].inputTargetItem[5200].inputGeomTarget', 'L3'],  0.6 : ['[0][5200]' , 'L2'],  1 : ['[0][5200]','L1']} ] ............}
		attrX, attrY = attrList
		valueX, valueY = drvValueList
		
		drvAttrX = drvObj+'.'+attrX
		drvAttrY = drvObj+'.'+attrY
		
#		drvAttr = drvObj + '.' + attr
		BSNodeShape = listRelatives(baseBSObj, shapes = True)[0]
		BSNodes = listConnections(BSNodeShape, destination = False, source = True, type = 'blendShape')
		
		if BSNodes == None:
			BSNodes = blendShape(goalObj, baseBSObj, foc = True, n = 'BS_List')

		else:
			BSDict = self.blendShapeData(BSNodes[0])
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
			blendShape(BSNodes[0], edit = True, t = (baseBSObj, numKeys, goalObj, 1))
		
		# Snap the value to zero or one
		if 0 <valueX < 1:
			valueX = 1
			warningString = 'warning "This goal is driven by int 1!"'
			mm.eval(warningString)
		elif -1 < valueX < 0:
			valueX = -1
			warningString = 'warning "This goal is driven by int -1!"'
			mm.eval(warningString)
		elif 0 <valueY < 1:
			valueY = 1
			warningString = 'warning "This goal is driven by int 1!"'
			mm.eval(warningString)
		elif -1 < valueY < 0:
			valueY = -1
			warningString = 'warning "This goal is driven by int -1!"'
			mm.eval(warningString)
		elif valueY == 0:
			raise RuntimeError, 'The value of attribute can not be zero!'
		elif valueX == 0 and valueY == 0:
			raise RuntimeError, 'The value of attribute can not be zero!'
		else:
			pass
		
		# Begin to create the construction connected to the blendshape
		# if one value of the axis is zero start the first loop
		# else go to the second loop to create the clamp construction
		if not (valueX * valueY) and (valueX + valueY):
			if valueX > 0:
				fix = 'Out'
			elif valueX < 0:
				fix = 'In'
			elif valueY > 0:
				fix = 'Up'
			else:
				fix = 'Dn'

			MDNode = createNode('multiplyDivide', n = 'opreateMD_(string)'.fomate(string = fix))
			connetAttr(MDNode + '.outputX', BSNodes[0] + '.' + goalObj)
			drnAttrX = MDNode + '.input1X'
			drnAttrY = MDNode + '.input2X'
			#setDrivenKeyframe(BSNodes[0] + '.' + goalObj, currentDriver = drvAttr, driverValue = 0, value = 0)
			
			self.autoSDK(drvAttrX, drnAttrX, valueX, 1)
			self.autoSDK(drvAttrY, drnAttrY, valueY, 1)
			#setDrivenKeyframe(BSNodes[0] + '.' + goalObj, driverValue = drvValue, value = 1)
		else:
			if valueX > 0:
				if valueY > 0:
					xfix = '_Out'
					yfix = '_Up'
					operateMD, clampX, clampY, addDoubleX = self.createClampNodes(BSNodes[0], goalObj, drvObj, xfix, yfix)
					drivenX = addDoubleX + '.input1'
					drivenY = clampY + '.inputR'
					drivenValueX = 1
					drivenValueY = 1
				else:
					xfix = '_Out'
					yfix = '_Dn'
					operateMD, clampX, clampY, addDoubleX = self.createClampNodes(BSNodes[0], goalObj, drvObj, xfix, yfix)
					negMD = createNode('multiplyDivide', n = '%s_negMD%s'%(drvObj, yfix))
					setAttr(negMD + '.input2X', -1)
					connectAttr(negMD + '.outputX', clampY + '.inputR')
					drivenX = addDoubleX + '.input1'
					drivenY = negMD + '.input1X'
					drivenValueX = 1
					drivenValueY = -1
			else:
				if valueY > 0:
					xfix = '_In'
					yfix = '_Up'
					operateMD, clampX, clampY, addDoubleX = self.createClampNodes(BSNodes[0], goalObj, drvObj, xfix, yfix)
					negMD = createNode('multiplyDivide', n = '%s_negMD%s'%(drvObj, xfix))
					setAttr(negMD + '.input2X', -1)
					connectAttr(negMD + '.outputX', addDoubleX + '.input1')
					drivenX = negMD + '.input1X'
					drivenY = clampY + '.inputR'
					drivenValueX = -1
					drivenValueY = 1
				else:
					xfix = '_In'
					yfix = '_Dn'
					operateMD, clampX, clampY, addDoubleX = self.createClampNodes(BSNodes[0], goalObj, drvObj, xfix, yfix)
					negMDX = createNode('multiplyDivide', n = '%s_negMD%s'%(drvObj, xfix))
					negMDY = createNode('multiplyDivide', n = '%s_negMD%s'%(drvObj, yfix))
					setAttr(negMDX + '.input2X', -1)
					setAttr(negMDY + '.input2X', -1)
					connectAttr(negMDX + '.outputX', addDoubleX + '.input1')
					connectAttr(negMDY + '.outputX', clampY + '.inputR')
					drivenX = negMDX + '.input1X'
					drivenY = negMDY + '.input1X'
					drivenValueX = -1
					drivenValueY = -1
			self.autoSDK(drvAttrX, drivenX, valueX, drivenValueX)
			self.autoSDK(drvAttrY, drivenY, valueY, drivenValueY)
						
	def createClampNodes(self, BSNode, goalObj, drvObj, xfix, yfix):
		operateMD = createNode('multiplyDivide', n = '%s_oprateMD%s%s'%(drvObj, xfix, yfix))
		clampX = createNode('clamp', n = '%s_clampX%s'%(drvObj, xfix))
		clampY = createNode('clamp', n = '%s_clampY%s'%(drvObj, yfix))
		setAttr(clampX + '.minR', 0)
		setAttr(clampX + '.maxR', 1)
		setAttr(clampY + '.minR', 0)
		setAttr(clampY + '.maxR', 1)
		addDoubleX = createNode('addDoubleLinear', n = '%s_addDouble%s' % (drvObj, xfix) )
		setAttr(addDoubleX + '.input1', k = True)
		setAttr(addDoubleX + '.input2', 1)
		connectAttr('%s.output'%addDoubleX, '%s.inputR'%clampX)
		connectAttr('%s.outputR'%clampX, '%s.input1X'%operateMD)
		connectAttr('%s.outputR'%clampY, '%s.input2X'%operateMD)
		connectAttr(operateMD + '.outputX', BSNode + '.' + goalObj)
		return operateMD, clampX, clampY, addDoubleX
	
	def autoSDK(self, driver, driven, drvValue, drnValue):
		setDrivenKeyframe(driven, currentDriver = driver, driverValue = 0, value = 0)
		setDrivenKeyframe(driven, currentDriver = driver, driverValue = drvValue, value = drnValue)
		sdkCurves = listConnections(driver, s = False, d = True)
		for sdkCurve in sdkCurves:
			setAttr(sdkCurve + '.preInfinity', 1)
			setAttr(sdkCurve + '.postInfinity', 1)
		
		#print 'it works'
			
	## Add The Inbetween BlendShape
	def addInbetween(self, baseBSObj, goalObj, drvObj, attr, drvValue):
		drvAttr = drvObj + '.' + attr
		
		goalObjShape = listRelatives(goalObj, shapes = True)
		drvAniNodes = listConnections(drvAttr, destination = True, type = 'animCurveUU')
		
		findit = None
		
		for drvAniNode in drvAniNodes:
			keyCount = keyframe(drvAniNode, q = True, floatChange = True)
			
			if keyCount[0] <= drvValue <= keyCount[-1]:
				# Dict{'L1' : [0, { 0.3 : ['inputTarget[0].inputTargetGroup[0].inputTargetItem[5200].inputGeomTarget', 'L3'],  0.6 : ['[0][5200]' , 'L2'],  1 : ['[0][5200]','L1']} ] ............}
				
				drivenAttr = listConnections(drvAniNode + '.output', destination = True, p = True)[0]
				BSNodes = listConnections(drvAniNode + '.output', destination = True)
				cmd = 'keyframe -f %g -q -vc "%s"' % (drvValue, drvAniNode)
				drivenValue = mm.eval(cmd)
				if drivenValue != None:
					drivenValue = drivenValue[0]
		
				BSDict = self.blendShapeData(BSNodes[0]) # ---------------------------------BlendShape Dict-------------------------------- #
				dictList = BSDict[drivenAttr.split('.')[-1]]
				#print dictList,BSDict, BSDict[drivenAttr]

				if drivenValue in dictList[1].keys():
					if dictList[1][drivenValue][1] != '': 
						orgIbObj = dictList[1][drivenValue][1]
						orgIbObjShape = listRelatives(orgIbObj, shapes = True)[0]
						self.transferShape(goalObjShape[0], orgIbObjShape)
						self.showGoal(orgIbObj)
						delete(goalObj)	
					else:
						blendShape(BSNodes[0], edit = True, ib = True, t = (baseBSObj, dictList[0], goalObj, drivenValue ))
				else:
					blendShape(BSNodes[0], edit = True, ib = True, t = (baseBSObj, dictList[0], goalObj, abs(drvValue) ))
				setDrivenKeyframe(drivenAttr, currentDriver = drvAttr, driverValue = drvValue, value = abs(drvValue))
				keyTangent(drvAniNode, itt = 'linear', ott = 'linear')
				#rename(drvAniNode, drvAniNode.split('_')[0] + '_' +goalObj)
				findit = drvAniNode
				
				break
		if findit == None:
			raise RuntimeError, 'There is no setDrivenKeyframe node fit the condition!'
		print 'Add a new target in %s at %s.%s' % (drvValue, drvObj, attr)
		
	## Add The Inbetween BlendShape
	def addInbetween2(self, baseBSObj, goalObj, drvObj, attrList, drvValueList):
		attrX, attrY = attrList
		drvValueX, drvValueY = drvValueList
		drvAttrX = drvObj + '.' + attrX
		drvAttrY = drvObj + '.' + attrY
		
		goalObjShape = listRelatives(goalObj, shapes = True)[0]
		drvAniNodesX = listConnections(drvAttrX, destination = True, type = 'animCurveUU')
		drvAniNodesY = listConnections(drvAttrY, destination = True, type = 'animCurveUU')
		
		findit = None
		# First judge the driver is a single axis or the double axis
		# 2nd find the animation node fit the condition
		# start the loop
		for drvAniNodeX in drvAniNodesX:
			keyCountX = keyframe(drvAniNodeX, q = True, floatChange = True)
			for drvAniNodeY in drvAniNodesY:
				keyCountY = keyframe(drvAniNodeY, q = True, floatChange = True)
				if len(keyCountX) == 1:
					if keyCountY[0] <= drvValueY <= keyCountY[-1]:
						findit = self.addInbetweenFunction(drvAniNodeX, drvAniNodeY, drvAttrX, drvAttrY, goalObjShape)
						break
				elif len(keyCountY) == 1:
					if keyCountX[0] <= drvValueX <= keyCountX[-1]:
						findit = self.addInbetweenFunction(drvAniNodeX, drvAniNodeY, drvAttrX, drvAttrY, goalObjShape)
						break
				else:
					if keyCountX[0] <= drvValueX <= keyCountX[-1] and keyCountY[0] <= drvValueY <= keyCountY[-1]:
						findit = self.addInbetweenFunction(drvAniNodeX, drvAniNodeY, drvAttrX, drvAttrY, goalObjShape)
						break
		if findit == None:
			raise RuntimeError, 'There is no setDrivenKeyframe node fit the condition!'
		
	def getDrnValue(self, drvValue, drvAniNode):
		cmd = 'keyframe -f %g -q -vc "%s"' % (drvValue, drvAniNode)
		drivenValue = mm.eval(cmd)
		return drivenValue
	
	def addInbetweenFunction(self, drvAniNodeX, drvAniNodeY, drvAttrX, drvAttrY, goalObjShape):
		# Dict{'L1' : [0, { 0.3 : ['inputTarget[0].inputTargetGroup[0].inputTargetItem[5200].inputGeomTarget', 'L3'],  0.6 : ['[0][5200]' , 'L2'],  1 : ['[0][5200]','L1']} ] ............}
		# Find the last MDNode connect to bsnode
		hisListX = listHistory(drvAniNodeX, future = True)
		lastMDNode = [node for node in hisListX if nodeType(node) == 'multiplyDivide'][-1]
		# Get the bsnode's goal attribute and the bsnode
		bsnodeAttr = listConnections(lastMDNode + '.outputX', destination = True, p = True)[0]
		BSNodes = listConnections(lastMDNode + '.output', destination = True)
		# Find if there is a key in the animnode
		drivenValueX = self.getDrnValue(drvValueX, drvAniNodeX)
		if drivenValueX != None:
			drivenValueX = drivenValueX[0]
		drivenValueY = self.getDrnValue(drvValueY, drvAniNodeY)
		if drivenValueY != None:
			drivenValueY = drivenValueY[0]
		drivenValue = getAttr(lastMDNode + '.outputX')

		BSDict = self.blendShapeData(BSNodes[0]) # ---------------------------------BlendShape Dict-------------------------------- #
		dictList = BSDict[bsnodeAttr.split('.')[-1]]
		#print dictList,BSDict, BSDict[bsnodeAttr]

		if drivenValue in dictList[1].keys():
			if dictList[1][drivenValue][1] != '': 
				orgIbObj = dictList[1][drivenValue][1]
				orgIbObjShape = listRelatives(orgIbObj, shapes = True)[0]
				self.transferShape(goalObjShape, orgIbObjShape)
				self.showGoal(orgIbObj)
				delete(goalObj)	
			else:
				blendShape(BSNodes[0], edit = True, ib = True, t = (baseBSObj, dictList[0], goalObj, drivenValue ))
		else:
			blendShape(BSNodes[0], edit = True, ib = True, t = (baseBSObj, dictList[0], goalObj, abs(drvValue) ))
		# Get the drivenAttr
		drivenAttrX = listConnections(drvAniNodeX, s = False, d = True, p = True)[0]
		drivenAttrY = listConnections(drvAniNodeY, s = False, d = True, p = True)[0]
		
		setDrivenKeyframe(drivenAttrX, currentDriver = drvAttrX, driverValue = drvValueX, value = abs(drvValueX))
		setDrivenKeyframe(drivenAttrY, currentDriver = drvAttrY, driverValue = drvValueY, value = abs(drvValueY))
		keyTangent(drvAniNodeX, itt = 'linear', ott = 'linear')
		keyTangent(drvAniNodeY, itt = 'linear', ott = 'linear')
		findit = drvAniNodeX
		return findit
	
	# Start with ctrl, attrList and valueList to get the blendshape node, driven attribute and the value
	def getDrnInfo(self, ctrl, attrList, valueList):
		attrX, attrY = attrList
		drvValueX, drvValueY = drvValueList
		drvAttrX = drvObj + '.' + attrX
		drvAttrY = drvObj + '.' + attrY
		
		drvAniNodesX = listConnections(drvAttrX, destination = True, type = 'animCurveUU')
		drvAniNodesY = listConnections(drvAttrY, destination = True, type = 'animCurveUU')
		
		findit = None
		# First judge the driver is a single axis or the double axis
		# 2nd find the animation node fit the condition
		# start the loop
		for drvAniNodeX in drvAniNodesX:
			keyCountX = keyframe(drvAniNodeX, q = True, floatChange = True)
			for drvAniNodeY in drvAniNodesY:
				keyCountY = keyframe(drvAniNodeY, q = True, floatChange = True)
				if len(keyCountX) == 1:
					if keyCountY[0] <= drvValueY <= keyCountY[-1]:
						outputValue = drvValueY
						animNode = drvAniNodeX
						findit = 1
						break
				elif len(keyCountY) == 1:
					if keyCountX[0] <= drvValueX <= keyCountX[-1]:
						outputValue = drvValueX
						animNode = drvAniNodeX
						findit = 1
						break
				else:
					if keyCountX[0] <= drvValueX <= keyCountX[-1] and keyCountY[0] <= drvValueY <= keyCountY[-1]:
						outputValue = self.clampOpreate(drvValueX, drvValueY)
						animNode = drvAniNodeX
						findit = 1
						break
		if findit == None:
			raise RuntimeError, 'There is no setDrivenKeyframe node fit the condition!'
		
		hisListX = listHistory(drvAniNodeX, future = True)
		lastMDNode = [node for node in hisListX if nodeType(node) == 'multiplyDivide'][-1]
		# Get the bsnode's goal attribute and the bsnode
		bsnodeAttr = listConnections(lastMDNode + '.outputX', destination = True, p = True)[0]
		BSNode, bsAttr = bsnodeAttr.split('.')
		return BSNode, bsAttr, outputValue
	
	def clampOpreate(self, valueX, vlaueY):
		outValueA = utility.clamp(0, 1, abs(valueX) + 1)
		outValueB = utility.clamp(0, 1, abs(valueY))
		outValue = outValueA * outValueB
		return outValue
		
	def getGoalList(self, drvObj, attr, skinGeo):
		drns = self.getDrnList(drvObj, attr, skinGeo)
		fs = []
		vs = []
		for drn in drns:
			fs.extend(keyframe(drn,q=1,fc=1))
			vs.extend(keyframe(drn,q=1,vc=1))
		list = {}
		for i in range(len(fs)):
			vfi = str(self.getCloseMath(fs[i]))
			list[vfi] = vs[i]
		return list

	def showBS(self, drvObj, attr, drvValue, skinGeo):
		BSList = getGoalList(drvObj, attr)
		drivenValue = self.getBlendShapeInfo(drvObj, attr, drvValue, skinGeo)[2]
		drivenObj = BSList[drivenValue]
		if objExists(drivenObj):
			showHidden(drivenObj, a = True)
		else:
			drivenObj = self.backToBS(drvObj, attr, drivenValue)
		select(drivenObj)
		return dirvenObj

	# Return The Infomation Of The BlendShape Dict --- eg:(BSNode, weightAttr, weightValue, inputTargetAttr, inputTargetObj)
	def getBlendShapeInfo(self, ctrl, attr, value, skinGeo):
		if skinGeo == '' :
			raise RuntimeError, 'Fuck, There is no model assigned!'
		his = listHistory(skinGeo)

		str = listConnections('%s.%s'%(ctrl,attr), d=1, s=0,scn=1)

		if str == None:
			return None
		aniNodes = str
		aniNodeList = []
		vc = None
#		aniNode = None
		for item in aniNodes:
			cmds = 'keyframe -f %g -q -vc %s' % (value,item)
			try:
				vc = mm.eval(cmds)[0]
#				aniNode = item
				aniNodeList.append(item)
			except:
				continue
		if aniNodeList == []:
			return None
#		if aniNode == None:
#			return None
		for aniNode in aniNodeList:
#			print 'animNode:', aniNode
			str = listConnections('%s.output'%aniNode,d=1,s=0,p=1)
			BSNode,weightAttr = str[0].split('.')
			if nodeType(BSNode)=='blendWeighted':
#				print 'aniNode:', BSNode
				aniNode = BSNode
				str = listConnections('%s.output'%aniNode,d=1,s=0,p=1)
				BSNode,weightAttr = str[0].split('.')
			if nodeType(BSNode) == 'blendShape' and BSNode in his:
#			if BSNode in his:
				dictList = self.blendShapeData(BSNode)
				#print dictList
				cmds = 'keyframe -f %g -q -vc %s' % (value,aniNode)
				try:
					vc = mm.eval(cmds)[0]
	#				aniNode = item
				except:
					continue
				weightValue = vc
				#print dictList[weightAttr][1],weightValue
#				print 'dictList:',dictList
#				print 'weightAttr:',weightAttr
#				print 'weightValue',weightValue
				inputTargetAttr = dictList[weightAttr][1][weightValue][0]
				inputTargetObj = dictList[weightAttr][1][weightValue][1]
				return (BSNode, weightAttr, weightValue, inputTargetAttr, inputTargetObj)
		return None

	def getBlendShapeInfo2(self, ctrl, attrList, valueList):
		BSNode, weightAttr,veightValue = getDrnInfo(ctrl, attrList, valueList)
		if nodeType(BSNode) == 'blendShape':
			dictList = self.blendShapeData(BSNode)
#			print 'dictList:',dictList
#			print 'weightAttr:',weightAttr
#			print 'weightValue',weightValue
			inputTargetAttr = dictList[weightAttr][1][weightValue][0]
			inputTargetObj = dictList[weightAttr][1][weightValue][1]
			return (BSNode, weightAttr, weightValue, inputTargetAttr, inputTargetObj)
		return None


	# If There Is No Goal Geomtry Exists, Create A New One And Add Inbetween To The BlendShape Attribute
	def backToBS(self, drvObj, attr, drvValue, skinGeo):
		BSNode, drnThatAttr, weightValue, inputTargetAttr, goalObjName = self.getBlendShapeInfo(drvObj, attr, drvValue, skinGeo)
		baseBSObjList = listConnections(BSNode, destination = True, source = False)
		baseBSObj = [item for item in baseBSObjList if nodeType(item) == 'transform' ][0]
#		print 'BSNode, baseBSObj',BSNode, baseBSObj
		baseBSObjShape = listRelatives(baseBSObj, shapes = True)[0]

		BSDict = self.blendShapeData(BSNode)
		preValue = []
		for drnAttr in BSDict.keys():
			currentValue = getAttr(BSNode + '.' + drnAttr)
			preValue.append(currentValue)
			try:
				setAttr(BSNode + '.' + drnAttr, 0)
			except:
				pass
		setAttr((BSNode + '.' + drnThatAttr), weightValue)
		goalObjShape, goalObj = self.createBSShape(baseBSObjShape)
		goalObjShape = rename(goalObjShape, '%s_%sShape#' % (drvObj, attr))
		goalObj = rename(goalObj, '%s_%s#' % (drvObj, attr))

		blendShape(BSNode, edit = True, ib = True, t = (baseBSObj, BSDict[drnThatAttr][0], goalObj, weightValue))
		for i in range(len(BSDict.keys())):
			try:
				setAttr(BSNode + '.' + BSDict.keys()[i], preValue[i])
			except:
				pass

		return goalObj

	# Remove The BlendShape Attribute
	def removeBS(self, drvObj, attr, drvValue, skinGeo):
		BSNode, drnThatAttr, weightValue, noneed, goalObjName = self.getBlendShapeInfo(drvObj, attr, drvValue, skinGeo)
		BSDict = self.blendShapeData(BSNode)
		outputObj = listConnections(BSNode, destination = True, source = False, shapes = True)
#		print outputObj
		for obj in outputObj:
			if nodeType(obj) == 'mesh':
				baseBSObj = listRelatives(obj, p = True)[0]
		str = listConnections('%s.%s'%(drvObj,attr), d=1, s=0)
		if str == None:
			return None
		aniNodes = str
		vc = None
		aniNode = None
		for item in aniNodes:
			cmds = 'keyframe -f %g -q -vc %s' % (drvValue,item)
			try:
				vc = mm.eval(cmds)[0]
				aniNode = item
			except:
				continue
		if aniNode == None:
			return None
		
		if goalObjName == '':
			goalObj = self.backToBS(drvObj, attr, drvValue)
		else:
			goalObj = goalObjName
		cmds = 'cutKey -f %g -attribute %s -option keys %s' % (drvValue, drnThatAttr, BSNode)
		mm.eval(cmds)
		blendShape(BSNode, e = True, tc = False, rm = True, t = (baseBSObj, len(BSDict.keys()), goalObj, 1))
		delete(goalObj)
		if keyframe(aniNode, q = True, keyframeCount = True) == 1:
			delete(aniNode)
		
	# Find The Base Geomtry As The Goals Blend To From The SkinGeo, If There Is No Geomtry List This, Create A New One	
	def findBSGeo(self, skinGeo):
		selObj = ls(sl = True)
		allHis = listHistory(skinGeo)
		BSList = []
		[BSList.append(BSNode) for BSNode in allHis if nodeType(BSNode) == 'blendShape']
		orgMeshList = []
		skinGeoShape = listRelatives(skinGeo, shapes = True)
		typeName = objectType(skinGeoShape[0])
		[orgMeshList.append(meshNode) for meshNode in allHis if nodeType(meshNode) == typeName]

		if len(BSList) is 0:
			if len(orgMeshList) > 1:
				goalShape, goalObj = self.createBSShape(orgMeshList[1])
			else:
				#goalObj = self.createGoal(skinGeo)
				goalShape, goalObj = self.createBSShape(orgMeshList[0])
			goalObj = rename(goalObj, '%s_BSBase' % skinGeo)
			goalShape = rename(goalShape, '%s_BSBaseShape' % skinGeo)
			hide(goalObj)
			BSNodes = blendShape(goalObj, skinGeo, n = 'BS_On_Off', foc = True)
			BSNode = BSNodes[0]
		else:
			BSNode = BSList[0]
		BSAttrs = blendShape(BSNode, q = True, t =True)
		setAttr(BSNode + '.' + BSAttrs[0], 1)
		baseBSObj = listConnections(BSNode, destination = False, source = True, type = 'mesh')## Get all BS geo
		if len(selObj) > 0:
			if nodeType(listRelatives(selObj[0], s = True)[0]) == 'mesh':
				select(selObj[0])

		return baseBSObj[0]
		
	# Search If There Is Any SetDrivenKey Animation Node Connected The Controller	
	def findAniNode(self, drvObj, attr, drvValue):
		drvAttr = drvObj + '.' + attr
		drvAniNodes = listConnections(drvAttr, destination = True, type = 'animCurveUU')
		
		if drvAniNodes is None:
			return 'none'
		for drvAniNode in drvAniNodes:
			keyCount = keyframe(drvAniNode, q = True, floatChange = True)
			plusValue = keyCount[0] + keyCount[-1]
			outNode = listConnections(drvAniNode, s = False, d = True)
			if outNode != None:
				if outNode[0] == 'BS_List':
					if drvValue > 0 and plusValue > 0:
						return 'con1'
					elif drvValue < 0 and plusValue < 0:
						return 'con2'
		return 'none'
	
	# Get the blendShape data from the blendShape node --- eg: {BSAttr(str):[index(int),{value(float):[inputAttr(str),obj(str)],...}],...}
	def blendShapeData(self, blendShapeNode):
		'''# return {BSAttr(str):[index(int),{value(float):[inputAttr(str),obj(str)],...}],...}
		#        {'L1':[0,{0.3:L3, 0.6:L2, 1:L1}],
		#         'H1':[1,{0.3:H3, 0.5:H2, 1:H1}],
		#         'S1':[3,{0.3:S3, 0.5:S2, 1:S1}],
		#         ...}'''
		
		weightList = listAttr('%s.weight'%blendShapeNode,m=1)
		#// Result: L1 R1 U1 D1 //
		if weightList == None:
			return None
		
		inputTargetList = listAttr('%s.inputTarget'%blendShapeNode,m=1)#;print inputTargetList
		#[inputTarget[0],inputTarget[0].inputTargetGroup[0],...]
		
		info = {}
		# {0:{0.3:'inputTarget[0].inputTargetGroup[0].inputTargetItem[5500]',...},...}
		import re
		q = re.compile(u'inputTarget\[(\d*)\]\.inputTargetGroup\[(\d*)\]\.inputTargetItem\[(\d*)\]$')
		#print q.match(inputTargetList[2]).groups()
		n = 0
		while n<len(inputTargetList):
		    r = None
		    r = q.match(inputTargetList[n])
		    #print 'r:',r
		    if r is not None:
				g = r.groups();#print 'value:',g
				index = int(g[1])
				value = (int(g[2])-5000.0)/1000.0
				value = self.getCloseMath(value)
				if index not in info:
					info[index] = {}
				attr = inputTargetList[n+1];#print attr
				shape = listConnections('%s.%s'%(blendShapeNode,attr),d=0,s=1)
				if shape==None:
				    shape = ['']
				info[index][value] = [attr,shape[0]]
				#print info,'is info0'
		    n += 1
		#print weightList
		#print info,'is info1'
		infoKeys = info.keys()
		infoKeys.sort()
		#print infoKeys
		output = {}
		for i in range(len(weightList)):
			#print '-------'
			#print info,'is info2'
			#print i
			#print weightList[i]
			#output[weightList[i]] = [i,info[i]]
			output[weightList[i]] = [infoKeys[i],info[infoKeys[i]]]
		#print 'output:',output
		return output

	# Get the list of the driven animNodes
	def getDrnList(self, ctrl, attr, skinGeo):
		outList = []
		if skinGeo == '' :
			return outList
			raise RuntimeError, 'Fuck, There is no model assigned!'
		# find history
		his = listHistory(skinGeo)
		list = listConnections('%s.%s'%(ctrl,attr),d=1,s=0,scn=1)
		
		if list is None:
			return outList
		else:
			#list = [obj for obj in list if nodeType(obj) == 'animCurveUU']
			for obj in list:
				if nodeType(obj) == 'animCurveUU':
#					print 'animNode:', obj
					BSNode = listConnections(obj, s = False, d = True, scn = True)
					if BSNode == None:
						mm.eval('warning "Unuseful animation node: %s"'%obj)
					else:
						BSNode = BSNode[0]
						if nodeType(BSNode) == 'blendWeighted':
							BSNode = listConnections(BSNode, s = False, d = True, scn = True)[0]
#						print 'BSNode:',BSNode
						if BSNode in his:
							outList.append(obj)
#		print 'outList:', outList
		return outList	
	
	# Make the goalGeo appear in the scene
	def showGoal(self, goal, state=1):
		if state==1:
			if not objExists(g.GOAL_MODEL_GRP):
				createNode('transform',n=g.GOAL_MODEL_GRP,p=g.ROOT_GRP)
			#print goal,g.GOAL_MODEL_GRP,'FIIIIIND'
			List = listRelatives(g.GOAL_MODEL_GRP,c=1)
			if List == None:
				List = []
			if goal not in List:
				parent(goal,g.GOAL_MODEL_GRP)
		elif state==0:
			if not objExists(g.GOAL_MODEL_HIDE_GRP):
				createNode('transform',n=g.GOAL_MODEL_HIDE_GRP,p=g.GOAL_MODEL_GRP)
				setAttr('%s.v'%g.GOAL_MODEL_HIDE_GRP,0)
			parent(goal,g.GOAL_MODEL_HIDE_GRP)
	
	# Hide the goals geomtry
	def hideAllGoal(self):
		try:
			objs = listRelatives(g.GOAL_MODEL_GRP,c=1)
			if objs is not None:
				try:
					objs.remove(g.GOAL_MODEL_HIDE_GRP)
				except:
					pass
				#print objs
				for obj in objs:
					self.showGoal(obj,0)
		except:
			pass
	
	# Mirror construct of the BS
	def mirrorConstruct(self, ctrl, attr, value, skinGeo, converse):
		mirGoal = self.getBlendShapeInfo(ctrl, attr, value, skinGeo)[4]
		#print mirGoal,'OPOP'
		if mirGoal == None:
			raise RuntimeError, 'There is no target exists!'
		if value == 0:
			raise RuntimeError, 'The value can not be zero!'

		fixdict = {'L':'R', 'R':'L', 'l':'r', 'r':'l'}
		patt = 'tx|translateX|ry|rotateY'
		for fix in fixdict.keys():
			if ctrl.startswith(fix+'_') or ctrl.endswith('_'+fix) or ('_%s_'%fix) in ctrl:
				mirctrl = ctrl.replace(fix, fixdict[fix])
				converse = 0
#				print 'Mirror Ctrl: %s'%mirctrl
				#if re.search(patt, attr) is not None:
				#	converse = 1
				#else:
				#	converse = 0
				break
			else:
				print 'No Mirror'
				if attr == 'ty' or attr == 'translateY':
					pass
				else:
					mirctrl = ctrl
					converse = 1
#		print mirctrl
		mirattr = attr
		
		if converse == 1:
			mirvalue = value * -1
		else:
			mirvalue = value
		

		#print mirctrl, mirattr, mirvalue, skinGeo,converse, '+++++++'
		
		mirGeo = self.mirrorBSGeo(skinGeo, mirGoal)
		select(mirGeo)
		self.createBS(mirctrl, mirattr, mirvalue, skinGeo)
		delete(mirGeo)
		setAttr('%s.%s'% (ctrl, attr), 0)
		setAttr('%s.%s'% (mirctrl, mirattr), mirvalue)
		select(mirctrl)
		
	# Mirror the blendshape target
	def mirrorBSGeo(self, skinGeo, sideGeo):
		wrapGrp, mirGeo, inputBSNode= self.construct(skinGeo, sideGeo, 0)
		setAttr(inputBSNode + '.' + sideGeo, 1)
		delete(mirGeo, ch = True)
		delete(wrapGrp)
		return mirGeo
	
	def doubleDisplay(self, orgGeoShape, sideGeos, nodeName):
		wrapGrp, otherSideGeo, inputBSNode, doubleGeo = self.construct(orgGeoShape, sideGeos, 1)
		setAttr(inputBSNode + '.' + nodeName, 1)
		
	def construct(self, skinGeo, sideGeo, arg = 0):
		orgGeoShapes = listRelatives(skinGeo, s = True)
		if len(orgGeoShapes) > 1:
			orgGeoShape = orgGeoShapes[1]
		else:
			orgGeoShape = orgGeoShapes[0]
		dis = getAttr(sideGeo + '.tx')
		wrapGeoShape, wrapGeo = self.createBSShape(orgGeoShape)
		wrapGeoShape = rename(wrapGeoShape, 'wrapGeoShape')
		wrapGeo = rename(wrapGeo, 'wrapGeo')
		setAttr(wrapGeo + '.tx', dis * 2)
		mirGeo = duplicate(wrapGeo, n ='mirGeo')[0]
		setAttr(wrapGeo + '.sx', -1)
		#print getAttr(wrapGeo + '.sx'), '??'
		
		
		#doubleGeo = duplicate(wrapGeo, n ='doubleGeo')
		#setAttr(doubleGeo + '.tx', dis * 3)
		
		select(mirGeo, r =True)
		select(wrapGeo, add = True)
		CreateWrap()
		select(cl = True)
		wrapGrp = group(wrapGeo, wrapGeo + 'Base')
		hide(wrapGeo)
		
		inputBSNode = blendShape(sideGeo, wrapGeo, foc = True, n = 'inputBS')
		#print inputBSNode,'PPPP'
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
		
		return wrapGrp, mirGeo, inputBSNode[0]
	
	# By default, use this function you can create the blendshape construction of every controller.
	def createGoalInterface(self, skinGeo):
		import utility as u
		curveList = u.getNodeInGrp(g.GOAL_CTRL_GRP, 'nurbsCurve')
		ctrlList = []
		for obj in curveList:
			attrList = listAttr(obj, k = True)
			if len(attrList) < 4:
				ctrlList.append(obj)
		#print ctrlList,'+++'
		for ctrl in ctrlList:
			attrs = listAttr(ctrl, k = True)
			for attr in attrs:
				cmds1 = 'transformLimits -q -e%s %s'%(attr[0]+attr[-1].lower(), ctrl)
				#print cmds1,'++'
				enList = mm.eval(cmds1)
				cmds2 = 'transformLimits -q -%s %s'%(attr[0]+attr[-1].lower(), ctrl)
				limitList = mm.eval(cmds2)
				for i in range(len(enList)):
					if enList[i] == 1:
						value = limitList[i]
						if value != 0:
							select(cl = True)
							self.createBS(ctrl, attr, value, skinGeo)
	

	