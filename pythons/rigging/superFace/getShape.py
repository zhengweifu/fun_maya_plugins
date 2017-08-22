from maya.cmds import *
from math import *
class getShape:
	def getShape(self):
		vtxList = ls(sl = True, fl = True)

		model = vtxList[0].split('.')[0]
		meshShape = listRelatives(model, shapes = True)[0]
#		vtxList = ls(model + '.vtx[*]', fl = True)
		
		
		radius = []
		posX = []
		posY = []
		posZ = []
		for vtx in vtxList:
			pos = xform(vtx, q = True, ws = True, t = True)
			posX.append(pos[0])
			posY.append(pos[1])
			posZ.append(pos[2])
			[radius.append(item) for item in pos]
		maxRadius = max(radius)
		dis = maxRadius + 2.5
		
		sumX = 0
		sumY = 0
		sumZ = 0
		for i in range(len(vtxList)):
			sumX = sumX + posX[i]
			sumY = sumY + posY[i]
			sumZ = sumZ + posZ[i]
		cenX = sumX / len(vtxList)
		cenY = sumY / len(vtxList)
		cenZ = sumZ / len(vtxList)
		print cenZ, '???'
		
		cpom = createNode('closestPointOnMesh')
		connectAttr(meshShape+'.worldMesh[0]',cpom+'.inMesh')
		setAttr(cpom + '.inPositionZ', cenZ + 1)
		
		vtxList2 = []
		degree = 0
		while degree < 360:
			x = cos(radians(degree)) * dis
			y = sin(radians(degree)) * dis
			setAttr(cpom + '.inPositionX', x + cenX)
			setAttr(cpom + '.inPositionY', y + cenY)
			num = getAttr((cpom + ".closestVertexIndex"))
			vtxName = model + '.vtx[' + str(num) +']'
			vtxList2.append(vtxName)
			degree += 1
			
		vtxListNew = []
		[vtxListNew.append(item) for item in vtxList2 if item not in vtxListNew if item in vtxList]
		print vtxListNew
		posList = []
		for vtx in vtxListNew:
			pos = xform(vtx, q = True, ws = True, t = True)
			posNew = [pos[0], pos[1], 0]
			posList.append(posNew)
		
		cur = curve(n = 'Outline', d = 3, p = posList)
		closeCurve(cur, ch = True, ps = True, rpo = True, bki = False)
		
	
