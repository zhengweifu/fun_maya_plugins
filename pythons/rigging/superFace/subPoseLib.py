from sfGlobal import *
import os
import maya.cmds as mc
from utility import *
class subPoseLib:
	
#	## Get All Of The SubCtrls
#	def getLeaf(self, node):
#		allLesves = []
#		chds = mc.listRelatives(node, children = True, type = 'transform')
#		if chds==None:
#			return [node]
#		for chd in chds:
#			if mc.nodeType(chd) != 'transform':
#				continue
#			allLesves.extend(self.getLeaf(chd))
#		return allLesves


	
	## Get The SubCtrls' Name
	def getTxtInfo(self, subCtrls):
		txt = []
		for subCtrl in subCtrls:
			pos = mc.getAttr(subCtrl + '.t')
			rot = mc.getAttr(subCtrl + '.r')
			print pos
			string = subCtrl + ' ' + str(pos[0][0]) + ' ' + str(pos[0][1]) + ' ' + str(pos[0][2]) + ' ' + str(rot[0][0]) + ' ' + str(rot[0][1]) + ' ' + str(rot[0][2]) + '\n'
			txt.append(string)
		print txt
		return txt
	
	## Create A .sf File To Get The Information
	def writeTxt(self, drvObj, attr, drvValue):
		filename = attr + '_' + str(drvValue) + '_V'
		filePath = g.SUB_POSE_LIB_PATH + '/' + drvObj + '/'
		postfix = '.sf'
		subCtrls = getNodeInGrp(g.SUB_CTRL_LIST_GRP, 'nurbsCurve')
		txt = self.getTxtInfo(subCtrls)
		if not os.path.isdir(filePath):
			os.mkdir(filePath)
		i = 1
		while i:
			if not os.path.isfile(filePath + filename + str(i) + postfix):
				break
			i+=1
		fileHandle = open(filePath + filename +str(i) + postfix, 'w')
		fileHandle.writelines(txt)
		fileHandle.close()
		return 'Save succeed!'
	
	## Get The Info From The .sf File And SetAttr
	def readTxt(self, drvObj, filename):
		fullPath = g.SUB_POSE_LIB_PATH + '/' + drvObj + '/' + filename
		fileContect = open(fullPath, 'r')
		fileList = fileContect.readlines()
		for i in range(len(fileList)):
			newList = fileList[i].strip().split()
			mc.setAttr(newList[0] + '.t', float(newList[1]), float(newList[2]), float(newList[3]))
			mc.setAttr(newList[0] + '.r', float(newList[4]), float(newList[5]), float(newList[6]))
		return 'Read '
		
	## Get The List Of The Files
	
	def getFileList(self, drvObj, attr):
		fullPath = g.SUB_POSE_LIB_PATH + '/' + drvObj
		allFiles = []
		if os.path.isdir(fullPath):
			allFiles = os.listdir(fullPath)
		return allFiles
	
