#------------------------------
# Import Standard Modules
#------------------------------
from sfGlobal import *
from jointCtrl import *
import maya.mel as mm
import re
#-------------------------------
# The Main Function
#-------------------------------
class eyeCtrl(jointCtrl):
	locGrp = g.EYE_LOC_GRP
	rigGrp = g.EYE_RIG_GRP
	## Get a list and then rig the eyes in a loop
	def create(self, List):
		## Get the information of the eyeLocs
		self.pos = self.getPosition(List[0])
		
		eyeRigGrp = g.EYE_RIG_GRP
		if mc.objExists(eyeRigGrp) == 0:
			mc.createNode('transform', n = eyeRigGrp, p = g.EYE_CTRL_GRP)
		self.sf_EyeAimCtrlNode = 'eye_AimCtrl' ## This is a parent group of the L/R aimCtrl
		
		if mc.objExists(self.sf_EyeAimCtrlNode):
			self.sf_EyeAimCtrlZero = self.sf_EyeAimCtrlNode + '_zero'
		else:
			self.sf_EyeAimCtrlNode = mc.createNode('transform', n = self.sf_EyeAimCtrlNode)
			self.sf_EyeAimCtrlZero = mc.group(self.sf_EyeAimCtrlNode, n = self.sf_EyeAimCtrlNode + '_zero')
			mc.parent(self.sf_EyeAimCtrlZero, eyeRigGrp)
		## Create The Joint And Freeze
		mc.select(cl = True)
		self.eyeCtrl = mc.joint(n = List[0].replace('Loc','ctrl'))
		self.eyeCtrlDrv = mc.group(self.eyeCtrl, n = self.eyeCtrl + '_drv')
		eyeCtrlZero = mc.group(self.eyeCtrlDrv, n = self.eyeCtrl + '_zero')
		state = 1
		m= re.search('r_|_r_|_r|R_|_R_|R_', eyeCtrlZero)
		if m is not None:
#			mc.setAttr(eyeCtrlZero + '.rotateZ', 180)
			state = -1
		mc.xform(eyeCtrlZero, ws = True, t=(self.pos[0],self.pos[1],self.pos[2]))
    	    
		## Create The Controllers
		ctrl = mc.curve(n='ctrl#', d=1,p = [(0, 0, 0), (0, 0, 3), (0, 1, 2), (0, 0, 3), (0, -1, 2), (0, 0, 3), (-1, 0, 2), (0, 0, 3), (1, 0, 2)], k = [0, 1, 2, 3, 4, 5, 6, 7, 8])
		ctrlShape = mc.listRelatives(ctrl, shapes = True)
		ctrlShape = mc.rename(ctrlShape, List[0].replace('Loc','ctrlShape'))
		rootPos = mc.xform(g.FACE_ROOT_LOC, q = True, ws = True, t = True)
		eyePos = mc.xform(List[0], q = True, ws = True, t = True)
		self.allScale = mc.getAttr(g.JOINT_CTRL_GRP + '.scaleY') 
		mc.setAttr(ctrl + '.s', self.allScale , self.allScale , self.allScale )
		mc.makeIdentity(ctrl, apply = True, t = 0, r = 0, s = 1, n = 0)
		mc.parent(ctrlShape, self.eyeCtrl, r = True, s = True)
		mc.delete(ctrl)
		
		## Set To The Group
		mc.parent(eyeCtrlZero, eyeRigGrp)############## eyeCtrlGrp
		
		self.eyeAimCtrl = mc.curve(n = List[0].replace('Loc','aimCtrl'), d = 1, p = [(0,1,0),(0,-1,0),(0,-1,0),(0,0,0),(-1,0,0),(1,0,0),(0,0,0),(0,0,1),(0,0,-1)], k = [0,1,2,3,4,5,6,7,8])
		eyeAimCtrlShape = mc.listRelatives(self.eyeAimCtrl, s = True)[0]
		eyeAimCtrlShape = mc.rename(eyeAimCtrlShape, List[0].replace('Loc','aimCtrlShape'))
		mc.setAttr(self.eyeAimCtrl + '.s', self.allScale, self.allScale, self.allScale)
		mc.makeIdentity(self.eyeAimCtrl, apply = True, t = 0, r = 0, s = 1, n = 0)
		eyeAimCtrlZero = mc.group(self.eyeAimCtrl, n = self.eyeAimCtrl + '_zero')
		mc.xform(eyeAimCtrlZero, ws = True, t = (self.pos[0], self.pos[1], self.pos[2] + 6 * self.allScale))

		mc.parent(eyeAimCtrlZero, self.sf_EyeAimCtrlNode) ############# self.sf_EyeAimCtrlNode
		
		self.dudgeTheKids(1)
		
		## Add Extra Attributes
		mc.addAttr(self.eyeCtrl, ln = 'aimLock', at = 'double', min = 0, max = 1, dv =1)
		mc.setAttr(self.eyeCtrl + '.aimLock', e = True, keyable = True)
		mc.connectAttr(self.eyeCtrl + '.aimLock', self.eyeCtrlDrv + '_aimConstraint1.'+self.eyeAimCtrl+'W0', force = True)
		
		## Create eyelip
