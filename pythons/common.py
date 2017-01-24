import maya.OpenMaya as om

class Common(object):
	@classmethod
	def MMatrixToArray(self, mMatrix):
		result = []
		for i in range(4):
			for j in range(4):
				result.append(om.MScriptUtil.getDoubleArrayItem(mMatrix[i], j))
		return result