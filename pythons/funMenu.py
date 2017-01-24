import maya.cmds as cmds
def start():
	funMainMenu = cmds.menu(label = 'fun.zheng', tearOff = True, parent = 'MayaWindow')
	cmds.menuItem(label = 'three.js', subMenu = True)
	cmds.menuItem(label = 'import and export project datas', command = 'import threejs.importAndExport.importAndExport as imEx; reload(imEx); imEx.main()')
	cmds.setParent(funMainMenu, menu = True)
	cmds.menuItem(label = 'misc', subMenu = True)
	cmds.menuItem(label = 'generate cubemap', command = 'import misc.renderCubemap as renCm; reload(renCm); renCm.main()')
	cmds.menuItem(label = 'calculator volume', command = 'import misc.volumeCalculator as vc; reload(vc); vc.main()')
if __name__ == '__main__':
	start();