#		try:
		mc.addAttr(self.eyeCtrl, ln = 'goal_ctrl_instance', at = 'enum', en = "Connection:Blue:", k = True)
		mc.setAttr(self.eyeCtrl + '.goal_ctrl_instance', l = True)
		mc.addAttr(self.eyeCtrl, ln = 'eye_upper_X', at = 'double', min = -1, max = 1, dv = 0, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'eye_upper_Y', at = 'double', min = -1, max = 1, dv = 0, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'eye_lower_X', at = 'double', min = -1, max = 1, dv = 0, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'eye_lower_Y', at = 'double', min = -1, max = 1, dv = 0, k = True)
		
		mc.addAttr(self.eyeCtrl, ln = 'set_uprlip', at = 'enum', en = "AboutUprLip:Blue:", k = True)
		mc.setAttr(self.eyeCtrl + '.set_uprlip', l = True)
		mc.addAttr(self.eyeCtrl, ln = 'uprlip_dn_limit', at = 'double', dv = -15, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'uprlip_up_limit', at = 'double', dv = 35, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'uprlip_ty_radio', at = 'double', dv = -20, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'uprlip_ry_radio', at = 'double', dv = 0.3, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'uprlip_rz_radio', at = 'double', dv = -20 * state, k = True)
		
		mc.addAttr(self.eyeCtrl, ln = 'set_lwrlip', at = 'enum', en = "AboutLwrLip:Blue:", k = True)
		mc.setAttr(self.eyeCtrl + '.set_lwrlip', l = True)
		mc.addAttr(self.eyeCtrl, ln = 'lwrlip_dn_limit', at = 'double', dv = -30, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'lwrlip_up_limit', at = 'double', dv = 15, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'lwrlip_ty_radio', at = 'double', dv = 20, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'lwrlip_ry_radio', at = 'double', dv = 0.3, k = True)
		mc.addAttr(self.eyeCtrl, ln = 'lwrlip_rz_radio', at = 'double', dv = 20 * state, k = True)
