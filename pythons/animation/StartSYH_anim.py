import sys
import shiboken
from PySide import QtCore, QtGui
import maya.OpenMayaUI

# Make SYH_anim_panel_fin by: pyuic4 SYH_animPanel.ui>SYH_anim_panel_fin.py
import SYH_anim_panel_fin 
# reload only for tests
reload(SYH_anim_panel_fin)

import maya.cmds as cmds
import maya.mel as mel

#import scripts.animation.SYH_animPanel
## reload only for tests 
#reload(scripts.animation.SYH_animPanel)

class StartSYH_animPanel(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(StartSYH_animPanel, self).__init__(parent)
        self.ui = SYH_anim_panel_fin.Ui_Form()
        self.ui.setupUi(self)
        self.SHIFT_PRESSED = ' -r '
        #
        self.getChar()
        
    def getChar(self):
        topTran = cmds.ls(assemblies = True)
        listItem1 = []
        chars = []
        for top in topTran:
            if("CharNode" in top):
                chars.append( top )
                #cmds.menself.uitem(p = self.ui + "|widget|comboBox", label = top)
#        for char in chars :
#            listItem1.append(QtGui.QListWidgetItem(char))

        for i in range(len(chars)):
            self.ui.comboBox.insertItem(i+1,chars[i])
                
#    def changeVis(self):
#        cmds.control(self.ui + "|tabWidget", edit=True, visible=True)
            
    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if (event.modifiers() & QtCore.Qt.ShiftModifier):
                #here accept the event and do something
                event.accept()
                self.SHIFT_PRESSED = ' -tgl '
         
    def keyReleaseEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if QtCore.Qt.ShiftModifier :
                if event.key() != QtCore.Qt.Key_Tab :
                    event.accept()
                    self.SHIFT_PRESSED = ' -r '

#    def mousePressEvent(self,event):
#        self.mousePressEvent(self,event)
#        self.ui.tabWidget.setFocus()
#        
    def getCurrentChar(self):
        returnName = ""
        #name = cmds.optionMenu(self.ui + "|widget|comboBox", q = True, v = True)
        name = str( self.ui.comboBox.currentText() )
        if(name != ""):
            temp = name.split("_")
            returnName = temp[0]
        return returnName
    
    def selAllRFiger(self):
        if self.SHIFT_PRESSED == ' -r ' :
            cmds.select(self.getCurrentChar() + "_R_000_Pinky_002_Ctrl", r = True)
        else :
            cmds.select(self.getCurrentChar() + "_R_000_Pinky_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Pinky_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Pinky_000_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Middle_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Middle_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Middle_000_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Index_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Index_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Index_000_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Thumb_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Thumb_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_R_000_Thumb_000_Ctrl", tgl = True)
        
    def selAllLFiger(self):
        if self.SHIFT_PRESSED == ' -r ' :
            cmds.select(self.getCurrentChar() + "_L_000_Pinky_002_Ctrl", r = True)
        else :
            cmds.select(self.getCurrentChar() + "_L_000_Pinky_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Pinky_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Pinky_000_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Middle_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Middle_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Middle_000_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Index_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Index_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Index_000_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Thumb_002_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Thumb_001_Ctrl", tgl = True)
        cmds.select(self.getCurrentChar() + "_L_000_Thumb_000_Ctrl", tgl = True)
        
    def selAll(self):
        temp = cmds.ls(dep = True)
        for t in temp:
            if("ATD" in t and "Ctrl" in t and not "Shape" in t and not "biaoqing" in t):
                cmds.select(t, add = True)
    
    def on_ATD_head_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_C_000_Head_000_Ctrl"
        mel.eval( cmd )

    def on_ATD_spline_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_000_C_Spine_002_Ctrl"
        mel.eval( cmd )
        
    def on_ATD_root_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_000_C_Root_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_bigcircle01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_Global_All_Walk_Unique_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_bigcircle02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_Global_All_Bottom_Unique_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_flyctrl_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_Global_All_Fly_Unique_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_selectall_pressed(self):
        self.ui.tabWidget.setFocus()
        self.selAll()


    def on_ATD_R_shoulder_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Scapuler_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_arm_sec01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_MidArmBend_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_arm_sec02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_MidElbowBend_000_Ctrl"
        mel.eval( cmd )        

    def on_ATD_R_arm_pole_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_000_R_ArmPole_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_twist_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Wrist_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_fkik_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_000_R_ArmIKFKSwitch_000_Ctrl"
        mel.eval( cmd )        

    def on_ATD_R_fb_01_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Thumb_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_fb_02_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Thumb_001_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_fb_03_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Thumb_002_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_ff_01_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Index_000_Ctrl"
        mel.eval( cmd )        
                            
    def on_ATD_R_ff_02_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Index_001_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_ff_03_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Index_002_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_fm_01_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Middle_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_fm_02_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Middle_001_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_R_fm_03_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Middle_002_Ctrl"
        mel.eval( cmd )        
                                                                             
    def on_ATD_R_fr_01_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Pinky_000_Ctrl"
        mel.eval( cmd )        
                                                                                         
    def on_ATD_R_fr_02_pressed(self):
        self.ui.tabWidget.setFocus()        
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Pinky_001_Ctrl"
        mel.eval( cmd )        
                                                                                         
    def on_ATD_R_fr_03_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Pinky_002_Ctrl"
        mel.eval( cmd )        
                                                                                           
    def on_ATD_R_figer_sec_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Finger_Unique_Ctrl"
        mel.eval( cmd )        
              
    def on_ATD_R_leg_sec_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_MidLegBend_000_Ctrl"
        mel.eval( cmd )        
                                                                                           
    def on_ATD_R_leg_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_R_000_Foot_000_Ctrl"
        mel.eval( cmd )        

    def on_ATD_L_shoulder_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Scapuler_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_arm_sec01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_MidArmBend_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_arm_sec02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_MidElbowBend_000_Ctrl"
        mel.eval( cmd )        

    def on_ATD_L_arm_pole_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_000_L_ArmPole_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_twist_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Wrist_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_fkik_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_000_L_ArmIKFKSwitch_000_Ctrl"
        mel.eval( cmd )        
                
    def on_ATD_L_fb_01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Thumb_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_fb_02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Thumb_001_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_fb_03_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Thumb_002_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_ff_01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Index_000_Ctrl"
        mel.eval( cmd )        
                            
    def on_ATD_L_ff_02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Index_001_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_ff_03_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Index_002_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_fm_01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Middle_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_fm_02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Middle_001_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_fm_03_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Middle_002_Ctrl"
        mel.eval( cmd )        
                                                                             
    def on_ATD_L_fr_01_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Pinky_000_Ctrl"
        mel.eval( cmd )        
                                                                                         
    def on_ATD_L_fr_02_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Pinky_001_Ctrl"
        mel.eval( cmd )         
                                                                                         
    def on_ATD_L_fr_03_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Pinky_002_Ctrl"
        mel.eval( cmd )        
                                                                                           
    def on_ATD_L_figer_sec_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Finger_Unique_Ctrl"
        mel.eval( cmd )        
              
    def on_ATD_L_leg_sec_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_MidLegBend_000_Ctrl"
        mel.eval( cmd )        
                                                                                           
    def on_ATD_L_leg_pressed(self):
        self.ui.tabWidget.setFocus()
        cmd = 'select' +  self.SHIFT_PRESSED + self.getCurrentChar() + "_L_000_Foot_000_Ctrl"
        mel.eval( cmd )        
        
    def on_ATD_L_allfiger_pressed(self):
        self.ui.tabWidget.setFocus()
        self.selAllLFiger()
        
    def on_ATD_R_allfiger_pressed(self):
        self.ui.tabWidget.setFocus()
        self.selAllRFiger()

#    def connBut(self):
    
#        cmds.button(self.ui + "|tabWidget|tab|ATD_head", e = True, c = "cmds.select(getCurrentChar() + \"_C_000_Head_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_spline", e = True, c = "cmds.select(getCurrentChar() + \"_000_C_Spine_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_root", e = True, c = "cmds.select(getCurrentChar() + \"_000_C_Root_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_bigcircle01", e = True, c = "cmds.select(getCurrentChar() + \"_Global_All_Walk_Unique_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_bigcircle02", e = True, c = "cmds.select(getCurrentChar() + \"_Global_All_Bottom_Unique_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_flyctrl", e = True, c = "cmds.select(getCurrentChar() + \"_Global_All_Fly_Unique_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_selectall", e = True, c = "selAll()")
        
        #################################################################### right ##################################################################
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_shoulder", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Scapuler_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_arm_sec01", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_MidArmBend_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_arm_sec02", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_MidElbowBend_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_arm_pole", e = True, c = "cmds.select(getCurrentChar() + \"_000_R_ArmPole_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_twist", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Wrist_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fkik", e = True, c = "cmds.select(getCurrentChar() + \"_000_R_ArmIKFKSwitch_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_allfiger", e = True, c = "selAllRFiger()")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fb_01", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Thumb_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fb_02", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Thumb_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fb_03", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Thumb_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_ff_01", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Index_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_ff_02", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Index_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_ff_03", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Index_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fm_01", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Middle_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fm_02", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Middle_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fm_03", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Middle_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fr_01", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Pinky_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fr_02", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Pinky_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_fr_03", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Pinky_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_figer_sec", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Finger_Unique_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_leg_sec", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_MidLegBend_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_R_leg", e = True, c = "cmds.select(getCurrentChar() + \"_R_000_Foot_000_Ctrl\", r = True)")
        
        #################################################################### left ##################################################################
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_shoulder", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Scapuler_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_arm_sec01", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_MidArmBend_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_arm_sec02", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_MidElbowBend_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_arm_pole", e = True, c = "cmds.select(getCurrentChar() + \"_000_L_ArmPole_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_twist", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Wrist_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fkik", e = True, c = "cmds.select(getCurrentChar() + \"_000_L_ArmIKFKSwitch_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_allfiger", e = True, c = "selAllLFiger()")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fb_01", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Thumb_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fb_02", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Thumb_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fb_03", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Thumb_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_ff_01", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Index_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_ff_02", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Index_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_ff_03", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Index_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fm_01", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Middle_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fm_02", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Middle_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fm_03", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Middle_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fr_01", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Pinky_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fr_02", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Pinky_001_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_fr_03", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Pinky_002_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_figer_sec", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Finger_Unique_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_leg_sec", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_MidLegBend_000_Ctrl\", r = True)")
#        cmds.button(self.ui + "|tabWidget|tab|ATD_L_leg", e = True, c = "cmds.select(getCurrentChar() + \"_L_000_Foot_000_Ctrl\", r = True)")

                
def getMayaWindow():
    ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtCore.QObject)

def main():
    global SYH_animPanel_app
    global SYH_animPanel_myapp
    SYH_animPanel_app = QtGui.qApp
    SYH_animPanel_myapp = StartSYH_animPanel(getMayaWindow())
    SYH_animPanel_myapp.show()
        
if __name__ == "__main__":
    main()

