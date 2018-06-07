# -*- coding: utf-8 -*-
import importAndExport
import rendering.Utils as rend_utils
import os, uuid, time, shutil, json, sys
import maya.mel as mel
import maya.cmds as cmds


reload(importAndExport)
reload(rend_utils)
# reload(sys)
# sys.setdefaultencoding('utf-8') 

class JXZYBatch(object):
	def __init__(self, sourceFbxDir, textureDir, outputDir):
		self.sourceFbxDir = sourceFbxDir
		self.textureDir = textureDir
		self.outputDir = outputDir
		self.imExport = importAndExport.ImportAndExport();
		self.output = []


	def _each(self, fbxDir, dirName):
		cmds.file(new = 1, f = 1)
		fbxFile = os.path.join(fbxDir, "model.FBX")
		imageFile = os.path.join(fbxDir, "image.jpg")
		if os.path.isfile(fbxFile):
			importCommand = 'file -import -type "FBX"  -ignoreVersion -ra true -mergeNamespacesOnClash false -options "fbx"  -pr "%s"'%fbxFile;
			mel.eval(importCommand);
			_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, `time.time()`))
			rend_utils.Utils.create().changeFilePath(self.textureDir, True, ".jpg")
			_dir = os.path.join(self.outputDir, _uuid)
			if not os.path.isdir(_dir):
				os.makedirs(_dir)
			_pFile = os.path.join(_dir, _uuid + ".project")
			self.imExport.writeProject(_pFile)
			if os.path.isfile(imageFile):
				shutil.copy(imageFile, os.path.join(_dir, "cover.jpg"))
			_outputItem = {
				"name": dirName,
				"image": "assets/case/%s/cover.jpg"%_uuid,
				"introduce": u"制首乌为何首乌的炮制加工品，表面黑褐色或棕褐色，凹凸不平。质坚硬，断面角质样，棕褐色或黑色。气微，味微甘而苦涩。置干燥处，防蛀。",
				"project": "assets/case/%s/%s.project"%(_uuid, _uuid)
			}
			self.output.append(_outputItem)


	def batch(self, isPutty):
		for s in os.listdir(self.sourceFbxDir):
			if s != '.DS_Store':
				# continue
				fbxDir = os.path.join(self.sourceFbxDir, s)
				if os.path.isdir(fbxDir):
					self._each(fbxDir, s)
					# break
		if isPutty:
			_outputJson = json.dumps(self.output, sort_keys = True, indent = 2, separators = (',', ': '))
		else:
			_outputJson = json.dumps(self.output, separators = (',', ':'))

		url = os.path.join(os.path.dirname(self.outputDir), 'productInfo.json')
		_f = open(url, 'w')
		try:
			_f.write(_outputJson)
		finally:
			_f.close()

def main():
	jxzy_batch = JXZYBatch("/Users/zwf/Documents/zwf/templates/yinpian_2018-6-6/fbx", "/Users/zwf/Documents/zwf/templates/yinpian_2018-6-6/textures_jpg", "/Users/zwf/Documents/zwf/rd/web/JXZY/assets/case")
	jxzy_batch.batch(True)