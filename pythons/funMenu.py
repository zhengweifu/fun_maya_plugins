import maya.cmds as cmds
def start():
	funMainMenu = cmds.menu(label = 'fun.zheng', tearOff = True, parent = 'MayaWindow')
	cmds.menuItem(label = 'modeling', subMenu = True)
	cmds.menuItem(label = 'Checking Box', command = 'import modeling.checkModel as cm; reload(cm); cm.checkModel()')
	cmds.setParent(funMainMenu, menu = True)
	cmds.menuItem(label = 'animation', subMenu = True)
	cmds.menuItem(label = 'animation panel', command = 'import animation.StartSYH_anim as s_anim; reload(s_anim); s_anim.main()')
	cmds.setParent(funMainMenu, menu = True)
	cmds.menuItem(label = 'rigging', subMenu = True)
	cmds.menuItem(label = 'SuperFace', command = 'import rigging.superFace as sf; reload(sf); sf.main()')
	cmds.setParent(funMainMenu, menu = True)
	cmds.menuItem(label = 'three.js', subMenu = True)
	cmds.menuItem(label = 'import and export mesh', command = 'import threejs.importAndExport.meshFileManager as immesh; reload(immesh); immesh.main()')
	cmds.menuItem(label = 'import and export project datas', command = 'import threejs.importAndExport.importAndExport as imEx; reload(imEx); imEx.main()')
	cmds.setParent(funMainMenu, menu = True)
	cmds.menuItem(label = 'misc', subMenu = True)
	cmds.menuItem(label = 'import and export stl', command = 'import misc.stlFileManager as imstl; reload(imstl); imstl.main()')
	cmds.menuItem(label = 'generate cubemap', command = 'import misc.renderCubemap as renCm; reload(renCm); renCm.main()')
	cmds.menuItem(label = 'calculator volume', command = 'import misc.volumeCalculator as vc; reload(vc); vc.main()')
if __name__ == '__main__':
	start();
