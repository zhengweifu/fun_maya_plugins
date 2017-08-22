from sfGlobal import *
from maya.cmds import *
import maya.mel as mm
from lib import *

class mainUI:
    global currentRoot
    currentRoot = ''
    
    Title = 'Super Face'
    win = None
    root = None
    win_width = 328
    win_height = 500
    def __init__(self,name):
        self.win = name
    def build(self):
        if window(self.win, exists=1):
            deleteUI(self.win)
            #print 'Exists window:',self.win
            #return
        window(self.win, title = self.Title)
        self.buildRoot()
        state = rootUI()
        state.Layout(self.root)
        state.build()

        #print 'Last size:',window(self.win,q=1,wh=1)
        window(self.win,e=1,wh=[self.win_width,self.win_height])
    def buildRoot(self):
        self.root = formLayout('mainForm',numberOfDivisions=100)
        #self.root = columnLayout(adj=1)
    def show(self):
        showWindow(self.win)
        
    def close(self, *args):
        deleteUI(self.win)

    def cleanup(self,root):
        chdn = layout(root, q=1, ca=1)
        if not chdn==None:
            for chd in chdn:
                deleteUI(chd)#, layout=1
    def update(self,*args):
        self.cleanup(self.root)
        setParent(self.root)
        # build layouts
    def title(self,title=''):
        if window(self.win, exists=1) and title!='':
            self.Title = title
            window(self.win, e=1, title = self.Title)
        return self.Title
    def width(self, width=''):
        if window(self.win, exists=1) and width!='':
            self.win_width = width
            window(self.win, e=1, width = self.win_width)
        return self.win_width
    def height(self, height=''):
        if window(self.win, exists=1) and height!='':
            self.win_height = height
            window(self.win, e=1, height = self.win_height)
        return self.win_height