#		except:
#			pass
		goalUpperAttrX = self.eyeCtrl + '.eye_upper_X'
		goalUpperAttrY = self.eyeCtrl + '.eye_upper_Y'
		goalLowerAttrX = self.eyeCtrl + '.eye_lower_X'
		goalLowerAttrY = self.eyeCtrl + '.eye_lower_Y'
		
		upperLipDnLimit = self.eyeCtrl + '.uprlip_dn_limit'
		upperLipUpLimit = self.eyeCtrl + '.uprlip_up_limit'
		upperLipGoalRadioTy = self.eyeCtrl + '.uprlip_ty_radio'
		upperLipGoalRadioRy = self.eyeCtrl + '.uprlip_ry_radio'
		upperLipGoalRadioRz = self.eyeCtrl + '.uprlip_rz_radio'
		
		lowerLipDnLimit = self.eyeCtrl + '.lwrlip_dn_limit'
		lowerLipUpLimit = self.eyeCtrl + '.lwrlip_up_limit'
		lowerLipGoalRadioTy = self.eyeCtrl + '.lwrlip_ty_radio'
		lowerLipGoalRadioRy = self.eyeCtrl + '.lwrlip_ry_radio'
		lowerLipGoalRadioRz = self.eyeCtrl + '.lwrlip_rz_radio'
		
		upperAttList = [goalUpperAttrX, goalUpperAttrY, upperLipDnLimit, upperLipUpLimit, upperLipGoalRadioTy, upperLipGoalRadioRy, upperLipGoalRadioRz]
		lowerAttList = [goalLowerAttrX, goalLowerAttrY, lowerLipDnLimit, lowerLipUpLimit, lowerLipGoalRadioTy, lowerLipGoalRadioRy, lowerLipGoalRadioRz]
		
		upperLipJnt = self.createLipJnt( List[0], self.pos, 1, 'upperLip_Jnt')
		lowerLipJnt = self.createLipJnt( List[0], self.pos, 1, 'lowerLip_Jnt')
		self.setUpperlip( upperLipJnt, lowerLipJnt, self.eyeCtrl, self.eyeCtrlDrv, upperAttList, 1)
		self.setLowerlip( upperLipJnt, lowerLipJnt, self.eyeCtrl, self.eyeCtrlDrv, lowerAttList, 1)

		
		## Hide LocGrp
		eyeJntGrp = mc.listRelatives(List[0], parent = True)[0]
		mc.parent(eyeJntGrp, self.eyeCtrl)
		mc.hide(eyeJntGrp )
		
		
	def dudgeTheKids(self, state):
		## Dudge The Kids' Number Of The self.sf_EyeAimCtrlNode
		[mc.setAttr(self.sf_EyeAimCtrlNode + attr, lock = False, keyable = True, channelBox = True) for attr in ['.rx', '.ry', '.rz', '.sx', '.sy', '.sz']]

		eyeCtrlKids = mc.listRelatives(self.sf_EyeAimCtrlNode, children = True, type = 'transform')
		
		mc.select(eyeCtrlKids)
		mc.Unparent()
		
		## Get the information of the eyes' distance to operate the scale
		kidPosX = 0
		kidPosY = 0
		kidPosZ = 0
		listX = []
		listY = []

		kid = 0
		while (kid < len(eyeCtrlKids)):
			kidPos = mc.xform(eyeCtrlKids[kid], query = True, ws = True, t = True)
			kidPosX = kidPosX + kidPos[0]
			kidPosY = kidPosY + kidPos[1]
			kidPosZ = kidPosZ + kidPos[2]
			listX.append(kidPos[0])
			listY.append(kidPos[1])
			kid += 1
		kidPosCenX = kidPosX / len(eyeCtrlKids)
		kidPosCenY = kidPosY / len(eyeCtrlKids)
		kidPosCenZ = kidPosZ / len(eyeCtrlKids)
		mc.xform(self.sf_EyeAimCtrlZero, ws = True, t = (kidPosCenX, kidPosCenY, kidPosCenZ)) ############## sf_EyeAimCtrlZero
		## Get The Scale Ratio
		maxX = max(listX)
		minX = min(listX)
		maxY = max(listY)
		minY = min(listY)
		#scaleX = abs(maxX - minX) / 1.790072 / 2
		#scaleY = abs(maxY - minY) + 1
		
		## Edit the sf_EyeAimCtrlNode
		mc.parent(eyeCtrlKids, self.sf_EyeAimCtrlNode) ############# self.sf_EyeAimCtrlNode
		mc.aimConstraint(self.eyeAimCtrl, self.eyeCtrlDrv,offset = (0, 0, 0), weight = 1, aimVector = (0, 0, 1), upVector = (0, 1 * state, 0),worldUpType = "vector", worldUpVector = (0,1,0))
		
		bmaxX = mc.getAttr(self.sf_EyeAimCtrlZero + '.boundingBox.boundingBoxMax.boundingBoxMaxX')
		bminX = mc.getAttr(self.sf_EyeAimCtrlZero + '.boundingBox.boundingBoxMin.boundingBoxMinX')
		bmaxY = mc.getAttr(self.sf_EyeAimCtrlZero + '.boundingBox.boundingBoxMax.boundingBoxMaxY')
		bminY = mc.getAttr(self.sf_EyeAimCtrlZero + '.boundingBox.boundingBoxMin.boundingBoxMinY')
		scaleX = self.allScale * abs(bmaxX - bminX) / 2 / 3
		scaleY = self.allScale * abs(bmaxY - bminY) / 2
		if len(eyeCtrlKids) > 1:
			aimCurve = mc.curve(n='ctrl#', d=1,p = [(-3, 1, 0), (-3, -1, 0), (3, -1, 0), (3, 1, 0), (-3, 1, 0)], k = [0, 1, 2, 3, 4])
			aimCurveShape = mc.listRelatives(aimCurve, shapes = True)
			mc.setAttr(aimCurve + '.s', scaleX, scaleY, 1)
			mc.makeIdentity(aimCurve, apply = True, t = 0, r = 0, s = 1, n = 0)
			mc.parent(aimCurveShape[0], self.sf_EyeAimCtrlNode, r = True , s = True)
			aimCurveShape = mc.rename(aimCurveShape, self.sf_EyeAimCtrlNode + 'Shape')
			mc.delete(aimCurve)
		else:
			pass
		
		mc.select(cl = True)
		self.lockAndHide()
	
	## Lock And Hide The Unuseful Attributes
		
	def lockAndHide(self):
		attrs = ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v', '.radi'] ## List All Attributes
			
		[mc.setAttr(self.eyeCtrl + attr, lock = True, keyable = False, channelBox = False) for attr in attrs if attr not in ['.rx','.ry']] ## Set The eyeCtrl
		
		[mc.setAttr(self.eyeAimCtrl + attr, lock = True, keyable = False, channelBox = False) for attr in attrs if attr not in ['.tx', '.ty', '.tz', '.radi']] ## Set The self.eyeAimCtrl
		
		[mc.setAttr(self.sf_EyeAimCtrlNode + attr, lock = True, keyable = False, channelBox = False) for attr in attrs if attr not in ['.tx', '.ty', '.tz', '.radi']] ## Set The self.sf_EyeAimCtrlNode
	def locBack(self):
		import utility as u
		locList = u.getNodeInGrp(g.EYE_RIG_GRP, 'locator')
		if mc.objExists(g.EYE_LOC_GRP) == 0:
			mc.createNode('transform', n = g.EYE_LOC_GRP, p = g.EYE_CTRL_GRP)
		for obj in locList:
			locGrp = mc.listRelatives(obj, parent = True)[0]
			mc.parent(locGrp, g.EYE_LOC_GRP)
			mc.showHidden(locGrp)
		mc.delete(g.EYE_RIG_GRP)
		mc.select(obj)
		
	def createLipJnt(self, loc, pos, state, fix):
		mc.select( cl = True )
		jnt = mc.joint(n = loc.replace('Loc', fix))
		grp = mc.group(jnt, n = jnt + '_zero')
		mc.xform(grp, ws = True, t = pos)
