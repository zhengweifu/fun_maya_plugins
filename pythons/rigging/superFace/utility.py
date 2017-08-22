from maya.cmds import *
from sfGlobal import *

def getNodeInGrp(node, shapeType):
	allLesves = []
	chds = listRelatives(node, ad = True, type = shapeType)
	for chd in chds:
		node = listRelatives(chd, parent = True)[0]
		allLesves.append(node)
	return allLesves

def clamp(minValue, maxValue, value):
	if value <= minValue:
		outputValue = minValue
	elif value >= maxValue:
		outputValue = maxValue
	else:
		outputValue = value