class rootUI:
    #global currentRoot
    currentRoot = None
    rootLayout = None
    def __init__(self):
        pass
        #self.build()
        #self.tabs = columnLayout(adj=1)
        #state.rootLayout = self.tabs
        #state.buildTabs()
    def Layout(self, ui):
        self.root = ui
    def cleanup(self,root):
        chdn = layout(root, q=1, ca=1)
        if not chdn==None:
            for chd in chdn:
                deleteUI(chd)
    def build(self):
        self.cleanup(self.root)
        setParent(self.root)
        count = self.checkScene()
        if count>1:
            print 'Exists multi faceCtrlGrp in scene...'
            text(l='Warning: Exists multi faceCtrlGrp in scene...')
        if count==1:
            self.currentRoot = self.getExists()[0]
            print 'Exists the faceCtrlGrp.'
            
            ui1 = self.currentUI(self.currentRoot)
            ui2 = self.currentModelUI()
            ui3 = self.buildTabs()
            formLayout(self.root,e=1,
                 af=[(ui1,'top',5),(ui1,'left',5),(ui1,'right',5),
                     (ui2,'left',5),(ui2,'right',5),
                     (ui3,'left',0),(ui3,'right',0),(ui3,'bottom',0)],
                 ac=[(ui2,'top',2,ui1),
                     (ui3,'top',2,ui2)])
        if count==0:
            print 'Create the faceCtrlGrp from library.'
            self.libraryUI()
        setParent('..')
    def buildTabs(self):
        
        tabs = tabLayout('mainTabs',innerMarginWidth=5, innerMarginHeight=5,scr=1,cr=1,mcw=300,hst=16,vst=16)
        if self.currentRoot==None:
            return tabs
        child2 = formLayout('jointTab',numberOfDivisions=100)
        c2 = jointCtrlUI()
        c2.rootLayout(child2)
        c2.build()
        c2.ModelUI(self.modelUI)
        setParent('..')
            
        child3 = formLayout('subTab',numberOfDivisions=100)
        c3 = subCtrlUI()
        c3.rootLayout(child3)
        c3.build()
        c3.ModelUI(self.modelUI)
        setParent('..')
            
        child4 = formLayout('goalTab',numberOfDivisions=100)
        c4 = goalCtrlUI()
        c4.rootLayout(child4)
        c4.build()
        c4.ModelUI(self.modelUI)
        setParent('..')
        #setParent('..')
        tabLayout( tabs, edit=True,
                   tabLabel=((child2, 'Joint'),
                             (child3, 'Sub'), 
                             (child4, 'Goal')))
        return tabs
    def checkScene(self):
        return len(self.getExists())
    def currentUI(self, currentRoot):
        ui = columnLayout('current',adj=1,rs=2)
        rowLayout(numberOfColumns=2,
                  cw=[1,60],
                  ct2=['right','left'])
        text(l='Current:')
        #self.current = text(l='')
        self.current = iconTextButton( style='textOnly',  label='' ,h=20,w=100,bgc=(0.9,1,0.9))
        self.updateCurrent(currentRoot)
        setParent('..')
        separator()
        setParent('..')
        return ui
    def currentModelUI(self):
        ui = columnLayout('currentModel',adj=1,rs=2)
        rowLayout(numberOfColumns=3,
                  cw=([1,60],[2,150],[3,80]),
                  ct3=['right','both','left'])
        text(l='Model:')
        self.modelUI = textField(en=0)
        button(l='Add Selected',c=self.addSelectedModel)
        setParent('..')
        separator()
        setParent('..')
        return ui
    def libraryUI(self, *args):
        ui = columnLayout('library',adj=1,rs=2)
        rowLayout(nc=2,
                  cw=[[1,60],[2,200]],
                  ct2=['right','both'])
        text(l='Library:')
        list = self.getLibList()
        self.libList = optionMenu();print self.libList
        for item in list:
            menuItem(l=item)
        setParent('..')
        rowLayout(nc=2,cal=[2,'center'],
                  cw=[[1,60],[2,200]],
                  ct2=['right','both'])
        text(l='')
        button(l='Load',
               en=len(list),
               c=self.loadLib)
        setParent('..')
        setParent('..')
        return ui
    def existsUI(self, *args): # No need...
        rowLayout(nc=2,cal=[2,'center'],
                  cw=[[1,60],[2,200]],
                  ct2=['right','both'])
        text(l='Exists:')
        button(l='Refresh', w=200, c=self.updateExistsList)
        setParent('..')
        
        rowLayout(nc=2,cal=[2,'center'],
                  cw=[[1,60],[2,200]],
                  ct2=['right','both'])
        text(l='')
        self.existsList = textScrollList(numberOfRows=5,
                                         allowMultiSelection=0,
                                         sc=self.selectExistsListItem)
        setParent('..')
        
        rowLayout(nc=2,cal=[2,'center'],
                  cw=[[1,60],[2,200]],
                  ct2=['right','both'])
        text(l='')
        self.loadExists = button(l='Set ', en=0, c=self.loadExi)
        self.updateExistsList()
        setParent('..')
    def getLibList(self, *args):
        obj = lib()
        obj.setPath(g.ROOT_CTRL_LIB_PATH)
        return obj.libList()
    def getExists(self, *args):
        list = []
        nodes = ls(g.ROOT_GRP)
        #print nodes
        for node in nodes:
            try:
                mark = getAttr((node+'.notes'))
            except:
                continue
            #print mark
            if mark==g.ROOT_MARK:
                list.append(node)
        return list
    def loadLib(self, *args):
        print self.libList
        item = optionMenu(self.libList,q=1,v=1)
        print 'Load Root Ctrl:',item
        obj = lib()
        obj.setPath(g.ROOT_CTRL_LIB_PATH)
        obj.setFile(item)
        obj.load()
        setToolTo( 'moveSuperContext' )
        self.build()
    def loadExi(self, *args): # No need...
        item = textScrollList(self.existsList,q=1,si=1)
        #print item
        if item != None:
            currentRoot = item[0]
            #print currentRoot
            self.updateCurrent(currentRoot)
    def updateExistsList(self, *args): # No need...
        list = self.getExists()
        textScrollList(self.existsList,e=1,ra=1)
        textScrollList(self.existsList,e=1,append=list)
        button(self.loadExists,e=1,en=len(list))
    def updateCurrent(self, current):
        cr = 'None...'
        cmd = "print ''"
        if current != '':
            #print 'Current Root:',current
            cr = current
            cmd = "select('"+current+"')"
        #print args
        iconTextButton(self.current, e=1, l=cr, c=lambda *args:self.selectCurrentRoot(current))
    def selectCurrentRoot(self, args):
        #print args
        select(args)
    def selectExistsListItem(self, *args): # No need...
        item = textScrollList(self.existsList,q=1,si=1)
        select(item)
    def addSelectedModel(self, *args):
        obj = ls(sl=1)
        if obj==[]:
            obj = ['']
        tv = xform(obj[0],q=1,ws=1,t=1)
        rv = xform(obj[0],q=1,ws=1,ro=1)
        sv = xform(obj[0],q=1,r=1,s=1)
        objShape = listRelatives(obj, s=1)[0]
        if nodeType(objShape) != 'mesh':
            raise RuntimeError, 'There is no polygon model assigned!'
        if  tv != [0,0,0] or rv != [0,0,0] or sv != [1,1,1]:
            raise RuntimeError, "Model's transform is not in originality!"
        textField(self.modelUI,e=1,text=obj[0])
