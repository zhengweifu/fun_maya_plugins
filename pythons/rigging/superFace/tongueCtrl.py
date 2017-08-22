from jointCtrl import *
import maya.mel as mm

class tongueCtrl(jointCtrl):
	locGrp = g.TONGUE_LOC_GRP
	rigGrp = g.TONGUE_RIG_GRP
	def create(self, List):
		mc.select(cl = True)
		List.sort()
		jnts = []
		i = 0
		while (i < len(List)):
			pos = self.getPosition(List[i])
			jnt = mc.joint(n = List[i].replace('Loc', 'Ctrl'), p = (pos[0], pos[1], pos[2]))
			jnts.append(jnt)
			i += 1
		#mc.rename(jnts[-1], jnts[-1].replace('Ctrl', 'JntTip'))
		mc.joint(jnts[0], e = True, zso = True, ch = True, oj = 'xyz', sao = 'yup')
		
		allTongueRigGrp = g.TONGUE_RIG_GRP
		tongueRigGrp = mc.listRelatives(List[0], parent = True)[0].replace('Loc', 'Rig')
		
		if mc.objExists(allTongueRigGrp) == 0:
			mc.createNode('transform', n = allTongueRigGrp, p = g.TONGUE_CTRL_GRP)
		if mc.objExists(tongueRigGrp) == 0:
			mc.createNode('transform', n = tongueRigGrp, p = allTongueRigGrp)

		mc.parent(jnts[0], tongueRigGrp)

		
		k = 0
		while (k < len(jnts) - 1):
			mc.select(jnts[k])

			[mc.setAttr(jnts[k] + attr, lock = True, keyable = False, channelBox = False) for attr in ['.sx', '.sy', '.sz', '.v', '.radi']]

			self.setToZero()
			#stringCurveTongue = 'createNode nurbsCurve -n %s -p %s; setAttr -k off ".v"; setAttr ".cc"  -type "nurbsCurve" 3 8 2 no 3 13 -2 -1 0 1 2 3 4 5 6 7 8 9 10 11 4.0129729326112725e-016 0.40378865824763382 -0.78361162489122504 / 3.2145153411776922e-016 0.57104339682623884 1.2643170607829333e-016//5.3303825933859776e-017 0.40378865824763405 0.78361162489122427 / -2.4606854055573001e-016 1.6547409002244672e-016 1.1081941875543879 / -4.0129729326112715e-016 -0.40378865824763394 0.78361162489122449 / -3.2145153411776947e-016 -0.57104339682623895 3.339205363590519e-016 / -5.3303825933859875e-017 -0.4037886582476341 -0.78361162489122382 / 2.4606854055572992e-016 -3.0670852238940873e-016 -1.1081941875543879 / 4.0129729326112725e-016 0.40378865824763382 -0.78361162489122504 / 3.2145153411776922e-016 0.57104339682623884 1.2643170607829333e-016 / 5.3303825933859776e-017 0.40378865824763405 0.78361162489122427;' % (jnts[k] + 'Shape', jnts[k])
			#mm.eval(stringCurveTongue)
			k += 1
			
		s = 1
		while (s < len(jnts)):
			posUp = mc.xform(jnts[s-1], q = True, ws = True, t = True)
			posDn = mc.xform(jnts[s], q = True, ws = True, t = True)
			distance = ((posUp[0] - posDn[0])**2 + (posUp[1] - posDn[1])**2 + (posUp[2] - posDn[2]) ** 2 ) ** 0.5
			scale = distance / 0.433569
			ctrl = mc.curve(n='ctrl#', d=3,p = [(4.0129729326112725e-016, 0.40378865824763382, -0.78361162489122504), 
					(3.2145153411776922e-016, 0.57104339682623884, 1.2643170607829333e-016), (5.3303825933859776e-017, 0.40378865824763405, 0.78361162489122427), 
					(-2.4606854055573001e-016, 1.6547409002244672e-016, 1.1081941875543879), (-4.0129729326112715e-016, -0.40378865824763394, 0.78361162489122449), 
					(-3.2145153411776947e-016, -0.57104339682623895, 3.339205363590519e-016), (-5.3303825933859875e-017, -0.4037886582476341, -0.78361162489122382), 
					(2.4606854055572992e-016, -3.0670852238940873e-016, -1.1081941875543879), (4.0129729326112725e-016, 0.40378865824763382, -0.78361162489122504), 
					(3.2145153411776922e-016, 0.57104339682623884, 1.2643170607829333e-016), (5.3303825933859776e-017, 0.40378865824763405, 0.78361162489122427)], 
					k = [-2,-1,0, 1, 2, 3, 4, 5, 6, 7,8,9,10])
			ctrlShape = mc.listRelatives(ctrl, shapes = True)[0]
			ctrlShape = mc.rename(ctrlShape, '%sShape'%jnts[s-1])
			mc.setAttr(ctrl + '.s', scale , scale , scale )
			mc.makeIdentity(ctrl, apply = True, t = 0, r = 0, s = 1, n = 0)
			mc.parent(ctrlShape, jnts[s-1], r = True, s = True)
			mc.delete(ctrl)

			s += 1
		mc.select(cl = True)
		
		## Hide The Locs
		n = 0
		while n < len(jnts):
			mc.parent(List[n], jnts[n])
			mc.hide(List[n])
			n += 1
		#mc.hide( mc.listRelatives(List[0], parent = True) )

		
	## Set To Zero
	def setToZero(self):
		sel = mc.ls(sl = True)
		objPos = mc.xform(sel[0], q = True, ws = True, t = True)
		rot = mc.xform(sel[0], q = True, ws = True, ro = True)
		zeroNode = mc.createNode('transform', n = sel[0] + '_zero')
		mc.xform(zeroNode, ws = True, t = (objPos[0], objPos[1], objPos[2]))
		mc.xform(zeroNode, ws = True, ro = (rot[0], rot[1], rot[2]))
		parent = mc.listRelatives(sel[0], parent = True)

		if len(parent) > 0:
			mc.parent(sel[0], zeroNode)
			mc.parent(zeroNode, parent[0])
		else:
			mc.parent(zeroNode, parent[0])


				
				
				


			