#		if not state:
#			mc.setAttr(grp + '.rz', 180)
		eyelipGrp = 'eyelipRigGrp'
		if not mc.objExists(eyelipGrp):
			mc.createNode('transform', n = eyelipGrp, p = g.EYE_RIG_GRP)	
		mc.parent(grp, eyelipGrp)
		return jnt
	
	def setUpperlip(self, upperJnt, lowerJnt, eyeCtrl, eyeCtrlGrp, upperAttrList, state):
		goalUpperAttrX, goalUpperAttrY, upperLipDnLimit, upperLipUpLimit, upperLipGoalRadioTy, upperLipGoalRadioRy, upperLipGoalRadioRz = upperAttrList
		
		# Set rotateX
		clampAInput1 = upperLipDnLimit #-15
		clampAInput2 = self.addFn([lowerJnt + '.rotateX', upperLipUpLimit]) #35
		clampAInput3 = self.addFn([eyeCtrl + '.rotateX', eyeCtrlGrp + '.rotateX'])
		clampAOutput = self.clampFn(clampAInput1, clampAInput2, clampAInput3)
		
		clampBOutput = self.clampFn(-1, 0.7, goalUpperAttrY)
		
		outputX =  self.addFn([ self.multiplyDivideFn(clampAOutput, 0.8), self.multiplyDivideFn( self.multiplyDivideFn( clampBOutput, upperLipGoalRadioTy ), state)])
		
		# Set rotateY
		goalRadioY = upperLipGoalRadioRy # 0.3
		print 'Find rotateY:',goalRadioY
		outputY = self.multiplyDivideFn( self.addFn([eyeCtrl + '.rotateY', eyeCtrlGrp + '.rotateY']), goalRadioY )
		
		# Set rotateZ
		goalRadioZ = upperLipGoalRadioRz #20
		outputZ = self.multiplyDivideFn(goalUpperAttrX, goalRadioZ)
		
		mc.connectAttr(outputX, upperJnt + '.rotateX')
		mc.connectAttr(outputY, upperJnt + '.rotateY')
		mc.connectAttr(outputZ, upperJnt + '.rotateZ')
		
	def setLowerlip(self, upperJnt, lowerJnt, eyeCtrl, eyeCtrlGrp, lowerAttrList, state):
		goalLowerAttrX, goalLowerAttrY, lowerLipDnLimit, lowerLipUpLimit, lowerLipGoalRadioTy, lowerLipGoalRadioRy, lowerLipGoalRadioRz = lowerAttrList
		# Set rotateX
		clampAInput1 = lowerLipDnLimit #-30
		clampAInput2 = lowerLipUpLimit #15
		goalRadioX1 = 0.3
		goalRadioX2 = 0.5
		clampAInput3a = self.multiplyDivideFn( self.addFn([eyeCtrl + '.rotateX', eyeCtrlGrp + '.rotateX']), goalRadioX1 )
		clampAInput3b = self.clampFn( 0, 40, self.multiplyDivideFn( self.addFn([eyeCtrl + '.rotateX', eyeCtrlGrp + '.rotateX']), goalRadioX2 ) )
		clampAInput3 = self.addFn([clampAInput3a, clampAInput3b])
		clampAOutput = self.clampFn(clampAInput1, clampAInput2, clampAInput3)
		
		clampBInput1 = -0.25
		clampBInput2 = 0.7
		goalRadioY = lowerLipGoalRadioTy #20
		clampBOutput = self.multiplyDivideFn( self.clampFn(clampBInput1, clampBInput2, goalLowerAttrY), goalRadioY )
		
		outputX = self.multiplyDivideFn( self.addFn([clampAOutput, clampBOutput]), state )
		
		# Set rotateY
		goalRadioY = lowerLipGoalRadioRy #0.3 
		outputY = self.multiplyDivideFn( self.addFn([eyeCtrl + '.rotateY', eyeCtrlGrp + '.rotateY']), goalRadioY )
		
		# Set rotateZ
		goalRadioZ = lowerLipGoalRadioRz #20
		outputZ = self.multiplyDivideFn(goalLowerAttrX, goalRadioZ)
		
		mc.connectAttr(outputX, lowerJnt + '.rotateX')
		mc.connectAttr(outputY, lowerJnt + '.rotateY')
		mc.connectAttr(outputZ, lowerJnt + '.rotateZ')
		
	def clampFn(self, input1, input2, input3):
		node = mc.createNode('clamp')
		try:
			mc.setAttr(node + '.minR', input1)
		except:
			mc.connectAttr(input1, node + '.minR')
			
		try:
			mc.setAttr(node + '.maxR', input2)
		except:
			mc.connectAttr(input2, node + '.maxR')
		mc.connectAttr(input3, node + '.inputR')
		output = node + '.outputR'
		return output
	
	def addFn(self, List):
		node = mc.createNode('plusMinusAverage')
		for i in range(len(List)):
			try:
				mc.setAttr('%s.input1D[%d]' % (node, i), List[i])
			except:
				mc.connectAttr(List[i], '%s.input1D[%d]' % (node, i))
		output = node + '.output1D'
		return output
	
	def multiplyDivideFn(self, input1, input2):
		node = mc.createNode('multiplyDivide')
		try:
			mc.setAttr(node + '.input1X', input1)
		except:
			mc.connectAttr(input1, node + '.input1X')
			
		try:
			mc.setAttr(node + '.input2X', input2)
		except:
			mc.connectAttr(input2, node + '.input2X')
		
		output = node + '.outputX'
		return output
	
			
			