class jointCtrlUI:
    import eyeCtrl
    import chinCtrl
    import tongueCtrl
    eyeobj = eyeCtrl.eyeCtrl()
    chinobj = chinCtrl.chinCtrl()
    tongueobj = tongueCtrl.tongueCtrl()

    def __init__(self):
        pass
    def ModelUI(self, ui):
        self.modelUI = ui
    def rootLayout(self, ui):
        self.root = ui
    def build(self):
        setParent(self.root)
        b1 = button(l='Mirror +',c=self.mirrorLeft)
        b2 = button(l='Mirror -',c=self.mirrorRight)
        s1 = separator()
        self.eyeCheckBox = checkBox(l='Eys',align='left',onc=self.eyeOn,ofc=self.eyeOff)
        self.chinCheckBox = checkBox(l='Chin',align='left',onc=self.chinOn,ofc=self.chinOff)
        self.tongueCheckBox = checkBox(l='Tongue',align='left',onc=self.tongueOn,ofc=self.tongueOff)
        s2 = separator()
        b3 = button(l='Paint Skin Weight Tool',c=self.weightTool,vis=0)
        formLayout(self.root,e=1,
                   af=[(b1,'top',5),(b2,'top',5),
                       (s1,'left',5),(s1,'right',5),
                       (s2,'left',5),(s2,'right',5),
                       (b3,'left',60),(b3,'right',60)],
                   ac=[(s1,'top',5,b1),(s2,'top',5,self.eyeCheckBox),
                       (self.eyeCheckBox,'top',5,s1),(self.chinCheckBox,'top',5,s1),(self.tongueCheckBox,'top',5,s1),
                       (b3,'top',5,s2)],
                   ap=[(self.eyeCheckBox,'left',0,20),(self.chinCheckBox,'left',0,40),(self.tongueCheckBox,'left',0,60),
                       (b1,'left',0,25),(b1,'right',0,48),
                       (b2,'left',0,52),(b2,'right',0,75)])
        self.initCheckBox()

    def initCheckBox(self):
        checkBox(self.eyeCheckBox, e=1, v=self.eyeobj.checkState())
        checkBox(self.chinCheckBox, e=1, v=self.chinobj.checkState())
        checkBox(self.tongueCheckBox, e=1, v=self.tongueobj.checkState())
    # button comands #
    def mirrorLeft(self, *args):
        self.doMirror(1)
    def mirrorRight(self, *args):
        self.doMirror(-1)
    def eyeOn(self, *args):
        self.eyeobj.createAll()
    def eyeOff(self, *args):
        self.eyeobj.locBack()
    def chinOn(self, *args):
        self.chinobj.createAll()
    def chinOff(self, *args):
        self.chinobj.locBack()
    def tongueOn(self, *args):
        self.tongueobj.createAll()
    def tongueOff(self, *args):
        self.tongueobj.locBack()
    # execute comands #
    def doMirror(self, arg=1):
        self.eyeobj.mirror(arg)
        self.chinobj.mirror(arg)
        self.tongueobj.mirror(arg)
    def weightTool(self, *args):
        model = textField(self.modelUI,q=1,text=1)
        select(model)
        cmd = 'AS_Skinny()'
        mm.eval(cmd)
