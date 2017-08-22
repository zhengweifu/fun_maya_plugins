from maya.cmds import *

class checkingBoxCmd:
    label = 'checking'
    def cmd(self):
        pass
    def showInfo(self):
        self.clearInfo()
        setParent(self.infoUI)
        # Contents
        if self.cont!='':
            text(al='left',l=self.cont)
        
    cont = ''
    colors = [(0.85,0.85,0.85),(0.8,0.8,0.8)]
    resultColors = {-1:[.847,.847,.847],
                    0:[1,0.5,0.5],
                    .5:[1,1,0.5],
                    1:[0.5,1,0.5]}
    colorId = 0
    ui = None
    def __init__(self,active=1):
        if active:
            self.infoUI = checkingBoxCmd.ui
            self.createButton()
    def clearInfo(self):
        chdn = layout(self.infoUI, q=1, ca=1)
        if not chdn==None:
            for chd in chdn:
                deleteUI(chd)
    def setUI(self,ui):
        checkingBoxCmd.ui = ui
    def createButton(self):
        checkingBoxCmd.colorId = 1 - checkingBoxCmd.colorId
        col = self.colors[checkingBoxCmd.colorId]
        self.button = iconTextButton(style='iconAndTextCentered', al='left',
                                     bgc=col, h = 24, fn='plainLabelFont',
                                     label=self.label, c=self.do )
    def setButtonColor(self,state=-1):
        if state==-1:
            return
        '''
        col = [1,0.5,0.5]
        if state==.5:
            col = [1,1,0.5]
        elif state==1:
            col = [0.5,1,0.5]
        '''
        iconTextButton(self.button, e=1, bgc=self.resultColors[state] )
    def do(self, *args):
        self.cont = ''
        r = self.cmd()
        self.setButtonColor(r)
        self.showInfo()
'''
class checking1(checkingBoxCmd):
    label = 'checking1'
    def cmd(self):
        print 'checking1'
        self.cont = u'finish'
        return 1
    def showInfo(self):
        cbb.checkingBoxCmd.showInfo(self)
        text(al='left',l='other info')
'''
class checkingBoxUI:
    title = None
    win = None
    win_width = 350
    win_height = 500

    helpUI = 'checkingBoxHelp'
    cmds = None
    root = None
    def __init__(self,name):
        self.win = name
    def setInfoUI(self):
        cbc = checkingBoxCmd(0)
        cbc.setUI(self.info)

    def build(self):		# ( No need to change )
        if window(self.win, exists=1):
            #self.update()
            return
        window(self.win, title = self.title, wh=(320,240))
        formLayout('MAINFORM',nd=100)
        r = button(h=32,l='Restart',c=self.update)
        c = button(h=32,l='Close',c=self.close)
        h = button(h=32,l='Help',c=self.help)
        p = paneLayout( configuration='horizontal2' ,ps=(1,100,70) )
        self.listScr = scrollLayout(vst=1,hst=0,cr=1)
        self.list = columnLayout(adj=1)
        setParent(p)
        scrollLayout(vst=1,hst=0,cr=1)
        self.info = columnLayout(adj=1)
        self.setInfoUI()
        self.updateList()   # after setInfoUI
        self.updateListBGC()
        formLayout('MAINFORM',e=1,
                   af=[(r,'bottom',5),(r,'left',5),(h,'right',5),
                       (c,'bottom',5),(h,'bottom',5),
                       (p,'left',2),(p,'right',2),(p,'top',2)],
                   ac=[(p,'bottom',5,r),(c,'left',3,r),(c,'right',3,h)],
                   ap=[(r,'right',0,30),(h,'left',0,70)]
                   )
        #print window(self.win,q=1,wh=1)
        window(self.win,e=1,wh=[self.win_width,self.win_height])		# Set the size of the window
    def help(self,*args):
        if window(self.helpUI,ex=1):
            deleteUI(self.helpUI)
        window(self.helpUI,title='Checking Box - Help')
        f = formLayout(nd=100)
        b = button(l='Close',c=self.closeHelp)
        s = scrollLayout(vst=1,hst=0,cr=1)
        columnLayout(adj=1,rs=3,cat=('left',3))
        text(al='left',l=u'执行各项检查命令后，命令颜色会改变。')
        text(al='left',l=u'颜色示意如下：')
        colors = checkingBoxCmd(0).resultColors
        rowLayout(numberOfColumns=2,cw=(1,50))
        text(l='            ',bgc=colors[-1])
        text(l=u'未检查')
        setParent('..')
        rowLayout(numberOfColumns=2,cw=(1,50))
        text(l='            ',bgc=colors[0])
        text(l=u'存在错误')
        setParent('..')
        rowLayout(numberOfColumns=2,cw=(1,50))
        text(l='            ',bgc=colors[.5])
        text(l=u'需人工检查')
        setParent('..')
        rowLayout(numberOfColumns=2,cw=(1,50))
        text(l='            ',bgc=colors[1])
        text(l=u'检查通过')
        formLayout(f,e=1,
                   af = [(s,'top',2),(s,'left',2),(s,'right',2),
                       (b,'bottom',2),(b,'left',2),(b,'right',2)],
                   ac = [(s,'bottom',5,b)])
        window(self.helpUI,e=1,wh=(320,240))
        showWindow(self.helpUI)
    def closeHelp(self,*args):
        deleteUI(self.helpUI)
    def show(self):		# ( No need to change )
        if window(self.win, exists=1):
            showWindow(self.win)
    def close(self,*args):		# ( No need to change )
        if window(self.win, exists=1):
            deleteUI(self.win)
    def cleanup(self,root):		# ( No need to change )
        chdn = layout(root, q=1, ca=1)
        if not chdn==None:
            for chd in chdn:
                deleteUI(chd)#, layout=1
    def update(self,*args):
        self.updateList()
        self.cleanup(self.info)
    def updateListBGC(self,*args):
        chdn = layout(self.list, q=1, ca=1)
        colors = checkingBoxCmd(0).colors
        scrollLayout(self.listScr,e=1,bgc=colors[1-len(chdn)%2])
    def updateList(self,*args):
        self.cleanup(self.list)
        setParent(self.list)
        checkingBoxCmd.colorId = 0
        # build layouts
        '''
        checking1()
        checking1()
        checking1()
        checking1()
        '''


'''
cb = checkingBoxUI('checkingBox')
#cb.close()
cb.build()
cb.show()
'''