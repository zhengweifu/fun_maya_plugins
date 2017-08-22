from jointCtrl import *
import maya.mel as mm

class chinCtrl(jointCtrl):
	locGrp = g.CHIN_LOC_GRP
	rigGrp = g.CHIN_RIG_GRP
	def create(self, List):
		List.sort()
		mc.select(cl = True)
		jnts = []
		i = 0
		while (i < len(List)):
			pos = self.getPosition(List[i])
			jnt = mc.joint(n = List[i].replace('Loc', 'Jnt'), p = (pos[0], pos[1], pos[2]))
			jnts.append(jnt)
			i += 1
		mc.joint(jnts[0], e = True, zso = True, ch = True, oj = 'xyz', sao = 'yup')
		
		allChinRigGrp = self.rigGrp
		chinRigGrp = mc.listRelatives(List[0], parent = True)[0].replace('Loc', 'Rig')
		
		if mc.objExists(allChinRigGrp) == 0:
			mc.createNode('transform', n = allChinRigGrp, p = g.CHIN_CTRL_GRP)
		if mc.objExists(chinRigGrp) == 0:
			mc.createNode('transform', n = chinRigGrp, p = allChinRigGrp)
		
		mc.parent(jnts[0], chinRigGrp)
		#mc.rename(jnts[-1], jnts[-1].replace('Ctrl', 'JntTip'))	

		k = 0
		while (k < len(jnts) - 1):
			mc.select(jnts[k])

			[mc.setAttr(jnts[k] + attr, lock = True, keyable = False, channelBox = False) for attr in ['.sx', '.sy', '.sz', '.v', '.radi']]

			self.setToZero(postfix = '_drv')
			self.setToZero(postfix = '_zero')
			#self.setToZero()
			#stringCurveChin = 'createNode nurbsCurve -n %s -p %s; setAttr -k off ".v"; setAttr ".ove" yes; setAttr ".cc" -type "nurbsCurve" 1 11 0 no 3 12 0 1 2 3 4 5 6 7 8 9 10 11 12 0 0 0 5.3570837727925822 4.638654233995316e-016 0 5.5562625211552215 0.61301051460911149 0 6.0777206347589257 0.99187329975731642 0 6.7222793652410608 0.99187329975731853 0 7.2437374788447721 0.61301051460911249 0 7.4429162272074105 -1.1506938070090568e-016 0 7.2437374788447721 -0.61301051460911105 0 6.7222793652410591 -0.99187329975731642 0 6.0777206347589257 -0.99187329975731642 0 5.5562625211552197 -0.61301051460911127 0 5.3570837727925822 4.638654233995316e-016 0;' % (jnts[k] + 'Shape', jnts[k])
			#mm.eval(stringCurveChin)
			k += 1
		#print jnts
		posBaseJnt = mc.xform(jnts[0], q = True, ws = True, t = True)
		posTipJnt = mc.xform(jnts[1], q = True, ws = True, t = True)
		
		distance = ((posBaseJnt[0] - posTipJnt[0]) ** 2 + (posBaseJnt[1] - posTipJnt[1]) ** 2 + (posBaseJnt[2] - posTipJnt[2]) ** 2 ) ** 0.5
		scale = distance / 4
		# ctrl = mc.curve(n='ctrl#', d=1,p = [(0, 0, 0), (5.3570837727925822, 4.638654233995316e-016, 0), (5.5562625211552215, 0.61301051460911149, 0), (6.0777206347589257, 0.99187329975731853, 0), (6.7222793652410608, 0.99187329975731853, 0), (7.2437374788447721, 0.61301051460911249, 0), (7.4429162272074105, -1.1506938070090568e-016, 0), ( 7.2437374788447721, -0.61301051460911105, 0), (6.7222793652410591, -0.99187329975731642, 0), (6.0777206347589257, -0.99187329975731642, 0), (5.5562625211552197, -0.61301051460911127, 0), (5.3570837727925822, 4.638654233995316e-016, 0)], k = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
		# ctrlShape = mc.listRelatives(ctrl, s = True)[0]
		# mc.rename(ctrlShape, '%sShape'%jnts[0])
		# mc.setAttr(ctrl + '.s', scale, scale, scale)
		# mc.makeIdentity(ctrl, apply = True, t = 0, r = 0, s = 1, n = 0)
		# ctrlShape = mc.listRelatives(ctrl, shapes = True)
		# mc.parent(ctrlShape[0], jnts[0], r = True, s = True)
		# mc.delete(ctrl)
		# mc.select(cl = True)
		## Hide LocGrp
		#mc.hide( mc.listRelatives(List[0], parent = True) )
		
		## Hide The Locs
		n = 0
		while n < len(jnts):
			mc.parent(List[n], jnts[n])
			mc.hide(List[n])
			n += 1
		
	## Set To Zero
	def setToZero(self,postfix):
		sel = mc.ls(sl = True)
		objPos = mc.xform(sel[0], q = True, ws = True, t = True)
		rot = mc.xform(sel[0], q = True, ws = True, ro = True)
		zeroNode = mc.createNode('transform', n = sel[0] + postfix)
		mc.xform(zeroNode, ws = True, t = (objPos[0], objPos[1], objPos[2]))
		mc.xform(zeroNode, ws = True, ro = (rot[0], rot[1], rot[2]))
		parent = mc.listRelatives(sel[0], parent = True)

		if len(parent) > 0:
			mc.parent(sel[0], zeroNode)
			mc.parent(zeroNode, parent[0])
		else:
			mc.parent(zeroNode, parent[0])
			

		
	