class eyeCtrlUI:    # No need ...
    grp = g.EYE_LOC_GRP
    
    def getCtrlObj(self):
        import eyeCtrl
        self.ctrlObj = eyeCtrl.eyeCtrl()
    def __init__(self):
        self.getCtrlObj()
        self.build()
    def build(self):
        columnLayout(adj=1,rs=2)
        self.listUI()
        separator()
        self.updateSetting()
        separator()
        #self.loadModelUI()
        setParent('..')
    def listUI(self, *args):
        self.locList = textScrollList(numberOfRows=6,
                                      allowMultiSelection=True,
                                      sc=self.selectLoc)
        list = self.getLocList()
        textScrollList(self.locList,e=1,append=list)
    def selectLoc(self, *args):
        items = textScrollList(self.locList,q=1,si=1)
        select(cl=1)
        for item in items:
            if objExists(item):
                select(item,add=1)
            else:
                print 'No exists obj:',item
    def updateSetting(self, *args):
        button(l='Mirror',c=self.doMirror)
        button(l='Build',c=self.createAll)
    def loadModelUI(self, *args):
        text(l='Building Load Model')
    def getColGrpList(self, *args):
        output = []
        if objExists(self.grp):
            output = listRelatives(self.grp,c=1)
            if output==None:
                output = []
        return output
    def getLocList(self, *args):
        list = []
        grps = self.getColGrpList()
        for item in grps:
            loc = listRelatives(item, c=1)
            if loc!=None:
                list.extend(loc)
        return list
    def getArgs(self):
        list = []
        grps = self.getColGrpList()
        for item in grps:
            loc = listRelatives(item, c=1)
            if loc!=None:
                list.append(loc)
        return list
    def createAll(self, *args):
        list = self.getArgs()
        self.ctrlObj.createAll(list)
    def doMirror(self, *args):
        listSel = ls(sl = True)
        for obj in listSel:
            posObj = xform(obj, q = True, ws = True, t = True)
            if '_L_' in obj:
                xform(obj.replace('_L_','_R_'), ws = True, t = (posObj[0] * -1, posObj[1], posObj[2]))
            elif '_R_' in obj:
                xform(obj.replace('_R_','_L_'), ws = True, t = (posObj[0] * -1, posObj[1], posObj[2]))
            else:
                xform(obj, ws = True, t = (0, posObj[1], posObj[2]))
class chinCtrlUI(eyeCtrlUI):    # No need ...
    grp = g.CHIN_LOC_GRP
    def getCtrlObj(self):
        import chinCtrl
        self.ctrlObj = chinCtrl.chinCtrl()
class tongueCtrlUI(eyeCtrlUI):    # No need ...
    grp = g.TONGUE_LOC_GRP
    def getCtrlObj(self):
        import tongueCtrl
        self.ctrlObj = tongueCtrl.tongueCtrl()

class subCtrlUI:
    import subCtrl as sc
    obj = sc.subCtrl()
    
    def __init__(self):
        pass
    def rootLayout(self, ui):
        self.root = ui
    def ModelUI(self, ui):
        self.modelUI = ui
    def build(self):
        list = self.getCtrlLibList()    #
        
        setParent(self.root)
        # lib
        l11 = text(l='Library:')
        self.libList = optionMenu()
        for item in list:
            menuItem(l=item)
        l13 = button(l='Load',w=50,
               en=len(list),
               c=self.loadLib)  #
        s1 = separator()
        # loc add & remove
        l20 = text(l='Locator:')
        l21 = button(l='Add',w=80,c=self.createLoc)    #
        l22 = button(l='Remove',w=80,c=self.removeLoc)
        # mirror
        l31 = button(l='Mirror +',w=80, c=self.mirrorLeft)
        l32 = button(l='Mirror -',w=80, c=self.mirrorRight)
        l33 = button(l='Snap to Geometry',w=170,c=self.snapToGeo)
        s3 = separator()
        # ctrl create & reset
        l40 = text(l='Controller:')
        l41 = button(l='Build',w=80, c=self.buildSubCtrl)
        l42 = button(l='Reset',w=80, c=self.resetSubCtrl)
        s4 = separator()
        self.weight = floatSliderButtonGrp( label='Weight:',
                                    field=True,
                                    buttonLabel='Setup',
                                    columnWidth=[(1,60),(2,30)],
                                    min=0,max=10,v=0.4,step=0.1,
                                    bc=self.setWeight)
        l52 = button(l='Paint Skin Weight Tool',c=self.weightTool,vis=0)
        
        formLayout(self.root,e=1,
                   af=[(l11,'top',5),
                       (self.libList,'left',80),(self.libList,'top',5),
                       (l13,'top',5),
                       (s1,'left',5),(s1,'right',5),
                       (l21,'left',80),
                       (l31,'left',80),
                       (l33,'left',80),
                       (s3,'left',5),(s3,'right',5),
                       (l41,'left',80),
                       (s4,'left',5),(s4,'right',5),
                       (self.weight,'left',5),
                       (l52,'left',60),(l52,'right',60)],
                   ac=[(l11,'right',2,self.libList),
                       (l13,'left',2,self.libList),
                       (s1,'top',5,self.libList),
                       (l20,'top',5,s1),(l20,'right',2,l21),
                       (l21,'top',5,s1),
                       (l22,'top',5,s1),(l22,'left',10,l21),
                       (l31,'top',5,l21),
                       (l32,'top',5,l21),(l32,'left',10,l31),
                       (l33,'top',5,l32),
                       (s3,'top',5,l33),
                       (l40,'top',5,s3),(l40,'right',2,l41),
                       (l41,'top',5,s3),
                       (l42,'top',5,s3),(l42,'left',10,l41),
                       (s4,'top',5,l41),
                       (self.weight,'top',5,s4),
                       (l52,'top',5,self.weight)])

    def getCtrlLibList(self, *args):
        obj = lib()
        obj.setPath(g.SUB_CTRL_LIB_PATH)
        return obj.libList()
    def loadLib(self, *args):
        item = optionMenu(self.libList,q=1,v=1)
        print 'load Sub Ctrl:',item
        obj = lib()
        obj.setPath(g.SUB_CTRL_LIB_PATH)
        obj.setFile(item)
        obj.setGroup(g.SUB_LOC_GRP)
        obj.load()
        obj.moveToGroup()
    def createLoc(self, *args):
        self.obj.addLoc()
    def removeLoc(self, *args):
        self.obj.removeLoc()
    def mirrorLeft(self, *args):
        self.obj.mirror(1)
    def mirrorRight(self, *args):
        self.obj.mirror(-1)
    def snapToGeo(self, *args):
        model = textField(self.modelUI,q=1,text=1)
        locList = self.obj.locList()
        self.obj.snapToGeo(model, locList)
    def buildSubCtrl(self, *args):
        model = textField(self.modelUI,q=1,text=1)
        locList = self.obj.locList()
        self.obj.buildSubCtrl(model, locList)
    def resetSubCtrl(self, *args):
        self.obj.subLocReset()
    def selectCtrl(self, *args):    # No need ...
        item = textScrollList(self.subCtrlList,q=1,si=1)
        try:
            select(item)
        except:
            print 'No exists object:'
            print item
    def weightTool(self, *args):
        model = textField(self.modelUI,q=1,text=1)
        select(model)
        cmd = 'AS_Skinny()'
        mm.eval(cmd)
    def setWeight(self, *args):
        model = textField(self.modelUI,q=1,text=1)
        value = floatSliderButtonGrp(self.weight,q=1,v=1)
        self.obj.setWeight(model,value)
    def updateLocList(self):    # No need ...
        list = self.obj.locList()
        textScrollList(self.subCtrlList,e=1,ra=1)
        textScrollList(self.subCtrlList,e=1,append=list)
class goalCtrlUI:
    import goalCtrl as gc
    reload(gc)
    obj = gc.goalCtrl()
    
    def __init__(self):
        pass
    def rootLayout(self, ui):
        self.root = ui
    def ModelUI(self, ui):
        self.modelUI = ui
    def build(self):
        list = self.getCtrlLibList()
        
        setParent(self.root)
        
        lib1 = text(l='Library:')
        self.libList = optionMenu()
        for item in list:
            menuItem(l=item)
        lib3 = button(l='Load',w=50,
                      en=len(list),
                      c=self.loadLib)
        s1 = separator()
        newlib = button(l='Create New Controller',
                        c=self.showGoalCtrlLibUI)
        s2 = separator()
        s3 = separator()
        list1 = self.listUI()
        s4 = separator()
        self.attrsListUI = columnLayout(adj=1,rs=2)
        self.updateAttrsList()
        
        formLayout(self.root,e=1,
                   af=[(lib1,'top',5),
                       (self.libList,'top',5),(self.libList,'left',80),
                       (lib3,'top',5),
                       (s1,'left',5),(s1,'right',5),
                       (newlib,'left',60),(newlib,'right',60),
                       (s2,'left',5),(s2,'right',5),
                       (s3,'left',5),(s3,'right',5),
                       (list1,'left',0),
                       (s4,'left',5),(s4,'right',5),
                       (self.attrsListUI,'left',0),(self.attrsListUI,'right',0),(self.attrsListUI,'bottom',0)],
                   ac=[(lib1,'right',2,self.libList),
                       (lib3,'left',2,self.libList),
                       (s1,'top',5,self.libList),
                       (newlib,'top',5,s1),
                       (s2,'top',5,newlib),
                       (s3,'top',2,s2),
                       (list1,'top',5,s3),
                       (s4,'top',5,list1),
                       (self.attrsListUI,'top',5,s4)])
        
    def listUI(self, *args):
        zone = formLayout(numberOfDivisions=100)
        t1 = text(l='Controller List:')
        self.goalCtrlList = textScrollList(numberOfRows=6,w=160,
                                           allowMultiSelection = 0,
                                           sc=self.updateAttrsList)
        b1 = button(h=20,w=20, l='<', ann='Reload selected to list.', c=self.reloadToList)
        b2 = button(h=20,w=20, l='+', ann='Add selected to list.', c=self.addToList)
        b3 = button(h=20,w=20, l='-', ann='Remove selected Items.', c=self.delFromList)
        setParent('..')
        formLayout(zone,e=1,
                   af=[(t1,'top',0),
                       (self.goalCtrlList,'top',0),(self.goalCtrlList,'left',80),
                       (b1,'top',0)],
                   ac=[(t1,'right',2,self.goalCtrlList),
                       (b1,'left',2,self.goalCtrlList),
                       (b2,'top',2,b1),(b2,'left',2,self.goalCtrlList),
                       (b3,'top',2,b2),(b3,'left',2,self.goalCtrlList)])
        return zone
    def updateAttrsList(self, *args):
        self.cleanup(self.attrsListUI)
        setParent(self.attrsListUI)
        ctrl = textScrollList(self.goalCtrlList,q=1,si=1)
        if ctrl==None:
            return
        ctrl = ctrl[0]
        select(ctrl)
        
        rowLayout(nc=2,cal=[2,'center'],
                  cw=[[1,60],[2,200]],
                  ct2=['right','both'])
        text(l='Atts:')
        attrs = self.getAttrs(ctrl)
        rowLayout(nc=5,cw5=(30,30,30,30,30))
        self.attsUI = iconTextRadioCollection()
        for attr in attrs:
            iconTextRadioButton((ctrl+'___'+attr),w=20,h=20, st='textOnly',bgc=(0.9,1,0.9),
                                l=attr,onc=self.updateSetting)
        setParent('..')
        setParent('..')
        separator()
        self.settingUI = formLayout(numberOfDivisions=100)
    def updateSetting(self, *args):
        args = self.__getArgs__()
        ctrl = args[0]
        attr = args[1]
        self.cleanup(self.settingUI)
            
        setParent(self.settingUI)
        l = attrFieldSliderGrp(cw=[[1,60],[2,40]],pre=2,
                               at='%s.%s'%(ctrl,attr),
                               l=attr,
                               min=-1,max=1,s=0.01)
        b1 = button(w=100,l='Zero all sub ctrls',c=self.zeroAllSubCtrls)
        b2 = button(w=100,l='Sub Pose Lib',c=self.showGoalLibUI)
        b3 = button(w=100,l='Save Sub Pose',c=self.saveGoalLib)
        b4 = button(w=100,l='+',c=self.createNewGoal)
        
        self.goalListLayout = columnLayout(adj=1)
        self.updateGoalList()
        formLayout(self.settingUI,e=1,
                   af=[(l,'top',5),(l,'left',0),
                       (self.goalListLayout,'left',20),
                       (b1,'left',180),
                       (b2,'left',180),
                       (b3,'left',180),
                       (b4,'left',180),(b4,'bottom',0)],
                   ac=[(self.goalListLayout,'top',5,l),
                       (b1,'top',5,l),
                       (b2,'top',5,b1),
                       (b3,'top',2,b2),
                       (b4,'top',5,b3),
                       (self.goalListLayout,'right',2,b1)])
    def updateGoalList(self):
        self.cleanup(self.goalListLayout)
        setParent(self.goalListLayout)
        args = self.__getArgs__()
        ctrl = args[0]
        attr = args[1]
        list = self.getGoalList(ctrl,attr)
        self.currentGoalListUI = textScrollList(numberOfRows=8,
                                                allowMultiSelection=0,
                                                append=list,
                                                sc=self.editGoal,
                                                dkc=self.removeGoal)
    def cleanup(self,root):
        chdn = layout(root, q=1, ca=1)
        if not chdn==None:
            for chd in chdn:
                deleteUI(chd)
    def loadLib(self, *args):
        item = optionMenu(self.libList,q=1,v=1)
        print 'load Goal Ctrl:',item
        obj = lib()
        obj.setPath(g.GOAL_CTRL_LIB_PATH)
        obj.setFile(item)
        obj.setGroup(g.GOAL_CTRL_GRP)
        obj.load()
        obj.moveToGroup()
    def getCtrlLibList(self, *args):
        obj = lib()
        obj.setPath(g.GOAL_CTRL_LIB_PATH)
        return obj.libList()
    def addToList(self, *args):
        sel = ls(sl=1)
        items = textScrollList(self.goalCtrlList,q=1,ai=1)
        if items == None:
            textScrollList(self.goalCtrlList,e=1,a=sel)
        else:
            for item in sel:
                if item not in items:
                    textScrollList(self.goalCtrlList,e=1,a=item)
        self.updateAttrsList()
    def delFromList(self, *args):
        item = textScrollList(self.goalCtrlList,q=1,si=1)
        if item!=None:
            textScrollList(self.goalCtrlList,e=1,ri=item)
            self.updateAttrsList()
    def reloadToList(self, *args):
        textScrollList(self.goalCtrlList,e=1,ra=1)
        self.delFromList()
        self.addToList()
    def __getArgs__(self):
        args = iconTextRadioCollection(self.attsUI,q=1,sl=1).split('___')
        ctrl,attr = args
        value = getAttr('%s.%s'%(ctrl,attr))
        value = round(value*100)/100
        model = textField(self.modelUI,q=1,text=1)
        return (ctrl,attr,value,model)
    def createNewGoal(self, *args):
        args = self.__getArgs__()
        drvObj = args[0]
        attr = args[1]
        drvValue = args[2]
        skinGeo = args[3]
        #baseBSObj = self.obj.findBSGeo(args[3])
        self.obj.createBS(drvObj, attr, drvValue, skinGeo)
        
        import subCtrl as sc
        subObj = sc.subCtrl()
        subObj.zeroSubCtrls()
        
        self.updateGoalList()
    def zeroAllSubCtrls(self, *args):
        import subCtrl as sc
        subObj = sc.subCtrl()
        subObj.zeroSubCtrls()
    def saveGoalLib(self, *args):
        args = self.__getArgs__()
        ctrl = args[0]
        attr = args[1]
        value = args[2]
        import subPoseLib as spl
        obj = spl.subPoseLib()
        obj.writeTxt(ctrl,attr,value)
        self.showGoalLibUI()
    def editGoal(self, *args):
        args = self.__getArgs__()
        ctrl = args[0]
        attr = args[1]
        #value = args[2]
        value = float(textScrollList(self.currentGoalListUI,q=1,si=1)[0])
        setAttr('%s.%s'%(ctrl,attr),value)
        self.obj.hideAllGoal()
        node = self.obj.getBlendShapeInfo(ctrl,attr,value)[4]
        if node == '':
            node = self.obj.backToBS(ctrl,attr,value)
        self.obj.showGoal(node)
    def removeGoal(self, *args):
        print 'remove goal'
        args = self.__getArgs__()
        ctrl = args[0]
        attr = args[1]
        #value = args[2]
        value = float(textScrollList(self.currentGoalListUI,q=1,si=1)[0])
        self.obj.removeBS(ctrl,attr,value)
        self.updateGoalList()
    def getAttrs(self, obj):
        attrs = listAttr(obj,k=1,u=1,v=1,s=1,sn=1)
        if attrs==None:
            attrs = []
        return attrs
    def getLimitInfo(self, attr):
        pass
    def getGoalList(self, ctrl, attr):
        list = self.obj.getGoalList(ctrl,attr)
        keys = list.keys()
        try:
            keys.remove('0.0')
        except:
            pass
        keys.sort()
        keys.reverse()
        return keys
    def showGoalCtrlLibUI(self, *args):
        ins = goalCtrlLibUI()
        ins.build()
        ins.show()
    def showGoalLibUI(self, *args):
        args = self.__getArgs__()
        ctrl = args[0]
        attr = args[1]
        ins = subPoseLibUI()
        ins.getArgs(ctrl,attr)
        ins.build()
        ins.show()
class goalCtrlLibUI:
    win = 'goalCtrlLibUI'
    win_width = 169
    win_height = 300
    
    def __init__(self):
        #self.build()
        pass
        
    def build(self):
        if window(self.win, exists=1):
            print 'Exists window:',self.win
            return
        window(self.win, title='Goal Controller Library')
        columnLayout(adj=1)
        self.inputName = textFieldGrp(l='Name:',cw2=[60,100])
        separator()
        gridLayout(nc=2,cellWidthHeight=(80,80))
        iconTextButton(style='iconOnly', image1=(g.ICONS_PATH+'/ctrlA.bmp'),c=self.ctrlA)
        iconTextButton(style='iconOnly', image1=(g.ICONS_PATH+'/ctrlB.bmp'),c=self.ctrlB)
        iconTextButton(style='iconOnly', image1=(g.ICONS_PATH+'/ctrlC.bmp'),c=self.ctrlC)
        iconTextButton(style='iconOnly', image1=(g.ICONS_PATH+'/ctrlD.bmp'),c=self.ctrlD)
        iconTextButton(style='iconOnly', image1=(g.ICONS_PATH+'/ctrlE.bmp'),c=self.ctrlE)
        iconTextButton(style='iconOnly', image1=(g.ICONS_PATH+'/ctrlF.bmp'),c=self.ctrlF)
        #print 'Last size:',window(self.win,q=1,wh=1)
        window(self.win,e=1,wh=[self.win_width,self.win_height])
        
    def show(self):
        showWindow(self.win)
    def getArgs(self):
        return textFieldGrp(self.inputName,q=1,text=1)
    import goalCtrl as gc
    obj = gc.goalCtrl()
    def ctrlA(self, *args):
        self.obj.ctrlA(self.getArgs())
    def ctrlB(self, *args):
        self.obj.ctrlB(self.getArgs())
    def ctrlC(self, *args):
        self.obj.ctrlC(self.getArgs())
    def ctrlD(self, *args):
        self.obj.ctrlD(self.getArgs())
    def ctrlE(self, *args):
        self.obj.ctrlE(self.getArgs())
    def ctrlF(self, *args):
        self.obj.ctrlF(self.getArgs())
class subPoseLibUI:
    win = 'subPoseLibUI'
    win_width = 169
    win_height = 275
    import subPoseLib as spl
    obj = spl.subPoseLib()
    def __init__(self):
        pass
    def getArgs(self, ctrl, attr):
        self.ctrl = ctrl
        self.attr = attr
    def build(self):
        if window(self.win, exists=1):
            print 'Exists window:',self.win
            deleteUI(self.win)
        list = self.obj.getFileList(self.ctrl, self.attr)
        list = [item.split('.sf')[0] for item in list]
        
        window(self.win, title='Sub Pose Library')
        paneLayout()
        self.poseUI = textScrollList(allowMultiSelection=0,append=list,sc=self.loadPose)
        #print 'Last size:',window(self.win,q=1,wh=1)
        window(self.win,e=1,wh=[self.win_width,self.win_height])
        
    def show(self):
        showWindow(self.win)
    def loadPose(self, *args):
        filename = textScrollList(self.poseUI,q=1,si=1)[0] + '.sf'
        print 'load pose'
        print self.ctrl
        print filename
        self.obj.readTxt(self.ctrl,filename)
